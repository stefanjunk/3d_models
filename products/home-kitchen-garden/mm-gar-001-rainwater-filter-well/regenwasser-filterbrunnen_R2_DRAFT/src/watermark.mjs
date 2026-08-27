import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Sketcher } from "replicad";

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(moduleDir, "..");
const BOOLEAN_OVERLAP_MM = 0.01;

function parseDxfPolylines(dxfText) {
  const lines = dxfText.split(/\r?\n/);
  const pairs = [];
  for (let index = 0; index + 1 < lines.length; index += 2) {
    pairs.push([Number(lines[index].trim()), lines[index + 1].trim()]);
  }

  const contours = [];
  let active = null;
  let vertex = null;
  for (const [code, value] of pairs) {
    if (code === 0 && value === "POLYLINE") {
      active = [];
      vertex = null;
      continue;
    }
    if (!active) continue;
    if (code === 0 && value === "VERTEX") {
      if (vertex && Number.isFinite(vertex.x) && Number.isFinite(vertex.y)) {
        active.push([vertex.x, vertex.y]);
      }
      vertex = {};
      continue;
    }
    if (code === 0 && value === "SEQEND") {
      if (vertex && Number.isFinite(vertex.x) && Number.isFinite(vertex.y)) {
        active.push([vertex.x, vertex.y]);
      }
      if (active.length >= 3) contours.push(active);
      active = null;
      vertex = null;
      continue;
    }
    if (vertex && code === 10) vertex.x = Number(value);
    if (vertex && code === 20) vertex.y = Number(value);
  }

  if (!contours.length) throw new Error("No closed watermark polylines found in DXF asset");
  return contours;
}

function pointInPolygon([px, py], polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i, i += 1) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const crosses = (yi > py) !== (yj > py);
    if (crosses) {
      const xAtY = ((xj - xi) * (py - yi)) / (yj - yi) + xi;
      if (px < xAtY) inside = !inside;
    }
  }
  return inside;
}

function transformedContour(contour, config) {
  const xSign = config.mirrorX ? -1 : 1;
  return contour.map(([x, y]) => [
    config.position[0] + xSign * config.scale * x,
    config.position[1] + config.scale * y,
  ]);
}

function polygonExtrusion(points, depth) {
  let sketch = new Sketcher("XY").movePointerTo(points[0]);
  for (const point of points.slice(1)) sketch = sketch.lineTo(point);
  return sketch
    .close()
    .extrude(depth + BOOLEAN_OVERLAP_MM)
    .translateZ(-BOOLEAN_OVERLAP_MM);
}

function buildEvenOddCutters(contours, config) {
  const transformed = contours.map((contour) => transformedContour(contour, config));
  const nestingDepth = transformed.map((contour, index) => {
    const sample = contour[0];
    return transformed.reduce((depth, other, otherIndex) => {
      if (index === otherIndex) return depth;
      return depth + (pointInPolygon(sample, other) ? 1 : 0);
    }, 0);
  });

  const solids = [];
  transformed.forEach((contour, index) => {
    if (nestingDepth[index] % 2 !== 0) return;
    let solid = polygonExtrusion(contour, config.depth);
    transformed.forEach((hole, holeIndex) => {
      if (nestingDepth[holeIndex] !== nestingDepth[index] + 1) return;
      if (!pointInPolygon(hole[0], contour)) return;
      solid = solid.cut(polygonExtrusion(hole, config.depth));
    });
    solids.push(solid);
  });
  return solids;
}

export function watermarkDxfPath(p) {
  return path.join(
    projectRoot,
    "assets",
    "just-innovation-watermark",
    "exports",
    "dxf",
    `just-innovation-${p.watermark.profile}.dxf`
  );
}

export function applyUndersideWatermark(body, p) {
  if (!p.watermark.enabled) return body;
  const dxfPath = watermarkDxfPath(p);
  const contours = parseDxfPolylines(fs.readFileSync(dxfPath, "utf8"));
  const cutters = buildEvenOddCutters(contours, {
    position: p.watermark.position,
    scale: p.watermark.uniformScale,
    mirrorX: p.watermark.mirrorX,
    depth: p.watermark.depth,
  });
  return cutters.reduce((result, cutter) => result.cut(cutter), body);
}

export function watermarkOutlineMetadata(p) {
  const dxfPath = watermarkDxfPath(p);
  const contours = parseDxfPolylines(fs.readFileSync(dxfPath, "utf8"));
  const points = contours.flatMap((contour) => transformedContour(contour, {
    position: p.watermark.position,
    scale: p.watermark.uniformScale,
    mirrorX: p.watermark.mirrorX,
  }));
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  return {
    source: path.relative(projectRoot, dxfPath),
    contourCount: contours.length,
    boundsMm: [
      [Math.min(...xs), Math.min(...ys)],
      [Math.max(...xs), Math.max(...ys)],
    ],
  };
}
