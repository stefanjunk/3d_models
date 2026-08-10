#!/usr/bin/env node
"use strict";

/**
 * Parametric B-Rep generator for the modular honeycomb display shelf.
 *
 * RepliCAD uses OpenCascade and exports an editable STEP master plus controlled
 * STL tessellations. The dense wood field is intentionally generated later as
 * a mesh by ../scripts/generate_textured_mesh.py.
 */

const fs = require("fs");
const path = require("path");

const opencascadePackage = require("replicad-opencascadejs");
const opencascade = opencascadePackage.default;
globalThis.require = require;
globalThis.__dirname = path.dirname(require.resolve("replicad-opencascadejs"));

const projectDir = path.resolve(__dirname, "..");
const params = JSON.parse(fs.readFileSync(path.join(projectDir, "parameters.json"), "utf8"));
const outputDir = path.join(projectDir, "generated");
fs.mkdirSync(outputDir, { recursive: true });

function assertParameters() {
  const m = params.module;
  const t = params.texture;
  if (!(m.outer_radius > 0 && m.wall_thickness > 0 && m.depth > 0)) {
    throw new Error("Module dimensions must be positive");
  }
  const innerRadius = m.outer_radius - m.wall_thickness / Math.cos(Math.PI / 6);
  if (innerRadius <= 0) throw new Error("wall_thickness consumes the hexagon");
  if (!(m.back_thickness > 0 && m.back_thickness < m.depth)) {
    throw new Error("back_thickness must be positive and smaller than depth");
  }
  if (!(t.depth > 0 && t.depth < m.wall_thickness * 0.25)) {
    throw new Error("Texture depth must be positive and below 25% of wall thickness");
  }
  const mount = params.mounting;
  const mountingThickness = m.back_panel_enabled ? m.back_thickness : mount.ear_thickness;
  if (!(mountingThickness > mount.counterbore_depth)) {
    throw new Error("counterbore_depth must leave material in the mounting feature");
  }
  if (!(mount.ear_outer_radius > mount.head_counterbore_diameter / 2 + 2.0)) {
    throw new Error("mounting ears need at least 2 mm around the screw head");
  }
  if (!(mount.ear_neck_width > 0 && mount.ear_neck_width < 2 * mount.ear_outer_radius)) {
    throw new Error("ear_neck_width must be positive and smaller than the ear diameter");
  }
}

function hexPoints(radius) {
  return Array.from({ length: 6 }, (_, index) => {
    const angle = (index * Math.PI) / 3;
    return [radius * Math.cos(angle), radius * Math.sin(angle)];
  });
}

function polygonDrawing(draw, points) {
  const pen = draw(points[0]);
  for (const point of points.slice(1)) pen.lineTo(point);
  return pen.close();
}

function mountingEarPoints(center, radius, neckWidth, innerTop, segments = 72) {
  const [cx, cy] = center;
  const halfNeck = neckWidth / 2;
  const px = halfNeck;
  const py = innerTop - cy;
  const distanceSquared = px * px + py * py;
  if (distanceSquared <= radius * radius) {
    throw new Error("mounting-ear neck corners must sit outside the circular pad");
  }
  const baseX = (radius * radius * px) / distanceSquared;
  const baseY = (radius * radius * py) / distanceSquared;
  const tangentScale =
    (radius * Math.sqrt(distanceSquared - radius * radius)) / distanceSquared;
  const tangentX = baseX + tangentScale * py;
  const tangentY = baseY - tangentScale * px;
  const rightAngle = Math.atan2(tangentY, tangentX);
  const leftAngle = Math.PI - rightAngle;
  const points = [[cx - halfNeck, innerTop]];
  for (let index = 0; index <= segments; index += 1) {
    const angle = leftAngle + ((2 * Math.PI + rightAngle - leftAngle) * index) / segments;
    points.push([cx + radius * Math.cos(angle), cy + radius * Math.sin(angle)]);
  }
  points.push([cx + halfNeck, innerTop]);
  return points;
}

function buildModule(api) {
  const { draw, makeCylinder } = api;
  const m = params.module;
  const innerRadius = m.outer_radius - m.wall_thickness / Math.cos(Math.PI / 6);
  const outer = polygonDrawing(draw, hexPoints(m.outer_radius)).sketchOnPlane().extrude(m.depth);
  const cavityStart = m.back_panel_enabled ? m.back_thickness : -1.0;
  const innerCutter = polygonDrawing(draw, hexPoints(innerRadius))
    .sketchOnPlane("XY", cavityStart)
    .extrude(m.depth - cavityStart + 1.0);
  let body = outer.cut(innerCutter);

  const mount = params.mounting;
  const mountingThickness = m.back_panel_enabled ? m.back_thickness : mount.ear_thickness;
  const innerTop = innerRadius * Math.sin(Math.PI / 3);
  for (const [x, y] of mount.hole_centers) {
    if (!m.back_panel_enabled) {
      const ear = polygonDrawing(
        draw,
        mountingEarPoints(
          [x, y],
          mount.ear_outer_radius,
          mount.ear_neck_width,
          innerTop
        )
      )
        .sketchOnPlane()
        .extrude(mountingThickness);
      body = body.fuse(ear);
    }
    const through = makeCylinder(
      mount.shank_clearance_diameter / 2,
      mountingThickness + 2.0,
      [x, y, -1.0]
    );
    const counterbore = makeCylinder(
      mount.head_counterbore_diameter / 2,
      mount.counterbore_depth + 1.0,
      [x, y, mountingThickness - mount.counterbore_depth]
    );
    body = body.cut(through).cut(counterbore);
  }
  return body;
}

function buildWallSpacer(api) {
  const { makeCylinder } = api;
  const spacing = params.wall_spacing;
  const outer = makeCylinder(
    spacing.spacer_outer_diameter / 2,
    spacing.rear_clip_standoff
  );
  const hole = makeCylinder(
    spacing.spacer_hole_diameter / 2,
    spacing.rear_clip_standoff + 2.0,
    [0, 0, -1.0]
  );
  return outer.cut(hole);
}

function buildClip(api, clearancePerSide) {
  const { draw } = api;
  const c = params.connector;
  const combinedWall = params.module.wall_thickness * 2;
  const gap = combinedWall + 2 * clearancePerSide;
  const halfGap = gap / 2;
  const halfOuter = halfGap + c.leg_thickness;
  const leadStart = c.insertion_depth - c.lead_in_height;
  const points = [
    [-halfOuter, 0],
    [halfOuter, 0],
    [halfOuter, c.insertion_depth],
    [halfGap + c.lead_in_extra, c.insertion_depth],
    [halfGap, leadStart],
    [halfGap, c.cap_thickness],
    [-halfGap, c.cap_thickness],
    [-halfGap, leadStart],
    [-halfGap - c.lead_in_extra, c.insertion_depth],
    [-halfOuter, c.insertion_depth]
  ];
  return polygonDrawing(draw, points).sketchOnPlane("YZ").extrude(c.length);
}

async function writeBlob(filePath, blob) {
  const buffer = Buffer.from(await blob.arrayBuffer());
  fs.writeFileSync(filePath, buffer);
}

async function exportShape(shape, stem) {
  const e = params.export;
  await writeBlob(path.join(outputDir, `${stem}.step`), await shape.blobSTEP());
  await writeBlob(
    path.join(outputDir, `${stem}.stl`),
    await shape.blobSTL({
      tolerance: e.stl_linear_tolerance,
      angularTolerance: e.stl_angular_tolerance,
      binary: true
    })
  );
}

(async () => {
  assertParameters();
  const oc = await opencascade();
  const api = await import("replicad");
  api.setOC(oc);

  const moduleShape = buildModule(api);
  const clipShape = buildClip(api, params.connector.clearance_per_side);
  const spacerShape = buildWallSpacer(api);
  await exportShape(moduleShape, "honeycomb-module-base");
  await exportShape(clipShape, "bridge-clip");
  await exportShape(spacerShape, "rear-wall-spacer");

  for (const clearance of [0.10, 0.20, 0.30]) {
    const coupon = buildClip(api, clearance);
    const suffix = clearance.toFixed(2).replace(".", "p");
    await exportShape(coupon, `clip-fit-${suffix}`);
  }

  const bb = moduleShape.boundingBox;
  const report = {
    generator: "RepliCAD 0.23.1 / OpenCascade WASM",
    parameters: params,
    derived: {
      inner_radius_mm:
        params.module.outer_radius -
        params.module.wall_thickness / Math.cos(Math.PI / 6),
      module_bounds_mm: [bb.width, bb.height, bb.depth],
      module_volume_mm3: api.measureVolume(moduleShape),
      back_panel_enabled: params.module.back_panel_enabled,
      mounting_ear_thickness_mm: params.mounting.ear_thickness,
      connector_insertion_direction: "rear-to-front before wall mounting",
      rear_clip_standoff_mm: params.wall_spacing.rear_clip_standoff,
      recommended_clips_per_shared_edge: 2,
      recommended_spacers_per_mounted_module: 2
    },
    warning:
      "No load rating. Match screws and certified anchors to the actual wall and proof-test the installed system."
  };
  fs.writeFileSync(
    path.join(outputDir, "cad-build-report.json"),
    `${JSON.stringify(report, null, 2)}\n`,
    "utf8"
  );
  console.log(JSON.stringify(report, null, 2));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
