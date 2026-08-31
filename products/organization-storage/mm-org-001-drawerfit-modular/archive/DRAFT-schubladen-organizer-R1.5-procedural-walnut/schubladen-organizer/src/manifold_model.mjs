import { CrossSection, Manifold } from 'manifold-3d/manifoldCAD'

import { watermarkCutter } from './watermark.mjs'
import { applyProceduralTexturePatch, summarizeTextureStats } from './surface_texture.mjs'

const EPS = 1.0e-6

function box (x0, x1, y0, y1, z0, z1) {
  const size = [x1 - x0, y1 - y0, z1 - z0]
  if (size.some(value => value <= EPS)) return null
  return Manifold.cube(size).translate([x0, y0, z0])
}

function cylinderZ (cx, cy, radius, z0, z1, segments) {
  return Manifold.cylinder(z1 - z0, radius, radius, segments).translate([cx, cy, z0])
}

function cylinderY (cx, cy, cz, radius, yLength, segments) {
  return Manifold.cylinder(yLength, radius, radius, segments, true)
    .rotate([90, 0, 0])
    .translate([cx, cy, cz])
}

function unionMany (items) {
  const filtered = items.filter(Boolean)
  if (filtered.length === 0) return null
  if (filtered.length === 1) return filtered[0]
  return Manifold.union(filtered)
}

export function resolveModelParameters (params) {
  const base = params.organizer.base_wall_thickness
  if (!Number.isFinite(base)) throw new Error('base_wall_thickness must be a finite millimetre value')
  return {
    ...params,
    organizer: {
      ...params.organizer,
      outer_wall_thickness: params.organizer.outer_wall_thickness_override ?? base,
      divider_thickness: params.organizer.divider_wall_thickness_override ?? base
    }
  }
}

function trianglePrism (points, height) {
  let area2 = 0
  for (let i = 0; i < points.length; i += 1) {
    const a = points[i]
    const b = points[(i + 1) % points.length]
    area2 += a[0] * b[1] - b[0] * a[1]
  }
  const ordered = area2 < 0 ? [...points].reverse() : points
  return CrossSection.ofPolygons([ordered]).extrude(height)
}

function roundedRectPrism (width, depth, radius, height) {
  if (radius <= EPS) return box(0, width, 0, depth, 0, height)
  const r = Math.min(radius, width / 2 - EPS, depth / 2 - EPS)
  const parts = [
    box(r, width - r, 0, depth, 0, height),
    box(0, width, r, depth - r, 0, height),
    cylinderZ(r, r, r, 0, height, 36),
    cylinderZ(width - r, r, r, 0, height, 36),
    cylinderZ(r, depth - r, r, 0, height, 36),
    cylinderZ(width - r, depth - r, r, 0, height, 36)
  ]
  return unionMany(parts)
}

function globalOuterTray (p) {
  const o = p.organizer
  const outer = roundedRectPrism(o.width_x, o.depth_y, o.outer_corner_radius, o.outer_wall_height)
  const innerRadius = Math.max(0.2, o.outer_corner_radius - o.outer_wall_thickness)
  const inner = roundedRectPrism(
    o.width_x - 2 * o.outer_wall_thickness,
    o.depth_y - 2 * o.outer_wall_thickness,
    innerRadius,
    o.outer_wall_height - o.floor_thickness + 1
  ).translate([o.outer_wall_thickness, o.outer_wall_thickness, o.floor_thickness])
  return outer.subtract(inner)
}

function moduleDefinitions (p) {
  const x = p.layout.screwdriver_zone_width
  const y = p.layout.depth_split
  const w = p.organizer.width_x
  const d = p.organizer.depth_y
  return [
    { id: 'driver-front', kind: 'driver', rowHalf: 'front', bounds: [0, x, 0, y] },
    { id: 'driver-back', kind: 'driver', rowHalf: 'back', bounds: [0, x, y, d] },
    { id: 'hardware-front', kind: 'hardware', rowHalf: 'front', bounds: [x, w, 0, y] },
    { id: 'hardware-back', kind: 'hardware', rowHalf: 'back', bounds: [x, w, y, d] }
  ]
}

function clipTrayToModule (tray, def, p) {
  const [x0, x1, y0, y1] = def.bounds
  return tray.intersect(box(x0, x1, y0, y1, 0, p.organizer.outer_wall_height))
}

function functionalWallsAndGussets (def, p) {
  const o = p.organizer
  const l = p.layout
  const dt = o.divider_thickness
  const zone = l.screwdriver_zone_width
  const parts = []
  if (def.kind === 'driver') {
    parts.push(box(zone - dt, zone, def.bounds[2], def.bounds[3], 0, o.outer_wall_height))
    const markers = [89.25, 178.5, 267.75].filter(y => y > def.bounds[2] + 5 && y < def.bounds[3] - 5)
    for (const y of markers) {
      parts.push(trianglePrism([[o.outer_wall_thickness - 0.4, y - 4], [o.outer_wall_thickness + 4, y], [o.outer_wall_thickness - 0.4, y + 4]], o.root_gusset_height))
      parts.push(trianglePrism([[zone - dt + 0.4, y - 4], [zone - dt - 4, y], [zone - dt + 0.4, y + 4]], o.root_gusset_height))
    }
  } else {
    const hwRight = o.width_x - o.outer_wall_thickness
    const centerX = (zone + hwRight) / 2
    parts.push(box(centerX - dt / 2, centerX + dt / 2, def.bounds[2], def.bounds[3], 0, o.divider_height))
    const rowPitch = o.depth_y / l.hardware_rows
    const ownedWalls = def.rowHalf === 'front' ? [rowPitch, l.depth_split] : [3 * rowPitch]
    for (const y of ownedWalls) {
      const y0 = Math.abs(y - l.depth_split) < 0.01 ? y - dt : y - dt / 2
      const y1 = Math.abs(y - l.depth_split) < 0.01 ? y : y + dt / 2
      parts.push(box(zone, o.width_x, y0, y1, 0, o.divider_height))
      const g = o.root_gusset_size
      parts.push(trianglePrism([[centerX - dt / 2 + 0.3, y0 + 0.3], [centerX - dt / 2 - g, y0 + 0.3], [centerX - dt / 2 + 0.3, y0 - g]], o.root_gusset_height))
      parts.push(trianglePrism([[centerX + dt / 2 - 0.3, y0 + 0.3], [centerX + dt / 2 + g, y0 + 0.3], [centerX + dt / 2 - 0.3, y0 - g]], o.root_gusset_height))
    }
  }
  return parts
}

function clippedJunctionCylinder (def, p, cx, cy, radius, segments) {
  const o = p.organizer
  const z0 = Math.max(o.floor_thickness, o.junction_start_height)
  const z1 = Math.min(o.divider_height, o.junction_end_height)
  const cylinder = cylinderZ(cx, cy, radius, z0, z1, segments)
  return cylinder.intersect(box(def.bounds[0], def.bounds[1], def.bounds[2], def.bounds[3], z0, z1))
}

function junctionBlendBodies (def, p, segments) {
  if (def.kind !== 'hardware') return []
  const o = p.organizer
  const l = p.layout
  const zone = l.screwdriver_zone_width
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerX = (zone + innerRight) / 2
  const rowPitch = o.depth_y / l.hardware_rows
  const ownedWalls = def.rowHalf === 'front' ? [rowPitch, l.depth_split] : [3 * rowPitch]
  const bodies = []
  for (const y of ownedWalls) {
    bodies.push(clippedJunctionCylinder(def, p, centerX, y, o.junction_cross_hub_radius, segments))
    bodies.push(clippedJunctionCylinder(def, p, zone, y, o.junction_vertical_blend_radius, segments))
    bodies.push(clippedJunctionCylinder(def, p, innerRight, y, o.junction_vertical_blend_radius, segments))
  }
  return bodies
}

function xMaleConnector (edgeX, cy, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  return unionMany([
    cylinderZ(edgeX + c.lug_radius, cy, c.lug_radius, 0, h, segments),
    box(edgeX - 0.6, edgeX + c.lug_radius, cy - c.neck_width / 2, cy + c.neck_width / 2, 0, h)
  ])
}

function xFemaleConnector (edgeX, cy, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  return unionMany([
    cylinderZ(edgeX + c.lug_radius, cy, c.lug_radius + c.clearance, -0.3, h + 0.3, segments),
    box(edgeX - 0.3, edgeX + c.lug_radius, cy - c.neck_width / 2 - c.clearance, cy + c.neck_width / 2 + c.clearance, -0.3, h + 0.3)
  ])
}

function yMaleConnector (edgeY, cx, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  return unionMany([
    cylinderZ(cx, edgeY + c.lug_radius, c.lug_radius, 0, h, segments),
    box(cx - c.neck_width / 2, cx + c.neck_width / 2, edgeY - 0.6, edgeY + c.lug_radius, 0, h)
  ])
}

function yFemaleConnector (edgeY, cx, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  return unionMany([
    cylinderZ(cx, edgeY + c.lug_radius, c.lug_radius + c.clearance, -0.3, h + 0.3, segments),
    box(cx - c.neck_width / 2 - c.clearance, cx + c.neck_width / 2 + c.clearance, edgeY - 0.3, edgeY + c.lug_radius, -0.3, h + 0.3)
  ])
}

function connectorBodies (def, p, segments) {
  const zone = p.layout.screwdriver_zone_width
  const split = p.layout.depth_split
  const additions = []
  const cutters = []
  const yPositions = def.rowHalf === 'front' ? [45, 133] : [223, 312]
  for (const y of yPositions) {
    if (def.kind === 'driver') additions.push(xMaleConnector(zone, y, p, segments))
    else cutters.push(xFemaleConnector(zone, y, p, segments))
  }
  const xPositions = def.kind === 'driver' ? [30, 65] : [122, 196]
  for (const x of xPositions) {
    if (def.rowHalf === 'front') additions.push(yMaleConnector(split, x, p, segments))
    else cutters.push(yFemaleConnector(split, x, p, segments))
  }
  return { additions, cutters }
}

function roundedAccessGrooveCutter (cx, cy, wallThickness, wallTop, p, segments) {
  const l = p.layout
  const width = l.access_groove_width
  const depth = l.access_groove_depth
  const radius = Math.min(l.access_groove_bottom_radius, width / 2, depth)
  const x0 = cx - width / 2
  const x1 = cx + width / 2
  const z0 = wallTop - depth
  const z1 = wallTop + 2
  const yLength = wallThickness + 4
  return unionMany([
    box(x0 + radius, x1 - radius, cy - yLength / 2, cy + yLength / 2, z0, z1),
    box(x0, x1, cy - yLength / 2, cy + yLength / 2, z0 + radius, z1),
    cylinderY(x0 + radius, cy, z0 + radius, radius, yLength, segments),
    cylinderY(x1 - radius, cy, z0 + radius, radius, yLength, segments)
  ])
}

function accessGrooveCutters (def, p, segments) {
  if (def.kind !== 'hardware') return []
  const o = p.organizer
  const l = p.layout
  const zone = l.screwdriver_zone_width
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerWallX = (zone + innerRight) / 2
  const centers = [(zone + centerWallX) / 2, (centerWallX + innerRight) / 2]
  const rowPitch = o.depth_y / l.hardware_rows
  const wallSpecs = def.rowHalf === 'front'
    ? [
        { y: o.outer_wall_thickness / 2, thickness: o.outer_wall_thickness, top: o.outer_wall_height },
        { y: rowPitch, thickness: o.divider_thickness, top: o.divider_height },
        { y: l.depth_split - o.divider_thickness / 2, thickness: o.divider_thickness, top: o.divider_height }
      ]
    : [{ y: 3 * rowPitch, thickness: o.divider_thickness, top: o.divider_height }]
  const tools = []
  for (const wall of wallSpecs) {
    for (const x of centers) {
      tools.push(roundedAccessGrooveCutter(x, wall.y, wall.thickness, wall.top, p, segments))
    }
  }
  return tools
}

function subtractRectangle (rect, hole) {
  const ix0 = Math.max(rect.x0, hole.x0)
  const ix1 = Math.min(rect.x1, hole.x1)
  const iy0 = Math.max(rect.y0, hole.y0)
  const iy1 = Math.min(rect.y1, hole.y1)
  if (ix1 <= ix0 || iy1 <= iy0) return [rect]
  return [
    { x0: rect.x0, x1: ix0, y0: rect.y0, y1: rect.y1 },
    { x0: ix1, x1: rect.x1, y0: rect.y0, y1: rect.y1 },
    { x0: ix0, x1: ix1, y0: rect.y0, y1: iy0 },
    { x0: ix0, x1: ix1, y0: iy1, y1: rect.y1 }
  ].filter(item => item.x1 - item.x0 > EPS && item.y1 - item.y0 > EPS)
}

function watermarkKeepout (def, p) {
  const placement = p.watermark?.placements_global_xy?.[def.id]
  const envelope = p.watermark?.actual_envelope
  if (!placement || !envelope) return null
  const margin = p.surface_texture.protected_regions.watermark_margin_mm ?? 0
  return {
    x0: placement[0] - envelope[0] / 2 - margin,
    x1: placement[0] + envelope[0] / 2 + margin,
    y0: placement[1] - envelope[1] / 2 - margin,
    y1: placement[1] + envelope[1] / 2 + margin
  }
}

function floorRectsWithMarkKeepout (def, p) {
  const keepout = watermarkKeepout(def, p)
  if (!keepout) return floorRectsForModule(def, p)
  return floorRectsForModule(def, p).flatMap(rect => subtractRectangle(rect, keepout))
}

function floorRectsForModule (def, p) {
  const o = p.organizer
  const l = p.layout
  const margin = l.floor_texture_margin
  if (def.kind === 'driver') {
    const openSeamMargin = def.bounds[2] === 0
      ? o.outer_wall_thickness + margin
      : 2 * p.connectors.lug_radius + margin
    return [{
      x0: o.outer_wall_thickness + margin,
      x1: l.screwdriver_zone_width - o.divider_thickness - margin,
      y0: def.bounds[2] + openSeamMargin,
      y1: def.bounds[3] - (def.bounds[3] === o.depth_y ? o.outer_wall_thickness + margin : margin)
    }]
  }
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerX = (l.screwdriver_zone_width + innerRight) / 2
  const connectorKeepout = 2 * p.connectors.lug_radius + p.surface_texture.protected_regions.connector_margin_mm
  const xRanges = [
    [l.screwdriver_zone_width + connectorKeepout, centerX - o.divider_thickness / 2 - margin],
    [centerX + o.divider_thickness / 2 + margin, innerRight - margin]
  ]
  const rowPitch = o.depth_y / l.hardware_rows
  const rows = def.rowHalf === 'front' ? [0, 1] : [2, 3]
  const rects = []
  for (const row of rows) {
    for (const [x0, x1] of xRanges) {
      rects.push({
        x0,
        x1,
        y0: row * rowPitch + (row === 0 ? o.outer_wall_thickness : o.divider_thickness) + margin,
        y1: (row + 1) * rowPitch - o.divider_thickness - margin
      })
    }
  }
  return rects
}

function rectangleAround (u, v, halfU, halfV) {
  return { u0: u - halfU, u1: u + halfU, v0: v - halfV, v1: v + halfV }
}

function floorTextureKeepouts (def, p) {
  const o = p.organizer
  const l = p.layout
  const protectedRegion = p.surface_texture.protected_regions
  const keepouts = []
  const connectorRadius = p.connectors.lug_radius + p.connectors.clearance + protectedRegion.connector_margin_mm
  const yPositions = def.rowHalf === 'front' ? [45, 133] : [223, 312]
  for (const y of yPositions) keepouts.push(rectangleAround(l.screwdriver_zone_width + p.connectors.lug_radius, y, connectorRadius, connectorRadius))
  const xPositions = def.kind === 'driver' ? [30, 65] : [122, 196]
  for (const x of xPositions) keepouts.push(rectangleAround(x, l.depth_split + p.connectors.lug_radius, connectorRadius, connectorRadius))
  if (def.kind === 'driver') {
    const markers = [89.25, 178.5, 267.75].filter(y => y > def.bounds[2] + 5 && y < def.bounds[3] - 5)
    const extent = o.root_gusset_size + protectedRegion.gusset_margin_mm
    for (const y of markers) {
      keepouts.push({ u0: 0, u1: o.outer_wall_thickness + extent, v0: y - extent, v1: y + extent })
      keepouts.push({ u0: l.screwdriver_zone_width - o.divider_thickness - extent, u1: l.screwdriver_zone_width, v0: y - extent, v1: y + extent })
    }
  } else {
    const innerRight = o.width_x - o.outer_wall_thickness
    const centerX = (l.screwdriver_zone_width + innerRight) / 2
    const rowPitch = o.depth_y / l.hardware_rows
    const walls = def.rowHalf === 'front' ? [rowPitch, l.depth_split] : [3 * rowPitch]
    const extent = o.root_gusset_size + o.divider_thickness / 2 + protectedRegion.gusset_margin_mm
    for (const y of walls) keepouts.push(rectangleAround(centerX, y, extent, extent))
  }
  return keepouts
}

function floorTexturePatches (def, p) {
  const z = p.organizer.floor_thickness
  const keepouts = floorTextureKeepouts(def, p)
  return floorRectsWithMarkKeepout(def, p).map((rect, index) => ({
    u0: rect.x0,
    u1: rect.x1,
    v0: rect.y0,
    v1: rect.y1,
    key: `floor-global-${index}`,
    continuityKey: 'floor-global-y',
    grainAxis: 'v',
    normal: [0, 0, 1],
    keepouts,
    pointAt: (x, y, offset) => [x, y, z + offset]
  }))
}

function grooveCenters (p) {
  const o = p.organizer
  const l = p.layout
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerWallX = (l.screwdriver_zone_width + innerRight) / 2
  return [(l.screwdriver_zone_width + centerWallX) / 2, (centerWallX + innerRight) / 2]
}

function innerWallTexturePatches (def, p) {
  const o = p.organizer
  const l = p.layout
  const t = p.surface_texture
  const bottom = o.floor_thickness + t.surfaces.inner_walls.bottom_keepout_mm
  const trim = 4.0
  const junction = t.protected_regions.junction_margin_mm
  const patches = []
  const addX = (x, normal, y0, y1, top, key, keepouts = []) => {
    const z1 = top - t.surfaces.inner_walls.top_keepout_mm
    if (y1 - y0 <= 2 || z1 - bottom <= 2) return
    patches.push({ u0: y0, u1: y1, v0: bottom, v1: z1, key, continuityKey: key, grainAxis: 'u', normal: [normal, 0, 0], keepouts, pointAt: (y, z, offset) => [x + normal * offset, y, z] })
  }
  const addY = (y, normal, x0, x1, top, key, keepouts = []) => {
    const z1 = top - t.surfaces.inner_walls.top_keepout_mm
    if (x1 - x0 <= 2 || z1 - bottom <= 2) return
    patches.push({ u0: x0, u1: x1, v0: bottom, v1: z1, key, continuityKey: key, grainAxis: 'u', normal: [0, normal, 0], keepouts, pointAt: (x, z, offset) => [x, y + normal * offset, z] })
  }
  const y0 = def.bounds[2] + trim
  const y1 = def.bounds[3] - trim
  const rowPitch = o.depth_y / l.hardware_rows
  const rowJunctions = [rowPitch, l.depth_split, 3 * rowPitch].filter(y => y > y0 && y < y1)
  const fullHeightKeepouts = rowJunctions.map(y => ({ u0: y - junction, u1: y + junction, v0: bottom, v1: o.outer_wall_height }))
  if (def.kind === 'driver') {
    addX(o.outer_wall_thickness, 1, y0, y1, o.outer_wall_height, 'wall-x-driver-outer-inner')
    addX(l.screwdriver_zone_width - o.divider_thickness, -1, y0, y1, o.outer_wall_height, 'wall-x-driver-zone-inner')
    addX(l.screwdriver_zone_width, 1, y0, y1, o.outer_wall_height, 'wall-x-hardware-zone-inner', fullHeightKeepouts)
  } else {
    const innerRight = o.width_x - o.outer_wall_thickness
    const centerX = (l.screwdriver_zone_width + innerRight) / 2
    addX(innerRight, -1, y0, y1, o.outer_wall_height, 'wall-x-hardware-outer-inner', fullHeightKeepouts)
    addX(centerX - o.divider_thickness / 2, -1, y0, y1, o.divider_height, 'wall-x-center-left', fullHeightKeepouts)
    addX(centerX + o.divider_thickness / 2, 1, y0, y1, o.divider_height, 'wall-x-center-right', fullHeightKeepouts)
    const walls = def.rowHalf === 'front' ? [rowPitch, l.depth_split] : [3 * rowPitch]
    const accessKeepouts = grooveCenters(p).map(x => ({
      u0: x - l.access_groove_width / 2 - t.protected_regions.access_groove_margin_mm,
      u1: x + l.access_groove_width / 2 + t.protected_regions.access_groove_margin_mm,
      v0: o.divider_height - l.access_groove_depth - t.protected_regions.access_groove_margin_mm,
      v1: o.divider_height
    }))
    const junctionKeepout = { u0: centerX - junction, u1: centerX + junction, v0: bottom, v1: o.divider_height }
    for (const y of walls) {
      const splitWall = Math.abs(y - l.depth_split) < 0.01
      const faceA = splitWall ? y - o.divider_thickness : y - o.divider_thickness / 2
      const faceB = splitWall ? y : y + o.divider_thickness / 2
      addY(faceA, -1, l.screwdriver_zone_width + trim, o.width_x - trim, o.divider_height, `wall-y-${y}-front`, [junctionKeepout, ...accessKeepouts])
      addY(faceB, 1, l.screwdriver_zone_width + trim, o.width_x - trim, o.divider_height, `wall-y-${y}-back`, [junctionKeepout, ...accessKeepouts])
    }
  }
  if (def.bounds[2] === 0) {
    const keepouts = def.kind === 'hardware'
      ? [{
          u0: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 - junction,
          u1: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 + junction,
          v0: bottom,
          v1: o.outer_wall_height
        }, ...grooveCenters(p).map(x => ({
          u0: x - l.access_groove_width / 2 - t.protected_regions.access_groove_margin_mm,
          u1: x + l.access_groove_width / 2 + t.protected_regions.access_groove_margin_mm,
          v0: o.outer_wall_height - l.access_groove_depth - t.protected_regions.access_groove_margin_mm,
          v1: o.outer_wall_height
        }))]
      : []
    addY(o.outer_wall_thickness, 1, def.bounds[0] + trim, def.bounds[1] - trim, o.outer_wall_height, `wall-y-front-${def.kind}`, keepouts)
  }
  if (def.bounds[3] === o.depth_y) {
    const keepouts = def.kind === 'hardware'
      ? [{
          u0: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 - junction,
          u1: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 + junction,
          v0: bottom,
          v1: o.outer_wall_height
        }]
      : []
    addY(o.depth_y - o.outer_wall_thickness, -1, def.bounds[0] + trim, def.bounds[1] - trim, o.outer_wall_height, `wall-y-back-${def.kind}`, keepouts)
  }
  return patches
}

function wallTopPatch (rect, z, key, globalKeepouts = []) {
  const widthX = rect.x1 - rect.x0
  const widthY = rect.y1 - rect.y0
  const alongX = widthX >= widthY
  const toLocal = globalKeepouts.map(item => alongX
    ? { u0: item.x0 - rect.x0, u1: item.x1 - rect.x0, v0: item.y0 - rect.y0, v1: item.y1 - rect.y0 }
    : { u0: item.y0 - rect.y0, u1: item.y1 - rect.y0, v0: item.x0 - rect.x0, v1: item.x1 - rect.x0 })
  return alongX
    ? { u0: 0, u1: widthX, v0: 0, v1: widthY, key, continuityKey: key, grainAxis: 'u', centerGrain: true, normal: [0, 0, 1], keepouts: toLocal, pointAt: (u, v, offset) => [rect.x0 + u, rect.y0 + v, z + offset] }
    : { u0: 0, u1: widthY, v0: 0, v1: widthX, key, continuityKey: key, grainAxis: 'u', centerGrain: true, normal: [0, 0, 1], keepouts: toLocal, pointAt: (u, v, offset) => [rect.x0 + v, rect.y0 + u, z + offset] }
}

function wallTopTexturePatches (def, p) {
  const o = p.organizer
  const l = p.layout
  const trim = 4.0
  const junction = p.surface_texture.protected_regions.junction_margin_mm
  const patches = []
  const add = (rect, z, key, keepouts = []) => {
    if (rect.x1 - rect.x0 > 1 && rect.y1 - rect.y0 > 1) patches.push(wallTopPatch(rect, z, key, keepouts))
  }
  const rowPitch = o.depth_y / l.hardware_rows
  const rowCenters = [rowPitch, l.depth_split, 3 * rowPitch].filter(y => y > def.bounds[2] && y < def.bounds[3])
  const yKeepouts = rowCenters.map(y => ({ x0: -1e6, x1: 1e6, y0: y - junction, y1: y + junction }))
  if (def.kind === 'driver') {
    add({ x0: 0, x1: o.outer_wall_thickness, y0: def.bounds[2] + trim, y1: def.bounds[3] - trim }, o.outer_wall_height, `top-driver-outer-${def.rowHalf}`)
    add({ x0: l.screwdriver_zone_width - o.divider_thickness, x1: l.screwdriver_zone_width, y0: def.bounds[2] + trim, y1: def.bounds[3] - trim }, o.outer_wall_height, `top-driver-zone-${def.rowHalf}`, yKeepouts)
  } else {
    const innerRight = o.width_x - o.outer_wall_thickness
    const centerX = (l.screwdriver_zone_width + innerRight) / 2
    add({ x0: innerRight, x1: o.width_x, y0: def.bounds[2] + trim, y1: def.bounds[3] - trim }, o.outer_wall_height, `top-hardware-outer-${def.rowHalf}`, yKeepouts)
    add({ x0: centerX - o.divider_thickness / 2, x1: centerX + o.divider_thickness / 2, y0: def.bounds[2] + trim, y1: def.bounds[3] - trim }, o.divider_height, `top-center-${def.rowHalf}`, yKeepouts)
    const accessX = grooveCenters(p).map(x => ({
      x0: x - l.access_groove_width / 2 - p.surface_texture.protected_regions.access_groove_margin_mm,
      x1: x + l.access_groove_width / 2 + p.surface_texture.protected_regions.access_groove_margin_mm,
      y0: -1e6,
      y1: 1e6
    }))
    const centerKeepout = { x0: centerX - junction, x1: centerX + junction, y0: -1e6, y1: 1e6 }
    const walls = def.rowHalf === 'front' ? [rowPitch, l.depth_split] : [3 * rowPitch]
    for (const y of walls) {
      const splitWall = Math.abs(y - l.depth_split) < 0.01
      const y0 = splitWall ? y - o.divider_thickness : y - o.divider_thickness / 2
      const y1 = splitWall ? y : y + o.divider_thickness / 2
      add({ x0: l.screwdriver_zone_width + trim, x1: o.width_x - trim, y0, y1 }, o.divider_height, `top-row-${y}`, [centerKeepout, ...accessX])
    }
  }
  if (def.bounds[2] === 0) {
    const keepouts = def.kind === 'hardware'
      ? [{
          x0: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 - junction,
          x1: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 + junction,
          y0: -1e6,
          y1: 1e6
        }, ...grooveCenters(p).map(x => ({ x0: x - l.access_groove_width / 2 - 1.5, x1: x + l.access_groove_width / 2 + 1.5, y0: -1e6, y1: 1e6 }))]
      : []
    add({ x0: def.bounds[0] + trim, x1: def.bounds[1] - trim, y0: 0, y1: o.outer_wall_thickness }, o.outer_wall_height, `top-front-${def.kind}`, keepouts)
  }
  if (def.bounds[3] === o.depth_y) {
    const keepouts = def.kind === 'hardware'
      ? [{
          x0: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 - junction,
          x1: (l.screwdriver_zone_width + (o.width_x - o.outer_wall_thickness)) / 2 + junction,
          y0: -1e6,
          y1: 1e6
        }]
      : []
    add({ x0: def.bounds[0] + trim, x1: def.bounds[1] - trim, y0: o.depth_y - o.outer_wall_thickness, y1: o.depth_y }, o.outer_wall_height, `top-back-${def.kind}`, keepouts)
  }
  return patches
}

function applyTexturePatches (shape, patches, surfaceName, p, stats) {
  let result = shape
  for (const patch of patches) {
    const applied = applyProceduralTexturePatch(result, patch, surfaceName, p.surface_texture)
    result = applied.shape
    stats.push(applied.stats)
  }
  return result
}

function buildModule (tray, def, p, segments, withTexture) {
  let shape = clipTrayToModule(tray, def, p)
  const functional = unionMany(functionalWallsAndGussets(def, p))
  if (functional) shape = shape.add(functional)
  const connectors = connectorBodies(def, p, segments)
  const connectorAdds = unionMany(connectors.additions)
  const connectorCuts = unionMany(connectors.cutters)
  if (connectorAdds) shape = shape.add(connectorAdds)
  if (connectorCuts) shape = shape.subtract(connectorCuts)
  const grooves = unionMany(accessGrooveCutters(def, p, segments))
  if (grooves) shape = shape.subtract(grooves)
  const textureStats = []
  if (withTexture && p.surface_texture.enabled) {
    shape = applyTexturePatches(shape, floorTexturePatches(def, p), 'floor', p, textureStats)
    shape = applyTexturePatches(shape, innerWallTexturePatches(def, p), 'inner_walls', p, textureStats)
    shape = applyTexturePatches(shape, wallTopTexturePatches(def, p), 'wall_tops', p, textureStats)
  }
  const junctions = unionMany(junctionBlendBodies(def, p, segments))
  if (junctions) {
    const next = shape.add(junctions)
    shape.delete()
    junctions.delete()
    shape = next
  }
  return { def, smooth: shape, textured: shape, texture_stats: summarizeTextureStats(textureStats) }
}

function assertParameters (p) {
  if (p.organizer.width_x > p.drawer.inside_width_x || p.organizer.depth_y > p.drawer.inside_depth_y) throw new Error('organizer exceeds drawer')
  const minimum = p.surface_texture.protected_regions.minimum_residual_wall_mm
  const maximumSurfaceDepth = surface => Math.max(
    ...surface.grain.depth_mm,
    ...(surface.knots?.enabled ? surface.knots.depth_mm : [0])
  )
  const floorDepth = maximumSurfaceDepth(p.surface_texture.surfaces.floor)
  const wallDepth = maximumSurfaceDepth(p.surface_texture.surfaces.inner_walls)
  if (p.organizer.floor_thickness - floorDepth < minimum) throw new Error('floor texture violates residual-wall requirement')
  if (p.organizer.divider_thickness - 2 * wallDepth < minimum) throw new Error('double-sided divider texture violates residual-wall requirement')
  if (p.surface_texture.surfaces.outer_walls.enabled) throw new Error('R1.5 approved concept requires smooth outer walls')
  if (p.layout.access_groove_width <= 2 * p.layout.access_groove_bottom_radius) throw new Error('access groove width must exceed twice the bottom radius')
  if (p.layout.access_groove_depth < p.layout.access_groove_bottom_radius) throw new Error('access groove depth is smaller than its bottom radius')
  if (p.layout.hardware_columns !== 2 || p.layout.hardware_rows !== 4) throw new Error('R1 requires exactly eight hardware bins')
}

export function buildModulesManifold (p, options = {}) {
  assertParameters(p)
  const segments = options.segments ?? p.export.segments_final
  const tray = globalOuterTray(p)
  const requested = options.moduleIds ? new Set(options.moduleIds) : null
  const definitions = moduleDefinitions(p).filter(def => requested === null || requested.has(def.id))
  if (requested && definitions.length !== requested.size) throw new Error('unknown module id requested')
  const builtModules = definitions.map(def => {
    const built = buildModule(tray, def, p, segments, options.withTexture ?? true)
    if (options.withWatermark && p.watermark?.enabled && options.watermarkOutline) {
      const placement = p.watermark.placements_global_xy[def.id]
      const cutter = watermarkCutter(
        options.watermarkOutline,
        placement,
        p.watermark.depth,
        p.watermark.boolean_overlap
      )
      const marked = built.textured.subtract(cutter)
      built.textured.delete()
      cutter.delete()
      built.smooth = marked
      built.textured = marked
    }
    return built
  })
  tray.delete()
  return builtModules
}

export function buildCombManifold (p, segments) {
  const c = p.comb
  let shape = box(0, c.width, 0, c.depth, 0, c.height)
  const usable = c.width - 2 * c.slot_radius
  const pitch = usable / (c.slot_count - 1)
  const cutters = []
  for (let i = 0; i < c.slot_count; i += 1) {
    const x = c.slot_radius + i * pitch
    cutters.push(
      Manifold.cylinder(c.depth + 2, c.slot_radius, c.slot_radius, segments, true)
        .rotate([90, 0, 0])
        .translate([x, c.depth / 2, c.height])
    )
    cutters.push(box(x - c.slot_radius, x + c.slot_radius, -1, c.depth + 1, c.height, c.height + c.slot_radius + 1))
  }
  return shape.subtract(unionMany(cutters))
}

export function buildFitCouponManifold (p) {
  return globalOuterTray(p).intersect(box(0, 40, 0, 40, 0, 12))
}

export function buildTextureCouponManifold (p) {
  const floor = p.organizer.floor_thickness
  let shape = unionMany([
    box(0, 90, 0, 50, 0, floor),
    box(0, 90, 47, 50, 0, 30)
  ])
  const stats = []
  const floorPatches = [
    { x0: 18, x1: 40, pitchScale: 0.78, depthScale: 0.75, amplitudeScale: 0.75, allowKnots: false, name: 'fine' },
    { x0: 41, x1: 65, pitchScale: 1.0, depthScale: 1.0, amplitudeScale: 1.0, knotScale: 0.55, allowKnots: true, forceKnot: true, name: 'approved' },
    { x0: 66, x1: 88, pitchScale: 1.25, depthScale: 1.10, amplitudeScale: 1.15, allowKnots: false, name: 'coarse' }
  ].map(item => ({
    u0: item.x0,
    u1: item.x1,
    v0: 2,
    v1: 45,
    key: `coupon-floor-${item.name}`,
    continuityKey: `coupon-floor-${item.name}`,
    grainAxis: 'v',
    pitchScale: item.pitchScale,
    depthScale: item.depthScale,
    amplitudeScale: item.amplitudeScale,
    knotScale: item.knotScale,
    allowKnots: item.allowKnots,
    forceKnot: item.forceKnot,
    normal: [0, 0, 1],
    pointAt: (x, y, offset) => [x, y, floor + offset]
  }))
  shape = applyTexturePatches(shape, floorPatches, 'floor', p, stats)
  shape = applyTexturePatches(shape, [{
    u0: 18,
    u1: 88,
    v0: floor + p.surface_texture.surfaces.inner_walls.bottom_keepout_mm,
    v1: 28,
    key: 'coupon-wall-approved',
    continuityKey: 'coupon-wall-approved',
    grainAxis: 'u',
    normal: [0, -1, 0],
    pointAt: (x, z, offset) => [x, 47 - offset, z]
  }], 'inner_walls', p, stats)
  shape = applyTexturePatches(shape, [wallTopPatch({ x0: 18, x1: 88, y0: 47, y1: 50 }, 30, 'coupon-top-approved')], 'wall_tops', p, stats)
  return shape
}

export function buildConnectorCouponManifold (p, segments) {
  const height = p.organizer.floor_thickness
  const maleBase = box(0, 20, 0, 20, 0, height)
  const male = maleBase.add(xMaleConnector(20, 10, p, segments))
  const femaleBase = box(0, 20, 0, 20, 0, height)
  // Translate the production female cutter so its mating edge lies at x = 0.
  const productionCutter = xFemaleConnector(p.layout.screwdriver_zone_width, 10, p, segments)
    .translate([-p.layout.screwdriver_zone_width, 0, 0])
  const female = femaleBase.subtract(productionCutter)
  return { male, female }
}

export function assemblyEnvelope (modules) {
  const bounds = modules.map(module => module.textured.boundingBox())
  return {
    min: [0, 1, 2].map(axis => Math.min(...bounds.map(bound => bound.min[axis]))),
    max: [0, 1, 2].map(axis => Math.max(...bounds.map(bound => bound.max[axis])))
  }
}
