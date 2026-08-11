import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { unzipSync } from "fflate";
import sharp from "sharp";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const exportsRoot = path.join(root, "exports");
const validationRoot = path.join(root, "validation");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function round(value, digits = 6) {
  return Number(value.toFixed(digits));
}

function vertexKey(point) {
  return point.map((value) => Object.is(value, -0) ? "0" : String(value)).join("|");
}

function addEdge(edgeCounts, a, b) {
  const key = a < b ? `${a}::${b}` : `${b}::${a}`;
  edgeCounts.set(key, (edgeCounts.get(key) ?? 0) + 1);
}

function meshTopology(vertices, triangles, label) {
  const edges = new Map();
  let zeroAreaTriangles = 0;
  let signedVolume = 0;
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  for (const point of vertices) {
    for (let axis = 0; axis < 3; axis += 1) {
      min[axis] = Math.min(min[axis], point[axis]);
      max[axis] = Math.max(max[axis], point[axis]);
    }
  }
  for (const [i0, i1, i2] of triangles) {
    assert(i0 < vertices.length && i1 < vertices.length && i2 < vertices.length, `${label}: triangle index out of range`);
    const a = vertices[i0];
    const b = vertices[i1];
    const c = vertices[i2];
    const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
    const ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
    const cross = [
      ab[1] * ac[2] - ab[2] * ac[1],
      ab[2] * ac[0] - ab[0] * ac[2],
      ab[0] * ac[1] - ab[1] * ac[0],
    ];
    if (Math.hypot(...cross) / 2 < 1e-10) zeroAreaTriangles += 1;
    signedVolume += (
      a[0] * (b[1] * c[2] - b[2] * c[1])
      - a[1] * (b[0] * c[2] - b[2] * c[0])
      + a[2] * (b[0] * c[1] - b[1] * c[0])
    ) / 6;
    const keys = [vertexKey(a), vertexKey(b), vertexKey(c)];
    addEdge(edges, keys[0], keys[1]);
    addEdge(edges, keys[1], keys[2]);
    addEdge(edges, keys[2], keys[0]);
  }
  const counts = [...edges.values()];
  const boundaryEdges = counts.filter((count) => count === 1).length;
  const nonManifoldEdges = counts.filter((count) => count > 2).length;
  assert(zeroAreaTriangles === 0, `${label}: zero-area triangles found`);
  assert(boundaryEdges === 0, `${label}: ${boundaryEdges} boundary edges found`);
  assert(nonManifoldEdges === 0, `${label}: ${nonManifoldEdges} non-manifold edges found`);
  assert(signedVolume > 0, `${label}: triangle winding does not enclose positive volume`);
  return {
    vertices: vertices.length,
    triangles: triangles.length,
    boundary_edges: boundaryEdges,
    non_manifold_edges: nonManifoldEdges,
    zero_area_triangles: zeroAreaTriangles,
    signed_volume_mm3: round(signedVolume),
    bounds_mm: [min.map((value) => round(value)), max.map((value) => round(value))],
  };
}

function parseBinaryStl(buffer, label) {
  assert(buffer.length >= 84, `${label}: truncated STL`);
  const triangleCount = buffer.readUInt32LE(80);
  assert(buffer.length === 84 + triangleCount * 50, `${label}: STL byte count mismatch`);
  const vertices = [];
  const vertexIds = new Map();
  const triangles = [];
  function idFor(point) {
    const key = vertexKey(point);
    if (!vertexIds.has(key)) {
      vertexIds.set(key, vertices.length);
      vertices.push(point);
    }
    return vertexIds.get(key);
  }
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    const offset = 84 + triangle * 50 + 12;
    const ids = [];
    for (let corner = 0; corner < 3; corner += 1) {
      const base = offset + corner * 12;
      ids.push(idFor([
        buffer.readFloatLE(base),
        buffer.readFloatLE(base + 4),
        buffer.readFloatLE(base + 8),
      ]));
    }
    triangles.push(ids);
  }
  return meshTopology(vertices, triangles, label);
}

function parse3mf(buffer, label) {
  const files = unzipSync(new Uint8Array(buffer));
  for (const required of ["[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"]) {
    assert(files[required], `${label}: missing ${required}`);
  }
  const xml = new TextDecoder().decode(files["3D/3dmodel.model"]);
  assert(/<model unit="millimeter"/.test(xml), `${label}: model unit is not millimetres`);
  assert(xml.includes("jsi:ReleaseID"), `${label}: release metadata missing`);
  assert(xml.includes("jsi:AIUse"), `${label}: AI-use metadata missing`);
  const vertices = [...xml.matchAll(/<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"\/>/g)]
    .map((match) => match.slice(1).map(Number));
  const triangles = [...xml.matchAll(/<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"\/>/g)]
    .map((match) => match.slice(1).map(Number));
  assert(vertices.length > 0 && triangles.length > 0, `${label}: empty 3MF mesh`);
  return meshTopology(vertices, triangles, label);
}

async function sha256(filePath) {
  return crypto.createHash("sha256").update(await fs.readFile(filePath)).digest("hex");
}

async function walkFiles(directory) {
  const files = [];
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    if (entry.name === "node_modules") continue;
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walkFiles(fullPath));
    else files.push(fullPath);
  }
  return files;
}

const metrics = JSON.parse(await fs.readFile(path.join(validationRoot, "geometry-metrics.json"), "utf8"));
assert(metrics.release_id === "JSI-WM-001-R1", "Unexpected release ID");

const results = {
  release_id: metrics.release_id,
  validated_at: new Date().toISOString(),
  status: "passed-with-physical-test-pending",
  geometry: [],
  format_checks: {},
  physical_test: {
    status: "pending",
    reason: "A slicer-specific preview and a physical coupon print require the target machine and filament.",
  },
};

for (const shape of metrics.exported_shapes) {
  assert(shape.brep_valid === true, `${shape.name}: generator did not confirm B-Rep validity`);
  assert(shape.manifold_mesh_valid === true, `${shape.name}: generator did not confirm manifold validity`);
  const delta = Math.abs(shape.manifold_mesh_volume_mm3 - shape.volume_mm3) / shape.volume_mm3;
  assert(delta <= 0.005, `${shape.name}: B-Rep/mesh volume mismatch exceeds 0.5%`);
  const stlPath = path.join(exportsRoot, "stl", `${shape.name}.stl`);
  const threeMfPath = path.join(exportsRoot, "3mf", `${shape.name}.3mf`);
  const stepPath = path.join(exportsRoot, "step", `${shape.name}.step`);
  const stl = parseBinaryStl(await fs.readFile(stlPath), `${shape.name}.stl`);
  const threeMf = parse3mf(await fs.readFile(threeMfPath), `${shape.name}.3mf`);
  assert(stl.triangles === threeMf.triangles, `${shape.name}: STL/3MF triangle counts differ`);
  const step = await fs.readFile(stepPath, "utf8");
  assert(step.startsWith("ISO-10303-21;"), `${shape.name}: invalid STEP header`);
  assert(step.includes("DATA;") && step.includes("END-ISO-10303-21;"), `${shape.name}: incomplete STEP structure`);
  results.geometry.push({
    name: shape.name,
    brep_valid: true,
    brep_mesh_volume_delta_percent: round(delta * 100, 4),
    stl,
    three_mf: threeMf,
    sha256: {
      stl: await sha256(stlPath),
      three_mf: await sha256(threeMfPath),
      step: await sha256(stepPath),
    },
  });
}

for (const format of ["svg", "dxf", "png"]) {
  const directory = path.join(exportsRoot, format);
  const files = (await fs.readdir(directory)).sort();
  assert(files.length >= 4, `${format}: expected at least four profile files`);
  results.format_checks[format] = [];
  for (const file of files) {
    const filePath = path.join(directory, file);
    if (format === "svg") {
      const svg = await fs.readFile(filePath, "utf8");
      assert(svg.includes("xmlns=\"http://www.w3.org/2000/svg\""), `${file}: invalid SVG root`);
      assert(!svg.includes("<text"), `${file}: manufacturing SVG contains live text`);
      assert(svg.includes("units millimetres"), `${file}: millimetre metadata missing`);
    } else if (format === "dxf") {
      const dxf = await fs.readFile(filePath, "utf8");
      assert(dxf.includes("$INSUNITS") && dxf.includes("AC1009"), `${file}: DXF header/unit metadata missing`);
      assert(dxf.trimEnd().endsWith("EOF"), `${file}: incomplete DXF`);
    } else {
      const metadata = await sharp(filePath).metadata();
      assert(metadata.format === "png" && metadata.width > 0 && metadata.height > 0, `${file}: invalid PNG`);
    }
    results.format_checks[format].push({ file, sha256: await sha256(filePath) });
  }
}

const scadPath = path.join(root, "source", "just-innovation-watermark.scad");
const scad = await fs.readFile(scadPath, "utf8");
assert(scad.includes("module jsi_watermark_cutter"), "OpenSCAD cutter module missing");
assert(scad.includes("module jsi_subtract_watermark"), "OpenSCAD subtraction module missing");
results.format_checks.scad = {
  syntax: "static checks passed; OpenSCAD executable not available in validation environment",
  sha256: await sha256(scadPath),
};

await fs.writeFile(
  path.join(validationRoot, "validation-results.json"),
  `${JSON.stringify(results, null, 2)}\n`,
);
const reportRows = results.geometry.map((item) => (
  `| ${item.name} | ja | ${item.stl.triangles} | ${item.stl.boundary_edges} | ${item.stl.non_manifold_edges} | ${item.brep_mesh_volume_delta_percent.toFixed(4)} % |`
)).join("\n");
await fs.writeFile(
  path.join(validationRoot, "validation-report.md"),
  `# Digitale Validierung – ${results.release_id}\n\n`
  + `Status: **bestanden; physischer Test ausstehend**  \n`
  + `Validiert: ${results.validated_at}\n\n`
  + `| Geometrie | B-Rep gültig | STL-Dreiecke | Randkanten | Nicht-manifold Kanten | B-Rep/Netz-Volumendifferenz |\n`
  + `|---|---:|---:|---:|---:|---:|\n${reportRows}\n\n`
  + `## Bestandene Prüfungen\n\n`
  + `- OpenCascade-BRep-Prüfung für alle fünf STEP-Geometrien.\n`
  + `- Geschlossene, orientierte STL- und 3MF-Netze ohne Randkanten, nicht-manifold Kanten oder Nullflächendreiecke.\n`
  + `- Positive Volumina und maximal 0,5 % zulässige Abweichung zwischen B-Rep und Netz; alle Profile liegen darunter.\n`
  + `- Gültige 3MF-ZIP-Struktur mit Millimetereinheit, Release-ID und KI-Provenienzmetadaten.\n`
  + `- STEP-Grundstruktur, SVG-Fertigungspfade ohne Live-Schrift, DXF-R12-Millimetermetadaten und lesbare PNG-Dateien.\n`
  + `- OpenSCAD-Modulschnittstellen statisch vorhanden.\n\n`
  + `## Noch offen\n\n`
  + `Ein OpenSCAD-Parser, ein Ziel-Slicer und der reale Drucker standen in der digitalen Prüfumgebung nicht zur Verfügung. `
  + `Deshalb müssen Slicer-Vorschau und Coupon-Druck gemäß \`test-plan.yaml\` vor dem Serieneinsatz abgeschlossen werden.\n`,
);
await fs.writeFile(
  path.join(validationRoot, "physical-test-record.csv"),
  "date,operator,printer,slicer_and_version,material,filament_brand,plate,nozzle_mm,layer_height_mm,first_layer_height_mm,line_width_mm,xy_compensation_mm,standard_d020,standard_d040,standard_d060,compact_8af,compact_10af,compact_12af,selected_profile,selected_depth_mm,result,notes\n"
  + ",,,,,,,0.40,0.20,,,,,,,,,,,,pending,\n",
);
const manifestPath = path.join(root, "manifest.sha256");
const manifestFiles = (await walkFiles(root))
  .filter((filePath) => filePath !== manifestPath && !filePath.endsWith(".zip"))
  .sort((a, b) => a.localeCompare(b));
const manifestLines = [];
for (const filePath of manifestFiles) {
  manifestLines.push(`${await sha256(filePath)}  ${path.relative(root, filePath).split(path.sep).join("/")}`);
}
await fs.writeFile(manifestPath, `${manifestLines.join("\n")}\n`);
console.log(`Validated ${results.geometry.length} B-Rep/mesh presets; physical coupon test remains pending.`);
