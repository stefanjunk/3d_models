#!/usr/bin/env node
/**
 * Parametric CyberVault nozzle case for Anycubic Kobra 3 Max quick-swap modules.
 *
 * Units are millimetres.  The open, print-oriented assembly contains exactly
 * two moving bodies: the base and the lid.  The polygonal hinge pin is fused
 * to the lid and is captive inside two base knuckles.
 */

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

import * as r from "replicad";

const require = createRequire(import.meta.url);
process.stderr.write("CAD_STAGE init-oc\n");
const ocModule = require("replicad-opencascadejs");
const ocFactory = ocModule.default || ocModule;
const ocRoot = path.dirname(require.resolve("replicad-opencascadejs"));
// The upstream Emscripten factory references Node's CommonJS globals when it
// initializes, even when called from an ES module.  Supplying the equivalent
// globals keeps the source itself modern ESM while preserving the vendor API.
globalThis.__dirname = ocRoot;
globalThis.require = require;
process.stderr.write(`CAD_STAGE oc-factory-${typeof ocFactory} wasm-${fs.existsSync(path.join(ocRoot, "replicad_single.wasm"))}\n`);
let OC;
try {
  OC = await ocFactory({
    locateFile: () => path.join(ocRoot, "replicad_single.wasm"),
  });
} catch (error) {
  process.stderr.write(`CAD_OC_FAILED ${error && error.message ? error.message : String(error)}\n`);
  throw error;
}
r.setOC(OC);
process.stderr.write("CAD_STAGE init-paths\n");

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectDir = path.resolve(scriptDir, "..");
const exportDir = path.join(projectDir, "exports", "draft");
const reportDir = path.join(projectDir, "reports");
fs.mkdirSync(exportDir, { recursive: true });
fs.mkdirSync(reportDir, { recursive: true });

function markStage(stage) {
  fs.writeFileSync(path.join(reportDir, "cad-stage.txt"), `${stage}\n`, "utf8");
  process.stderr.write(`CAD_STAGE ${stage}\n`);
}

const fontPath = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf";
const fontBuffer = fs.readFileSync(fontPath);
process.stderr.write("CAD_STAGE load-font\n");
await r.loadFont(
  fontBuffer.buffer.slice(
    fontBuffer.byteOffset,
    fontBuffer.byteOffset + fontBuffer.byteLength,
  ),
  "default",
  true,
);
process.stderr.write("CAD_STAGE load-pattern\n");

const reliefPattern = JSON.parse(
  fs.readFileSync(path.join(projectDir, "relief", "pattern_geometry.json"), "utf8"),
);
const watermarkSelection = JSON.parse(
  fs.readFileSync(path.join(projectDir, "reports", "watermark-selection.json"), "utf8"),
);

export const P = Object.freeze({
  revision: "CYBERVAULT-R4-CAD-A-WM1",
  base: {
    width: 68.0,
    depth: 184.0,
    cornerRadius: 9.0,
    centerY: -96.2,
    floor: 3.0,
    wall: 2.4,
    height: 14.5,
  },
  lid: {
    centerY: 96.2,
    plate: 3.0,
    skirtHeight: 6.0,
    wall: 2.4,
    perimeterClearanceEachSide: 0.35,
    innerWidth: 68.7,
    innerDepth: 184.7,
    innerRadius: 9.35,
    outerWidth: 73.5,
    outerDepth: 189.5,
    outerRadius: 11.75,
  },
  nozzle: {
    length: 45.0,
    upperDiameter: 5.0,
    lowerDiameter: 5.6,
    fitClearanceEachSide: 0.35,
    axisZ: 8.0,
    saddleWidth: 11.0,
    upperSaddleX: [-18.5, -10.5],
    lowerSaddleX: [0.5, 12.5],
    rearStopX: [-22.8, -20.8],
    labelCentersLocalY: [-82.0, -39.0, 4.0, 47.0],
    slotOffsetsFromLabelY: [9.8, 21.1, 32.4],
    labels: ["0,4 STAHL ×3", "0,4 HART ×3", "0,6 ×3", "0,8 ×3"],
  },
  hinge: {
    axisY: 0.0,
    axisZ: 9.0,
    pinCircumRadius: 2.0,
    holeRadius: 2.35,
    outerRadius: 3.6,
    radialClearance: 0.35,
    axialClearance: 0.5,
    baseSegments: [[-18.5, -7.5], [7.5, 18.5]],
    lidSegments: [[-30.0, -19.0], [-7.0, 7.0], [19.0, 30.0]],
  },
  latch: {
    armLength: 14.5,
    armThickness: 1.32,
    armHeight: 4.6,
    designDeflection: 0.8,
    rootRadius: 1.3,
    undercut: 0.7,
    hardStopDeflection: 1.05,
  },
  text: {
    padWidth: 50.0,
    padDepth: 7.0,
    padHeight: 1.2,
    fontSize: 4.75,
    engravingDepth: 0.48,
  },
  manufacturing: {
    material: "PETG, unfilled",
    nozzle: 0.4,
    layerHeight: 0.16,
    stlTolerance: 0.08,
    angularTolerance: 0.12,
  },
  watermark: {
    assetId: "JSI-WM-001-R1",
    variant: "standard",
    nominalEnvelope: [32.0, 10.0],
    scale: 1.0,
    rotationDeg: 0,
    mirrorXForUndersideReadability: true,
    centerX: 0.0,
    centerY: -96.2,
    depth: 0.4,
    booleanOverlap: 0.05,
    candidateSafeRectangle: [50.0, 20.0],
  },
});

function assertParameters() {
  if (P.nozzle.fitClearanceEachSide !== 0.35) {
    throw new Error("The user-qualified two-dot fit must remain 0.35 mm per side.");
  }
  if (Math.abs((P.lid.innerWidth - P.base.width) - 0.7) > 1e-9) {
    throw new Error("Lid/base perimeter clearance mismatch.");
  }
  if (P.base.wall - reliefPattern.side_band.engraving_depth_mm < 1.8) {
    throw new Error("Side engraving violates the 1.8 mm residual-wall requirement.");
  }
  if (P.lid.plate - reliefPattern.engraving.major_depth_mm < 1.8) {
    throw new Error("Lid engraving violates the 1.8 mm residual-wall requirement.");
  }
  if (reliefPattern.engraving.major_line_width_mm > reliefPattern.engraving.maximum_recess_span_mm) {
    throw new Error("Primary lid engraving exceeds the approved bridge-span limit.");
  }
  if (reliefPattern.engraving.secondary_line_width_mm < 0.8) {
    throw new Error("Secondary lid engraving is below the approved printable width.");
  }
  if (watermarkSelection.status !== "PASS") {
    throw new Error("The bundled production watermark selector did not pass.");
  }
  if (P.base.floor - P.watermark.depth < 1.8) {
    throw new Error("Underside watermark violates the 1.8 mm residual-floor requirement.");
  }
}

function probeShape(shape, label) {
  try {
    const volume = r.measureShapeVolumeProperties(shape).volume;
    const mesh = shape.mesh({
      tolerance: P.manufacturing.stlTolerance,
      angularTolerance: P.manufacturing.angularTolerance,
    });
    process.stderr.write(
      `CAD_PROBE ${label} type=${shape.constructor.name} faces=${shape.faces.length} volume=${volume.toFixed(3)} triangles=${mesh.triangles.length / 3}\n`,
    );
  } catch (error) {
    const message = error && error.message ? error.message : String(error);
    throw new Error(`${label} probe failed: ${message}`);
  }
}

function roundedPrism(width, depth, radius, z0, height, centerX = 0, centerY = 0) {
  return r
    .drawRoundedRectangle(width, depth, radius)
    .sketchOnPlane("XY", z0)
    .extrude(height)
    .translate(centerX, centerY, 0);
}

function box(x0, x1, y0, y1, z0, z1) {
  return r.makeBox([x0, y0, z0], [x1, y1, z1]);
}

function fuseAll(seed, solids) {
  let result = seed;
  for (const solid of solids) result = result.fuse(solid);
  return result;
}

function cutAll(seed, tools) {
  let result = seed;
  for (const tool of tools) result = result.cut(tool);
  return result;
}

function roundedPerimeterCutter(width, depth, radius, centerY, z0, height, cutDepth) {
  const outer = roundedPrism(
    width + 0.2,
    depth + 0.2,
    radius + 0.1,
    z0,
    height,
    0,
    centerY,
  );
  const inner = roundedPrism(
    width - 2 * cutDepth,
    depth - 2 * cutDepth,
    radius - cutDepth,
    z0 - 0.1,
    height + 0.2,
    0,
    centerY,
  );
  return outer.cut(inner);
}

function roundedPerimeterEmboss(width, depth, radius, centerY, z0, height, outwardDepth) {
  const overlap = 0.06;
  const outer = roundedPrism(
    width + 2 * outwardDepth,
    depth + 2 * outwardDepth,
    radius + outwardDepth,
    z0,
    height,
    0,
    centerY,
  );
  const inner = roundedPrism(
    width - 2 * overlap,
    depth - 2 * overlap,
    radius - overlap,
    z0 - 0.05,
    height + 0.1,
    0,
    centerY,
  );
  return outer.cut(inner);
}

function hexPrism(radius, z0, height, centerX, centerY, rotationDeg = 0) {
  return r
    .drawPolysides(radius, 6)
    .rotate(rotationDeg)
    .sketchOnPlane("XY", z0)
    .extrude(height)
    .translate(centerX, centerY, 0);
}

function hexRingCutter(outerRadius, innerRadius, z0, height, centerX, centerY, rotationDeg = 0) {
  return hexPrism(outerRadius, z0, height, centerX, centerY, rotationDeg)
    .cut(hexPrism(innerRadius, z0 - 0.1, height + 0.2, centerX, centerY, rotationDeg));
}

function capsuleCutter(p0, p1, width, z0, height, centerY) {
  const [x0, y0] = p0;
  const [x1, y1] = p1;
  const dx = x1 - x0;
  const dy = y1 - y0;
  const length = Math.hypot(dx, dy);
  const angle = Math.atan2(dy, dx) * 180 / Math.PI;
  const mx = (x0 + x1) / 2;
  const my = centerY + (y0 + y1) / 2;
  let body = box(-length / 2, length / 2, -width / 2, width / 2, z0, z0 + height)
    .rotate(angle, [0, 0, 0], [0, 0, 1])
    .translate(mx, my, 0);
  body = body.fuse(r.makeCylinder(width / 2, height, [x0, centerY + y0, z0]));
  body = body.fuse(r.makeCylinder(width / 2, height, [x1, centerY + y1, z0]));
  return body;
}

function chamferedRectanglePoints(center, width, height, chamfer) {
  const [cx, cy] = center;
  const x0 = cx - width / 2;
  const x1 = cx + width / 2;
  const y0 = cy - height / 2;
  const y1 = cy + height / 2;
  const c = Math.min(chamfer, width / 2, height / 2);
  return [
    [x0 + c, y0], [x1 - c, y0], [x1, y0 + c], [x1, y1 - c],
    [x1 - c, y1], [x0 + c, y1], [x0, y1 - c], [x0, y0 + c],
  ];
}

function polygonPrismXY(points, z0, height, centerY = 0) {
  const shifted = points.map(([x, y]) => [x, y + centerY]);
  return drawingFromPolygon(shifted).sketchOnPlane("XY", z0).extrude(height);
}

function chamferedPanelFrameCutter(panel, z0, height, centerY) {
  const outer = polygonPrismXY(
    chamferedRectanglePoints(
      panel.center,
      panel.width_mm,
      panel.height_mm,
      panel.chamfer_mm,
    ),
    z0,
    height,
    centerY,
  );
  const inner = polygonPrismXY(
    chamferedRectanglePoints(
      panel.center,
      panel.width_mm - 2 * panel.line_width_mm,
      panel.height_mm - 2 * panel.line_width_mm,
      Math.max(0.5, panel.chamfer_mm - panel.line_width_mm),
    ),
    z0 - 0.05,
    height + 0.1,
    centerY,
  );
  return outer.cut(inner);
}

function depthForClass(depthClass) {
  return depthClass === "major"
    ? reliefPattern.engraving.major_depth_mm
    : reliefPattern.engraving.secondary_depth_mm;
}

function widthForClass(depthClass) {
  return depthClass === "major"
    ? reliefPattern.engraving.major_line_width_mm
    : reliefPattern.engraving.secondary_line_width_mm;
}

function textMarkCutter(mark, centerY) {
  let drawing = r.drawText(mark.text, {
    fontSize: mark.font_size_mm,
    fontFamily: "default",
  });
  const [[x0, y0], [x1, y1]] = drawing.boundingBox.bounds;
  drawing = drawing.translate(-(x0 + x1) / 2, -(y0 + y1) / 2);
  if (mark.rotation_deg) drawing = drawing.rotate(mark.rotation_deg);
  const depth = depthForClass(mark.depth_class);
  return drawing
    .sketchOnPlane("XY", -0.1)
    .extrude(depth + 0.2)
    .translate(mark.center[0], centerY + mark.center[1], 0);
}

function expandBusLane(lane) {
  const side = lane.side;
  return [
    [side * lane.x_start_mm, lane.y_mm],
    [side * lane.x_elbow_mm, lane.y_mm],
    [side * lane.x_end_mm, lane.y_mm + lane.rise_mm],
  ];
}

function segmentCutters(points, width, z0, height, centerY) {
  const cutters = [];
  for (let index = 0; index + 1 < points.length; index += 1) {
    cutters.push(capsuleCutter(points[index], points[index + 1], width, z0, height, centerY));
  }
  return cutters;
}

function cutInBatches(shape, cutters, label, batchSize = 10) {
  let result = shape;
  const batchCount = Math.ceil(cutters.length / batchSize);
  for (let batchIndex = 0; batchIndex < batchCount; batchIndex += 1) {
    markStage(`${label}-${batchIndex + 1}-of-${batchCount}`);
    const batch = cutters.slice(batchIndex * batchSize, (batchIndex + 1) * batchSize);
    try {
      result = result.cut(batch.length === 1 ? batch[0] : r.makeCompound(batch));
    } catch (error) {
      const detail = error && error.message ? error.message : String(error);
      throw new Error(`${label} batch ${batchIndex + 1} failed: ${detail}`);
    }
  }
  return result;
}

function capsulePrismAlongX(x0, x1, p0, p1, width, centerY) {
  const [y0Local, z0] = p0;
  const [y1Local, z1] = p1;
  const y0 = centerY + y0Local;
  const y1 = centerY + y1Local;
  const dy = y1 - y0;
  const dz = z1 - z0;
  const length = Math.hypot(dy, dz);
  if (length < 1e-8) {
    return r.makeCylinder(width / 2, x1 - x0, [x0, y0, z0], [1, 0, 0]);
  }
  const ny = -dz / length * width / 2;
  const nz = dy / length * width / 2;
  const body = polygonPrismAlongX(x0, x1, [
    [y0 + ny, z0 + nz],
    [y1 + ny, z1 + nz],
    [y1 - ny, z1 - nz],
    [y0 - ny, z0 - nz],
  ]);
  const cap0 = r.makeCylinder(width / 2, x1 - x0, [x0, y0, z0], [1, 0, 0]);
  const cap1 = r.makeCylinder(width / 2, x1 - x0, [x0, y1, z1], [1, 0, 0]);
  return body.fuse(cap0).fuse(cap1);
}

function hexRingPrismAlongX(x0, x1, centerY, centerZ, outerRadius, innerRadius) {
  const outerPoints = [];
  const innerPoints = [];
  for (let index = 0; index < 6; index += 1) {
    const angle = Math.PI / 6 + index * Math.PI / 3;
    outerPoints.push([
      centerY + outerRadius * Math.cos(angle),
      centerZ + outerRadius * Math.sin(angle),
    ]);
    innerPoints.push([
      centerY + innerRadius * Math.cos(angle),
      centerZ + innerRadius * Math.sin(angle),
    ]);
  }
  const outer = polygonPrismAlongX(x0, x1, outerPoints);
  const inner = polygonPrismAlongX(x0 - 0.02, x1 + 0.02, innerPoints);
  return outer.cut(inner);
}

function polygonPrismAlongX(x0, x1, yzPoints) {
  let pen = new r.DrawingPen(yzPoints[0]);
  for (const point of yzPoints.slice(1)) pen = pen.lineTo(point);
  const drawing = pen.close();
  return drawing.sketchOnPlane("YZ", x0).extrude(x1 - x0);
}

function readClosedDxfPolylines(target) {
  const lines = fs.readFileSync(target, "utf8").split(/\r?\n/);
  const pairs = [];
  for (let i = 0; i + 1 < lines.length; i += 2) {
    pairs.push([Number(lines[i].trim()), lines[i + 1].trim()]);
  }

  const contours = [];
  let contour = null;
  let vertex = null;
  function finishVertex() {
    if (vertex && Number.isFinite(vertex.x) && Number.isFinite(vertex.y)) {
      contour.push([vertex.x, vertex.y]);
    }
    vertex = null;
  }
  function finishContour() {
    finishVertex();
    if (contour && contour.length >= 3) contours.push(contour);
    contour = null;
  }

  for (const [code, value] of pairs) {
    if (code === 0) {
      if (value === "POLYLINE") {
        finishContour();
        contour = [];
      } else if (value === "VERTEX" && contour) {
        finishVertex();
        vertex = { x: NaN, y: NaN };
      } else if (value === "SEQEND" && contour) {
        finishContour();
      }
      continue;
    }
    if (vertex && code === 10) vertex.x = Number(value);
    if (vertex && code === 20) vertex.y = Number(value);
  }
  finishContour();
  return contours;
}

function polygonSignedArea(points) {
  let area = 0;
  for (let i = 0; i < points.length; i += 1) {
    const a = points[i];
    const b = points[(i + 1) % points.length];
    area += a[0] * b[1] - b[0] * a[1];
  }
  return area / 2;
}

function pointInPolygon(point, polygon) {
  let inside = false;
  const [px, py] = point;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i, i += 1) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    const crosses = (yi > py) !== (yj > py)
      && px < (xj - xi) * (py - yi) / (yj - yi) + xi;
    if (crosses) inside = !inside;
  }
  return inside;
}

function drawingFromPolygon(points) {
  let pen = new r.DrawingPen(points[0]);
  for (const point of points.slice(1)) pen = pen.lineTo(point);
  return pen.close();
}

function buildProductionWatermarkCutter() {
  const w = P.watermark;
  const dxfPath = path.join(
    projectDir,
    "assets",
    "just-innovation-watermark",
    "exports",
    "dxf",
    "just-innovation-standard.dxf",
  );
  const sourceContours = readClosedDxfPolylines(dxfPath);
  if (!sourceContours.length) throw new Error("No closed watermark contours found in bundled DXF.");

  const contours = sourceContours.map((points) => points.map(([x, y]) => [
    (w.mirrorXForUndersideReadability ? -x : x) * w.scale + w.centerX,
    y * w.scale + w.centerY,
  ]));
  const areas = contours.map((points) => Math.abs(polygonSignedArea(points)));
  const parents = contours.map((points, index) => {
    let parent = -1;
    let parentArea = Infinity;
    for (let candidate = 0; candidate < contours.length; candidate += 1) {
      if (candidate === index || areas[candidate] <= areas[index]) continue;
      if (pointInPolygon(points[0], contours[candidate]) && areas[candidate] < parentArea) {
        parent = candidate;
        parentArea = areas[candidate];
      }
    }
    return parent;
  });
  const depths = parents.map((_, index) => {
    let depth = 0;
    let parent = parents[index];
    while (parent !== -1) {
      depth += 1;
      parent = parents[parent];
    }
    return depth;
  });

  const z0 = -w.booleanOverlap;
  // Overlap only below the original bed datum; the upper cutter face remains
  // exactly at the specified recess depth.
  const height = w.depth + w.booleanOverlap;
  const evenSolids = [];
  for (let index = 0; index < contours.length; index += 1) {
    if (depths[index] % 2 !== 0) continue;
    let solid = drawingFromPolygon(contours[index]).sketchOnPlane("XY", z0).extrude(height);
    for (let child = 0; child < contours.length; child += 1) {
      if (parents[child] !== index || depths[child] % 2 !== 1) continue;
      const hole = drawingFromPolygon(contours[child])
        .sketchOnPlane("XY", z0 - 0.01)
        .extrude(height + 0.02);
      solid = solid.cut(hole);
    }
    evenSolids.push(solid);
  }
  let cutter = evenSolids[0];
  for (const solid of evenSolids.slice(1)) cutter = cutter.fuse(solid);

  const allPoints = contours.flat();
  const bounds = [
    [Math.min(...allPoints.map((p) => p[0])), Math.min(...allPoints.map((p) => p[1]))],
    [Math.max(...allPoints.map((p) => p[0])), Math.max(...allPoints.map((p) => p[1]))],
  ];
  return {
    cutter,
    evidence: {
      source_dxf: path.relative(projectDir, dxfPath),
      source_contour_count: sourceContours.length,
      filled_region_count: evenSolids.length,
      outline_bounds_mm: bounds.map((row) => row.map((value) => Number(value.toFixed(5)))),
      outline_size_mm: [
        Number((bounds[1][0] - bounds[0][0]).toFixed(5)),
        Number((bounds[1][1] - bounds[0][1]).toFixed(5)),
      ],
    },
  };
}

function addProductionWatermark(base) {
  markStage("production-watermark-last-geometry-change");
  const watermark = buildProductionWatermarkCutter();
  probeShape(watermark.cutter, "production-watermark-cutter");
  const markedBase = base.cut(watermark.cutter);
  probeShape(markedBase, "base-watermarked");
  return { shape: markedBase, evidence: watermark.evidence };
}

function hexPinAlongX(x0, x1, centerY, centerZ, radius) {
  const points = [];
  for (let i = 0; i < 6; i += 1) {
    const angle = (-120 + i * 60) * Math.PI / 180;
    points.push([
      centerY + radius * Math.cos(angle),
      centerZ + radius * Math.sin(angle),
    ]);
  }
  return polygonPrismAlongX(x0, x1, points);
}

function engravedTextCutter(text, centerY, padTopZ) {
  let drawing = r.drawText(text, { fontSize: P.text.fontSize, fontFamily: "default" });
  const [[x0, y0], [x1, y1]] = drawing.boundingBox.bounds;
  drawing = drawing.translate(-(x0 + x1) / 2, -(y0 + y1) / 2);
  return drawing
    .sketchOnPlane("XY", padTopZ - P.text.engravingDepth)
    .extrude(P.text.engravingDepth + 0.2)
    .translateY(centerY);
}

function addSteppedPerimeterEmboss(shape, body, zCenter) {
  const band = reliefPattern.side_band;
  const fullHeight = band.emboss_height_mm;
  const stepHeight = band.ramp_step_height_mm;
  const middleHeight = fullHeight - 2 * stepHeight;
  const z0 = zCenter - fullHeight / 2;
  const parts = [
    roundedPerimeterEmboss(
      body.width,
      body.depth,
      body.cornerRadius,
      body.centerY,
      z0,
      stepHeight,
      band.ramp_step_depth_mm,
    ),
    roundedPerimeterEmboss(
      body.width,
      body.depth,
      body.cornerRadius,
      body.centerY,
      z0 + stepHeight,
      middleHeight,
      band.emboss_depth_mm,
    ),
    roundedPerimeterEmboss(
      body.width,
      body.depth,
      body.cornerRadius,
      body.centerY,
      z0 + stepHeight + middleHeight,
      stepHeight,
      band.ramp_step_depth_mm,
    ),
  ];
  return shape.fuse(r.makeCompound(parts));
}

function addLongSideTechEngraving(shape, body, zMin, zMax) {
  const band = reliefPattern.side_band;
  const sideDepth = band.engraving_depth_mm;
  const overlap = 0.08;
  const halfWidth = body.width / 2;
  const usableHalfY = body.depth / 2 - body.cornerRadius - band.keepout_from_hinge_latch_mm;
  const zSpan = zMax - zMin;
  const paths = [
    [[-0.86, 0.28], [-0.62, 0.28], [-0.52, 0.43], [-0.20, 0.43]],
    [[0.20, 0.57], [0.52, 0.57], [0.62, 0.72], [0.86, 0.72]],
    [[-0.82, 0.72], [-0.58, 0.72], [-0.48, 0.57], [-0.30, 0.57]],
    [[0.30, 0.43], [0.48, 0.43], [0.58, 0.28], [0.82, 0.28]],
  ];
  const cutters = [];
  for (const side of [-1, 1]) {
    const x0 = side > 0 ? halfWidth - sideDepth : -halfWidth - overlap;
    const x1 = side > 0 ? halfWidth + overlap : -halfWidth + sideDepth;
    for (let pathIndex = 0; pathIndex < paths.length; pathIndex += 1) {
      const points = paths[pathIndex].map(([u, v]) => [u * usableHalfY, zMin + v * zSpan]);
      for (let index = 0; index + 1 < points.length; index += 1) {
        cutters.push(capsulePrismAlongX(
          x0,
          x1,
          points[index],
          points[index + 1],
          pathIndex % 2 === 0 ? 1.0 : 0.8,
          body.centerY,
        ));
      }
    }
    for (const [u, v] of [[-0.62, 0.28], [-0.20, 0.43], [0.20, 0.57], [0.62, 0.72]]) {
      cutters.push(hexRingPrismAlongX(
        x0,
        x1,
        body.centerY + u * usableHalfY,
        zMin + v * zSpan,
        1.55,
        0.72,
      ));
    }
  }
  let result = shape;
  for (let index = 0; index < cutters.length; index += 1) {
    try {
      result = result.cut(cutters[index]);
    } catch (error) {
      const detail = error && error.message ? error.message : String(error);
      throw new Error(`long-side tech cutter ${index} failed: ${detail}`);
    }
  }
  return result;
}

function buildBaseShell() {
  markStage("base-shell-outer");
  const b = P.base;
  const outer = roundedPrism(b.width, b.depth, b.cornerRadius, 0, b.height, 0, b.centerY);
  const inner = roundedPrism(
    b.width - 2 * b.wall,
    b.depth - 2 * b.wall,
    b.cornerRadius - b.wall,
    b.floor,
    b.height + 2,
    0,
    b.centerY,
  );
  let base = outer.cut(inner);

  markStage("base-shell-side-bands");
  const band = reliefPattern.side_band;
  for (const zCenter of band.base_engrave_z_centers_mm) {
    markStage(`base-shell-side-groove-${zCenter}`);
    base = base.cut(roundedPerimeterCutter(
      b.width,
      b.depth,
      b.cornerRadius,
      b.centerY,
      zCenter - band.trace_height_mm / 2,
      band.trace_height_mm,
      band.engraving_depth_mm,
    ));
  }
  markStage("base-shell-side-local-tech");
  base = addLongSideTechEngraving(base, b, 3.2, 12.2);
  markStage("base-shell-side-emboss");
  base = addSteppedPerimeterEmboss(base, b, band.base_emboss_z_center_mm);
  markStage("base-shell-side-complete");
  return base;
}

function buildNozzleStorage(base) {
  markStage("base-storage-primitives");
  const n = P.nozzle;
  const b = P.base;
  const additions = [];
  const textCutters = [];
  const padTop = b.floor + P.text.padHeight;
  const slotCenters = [];

  n.labelCentersLocalY.forEach((labelLocalY, groupIndex) => {
    const labelY = b.centerY + labelLocalY;
    additions.push(
      roundedPrism(
        P.text.padWidth,
        P.text.padDepth,
        1.6,
        b.floor - 0.05,
        P.text.padHeight + 0.05,
        0,
        labelY,
      ),
    );
    textCutters.push(engravedTextCutter(n.labels[groupIndex], labelY, padTop));

    for (const offset of n.slotOffsetsFromLabelY) {
      const yc = b.centerY + labelLocalY + offset;
      slotCenters.push(yc);
      additions.push(box(
        n.rearStopX[0], n.rearStopX[1],
        yc - 3.9, yc + 3.9,
        b.floor - 0.05, n.axisZ,
      ));

      for (const [xRange, diameter] of [
        [n.upperSaddleX, n.upperDiameter],
        [n.lowerSaddleX, n.lowerDiameter],
      ]) {
        let saddle = box(
          xRange[0], xRange[1],
          yc - n.saddleWidth / 2, yc + n.saddleWidth / 2,
          b.floor - 0.05, n.axisZ,
        );
        const grooveRadius = diameter / 2 + n.fitClearanceEachSide;
        const groove = r.makeCylinder(
          grooveRadius,
          xRange[1] - xRange[0] + 1.0,
          [xRange[0] - 0.5, yc, n.axisZ],
          [1, 0, 0],
        );
        saddle = saddle.cut(groove);
        additions.push(saddle);
      }
    }
  });

  markStage("base-storage-fuse");
  let result = base.fuse(r.makeCompound(additions));
  probeShape(result, "base-storage-before-text");
  markStage("base-storage-text-cut");
  result = result.cut(r.makeCompound(textCutters));
  return { shape: result, slotCenters };
}

function buildBaseHinge(base) {
  markStage("base-hinge");
  const h = P.hinge;
  const parts = [];
  for (const [x0, x1] of h.baseSegments) {
    const barrel = r.makeCylinder(
      h.outerRadius,
      x1 - x0,
      [x0, h.axisY, h.axisZ],
      [1, 0, 0],
    );
    const hole = r.makeCylinder(
      h.holeRadius,
      x1 - x0 + 0.4,
      [x0 - 0.2, h.axisY, h.axisZ],
      [1, 0, 0],
    );
    const strap = box(x0, x1, -4.7, -1.0, 5.8, 12.2);
    // Cut the pin channel after fusing the support strap so the strap cannot
    // accidentally refill the lower half of the clearance bore.
    parts.push(barrel.fuse(strap).cut(hole));
  }
  return fuseAll(base, parts);
}

function buildBaseLatchCatch(base) {
  markStage("base-latch-catch");
  const x0 = -5.5;
  const x1 = 5.5;
  const yz = [
    [-189.5, 10.6],
    [-188.15, 10.6],
    [-188.15, 12.2],
    [-189.15, 12.2],
  ];
  const catchShape = polygonPrismAlongX(x0, x1, yz);
  return base.fuse(catchShape);
}

function buildBase() {
  let base = buildBaseShell();
  probeShape(base, "base-shell");
  const storage = buildNozzleStorage(base);
  probeShape(storage.shape, "base-storage");
  base = buildBaseHinge(storage.shape);
  probeShape(base, "base-hinge");
  base = buildBaseLatchCatch(base);
  probeShape(base, "base-catch");
  return { shape: base, slotCenters: storage.slotCenters };
}

function buildLidShell() {
  markStage("lid-shell");
  const l = P.lid;
  let lid = roundedPrism(
    l.outerWidth,
    l.outerDepth,
    l.outerRadius,
    0,
    l.plate,
    0,
    l.centerY,
  );
  let skirt = roundedPrism(
    l.outerWidth,
    l.outerDepth,
    l.outerRadius,
    l.plate,
    l.skirtHeight,
    0,
    l.centerY,
  );
  const skirtVoid = roundedPrism(
    l.innerWidth,
    l.innerDepth,
    l.innerRadius,
    l.plate - 0.1,
    l.skirtHeight + 0.2,
    0,
    l.centerY,
  );
  skirt = skirt.cut(skirtVoid);
  lid = lid.fuse(skirt);

  const band = reliefPattern.side_band;
  const lidBandBody = {
    width: l.outerWidth,
    depth: l.outerDepth,
    cornerRadius: l.outerRadius,
    centerY: l.centerY,
  };
  for (const zCenter of band.lid_engrave_z_centers_mm) {
    markStage(`lid-shell-side-groove-${zCenter}`);
    lid = lid.cut(roundedPerimeterCutter(
      l.outerWidth,
      l.outerDepth,
      l.outerRadius,
      l.centerY,
      zCenter - band.trace_height_mm / 2,
      band.trace_height_mm,
      band.engraving_depth_mm,
    ));
  }
  markStage("lid-shell-side-local-tech");
  lid = addLongSideTechEngraving(lid, lidBandBody, 3.35, 8.75);
  markStage("lid-shell-side-emboss");
  lid = addSteppedPerimeterEmboss(lid, lidBandBody, band.lid_emboss_z_center_mm);
  markStage("lid-shell-side-complete");
  return lid;
}

function addLidCyberEngraving(lid) {
  markStage("lid-cyber-cutters");
  const l = P.lid;
  const z0 = -0.1;
  const byClass = { major: [], secondary: [] };

  for (const frame of reliefPattern.perimeter_frames) {
    const depth = depthForClass(frame.depth_class);
    const outer = roundedPrism(
      frame.width_mm,
      frame.height_mm,
      frame.radius_mm,
      z0,
      depth + 0.2,
      0,
      l.centerY,
    );
    const inner = roundedPrism(
      frame.width_mm - 2 * frame.line_width_mm,
      frame.height_mm - 2 * frame.line_width_mm,
      Math.max(0.5, frame.radius_mm - frame.line_width_mm),
      z0 - 0.05,
      depth + 0.3,
      0,
      l.centerY,
    );
    byClass[frame.depth_class].push(outer.cut(inner));
  }

  for (const ring of reliefPattern.reactor_rings) {
    const depth = depthForClass(ring.depth_class);
    byClass[ring.depth_class].push(hexRingCutter(
      ring.outer_radius_mm,
      ring.inner_radius_mm,
      z0,
      depth + 0.2,
      ring.center[0],
      l.centerY + ring.center[1],
      ring.rotation_deg,
    ));
  }

  for (const panel of reliefPattern.panel_frames) {
    const depth = depthForClass(panel.depth_class);
    byClass[panel.depth_class].push(chamferedPanelFrameCutter(
      panel,
      z0,
      depth + 0.2,
      l.centerY,
    ));
  }

  for (const lane of reliefPattern.bus_lanes) {
    const depth = depthForClass(lane.depth_class);
    byClass[lane.depth_class].push(...segmentCutters(
      expandBusLane(lane),
      widthForClass(lane.depth_class),
      z0,
      depth + 0.2,
      l.centerY,
    ));
  }

  for (const bus of reliefPattern.vertical_buses) {
    const depth = depthForClass(bus.depth_class);
    byClass[bus.depth_class].push(capsuleCutter(
      [bus.x_mm, bus.y0_mm],
      [bus.x_mm, bus.y1_mm],
      widthForClass(bus.depth_class),
      z0,
      depth + 0.2,
      l.centerY,
    ));
  }

  for (const field of reliefPattern.microhex_fields) {
    for (let row = 0; row < field.rows; row += 1) {
      for (let column = 0; column < field.columns; column += 1) {
        const x = field.origin[0]
          + column * field.pitch_x_mm
          + (row % 2) * field.pitch_x_mm / 2;
        const y = field.origin[1] + row * field.pitch_y_mm;
        byClass.secondary.push(hexRingCutter(
          reliefPattern.microhex_outer_radius_mm,
          reliefPattern.microhex_inner_radius_mm,
          z0,
          depthForClass("secondary") + 0.2,
          x,
          l.centerY + y,
          30,
        ));
      }
    }
  }

  for (const node of reliefPattern.node_rings) {
    byClass[node.depth_class].push(hexRingCutter(
      node.outer_radius_mm,
      node.inner_radius_mm,
      z0,
      depthForClass(node.depth_class) + 0.2,
      node.center[0],
      l.centerY + node.center[1],
      0,
    ));
  }

  for (const bank of reliefPattern.tick_banks) {
    const angle = bank.angle_deg * Math.PI / 180;
    const dx = Math.cos(angle) * bank.length_mm / 2;
    const dy = Math.sin(angle) * bank.length_mm / 2;
    for (let index = 0; index < bank.count; index += 1) {
      const x = bank.center[0] + (index - (bank.count - 1) / 2) * bank.spacing_mm;
      byClass.secondary.push(capsuleCutter(
        [x - dx, bank.center[1] - dy],
        [x + dx, bank.center[1] + dy],
        0.8,
        z0,
        depthForClass("secondary") + 0.2,
        l.centerY,
      ));
    }
  }

  for (const bank of reliefPattern.chevron_banks) {
    for (let index = 0; index < bank.count; index += 1) {
      const x = bank.center[0] + bank.direction * index * bank.size_mm * 0.8;
      const points = [
        [x - bank.direction * bank.size_mm / 2, bank.center[1] - bank.size_mm / 2],
        [x + bank.direction * bank.size_mm / 2, bank.center[1]],
        [x - bank.direction * bank.size_mm / 2, bank.center[1] + bank.size_mm / 2],
      ];
      byClass.major.push(...segmentCutters(
        points,
        0.9,
        z0,
        depthForClass("major") + 0.2,
        l.centerY,
      ));
    }
  }

  markStage("lid-cyber-major-cut");
  const majorTool = r.makeCompound(byClass.major);
  probeShape(majorTool, "lid-cyber-major-tool");
  let result = lid.cut(majorTool);
  markStage("lid-cyber-secondary-cut");
  result = cutInBatches(result, byClass.secondary, "lid-cyber-secondary-feature", 1);

  markStage("lid-cyber-exact-text");
  for (const mark of reliefPattern.text_marks) {
    result = result.cut(textMarkCutter(mark, l.centerY));
  }
  return result;
}

function cutLidHingeWindows(lid) {
  markStage("lid-hinge-windows");
  const windows = [];
  for (const [x0, x1] of P.hinge.baseSegments) {
    windows.push(box(x0 - 0.3, x1 + 0.3, 0.7, 4.2, 3.1, 13.2));
  }
  return cutAll(lid, windows);
}

function addLidHinge(lid) {
  markStage("lid-hinge-fuse");
  const h = P.hinge;
  const parts = [];
  for (const [x0, x1] of h.lidSegments) {
    parts.push(r.makeCylinder(
      h.outerRadius,
      x1 - x0,
      [x0, h.axisY, h.axisZ],
      [1, 0, 0],
    ));
  }
  parts.push(hexPinAlongX(-30.0, 30.0, h.axisY, h.axisZ, h.pinCircumRadius));
  markStage("lid-hinge-subassembly");
  let hingeSubassembly = parts[0];
  for (const part of parts.slice(1)) hingeSubassembly = hingeSubassembly.fuse(part);
  markStage("lid-hinge-to-shell");
  return lid.fuse(hingeSubassembly);
}

function addLidGroupRibs(lid) {
  markStage("lid-group-ribs");
  const baseLocalBoundaries = [-39.4, 3.6, 46.6];
  const ribs = baseLocalBoundaries.map((boundary) => {
    const openY = P.lid.centerY - boundary;
    return box(-26.0, 26.0, openY - 0.7, openY + 0.7, P.lid.plate, 6.0);
  });
  return lid.fuse(r.makeCompound(ribs), { optimisation: "commonFace" });
}

function addLidLatch(lid) {
  markStage("lid-latch");
  const l = P.lid;
  const outerFront = l.centerY + l.outerDepth / 2;
  const innerFront = l.centerY + l.innerDepth / 2;

  const window = box(-20.5, 20.5, innerFront - 0.5, outerFront + 1.0, 3.2, 9.2);
  let result = lid.cut(window);

  const armY0 = 190.15;
  const armY1 = armY0 + P.latch.armThickness;
  const z0 = 4.0;
  const z1 = z0 + P.latch.armHeight;
  const additions = [
    box(-20.5, -17.0, 188.7, 191.5, 3.2, 9.0),
    box(17.0, 20.5, 188.7, 191.5, 3.2, 9.0),
    box(-18.0, -3.5, armY0, armY1, z0, z1),
    box(3.5, 18.0, armY0, armY1, z0, z1),
    box(-4.5, 4.5, 189.8, 192.3, 3.8, 9.0),
    r.makeCylinder(P.latch.rootRadius, P.latch.armHeight, [-17.5, (armY0 + armY1) / 2, z0]),
    r.makeCylinder(P.latch.rootRadius, P.latch.armHeight, [17.5, (armY0 + armY1) / 2, z0]),
    box(-3.4, 3.4, 192.15, 192.75, 4.5, 8.5),
  ];

  const hook = polygonPrismAlongX(-4.8, 4.8, [
    [188.8, 7.4],
    [190.3, 7.4],
    [190.3, 8.5],
    [189.4, 8.5],
  ]);
  additions.push(hook);
  // These pieces form one flexure chain.  Fuse them successively so overlapping
  // arms, roots, carrier, hook and hard stop are topologically one lid body.
  result = fuseAll(result, additions);
  return result;
}

function buildLid() {
  let lid = buildLidShell();
  probeShape(lid, "lid-shell");
  lid = cutLidHingeWindows(lid);
  probeShape(lid, "lid-windows");
  lid = addLidHinge(lid);
  probeShape(lid, "lid-hinge");
  lid = addLidGroupRibs(lid);
  probeShape(lid, "lid-ribs");
  lid = addLidLatch(lid);
  probeShape(lid, "lid-latch");
  // Dense R4 line art is applied after controlled STL tessellation as a
  // closed height-map cutter. Keeping it out of the B-Rep avoids thousands of
  // fragile faces while preserving the exact functional STEP master.
  markStage("lid-dense-relief-deferred-to-mesh-pipeline");
  probeShape(lid, "lid-pre-dense-relief");
  return lid;
}

function buildHingeCoupon() {
  const h = P.hinge;
  let couponBase = box(-16, 16, -18, -4.2, 0, 3.0);
  let baseBarrel = r.makeCylinder(h.outerRadius, 11.0, [-5.5, 0, h.axisZ], [1, 0, 0]);
  baseBarrel = baseBarrel.fuse(box(-5.5, 5.5, -4.7, -1.0, 5.8, 12.2));
  baseBarrel = baseBarrel.cut(
    r.makeCylinder(h.holeRadius, 11.4, [-5.7, 0, h.axisZ], [1, 0, 0]),
  );
  const baseCouponWeb = box(-5.5, 5.5, -5.0, -4.0, 2.8, 12.2);
  couponBase = couponBase.fuse(baseBarrel).fuse(baseCouponWeb);

  let couponLid = box(-16, 16, 1.45, 18, 0, 3.0);
  couponLid = couponLid.fuse(r.makeCylinder(h.outerRadius, 9.5, [-15.5, 0, h.axisZ], [1, 0, 0]));
  couponLid = couponLid.fuse(r.makeCylinder(h.outerRadius, 9.5, [6.0, 0, h.axisZ], [1, 0, 0]));
  couponLid = couponLid.fuse(hexPinAlongX(-15.5, 15.5, 0, h.axisZ, h.pinCircumRadius));
  couponLid = couponLid.fuse(box(-16, 16, 1.0, 2.0, 2.8, 12.2));
  return { base: couponBase, lid: couponLid };
}

async function writeBlob(target, blob) {
  fs.writeFileSync(target, Buffer.from(await blob.arrayBuffer()));
}

function shapeStats(shape) {
  const bounds = shape.boundingBox.bounds.map((p) => p.map((v) => Number(v.toFixed(5))));
  const volume = r.measureShapeVolumeProperties(shape).volume;
  const mesh = shape.mesh({
    tolerance: P.manufacturing.stlTolerance,
    angularTolerance: P.manufacturing.angularTolerance,
  });
  return {
    bounds_mm: bounds,
    size_mm: bounds[1].map((v, i) => Number((v - bounds[0][i]).toFixed(5))),
    volume_mm3: Number(volume.toFixed(5)),
    face_count: shape.faces.length,
    mesh_vertex_rows: mesh.vertices.length / 3,
    mesh_triangle_count: mesh.triangles.length / 3,
  };
}

async function main() {
  assertParameters();
  process.stderr.write("CAD_STAGE build-base\n");
  const baseResult = buildBase();
  process.stderr.write("CAD_STAGE build-lid\n");
  const lid = buildLid();
  // The product mark is deliberately the final geometry operation after all
  // functional and decorative geometry has stabilized.
  const markedBase = addProductionWatermark(baseResult.shape);
  const base = markedBase.shape;
  process.stderr.write("CAD_STAGE build-assemblies\n");
  const assembly = r.makeCompound([base.clone(), lid.clone()]);
  const hingeCoupon = buildHingeCoupon();
  const couponAssembly = r.makeCompound([
    hingeCoupon.base.clone(),
    hingeCoupon.lid.clone(),
  ]);

  const prefix = "cyber_nozzle_case_R4_DRAFT";
  process.stderr.write("CAD_STAGE export-stl\n");
  markStage("export-base-stl");
  await writeBlob(
    path.join(exportDir, `${prefix}_base.stl`),
    base.blobSTL({
      tolerance: P.manufacturing.stlTolerance,
      angularTolerance: P.manufacturing.angularTolerance,
      binary: true,
    }),
  );
  markStage("export-lid-stl");
  await writeBlob(
    path.join(exportDir, `${prefix}_lid.stl`),
    lid.blobSTL({
      tolerance: P.manufacturing.stlTolerance,
      angularTolerance: P.manufacturing.angularTolerance,
      binary: true,
    }),
  );
  markStage("export-assembly-stl");
  await writeBlob(
    path.join(exportDir, `${prefix}_print_in_place.stl`),
    assembly.blobSTL({
      tolerance: P.manufacturing.stlTolerance,
      angularTolerance: P.manufacturing.angularTolerance,
      binary: true,
    }),
  );
  markStage("export-hinge-coupon-stl");
  await writeBlob(
    path.join(exportDir, "hinge_coupon_R4_DRAFT.stl"),
    couponAssembly.blobSTL({
      tolerance: P.manufacturing.stlTolerance,
      angularTolerance: P.manufacturing.angularTolerance,
      binary: true,
    }),
  );
  process.stderr.write("CAD_STAGE export-step\n");
  await writeBlob(
    path.join(exportDir, `${prefix}.step`),
    r.exportSTEP([
      { shape: base.clone(), name: "CyberVault Base" },
      { shape: lid.clone(), name: "CyberVault Lid with captive printed pin" },
    ], { unit: "MM", modelUnit: "MM" }),
  );

  process.stderr.write("CAD_STAGE collision-check-deferred-to-independent-mesh-validator\n");

  const armStrain = 1.5 * P.latch.armThickness * P.latch.designDeflection
    / (P.latch.armLength ** 2);
  const assumedPetgModulusMpa = 1500;
  const armForceEachN = assumedPetgModulusMpa
    * P.latch.armHeight
    * (P.latch.armThickness ** 3)
    * P.latch.designDeflection
    / (4 * (P.latch.armLength ** 3));

  process.stderr.write("CAD_STAGE report\n");
  const report = {
    geometry_revision: P.revision,
    release_status: "DRAFT — REVISION 4 COMPLETE RELEASE APPROVAL PENDING",
    units: "mm",
    qualified_nozzle_fit_clearance_each_side_mm: P.nozzle.fitClearanceEachSide,
    body_count: 2,
    base: shapeStats(base),
    lid: shapeStats(lid),
    open_print_envelope_mm: shapeStats(assembly).size_mm,
    hinge_coupon_envelope_mm: shapeStats(couponAssembly).size_mm,
    nozzle_slot_centers_global_y_mm: baseResult.slotCenters.map((v) => Number(v.toFixed(3))),
    hinge: {
      pin_profile: "regular hexagon, flat-bottom print orientation",
      pin_circumradius_mm: P.hinge.pinCircumRadius,
      hole_radius_mm: P.hinge.holeRadius,
      minimum_radial_clearance_mm: P.hinge.radialClearance,
      axial_clearance_mm: P.hinge.axialClearance,
      captured_pin_body: "lid",
    },
    latch_preliminary_calculation: {
      model: "two symmetric rectangular in-plane cantilever arms",
      design_deflection_mm: P.latch.designDeflection,
      strain_each_arm: Number(armStrain.toFixed(6)),
      strain_percent: Number((armStrain * 100).toFixed(3)),
      assumed_modulus_mpa: assumedPetgModulusMpa,
      estimated_force_each_arm_n: Number(armForceEachN.toFixed(3)),
      estimated_total_force_n: Number((2 * armForceEachN).toFixed(3)),
      evidence_limit: "Preliminary only; printed PETG coupon and cycle test required.",
    },
    collision_volume_mm3: {
      open: null,
      closed_rigid_nominal: null,
      note: "Computed after export by the independent mesh validator; latch engagement remains a compliant physical test.",
    },
    relief: {
      top_major_depth_mm: reliefPattern.engraving.major_depth_mm,
      top_secondary_depth_mm: reliefPattern.engraving.secondary_depth_mm,
      side_engraving_depth_mm: reliefPattern.side_band.engraving_depth_mm,
      side_emboss_depth_mm: reliefPattern.side_band.emboss_depth_mm,
      minimum_base_wall_after_side_engraving_mm: P.base.wall - reliefPattern.side_band.engraving_depth_mm,
      minimum_lid_plate_after_top_engraving_mm: P.lid.plate - reliefPattern.engraving.major_depth_mm,
      decorated_lid_cell_coverage_fraction: 0.85239,
      geometry_source: "relief/pattern_geometry.json",
    },
    physical_qualification: {
      nozzle_fit: "PASS — user selected two-dot 0.35 mm coupon",
      hinge: "PASS BASIC FUNCTION — user confirmed fit on 2026-08-11; cycle count not reported",
      latch: "PASS BASIC FUNCTION — user confirmed fit on 2026-08-11; cycle count not reported",
      full_case: "PARTIAL — mechanism fit confirmed; loaded inversion and long-term cycles not reported",
    },
    watermark: {
      asset_id: P.watermark.assetId,
      variant: P.watermark.variant,
      operation: "recessed",
      surface: "base print-bed-facing underside",
      nominal_profile_envelope_mm: P.watermark.nominalEnvelope,
      uniform_scale: P.watermark.scale,
      rotation_deg: P.watermark.rotationDeg,
      mirrored_x_for_finished_underside_readability: P.watermark.mirrorXForUndersideReadability,
      center_mm: [P.watermark.centerX, P.watermark.centerY, 0],
      depth_mm: P.watermark.depth,
      unchanged_bed_datum_z_mm: 0,
      local_floor_before_mm: P.base.floor,
      local_floor_after_mm: P.base.floor - P.watermark.depth,
      candidate_safe_rectangle_mm: P.watermark.candidateSafeRectangle,
      selector: "reports/watermark-selection.json",
      ...markedBase.evidence,
    },
  };
  fs.writeFileSync(
    path.join(reportDir, "production-cad-candidate.json"),
    `${JSON.stringify(report, null, 2)}\n`,
    "utf8",
  );
  fs.writeFileSync(
    path.join(reportDir, "production-parameters.json"),
    `${JSON.stringify(P, null, 2)}\n`,
    "utf8",
  );
  await new Promise((resolve, reject) => {
    process.stdout.write(`${JSON.stringify(report, null, 2)}\n`, (error) => {
      if (error) reject(error);
      else resolve();
    });
  });
}

try {
  await main();
  // OpenCascade's vendor WASM binding can throw from a late destructor during
  // Node shutdown even after every export is safely written.  Exiting after
  // stdout flushes avoids that non-model-related teardown fault.
  process.exit(0);
} catch (error) {
  const message = error && error.message ? error.message : String(error);
  process.stderr.write(`CAD_BUILD_FAILED ${message}\n`);
  process.exit(1);
}
