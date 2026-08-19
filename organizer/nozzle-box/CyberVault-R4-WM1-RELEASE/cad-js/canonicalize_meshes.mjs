#!/usr/bin/env node
/** Canonicalize final R4 candidate meshes without changing design intent. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Module from "manifold-3d";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectDir = path.resolve(scriptDir, "..");
const exportDir = path.join(projectDir, "exports", "draft");
const reportDir = path.join(projectDir, "reports");

function parseBinaryStl(target) {
  const data = fs.readFileSync(target);
  const triangleCount = data.readUInt32LE(80);
  if (data.length !== 84 + triangleCount * 50) throw new Error(`${target}: invalid binary STL`);
  const vertices = [];
  const triangles = new Uint32Array(triangleCount * 3);
  const indexByPosition = new Map();
  let cursor = 84;
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    cursor += 12;
    for (let corner = 0; corner < 3; corner += 1) {
      const xyz = [data.readFloatLE(cursor), data.readFloatLE(cursor + 4), data.readFloatLE(cursor + 8)];
      cursor += 12;
      const key = xyz.map((value) => Math.round(value * 1e6)).join(",");
      let index = indexByPosition.get(key);
      if (index === undefined) {
        index = vertices.length / 3;
        indexByPosition.set(key, index);
        vertices.push(...xyz);
      }
      triangles[triangle * 3 + corner] = index;
    }
    cursor += 2;
  }
  return { triangleCount, vertices: new Float32Array(vertices), triangles };
}

function makeManifold(wasm, parsed) {
  const mesh = new wasm.Mesh({
    numProp: 3,
    vertProperties: parsed.vertices,
    triVerts: parsed.triangles,
    tolerance: 1e-5,
  });
  mesh.merge();
  return new wasm.Manifold(mesh);
}

function validTriangles(mesh) {
  const records = [];
  for (let triangle = 0; triangle < mesh.triVerts.length / 3; triangle += 1) {
    const ids = [mesh.triVerts[triangle * 3], mesh.triVerts[triangle * 3 + 1], mesh.triVerts[triangle * 3 + 2]];
    const points = ids.map((id) => [
      mesh.vertProperties[id * mesh.numProp],
      mesh.vertProperties[id * mesh.numProp + 1],
      mesh.vertProperties[id * mesh.numProp + 2],
    ]);
    const ab = points[1].map((value, axis) => value - points[0][axis]);
    const ac = points[2].map((value, axis) => value - points[0][axis]);
    const normal = [
      ab[1] * ac[2] - ab[2] * ac[1],
      ab[2] * ac[0] - ab[0] * ac[2],
      ab[0] * ac[1] - ab[1] * ac[0],
    ];
    const length = Math.hypot(...normal);
    if (length <= 1e-10) continue;
    records.push({ points, normal: normal.map((value) => value / length) });
  }
  return records;
}

function writeBinaryStl(target, mesh, label) {
  const records = validTriangles(mesh);
  const data = Buffer.allocUnsafe(84 + records.length * 50);
  data.fill(0, 0, 80);
  data.write(label, 0, "ascii");
  data.writeUInt32LE(records.length, 80);
  let cursor = 84;
  for (const record of records) {
    for (const value of record.normal) { data.writeFloatLE(value, cursor); cursor += 4; }
    for (const point of record.points) {
      for (const value of point) { data.writeFloatLE(value, cursor); cursor += 4; }
    }
    data.writeUInt16LE(0, cursor); cursor += 2;
  }
  fs.writeFileSync(target, data);
  return records.length;
}

const wasm = await Module();
wasm.setup();
const jobs = [
  {
    name: "base",
    input: path.join(exportDir, "cyber_nozzle_case_R4_DRAFT_base.stl"),
    output: path.join(exportDir, "cyber_nozzle_case_R4_DRAFT_base_manifold.stl"),
  },
  {
    name: "lid",
    input: path.join(exportDir, "cyber_nozzle_case_R4_DRAFT_lid_relief.stl"),
    output: path.join(exportDir, "cyber_nozzle_case_R4_DRAFT_lid_relief_manifold.stl"),
  },
];
const results = [];
for (const job of jobs) {
  const parsed = parseBinaryStl(job.input);
  const manifold = makeManifold(wasm, parsed);
  if (manifold.status() !== "NoError") throw new Error(`${job.name}: ${manifold.status()}`);
  const simplified = manifold.simplify(1e-5);
  if (simplified.status() !== "NoError") throw new Error(`${job.name} simplified: ${simplified.status()}`);
  const beforeVolume = manifold.volume();
  const afterVolume = simplified.volume();
  const outputTriangles = writeBinaryStl(job.output, simplified.getMesh(), `CyberVault R4 canonical ${job.name}`);
  results.push({
    name: job.name,
    input: path.relative(projectDir, job.input),
    output: path.relative(projectDir, job.output),
    input_triangles: parsed.triangleCount,
    output_triangles: outputTriangles,
    input_volume_mm3: Number(beforeVolume.toFixed(6)),
    output_volume_mm3: Number(afterVolume.toFixed(6)),
    volume_delta_mm3: Number((afterVolume - beforeVolume).toFixed(9)),
    connected_components: simplified.decompose().length,
  });
  simplified.delete();
  manifold.delete();
}
const report = { status: "PASS", engine: "manifold-3d 3.5.1", tolerance_mm: 0.00001, results };
fs.writeFileSync(
  path.join(reportDir, "mesh-canonicalization.json"),
  `${JSON.stringify(report, null, 2)}\n`,
  "utf8",
);
process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
