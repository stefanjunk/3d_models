import modeling from '@jscad/modeling'

const { booleans, extrusions, primitives, transforms } = modeling

import {
  applyReliefBodies,
  boxFromBounds,
  floorReliefBodies,
  mergeReliefBodies,
  wallXReliefBodies,
  wallYReliefBodies
} from './relief.mjs'

const { subtract, intersect, union } = booleans
const { extrudeLinear } = extrusions
const { cuboid, cylinder, polygon, roundedCuboid } = primitives
const { rotateX, rotateY, translate } = transforms

function assertParameters (p) {
  const d = p.drawer
  const o = p.organizer
  const l = p.layout
  if (o.width_x > d.inside_width_x || o.depth_y > d.inside_depth_y) throw new Error('Organizer exceeds drawer XY envelope')
  if (o.max_height_z > d.inside_height_z) throw new Error('Organizer exceeds drawer height')
  if (o.floor_thickness < 2.0) throw new Error('Floor thickness below approved 2.0 mm reserve')
  if (o.outer_wall_thickness < 2.4 || o.divider_thickness < 2.0) throw new Error('Wall thickness below approved minimum')
  if (l.screwdriver_zone_width <= 40 || l.screwdriver_zone_width >= o.width_x - 50) throw new Error('Invalid screwdriver zone width')
  if (Math.abs(l.depth_split * 2 - o.depth_y) > 0.01) throw new Error('Depth split must bisect the organizer')
  if (l.hardware_columns !== 2 || l.hardware_rows !== 4) throw new Error('R0 requires exactly 2 x 4 hardware compartments')
}

function globalOuterTray (p, segments) {
  const o = p.organizer
  const outer = roundedCuboid({
    size: [o.width_x, o.depth_y, o.outer_wall_height],
    center: [o.width_x / 2, o.depth_y / 2, o.outer_wall_height / 2],
    roundRadius: o.outer_corner_radius,
    segments
  })
  const innerRadius = Math.max(0.2, o.outer_corner_radius - o.outer_wall_thickness)
  const voidHeight = o.outer_wall_height + 2
  const innerVoid = roundedCuboid({
    size: [
      o.width_x - 2 * o.outer_wall_thickness,
      o.depth_y - 2 * o.outer_wall_thickness,
      voidHeight
    ],
    center: [
      o.width_x / 2,
      o.depth_y / 2,
      o.floor_thickness + voidHeight / 2
    ],
    roundRadius: innerRadius,
    segments
  })
  return subtract(outer, innerVoid)
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
  const cutter = boxFromBounds(x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.01, -0.01, p.organizer.outer_wall_height + 0.01)
  return intersect(tray, cutter)
}

function trapezoidGusset (points, height) {
  let area2 = 0
  for (let i = 0; i < points.length; i += 1) {
    const a = points[i]
    const b = points[(i + 1) % points.length]
    area2 += a[0] * b[1] - b[0] * a[1]
  }
  const ordered = area2 < 0 ? [...points].reverse() : points
  return extrudeLinear({ height }, polygon({ points: ordered }))
}

function functionalWallsAndGussets (def, p) {
  const o = p.organizer
  const l = p.layout
  const dt = o.divider_thickness
  const zone = l.screwdriver_zone_width
  const parts = []
  const gussets = []
  if (def.kind === 'driver') {
    parts.push(boxFromBounds(zone - dt, zone, def.bounds[2], def.bounds[3], 0, o.outer_wall_height))
    const localMarkers = [89.25, 178.5, 267.75].filter(y => y > def.bounds[2] + 5 && y < def.bounds[3] - 5)
    for (const y of localMarkers) {
      gussets.push(trapezoidGusset([[o.outer_wall_thickness, y - 4], [o.outer_wall_thickness + 4, y], [o.outer_wall_thickness, y + 4]], o.root_gusset_height))
      gussets.push(trapezoidGusset([[zone - dt, y - 4], [zone - dt - 4, y], [zone - dt, y + 4]], o.root_gusset_height))
    }
  } else {
    const hwLeft = zone
    const hwRight = o.width_x - o.outer_wall_thickness
    const centerX = (hwLeft + hwRight) / 2
    parts.push(boxFromBounds(centerX - dt / 2, centerX + dt / 2, def.bounds[2], def.bounds[3], 0, o.divider_height))
    const rowPitch = o.depth_y / l.hardware_rows
    const ownedWalls = def.rowHalf === 'front'
      ? [rowPitch, l.depth_split]
      : [3 * rowPitch]
    for (const y of ownedWalls) {
      const y0 = Math.abs(y - l.depth_split) < 0.01 ? y - dt : y - dt / 2
      const y1 = Math.abs(y - l.depth_split) < 0.01 ? y : y + dt / 2
      parts.push(boxFromBounds(zone, o.width_x, y0, y1, 0, o.divider_height))
      const g = o.root_gusset_size
      gussets.push(trapezoidGusset([[centerX - dt / 2, y0], [centerX - dt / 2 - g, y0], [centerX - dt / 2, y0 - g]], o.root_gusset_height))
      gussets.push(trapezoidGusset([[centerX + dt / 2, y0], [centerX + dt / 2 + g, y0], [centerX + dt / 2, y0 - g]], o.root_gusset_height))
    }
  }
  return [...parts, ...gussets.filter(Boolean)]
}

function circleLug (cx, cy, radius, height, segments) {
  return cylinder({ radius, height, center: [cx, cy, height / 2], segments })
}

function xMaleConnector (edgeX, cy, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  const disk = circleLug(edgeX + c.lug_radius, cy, c.lug_radius, h, segments)
  const neck = boxFromBounds(edgeX - 0.6, edgeX + c.lug_radius, cy - c.neck_width / 2, cy + c.neck_width / 2, 0, h)
  return union(disk, neck)
}

function xFemaleConnector (edgeX, cy, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness + 0.4
  const disk = translate([0, 0, -0.2], circleLug(edgeX + c.lug_radius, cy, c.lug_radius + c.clearance, h, segments))
  const neck = boxFromBounds(edgeX - 0.2, edgeX + c.lug_radius, cy - c.neck_width / 2 - c.clearance, cy + c.neck_width / 2 + c.clearance, -0.2, h)
  return union(disk, neck)
}

function yMaleConnector (edgeY, cx, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  const disk = circleLug(cx, edgeY + c.lug_radius, c.lug_radius, h, segments)
  const neck = boxFromBounds(cx - c.neck_width / 2, cx + c.neck_width / 2, edgeY - 0.6, edgeY + c.lug_radius, 0, h)
  return union(disk, neck)
}

function yFemaleConnector (edgeY, cx, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness + 0.4
  const disk = translate([0, 0, -0.2], circleLug(cx, edgeY + c.lug_radius, c.lug_radius + c.clearance, h, segments))
  const neck = boxFromBounds(cx - c.neck_width / 2 - c.clearance, cx + c.neck_width / 2 + c.clearance, edgeY - 0.2, edgeY + c.lug_radius, -0.2, h)
  return union(disk, neck)
}

function connectorBodies (def, p, segments) {
  const zone = p.layout.screwdriver_zone_width
  const split = p.layout.depth_split
  const additions = []
  const cutters = []
  if (def.kind === 'driver') {
    const yPositions = def.rowHalf === 'front' ? [45, 133] : [223, 312]
    for (const y of yPositions) additions.push(xMaleConnector(zone, y, p, segments))
  } else {
    const yPositions = def.rowHalf === 'front' ? [45, 133] : [223, 312]
    for (const y of yPositions) cutters.push(xFemaleConnector(zone, y, p, segments))
  }
  const xPositions = def.kind === 'driver' ? [30, 65] : [122, 196]
  if (def.rowHalf === 'front') {
    for (const x of xPositions) additions.push(yMaleConnector(split, x, p, segments))
  } else {
    for (const x of xPositions) cutters.push(yFemaleConnector(split, x, p, segments))
  }
  return { additions, cutters }
}

function fingerScoopCutters (def, p, segments) {
  if (def.kind !== 'hardware') return []
  const o = p.organizer
  const l = p.layout
  const zone = l.screwdriver_zone_width
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerWallX = (zone + innerRight) / 2
  const centers = [(zone + centerWallX) / 2, (centerWallX + innerRight) / 2]
  const rowPitch = o.depth_y / l.hardware_rows
  const yValues = def.rowHalf === 'front'
    ? [o.outer_wall_thickness / 2, rowPitch, l.depth_split]
    : [3 * rowPitch]
  const cutters = []
  for (const y of yValues) {
    for (const x of centers) {
      let tool = cylinder({ radius: l.finger_scoop_radius, height: o.divider_thickness + 4, segments })
      tool = rotateY(Math.PI / 2, tool)
      tool = translate([x, y, o.divider_height], tool)
      cutters.push(tool)
    }
  }
  return cutters
}

function floorRectsForModule (def, p) {
  const o = p.organizer
  const l = p.layout
  const margin = l.floor_relief_margin
  if (def.kind === 'driver') {
    return [{
      x0: o.outer_wall_thickness + margin,
      x1: l.screwdriver_zone_width - o.divider_thickness - margin,
      y0: def.bounds[2] + (def.bounds[2] === 0 ? o.outer_wall_thickness + margin : margin),
      y1: def.bounds[3] - (def.bounds[3] === o.depth_y ? o.outer_wall_thickness + margin : margin)
    }]
  }
  const innerRight = o.width_x - o.outer_wall_thickness
  const centerWallX = (l.screwdriver_zone_width + innerRight) / 2
  const xRanges = [
    [l.screwdriver_zone_width + margin, centerWallX - o.divider_thickness / 2 - margin],
    [centerWallX + o.divider_thickness / 2 + margin, innerRight - margin]
  ]
  const rowPitch = o.depth_y / l.hardware_rows
  const rowIndices = def.rowHalf === 'front' ? [0, 1] : [2, 3]
  const rects = []
  for (const row of rowIndices) {
    const rawY0 = row * rowPitch
    const rawY1 = (row + 1) * rowPitch
    for (const [x0, x1] of xRanges) {
      rects.push({
        x0,
        x1,
        y0: rawY0 + (row === 0 ? o.outer_wall_thickness : o.divider_thickness) + margin,
        y1: rawY1 - o.divider_thickness - margin
      })
    }
  }
  return rects
}

function wallReliefGroups (def, p, manifest) {
  const o = p.organizer
  const l = p.layout
  const r = p.relief
  const wallRelief = { ...r, engrave_depth: Math.min(r.engrave_depth, 0.18) }
  const z0 = r.wall_band_bottom
  const z1 = Math.min(r.wall_band_top, o.outer_wall_height - 3)
  const groups = []
  const y0 = def.bounds[2] + 4
  const y1 = def.bounds[3] - 4
  const recessedOuterX = (x, normal, targetY0, targetY1) => {
    const shiftedX = x - normal * r.emboss_depth
    const panelX0 = Math.min(x, shiftedX) - (normal < 0 ? r.boolean_overlap : 0)
    const panelX1 = Math.max(x, shiftedX) + (normal > 0 ? r.boolean_overlap : 0)
    const panelCutter = boxFromBounds(panelX0, panelX1, targetY0, targetY1, z0, z1)
    return mergeReliefBodies(
      { additions: [], cutters: [panelCutter] },
      wallXReliefBodies(manifest, { x: shiftedX, normal, y0: targetY0, y1: targetY1, z0, z1 }, wallRelief)
    )
  }
  const recessedOuterY = (y, normal, targetX0, targetX1) => {
    const shiftedY = y - normal * r.emboss_depth
    const panelY0 = Math.min(y, shiftedY) - (normal < 0 ? r.boolean_overlap : 0)
    const panelY1 = Math.max(y, shiftedY) + (normal > 0 ? r.boolean_overlap : 0)
    const panelCutter = boxFromBounds(targetX0, targetX1, panelY0, panelY1, z0, z1)
    return mergeReliefBodies(
      { additions: [], cutters: [panelCutter] },
      wallYReliefBodies(manifest, { y: shiftedY, normal, x0: targetX0, x1: targetX1, z0, z1 }, wallRelief)
    )
  }
  if (r.apply_outer_walls) {
    if (def.kind === 'driver') groups.push(recessedOuterX(0, -1, y0, y1))
    if (def.kind === 'hardware') groups.push(recessedOuterX(o.width_x, 1, y0, y1))
    if (def.bounds[2] === 0) groups.push(recessedOuterY(0, -1, def.bounds[0] + 4, def.bounds[1] - 4))
    if (def.bounds[3] === o.depth_y) groups.push(recessedOuterY(o.depth_y, 1, def.bounds[0] + 4, def.bounds[1] - 4))
  }
  if (r.apply_inner_walls) {
    if (def.kind === 'driver') {
      groups.push(wallXReliefBodies(manifest, { x: o.outer_wall_thickness, normal: 1, y0, y1, z0, z1 }, wallRelief))
      groups.push(wallXReliefBodies(manifest, { x: l.screwdriver_zone_width - o.divider_thickness, normal: -1, y0, y1, z0, z1 }, wallRelief))
      groups.push(wallXReliefBodies(manifest, { x: l.screwdriver_zone_width, normal: 1, y0, y1, z0, z1 }, wallRelief))
    } else {
      const innerRight = o.width_x - o.outer_wall_thickness
      const centerX = (l.screwdriver_zone_width + innerRight) / 2
      groups.push(wallXReliefBodies(manifest, { x: innerRight, normal: -1, y0, y1, z0, z1 }, wallRelief))
      groups.push(wallXReliefBodies(manifest, { x: centerX - o.divider_thickness / 2, normal: -1, y0, y1, z0, z1: Math.min(z1, o.divider_height - 3) }, wallRelief))
      groups.push(wallXReliefBodies(manifest, { x: centerX + o.divider_thickness / 2, normal: 1, y0, y1, z0, z1: Math.min(z1, o.divider_height - 3) }, wallRelief))
      const rowPitch = o.depth_y / l.hardware_rows
      const walls = def.rowHalf === 'front' ? [rowPitch, l.depth_split] : [3 * rowPitch]
      for (const y of walls) {
        groups.push(wallYReliefBodies(manifest, { y: y - o.divider_thickness / 2, normal: -1, x0: l.screwdriver_zone_width + 4, x1: o.width_x - 4, z0, z1: Math.min(z1, o.divider_height - 3) }, wallRelief))
        groups.push(wallYReliefBodies(manifest, { y, normal: 1, x0: l.screwdriver_zone_width + 4, x1: o.width_x - 4, z0, z1: Math.min(z1, o.divider_height - 3) }, wallRelief))
      }
    }
    if (def.bounds[2] === 0) groups.push(wallYReliefBodies(manifest, { y: o.outer_wall_thickness, normal: 1, x0: def.bounds[0] + 4, x1: def.bounds[1] - 4, z0, z1 }, wallRelief))
    if (def.bounds[3] === o.depth_y) groups.push(wallYReliefBodies(manifest, { y: o.depth_y - o.outer_wall_thickness, normal: -1, x0: def.bounds[0] + 4, x1: def.bounds[1] - 4, z0, z1 }, wallRelief))
  }
  return groups
}

function buildModule (tray, def, p, manifest, segments, withRelief) {
  let shape = clipTrayToModule(tray, def, p)
  shape = union(shape, ...functionalWallsAndGussets(def, p))
  const connectors = connectorBodies(def, p, segments)
  if (connectors.additions.length) shape = union(shape, ...connectors.additions)
  const cutters = [...connectors.cutters, ...fingerScoopCutters(def, p, segments)]
  if (cutters.length) shape = subtract(shape, ...cutters)
  const smooth = shape
  if (withRelief && p.relief.enabled) {
    const groups = []
    if (p.relief.apply_floor) {
      for (const rect of floorRectsForModule(def, p)) {
        groups.push(floorReliefBodies(manifest, rect, p.organizer.floor_thickness, p.relief))
      }
    }
    groups.push(...wallReliefGroups(def, p, manifest))
    shape = applyReliefBodies(shape, mergeReliefBodies(...groups))
  }
  shape.name = def.id
  smooth.name = `${def.id}-smooth`
  return { def, smooth, textured: shape }
}

export function buildModules (p, manifest, options = {}) {
  assertParameters(p)
  const segments = options.segments ?? p.export.segments_final
  const withRelief = options.withRelief ?? true
  const tray = globalOuterTray(p, segments)
  return moduleDefinitions(p).map(def => buildModule(tray, def, p, manifest, segments, withRelief))
}

export function buildComb (p, segments) {
  const c = p.comb
  let shape = boxFromBounds(0, c.width, 0, c.depth, 0, c.height)
  const usable = c.width - 2 * c.slot_radius
  const pitch = usable / (c.slot_count - 1)
  const cutters = []
  for (let i = 0; i < c.slot_count; i += 1) {
    const x = c.slot_radius + i * pitch
    let tool = cylinder({ radius: c.slot_radius, height: c.depth + 2, segments })
    tool = rotateX(Math.PI / 2, tool)
    tool = translate([x, c.depth / 2, c.height], tool)
    cutters.push(tool)
    cutters.push(boxFromBounds(x - c.slot_radius, x + c.slot_radius, -1, c.depth + 1, c.height, c.height + c.slot_radius + 1))
  }
  shape = subtract(shape, ...cutters)
  shape.name = 'screwdriver-comb'
  return shape
}

export function buildFitCoupon (p, segments) {
  const tray = globalOuterTray(p, segments)
  const clip = boxFromBounds(-0.01, 40, -0.01, 40, -0.01, 12)
  const shape = intersect(tray, clip)
  shape.name = 'drawer-fit-corner-coupon'
  return shape
}

export function buildReliefCoupon (p, manifest) {
  const base = boxFromBounds(0, 90, 0, 32, 0, p.organizer.floor_thickness)
  const groups = []
  const depths = [0.2, 0.4, 0.6]
  for (let i = 0; i < depths.length; i += 1) {
    const localRelief = {
      ...p.relief,
      emboss_depth: depths[i],
      engrave_depth: Math.min(depths[i], 0.5),
      tile_scale: 0.75
    }
    groups.push(floorReliefBodies(manifest, { x0: i * 30 + 1, x1: (i + 1) * 30 - 1, y0: 1, y1: 31 }, p.organizer.floor_thickness, localRelief))
  }
  const shape = applyReliefBodies(base, mergeReliefBodies(...groups))
  shape.name = 'relief-depth-coupon'
  return shape
}
