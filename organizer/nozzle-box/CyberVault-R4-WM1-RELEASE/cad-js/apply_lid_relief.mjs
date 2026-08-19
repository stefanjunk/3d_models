#!/usr/bin/env node
/** Apply the closed R4 lid engraving cutter with Manifold3D. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Module from "manifold-3d";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectDir = path.resolve(scriptDir, "..");
const exportDir = path.join(projectDir, "exports", "draft");
const reportDir = path.join(projectDir, "reports");
const inputPath = path.join(exportDir, "cyber_nozzle_case_R4_DRAFT_lid.stl");
const cutterPath = path.join(projectDir, "relief", "cyber_lid_engraving_cutter_R4.stl");
const outputPath = path.join(exportDir, "cyber_nozzle_case_R4_DRAFT_lid_relief.stl");

function parseBinaryStl(target) {
  const data = fs.readFileSync(target);
  const triangleCount = data.readUInt32LE(80);
  if (data.length !== 84 + triangleCount * 50) throw new Error(`${target}: invalid binary STL`);
  const vertices = [];
  const triangles = new Uint32Array(triangleCount * 3);
  const indexes = new Map();
  let cursor = 84;
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    cursor += 12;
    for (let corner = 0; corner < 3; corner += 1) {
      const xyz = [data.readFloatLE(cursor), data.readFloatLE(cursor + 4), data.readFloatLE(cursor + 8)];
      cursor += 12;
      const key = xyz.map((value) => Math.round(value * 1e5)).join(",");
      let index = indexes.get(key);
      if (index === undefined) {
        index = vertices.length / 3;
        indexes.set(key, index);
        vertices.push(...xyz);
      }
      triangles[triangle * 3 + corner] = index;
    }
    cursor += 2;
  }
  return { triangleCount, vertices: new Float32Array(vertices), triangles };
}

function makeManifold(wasm, parsed) {
  return new wasm.Manifold(new wasm.Mesh({
    numProp: 3,
    vertProperties: parsed.vertices,
    triVerts: parsed.triangles,
    tolerance: 1e-4,
  }));
}

function writeBinaryStl(target, mesh) {
  const triangleCount = mesh.triVerts.length / 3;
  const data = Buffer.allocUnsafe(84 + triangleCount * 50);
  data.fill(0, 0, 80);
  data.write("CyberVault R4 Manifold lid relief", 0, "ascii");
  data.writeUInt32LE(triangleCount, 80);
  let cursor = 84;
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
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
    const length = Math.hypot(...normal) || 1;
    for (const value of normal) { data.writeFloatLE(value / length, cursor); cursor += 4; }
    for (const point of points) {
      for (const value of point) { data.writeFloatLE(value, cursor); cursor += 4; }
    }
    data.writeUInt16LE(0, cursor); cursor += 2;
  }
  fs.writeFileSync(target, data);
}

const wasm = await Module();
wasm.setup();
const lidInput = parseBinaryStl(inputPath);
const cutterInput = parseBinaryStl(cutterPath);
const lid = makeManifold(wasm, lidInput);
const cutter = makeManifold(wasm, cutterInput);
if (lid.status() !== "NoError") throw new Error(`Input lid status: ${lid.status()}`);
if (cutter.status() !== "NoError") throw new Error(`Cutter status: ${cutter.status()}`);
const result = lid.subtract(cutter);
if (result.status() !== "NoError") throw new Error(`Relief Boolean status: ${result.status()}`);
const resultMesh = result.getMesh();
writeBinaryStl(outputPath, resultMesh);
const report = {
  status: "PASS",
  operation: "difference",
  engine: "manifold-3d 3.5.1",
  input_lid: path.relative(projectDir, inputPath),
  cutter: path.relative(projectDir, cutterPath),
  output: path.relative(projectDir, outputPath),
  input_lid_triangles: lidInput.triangleCount,
  cutter_triangles: cutterInput.triangleCount,
  output_triangles: resultMesh.triVerts.length / 3,
  input_lid_volume_mm3: Number(lid.volume().toFixed(6)),
  cutter_volume_mm3: Number(cutter.volume().toFixed(6)),
  output_lid_volume_mm3: Number(result.volume().toFixed(6)),
  removed_volume_mm3: Number((lid.volume() - result.volume()).toFixed(6)),
  connected_components: result.decompose().length,
};
fs.writeFileSync(
  path.join(reportDir, "cyber-lid-relief-boolean.json"),
  `${JSON.stringify(report, null, 2)}\n`,
  "utf8",
);
process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
for (const item of [result, cutter, lid]) item.delete();
