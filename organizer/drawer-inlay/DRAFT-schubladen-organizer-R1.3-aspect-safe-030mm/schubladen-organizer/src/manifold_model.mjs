import { CrossSection, Manifold, Mesh } from 'manifold-3d/manifoldCAD'

import { watermarkCutter } from './watermark.mjs'

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
  const margin = p.relief.watermark_keepout ?? 0
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
  const margin = l.floor_relief_margin
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
  const functional = unionMany(functionalWallsAndGussets(def, p))
  if (functional) shape = shape.add(functional)
  const connectors = connectorBodies(def, p, segments)
  const connectorAdds = unionMany(connectors.additions)
  const connectorCuts = unionMany(connectors.cutters)
  if (connectorAdds) shape = shape.add(connectorAdds)
  if (connectorCuts) shape = shape.subtract(connectorCuts)
  const grooves = unionMany(accessGrooveCutters(def, p, segments))
  if (grooves) shape = shape.subtract(grooves)
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
  const junctions = unionMany(junctionBlendBodies(def, p, segments))
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

export function buildReliefCouponManifold (p, manifest) {
  const base = box(0, 90, 0, 32, 0, p.organizer.floor_thickness)
  let shape = base
  for (const [index, depth] of [0.2, 0.4, 0.6].entries()) {
    const local = { ...p.relief, emboss_depth: depth, engrave_depth: Math.min(depth, 0.5), tile_scale: 0.75 }
    shape = applyReliefGroup(shape, floorReliefBodies(manifest, { x0: index * 30 + 1, x1: (index + 1) * 30 - 1, y0: 1, y1: 31 }, p.organizer.floor_thickness, local))
  }
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
