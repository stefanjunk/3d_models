#!/usr/bin/env node
/** Independent manifold and collision validation for exported binary STLs. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import Module from "manifold-3d";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectDir = path.resolve(scriptDir, "..");
const exportDir = path.join(projectDir, "exports", "draft");
const reportDir = path.join(projectDir, "reports");
const prefix = "cyber_nozzle_case_R4_DRAFT";

function parseBinaryStl(target) {
  const data = fs.readFileSync(target);
  if (data.length < 84) throw new Error(`${target}: file is too short for binary STL`);
  const triangleCount = data.readUInt32LE(80);
  const expected = 84 + triangleCount * 50;
  if (data.length !== expected) {
    throw new Error(`${target}: expected ${expected} bytes, got ${data.length}`);
  }

  const vertices = [];
  const triangles = new Uint32Array(triangleCount * 3);
  const indexByPosition = new Map();
  const quantization = 1e5;
  let cursor = 84;
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    cursor += 12; // stored face normal
    for (let corner = 0; corner < 3; corner += 1) {
      const x = data.readFloatLE(cursor);
      const y = data.readFloatLE(cursor + 4);
      const z = data.readFloatLE(cursor + 8);
      cursor += 12;
      const key = `${Math.round(x * quantization)},${Math.round(y * quantization)},${Math.round(z * quantization)}`;
      let index = indexByPosition.get(key);
      if (index === undefined) {
        index = vertices.length / 3;
        indexByPosition.set(key, index);
        vertices.push(x, y, z);
      }
      triangles[triangle * 3 + corner] = index;
    }
    cursor += 2;
  }
  return {
    triangleCount,
    vertexCount: vertices.length / 3,
    vertices: new Float32Array(vertices),
    triangles,
  };
}

function makeManifold(wasm, parsed) {
  const mesh = new wasm.Mesh({
    numProp: 3,
    vertProperties: parsed.vertices,
    triVerts: parsed.triangles,
    tolerance: 1e-4,
  });
  return new wasm.Manifold(mesh);
}

function fixed(value) {
  return Number(value.toFixed(6));
}

function describe(manifold, source) {
  return {
    source,
    status: manifold.status(),
    volume_mm3: fixed(manifold.volume()),
    surface_area_mm2: fixed(manifold.surfaceArea()),
    genus: manifold.genus(),
  };
}

function boundsOf(manifold) {
  const mesh = manifold.getMesh();
  if (mesh.vertProperties.length === 0) return null;
  const bounds = [[Infinity, Infinity, Infinity], [-Infinity, -Infinity, -Infinity]];
  for (let i = 0; i < mesh.vertProperties.length; i += mesh.numProp) {
    for (let axis = 0; axis < 3; axis += 1) {
      bounds[0][axis] = Math.min(bounds[0][axis], mesh.vertProperties[i + axis]);
      bounds[1][axis] = Math.max(bounds[1][axis], mesh.vertProperties[i + axis]);
    }
  }
  return bounds.map((row) => row.map(fixed));
}

function componentReport(manifold) {
  const components = manifold.decompose();
  const result = components
    .map((component) => ({
      volume_mm3: fixed(component.volume()),
      bounds_mm: boundsOf(component),
    }))
    .sort((a, b) => b.volume_mm3 - a.volume_mm3);
  for (const component of components) component.delete();
  return result;
}

const wasm = await Module();
wasm.setup();

const baseSource = `${prefix}_base_manifold.stl`;
const baseParsed = parseBinaryStl(path.join(exportDir, baseSource));
const lidSource = `${prefix}_lid_relief_manifold.stl`;
const lidParsed = parseBinaryStl(path.join(exportDir, lidSource));
const base = makeManifold(wasm, baseParsed);
const lid = makeManifold(wasm, lidParsed);
const closedLid = lid.translate(0, 0, -9).rotate(180, 0, 0).translate(0, 0, 9);
const openIntersection = base.intersect(lid);
const closedIntersection = base.intersect(closedLid);

const report = {
  validator: "manifold-3d 3.5.1",
  coordinate_convention: {
    open: "as exported, both bed-facing exteriors at z=0",
    closed: "lid rotated 180 degrees about hinge axis x through y=0,z=9",
  },
  inputs: {
    base: {
      triangles: baseParsed.triangleCount,
      welded_vertices: baseParsed.vertexCount,
    },
    lid: {
      triangles: lidParsed.triangleCount,
      welded_vertices: lidParsed.vertexCount,
    },
  },
  base: describe(base, baseSource),
  lid: describe(lid, lidSource),
  connected_components: {
    base: componentReport(base),
    lid: componentReport(lid),
  },
  collision_volume_mm3: {
    open: fixed(openIntersection.volume()),
    closed_rigid_nominal: fixed(closedIntersection.volume()),
  },
  collision_bounds_mm: {
    open: boundsOf(openIntersection),
    closed_rigid_nominal: boundsOf(closedIntersection),
  },
  minimum_surface_gap_mm: {
    open_with_captive_hinge: fixed(base.minGap(lid, 2.0)),
    closed_rigid_nominal: fixed(base.minGap(closedLid, 2.0)),
    interpretation: "Zero is expected at touching/fused-style kinematic interfaces; collision volume is the acceptance metric.",
  },
};

for (const item of [base, lid, closedLid, openIntersection, closedIntersection]) {
  if (item.status() !== "NoError") throw new Error(`Manifold validation failed: ${item.status()}`);
}

fs.mkdirSync(reportDir, { recursive: true });
fs.writeFileSync(
  path.join(reportDir, "manifold-collision-candidate.json"),
  `${JSON.stringify(report, null, 2)}\n`,
  "utf8",
);

const productionReportPath = path.join(reportDir, "production-cad-candidate.json");
const productionReport = JSON.parse(fs.readFileSync(productionReportPath, "utf8"));
productionReport.collision_volume_mm3 = {
  ...report.collision_volume_mm3,
  validator: report.validator,
  note: "Rigid nominal mesh intersection; compliant latch engagement still requires the physical coupon/cycle test.",
};
fs.writeFileSync(productionReportPath, `${JSON.stringify(productionReport, null, 2)}\n`, "utf8");

process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);

for (const item of [openIntersection, closedIntersection, closedLid, lid, base]) item.delete();
