import { CrossSection, Manifold, Mesh } from 'manifold-3d/manifoldCAD'

import { clipProceduralWoodPlan, planProceduralWoodRegion } from './procedural_wood.mjs'
import { watermarkCutter } from './watermark.mjs'

const EPS = 1.0e-6
const R2_MODULE_IDS = new Set([
  'driver-front',
  'driver-back',
  'hardware-front',
  'hardware-back'
])
const R2_ASSEMBLY_FLOOR_SOURCE_ID = 'assembly-global-organizer-floor'

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

function unionOwnedBatched (items, batchSize = 64) {
  let level = items.filter(Boolean)
  if (level.length === 0) return null
  while (level.length > 1) {
    const next = []
    for (let first = 0; first < level.length; first += batchSize) {
      const batch = level.slice(first, first + batchSize)
      if (batch.length === 1) {
        next.push(batch[0])
        continue
      }
      const joined = Manifold.union(batch)
      for (const item of batch) item.delete()
      next.push(joined)
    }
    level = next
  }
  return level[0]
}

function clamp (value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, value))
}

function degrees (radians) {
  return radians * 180 / Math.PI
}

function hashSeed (seed, text) {
  let value = (Number(seed) >>> 0) ^ 0x811c9dc5
  for (let index = 0; index < text.length; index += 1) {
    value ^= text.charCodeAt(index)
    value = Math.imul(value, 0x01000193) >>> 0
  }
  return value >>> 0
}

function seededRandom (seed, key) {
  let state = hashSeed(seed, key)
  return () => {
    state = (state + 0x6d2b79f5) >>> 0
    let value = state
    value = Math.imul(value ^ (value >>> 15), value | 1)
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61)
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296
  }
}

function interpolateRange (rangeMinimum, rangeMaximum, fraction) {
  return rangeMinimum + (rangeMaximum - rangeMinimum) * fraction
}

function roundedPolylineCutter (path, points, normal, textureConfig) {
  if (points.length < 2) return null
  const radius = path.width_mm / 2
  const booleanOverlap = Math.min(0.02, path.depth_mm / 4)
  const normalAxis = normal.findIndex(value => Math.abs(value) > 0.5)
  if (normalAxis < 0 || normal.filter(value => Math.abs(value) > EPS).length !== 1) {
    throw new Error('procedural wood cutter normal must be axis-aligned')
  }
  const normalScale = (path.depth_mm + booleanOverlap) / radius
  const scale = [1, 1, 1]
  scale[normalAxis] = normalScale
  const shifted = point => point.map((value, axis) => value + normal[axis] * booleanOverlap)
  const parts = []
  const endpointCount = path.closed ? points.length - 1 : points.length
  for (let index = 0; index < endpointCount; index += 1) {
    parts.push(
      Manifold.sphere(radius, textureConfig.grain.endpoint_segments)
        .scale(scale)
        .translate(shifted(points[index]))
    )
  }
  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index]
    const end = points[index + 1]
    const delta = end.map((value, axis) => value - start[axis])
    const length = Math.hypot(...delta)
    if (length <= EPS) continue
    const tangent = delta.map(value => value / length)
    const overlap = textureConfig.grain.segment_overlap_mm
    const extendedLength = length + overlap
    const midpoint = start.map((value, axis) => (value + end[axis]) / 2)
    const pitch = degrees(Math.acos(clamp(tangent[2], -1, 1)))
    const azimuth = degrees(Math.atan2(tangent[1], tangent[0]))
    parts.push(
      Manifold.cylinder(extendedLength, radius, radius, textureConfig.grain.tube_segments, true)
        .rotate([0, pitch, azimuth])
        .scale(scale)
        .translate(shifted(midpoint))
    )
  }
  return unionOwnedBatched(parts)
}

function planPaths (plan) {
  return [
    ...plan.paths,
    ...plan.knots.flatMap(knot => knot.contours)
  ]
}

function engraveMappedPaths (shape, entries, textureConfig) {
  const cutters = entries.map(entry => roundedPolylineCutter(
    entry.path,
    entry.path.points_mm.map(entry.pointAt),
    entry.normal,
    textureConfig
  )).filter(Boolean)
  const cutter = unionOwnedBatched(cutters)
  if (!cutter) return shape
  const engraved = shape.subtract(cutter)
  shape.delete()
  cutter.delete()
  return engraved
}

function engravePlan (shape, plan, pointAt, normal, textureConfig) {
  return engraveMappedPaths(
    shape,
    planPaths(plan).map(path => ({ path, pointAt, normal })),
    textureConfig
  )
}

function splitPathAtAxisValue (path, axis, value) {
  const points = path.points_mm
  const crossing = points.findIndex(point => point[axis] >= value)
  if (crossing < 0) return [path, null]
  if (crossing === 0) return [null, path]
  if (points[crossing][axis] === value) {
    return [
      { ...path, points_mm: points.slice(0, crossing + 1) },
      { ...path, points_mm: points.slice(crossing) }
    ]
  }
  const before = points[crossing - 1]
  const after = points[crossing]
  const fraction = (value - before[axis]) / (after[axis] - before[axis])
  const intersection = before.map((coordinate, coordinateAxis) => (
    coordinate + (after[coordinateAxis] - coordinate) * fraction
  ))
  return [
    { ...path, points_mm: [...points.slice(0, crossing), intersection] },
    { ...path, points_mm: [intersection, ...points.slice(crossing)] }
  ]
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
  return unionOwnedBatched(parts)
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
  const tray = outer.subtract(inner)
  outer.delete()
  inner.delete()
  return tray
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
  const clippingBox = box(x0, x1, y0, y1, 0, p.organizer.outer_wall_height)
  const clipped = tray.intersect(clippingBox)
  clippingBox.delete()
  return clipped
}

function functionalWallsAndGussets (def, p) {
  const o = p.organizer
  const l = p.layout
  const dt = o.divider_thickness
  const zone = l.screwdriver_zone_width
  const parts = []
  if (def.kind === 'driver') {
    parts.push(box(zone - dt, zone, def.bounds[2], def.bounds[3], 0, o.outer_wall_height))
    parts.push(...driverRootGussetBodies(def, p))
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

function driverRootGussetBodies (def, p) {
  if (def.kind !== 'driver') return []
  const o = p.organizer
  const zone = p.layout.screwdriver_zone_width
  const dt = o.divider_thickness
  const markers = [89.25, 178.5, 267.75].filter(y => y > def.bounds[2] + 5 && y < def.bounds[3] - 5)
  return markers.flatMap(y => [
    trianglePrism([[o.outer_wall_thickness - 0.4, y - 4], [o.outer_wall_thickness + 4, y], [o.outer_wall_thickness - 0.4, y + 4]], o.root_gusset_height),
    trianglePrism([[zone - dt + 0.4, y - 4], [zone - dt - 4, y], [zone - dt + 0.4, y + 4]], o.root_gusset_height)
  ])
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
  return unionOwnedBatched([
    cylinderZ(edgeX + c.lug_radius, cy, c.lug_radius, 0, h, segments),
    box(edgeX - 0.6, edgeX + c.lug_radius, cy - c.neck_width / 2, cy + c.neck_width / 2, 0, h)
  ])
}

function xFemaleConnector (edgeX, cy, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  return unionOwnedBatched([
    cylinderZ(edgeX + c.lug_radius, cy, c.lug_radius + c.clearance, -0.3, h + 0.3, segments),
    box(edgeX - 0.3, edgeX + c.lug_radius, cy - c.neck_width / 2 - c.clearance, cy + c.neck_width / 2 + c.clearance, -0.3, h + 0.3)
  ])
}

function yMaleConnector (edgeY, cx, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  return unionOwnedBatched([
    cylinderZ(cx, edgeY + c.lug_radius, c.lug_radius, 0, h, segments),
    box(cx - c.neck_width / 2, cx + c.neck_width / 2, edgeY - 0.6, edgeY + c.lug_radius, 0, h)
  ])
}

function yFemaleConnector (edgeY, cx, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  return unionOwnedBatched([
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
  return unionOwnedBatched([
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
  const margin = p.surface_texture?.watermark_keepout ?? p.relief?.watermark_keepout ?? 0
  return {
    x0: placement[0] - envelope[0] / 2 - margin,
    x1: placement[0] + envelope[0] / 2 + margin,
    y0: placement[1] - envelope[1] / 2 - margin,
    y1: placement[1] + envelope[1] / 2 + margin
  }
}

function floorRectsWithMarkKeepout (def, p, textureConfig) {
  const keepout = watermarkKeepout(def, p)
  if (!keepout) return floorRectsForModule(def, p, textureConfig)
  return floorRectsForModule(def, p, textureConfig).flatMap(rect => subtractRectangle(rect, keepout))
}

function floorRectsForModule (def, p, textureConfig) {
  const o = p.organizer
  const l = p.layout
  const margin = l.floor_texture_margin ?? textureConfig?.grain.floor_margin_mm ?? l.floor_relief_margin
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
  const xRanges = [
    [l.screwdriver_zone_width + margin, centerX - o.divider_thickness / 2 - margin],
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

function positiveModulo (value, period) {
  return ((value % period) + period) % period
}

function heightfieldSamples (manifest) {
  if (manifest.schema_version !== 2 || manifest.representation !== 'continuous-heightfield-u16') {
    throw new Error('relief manifest must use schema 2 continuous-heightfield-u16')
  }
  if (manifest._samplesU16) return manifest._samplesU16
  const [nx, ny] = manifest.grid
  const encoded = Buffer.from(manifest.samples_u16_base64, 'base64')
  if (encoded.length !== nx * ny * 2) throw new Error('16-bit relief payload length does not match the declared grid')
  const samples = new Uint16Array(nx * ny)
  for (let i = 0; i < samples.length; i += 1) samples[i] = encoded.readUInt16LE(i * 2)
  Object.defineProperty(manifest, '_samplesU16', { value: samples, enumerable: false })
  return samples
}

function sampleHeightfieldU16 (manifest, u, v, scale) {
  const samples = heightfieldSamples(manifest)
  const [nx, ny] = manifest.grid
  const tileW = manifest.tile_width_mm * scale
  const tileH = manifest.tile_height_mm * scale
  const uFraction = positiveModulo(u, tileW) / tileW
  const vFraction = positiveModulo(v, tileH) / tileH
  const x = uFraction * (nx - 1)
  // Image row zero maps to the high-V edge. Matching prepared borders make the
  // modulo discontinuity exactly periodic.
  const y = (1 - vFraction) * (ny - 1)
  const x0 = Math.floor(x)
  const y0 = Math.floor(y)
  const x1 = Math.min(nx - 1, x0 + 1)
  const y1 = Math.min(ny - 1, y0 + 1)
  const tx = x - x0
  const ty = y - y0
  const a = samples[y0 * nx + x0] * (1 - tx) + samples[y0 * nx + x1] * tx
  const b = samples[y1 * nx + x0] * (1 - tx) + samples[y1 * nx + x1] * tx
  return a * (1 - ty) + b * ty
}

function signedReliefMm (manifest, sample, relief) {
  const mapping = manifest.height_mapping
  const neutral = mapping.neutral_u16
  const exponent = mapping.curve_exponent ?? 1
  if (sample <= neutral) {
    const span = neutral - mapping.input_min_u16
    const normalized = Math.max(0, Math.min(1, (neutral - sample) / span))
    return -relief.engrave_depth * Math.pow(normalized, exponent)
  }
  const span = mapping.input_max_u16 - neutral
  const normalized = Math.max(0, Math.min(1, (sample - neutral) / span))
  return relief.emboss_depth * Math.pow(normalized, exponent)
}

function cross3 (a, b) {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ]
}

function dot3 (a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

function subtract3 (a, b) {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

function heightfieldSolid (manifest, target, relief, normal, pointAt) {
  const pitch = Math.min(manifest.pitch_x_mm, manifest.pitch_y_mm) * relief.tile_scale
  const nu = Math.max(2, Math.ceil((target.u1 - target.u0) / pitch) + 1)
  const nv = Math.max(2, Math.ceil((target.v1 - target.v0) / pitch) + 1)
  const vertexCount = 2 * nu * nv
  const properties = new Float32Array(vertexCount * 3)
  const topIndex = (i, j) => j * nu + i
  const bottomIndex = (i, j) => nu * nv + j * nu + i
  const put = (index, point) => {
    properties[index * 3] = point[0]
    properties[index * 3 + 1] = point[1]
    properties[index * 3 + 2] = point[2]
  }
  for (let j = 0; j < nv; j += 1) {
    const v = target.v0 + (target.v1 - target.v0) * j / (nv - 1)
    for (let i = 0; i < nu; i += 1) {
      const u = target.u0 + (target.u1 - target.u0) * i / (nu - 1)
      const sample = sampleHeightfieldU16(manifest, u, v, relief.tile_scale)
      const displacement = signedReliefMm(manifest, sample, relief)
      put(topIndex(i, j), pointAt(u, v, displacement))
      put(bottomIndex(i, j), pointAt(u, v, -relief.engrave_depth - relief.boolean_overlap))
    }
  }

  const p00 = pointAt(target.u0, target.v0, 0)
  const pu = pointAt(target.u1, target.v0, 0)
  const pv = pointAt(target.u0, target.v1, 0)
  const parameterNormal = cross3(subtract3(pu, p00), subtract3(pv, p00))
  const forward = dot3(parameterNormal, normal) > 0
  const triangles = []
  for (let j = 0; j < nv - 1; j += 1) {
    for (let i = 0; i < nu - 1; i += 1) {
      const a = topIndex(i, j)
      const b = topIndex(i + 1, j)
      const c = topIndex(i + 1, j + 1)
      const d = topIndex(i, j + 1)
      const aa = bottomIndex(i, j)
      const bb = bottomIndex(i + 1, j)
      const cc = bottomIndex(i + 1, j + 1)
      const dd = bottomIndex(i, j + 1)
      if (forward) {
        triangles.push(a, b, c, a, c, d)
        triangles.push(aa, cc, bb, aa, dd, cc)
      } else {
        triangles.push(a, c, b, a, d, c)
        triangles.push(aa, bb, cc, aa, cc, dd)
      }
    }
  }

  let boundary = []
  for (let i = 0; i < nu; i += 1) boundary.push([i, 0])
  for (let j = 1; j < nv; j += 1) boundary.push([nu - 1, j])
  for (let i = nu - 2; i >= 0; i -= 1) boundary.push([i, nv - 1])
  for (let j = nv - 2; j > 0; j -= 1) boundary.push([0, j])
  if (!forward) boundary = boundary.reverse()
  for (let k = 0; k < boundary.length; k += 1) {
    const [i0, j0] = boundary[k]
    const [i1, j1] = boundary[(k + 1) % boundary.length]
    const t0 = topIndex(i0, j0)
    const t1 = topIndex(i1, j1)
    const b0 = bottomIndex(i0, j0)
    const b1 = bottomIndex(i1, j1)
    triangles.push(t0, b0, b1, t0, b1, t1)
  }
  const mesh = new Mesh({
    numProp: 3,
    vertProperties: properties,
    triVerts: new Uint32Array(triangles),
    tolerance: 1.0e-6
  })
  return Manifold.ofMesh(mesh)
}

function floorReliefBodies (manifest, rect, surfaceZ, relief) {
  const target = { u0: rect.x0, u1: rect.x1, v0: rect.y0, v1: rect.y1 }
  const inset = 0.02
  const cutter = box(
    rect.x0 + inset, rect.x1 - inset,
    rect.y0 + inset, rect.y1 - inset,
    surfaceZ - relief.engrave_depth,
    surfaceZ + relief.emboss_depth + relief.boolean_overlap
  )
  const patch = heightfieldSolid(
    manifest,
    target,
    relief,
    [0, 0, 1],
    (x, y, offset) => [x, y, surfaceZ + offset]
  )
  return { additions: [patch], cutters: [cutter] }
}

function wallXReliefBodies (manifest, spec, relief) {
  const target = { u0: spec.y0, u1: spec.y1, v0: spec.z0, v1: spec.z1 }
  const inward = spec.x - spec.normal * relief.engrave_depth
  const outward = spec.x + spec.normal * (relief.emboss_depth + relief.boolean_overlap)
  const inset = 0.02
  const cutter = box(
    Math.min(inward, outward), Math.max(inward, outward),
    spec.y0 + inset, spec.y1 - inset,
    spec.z0 + inset, spec.z1 - inset
  )
  const patch = heightfieldSolid(
    manifest,
    target,
    relief,
    [spec.normal, 0, 0],
    (y, z, offset) => [spec.x + spec.normal * offset, y, z]
  )
  return { additions: [patch], cutters: [cutter] }
}

function wallYReliefBodies (manifest, spec, relief) {
  const target = { u0: spec.x0, u1: spec.x1, v0: spec.z0, v1: spec.z1 }
  const inward = spec.y - spec.normal * relief.engrave_depth
  const outward = spec.y + spec.normal * (relief.emboss_depth + relief.boolean_overlap)
  const inset = 0.02
  const cutter = box(
    spec.x0 + inset, spec.x1 - inset,
    Math.min(inward, outward), Math.max(inward, outward),
    spec.z0 + inset, spec.z1 - inset
  )
  const patch = heightfieldSolid(
    manifest,
    target,
    relief,
    [0, spec.normal, 0],
    (x, z, offset) => [x, spec.y + spec.normal * offset, z]
  )
  return { additions: [patch], cutters: [cutter] }
}

function mergeGroups (...groups) {
  return {
    additions: groups.flatMap(group => group.additions),
    cutters: groups.flatMap(group => group.cutters)
  }
}

function * wallReliefGroups (def, p, manifest) {
  const o = p.organizer
  const l = p.layout
  const r = p.relief
  const wallRelief = { ...r, engrave_depth: r.wall_engrave_depth }
  const outerRelief = {
    ...r,
    emboss_depth: r.outer_panel_recess,
    engrave_depth: r.outer_wall_engrave_depth
  }
  const z0 = r.wall_band_bottom
  const z1 = Math.min(r.wall_band_top, o.outer_wall_height - 3)
  const y0 = def.bounds[2] + 4
  const y1 = def.bounds[3] - 4
  const recessedOuterX = (x, normal, a, b) => {
    const shifted = x - normal * r.outer_panel_recess
    const cutter = box(Math.min(x, shifted) - (normal < 0 ? r.boolean_overlap : 0), Math.max(x, shifted) + (normal > 0 ? r.boolean_overlap : 0), a, b, z0, z1)
    return mergeGroups({ additions: [], cutters: [cutter] }, wallXReliefBodies(manifest, { x: shifted, normal, y0: a, y1: b, z0, z1 }, outerRelief))
  }
  const recessedOuterY = (y, normal, a, b) => {
    const shifted = y - normal * r.outer_panel_recess
    const cutter = box(a, b, Math.min(y, shifted) - (normal < 0 ? r.boolean_overlap : 0), Math.max(y, shifted) + (normal > 0 ? r.boolean_overlap : 0), z0, z1)
    return mergeGroups({ additions: [], cutters: [cutter] }, wallYReliefBodies(manifest, { y: shifted, normal, x0: a, x1: b, z0, z1 }, outerRelief))
  }
  if (r.apply_outer_walls) {
    if (def.kind === 'driver') yield recessedOuterX(0, -1, y0, y1)
    else yield recessedOuterX(o.width_x, 1, y0, y1)
    if (def.bounds[2] === 0) yield recessedOuterY(0, -1, def.bounds[0] + 4, def.bounds[1] - 4)
    if (def.bounds[3] === o.depth_y) yield recessedOuterY(o.depth_y, 1, def.bounds[0] + 4, def.bounds[1] - 4)
  }
  if (r.apply_inner_walls) {
    if (def.kind === 'driver') {
      yield wallXReliefBodies(manifest, { x: o.outer_wall_thickness, normal: 1, y0, y1, z0, z1 }, wallRelief)
      yield wallXReliefBodies(manifest, { x: l.screwdriver_zone_width - o.divider_thickness, normal: -1, y0, y1, z0, z1 }, wallRelief)
      yield wallXReliefBodies(manifest, { x: l.screwdriver_zone_width, normal: 1, y0, y1, z0, z1 }, wallRelief)
    } else {
      const innerRight = o.width_x - o.outer_wall_thickness
      const centerX = (l.screwdriver_zone_width + innerRight) / 2
      const innerTop = Math.min(z1, o.divider_height - 3)
      yield wallXReliefBodies(manifest, { x: innerRight, normal: -1, y0, y1, z0, z1 }, wallRelief)
      yield wallXReliefBodies(manifest, { x: centerX - o.divider_thickness / 2, normal: -1, y0, y1, z0, z1: innerTop }, wallRelief)
      yield wallXReliefBodies(manifest, { x: centerX + o.divider_thickness / 2, normal: 1, y0, y1, z0, z1: innerTop }, wallRelief)
      const rowPitch = o.depth_y / l.hardware_rows
      const walls = def.rowHalf === 'front' ? [rowPitch, l.depth_split] : [3 * rowPitch]
      for (const y of walls) {
        const isSplitWall = Math.abs(y - l.depth_split) < 0.01
        const faceA = isSplitWall ? y - o.divider_thickness : y - o.divider_thickness / 2
        const faceB = isSplitWall ? y : y + o.divider_thickness / 2
        yield wallYReliefBodies(manifest, { y: faceA, normal: -1, x0: l.screwdriver_zone_width + 4, x1: o.width_x - 4, z0, z1: innerTop }, wallRelief)
        yield wallYReliefBodies(manifest, { y: faceB, normal: 1, x0: l.screwdriver_zone_width + 4, x1: o.width_x - 4, z0, z1: innerTop }, wallRelief)
      }
    }
    if (def.bounds[2] === 0) yield wallYReliefBodies(manifest, { y: o.outer_wall_thickness, normal: 1, x0: def.bounds[0] + 4, x1: def.bounds[1] - 4, z0, z1 }, wallRelief)
    if (def.bounds[3] === o.depth_y) yield wallYReliefBodies(manifest, { y: o.depth_y - o.outer_wall_thickness, normal: -1, x0: def.bounds[0] + 4, x1: def.bounds[1] - 4, z0, z1 }, wallRelief)
  }
}

function applyReliefGroup (shape, group) {
  let result = shape
  for (const cutter of group.cutters) {
    const next = result.subtract(cutter)
    result.delete()
    cutter.delete()
    result = next
  }
  for (const addition of group.additions) {
    const next = result.add(addition)
    result.delete()
    addition.delete()
    result = next
  }
  return result
}

function buildModule (tray, def, p, manifest, segments, withRelief) {
  let shape = clipTrayToModule(tray, def, p)
  const functional = unionOwnedBatched(functionalWallsAndGussets(def, p))
  if (functional) {
    const next = shape.add(functional)
    shape.delete()
    functional.delete()
    shape = next
  }
  const connectors = connectorBodies(def, p, segments)
  const connectorAdds = unionOwnedBatched(connectors.additions)
  const connectorCuts = unionOwnedBatched(connectors.cutters)
  if (connectorAdds) {
    const next = shape.add(connectorAdds)
    shape.delete()
    connectorAdds.delete()
    shape = next
  }
  if (connectorCuts) {
    const next = shape.subtract(connectorCuts)
    shape.delete()
    connectorCuts.delete()
    shape = next
  }
  const grooves = unionOwnedBatched(accessGrooveCutters(def, p, segments))
  if (grooves) {
    const next = shape.subtract(grooves)
    shape.delete()
    grooves.delete()
    shape = next
  }
  if (withRelief && p.relief.enabled) {
    if (p.relief.apply_floor) {
      for (const rect of floorRectsWithMarkKeepout(def, p)) {
        shape = applyReliefGroup(shape, floorReliefBodies(manifest, rect, p.organizer.floor_thickness, p.relief))
      }
    }
    for (const group of wallReliefGroups(def, p, manifest)) {
      shape = applyReliefGroup(shape, group)
    }
  }
  const junctions = unionOwnedBatched(junctionBlendBodies(def, p, segments))
  if (junctions) {
    const next = shape.add(junctions)
    shape.delete()
    junctions.delete()
    shape = next
  }
  return { def, smooth: shape, textured: shape }
}

function assertParameters (p) {
  if (p.organizer.width_x > p.drawer.inside_width_x || p.organizer.depth_y > p.drawer.inside_depth_y) throw new Error('organizer exceeds drawer')
  if (p.organizer.floor_thickness - p.relief.engrave_depth < 2) throw new Error('floor relief leaves less than 2.0 mm')
  if (p.organizer.divider_thickness - 2 * p.relief.wall_engrave_depth < 2) throw new Error('double-sided divider relief leaves less than 2.0 mm')
  if (p.organizer.outer_wall_thickness - p.relief.outer_panel_recess - p.relief.outer_wall_engrave_depth - p.relief.wall_engrave_depth < 2) throw new Error('double-sided outer-wall relief leaves less than 2.0 mm')
  if (p.layout.access_groove_width <= 2 * p.layout.access_groove_bottom_radius) throw new Error('access groove width must exceed twice the bottom radius')
  if (p.layout.access_groove_depth < p.layout.access_groove_bottom_radius) throw new Error('access groove depth is smaller than its bottom radius')
  if (p.layout.hardware_columns !== 2 || p.layout.hardware_rows !== 4) throw new Error('R1 requires exactly eight hardware bins')
}

export function buildModulesManifold (p, manifest, options = {}) {
  assertParameters(p)
  const segments = options.segments ?? p.export.segments_final
  const tray = globalOuterTray(p)
  const requested = options.moduleIds ? new Set(options.moduleIds) : null
  const definitions = moduleDefinitions(p).filter(def => requested === null || requested.has(def.id))
  if (requested && definitions.length !== requested.size) throw new Error('unknown module id requested')
  const builtModules = definitions.map(def => {
    const built = buildModule(tray, def, p, manifest, segments, options.withRelief ?? true)
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

function assertR2ModuleTextureParameters (p, textureConfig, moduleId) {
  if (!R2_MODULE_IDS.has(moduleId)) throw new Error('R2 procedural-wood module builder received an unknown module id')
  if (!p.surface_texture?.enabled) throw new Error('R2 procedural-wood module builder requires enabled surface_texture parameters')
  if (p.surface_texture.representation !== 'procedural-vector-wood-grooves') {
    throw new Error('R2 procedural-wood module builder requires procedural-vector-wood-grooves representation')
  }
  if (!p.surface_texture.apply_floor || !p.surface_texture.apply_inner_walls || !p.surface_texture.apply_top_faces) {
    throw new Error('R2 module integration requires floor, inner-wall, and top surface groups')
  }
  if (p.surface_texture.apply_outer_walls !== false) throw new Error('R2 module integration requires smooth outer wall faces')
  if (p.layout.floor_texture_margin !== 2.0 || textureConfig.grain.floor_margin_mm !== 2.0) {
    throw new Error('R2 module integration requires the approved 2.0 mm floor margin')
  }
  if (textureConfig.surface_policy.operation !== 'engrave-only') throw new Error('R2 module integration is engrave-only')
  if (p.organizer.floor_thickness - textureConfig.grain.floor_depth_mm < 2.4 - EPS) {
    throw new Error('R2 floor texture leaves less than the approved 2.40 mm residual floor')
  }
  if (p.organizer.divider_thickness - 2 * textureConfig.grain.inner_wall_depth_mm < 2.88 - EPS) {
    throw new Error('R2 inner-wall texture leaves less than the approved 2.88 mm double-sided divider reserve')
  }
  const def = moduleDefinitions(p).find(item => item.id === moduleId)
  if (!def) throw new Error('R2 module definition is unavailable')
  if (!watermarkKeepout(def, p)) throw new Error('R2 floor planning requires the approved watermark-opposite keepout')
  return def
}

function subtractRectangleInHorizontalBands (rect, hole) {
  const ix0 = Math.max(rect.x0, hole.x0)
  const ix1 = Math.min(rect.x1, hole.x1)
  const iy0 = Math.max(rect.y0, hole.y0)
  const iy1 = Math.min(rect.y1, hole.y1)
  if (ix1 <= ix0 || iy1 <= iy0) return [rect]
  return [
    { x0: rect.x0, x1: rect.x1, y0: rect.y0, y1: iy0 },
    { x0: rect.x0, x1: rect.x1, y0: iy1, y1: rect.y1 },
    { x0: rect.x0, x1: ix0, y0: iy0, y1: iy1 },
    { x0: ix1, x1: rect.x1, y0: iy0, y1: iy1 }
  ].filter(item => item.x1 - item.x0 > EPS && item.y1 - item.y0 > EPS)
}

function driverFloorRectangles (def, p, textureConfig) {
  const keepout = watermarkKeepout(def, p)
  return floorRectsForModule(def, p, textureConfig)
    .flatMap(rect => subtractRectangleInHorizontalBands(rect, keepout))
}

function placementFitsRectangle (placement, rectangle) {
  const radius = placement.diameter_mm / 2
  const [x, y] = placement.center_global_xy_mm
  return x - radius >= rectangle.x0 && x + radius <= rectangle.x1 &&
    y - radius >= rectangle.y0 && y + radius <= rectangle.y1
}

function splitIntervalByKeepouts (minimum, maximum, keepouts) {
  const clipped = keepouts
    .map(keepout => ({
      ...keepout,
      min: Math.max(minimum, keepout.min),
      max: Math.min(maximum, keepout.max)
    }))
    .filter(keepout => keepout.max - keepout.min > EPS)
    .sort((first, second) => first.min - second.min)
  const intervals = []
  let cursor = minimum
  for (const keepout of clipped) {
    if (keepout.min > cursor + EPS) intervals.push([cursor, keepout.min])
    cursor = Math.max(cursor, keepout.max)
  }
  if (maximum > cursor + EPS) intervals.push([cursor, maximum])
  return intervals
}

function numberedId (base, index) {
  return `${base}-patch-${String(index + 1).padStart(2, '0')}`
}

function makeFloorTargets (def, rectangles, textureConfig, floorTop, sourceIds) {
  const sourceCounts = new Map()
  return rectangles.map(rectangle => {
    const patchSourceId = sourceIds(rectangle)
    const patchIndex = sourceCounts.get(patchSourceId) ?? 0
    sourceCounts.set(patchSourceId, patchIndex + 1)
    return {
      sourceId: R2_ASSEMBLY_FLOOR_SOURCE_ID,
      faceClass: def.kind === 'hardware' ? 'hardware-compartment-floor' : 'driver-zone-floor',
      region: {
        id: numberedId(`${def.id}-${patchSourceId}`, patchIndex),
        surface: 'floor',
        rectangle_mm: { min: [rectangle.x0, rectangle.y0], max: [rectangle.x1, rectangle.y1] },
        module: def.id
      },
      plane: { axis: 'z', coordinate_mm: floorTop, normal: 1 },
      pointAt: point => [point[0], point[1], floorTop],
      normal: [0, 0, 1]
    }
  })
}

function makeXWallTargets ({
  id,
  faceClass,
  x,
  normal,
  y0,
  y1,
  z0,
  z1,
  junctionKeepouts = []
}) {
  return [[y0, y1]].map((interval, index) => ({
    sourceId: id,
    faceClass,
    junctionKeepouts,
    region: {
      id: numberedId(id, index),
      surface: 'wall',
      rectangle_mm: { min: [interval[0], z0], max: [interval[1], z1] },
      long_axis: 0
    },
    plane: { axis: 'x', coordinate_mm: x, normal },
    pointAt: point => [x, point[0], point[1]],
    normal: [normal, 0, 0]
  }))
}

function makeYWallTargets ({
  id,
  faceClass,
  y,
  normal,
  x0,
  x1,
  z0,
  z1,
  accessGrooveKeepouts = [],
  junctionKeepouts = []
}) {
  const keepouts = accessGrooveKeepouts
  return splitIntervalByKeepouts(x0, x1, keepouts).map((interval, index) => ({
    sourceId: id,
    faceClass,
    accessGrooveKeepouts,
    junctionKeepouts,
    region: {
      id: numberedId(id, index),
      surface: 'wall',
      rectangle_mm: { min: [interval[0], z0], max: [interval[1], z1] },
      long_axis: 0
    },
    plane: { axis: 'y', coordinate_mm: y, normal },
    pointAt: point => [point[0], y, point[1]],
    normal: [0, normal, 0]
  }))
}

function makeTopTargets ({
  id,
  faceClass,
  rectangle,
  longAxis,
  z,
  splitAxis,
  accessGrooveKeepouts = [],
  junctionKeepouts = []
}) {
  const keepouts = accessGrooveKeepouts
  const intervals = splitAxis === undefined
    ? [[rectangle.min[longAxis], rectangle.max[longAxis]]]
    : splitIntervalByKeepouts(rectangle.min[splitAxis], rectangle.max[splitAxis], keepouts)
  return intervals.map((interval, index) => {
    const minimum = [...rectangle.min]
    const maximum = [...rectangle.max]
    if (splitAxis !== undefined) {
      minimum[splitAxis] = interval[0]
      maximum[splitAxis] = interval[1]
    }
    return {
      sourceId: id,
      faceClass,
      accessGrooveKeepouts,
      junctionKeepouts,
      region: {
        id: numberedId(id, index),
        surface: 'top',
        rectangle_mm: { min: minimum, max: maximum },
        long_axis: longAxis
      },
      plane: { axis: 'z', coordinate_mm: z, normal: 1 },
      pointAt: point => [point[0], point[1], z],
      normal: [0, 0, 1]
    }
  })
}

function driverSurfaceTargets (def, p, textureConfig) {
  const o = p.organizer
  const l = p.layout
  const floorTop = o.floor_thickness
  const wallBottom = floorTop + textureConfig.grain.wall_bottom_clearance_from_floor_mm
  const wallTop = o.outer_wall_height - textureConfig.grain.wall_top_clearance_mm
  const wallEnd = textureConfig.grain.wall_end_margin_mm
  const topEnd = textureConfig.grain.top_end_margin_mm
  const zoneInnerX = l.screwdriver_zone_width - o.divider_thickness
  const physicalFront = def.bounds[2] === 0
  const physicalBack = def.bounds[3] === o.depth_y

  const floor = makeFloorTargets(
    def,
    driverFloorRectangles(def, p, textureConfig),
    textureConfig,
    floorTop,
    () => 'driver-zone-floor'
  )

  const wallY0 = def.bounds[2] + (physicalFront ? o.outer_wall_thickness : 0) + wallEnd
  const wallY1 = def.bounds[3] - (physicalBack ? o.outer_wall_thickness : 0) - wallEnd
  const innerWall = [
    {
      sourceId: `${def.id}-inner-wall-left`,
      faceClass: 'inner-wall-outer-left',
      region: {
        id: `${def.id}-inner-wall-left`,
        surface: 'wall',
        rectangle_mm: { min: [wallY0, wallBottom], max: [wallY1, wallTop] },
        long_axis: 0
      },
      plane: { axis: 'x', coordinate_mm: o.outer_wall_thickness, normal: 1 },
      pointAt: point => [o.outer_wall_thickness, point[0], point[1]],
      normal: [1, 0, 0]
    },
    {
      sourceId: `${def.id}-inner-wall-divider`,
      faceClass: 'inner-wall-driver-facing-divider',
      region: {
        id: `${def.id}-inner-wall-divider`,
        surface: 'wall',
        rectangle_mm: { min: [wallY0, wallBottom], max: [wallY1, wallTop] },
        long_axis: 0
      },
      plane: { axis: 'x', coordinate_mm: zoneInnerX, normal: -1 },
      pointAt: point => [zoneInnerX, point[0], point[1]],
      normal: [-1, 0, 0]
    }
  ]
  const hardwareJunctionKeepouts = [
    {
      kind: 'junction-blend',
      axis: 0,
      center_mm: def.rowHalf === 'front' ? o.depth_y / l.hardware_rows : 3 * o.depth_y / l.hardware_rows,
      min: (def.rowHalf === 'front' ? o.depth_y / l.hardware_rows : 3 * o.depth_y / l.hardware_rows) - o.junction_vertical_blend_radius,
      max: (def.rowHalf === 'front' ? o.depth_y / l.hardware_rows : 3 * o.depth_y / l.hardware_rows) + o.junction_vertical_blend_radius
    }
  ]
  innerWall.push(...makeXWallTargets({
    id: `${def.id}-inner-wall-hardware-facing-divider`,
    faceClass: 'inner-wall-hardware-facing-divider',
    x: l.screwdriver_zone_width,
    normal: 1,
    y0: wallY0,
    y1: wallY1,
    z0: wallBottom,
    z1: wallTop,
    junctionKeepouts: hardwareJunctionKeepouts
  }))
  if (physicalFront || physicalBack) {
    const faceY = physicalFront ? o.outer_wall_thickness : o.depth_y - o.outer_wall_thickness
    const normalY = physicalFront ? 1 : -1
    innerWall.push({
      sourceId: `${def.id}-inner-wall-${physicalFront ? 'front' : 'back'}`,
      faceClass: `inner-wall-physical-${physicalFront ? 'front' : 'back'}`,
      region: {
        id: `${def.id}-inner-wall-${physicalFront ? 'front' : 'back'}`,
        surface: 'wall',
        rectangle_mm: {
          min: [o.outer_wall_thickness + wallEnd, wallBottom],
          max: [zoneInnerX - wallEnd, wallTop]
        },
        long_axis: 0
      },
      plane: { axis: 'y', coordinate_mm: faceY, normal: normalY },
      pointAt: point => [point[0], faceY, point[1]],
      normal: [0, normalY, 0]
    })
  }

  const leftRimY0 = def.bounds[2] + topEnd + (physicalFront ? o.outer_corner_radius : 0)
  const leftRimY1 = def.bounds[3] - topEnd - (physicalBack ? o.outer_corner_radius : 0)
  const dividerY0 = def.bounds[2] + topEnd
  const dividerY1 = def.bounds[3] - topEnd
  const top = [
    {
      sourceId: `${def.id}-top-left-rim`,
      faceClass: 'top-outer-left-rim',
      region: {
        id: `${def.id}-top-left-rim`,
        surface: 'top',
        rectangle_mm: { min: [0, leftRimY0], max: [o.outer_wall_thickness, leftRimY1] },
        long_axis: 1
      },
      plane: { axis: 'z', coordinate_mm: o.outer_wall_height, normal: 1 },
      pointAt: point => [point[0], point[1], o.outer_wall_height],
      normal: [0, 0, 1]
    },
    {
      sourceId: `${def.id}-top-divider`,
      faceClass: 'top-zone-divider',
      region: {
        id: `${def.id}-top-divider`,
        surface: 'top',
        rectangle_mm: {
          min: [zoneInnerX, dividerY0],
          max: [l.screwdriver_zone_width, dividerY1]
        },
        long_axis: 1
      },
      plane: { axis: 'z', coordinate_mm: o.outer_wall_height, normal: 1 },
      pointAt: point => [point[0], point[1], o.outer_wall_height],
      normal: [0, 0, 1]
    }
  ]
  if (physicalFront || physicalBack) {
    const y0 = physicalFront ? 0 : o.depth_y - o.outer_wall_thickness
    const y1 = physicalFront ? o.outer_wall_thickness : o.depth_y
    top.push({
      sourceId: `${def.id}-top-${physicalFront ? 'front' : 'back'}-rim`,
      faceClass: `top-physical-${physicalFront ? 'front' : 'back'}-rim`,
      region: {
        id: `${def.id}-top-${physicalFront ? 'front' : 'back'}-rim`,
        surface: 'top',
        rectangle_mm: {
          min: [o.outer_corner_radius + topEnd, y0],
          max: [zoneInnerX - topEnd, y1]
        },
        long_axis: 0
      },
      plane: { axis: 'z', coordinate_mm: o.outer_wall_height, normal: 1 },
      pointAt: point => [point[0], point[1], o.outer_wall_height],
      normal: [0, 0, 1]
    })
  }
  return { floor, innerWall, top }
}

function hardwareOwnedRowWalls (def, p) {
  const o = p.organizer
  const l = p.layout
  const rowPitch = o.depth_y / l.hardware_rows
  if (def.rowHalf === 'front') {
    return [
      {
        id: 'row-divider-1',
        junctionY: rowPitch,
        centerY: rowPitch,
        faceA: rowPitch - o.divider_thickness / 2,
        faceB: rowPitch + o.divider_thickness / 2
      },
      {
        id: 'row-divider-2',
        junctionY: l.depth_split,
        centerY: l.depth_split - o.divider_thickness / 2,
        faceA: l.depth_split - o.divider_thickness,
        faceB: l.depth_split
      }
    ]
  }
  return [{
    id: 'row-divider-3',
    junctionY: 3 * rowPitch,
    centerY: 3 * rowPitch,
    faceA: 3 * rowPitch - o.divider_thickness / 2,
    faceB: 3 * rowPitch + o.divider_thickness / 2
  }]
}

function hardwareFloorRectangles (def, p, textureConfig) {
  const o = p.organizer
  const l = p.layout
  const margin = textureConfig.grain.floor_margin_mm
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerX = (l.screwdriver_zone_width + innerRight) / 2
  const xRanges = [
    [l.screwdriver_zone_width + margin, centerX - o.divider_thickness / 2 - margin],
    [centerX + o.divider_thickness / 2 + margin, innerRight - margin]
  ]
  const rowPitch = o.depth_y / l.hardware_rows
  const rows = def.rowHalf === 'front' ? [0, 1] : [2, 3]
  const rectangles = []
  for (const row of rows) {
    let floorY0
    let floorY1
    if (row === 0) floorY0 = o.outer_wall_thickness + margin
    else if (row === 2) floorY0 = l.depth_split + margin
    else floorY0 = row * rowPitch + o.divider_thickness / 2 + margin
    if (row === 1) floorY1 = l.depth_split - o.divider_thickness - margin
    else if (row === 3) floorY1 = o.depth_y - o.outer_wall_thickness - margin
    else floorY1 = (row + 1) * rowPitch - o.divider_thickness / 2 - margin
    for (const [column, [x0, x1]] of xRanges.entries()) {
      rectangles.push({
        sourceId: `compartment-row-${row + 1}-column-${column + 1}`,
        x0,
        x1,
        y0: floorY0,
        y1: floorY1
      })
    }
  }
  const keepout = watermarkKeepout(def, p)
  let patches = rectangles.flatMap(rectangle => (
    subtractRectangleInHorizontalBands(rectangle, keepout)
      .map(patch => ({ ...patch, sourceId: rectangle.sourceId }))
  ))
  if (def.rowHalf === 'back') {
    const connectorRadius = p.connectors.lug_radius + p.connectors.clearance
    const connectorKeepouts = [122, 196].map(x => ({
      x0: x - connectorRadius - margin,
      x1: x + connectorRadius + margin,
      y0: l.depth_split,
      y1: l.depth_split + p.connectors.lug_radius + connectorRadius + margin
    }))
    for (const connectorKeepout of connectorKeepouts) {
      patches = patches.flatMap(rectangle => (
        subtractRectangleInHorizontalBands(rectangle, connectorKeepout)
          .map(patch => ({ ...patch, sourceId: rectangle.sourceId }))
      ))
    }
  }
  return patches
}

function accessGrooveKeepouts (p, margin) {
  const o = p.organizer
  const l = p.layout
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerX = (l.screwdriver_zone_width + innerRight) / 2
  const centers = [
    (l.screwdriver_zone_width + centerX) / 2,
    (centerX + innerRight) / 2
  ]
  const protectedHalfWidth = l.access_groove_width / 2 + margin
  return centers.map(center => ({
    kind: 'access-groove',
    axis: 0,
    center_mm: center,
    groove_half_width_mm: l.access_groove_width / 2,
    extra_margin_mm: margin,
    min: center - protectedHalfWidth,
    max: center + protectedHalfWidth
  }))
}

function hardwareSurfaceTargets (def, p, textureConfig) {
  const o = p.organizer
  const l = p.layout
  const floorTop = o.floor_thickness
  const wallBottom = floorTop + textureConfig.grain.wall_bottom_clearance_from_floor_mm
  const outerWallTop = o.outer_wall_height - textureConfig.grain.wall_top_clearance_mm
  const dividerWallTop = o.divider_height - textureConfig.grain.wall_top_clearance_mm
  const wallEnd = textureConfig.grain.wall_end_margin_mm
  const topEnd = textureConfig.grain.top_end_margin_mm
  const physicalFront = def.bounds[2] === 0
  const physicalBack = def.bounds[3] === o.depth_y
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerX = (l.screwdriver_zone_width + innerRight) / 2
  const topStripHalfWidth = textureConfig.grain.groove_width_mm / 2 + textureConfig.grain.top_centerline_drift_mm
  const ownedWalls = hardwareOwnedRowWalls(def, p)
  const floorRectangles = hardwareFloorRectangles(def, p, textureConfig)
  const floor = makeFloorTargets(
    def,
    floorRectangles,
    textureConfig,
    floorTop,
    rectangle => rectangle.sourceId
  )

  const wallY0 = def.bounds[2] + (physicalFront ? o.outer_wall_thickness : 0) + wallEnd
  const wallY1 = def.bounds[3] - (physicalBack ? o.outer_wall_thickness : 0) - wallEnd
  const outerJunctionKeepouts = ownedWalls.map(wall => ({
    kind: 'junction-blend',
    axis: 0,
    center_mm: wall.junctionY,
    min: wall.junctionY - o.junction_vertical_blend_radius,
    max: wall.junctionY + o.junction_vertical_blend_radius
  }))
  const centerJunctionKeepouts = ownedWalls.map(wall => ({
    kind: 'junction-hub',
    axis: 0,
    center_mm: wall.junctionY,
    min: wall.junctionY - o.junction_cross_hub_radius,
    max: wall.junctionY + o.junction_cross_hub_radius
  }))
  const innerWall = [
    ...makeXWallTargets({
      id: `${def.id}-inner-wall-outer-right`,
      faceClass: 'inner-wall-outer-right',
      x: innerRight,
      normal: -1,
      y0: wallY0,
      y1: wallY1,
      z0: wallBottom,
      z1: outerWallTop,
      junctionKeepouts: outerJunctionKeepouts
    }),
    ...makeXWallTargets({
      id: `${def.id}-inner-wall-center-divider-negative-x-face`,
      faceClass: 'inner-wall-center-divider-negative-x-face',
      x: centerX - o.divider_thickness / 2,
      normal: -1,
      y0: wallY0,
      y1: wallY1,
      z0: wallBottom,
      z1: dividerWallTop,
      junctionKeepouts: centerJunctionKeepouts
    }),
    ...makeXWallTargets({
      id: `${def.id}-inner-wall-center-divider-positive-x-face`,
      faceClass: 'inner-wall-center-divider-positive-x-face',
      x: centerX + o.divider_thickness / 2,
      normal: 1,
      y0: wallY0,
      y1: wallY1,
      z0: wallBottom,
      z1: dividerWallTop,
      junctionKeepouts: centerJunctionKeepouts
    })
  ]
  const wallGrooveKeepouts = accessGrooveKeepouts(p, wallEnd)
  const centerXKeepout = [{
    kind: 'junction-hub',
    axis: 0,
    center_mm: centerX,
    min: centerX - o.junction_cross_hub_radius,
    max: centerX + o.junction_cross_hub_radius
  }]
  for (const wall of ownedWalls) {
    innerWall.push(...makeYWallTargets({
      id: `${def.id}-inner-wall-${wall.id}-negative-y-face`,
      faceClass: 'inner-wall-owned-row-negative-y-face',
      y: wall.faceA,
      normal: -1,
      x0: l.screwdriver_zone_width + wallEnd,
      x1: innerRight - wallEnd,
      z0: wallBottom,
      z1: dividerWallTop,
      accessGrooveKeepouts: wallGrooveKeepouts,
      junctionKeepouts: centerXKeepout
    }))
    innerWall.push(...makeYWallTargets({
      id: `${def.id}-inner-wall-${wall.id}-positive-y-face`,
      faceClass: 'inner-wall-owned-row-positive-y-face',
      y: wall.faceB,
      normal: 1,
      x0: l.screwdriver_zone_width + wallEnd,
      x1: innerRight - wallEnd,
      z0: wallBottom,
      z1: dividerWallTop,
      accessGrooveKeepouts: wallGrooveKeepouts,
      junctionKeepouts: centerXKeepout
    }))
  }
  if (physicalFront || physicalBack) {
    const faceName = physicalFront ? 'front' : 'back'
    const hasAccessGrooves = physicalFront
    innerWall.push(...makeYWallTargets({
      id: `${def.id}-inner-wall-physical-${faceName}`,
      faceClass: `inner-wall-physical-${faceName}`,
      y: physicalFront ? o.outer_wall_thickness : o.depth_y - o.outer_wall_thickness,
      normal: physicalFront ? 1 : -1,
      x0: l.screwdriver_zone_width + wallEnd,
      x1: innerRight - wallEnd,
      z0: wallBottom,
      z1: outerWallTop,
      accessGrooveKeepouts: hasAccessGrooves ? wallGrooveKeepouts : [],
      junctionKeepouts: centerXKeepout
    }))
  }

  const top = [
    ...makeTopTargets({
      id: `${def.id}-top-outer-right-rim`,
      faceClass: 'top-outer-right-rim',
      rectangle: {
        min: [(innerRight + o.width_x) / 2 - topStripHalfWidth, def.bounds[2] + topEnd + (physicalFront ? o.outer_corner_radius : 0)],
        max: [(innerRight + o.width_x) / 2 + topStripHalfWidth, def.bounds[3] - topEnd - (physicalBack ? o.outer_corner_radius : 0)]
      },
      longAxis: 1,
      splitAxis: 1,
      z: o.outer_wall_height,
      junctionKeepouts: outerJunctionKeepouts
    }),
    ...makeTopTargets({
      id: `${def.id}-top-center-divider`,
      faceClass: 'top-center-divider',
      rectangle: {
        min: [centerX - topStripHalfWidth, def.bounds[2] + topEnd],
        max: [centerX + topStripHalfWidth, def.bounds[3] - topEnd]
      },
      longAxis: 1,
      splitAxis: 1,
      z: o.divider_height,
      junctionKeepouts: centerJunctionKeepouts
    })
  ]
  const topGrooveKeepouts = accessGrooveKeepouts(p, topEnd)
  for (const wall of ownedWalls) {
    top.push(...makeTopTargets({
      id: `${def.id}-top-${wall.id}`,
      faceClass: 'top-owned-row-divider',
      rectangle: {
        min: [l.screwdriver_zone_width + topEnd, wall.centerY - topStripHalfWidth],
        max: [innerRight - topEnd, wall.centerY + topStripHalfWidth]
      },
      longAxis: 0,
      splitAxis: 0,
      z: o.divider_height,
      accessGrooveKeepouts: topGrooveKeepouts,
      junctionKeepouts: centerXKeepout
    }))
  }
  if (physicalFront || physicalBack) {
    const faceName = physicalFront ? 'front' : 'back'
    const centerY = physicalFront ? o.outer_wall_thickness / 2 : o.depth_y - o.outer_wall_thickness / 2
    top.push(...makeTopTargets({
      id: `${def.id}-top-physical-${faceName}-rim`,
      faceClass: `top-physical-${faceName}-rim`,
      rectangle: {
        min: [l.screwdriver_zone_width + topEnd, centerY - topStripHalfWidth],
        max: [innerRight - topEnd, centerY + topStripHalfWidth]
      },
      longAxis: 0,
      splitAxis: 0,
      z: o.outer_wall_height,
      accessGrooveKeepouts: physicalFront ? topGrooveKeepouts : [],
      junctionKeepouts: centerXKeepout
    }))
  }
  return { floor, innerWall, top }
}

function targetPlanMetadata (target) {
  return {
    region_id: target.region.id,
    source_id: target.sourceId,
    face_class: target.faceClass,
    plane: target.plane,
    rectangle_mm: target.region.rectangle_mm,
    long_axis: target.region.long_axis ?? (target.region.surface === 'floor' ? 1 : null),
    access_groove_keepouts_mm: target.accessGrooveKeepouts ?? [],
    junction_keepouts_mm: target.junctionKeepouts ?? []
  }
}

function assemblyGlobalFloorSourceRectangle (p, textureConfig) {
  const margin = textureConfig.grain.floor_margin_mm
  const wall = p.organizer.outer_wall_thickness
  return {
    min: [wall + margin, wall + margin],
    max: [
      p.organizer.width_x - wall - margin,
      p.organizer.depth_y - wall - margin
    ]
  }
}

function boundingTargetRectangle (targets) {
  return {
    min: [0, 1].map(axis => Math.min(...targets.map(target => target.region.rectangle_mm.min[axis]))),
    max: [0, 1].map(axis => Math.max(...targets.map(target => target.region.rectangle_mm.max[axis])))
  }
}

function groupedPhysicalSourceTargets (targets) {
  const groups = new Map()
  for (const target of targets) {
    const key = JSON.stringify({
      sourceId: target.sourceId,
      plane: target.plane,
      normal: target.normal,
      longAxis: target.region.long_axis ?? (target.region.surface === 'floor' ? 1 : null)
    })
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(target)
  }
  return [...groups.values()]
}

function planPhysicalSource (p, textureConfig, def, targets) {
  const first = targets[0]
  const isFloor = first.region.surface === 'floor'
  const sourceRegion = {
    id: first.sourceId,
    surface: first.region.surface,
    rectangle_mm: isFloor
      ? assemblyGlobalFloorSourceRectangle(p, textureConfig)
      : boundingTargetRectangle(targets)
  }
  if (first.region.long_axis !== undefined) sourceRegion.long_axis = first.region.long_axis
  if (isFloor) {
    sourceRegion.module = def.id
    sourceRegion.include_knots = textureConfig.knots.placements.some(placement => placement.module === def.id)
  }
  const sourcePlan = planProceduralWoodRegion(textureConfig, sourceRegion)
  const clipRectangles = targets.map(target => ({
    id: target.region.id,
    rectangle_mm: target.region.rectangle_mm
  }))
  return {
    plan: clipProceduralWoodPlan(sourcePlan, clipRectangles),
    integrations: targets.map(target => ({
      target,
      plan: clipProceduralWoodPlan(sourcePlan, [{
        id: target.region.id,
        rectangle_mm: target.region.rectangle_mm
      }])
    }))
  }
}

function makeR2ModuleSurfacePlan (p, textureConfig, moduleId) {
  const def = assertR2ModuleTextureParameters(p, textureConfig, moduleId)
  const targets = def.kind === 'driver'
    ? driverSurfaceTargets(def, p, textureConfig)
    : hardwareSurfaceTargets(def, p, textureConfig)
  const groupDefinitions = [
    { id: 'floor', surface: 'floor', direction: textureConfig.surface_policy.floor_direction, targets: targets.floor },
    { id: 'inner-wall', surface: 'inner-wall', direction: textureConfig.surface_policy.inner_wall_direction, targets: targets.innerWall },
    { id: 'top', surface: 'top', direction: textureConfig.surface_policy.top_direction, targets: targets.top }
  ]
  const integrations = groupDefinitions.map(group => {
    const sources = groupedPhysicalSourceTargets(group.targets).map(sourceTargets => (
      planPhysicalSource(p, textureConfig, def, sourceTargets)
    ))
    return {
      ...group,
      sources,
      entries: sources.flatMap(source => source.integrations)
    }
  })
  return {
    def,
    integrations,
    plan: {
      schema: 'organizer-r2-procedural-wood-module-plan-v1',
      revision: 'R2',
      units: 'mm',
      module: {
        id: def.id,
        kind: def.kind,
        bounds_global_mm: [...def.bounds]
      },
      config_identity: {
        schema: textureConfig.schema,
        representation: textureConfig.representation,
        seed: textureConfig.seed
      },
      policy: {
        operation: 'engrave-only',
        texture_additions: false,
        rounded_cutters: true,
        input_mode: 'parameters-only',
        input_dependencies: [],
        excluded_surface_classes: [
          'external-outer-face',
          'underside-bed-plane',
          'module-split-connector-pass-face',
          'watermark-region',
          'wall-root',
          'junction-blend',
          'access-groove-and-rounded-transition'
        ]
      },
      groups: integrations.map(group => ({
        id: group.id,
        surface: group.surface,
        direction: group.direction,
        face_classes: [...new Set(group.entries.map(entry => entry.target.faceClass))],
        targets: group.entries.map(entry => targetPlanMetadata(entry.target)),
        plans: group.sources.map(source => source.plan)
      }))
    }
  }
}

export function planR2ProceduralWoodModuleSurfaces (p, textureConfig, moduleId) {
  return makeR2ModuleSurfacePlan(p, textureConfig, moduleId).plan
}

export function planR2DriverProceduralWoodSurfaces (p, textureConfig, moduleId) {
  if (!['driver-front', 'driver-back'].includes(moduleId)) {
    throw new Error('R2 DRIVER compatibility planner supports only driver-front or driver-back')
  }
  return planR2ProceduralWoodModuleSurfaces(p, textureConfig, moduleId)
}

export function buildR2ProceduralWoodModuleManifold (p, textureConfig, moduleId, options = {}) {
  const planned = makeR2ModuleSurfacePlan(p, textureConfig, moduleId)
  const segments = options.segments ?? p.export.segments_final
  const tray = globalOuterTray(p)
  const built = buildModule(tray, planned.def, p, null, segments, false)
  tray.delete()
  let shape = built.textured
  for (const group of planned.integrations) {
    for (const entry of group.entries) {
      shape = engravePlan(
        shape,
        entry.plan,
        entry.target.pointAt,
        entry.target.normal,
        textureConfig
      )
    }
  }
  const smoothJunctions = unionOwnedBatched([
    ...driverRootGussetBodies(planned.def, p),
    ...junctionBlendBodies(planned.def, p, segments)
  ])
  if (smoothJunctions) {
    const restored = shape.add(smoothJunctions)
    shape.delete()
    smoothJunctions.delete()
    shape = restored
  }
  return { def: planned.def, solid: shape, plan: planned.plan }
}

export function buildR2DriverProceduralWoodModuleManifold (p, textureConfig, moduleId, options = {}) {
  if (!['driver-front', 'driver-back'].includes(moduleId)) {
    throw new Error('R2 DRIVER compatibility builder supports only driver-front or driver-back')
  }
  return buildR2ProceduralWoodModuleManifold(p, textureConfig, moduleId, options)
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

function makeR2AccessoriesSurfacePlan (p, textureConfig) {
  const c = p.comb
  if (!p.surface_texture?.enabled) throw new Error('R2 accessories require enabled surface_texture parameters')
  if (p.surface_texture.representation !== 'procedural-vector-wood-grooves') {
    throw new Error('R2 accessories require procedural-vector-wood-grooves representation')
  }
  if (p.surface_texture.apply_comb_top_faces !== true) {
    throw new Error('R2 accessories require enabled comb top-face texture')
  }
  if (textureConfig.surface_policy.operation !== 'engrave-only') throw new Error('R2 accessories are engrave-only')
  if (Math.abs(textureConfig.grain.top_depth_mm - 0.20) > EPS) {
    throw new Error('R2 comb top texture requires the approved 0.20 mm depth')
  }
  if (Math.abs(textureConfig.grain.groove_width_mm - 0.90) > EPS) {
    throw new Error('R2 comb top texture requires the approved 0.90 mm groove width')
  }
  if (!Number.isInteger(c.slot_count) || c.slot_count < 2) throw new Error('R2 comb requires at least two slots')

  const grooveHalfWidth = textureConfig.grain.groove_width_mm / 2
  // The configured 0.15 mm top-centerline drift is reused as a documented,
  // positive material clearance between each groove edge and adjacent slot cut.
  const slotEdgeClearance = textureConfig.grain.top_centerline_drift_mm
  if (!(slotEdgeClearance > 0)) throw new Error('R2 comb slot-edge clearance must be positive')
  const centerlineReserve = grooveHalfWidth + slotEdgeClearance
  const endMargin = textureConfig.grain.top_end_margin_mm
  if (c.depth - 2 * endMargin < textureConfig.grain.groove_width_mm - EPS) {
    throw new Error('R2 comb depth cannot hold a top groove after configured end margins')
  }

  const usable = c.width - 2 * c.slot_radius
  const pitch = usable / (c.slot_count - 1)
  const slotCenters = Array.from({ length: c.slot_count }, (_, index) => c.slot_radius + index * pitch)
  const bridgeRegions = []
  const integrations = []
  for (let index = 0; index < slotCenters.length - 1; index += 1) {
    const leftSlotBoundary = slotCenters[index] + c.slot_radius
    const rightSlotBoundary = slotCenters[index + 1] - c.slot_radius
    const materialBridgeWidth = rightSlotBoundary - leftSlotBoundary
    const safeMinimumX = leftSlotBoundary + slotEdgeClearance
    const safeMaximumX = rightSlotBoundary - slotEdgeClearance
    const safeWidth = safeMaximumX - safeMinimumX
    if (safeWidth < textureConfig.grain.groove_width_mm - EPS) continue
    const region = {
      id: `screwdriver-comb-top-bridge-${String(index + 1).padStart(2, '0')}`,
      surface: 'top',
      rectangle_mm: {
        min: [safeMinimumX, endMargin],
        max: [safeMaximumX, c.depth - endMargin]
      },
      long_axis: 1,
      depth_mm: textureConfig.grain.top_depth_mm
    }
    const plan = planProceduralWoodRegion(textureConfig, region)
    if (plan.paths.length !== 1) throw new Error(`${region.id} must contain exactly one +Y grain path`)
    const metadata = {
      id: region.id,
      face_class: 'comb-safe-upward-top-bridge',
      adjacent_slot_numbers: [index + 1, index + 2],
      slot_centers_x_mm: [slotCenters[index], slotCenters[index + 1]],
      slot_boundaries_x_mm: {
        left_slot_right_edge: leftSlotBoundary,
        right_slot_left_edge: rightSlotBoundary
      },
      material_bridge_width_mm: materialBridgeWidth,
      groove_half_width_mm: grooveHalfWidth,
      slot_edge_clearance_mm: slotEdgeClearance,
      centerline_reserve_from_each_slot_boundary_mm: centerlineReserve,
      remaining_safe_width_mm: safeWidth,
      front_back_end_margin_mm: endMargin,
      rectangle_mm: region.rectangle_mm,
      plan
    }
    bridgeRegions.push(metadata)
    integrations.push({ plan, pointAt: point => [point[0], point[1], c.height], normal: [0, 0, 1] })
  }
  if (bridgeRegions.length !== c.slot_count - 1) {
    throw new Error(`R2 comb requires ${c.slot_count - 1} safe top bridge regions; planned ${bridgeRegions.length}`)
  }

  const smoothKeepouts = [
    'comb-slot-bores-and-cut-faces',
    'comb-slot-boundaries-plus-positive-clearance',
    'comb-fit-and-contact-faces',
    'comb-front-back-and-side-outer-faces',
    'comb-underside-and-bed-contact',
    'comb-non-upward-facing-surfaces'
  ]
  const untexturedArtifacts = [
    { id: 'drawer-fit-corner-coupon', texture_plans: [] },
    { id: 'connector-coupon-male', texture_plans: [] },
    { id: 'connector-coupon-female', texture_plans: [] }
  ]
  return {
    integrations,
    plan: {
      schema: 'organizer-r2-procedural-wood-accessories-plan-v1',
      revision: 'R2',
      units: 'mm',
      config_identity: {
        schema: textureConfig.schema,
        representation: textureConfig.representation,
        seed: textureConfig.seed
      },
      policy: {
        operation: 'engrave-only',
        texture_additions: false,
        top_depth_mm: textureConfig.grain.top_depth_mm,
        groove_width_mm: textureConfig.grain.groove_width_mm,
        direction: { mode: 'local-long-axis-positive-y', vector: [0, 1] },
        knots: 'none-on-comb',
        smooth_keepouts: smoothKeepouts,
        excluded_surface_classes: [
          'floor',
          'wall',
          'outer-face',
          'underside-bed-plane',
          'slot-bore-and-cut-face',
          'fit-and-contact-face'
        ]
      },
      comb: {
        body_size_mm: [c.width, c.depth, c.height],
        bed_plane_z_mm: 0,
        connected_body_required: true,
        slot_count: c.slot_count,
        slot_radius_mm: c.slot_radius,
        slot_pitch_mm: pitch,
        slot_centers_x_mm: slotCenters,
        bridge_count: bridgeRegions.length,
        bridge_regions: bridgeRegions,
        smooth_keepouts: smoothKeepouts,
        texture_plans: bridgeRegions.map(bridge => bridge.plan)
      },
      artifacts: [
        { id: 'screwdriver-comb', texture_plans: bridgeRegions.map(bridge => bridge.plan) },
        ...untexturedArtifacts
      ]
    }
  }
}

export function planR2ProceduralWoodAccessories (p, textureConfig) {
  return makeR2AccessoriesSurfacePlan(p, textureConfig).plan
}

export function buildR2AccessoriesManifolds (p, textureConfig, options = {}) {
  const segments = options.segments ?? p.export.segments_final
  const planned = makeR2AccessoriesSurfacePlan(p, textureConfig)
  let comb = buildCombManifold(p, segments)
  for (const integration of planned.integrations) {
    comb = engravePlan(
      comb,
      integration.plan,
      integration.pointAt,
      integration.normal,
      textureConfig
    )
  }
  const connector = buildConnectorCouponManifold(p, segments)
  return {
    plan: planned.plan,
    artifacts: [
      { id: 'screwdriver-comb', solid: comb },
      { id: 'drawer-fit-corner-coupon', solid: buildFitCouponManifold(p) },
      { id: 'connector-coupon-male', solid: connector.male },
      { id: 'connector-coupon-female', solid: connector.female }
    ]
  }
}

export function buildFitCouponManifold (p) {
  return globalOuterTray(p).intersect(box(0, 40, 0, 40, 0, 12))
}

export function buildReliefCouponManifold (p, manifest) {
  const base = box(0, 90, 0, 32, 0, p.organizer.floor_thickness)
  let shape = base
  for (const [index, depth] of [0.2, 0.4, 0.6].entries()) {
    const local = { ...p.relief, emboss_depth: depth, engrave_depth: Math.min(depth, 0.5), tile_scale: 0.75 }
    shape = applyReliefGroup(shape, floorReliefBodies(manifest, { x0: index * 30 + 1, x1: (index + 1) * 30 - 1, y0: 1, y1: 31 }, p.organizer.floor_thickness, local))
  }
  return shape
}

export function buildProceduralWoodCouponManifold (p, textureConfig) {
  const floorTop = p.organizer.floor_thickness
  const wallTop = floorTop + 18
  const wallThickness = p.organizer.base_wall_thickness
  const couponWidth = 122
  const couponDepth = 80
  const rail = { x0: 4, x1: 54, y0: 50, y1: 58 }
  const corner = { x0: 64, x1: 94, y0: 50, y1: 74 }
  let shape = unionOwnedBatched([
    box(0, couponWidth, 0, couponDepth, 0, floorTop),
    box(rail.x0, rail.x1, rail.y0, rail.y1, 0, wallTop),
    box(corner.x0, corner.x1, corner.y0, corner.y0 + wallThickness, 0, wallTop),
    box(corner.x1 - wallThickness, corner.x1, corner.y0, corner.y1, 0, wallTop)
  ])

  const floorSamples = [
    { id: 'horizontal-depth-0.12', depth: 0.12, rectangle: { min: [34, 4], max: [58, 37] } },
    { id: 'horizontal-depth-0.16', depth: 0.16, rectangle: { min: [64, 4], max: [88, 37] } },
    { id: 'horizontal-depth-0.20', depth: 0.20, rectangle: { min: [94, 4], max: [118, 37] } }
  ]
  const plans = []
  for (const sample of floorSamples) {
    const plan = planProceduralWoodRegion(textureConfig, {
      id: sample.id,
      surface: 'floor',
      rectangle_mm: sample.rectangle,
      depth_mm: sample.depth
    })
    plans.push(plan)
    shape = engravePlan(shape, plan, point => [point[0], point[1], floorTop], [0, 0, 1], textureConfig)
  }

  const wallPlan = planProceduralWoodRegion(textureConfig, {
    id: 'vertical-wall-depth-0.16',
    surface: 'wall',
    rectangle_mm: {
      min: [rail.x0 + textureConfig.grain.wall_end_margin_mm, floorTop + textureConfig.grain.wall_bottom_clearance_from_floor_mm],
      max: [rail.x1 - textureConfig.grain.wall_end_margin_mm, wallTop - textureConfig.grain.wall_top_clearance_mm]
    },
    depth_mm: 0.16
  })
  plans.push(wallPlan)
  shape = engravePlan(shape, wallPlan, point => [point[0], rail.y0, point[1]], [0, -1, 0], textureConfig)

  const topPlan = planProceduralWoodRegion(textureConfig, {
    id: 'safe-top-cap-depth-0.20',
    surface: 'top',
    rectangle_mm: {
      min: [rail.x0 + textureConfig.grain.top_end_margin_mm, rail.y0 + 1.5],
      max: [rail.x1 - textureConfig.grain.top_end_margin_mm, rail.y1 - 1.5]
    },
    depth_mm: 0.20
  })
  plans.push(topPlan)
  shape = engravePlan(shape, topPlan, point => [point[0], point[1], wallTop], [0, 0, 1], textureConfig)

  const firstCornerLength = corner.x1 - corner.x0
  const secondCornerLength = corner.y1 - corner.y0 - 2
  const cornerPlan = planProceduralWoodRegion(textureConfig, {
    id: 'corner-phase-transition-depth-0.16',
    surface: 'wall',
    rectangle_mm: {
      min: [0, floorTop + textureConfig.grain.wall_bottom_clearance_from_floor_mm],
      max: [firstCornerLength + secondCornerLength, wallTop - textureConfig.grain.wall_top_clearance_mm]
    },
    long_axis: 0,
    depth_mm: 0.16
  })
  plans.push(cornerPlan)
  const cornerEntries = []
  for (const path of planPaths(cornerPlan)) {
    const [first, second] = splitPathAtAxisValue(path, 0, firstCornerLength)
    if (first) {
      cornerEntries.push({
        path: first,
        pointAt: point => [corner.x0 + point[0], corner.y0, point[1]],
        normal: [0, -1, 0]
      })
    }
    if (second) {
      cornerEntries.push({
        path: second,
        pointAt: point => [corner.x1, corner.y0 + point[0] - firstCornerLength, point[1]],
        normal: [1, 0, 0]
      })
    }
  }
  shape = engraveMappedPaths(shape, cornerEntries, textureConfig)

  return {
    solid: shape,
    plan: {
      schema: 'organizer-procedural-wood-coupon-plan-v1',
      revision: 'R2',
      units: 'mm',
      seed: textureConfig.seed,
      body: {
        size_mm: [couponWidth, couponDepth, wallTop],
        bed_plane_z_mm: 0,
        connected_body_required: true
      },
      policy: {
        operation: 'engrave-only',
        texture_additions: false,
        rounded_cutters: true,
        input_mode: 'parameters-only',
        input_dependencies: []
      },
      samples: [
        { id: 'plain-baseline', surface: 'floor', rectangle_mm: { min: [4, 4], max: [28, 37] }, depth_mm: 0 },
        ...floorSamples.map(sample => ({ id: sample.id, surface: 'floor', rectangle_mm: sample.rectangle, depth_mm: sample.depth })),
        { id: wallPlan.region.id, surface: 'wall', depth_mm: wallPlan.groove.depth_mm },
        { id: cornerPlan.region.id, surface: 'wall-corner-90-degree', depth_mm: cornerPlan.groove.depth_mm },
        { id: topPlan.region.id, surface: 'top', depth_mm: topPlan.groove.depth_mm }
      ],
      plans
    }
  }
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
