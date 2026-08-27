import { CrossSection, Manifold } from 'manifold-3d/manifoldCAD'

const EPS = 1.0e-6

function box (x0, x1, y0, y1, z0, z1) {
  const size = [x1 - x0, y1 - y0, z1 - z0]
  if (size.some(value => value <= EPS)) return null
  return Manifold.cube(size).translate([x0, y0, z0])
}

function cylinderZ (cx, cy, radius, z0, z1, segments) {
  return Manifold.cylinder(z1 - z0, radius, radius, segments).translate([cx, cy, z0])
}

function cylinderY (cx, cy, cz, radius, length, segments) {
  return Manifold.cylinder(length, radius, radius, segments, true)
    .rotate([90, 0, 0])
    .translate([cx, cy, cz])
}

function unionMany (items) {
  const filtered = items.filter(Boolean)
  if (filtered.length === 0) return null
  if (filtered.length === 1) return filtered[0]
  return Manifold.union(filtered)
}

function roundedRectPrism (width, depth, radius, height, segments) {
  if (radius <= EPS) return box(0, width, 0, depth, 0, height)
  const r = Math.min(radius, width / 2 - EPS, depth / 2 - EPS)
  return unionMany([
    box(r, width - r, 0, depth, 0, height),
    box(0, width, r, depth - r, 0, height),
    cylinderZ(r, r, r, 0, height, segments),
    cylinderZ(width - r, r, r, 0, height, segments),
    cylinderZ(r, depth - r, r, 0, height, segments),
    cylinderZ(width - r, depth - r, r, 0, height, segments)
  ])
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

export function resolveParameters (raw) {
  const p = structuredClone(raw)
  const o = p.organizer
  const l = p.layout
  const s = p.segmentation
  p.derived = {
    module_width: o.width_x / s.columns,
    module_depth: o.depth_y / s.rows,
    hardware_field_width: o.width_x - l.tool_lane_width,
    hardware_column_pitch: (o.width_x - l.tool_lane_width) / l.hardware_columns,
    hardware_row_pitch: o.depth_y / l.hardware_rows,
    tool_lane_inner_width: l.tool_lane_width - 1.5 * o.wall_thickness
  }
  p.comb.width = p.derived.tool_lane_inner_width - 2 * p.comb.side_clearance_each
  return p
}

export function assertParameters (p) {
  const o = p.organizer
  const l = p.layout
  const s = p.segmentation
  const c = p.connectors
  const d = p.derived
  if (s.columns !== 3 || s.rows !== 3 || s.module_count !== 9) throw new Error('revision 0.1.0 requires exactly nine modules in a 3 x 3 grid')
  if (l.hardware_columns * l.hardware_rows !== 18 || l.hardware_compartments !== 18) throw new Error('revision 0.1.0 requires exactly eighteen hardware compartments')
  if (Math.abs(l.tool_lane_width - d.module_width) > 1.0e-4) throw new Error('tool-lane boundary must coincide with the first manufacturing seam')
  if (d.module_width + 2 * (c.neck_length + c.lug_radius) > s.usable_bed_x + EPS) throw new Error('connector-bearing module exceeds usable bed width')
  if (d.module_depth + 2 * (c.neck_length + c.lug_radius) > s.usable_bed_y + EPS) throw new Error('connector-bearing module exceeds usable bed depth')
  if (o.floor_thickness < 2.0 || o.wall_thickness < 2.4) throw new Error('unqualified thin floor or wall')
  if (l.access_groove_width <= 2 * l.access_groove_bottom_radius) throw new Error('access groove is too narrow for its bottom radii')
  if (c.position_fraction_on_segment <= 0.1 || c.position_fraction_on_segment >= 0.4) throw new Error('connector position fraction leaves the qualified keep-out range')
}

function outerTray (p, segments) {
  const o = p.organizer
  const outer = roundedRectPrism(o.width_x, o.depth_y, o.outer_corner_radius, o.outer_wall_height, segments)
  const innerRadius = Math.max(0.2, o.outer_corner_radius - o.wall_thickness)
  const inner = roundedRectPrism(
    o.width_x - 2 * o.wall_thickness,
    o.depth_y - 2 * o.wall_thickness,
    innerRadius,
    o.outer_wall_height - o.floor_thickness + 1,
    segments
  ).translate([o.wall_thickness, o.wall_thickness, o.floor_thickness])
  return outer.subtract(inner)
}

function roundedAccessGroove (cx, cy, wallThickness, wallTop, p, segments) {
  const l = p.layout
  const radius = Math.min(l.access_groove_bottom_radius, l.access_groove_width / 2, l.access_groove_depth)
  const x0 = cx - l.access_groove_width / 2
  const x1 = cx + l.access_groove_width / 2
  const z0 = wallTop - l.access_groove_depth
  const z1 = wallTop + 2
  const yLength = wallThickness + 4
  return unionMany([
    box(x0 + radius, x1 - radius, cy - yLength / 2, cy + yLength / 2, z0, z1),
    box(x0, x1, cy - yLength / 2, cy + yLength / 2, z0 + radius, z1),
    cylinderY(x0 + radius, cy, z0 + radius, radius, yLength, segments),
    cylinderY(x1 - radius, cy, z0 + radius, radius, yLength, segments)
  ])
}

function functionalWalls (p) {
  const o = p.organizer
  const l = p.layout
  const d = p.derived
  const t = o.wall_thickness
  const walls = []
  walls.push(box(l.tool_lane_width - t / 2, l.tool_lane_width + t / 2, 0, o.depth_y, 0, o.divider_height))
  for (let column = 1; column < l.hardware_columns; column += 1) {
    const x = l.tool_lane_width + column * d.hardware_column_pitch
    walls.push(box(x - t / 2, x + t / 2, 0, o.depth_y, 0, o.divider_height))
  }
  for (let row = 1; row < l.hardware_rows; row += 1) {
    const y = row * d.hardware_row_pitch
    walls.push(box(l.tool_lane_width - t / 2, o.width_x, y - t / 2, y + t / 2, 0, o.divider_height))
  }

  // Low root gussets preserve R1.6's reinforced wall language without filling bin corners.
  const g = 3.5
  const gh = 8.0
  const verticals = [l.tool_lane_width, l.tool_lane_width + d.hardware_column_pitch, l.tool_lane_width + 2 * d.hardware_column_pitch]
  for (let row = 1; row < l.hardware_rows; row += 1) {
    const y = row * d.hardware_row_pitch
    for (const x of verticals) {
      walls.push(trianglePrism([[x + t / 2 - 0.2, y + t / 2 - 0.2], [x + t / 2 + g, y + t / 2 - 0.2], [x + t / 2 - 0.2, y + t / 2 + g]], gh))
    }
  }
  return unionMany(walls)
}

function accessGrooves (p, segments) {
  const o = p.organizer
  const l = p.layout
  const d = p.derived
  const centers = []
  for (let column = 0; column < l.hardware_columns; column += 1) {
    centers.push(l.tool_lane_width + (column + 0.5) * d.hardware_column_pitch)
  }
  const cutters = []
  for (const x of centers) cutters.push(roundedAccessGroove(x, o.wall_thickness / 2, o.wall_thickness, o.outer_wall_height, p, segments))
  for (let row = 1; row < l.hardware_rows; row += 1) {
    const y = row * d.hardware_row_pitch
    for (const x of centers) cutters.push(roundedAccessGroove(x, y, o.wall_thickness, o.divider_height, p, segments))
  }
  return unionMany(cutters)
}

export function buildAssembledOrganizer (p, segments = p.export.segments) {
  assertParameters(p)
  const shell = outerTray(p, segments)
  const walls = functionalWalls(p)
  const grooves = accessGrooves(p, segments)
  return shell.add(walls).subtract(grooves)
}

function xMaleConnector (edgeX, cy, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  const center = edgeX + c.neck_length
  return unionMany([
    cylinderZ(center, cy, c.lug_radius, 0, h, segments),
    box(edgeX - 0.6, center, cy - c.neck_width / 2, cy + c.neck_width / 2, 0, h)
  ])
}

function xFemaleConnector (edgeX, cy, p, segments, clearance = p.connectors.draft_clearance_per_side) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  const center = edgeX + c.neck_length
  return unionMany([
    cylinderZ(center, cy, c.lug_radius + clearance, -0.3, h + 0.3, segments),
    box(edgeX - 0.3, center, cy - c.neck_width / 2 - clearance, cy + c.neck_width / 2 + clearance, -0.3, h + 0.3)
  ])
}

function yMaleConnector (edgeY, cx, p, segments) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  const center = edgeY + c.neck_length
  return unionMany([
    cylinderZ(cx, center, c.lug_radius, 0, h, segments),
    box(cx - c.neck_width / 2, cx + c.neck_width / 2, edgeY - 0.6, center, 0, h)
  ])
}

function yFemaleConnector (edgeY, cx, p, segments, clearance = p.connectors.draft_clearance_per_side) {
  const c = p.connectors
  const h = p.organizer.floor_thickness
  const center = edgeY + c.neck_length
  return unionMany([
    cylinderZ(cx, center, c.lug_radius + clearance, -0.3, h + 0.3, segments),
    box(cx - c.neck_width / 2 - clearance, cx + c.neck_width / 2 + clearance, edgeY - 0.3, center, -0.3, h + 0.3)
  ])
}

export function moduleDefinitions (p) {
  const definitions = []
  for (let row = 0; row < p.segmentation.rows; row += 1) {
    for (let column = 0; column < p.segmentation.columns; column += 1) {
      const x0 = p.organizer.width_x * column / p.segmentation.columns
      const x1 = p.organizer.width_x * (column + 1) / p.segmentation.columns
      const y0 = p.organizer.depth_y * row / p.segmentation.rows
      const y1 = p.organizer.depth_y * (row + 1) / p.segmentation.rows
      definitions.push({
        id: `module-r${row + 1}-c${column + 1}`,
        row,
        column,
        bounds: [x0, x1, y0, y1]
      })
    }
  }
  return definitions
}

export function buildModules (p, segments = p.export.segments) {
  const assembled = buildAssembledOrganizer(p, segments)
  const fraction = p.connectors.position_fraction_on_segment
  const modules = moduleDefinitions(p).map(def => {
    const [x0, x1, y0, y1] = def.bounds
    const clip = box(x0, x1, y0, y1, 0, p.organizer.outer_wall_height)
    let solid = assembled.intersect(clip)
    const connectorY = y0 + fraction * (y1 - y0)
    const connectorX = x0 + fraction * (x1 - x0)
    if (def.column < p.segmentation.columns - 1) solid = solid.add(xMaleConnector(x1, connectorY, p, segments))
    if (def.column > 0) solid = solid.subtract(xFemaleConnector(x0, connectorY, p, segments))
    if (def.row < p.segmentation.rows - 1) solid = solid.add(yMaleConnector(y1, connectorX, p, segments))
    if (def.row > 0) solid = solid.subtract(yFemaleConnector(y0, connectorX, p, segments))
    return { def, solid }
  })
  return modules
}

export function buildComb (p, segments = p.export.segments) {
  const c = p.comb
  let solid = box(0, c.width, 0, c.depth, 0, c.height)
  const pitch = (c.width - 2 * c.end_margin) / (c.slot_count - 1)
  const cutters = []
  for (let index = 0; index < c.slot_count; index += 1) {
    const x = c.end_margin + index * pitch
    cutters.push(cylinderY(x, c.depth / 2, c.height, c.slot_radius, c.depth + 2, segments))
    cutters.push(box(x - c.slot_radius, x + c.slot_radius, -1, c.depth + 1, c.height, c.height + c.slot_radius + 1))
  }
  solid = solid.subtract(unionMany(cutters))
  return solid
}

export function buildCombInterfaceCoupon (p) {
  const width = p.comb.width
  return unionMany([
    box(0, 12, 0, 8, 0, 6),
    box(width - 12, width, 0, 8, 0, 6),
    box(10, width - 10, 3, 5, 0, 2)
  ])
}

export function buildFitCornerCoupon (p, segments = p.export.segments) {
  const tray = outerTray(p, segments)
  return tray.intersect(box(0, 42, 0, 42, 0, 12))
}

export function buildConnectorCouponMale (p, segments = p.export.segments) {
  const h = p.organizer.floor_thickness
  return box(0, 22, 0, 20, 0, h).add(xMaleConnector(22, 10, p, segments))
}

export function buildConnectorCouponFemale (p, clearance, segments = p.export.segments) {
  const h = p.organizer.floor_thickness
  return box(0, 24, 0, 20, 0, h).subtract(xFemaleConnector(0, 10, p, segments, clearance))
}
