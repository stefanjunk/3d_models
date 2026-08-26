import { createRequire } from "node:module";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { strToU8, zipSync } from "fflate";
import ManifoldModule from "manifold-3d";
import sharp from "sharp";

const here = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(here, "..");
const exportsRoot = path.join(projectRoot, "exports");
const validationRoot = path.join(projectRoot, "validation");

// replicad-opencascadejs 0.23.0 is an ESM bundle that still expects these
// Node globals. The postinstall script marks the package explicitly as ESM.
globalThis.require = createRequire(import.meta.url);
const ocPackagePath = globalThis.require.resolve(
  "replicad-opencascadejs/package.json",
);
globalThis.__dirname = path.join(path.dirname(ocPackagePath), "src");
globalThis.__filename = path.join(globalThis.__dirname, "replicad_single.js");

const { default: initOpenCascade } = await import("replicad-opencascadejs");
const cad = await import("replicad");
cad.setOC(await initOpenCascade());
const manifold = await ManifoldModule();
cad.setManifold(manifold);

const {
  drawCircle,
  drawRoundedRectangle,
  measureVolume,
} = cad;

const RELEASE_DATE = "2026-08-10";
const RELEASE_ID = "JSI-WM-001-R1";
const STROKE = 0.8;
const CLEAR_GAP = 0.6;
const CUTTER_DEPTH = 0.4;
const SQRT3 = Math.sqrt(3);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function round(value, digits = 5) {
  return Number(value.toFixed(digits));
}

function capsuleSegment(a, b, width = STROKE) {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const length = Math.hypot(dx, dy);
  assert(length > 1e-8, "Capsule segment must have positive length");
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  return drawRoundedRectangle(length + width, width, width / 2)
    .rotate(angle)
    .translate([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]);
}

function mergeDrawings(drawings) {
  assert(drawings.length > 0, "At least one drawing is required");
  let result = drawings[0];
  for (let i = 1; i < drawings.length; i += 1) {
    result = result.fuse(drawings[i]);
  }
  return result;
}

function polyline(points, width = STROKE, closed = false) {
  assert(points.length >= 2, "Polyline needs at least two points");
  const segments = [];
  for (let i = 0; i < points.length - 1; i += 1) {
    segments.push(capsuleSegment(points[i], points[i + 1], width));
  }
  if (closed) {
    segments.push(capsuleSegment(points.at(-1), points[0], width));
  }
  return mergeDrawings(segments);
}

function transformPoints(points, scale, offset = [0, 0]) {
  return points.map(([x, y]) => [x * scale + offset[0], y * scale + offset[1]]);
}

function jsMonogram(acrossFlats = 10, stroke = STROKE) {
  assert(acrossFlats >= 8, "Compact monogram is qualified only from 8 mm AF");
  assert(stroke >= STROKE, "Stroke must be at least 0.80 mm");

  const centerlineAF = acrossFlats - stroke;
  const radius = centerlineAF / SQRT3;
  const hex = [
    [-radius, 0],
    [-radius / 2, centerlineAF / 2],
    [radius / 2, centerlineAF / 2],
    [radius, 0],
    [radius / 2, -centerlineAF / 2],
    [-radius / 2, -centerlineAF / 2],
  ];

  const internalScale = centerlineAF / 9.2;
  const j = transformPoints(
    [
      [-3.15, 2.35],
      [-1.25, 2.35],
      [-1.25, -1.15],
      [-1.45, -1.85],
      [-2.05, -2.25],
      [-2.7, -2.25],
      [-3.1, -1.75],
    ],
    internalScale,
  );
  const s = transformPoints(
    [
      [3.05, 2.15],
      [2.45, 2.42],
      [1.45, 2.42],
      [0.75, 2.05],
      [0.5, 1.35],
      [0.8, 0.7],
      [1.45, 0.35],
      [2.25, 0.15],
      [2.85, -0.2],
      [3.15, -0.8],
      [3.0, -1.5],
      [2.45, -2.05],
      [1.55, -2.3],
      [0.65, -2.15],
    ],
    internalScale,
  );

  return mergeDrawings([
    polyline(hex, stroke, true),
    polyline(j, stroke),
    polyline(s, stroke),
  ]);
}

const GLYPH_PATHS = {
  A: [
    [[0, 0], [0.5, 1], [1, 0]],
    [[0.22, 0.5], [0.78, 0.5]],
  ],
  D: [
    [[0, 0], [0, 1], [0.62, 1], [1, 0.75], [1, 0.25], [0.62, 0], [0, 0]],
  ],
  I: [
    [[0, 1], [1, 1]],
    [[0.5, 1], [0.5, 0]],
    [[0, 0], [1, 0]],
  ],
  J: [
    [[0, 1], [1, 1], [1, 0.25], [0.72, 0], [0.25, 0], [0, 0.28]],
  ],
  N: [
    [[0, 0], [0, 1], [1, 0], [1, 1]],
  ],
  O: [
    [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]],
  ],
  S: [
    [[1, 0.88], [0.72, 1], [0.22, 1], [0, 0.78], [0.18, 0.55], [0.82, 0.45], [1, 0.22], [0.78, 0], [0.22, 0], [0, 0.12]],
  ],
  T: [
    [[0, 1], [1, 1]],
    [[0.5, 1], [0.5, 0]],
  ],
  U: [
    [[0, 1], [0, 0.22], [0.22, 0], [0.78, 0], [1, 0.22], [1, 1]],
  ],
  V: [
    [[0, 1], [0.5, 0], [1, 1]],
  ],
  "0": [
    [[0.2, 0], [0, 0.2], [0, 0.8], [0.2, 1], [0.8, 1], [1, 0.8], [1, 0.2], [0.8, 0], [0.2, 0]],
    [[0.18, 0.15], [0.82, 0.85]],
  ],
  "1": [
    [[0.22, 0.78], [0.5, 1], [0.5, 0]],
    [[0.15, 0], [0.85, 0]],
  ],
  "2": [
    [[0, 0.78], [0.2, 1], [0.8, 1], [1, 0.78], [1, 0.58], [0, 0], [1, 0]],
  ],
  "3": [
    [[0, 0.9], [0.2, 1], [0.8, 1], [1, 0.78], [0.72, 0.52], [1, 0.25], [0.8, 0], [0.2, 0], [0, 0.1]],
  ],
  "4": [
    [[0.85, 0], [0.85, 1]],
    [[0.85, 0.42], [0, 0.42], [0.68, 1]],
  ],
  "5": [
    [[1, 1], [0, 1], [0, 0.55], [0.78, 0.55], [1, 0.32], [0.82, 0], [0.18, 0], [0, 0.12]],
  ],
  "6": [
    [[0.9, 0.9], [0.7, 1], [0.22, 1], [0, 0.72], [0, 0.2], [0.2, 0], [0.78, 0], [1, 0.22], [0.82, 0.52], [0, 0.52]],
  ],
  "7": [
    [[0, 1], [1, 1], [0.35, 0]],
  ],
  "8": [
    [[0.2, 0.5], [0, 0.72], [0.2, 1], [0.8, 1], [1, 0.72], [0.8, 0.5], [0.2, 0.5], [0, 0.25], [0.2, 0], [0.8, 0], [1, 0.25], [0.8, 0.5]],
  ],
  "9": [
    [[0.1, 0.1], [0.3, 0], [0.78, 0], [1, 0.28], [1, 0.8], [0.8, 1], [0.22, 1], [0, 0.78], [0.18, 0.48], [1, 0.48]],
  ],
  "-": [
    [[0.1, 0.5], [0.9, 0.5]],
  ],
};

function glyph(character, width, height, stroke = STROKE) {
  const paths = GLYPH_PATHS[character];
  assert(paths, `Unsupported vector glyph: ${character}`);
  return mergeDrawings(
    paths.map((points) =>
      polyline(points.map(([x, y]) => [x * width, y * height]), stroke),
    ),
  );
}

function vectorText(
  text,
  {
    cellWidth = 1.6,
    cellHeight = 3.0,
    pitch = 3.0,
    stroke = STROKE,
    origin = [0, 0],
  } = {},
) {
  const segments = [];
  const seen = new Set();
  for (let i = 0; i < text.length; i += 1) {
    const paths = GLYPH_PATHS[text[i]];
    assert(paths, `Unsupported vector glyph: ${text[i]}`);
    for (const points of paths) {
      const transformed = points.map(([x, y]) => [
        origin[0] + i * pitch + x * cellWidth,
        origin[1] + y * cellHeight,
      ]);
      for (let j = 0; j < transformed.length - 1; j += 1) {
        const a = transformed[j];
        const b = transformed[j + 1];
        const aKey = `${round(a[0], 6)},${round(a[1], 6)}`;
        const bKey = `${round(b[0], 6)},${round(b[1], 6)}`;
        const key = aKey < bKey ? `${aKey}|${bKey}` : `${bKey}|${aKey}`;
        if (!seen.has(key)) {
          seen.add(key);
          segments.push(capsuleSegment(a, b, stroke));
        }
      }
    }
  }
  return mergeDrawings(segments);
}

function justWord(stroke = STROKE) {
  const x = -0.85;
  const y = 1.3;
  const pitch = 3.4;
  const j = glyph("J", 2.0, 3.2, stroke).translate([x, y]);
  const u = glyph("U", 2.0, 2.4, stroke).translate([x + pitch, y]);
  const s = glyph("S", 2.0, 3.2, stroke).translate([x + 2 * pitch, y]);
  const t = glyph("T", 2.0, 2.8, stroke).translate([x + 3 * pitch, y]);
  return mergeDrawings([j, u, s, t]);
}

function innovationWord(stroke = STROKE) {
  // The 32 mm production profile uses two rows so every glyph keeps the
  // approved 0.80 mm stroke and 0.60 mm horizontal clear gap.
  return mergeDrawings([
    vectorText("INNO", {
      cellWidth: 1.6,
      cellHeight: 1.4,
      pitch: 3.0,
      stroke,
      origin: [-0.45, -1.5],
    }),
    vectorText("VATION", {
      cellWidth: 1.6,
      cellHeight: 1.4,
      pitch: 3.0,
      stroke,
      origin: [-3.45, -4.3],
    }),
  ]);
}

function standardMark(stroke = STROKE) {
  const monogram = jsMonogram(8.4, stroke).translate([-10.95, 0]);
  const word = justWord(stroke);
  const innovation = innovationWord(stroke);
  return mergeDrawings([monogram, word, innovation]);
}

function traceMark(code, targetWidth, stroke = STROKE) {
  assert(code.length > 0, "Trace code cannot be empty");
  const minimumWidth = 33.4 + 3 * code.length;
  assert(
    targetWidth >= minimumWidth,
    `Trace width ${targetWidth} mm is below ${minimumWidth.toFixed(1)} mm for ${code}`,
  );
  const standardShift = 15.99 - targetWidth / 2;
  const separatorX = 15.0 + standardShift;
  const codeStart = separatorX + 1.4;
  return mergeDrawings([
    standardMark(stroke).translate([standardShift, 0]),
    capsuleSegment([separatorX, -3.2], [separatorX, 3.2], stroke),
    vectorText(code, {
      cellWidth: 1.6,
      cellHeight: 3.0,
      pitch: 3.0,
      stroke,
      origin: [codeStart, -1.5],
    }),
  ]);
}

function cutterFromDrawing(drawing, depth = CUTTER_DEPTH) {
  assert(depth >= 0.2, "Cutter depth must be at least one 0.20 mm layer");
  return drawing.sketchOnPlane("XY").extrude(depth);
}

function undersideCutter(drawing, depth) {
  return drawing
    .sketchOnPlane("XY", -0.01)
    .extrude(depth + 0.02);
}

function makeCoupon() {
  console.log("build: six-tile coupon set");
  const standardCenters = [-38, 0, 38];
  const depths = [0.2, 0.4, 0.6];
  const tiles = [];
  const meshTiles = [];
  for (let i = 0; i < standardCenters.length; i += 1) {
    console.log(`build: coupon standard ${i} depth ${depths[i]}`);
    const center = [standardCenters[i], 11];
    const tileDrawing = drawRoundedRectangle(34, 18, 2.5).translate(center);
    const tile = tileDrawing.sketchOnPlane("XY").extrude(2.4);
    const mark = standardDrawing.translate(center);
    tiles.push(tile.cut(undersideCutter(mark, depths[i])));
    meshTiles.push(
      drawingMeshShape(tileDrawing, 2.4).cut(
        drawingMeshShape(mark, depths[i] + 0.02).translateZ(-0.01),
      ),
    );
  }

  const sizes = [8, 10, 12];
  for (let i = 0; i < sizes.length; i += 1) {
    console.log(`build: coupon compact ${i} size ${sizes[i]}`);
    const center = [standardCenters[i], -11];
    const tileDrawing = drawRoundedRectangle(34, 18, 2.5).translate(center);
    const tile = tileDrawing.sketchOnPlane("XY").extrude(2.4);
    const mark = canonicalDrawing(jsMonogram(sizes[i])).translate(center);
    tiles.push(tile.cut(undersideCutter(mark, 0.4)));
    meshTiles.push(
      drawingMeshShape(tileDrawing, 2.4).cut(
        drawingMeshShape(mark, 0.42).translateZ(-0.01),
      ),
    );
  }
  return {
    brep: cad.compoundShapes(tiles),
    mesh: meshTiles.slice(1).reduce((result, tile) => result.fuse(tile), meshTiles[0]).simplify(0.001),
  };
}

function flattenPaths(value) {
  if (typeof value === "string") return [value];
  return value.flatMap(flattenPaths);
}

function groupedPaths(value) {
  if (typeof value === "string") return [value];
  if (value.every((entry) => typeof entry === "string")) {
    return [value.join(" ")];
  }
  return value.flatMap(groupedPaths);
}

function xmlEscape(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function drawingSVG(drawing, config) {
  const paths = groupedPaths(drawing.toSVGPaths());
  const title = xmlEscape(config.title);
  const description = xmlEscape(config.description);
  const pathElements = paths
    .map((d) => `    <path d="${d}"/>`)
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${config.width}mm" height="${config.height}mm" viewBox="${config.x} ${config.y} ${config.width} ${config.height}">
  <title>${title}</title>
  <desc>${description}</desc>
  <metadata>Release ${RELEASE_ID}; units millimetres; manufacturing outlines; no font dependency.</metadata>
  <g fill="#000000" fill-rule="evenodd" stroke="none">
${pathElements}
  </g>
</svg>
`;
}

function vectorAngle(ux, uy, vx, vy) {
  const dot = ux * vx + uy * vy;
  const lengths = Math.hypot(ux, uy) * Math.hypot(vx, vy);
  const cosine = Math.max(-1, Math.min(1, dot / lengths));
  const sign = ux * vy - uy * vx < 0 ? -1 : 1;
  return sign * Math.acos(cosine);
}

function sampleSvgArc(start, values, maximumStep = Math.PI / 18) {
  let [rx, ry, rotation, largeArcFlag, sweepFlag, endX, endY] = values;
  rx = Math.abs(rx);
  ry = Math.abs(ry);
  const end = [endX, endY];
  if (rx < 1e-9 || ry < 1e-9 || Math.hypot(endX - start[0], endY - start[1]) < 1e-9) {
    return [end];
  }

  const phi = (rotation * Math.PI) / 180;
  const cosPhi = Math.cos(phi);
  const sinPhi = Math.sin(phi);
  const dx = (start[0] - endX) / 2;
  const dy = (start[1] - endY) / 2;
  const xPrime = cosPhi * dx + sinPhi * dy;
  const yPrime = -sinPhi * dx + cosPhi * dy;
  const lambda = (xPrime * xPrime) / (rx * rx) + (yPrime * yPrime) / (ry * ry);
  if (lambda > 1) {
    const scale = Math.sqrt(lambda);
    rx *= scale;
    ry *= scale;
  }

  const numerator = Math.max(
    0,
    rx * rx * ry * ry - rx * rx * yPrime * yPrime - ry * ry * xPrime * xPrime,
  );
  const denominator = rx * rx * yPrime * yPrime + ry * ry * xPrime * xPrime;
  const direction = Number(largeArcFlag) === Number(sweepFlag) ? -1 : 1;
  const coefficient = direction * Math.sqrt(numerator / Math.max(denominator, 1e-18));
  const centerPrimeX = coefficient * ((rx * yPrime) / ry);
  const centerPrimeY = coefficient * (-(ry * xPrime) / rx);
  const centerX =
    cosPhi * centerPrimeX - sinPhi * centerPrimeY + (start[0] + endX) / 2;
  const centerY =
    sinPhi * centerPrimeX + cosPhi * centerPrimeY + (start[1] + endY) / 2;

  const ux = (xPrime - centerPrimeX) / rx;
  const uy = (yPrime - centerPrimeY) / ry;
  const vx = (-xPrime - centerPrimeX) / rx;
  const vy = (-yPrime - centerPrimeY) / ry;
  const startAngle = vectorAngle(1, 0, ux, uy);
  let deltaAngle = vectorAngle(ux, uy, vx, vy);
  if (!Number(sweepFlag) && deltaAngle > 0) deltaAngle -= 2 * Math.PI;
  if (Number(sweepFlag) && deltaAngle < 0) deltaAngle += 2 * Math.PI;
  const steps = Math.max(2, Math.ceil(Math.abs(deltaAngle) / maximumStep));
  const points = [];
  for (let i = 1; i <= steps; i += 1) {
    const angle = startAngle + (deltaAngle * i) / steps;
    const x =
      centerX + cosPhi * rx * Math.cos(angle) - sinPhi * ry * Math.sin(angle);
    const y =
      centerY + sinPhi * rx * Math.cos(angle) + cosPhi * ry * Math.sin(angle);
    points.push([x, y]);
  }
  points[points.length - 1] = end;
  return points;
}

function svgPathToPolylines(pathData) {
  const tokens = pathData.match(
    /[MLAZ]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?/g,
  );
  assert(tokens, "SVG path is empty");
  const polylines = [];
  let current = [];
  let cursor = [0, 0];
  let start = [0, 0];
  let index = 0;
  while (index < tokens.length) {
    const command = tokens[index++];
    if (command === "M") {
      if (current.length > 1) polylines.push(current);
      cursor = [Number(tokens[index++]), Number(tokens[index++])];
      start = cursor;
      current = [cursor];
    } else if (command === "L") {
      cursor = [Number(tokens[index++]), Number(tokens[index++])];
      current.push(cursor);
    } else if (command === "A") {
      const values = tokens.slice(index, index + 7).map(Number);
      index += 7;
      const sampled = sampleSvgArc(cursor, values);
      current.push(...sampled);
      cursor = sampled.at(-1);
    } else if (command === "Z") {
      if (Math.hypot(cursor[0] - start[0], cursor[1] - start[1]) > 1e-7) {
        current.push(start);
      }
      if (current.length > 2) polylines.push(current);
      current = [];
      cursor = start;
    } else {
      throw new Error(`Unsupported SVG path command: ${command}`);
    }
  }
  if (current.length > 1) polylines.push(current);
  return polylines;
}

function drawingCrossSection(drawing) {
  const crossSections = groupedPaths(drawing.toSVGPaths()).map((pathGroup) => {
    const contours = svgPathToPolylines(pathGroup).map((points) => {
      const closed = points.length > 2
        && Math.hypot(points[0][0] - points.at(-1)[0], points[0][1] - points.at(-1)[1]) < 1e-7;
      const contour = closed ? points.slice(0, -1) : points;
      return contour.map(([x, y]) => [x, -y]);
    });
    return new manifold.CrossSection(contours, "EvenOdd");
  });
  const crossSection = crossSections.slice(1)
    .reduce((result, section) => result.add(section), crossSections[0])
    .offset(0.005, "Round", 2, 24)
    .offset(-0.005, "Round", 2, 24)
    .simplify(0.001);
  assert(!crossSection.isEmpty(), "Cross-section conversion produced no area");
  return crossSection;
}

function canonicalDrawing(drawing) {
  const blueprints = drawingCrossSection(drawing).toPolygons().map((polygon) => {
    assert(polygon.length >= 3, "Canonical polygon needs at least three vertices");
    const pen = cad.draw(polygon[0]);
    for (const point of polygon.slice(1)) pen.lineTo(point);
    return pen.close().blueprint;
  });
  return new cad.Drawing(cad.organiseBlueprints(blueprints));
}

function drawingMeshShape(drawing, depth) {
  const crossSection = drawingCrossSection(drawing);
  const meshShape = new cad.MeshShape(crossSection.extrude(depth)).simplify(0.001);
  assert(!meshShape.isEmpty, "Manifold cross-section extrusion produced no solid");
  return meshShape;
}

function drawingDXF(drawing, title) {
  // replicad serializes SVG paths in screen coordinates (positive Y down).
  // Restore CAD coordinates for DXF so DXF, STEP and mesh exports agree.
  const polylines = flattenPaths(drawing.toSVGPaths())
    .flatMap(svgPathToPolylines)
    .map((points) => points.map(([x, y]) => [x, -y]));
  const lines = [
    "999", `JuSt Innovation - ${title} - ${RELEASE_ID}`,
    "0", "SECTION", "2", "HEADER",
    "9", "$ACADVER", "1", "AC1009",
    "9", "$INSUNITS", "70", "4",
    "9", "$MEASUREMENT", "70", "1",
    "0", "ENDSEC",
    "0", "SECTION", "2", "ENTITIES",
  ];
  for (const points of polylines) {
    const unique = points.slice(0, -1);
    lines.push("0", "POLYLINE", "8", "WATERMARK", "66", "1", "70", "1");
    for (const [x, y] of unique) {
      lines.push(
        "0", "VERTEX", "8", "WATERMARK", "10", String(round(x, 6)),
        "20", String(round(y, 6)), "30", "0",
      );
    }
    lines.push("0", "SEQEND", "8", "WATERMARK");
  }
  lines.push("0", "ENDSEC", "0", "EOF", "");
  return lines.join("\n");
}

function previewSVG(profiles) {
  const panels = [
    { key: "standard", label: "STANDARD · 32 × 10 mm", x: 100, y: 220, scale: 18 },
    { key: "traceSuffix", label: "TRACE SUFFIX · 48 × 10 mm · 26A1", x: 830, y: 220, scale: 12 },
    { key: "compact", label: "COMPACT · 10 mm AF", x: 100, y: 520, scale: 18 },
    { key: "traceFull", label: "TRACE FULL · 60 × 10 mm · JSI-26A1", x: 830, y: 520, scale: 9.6 },
  ];
  const blocks = panels.map((panel) => {
    const p = profiles[panel.key];
    const paths = groupedPaths(p.drawing.toSVGPaths())
      .map((d) => `<path d="${d}"/>`)
      .join("");
    return `
    <g transform="translate(${panel.x} ${panel.y})">
      <text x="0" y="-55" class="label">${panel.label}</text>
      <rect x="-24" y="-35" width="${p.width * panel.scale + 48}" height="${p.height * panel.scale + 70}" rx="18" class="plate"/>
      <g transform="translate(${(p.width * panel.scale) / 2} ${(p.height * panel.scale) / 2}) scale(${panel.scale})" fill="#163348" fill-rule="evenodd">
        ${paths}
      </g>
    </g>`;
  }).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0b1423"/><stop offset="1" stop-color="#17324a"/></linearGradient>
    <style>.title{font:700 44px DejaVu Sans,sans-serif;fill:#fff}.subtitle{font:22px DejaVu Sans,sans-serif;fill:#a8bed1}.label{font:700 18px DejaVu Sans,sans-serif;letter-spacing:1.2px;fill:#ef8a2f}.plate{fill:#eef2f4;stroke:#9aabb8;stroke-width:2}</style>
  </defs>
  <rect width="1600" height="900" fill="url(#bg)"/>
  <text x="80" y="74" class="title">JuSt Innovation · Produktionsprofile</text>
  <text x="80" y="112" class="subtitle">Exakte, einfarbige Unterseiten-Geometrie · 0,80 mm Mindeststrich · 0,40 mm Standardtiefe</text>
  ${blocks}
  <text x="80" y="850" class="subtitle">Unterseiten-Leserichtung · SVG-Pfade ohne Schriftabhängigkeit · ${RELEASE_ID}</text>
</svg>
`;
}

function modelXml(shape, metadata) {
  const mesh = shape.mesh({ tolerance: 0.025, angularTolerance: 0.12 });
  const vertices = [];
  for (let i = 0; i < mesh.vertices.length; i += 3) {
    vertices.push(
      `          <vertex x="${round(mesh.vertices[i], 6)}" y="${round(mesh.vertices[i + 1], 6)}" z="${round(mesh.vertices[i + 2], 6)}"/>`,
    );
  }
  const triangles = [];
  for (let i = 0; i < mesh.triangles.length; i += 3) {
    triangles.push(
      `          <triangle v1="${mesh.triangles[i]}" v2="${mesh.triangles[i + 1]}" v3="${mesh.triangles[i + 2]}"/>`,
    );
  }
  const metadataRows = Object.entries(metadata)
    .map(([name, value]) => `  <metadata name="${xmlEscape(name)}" preserve="1">${xmlEscape(value)}</metadata>`)
    .join("\n");
  return {
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="de-DE" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:jsi="urn:just-innovation:provenance:1.0">
${metadataRows}
  <resources>
    <object id="1" type="model" name="${xmlEscape(metadata.Title)}">
      <mesh>
        <vertices>
${vertices.join("\n")}
        </vertices>
        <triangles>
${triangles.join("\n")}
        </triangles>
      </mesh>
    </object>
  </resources>
  <build><item objectid="1"/></build>
</model>
`,
    vertices: vertices.length,
    triangles: triangles.length,
  };
}

function make3MF(shape, title, description) {
  const contentTypes = `<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>`;
  const relationships = `<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>`;
  const model = modelXml(shape, {
    Title: title,
    Designer: "JuSt Innovation",
    Description: description,
    Copyright: `Copyright ${RELEASE_DATE.slice(0, 4)} JuSt Innovation`,
    LicenseTerms: "Internal JuSt Innovation production asset; see README.md",
    CreationDate: RELEASE_DATE,
    "jsi:ReleaseID": RELEASE_ID,
    "jsi:AIUse": "AI-assisted design; human requirements and concept approved",
    "jsi:ProvenanceManifest": "provenance.json",
  });
  return {
    bytes: zipSync(
      {
        "[Content_Types].xml": strToU8(contentTypes),
        "_rels/.rels": strToU8(relationships),
        "3D/3dmodel.model": strToU8(model.xml),
      },
      { level: 6 },
    ),
    vertices: model.vertices,
    triangles: model.triangles,
  };
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, Buffer.from(await blob.arrayBuffer()));
}

async function exportShape(name, shape, meshShape, title, description) {
  const stlPath = path.join(exportsRoot, "stl", `${name}.stl`);
  const stepPath = path.join(exportsRoot, "step", `${name}.step`);
  const threeMfPath = path.join(exportsRoot, "3mf", `${name}.3mf`);
  const analyzer = new (cad.getOC().BRepCheck_Analyzer)(shape.wrapped, true, false);
  const brepValid = analyzer.IsValid_2();
  analyzer.delete();
  assert(brepValid, `${name}: OpenCascade B-Rep validation failed`);
  assert(!meshShape.isEmpty, `${name}: manifold mesh conversion produced no solid`);
  await writeBlob(
    stlPath,
    meshShape.blobSTL({ binary: true }),
  );
  await writeBlob(stepPath, shape.blobSTEP());
  const threeMf = make3MF(meshShape, title, description);
  await fs.writeFile(threeMfPath, threeMf.bytes);
  const bounds = shape.boundingBox.bounds;
  return {
    name,
    bounds_mm: bounds.map((point) => point.map((value) => round(value, 5))),
    size_mm: [
      round(bounds[1][0] - bounds[0][0], 5),
      round(bounds[1][1] - bounds[0][1], 5),
      round(bounds[1][2] - bounds[0][2], 5),
    ],
    volume_mm3: round(measureVolume(shape), 5),
    manifold_mesh_volume_mm3: round(meshShape.volume(), 5),
    brep_valid: brepValid,
    manifold_mesh_valid: true,
    faces: shape.faces.length,
    edges: shape.edges.length,
    mesh_vertices: threeMf.vertices,
    mesh_triangles: threeMf.triangles,
  };
}

for (const directory of [exportsRoot, validationRoot]) {
  await fs.rm(directory, { recursive: true, force: true });
}
for (const directory of [
  path.join(exportsRoot, "svg"),
  path.join(exportsRoot, "dxf"),
  path.join(exportsRoot, "stl"),
  path.join(exportsRoot, "step"),
  path.join(exportsRoot, "3mf"),
  path.join(exportsRoot, "png"),
  validationRoot,
]) {
  await fs.mkdir(directory, { recursive: true });
}

console.log("build: compact profile");
const compactDrawing = canonicalDrawing(jsMonogram(10));
console.log("build: standard profile");
const standardDrawing = canonicalDrawing(standardMark());
console.log("build: trace suffix profile");
const traceSuffixDrawing = canonicalDrawing(traceMark("26A1", 48));
console.log("build: trace full profile");
const traceFullDrawing = canonicalDrawing(traceMark("JSI-26A1", 60));

const profiles = {
  compact: {
    drawing: compactDrawing,
    width: 2 * ((10 - STROKE) / SQRT3) + STROKE,
    height: 10,
    x: -(2 * ((10 - STROKE) / SQRT3) + STROKE) / 2,
    y: -5,
    title: "JuSt Innovation compact JS watermark",
    description: "10 mm across-flats JS monogram for recessed FDM underside marking.",
  },
  standard: {
    drawing: standardDrawing,
    width: 32,
    height: 10,
    x: -16,
    y: -5,
    title: "JuSt Innovation standard watermark",
    description: "32 by 10 mm standard recessed underside watermark.",
  },
  traceSuffix: {
    drawing: traceSuffixDrawing,
    width: 48,
    height: 10,
    x: -24,
    y: -5,
    title: "JuSt Innovation trace watermark 26A1",
    description: "48 by 10 mm traced underside watermark with batch suffix 26A1.",
  },
  traceFull: {
    drawing: traceFullDrawing,
    width: 60,
    height: 10,
    x: -30,
    y: -5,
    title: "JuSt Innovation trace watermark JSI-26A1",
    description: "60 by 10 mm traced underside watermark with full release code JSI-26A1.",
  },
};

for (const [key, profile] of Object.entries(profiles)) {
  const slug = `just-innovation-${key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`)}`;
  const svg = drawingSVG(profile.drawing, profile);
  await fs.writeFile(path.join(exportsRoot, "svg", `${slug}.svg`), svg);
  await fs.writeFile(
    path.join(exportsRoot, "dxf", `${slug}.dxf`),
    drawingDXF(profile.drawing, profile.title),
  );
  await sharp(Buffer.from(svg)).resize({ width: 1600 }).flatten({ background: "#ffffff" }).png().toFile(
    path.join(exportsRoot, "png", `${slug}.png`),
  );
}

const preview = previewSVG(profiles);
await fs.writeFile(path.join(exportsRoot, "watermark-production-preview.svg"), preview);
await sharp(Buffer.from(preview)).png().toFile(
  path.join(exportsRoot, "png", "watermark-production-preview.png"),
);

const metrics = [];
metrics.push(
  await exportShape(
    "just-innovation-compact-cutter-10af-d040",
    cutterFromDrawing(compactDrawing),
    drawingMeshShape(compactDrawing, CUTTER_DEPTH),
    "JuSt Innovation compact cutter 10 AF",
    "10 mm AF compact JS cutter, 0.40 mm depth.",
  ),
);
metrics.push(
  await exportShape(
    "just-innovation-standard-cutter-32x10-d040",
    cutterFromDrawing(standardDrawing),
    drawingMeshShape(standardDrawing, CUTTER_DEPTH),
    "JuSt Innovation standard cutter 32x10",
    "32 by 10 mm standard watermark cutter, 0.40 mm depth.",
  ),
);
metrics.push(
  await exportShape(
    "just-innovation-trace-suffix-48x10-26A1-d040",
    cutterFromDrawing(traceSuffixDrawing),
    drawingMeshShape(traceSuffixDrawing, CUTTER_DEPTH),
    "JuSt Innovation trace suffix cutter 26A1",
    "48 by 10 mm trace watermark cutter with batch suffix 26A1, 0.40 mm depth.",
  ),
);
metrics.push(
  await exportShape(
    "just-innovation-trace-full-60x10-JSI-26A1-d040",
    cutterFromDrawing(traceFullDrawing),
    drawingMeshShape(traceFullDrawing, CUTTER_DEPTH),
    "JuSt Innovation full trace cutter JSI-26A1",
    "60 by 10 mm full trace watermark cutter JSI-26A1, 0.40 mm depth.",
  ),
);
const coupon = makeCoupon();
metrics.push(
  await exportShape(
    "just-innovation-depth-size-test-coupon",
    coupon.brep,
    coupon.mesh,
    "JuSt Innovation watermark depth and size test coupon",
    "110 by 40 by 2.4 mm underside coupon: standard marks at 0.20, 0.40, 0.60 mm and compact marks at 8, 10, 12 mm AF.",
  ),
);

const drawingMetrics = Object.fromEntries(
  Object.entries(profiles).map(([key, profile]) => {
    const bounds = profile.drawing.boundingBox.bounds;
    return [key, {
      bounds_mm: bounds.map((point) => point.map((value) => round(value, 5))),
      size_mm: [round(bounds[1][0] - bounds[0][0], 5), round(bounds[1][1] - bounds[0][1], 5)],
      nominal_envelope_mm: [round(profile.width, 5), profile.height],
    }];
  }),
);

await fs.writeFile(
  path.join(validationRoot, "geometry-metrics.json"),
  `${JSON.stringify({
    release_id: RELEASE_ID,
    units: "mm",
    nominal_constraints: {
      minimum_stroke_mm: STROKE,
      minimum_clear_gap_mm: CLEAR_GAP,
      default_depth_mm: CUTTER_DEPTH,
      compact_af_mm: 10,
      standard_envelope_mm: [32, 10],
      trace_suffix_envelope_mm: [48, 10],
      trace_full_envelope_mm: [60, 10],
      innovation_o_clear_gap_mm: 1.55 - STROKE,
      separated_code_glyph_clear_gap_mm: 3.0 - 1.6 - STROKE,
      standard_monogram_js_clear_gap_mm: round(1.75 * ((8.4 - STROKE) / 9.2) - STROKE, 5),
    },
    drawing_profiles: drawingMetrics,
    exported_shapes: metrics,
  }, null, 2)}\n`,
);

console.log(`Generated ${metrics.length} validated CAD/mesh presets in ${exportsRoot}`);
