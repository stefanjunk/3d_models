// Monolithic honeycomb hair clip, revision 4.
// Units: millimetres. The exported geometry is the open, unlatched print state.

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import ManifoldModule from 'manifold-3d'
import { strToU8, zipSync } from 'fflate'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const wasm = await ManifoldModule()
wasm.setup()
const { CrossSection, Manifold } = wasm

const DEFAULTS = Object.freeze({
  outputDir: path.join(__dirname, 'output'),
  quality: 'final',
  shellStartX: 4.0,
  shellEndX: 56.0,
  shellThickness: 2.4,
  clipWidth: 22.0,
  flexureThickness: 1.6,
  flexureBandWidth: 8.0,
  railCentralWidth: 12.5,
  latchWidth: 8.0,
  armorAcrossFlats: 10.0,
  armorGap: 0.8,
  armorRise: 0.9,
  armorEmbed: 0.45,
  petgDensityGPerCm3: 1.27
})

function assertParams (p) {
  if (!['preview', 'final'].includes(p.quality)) throw new Error('quality must be preview or final')
  if (p.shellThickness < 1.6) throw new Error('shellThickness must be at least 1.6 mm')
  if (p.flexureThickness < 1.6) throw new Error('flexureThickness must be at least 1.6 mm')
  if (p.clipWidth < 18 || p.clipWidth > 28) throw new Error('clipWidth outside validated range 18-28 mm')
  if (p.shellEndX - p.shellStartX < 45) throw new Error('arch span too short')
  if (p.armorAcrossFlats < 6.0) throw new Error('armorAcrossFlats is too small for a 0.4 mm nozzle')
  if (p.armorGap < 0.8) throw new Error('armorGap must be at least two 0.4 mm nozzle widths')
  if (p.railCentralWidth < 12.0) throw new Error('railCentralWidth would no longer support the comb teeth')
}

function sampledRange (a, b, count) {
  const out = []
  for (let i = 0; i <= count; i++) out.push(a + (b - a) * i / count)
  return out
}

function archOuterY (x, p) {
  const t = (x - p.shellStartX) / (p.shellEndX - p.shellStartX)
  return 16.5 + 7.5 * Math.sin(Math.PI * Math.max(0, Math.min(1, t)))
}

function archInnerY (x, p) {
  return archOuterY(x, p) - p.shellThickness
}

function signedAreaTwice (points) {
  let area = 0
  for (let i = 0; i < points.length; i++) {
    const a = points[i]
    const b = points[(i + 1) % points.length]
    area += a[0] * b[1] - b[0] * a[1]
  }
  return area
}

function extrudePolygon (points, z0, z1) {
  if (!(z1 > z0)) throw new Error('extrusion height must be positive')
  const oriented = signedAreaTwice(points) < 0 ? [...points].reverse() : points
  return new CrossSection([oriented]).extrude(z1 - z0).translate([0, 0, z0])
}

function manifoldFromIndexedMesh (vertices, triangles) {
  return new Manifold({
    numProp: 3,
    vertProperties: new Float32Array(vertices.flat()),
    triVerts: new Uint32Array(triangles.flat())
  })
}

// Build a closed prism whose footprint is in X/Z and whose two Y surfaces may
// vary per vertex. The centre fan keeps the curved bow approximation faceted
// while preserving the exact polygonal footprint of each armor cell.
function prismAlongY (pointsXZ, yBottom, yTop) {
  const count = pointsXZ.length
  const vertices = []
  for (const [x, z] of pointsXZ) vertices.push([x, yBottom(x, z), z])
  for (const [x, z] of pointsXZ) vertices.push([x, yTop(x, z), z])

  const centerX = pointsXZ.reduce((sum, point) => sum + point[0], 0) / count
  const centerZ = pointsXZ.reduce((sum, point) => sum + point[1], 0) / count
  const bottomCenter = vertices.length
  vertices.push([centerX, yBottom(centerX, centerZ), centerZ])
  const topCenter = vertices.length
  vertices.push([centerX, yTop(centerX, centerZ), centerZ])

  const triangles = []
  for (let i = 0; i < count; i++) {
    const j = (i + 1) % count
    triangles.push([bottomCenter, i, j])
    triangles.push([topCenter, count + j, count + i])
    triangles.push([i, count + i, count + j])
    triangles.push([i, count + j, j])
  }
  return manifoldFromIndexedMesh(vertices, triangles)
}

// Build a closed prism on an X/Y footprint with a piecewise-planar upper Z
// surface. This is used to taper the non-bed side of the lower rail.
function prismAlongZ (pointsXY, zTop) {
  const count = pointsXY.length
  const vertices = []
  for (const [x, y] of pointsXY) vertices.push([x, y, 0])
  for (const [x, y] of pointsXY) vertices.push([x, y, zTop(x, y)])

  const centerX = pointsXY.reduce((sum, point) => sum + point[0], 0) / count
  const centerY = pointsXY.reduce((sum, point) => sum + point[1], 0) / count
  const bottomCenter = vertices.length
  vertices.push([centerX, centerY, 0])
  const topCenter = vertices.length
  vertices.push([centerX, centerY, zTop(centerX, centerY)])

  const triangles = []
  for (let i = 0; i < count; i++) {
    const j = (i + 1) % count
    triangles.push([bottomCenter, j, i])
    triangles.push([topCenter, count + i, count + j])
    triangles.push([i, j, count + j])
    triangles.push([i, count + j, count + i])
  }
  return manifoldFromIndexedMesh(vertices, triangles)
}

function stripAlongPath2d (points, thickness, segments = 20) {
  const discs = points.map(point => CrossSection.circle(thickness / 2, segments).translate(point))
  const links = []
  for (let i = 0; i < discs.length - 1; i++) links.push(CrossSection.hull(discs[i], discs[i + 1]))
  return CrossSection.union(links)
}

function extrudePathStrip (points, thickness, z0, z1, segments) {
  return stripAlongPath2d(points, thickness, segments).extrude(z1 - z0).translate([0, 0, z0])
}

function makeArch (p) {
  const samples = p.quality === 'final' ? 40 : 20
  const xs = sampledRange(p.shellStartX, p.shellEndX, samples)
  const outer = xs.map(x => [x, archOuterY(x, p)])
  const inner = [...xs].reverse().map(x => [x, archInnerY(x, p)])
  return extrudePolygon([...outer, ...inner], 0, p.clipWidth)
}

function regularHexagon (centerA, centerB, circumradius) {
  const points = []
  for (let i = 0; i < 6; i++) {
    const angle = i * Math.PI / 3
    points.push([
      centerA + circumradius * Math.cos(angle),
      centerB + circumradius * Math.sin(angle)
    ])
  }
  return points
}

// Clip a convex X/Z footprint at the build plane. Revision 4 intentionally
// permits half cells only here; all other armor cells remain complete.
function clipPolygonAtMinZ (points, minZ = 0) {
  const clipped = []
  for (let i = 0; i < points.length; i++) {
    const current = points[i]
    const previous = points[(i + points.length - 1) % points.length]
    const currentInside = current[1] >= minZ - 1e-9
    const previousInside = previous[1] >= minZ - 1e-9
    if (currentInside !== previousInside) {
      const t = (minZ - previous[1]) / (current[1] - previous[1])
      clipped.push([
        previous[0] + t * (current[0] - previous[0]),
        minZ
      ])
    }
    if (currentInside) clipped.push(current)
  }
  return clipped
}

function makeArmor (p) {
  const parts = []
  const radius = p.armorAcrossFlats / Math.sqrt(3)
  const gridRadius = (p.armorAcrossFlats + p.armorGap) / Math.sqrt(3)
  const pitchX = 3 * gridRadius
  const pitchZ = (p.armorAcrossFlats + p.armorGap) / 2
  const evenRowStartX = 12.5
  const oddRowStartX = evenRowStartX - pitchX / 2
  const rowCount = 5
  const cellsPerRow = 3

  // A single, correctly staggered honeycomb lattice wraps the visible bow.
  // The build-plane row is clipped into half cells; rows 1-4 use complete
  // pointy-ended cells in one uniform orientation. Row 4 projects beyond the
  // non-bed side and its whole-cell outline creates the requested high/low edge.
  for (let row = 0; row < rowCount; row++) {
    const centerZ = row * pitchZ
    const firstCenterX = row % 2 === 0 ? evenRowStartX : oddRowStartX
    for (let column = 0; column < cellsPerRow; column++) {
      const centerX = firstCenterX + column * pitchX
      const wholeFootprint = regularHexagon(centerX, centerZ, radius)
      const footprint = row === 0 ? clipPolygonAtMinZ(wholeFootprint) : wholeFootprint
      parts.push(prismAlongY(
        footprint,
        x => archOuterY(x, p) - p.armorEmbed,
        x => archOuterY(x, p) + p.armorRise
      ))
    }
  }
  return Manifold.union(parts)
}

function railTopY (x) {
  return 4.8 + (x - 8.0) * (3.4 - 4.8) / (54.0 - 8.0)
}

function makeLowerRail (p) {
  const xStations = [7.0, 11.0, 16.0, 47.0, 52.0, 54.2]
  const railBottomY = x => 2.35 + (x - 7.0) * (0.75 - 2.35) / (54.2 - 7.0)
  const railUpperY = x => 4.83 + (x - 7.0) * (3.35 - 4.83) / (54.2 - 7.0)
  const railWidthAt = x => {
    if (x <= 11.0 || x >= 52.0) return p.clipWidth
    if (x < 16.0) return p.clipWidth + (x - 11.0) * (p.railCentralWidth - p.clipWidth) / 5.0
    if (x <= 47.0) return p.railCentralWidth
    return p.railCentralWidth + (x - 47.0) * (p.clipWidth - p.railCentralWidth) / 5.0
  }

  const railSections = []
  for (let i = 0; i < xStations.length - 1; i++) {
    const x0 = xStations[i]
    const x1 = xStations[i + 1]
    const footprint = [
      [x0, railBottomY(x0)],
      [x1, railBottomY(x1)],
      [x1, railUpperY(x1)],
      [x0, railUpperY(x0)]
    ]
    railSections.push(prismAlongZ(footprint, x => railWidthAt(x)))
  }
  const rail = Manifold.union(railSections)

  const teeth = []
  const centers = [13.0, 18.7, 24.4, 30.1, 35.8, 41.5, 47.2]
  for (let i = 0; i < centers.length; i++) {
    const x = centers[i]
    const baseY = railTopY(x) - 0.25
    const height = 5.8 + (i % 3) * 0.75
    teeth.push(extrudePolygon([
      [x - 2.0, baseY],
      [x + 2.0, baseY - 0.12],
      [x + 0.70, baseY + height],
      [x - 0.70, baseY + height]
    ], 0, 12.0))
  }
  return Manifold.union(rail, ...teeth)
}

function makeUpperTeeth (p) {
  const teeth = []
  const centers = [15, 21, 27, 33, 39, 45]
  for (let i = 0; i < centers.length; i++) {
    const x = centers[i]
    const baseY = archInnerY(x, p) + 0.22
    const length = 3.9 + (i % 2) * 0.55
    teeth.push(extrudePolygon([
      [x - 1.65, baseY],
      [x + 1.65, baseY],
      [x + 0.65, baseY - length],
      [x - 0.65, baseY - length]
    ], 0, 12.0))
  }
  return Manifold.union(teeth)
}

function makeFlexures (p) {
  const pathPoints = [
    [7.0, 16.2], [3.0, 14.5], [1.0, 10.0], [1.35, 6.0], [4.0, 3.3], [8.0, 4.30]
  ]
  const segs = p.quality === 'final' ? 24 : 14
  return extrudePathStrip(pathPoints, p.flexureThickness, 0, p.flexureBandWidth, segs)
}

function makeLatch (p) {
  const catchBody = extrudePolygon([
    [54.4, 10.95], [60.2, 10.95], [60.4, 14.8], [56.0, 15.1], [55.2, 12.7], [53.6, 12.7]
  ], 0, 9.6)

  const tonguePath = [[40.0, 2.20], [43.5, 1.60], [46.5, 2.50], [49.5, 4.50], [53.5, 6.50]]
  const tongue = extrudePathStrip(tonguePath, 1.6, 0, p.latchWidth, p.quality === 'final' ? 24 : 14)
  const hook = extrudePolygon([
    [52.9, 5.75], [56.1, 6.70], [55.85, 8.25], [53.45, 7.70]
  ], 0, p.latchWidth)
  const thumbPad = extrudePolygon([
    [52.5, 5.25], [56.8, 6.20], [56.3, 8.50], [53.0, 7.85]
  ], 0, p.latchWidth + 2.4)

  return Manifold.union(catchBody, tongue, hook, thumbPad)
}

function makeHardStop () {
  return extrudePolygon([
    [7.0, 2.2], [10.2, 3.0], [9.2, 7.2], [6.2, 7.0]
  ], 0, 11.0)
}

function buildHairClip (overrides = {}) {
  const p = { ...DEFAULTS, ...overrides }
  assertParams(p)
  return Manifold.union(
    makeArch(p),
    makeArmor(p),
    makeLowerRail(p),
    makeUpperTeeth(p),
    makeFlexures(p),
    makeLatch(p),
    makeHardStop(p)
  )
}

function makeLatchCoupon () {
  const base = Manifold.cube([30, 3, 8])
  const tongue = extrudePathStrip([[6, 2.5], [6, 8], [8.5, 14.5], [10.0, 17.0]], 1.6, 0, 8, 24)
  const hook = extrudePolygon([[9.3, 16.1], [12.4, 16.8], [12.0, 18.3], [9.8, 17.7]], 0, 8)
  const catchPost = extrudePolygon([[14.2, 2.5], [18.0, 2.5], [18.0, 18.5], [14.5, 18.5], [14.5, 17.1], [12.0, 17.1], [12.0, 15.8], [14.2, 15.8]], 0, 8)
  const labelBars = [22, 25.5, 29].map((x, i) => Manifold.cube([1.0, 6 + i * 1.3, 8]).translate([x - 0.5, 2, 0]))
  return Manifold.union(base, tongue, hook, catchPost, ...labelBars)
}

function meshData (manifold) {
  const mesh = manifold.getMesh()
  const vertices = []
  for (let i = 0; i < mesh.numVert; i++) {
    const offset = i * mesh.numProp
    vertices.push([
      mesh.vertProperties[offset],
      mesh.vertProperties[offset + 1],
      mesh.vertProperties[offset + 2]
    ])
  }
  const triangles = []
  for (let i = 0; i < mesh.numTri; i++) {
    triangles.push([mesh.triVerts[i * 3], mesh.triVerts[i * 3 + 1], mesh.triVerts[i * 3 + 2]])
  }
  return { vertices, triangles }
}

function normalForTriangle (a, b, c) {
  const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
  const ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
  const n = [
    ab[1] * ac[2] - ab[2] * ac[1],
    ab[2] * ac[0] - ab[0] * ac[2],
    ab[0] * ac[1] - ab[1] * ac[0]
  ]
  const length = Math.hypot(...n) || 1
  return n.map(value => value / length)
}

function writeBinaryStl (filename, mesh) {
  const out = Buffer.alloc(84 + mesh.triangles.length * 50)
  out.write('Monolithic honeycomb PETG hair clip r4', 0, 'ascii')
  out.writeUInt32LE(mesh.triangles.length, 80)
  let offset = 84
  for (const triangle of mesh.triangles) {
    const points = triangle.map(index => mesh.vertices[index])
    const normal = normalForTriangle(points[0], points[1], points[2])
    for (const value of normal) { out.writeFloatLE(value, offset); offset += 4 }
    for (const point of points) {
      for (const value of point) { out.writeFloatLE(value, offset); offset += 4 }
    }
    out.writeUInt16LE(0, offset)
    offset += 2
  }
  fs.writeFileSync(filename, out)
}

function xmlEscape (value) {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;')
}

function write3mf (filename, mesh, modelName) {
  const vertexXml = mesh.vertices.map(vertex => `        <vertex x="${vertex[0]}" y="${vertex[1]}" z="${vertex[2]}"/>`).join('\n')
  const triangleXml = mesh.triangles.map(triangle => `        <triangle v1="${triangle[0]}" v2="${triangle[1]}" v3="${triangle[2]}"/>`).join('\n')
  const modelXml = `<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <metadata name="Title">${xmlEscape(modelName)}</metadata>
  <metadata name="Designer">OpenAI Codex</metadata>
  <resources>
    <object id="1" type="model" name="${xmlEscape(modelName)}">
      <mesh>
        <vertices>
${vertexXml}
        </vertices>
        <triangles>
${triangleXml}
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1"/>
  </build>
</model>`
  const contentTypes = `<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>`
  const relationships = `<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>`
  const archive = zipSync({
    '[Content_Types].xml': strToU8(contentTypes),
    '_rels/.rels': strToU8(relationships),
    '3D/3dmodel.model': strToU8(modelXml)
  }, { level: 6 })
  fs.writeFileSync(filename, Buffer.from(archive))
}

function writeGeometry (manifold, basename, outputDir, include3mf = false) {
  fs.mkdirSync(outputDir, { recursive: true })
  const mesh = meshData(manifold)
  const stlPath = path.join(outputDir, `${basename}.stl`)
  writeBinaryStl(stlPath, mesh)
  let threeMfPath = null
  if (include3mf) {
    threeMfPath = path.join(outputDir, `${basename}.3mf`)
    write3mf(threeMfPath, mesh, basename)
  }
  const bounds = manifold.boundingBox()
  const dimensionsMm = bounds.max.map((value, index) => value - bounds.min[index])
  const volumeMm3 = manifold.volume()
  return {
    stlPath,
    threeMfPath,
    manifoldStatus: manifold.status(),
    connectedBodies: manifold.decompose().length,
    meshVertices: mesh.vertices.length,
    meshTriangles: mesh.triangles.length,
    bounds: [bounds.min, bounds.max],
    dimensionsMm,
    volumeMm3,
    petgMassG: volumeMm3 / 1000 * DEFAULTS.petgDensityGPerCm3
  }
}

function main () {
  const quality = process.argv.includes('--preview') ? 'preview' : 'final'
  const outputArg = process.argv.find(arg => arg.startsWith('--output-dir='))
  const outputDir = outputArg ? path.resolve(outputArg.slice('--output-dir='.length)) : DEFAULTS.outputDir
  const p = { ...DEFAULTS, quality, outputDir }
  const clip = buildHairClip(p)
  const coupon = makeLatchCoupon(p)
  const result = {
    generator: 'hair_clip.mjs',
    kernel: 'Manifold 3D 3.5.1',
    revision: 4,
    units: 'mm',
    quality,
    armor: {
      cellShape: 'uniform-pointy-regular-hexagon',
      layout: 'true-staggered-honeycomb-lattice',
      totalCellCount: 15,
      fullCellCount: 12,
      buildSideHalfCellCount: 3,
      nonBedSideWholeCellCount: 3,
      rowCount: 5,
      cellsPerRow: [3, 3, 3, 3, 3],
      acrossFlatsMm: p.armorAcrossFlats,
      nominalGrooveMm: p.armorGap,
      raisedHeightMm: p.armorRise,
      structuralShellWidthMm: p.clipWidth,
      nonBedCellEnvelopeMaxZMm: 4 * ((p.armorAcrossFlats + p.armorGap) / 2) + p.armorAcrossFlats / 2,
      uniformOrientation: true,
      dedicatedRotatedSideRow: false,
      standaloneEndBlocks: false
    },
    lowerRail: {
      centralWidthMm: p.railCentralWidth,
      fullEndWidthMm: p.clipWidth,
      leftTaperXmm: [11.0, 16.0],
      rightTaperXmm: [47.0, 52.0]
    },
    clip: writeGeometry(clip, 'masculine-honeycomb-hair-clip-r4', outputDir, true),
    coupon: writeGeometry(coupon, 'hair-clip-latch-coupon-r4', outputDir, false)
  }
  fs.writeFileSync(path.join(outputDir, 'generation-metrics.json'), JSON.stringify(result, null, 2) + '\n')
  process.stdout.write(JSON.stringify(result, null, 2) + '\n')
}

main()
