import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import Module from 'manifold-3d'

const wasm = await Module()
wasm.setup()
const { CrossSection, Manifold } = wasm

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const OUT = path.join(ROOT, 'output')
const STL = path.join(OUT, 'stl')
const ASSEMBLY = path.join(OUT, 'assembly')

// Millimetres. Public values are mirrored in model_parameters.json.
const P = Object.freeze({
  width: 320, depth: 230, housingHeight: 146, sorterHeight: 68,
  housingWall: 3.2, backWall: 2.4, shelf: 3.2, housingRadius: 10,
  drawerBodyWidth: 312.7, drawerDepth: 224.5, drawerBodyHeight: 62.5,
  drawerFrontWidth: 316, drawerFrontHeight: 65.2,
  drawerWall: 2.2, drawerBottom: 2.2,
  sorterBottom: 3.0, sorterRadius: 12,
  pegSize: 8.0, pegHeight: 2.8, socketSize: 8.6, socketDepth: 3.2,
  texturePrimaryDepth: 0.34, textureSecondaryDepth: 0.26,
  texturePrimaryWidth: 1.35, textureSecondaryWidth: 1.10,
  texturePitch: 7.2, textureAngleDeg: 45, curveSegments: 24
})

function assertParameters () {
  const opening = (P.housingHeight - 3 * P.shelf) / 2
  if (P.width > 419 || P.depth > 419 || P.depth > 499) throw new Error('Envelope exceeds printer contract')
  if (P.housingWall < 2.4 || P.drawerWall < 1.8) throw new Error('Wall below supported design range')
  if (P.drawerBodyWidth >= P.width - 2 * P.housingWall) throw new Error('Drawer has no side clearance')
  if (P.drawerBodyHeight >= opening) throw new Error('Drawer has no vertical clearance')
  if (P.texturePrimaryDepth > 0.5) throw new Error('Carbon emboss is too deep')
  if (P.textureSecondaryWidth < 0.8) throw new Error('Carbon feature is too narrow')
}

function roundedSection (width, depth, radius) {
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

function carbonPanelX ({ side, xFace, y0, y1, z0, z1 }) {
  const panelD = y1 - y0
  const panelH = z1 - z0
  const yc = (y0 + y1) / 2
  const zc = (z0 + z1) / 2
  const diagonal = Math.hypot(panelD, panelH) + 2 * P.texturePitch

  function strandFamily (angleDeg, pitch, width, depth, phase = 0) {
    const angle = angleDeg * Math.PI / 180
    const perpY = -Math.sin(angle)
    const perpZ = Math.cos(angle)
    const parts = []
    for (let offset = -diagonal / 2 + phase; offset <= diagonal / 2; offset += pitch) {
      const x = side === 'left' ? xFace - depth / 2 + 0.04 : xFace + depth / 2 - 0.04
      parts.push(Manifold.cube([depth + 0.12, diagonal, width], true)
        .rotate([angleDeg, 0, 0])
        .translate([x, yc + perpY * offset, zc + perpZ * offset]))
    }
    const slabX = side === 'left' ? xFace - depth : xFace - 0.08
    return Manifold.union(parts).intersect(boxAt(slabX, y0, z0, depth + 0.08, panelD, panelH))
  }

  return Manifold.union([
    strandFamily(P.textureAngleDeg, P.texturePitch, P.texturePrimaryWidth, P.texturePrimaryDepth),
    strandFamily(-P.textureAngleDeg, P.texturePitch, P.textureSecondaryWidth,
      P.textureSecondaryDepth, P.texturePitch / 2)
  ])
}

function carbonPanelZ ({ zFace, x0, x1, y0, y1 }) {
  const panelW = x1 - x0
  const panelD = y1 - y0
  const xc = (x0 + x1) / 2
  const yc = (y0 + y1) / 2
  const diagonal = Math.hypot(panelW, panelD) + 2 * P.texturePitch

  function strandFamily (angleDeg, pitch, width, depth, phase = 0) {
    const angle = angleDeg * Math.PI / 180
    const perpX = -Math.sin(angle)
    const perpY = Math.cos(angle)
    const parts = []
    for (let offset = -diagonal / 2 + phase; offset <= diagonal / 2; offset += pitch) {
      parts.push(Manifold.cube([diagonal, width, depth + 0.12], true)
        .rotate([0, 0, angleDeg])
        .translate([xc + perpX * offset, yc + perpY * offset, zFace + depth / 2 - 0.04]))
    }
    return Manifold.union(parts).intersect(boxAt(x0, y0, zFace - 0.08, panelW, panelD, depth + 0.08))
  }

  return Manifold.union([
    strandFamily(P.textureAngleDeg, P.texturePitch, P.texturePrimaryWidth, P.texturePrimaryDepth),
    strandFamily(-P.textureAngleDeg, P.texturePitch, P.textureSecondaryWidth,
      P.textureSecondaryDepth, P.texturePitch / 2)
  ])
}

function buildHousing () {
  const opening = (P.housingHeight - 3 * P.shelf) / 2
  let body = roundedPrismXZ(P.width, P.housingHeight, P.depth, P.housingRadius)
  const cavityW = P.width - 2 * P.housingWall
  const cavityD = P.depth - P.backWall + 0.6
  const cavities = Manifold.union([
    boxAt(P.housingWall, -0.3, P.shelf, cavityW, cavityD, opening),
    boxAt(P.housingWall, -0.3, 2 * P.shelf + opening, cavityW, cavityD, opening)
  ])
  body = body.subtract(cavities)

  const pegs = []
  for (const x of [22, P.width - 22 - P.pegSize]) {
    for (const y of [22, P.depth - 22 - P.pegSize]) {
      pegs.push(boxAt(x, y, P.housingHeight - 0.08,
        P.pegSize, P.pegSize, P.pegHeight + 0.08))
    }
  }
  body = Manifold.union([body, ...pegs])
  return Manifold.union([
    body,
    carbonPanelX({ side: 'left', xFace: 0, y0: 8, y1: P.depth - 8, z0: 12, z1: P.housingHeight - 12 }),
    carbonPanelX({ side: 'right', xFace: P.width, y0: 8, y1: P.depth - 8, z0: 12, z1: P.housingHeight - 12 })
  ])
}

function buildDrawer () {
  const x0 = (P.width - P.drawerBodyWidth) / 2
  const outer = roundedPrismXY(P.drawerBodyWidth, P.drawerDepth,
    P.drawerBodyHeight, 6).translate([x0, 0, 0])
  const inner = roundedPrismXY(P.drawerBodyWidth - 2 * P.drawerWall,
    P.drawerDepth - P.drawerWall - 3.2, P.drawerBodyHeight + 1, 3.8)
    .translate([x0 + P.drawerWall, 3.2, P.drawerBottom])
  let drawer = outer.subtract(inner)
  drawer = drawer.add(roundedPrismXZ(P.drawerFrontWidth, P.drawerFrontHeight, 3.6, 6)
    .translate([(P.width - P.drawerFrontWidth) / 2, 0, 0]))
  drawer = drawer.subtract(roundedPrismXZ(82, 28, 9, 10)
    .translate([(P.width - 82) / 2, -1, 50]))
  return Manifold.union([
    drawer,
    boxAt(x0 + 42, 4, 0, 4, P.drawerDepth - 8, 0.8),
    boxAt(x0 + P.drawerBodyWidth - 46, 4, 0, 4, P.drawerDepth - 8, 0.8)
  ])
}

function buildSorter () {
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
  sorter = sorter.subtract(Manifold.union(sockets))
  return Manifold.union([
    sorter,
    carbonPanelX({ side: 'left', xFace: 0, y0: 8, y1: P.depth - 8, z0: 9, z1: P.sorterHeight - 9 }),
    carbonPanelX({ side: 'right', xFace: P.width, y0: 8, y1: P.depth - 8, z0: 9, z1: P.sorterHeight - 9 })
  ])
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

function buildTextureCoupon () {
  // L-shaped coupon keeps the weave vertical, matching the final side panels.
  const base = boxAt(0, 0, 0, 90, 20, 2.4)
  const wall = boxAt(0, 8, 0, 90, 2.4, 55)
  const sidePattern = carbonPanelX({
    side: 'right', xFace: 0, y0: 4, y1: 86, z0: 4, z1: 51
  }).rotate([0, 0, 90]).translate([90, 10.4, 0])
  const feet = Manifold.union([
    boxAt(5, 5, 0, 7, 8, 8),
    boxAt(78, 5, 0, 7, 8, 8)
  ])
  return Manifold.union([base, wall, sidePattern, feet])
}

function printOrientHousing (housing) {
  return housing.rotate([-90, 0, 0]).translate([0, 0, P.depth])
}

function triangleNormal (a, b, c) {
  const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
  const v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
  let n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
  const length = Math.hypot(...n) || 1
  n = n.map(x => x / length)
  return n
}

function writeBinaryStl (filename, solid) {
  const mesh = solid.getMesh()
  const buffer = Buffer.allocUnsafe(84 + mesh.numTri * 50)
  buffer.fill(0, 0, 80)
  buffer.write('MANIFOLD-3D DESK ORGANIZER', 0, 'ascii')
  buffer.writeUInt32LE(mesh.numTri, 80)
  let offset = 84
  for (let tri = 0; tri < mesh.numTri; tri++) {
    const ids = mesh.triVerts.subarray(3 * tri, 3 * tri + 3)
    const vertices = Array.from(ids, id => [
      mesh.vertProperties[id * mesh.numProp], mesh.vertProperties[id * mesh.numProp + 1],
      mesh.vertProperties[id * mesh.numProp + 2]
    ])
    for (const value of triangleNormal(...vertices)) { buffer.writeFloatLE(value, offset); offset += 4 }
    for (const vertex of vertices) {
      for (const value of vertex) { buffer.writeFloatLE(value, offset); offset += 4 }
    }
    buffer.writeUInt16LE(0, offset); offset += 2
  }
  fs.writeFileSync(filename, buffer)
}

function boundsRecord (name, solid) {
  const bounds = solid.boundingBox()
  return {
    name, bounds: [bounds.min, bounds.max],
    size: bounds.max.map((v, i) => v - bounds.min[i]),
    volume_mm3: solid.volume(), surface_area_mm2: solid.surfaceArea(), status: solid.status()
  }
}

function main () {
  assertParameters()
  fs.mkdirSync(STL, { recursive: true })
  fs.mkdirSync(ASSEMBLY, { recursive: true })
  const housing = buildHousing()
  const drawer = buildDrawer()
  const sorter = buildSorter()
  const fitCoupon = buildFitCoupon()
  const textureCoupon = buildTextureCoupon()
  const housingPrint = printOrientHousing(housing)
  const solids = { housing, drawer, sorter, fitCoupon, textureCoupon, housingPrint }
  for (const [name, solid] of Object.entries(solids)) {
    if (solid.status() !== 'NoError') throw new Error(`${name}: ${solid.status()}`)
  }

  writeBinaryStl(path.join(STL, '01_housing_print_on_back.stl'), housingPrint)
  writeBinaryStl(path.join(STL, '02_drawer_print_twice.stl'), drawer)
  writeBinaryStl(path.join(STL, '03_top_sorter_print_bottom_down.stl'), sorter)
  writeBinaryStl(path.join(STL, '04_fit_coupon_optional.stl'), fitCoupon)
  writeBinaryStl(path.join(STL, '05_carbon_texture_coupon_optional.stl'), textureCoupon)

  const opening = (P.housingHeight - 3 * P.shelf) / 2
  const assembly = Manifold.compose([
    housing,
    drawer.translate([0, -44, P.shelf + 0.8]),
    drawer.translate([0, -18, 2 * P.shelf + opening + 0.8]),
    sorter.translate([0, 0, P.housingHeight + P.pegHeight - P.socketDepth])
  ])
  writeBinaryStl(path.join(ASSEMBLY, 'desk_organizer_assembly_preview.stl'), assembly)

  const manifest = {
    generated_utc: new Date().toISOString(), generator: 'Node.js + manifold-3d WASM', parameters: P,
    parts: [
      boundsRecord('housing_print', housingPrint), boundsRecord('drawer_print', drawer),
      boundsRecord('top_sorter_print', sorter), boundsRecord('fit_coupon', fitCoupon),
      boundsRecord('texture_coupon', textureCoupon)
    ]
  }
  fs.writeFileSync(path.join(OUT, 'build_manifest.json'), JSON.stringify(manifest, null, 2) + '\n')
}

main()
