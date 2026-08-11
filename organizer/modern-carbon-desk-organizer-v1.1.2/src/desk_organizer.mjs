import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'
import Module from 'manifold-3d'

const wasm = await Module()
wasm.setup()
const { CrossSection, Manifold, Mesh } = wasm

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const OUT = path.join(ROOT, 'output')
const STL = path.join(OUT, 'stl')
const BASE = path.join(OUT, 'base')
const CUTTERS = path.join(OUT, 'cutters')
const ASSEMBLY = path.join(OUT, 'assembly')
const PARAMS = JSON.parse(fs.readFileSync(path.join(ROOT, 'model_parameters.json'), 'utf8'))
const SAMPLE_META = JSON.parse(fs.readFileSync(
  path.join(ROOT, 'assets', 'carbon_twill_height_samples.json'), 'utf8'))
const SAMPLE_BYTES = fs.readFileSync(path.join(ROOT, SAMPLE_META.prepared_file))
const SAMPLE_DATA = new Uint16Array(
  SAMPLE_BYTES.buffer, SAMPLE_BYTES.byteOffset, SAMPLE_BYTES.byteLength / Uint16Array.BYTES_PER_ELEMENT)

const quality = process.env.QUALITY || PARAMS.quality
if (!['draft', 'final'].includes(quality)) throw new Error(`Unsupported quality: ${quality}`)

// Millimetres. User-facing values live in model_parameters.json.
const P = Object.freeze({
  width: PARAMS.organizer.width,
  depth: PARAMS.organizer.depth,
  housingHeight: PARAMS.organizer.housing_height,
  sorterHeight: PARAMS.organizer.sorter_height,
  housingWall: PARAMS.housing.shell_wall,
  backWall: PARAMS.housing.back_wall,
  shelf: PARAMS.housing.shelf_thickness,
  housingRadius: PARAMS.housing.plan_corner_radius,
  drawerBodyWidth: PARAMS.drawer.body_width,
  drawerDepth: PARAMS.drawer.body_depth,
  drawerBodyStartY: PARAMS.drawer.body_start_y,
  drawerBodyHeight: PARAMS.drawer.body_height,
  drawerFrontWidth: PARAMS.drawer.front_width,
  drawerFrontReveal: PARAMS.drawer.front_reveal_each,
  drawerFrontDepth: PARAMS.drawer.front_depth,
  drawerFrontRadius: PARAMS.drawer.front_plan_radius,
  drawerFrontHeight: PARAMS.drawer.front_height,
  drawerWall: PARAMS.drawer.wall,
  drawerBottom: PARAMS.drawer.bottom,
  sorterBottom: PARAMS.sorter.bottom,
  sorterRadius: PARAMS.sorter.vertical_corner_radius,
  pegSize: 8.0,
  pegHeight: 2.8,
  socketSize: 8.6,
  socketDepth: 3.2,
  textureDepth: PARAMS.carbon_relief.engraving_depth,
  textureOverlap: PARAMS.carbon_relief.boolean_overlap,
  textureTileW: PARAMS.carbon_relief.tile_size[0],
  textureTileH: PARAMS.carbon_relief.tile_size[1],
  texturePitch: quality === 'final'
    ? PARAMS.carbon_relief.geometry_sample_pitch
    : PARAMS.carbon_relief.draft_sample_pitch,
  textureMarginZ: PARAMS.carbon_relief.edge_margin_z,
  simplifyTolerance: quality === 'final'
    ? PARAMS.carbon_relief.mesh_simplify_tolerance
    : Math.max(0.04, PARAMS.carbon_relief.mesh_simplify_tolerance),
  curveSegments: quality === 'final' ? 64 : 32
})

function assertParameters () {
  const opening = (P.housingHeight - 3 * P.shelf) / 2
  const derivedDrawerRadius = P.housingRadius - P.drawerFrontReveal
  if (P.width > 420 || P.depth > 420 || P.depth > 500) throw new Error('Envelope exceeds printer contract')
  if (P.housingWall < 2.4 || P.drawerWall < 1.8) throw new Error('Wall below supported design range')
  if (P.drawerBodyWidth >= P.width - 2 * P.housingWall) throw new Error('Drawer has no side clearance')
  if (P.drawerBodyHeight >= opening) throw new Error('Drawer has no vertical clearance')
  if (P.textureDepth >= P.backWall - 1.2) throw new Error('Engraving leaves too little rear wall')
  if (Math.abs(P.drawerFrontRadius - derivedDrawerRadius) > 1e-6) {
    throw new Error('Drawer front radius must equal housing radius minus side reveal')
  }
  if (SAMPLE_DATA.length !== SAMPLE_META.prepared_pixels[0] * SAMPLE_META.prepared_pixels[1]) {
    throw new Error('Prepared height-map sample count does not match its metadata')
  }
}

function roundedSection (width, depth, radius) {
  if (radius <= 0 || radius * 2 >= Math.min(width, depth)) throw new Error('Invalid rounded-section radius')
  return CrossSection.square([width - 2 * radius, depth - 2 * radius])
    .translate([radius, radius])
    .offset(radius, 'Round', 2, P.curveSegments)
}

function roundedPrismXY (width, depth, height, radius) {
  return roundedSection(width, depth, radius).extrude(height)
}

function roundedPrismXZ (width, height, depth, radius) {
  return roundedSection(width, height, radius).extrude(depth)
    .rotate([90, 0, 0]).translate([0, depth, 0])
}

function boxAt (x, y, z, sx, sy, sz) {
  return Manifold.cube([sx, sy, sz]).translate([x, y, z])
}

function lineSegment (a, b, normal) {
  const length = Math.hypot(b[0] - a[0], b[1] - a[1])
  return {
    kind: 'line', length,
    sample: t => ({
      point: [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t],
      normal
    })
  }
}

function arcSegment (center, radius, angle0, angle1) {
  const delta = angle1 - angle0
  return {
    kind: 'arc', length: Math.abs(delta) * radius,
    sample: t => {
      const angle = angle0 + delta * t
      const normal = [Math.cos(angle), Math.sin(angle)]
      return { point: [center[0] + radius * normal[0], center[1] + radius * normal[1]], normal }
    }
  }
}

function makePath (segments, periodic = false) {
  const starts = []
  let length = 0
  for (const segment of segments) {
    starts.push(length)
    length += segment.length
  }
  return {
    segments, starts, length, periodic,
    sample: distance => {
      let s = periodic ? ((distance % length) + length) % length : Math.min(Math.max(distance, 0), length)
      for (let i = 0; i < segments.length; i++) {
        const end = starts[i] + segments[i].length
        if (s <= end || i === segments.length - 1) {
          return segments[i].sample(segments[i].length === 0 ? 0 : (s - starts[i]) / segments[i].length)
        }
      }
      throw new Error('Path sampling failed')
    }
  }
}

function sorterPerimeterPath () {
  const w = P.width; const d = P.depth; const r = P.sorterRadius
  return makePath([
    lineSegment([w / 2, d], [r, d], [0, 1]),
    arcSegment([r, d - r], r, Math.PI / 2, Math.PI),
    lineSegment([0, d - r], [0, r], [-1, 0]),
    arcSegment([r, r], r, Math.PI, 3 * Math.PI / 2),
    lineSegment([r, 0], [w - r, 0], [0, -1]),
    arcSegment([w - r, r], r, -Math.PI / 2, 0),
    lineSegment([w, r], [w, d - r], [1, 0]),
    arcSegment([w - r, d - r], r, 0, Math.PI / 2),
    lineSegment([w - r, d], [w / 2, d], [0, 1])
  ], true)
}

function housingSideRearPath () {
  const w = P.width; const d = P.depth; const r = P.housingRadius
  return makePath([
    lineSegment([w, r], [w, d - r], [1, 0]),
    arcSegment([w - r, d - r], r, 0, Math.PI / 2),
    lineSegment([w - r, d], [r, d], [0, 1]),
    arcSegment([r, d - r], r, Math.PI / 2, Math.PI),
    lineSegment([0, d - r], [0, r], [-1, 0])
  ], false)
}

function drawerFrontPath () {
  const reveal = P.drawerFrontReveal
  const r = P.drawerFrontRadius
  const leftCenter = [P.housingRadius, P.housingRadius]
  const rightCenter = [P.width - P.housingRadius, P.housingRadius]
  return makePath([
    arcSegment(leftCenter, r, Math.PI, 3 * Math.PI / 2),
    lineSegment([P.housingRadius, reveal], [P.width - P.housingRadius, reveal], [0, -1]),
    arcSegment(rightCenter, r, -Math.PI / 2, 0)
  ], false)
}

function flatCouponPath () {
  return makePath([lineSegment([0, 8], [90, 8], [0, -1])], false)
}

function sampleTexture (uMm, vMm) {
  const width = SAMPLE_META.prepared_pixels[0]
  const height = SAMPLE_META.prepared_pixels[1]
  const wrap = (value, period) => ((value % period) + period) % period
  const x = wrap(uMm, P.textureTileW) / P.textureTileW * width
  // Image row zero is the visual top; geometric V increases upward.
  const y = wrap(-vMm, P.textureTileH) / P.textureTileH * height
  const x0 = Math.floor(x) % width
  const y0 = Math.floor(y) % height
  const x1 = (x0 + 1) % width
  const y1 = (y0 + 1) % height
  const tx = x - Math.floor(x)
  const ty = y - Math.floor(y)
  const at = (ix, iy) => SAMPLE_DATA[iy * width + ix] / 65535
  return (1 - ty) * ((1 - tx) * at(x0, y0) + tx * at(x1, y0)) +
    ty * ((1 - tx) * at(x0, y1) + tx * at(x1, y1))
}

function makeReliefPatch ({ path2d, z0, z1, textureOffsetU = 0, textureOffsetV = 0 }) {
  const nU = path2d.periodic
    ? Math.max(3, Math.ceil(path2d.length / P.texturePitch))
    : Math.max(2, Math.ceil(path2d.length / P.texturePitch) + 1)
  const nV = Math.max(2, Math.ceil((z1 - z0) / P.texturePitch) + 1)
  const du = path2d.length / (path2d.periodic ? nU : nU - 1)
  const dz = (z1 - z0) / (nV - 1)
  const surfaceVertices = nU * nV
  const vertices = new Float32Array(surfaceVertices * 2 * 3)
  const outer = (i, j) => j * nU + i
  const inner = (i, j) => surfaceVertices + j * nU + i
  const put = (index, xyz) => {
    vertices[index * 3] = xyz[0]
    vertices[index * 3 + 1] = xyz[1]
    vertices[index * 3 + 2] = xyz[2]
  }

  for (let j = 0; j < nV; j++) {
    const z = z0 + dz * j
    for (let i = 0; i < nU; i++) {
      const u = du * i
      const { point, normal } = path2d.sample(u)
      const h = sampleTexture(u + textureOffsetU, z + textureOffsetV)
      put(outer(i, j), [
        point[0] + P.textureOverlap * normal[0],
        point[1] + P.textureOverlap * normal[1], z
      ])
      put(inner(i, j), [
        point[0] - P.textureDepth * h * normal[0],
        point[1] - P.textureDepth * h * normal[1], z
      ])
    }
  }

  const faces = []
  const add = (a, b, c) => faces.push(a, b, c)
  const uCells = path2d.periodic ? nU : nU - 1
  for (let j = 0; j < nV - 1; j++) {
    for (let i = 0; i < uCells; i++) {
      const i2 = (i + 1) % nU
      const oa = outer(i, j); const ob = outer(i2, j)
      const oc = outer(i2, j + 1); const od = outer(i, j + 1)
      add(oa, ob, oc); add(oa, oc, od)
      const ia = inner(i, j); const ib = inner(i2, j)
      const ic = inner(i2, j + 1); const id = inner(i, j + 1)
      add(ia, ic, ib); add(ia, id, ic)
    }
  }

  for (let i = 0; i < uCells; i++) {
    const i2 = (i + 1) % nU
    const ob0 = outer(i, 0); const ob1 = outer(i2, 0)
    const ib0 = inner(i, 0); const ib1 = inner(i2, 0)
    add(ob0, ib1, ob1); add(ob0, ib0, ib1)
    const ot0 = outer(i, nV - 1); const ot1 = outer(i2, nV - 1)
    const it0 = inner(i, nV - 1); const it1 = inner(i2, nV - 1)
    add(ot0, ot1, it1); add(ot0, it1, it0)
  }

  if (!path2d.periodic) {
    for (let j = 0; j < nV - 1; j++) {
      const os0 = outer(0, j); const os1 = outer(0, j + 1)
      const is0 = inner(0, j); const is1 = inner(0, j + 1)
      add(os0, os1, is1); add(os0, is1, is0)
      const oe0 = outer(nU - 1, j); const oe1 = outer(nU - 1, j + 1)
      const ie0 = inner(nU - 1, j); const ie1 = inner(nU - 1, j + 1)
      add(oe0, ie0, ie1); add(oe0, ie1, oe1)
    }
  }

  const patch = Manifold.ofMesh(new Mesh({
    numProp: 3,
    vertProperties: vertices,
    triVerts: new Uint32Array(faces)
  }))
  return patch.simplify(P.simplifyTolerance)
}

function pathPolyline (path2d) {
  const points = []
  for (const segment of path2d.segments) {
    const divisions = segment.kind === 'arc'
      ? Math.max(3, Math.ceil(segment.length / (2 * Math.PI * P.housingRadius / P.curveSegments)))
      : 1
    for (let i = 0; i < divisions; i++) points.push(segment.sample(i / divisions))
  }
  points.push(path2d.segments.at(-1).sample(1))
  return points
}

function drawerFrontBand () {
  const samples = pathPolyline(drawerFrontPath())
  const outer = samples.map(({ point }) => point)
  const inner = [...samples].reverse().map(({ point, normal }) => [
    point[0] - P.drawerFrontDepth * normal[0],
    point[1] - P.drawerFrontDepth * normal[1]
  ])
  const polygon = [...outer, ...inner]
  return CrossSection(polygon, 'NonZero').extrude(P.drawerFrontHeight)
}

function buildHousingBase () {
  const opening = (P.housingHeight - 3 * P.shelf) / 2
  let body = roundedPrismXY(P.width, P.depth, P.housingHeight, P.housingRadius)
  const cavityW = P.width - 2 * P.housingWall
  const cavityD = P.depth - P.backWall + 0.4
  const cavityR = P.housingRadius - P.housingWall
  const cavities = Manifold.union([
    roundedPrismXY(cavityW, cavityD, opening, cavityR)
      .translate([P.housingWall, -0.4, P.shelf]),
    roundedPrismXY(cavityW, cavityD, opening, cavityR)
      .translate([P.housingWall, -0.4, 2 * P.shelf + opening])
  ])
  body = body.subtract(cavities)

  const pegs = []
  for (const x of [22, P.width - 22 - P.pegSize]) {
    for (const y of [22, P.depth - 22 - P.pegSize]) {
      pegs.push(boxAt(x, y, P.housingHeight - 0.08,
        P.pegSize, P.pegSize, P.pegHeight + 0.08))
    }
  }
  return Manifold.union([body, ...pegs])
}

function buildDrawerBase () {
  const x0 = (P.width - P.drawerBodyWidth) / 2
  const outer = roundedPrismXY(P.drawerBodyWidth, P.drawerDepth,
    P.drawerBodyHeight, 6).translate([x0, P.drawerBodyStartY, 0])
  const inner = roundedPrismXY(P.drawerBodyWidth - 2 * P.drawerWall,
    P.drawerDepth - P.drawerWall - 3.2, P.drawerBodyHeight + 1, 3.8)
    .translate([x0 + P.drawerWall, P.drawerBodyStartY + 3.2, P.drawerBottom])
  let drawer = Manifold.union([outer.subtract(inner), drawerFrontBand()])
  const handleX = (P.width - 82) / 2
  drawer = drawer.subtract(roundedPrismXZ(82, 28, 12, 10)
    .translate([handleX, -1, 50]))
  return Manifold.union([
    drawer,
    boxAt(x0 + 42, P.drawerBodyStartY + 1, 0, 4, P.drawerDepth - 8, 0.8),
    boxAt(x0 + P.drawerBodyWidth - 46, P.drawerBodyStartY + 1, 0, 4, P.drawerDepth - 8, 0.8)
  ])
}

function buildSorterBase () {
  let sorter = roundedPrismXY(P.width, P.depth, P.sorterHeight, P.sorterRadius)
  const cavityHeight = P.sorterHeight - P.sorterBottom + 1
  const specs = [
    [4, 4, 96, 222, 8], [104, 4, 66, 106, 7], [174, 4, 68, 106, 7],
    [246, 4, 70, 106, 7], [104, 114, 104, 112, 8], [212, 114, 104, 112, 8]
  ]
  sorter = sorter.subtract(Manifold.union(specs.map(([x, y, w, d, r]) =>
    roundedPrismXY(w, d, cavityHeight, r).translate([x, y, P.sorterBottom]))))

  const sockets = []
  for (const x of [21.7, P.width - 22 - P.pegSize - 0.3]) {
    for (const y of [21.7, P.depth - 22 - P.pegSize - 0.3]) {
      sockets.push(boxAt(x, y, -0.1, P.socketSize, P.socketSize, P.socketDepth + 0.1))
    }
  }
  return sorter.subtract(Manifold.union(sockets))
}

function buildFitCoupon () {
  const parts = []
  ;[0.30, 0.45, 0.60].forEach((gap, i) => {
    const x = i * 36
    const channelW = 20
    const wall = 2.4
    parts.push(Manifold.union([
      boxAt(x, 0, 0, channelW + 2 * wall, 42, 2.4),
      boxAt(x, 0, 0, wall, 42, 12),
      boxAt(x + channelW + wall, 0, 0, wall, 42, 12)
    ]))
    parts.push(boxAt(x + wall + gap, 47, 0, channelW - 2 * gap, 28, 6))
  })
  return Manifold.compose(parts)
}

function buildTextureCouponBase () {
  return Manifold.union([
    boxAt(0, 0, 0, 90, 20, 2.4),
    boxAt(0, 8, 0, 90, 2.4, 55),
    boxAt(5, 5, 0, 7, 8, 8),
    boxAt(78, 5, 0, 7, 8, 8)
  ])
}

function printOrientHousing (housing) {
  return housing.rotate([-90, 0, 0]).translate([0, 0, P.depth])
}

function writeBinaryStl (filename, solid) {
  const mesh = solid.getMesh()
  const vertexPath = `${filename}.vertices.f32`
  const indexPath = `${filename}.indices.u32`
  fs.writeFileSync(vertexPath, Buffer.from(
    mesh.vertProperties.buffer, mesh.vertProperties.byteOffset, mesh.vertProperties.byteLength))
  fs.writeFileSync(indexPath, Buffer.from(
    mesh.triVerts.buffer, mesh.triVerts.byteOffset, mesh.triVerts.byteLength))
  const result = spawnSync(process.env.PYTHON || 'python3', [
    path.join(ROOT, 'tools', 'write_binary_stl.py'),
    '--vertices', vertexPath,
    '--indices', indexPath,
    '--num-prop', String(mesh.numProp),
    '--output', filename
  ], { encoding: 'utf8' })
  if (result.status !== 0) {
    throw new Error(`STL writer failed for ${path.basename(filename)}: ${result.stderr || result.stdout}`)
  }
  return mesh.numTri
}

function boundsRecord (name, solid, triangles) {
  const bounds = solid.boundingBox()
  return {
    name, bounds: [bounds.min, bounds.max],
    size: bounds.max.map((v, i) => v - bounds.min[i]),
    triangles,
    volume_mm3: solid.volume(), surface_area_mm2: solid.surfaceArea(), status: solid.status()
  }
}

function assertSolid (name, solid) {
  if (solid.status() !== 'NoError') throw new Error(`${name}: ${solid.status()}`)
}

function keepLargestBody (solid, name, maximumDiscardedVolumeMm3 = 0.2) {
  const bodies = solid.decompose()
  if (bodies.length === 1) return { solid, report: { name, input_bodies: 1, discarded_mm3: 0 } }
  const ranked = bodies.map(body => ({ body, volume: body.volume() }))
    .sort((a, b) => b.volume - a.volume)
  const discarded = ranked.slice(1).reduce((sum, item) => sum + item.volume, 0)
  if (discarded > maximumDiscardedVolumeMm3) {
    for (const item of ranked) item.body.delete()
    throw new Error(`${name}: detached bodies total ${discarded.toFixed(6)} mm3`)
  }
  const kept = ranked[0].body
  for (const item of ranked.slice(1)) item.body.delete()
  solid.delete()
  console.log(`[cleanup] ${name}: removed ${ranked.length - 1} chips (${discarded.toFixed(6)} mm3)`)
  return {
    solid: kept,
    report: {
      name, input_bodies: ranked.length, retained_bodies: 1,
      discarded_bodies: ranked.length - 1, discarded_mm3: discarded,
      maximum_allowed_discarded_mm3: maximumDiscardedVolumeMm3
    }
  }
}

function main () {
  assertParameters()
  for (const directory of [STL, BASE, CUTTERS, ASSEMBLY]) fs.mkdirSync(directory, { recursive: true })
  const partRecords = []
  const cutterRecords = []
  const cleanupRecords = []

  console.log(`[build] ${quality}: housing`)
  const housingBase = buildHousingBase()
  const housingCutter = makeReliefPatch({
    path2d: housingSideRearPath(), z0: P.textureMarginZ, z1: P.housingHeight - P.textureMarginZ
  })
  assertSolid('housingBase', housingBase); assertSolid('housingCutter', housingCutter)
  const housing = housingBase.subtract(housingCutter).simplify(P.simplifyTolerance)
  assertSolid('housing', housing)
  const housingPrint = printOrientHousing(housing)
  assertSolid('housingPrint', housingPrint)
  writeBinaryStl(path.join(BASE, 'housing_base_before_engraving.stl'), housingBase)
  const housingCutterTriangles = writeBinaryStl(
    path.join(CUTTERS, 'housing_carbon_engraving_cutter.stl'), housingCutter)
  const housingTriangles = writeBinaryStl(path.join(STL, '01_housing_print_on_back.stl'), housingPrint)
  cutterRecords.push(boundsRecord('housing_cutter', housingCutter, housingCutterTriangles))
  partRecords.push(boundsRecord('housing_print', housingPrint, housingTriangles))
  housingPrint.delete(); housing.delete(); housingCutter.delete(); housingBase.delete()

  console.log(`[build] ${quality}: drawer`)
  const drawerBase = buildDrawerBase()
  let drawerCutter = makeReliefPatch({
    path2d: drawerFrontPath(), z0: -0.1,
    z1: P.drawerFrontHeight + 0.1
  })
  const handleKeepout = boxAt((P.width - 82) / 2 - 3, -2, 47, 88, 17, 22)
  drawerCutter = drawerCutter.subtract(handleKeepout).simplify(P.simplifyTolerance)
  assertSolid('drawerBase', drawerBase); assertSolid('drawerCutter', drawerCutter)
  const drawerResult = keepLargestBody(
    drawerBase.subtract(drawerCutter).simplify(P.simplifyTolerance), 'drawer_after_engraving')
  const drawer = drawerResult.solid
  cleanupRecords.push(drawerResult.report)
  assertSolid('drawer', drawer)
  writeBinaryStl(path.join(BASE, 'drawer_base_before_engraving.stl'), drawerBase)
  const drawerCutterTriangles = writeBinaryStl(
    path.join(CUTTERS, 'drawer_front_carbon_engraving_cutter.stl'), drawerCutter)
  const drawerTriangles = writeBinaryStl(path.join(STL, '02_drawer_print_twice.stl'), drawer)
  cutterRecords.push(boundsRecord('drawer_cutter', drawerCutter, drawerCutterTriangles))
  partRecords.push(boundsRecord('drawer_print', drawer, drawerTriangles))
  drawer.delete(); drawerCutter.delete(); drawerBase.delete()

  console.log(`[build] ${quality}: sorter`)
  const sorterBase = buildSorterBase()
  const sorterCutter = makeReliefPatch({
    path2d: sorterPerimeterPath(), z0: P.textureMarginZ,
    z1: P.sorterHeight - P.textureMarginZ
  })
  assertSolid('sorterBase', sorterBase); assertSolid('sorterCutter', sorterCutter)
  const sorter = sorterBase.subtract(sorterCutter).simplify(P.simplifyTolerance)
  assertSolid('sorter', sorter)
  writeBinaryStl(path.join(BASE, 'top_sorter_base_before_engraving.stl'), sorterBase)
  const sorterCutterTriangles = writeBinaryStl(
    path.join(CUTTERS, 'top_sorter_carbon_engraving_cutter.stl'), sorterCutter)
  const sorterTriangles = writeBinaryStl(path.join(STL, '03_top_sorter_print_bottom_down.stl'), sorter)
  cutterRecords.push(boundsRecord('sorter_cutter', sorterCutter, sorterCutterTriangles))
  partRecords.push(boundsRecord('top_sorter_print', sorter, sorterTriangles))
  sorter.delete(); sorterCutter.delete(); sorterBase.delete()

  console.log(`[build] ${quality}: coupons and manufacturing STL exports`)
  const fitCoupon = buildFitCoupon()
  const textureCouponBase = buildTextureCouponBase()
  const textureCouponCutter = makeReliefPatch({ path2d: flatCouponPath(), z0: 4, z1: 51 })
  const textureCoupon = textureCouponBase.subtract(textureCouponCutter).simplify(P.simplifyTolerance)

  const solids = { fitCoupon, textureCoupon, textureCouponCutter }
  for (const [name, solid] of Object.entries(solids)) assertSolid(name, solid)

  const fitTriangles = writeBinaryStl(path.join(STL, '04_fit_coupon_optional.stl'), fitCoupon)
  const textureTriangles = writeBinaryStl(
    path.join(STL, '05_carbon_texture_coupon_optional.stl'), textureCoupon)
  const textureCutterTriangles = writeBinaryStl(
    path.join(CUTTERS, 'carbon_texture_coupon_engraving_cutter.stl'), textureCouponCutter)
  partRecords.push(boundsRecord('fit_coupon', fitCoupon, fitTriangles))
  partRecords.push(boundsRecord('texture_coupon', textureCoupon, textureTriangles))
  cutterRecords.push(boundsRecord(
    'texture_coupon_cutter', textureCouponCutter, textureCutterTriangles))
  fitCoupon.delete(); textureCoupon.delete(); textureCouponCutter.delete(); textureCouponBase.delete()

  console.log(`[build] ${quality}: lightweight assembly preview`)
  const opening = (P.housingHeight - 3 * P.shelf) / 2
  // Use the exact untextured bases for the lightweight assembly STL. The
  // manufacturing STLs above retain the full image-derived engraving; omitting
  // it here avoids misleading painter-order artifacts in simple preview tools.
  const previewHousing = buildHousingBase()
  const previewDrawer = buildDrawerBase()
  const previewSorter = buildSorterBase()
  const previewDrawerLow = previewDrawer.translate([0, -44, P.shelf + 0.8])
  const previewDrawerHigh = previewDrawer.translate([0, -18, 2 * P.shelf + opening + 0.8])
  const previewSorterPlaced = previewSorter.translate(
    [0, 0, P.housingHeight + P.pegHeight - P.socketDepth])
  const assembly = Manifold.compose([
    previewHousing, previewDrawerLow, previewDrawerHigh, previewSorterPlaced
  ])
  assertSolid('assembly', assembly)
  writeBinaryStl(path.join(ASSEMBLY, 'desk_organizer_assembly_preview.stl'), assembly)
  assembly.delete(); previewHousing.delete(); previewDrawer.delete(); previewSorter.delete()
  previewDrawerLow.delete(); previewDrawerHigh.delete(); previewSorterPlaced.delete()

  const manifest = {
    generated_utc: new Date().toISOString(),
    revision: '1.1.2', quality,
    generator: 'Node.js + manifold-3d WASM; image-derived uint16 height-map cutter',
    parameters: P,
    heightmap: SAMPLE_META,
    mapping: {
      operation: 'engraving', white_is: 'maximum_depth',
      u: 'continuous surface arc length', v: 'world Z',
      housing: 'right side through rear to left side',
      sorter: 'full rounded perimeter, periodic seam at rear center',
      drawer: 'housing-offset front curve; handles masked'
    },
    parts: partRecords,
    cutters: cutterRecords,
    mesh_cleanup: cleanupRecords
  }
  fs.writeFileSync(path.join(OUT, 'build_manifest.json'), JSON.stringify(manifest, null, 2) + '\n')
  console.log(`[build] ${quality}: complete`)
}

main()
