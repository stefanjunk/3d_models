// Parametric print-in-place honeycomb hair clip, revision 6.
// Units: millimetres. Exports are oriented on the large side face (Z = 0).

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

const PRESETS = Object.freeze({
  small: { clipLength: 68.0, archRise: 8.0 },
  medium: { clipLength: 76.0, archRise: 10.0 },
  large: { clipLength: 85.0, archRise: 12.0 },
  extra_large: { clipLength: 96.0, archRise: 15.0 }
})

const DEFAULTS = Object.freeze({
  outputDir: path.join(__dirname, 'output-r6-final'),
  releaseState: 'FINAL',
  quality: 'final',
  preset: 'large',
  clipLength: PRESETS.large.clipLength,
  archRise: PRESETS.large.archRise,
  bodyWidth: 24.0,
  armorEnvelopeWidth: 28.6,
  shellThickness: 2.4,
  railCentralWidth: 13.0,
  latchTongueThickness: 1.6,
  latchWidth: 9.0,
  armorGap: 0.8,
  armorRise: 0.9,
  armorEmbed: 0.45,
  armorMinLongitudinalScale: 0.94,
  armorMaxLongitudinalScale: 1.0,
  hingePinDiameter: 4.0,
  hingeRadialClearance: 0.35,
  hingeAxialClearance: 0.40,
  hingeOuterRadius: 4.60,
  hingeSleeveWall: 1.80,
  hingeMiddleLength: 8.0,
  hingeExportAngleDeg: -10.0,
  hingeClosedAngleDeg: -3.0,
  hingeFullOpenAngleDeg: -31.0,
  includeWatermark: true,
  watermarkDepth: 0.40,
  watermarkAssetId: 'JSI-WM-001-R1',
  watermarkProfile: 'compact',
  petgDensityGPerCm3: 1.27
})

function clamp (value, minValue, maxValue) {
  return Math.max(minValue, Math.min(maxValue, value))
}

function assertParams (p) {
  if (!['preview', 'final'].includes(p.quality)) throw new Error('quality must be preview or final')
  if (!['DRAFT', 'FINAL'].includes(p.releaseState)) throw new Error('releaseState must be DRAFT or FINAL')
  if (p.clipLength < 65 || p.clipLength > 105) throw new Error('clipLength outside validated generation range 65-105 mm')
  if (p.archRise < 7 || p.archRise > 18) throw new Error('archRise outside validated generation range 7-18 mm')
  if (p.bodyWidth < 22 || p.bodyWidth > 28) throw new Error('bodyWidth outside validated range 22-28 mm')
  if (p.shellThickness < 2.0) throw new Error('shellThickness must be at least 2.0 mm')
  if (p.railCentralWidth < 12.0) throw new Error('railCentralWidth would no longer support the comb teeth')
  if (p.latchTongueThickness < 1.6) throw new Error('latchTongueThickness must be at least 1.6 mm')
  if (p.armorGap < 0.8) throw new Error('armorGap must be at least two 0.4 mm nozzle widths')
  if (p.hingePinDiameter < 3.6 || p.hingePinDiameter > 5.0) throw new Error('hingePinDiameter outside validated range 3.6-5.0 mm')
  if (p.hingeRadialClearance < 0.25 || p.hingeRadialClearance > 0.60) throw new Error('hingeRadialClearance outside validated range 0.25-0.60 mm')
  if (p.hingeAxialClearance < 0.30 || p.hingeAxialClearance > 0.80) throw new Error('hingeAxialClearance outside validated range 0.30-0.80 mm')
  if (p.hingeFullOpenAngleDeg > p.hingeExportAngleDeg || p.hingeExportAngleDeg >= p.hingeClosedAngleDeg) {
    throw new Error('hinge angles must satisfy fullOpen < exportOpen < closed')
  }
  if (p.hingeClosedAngleDeg - p.hingeFullOpenAngleDeg < 28.0) throw new Error('hinge useful travel must be at least 28 degrees')
}

function deriveParameters (raw) {
  const p = { ...DEFAULTS, ...raw }
  assertParams(p)
  p.hingePinRadius = p.hingePinDiameter / 2
  p.hingeSleeveInnerRadius = p.hingePinRadius + p.hingeRadialClearance
  p.hingeSleeveOuterRadius = p.hingeSleeveInnerRadius + p.hingeSleeveWall
  if (p.hingeSleeveOuterRadius > p.hingeOuterRadius - 0.25) {
    throw new Error('hinge sleeve leaves insufficient radial separation from the outer knuckle envelope')
  }
  p.hingeOuterKnuckleLength = (p.bodyWidth - p.hingeMiddleLength - 2 * p.hingeAxialClearance) / 2
  if (p.hingeOuterKnuckleLength < 5.0) throw new Error('outer hinge knuckles are too short')

  p.hingeCenterX = p.hingeOuterRadius + 1.2
  p.hingeCenterY = 10.5
  p.shellStartX = p.hingeCenterX + p.hingeOuterRadius + 0.65
  p.shellEndX = p.clipLength - 7.0
  p.archEndOuterY = 16.0
  p.lowerRailStartLocalX = p.hingeOuterRadius + 0.85
  p.lowerRailEndLocalX = p.clipLength - p.hingeCenterX - 5.0

  p.armorAcrossFlats = (p.armorEnvelopeWidth - p.armorGap) / 1.5
  p.armorRadius = p.armorAcrossFlats / Math.sqrt(3)
  p.armorPitchZ = (p.armorAcrossFlats + p.armorGap) / 2

  const targetEnvelope = p.clipLength - 1.2
  const envelopeAt = (cellCount, scale) => {
    const radiusX = p.armorRadius * scale
    const pitchX = 3 * radiusX + Math.sqrt(3) * p.armorGap
    return (cellCount - 1) * pitchX + 2 * radiusX
  }
  let longitudinalCells = 1
  while (envelopeAt(longitudinalCells + 1, p.armorMinLongitudinalScale) <= targetEnvelope + 1e-8) longitudinalCells += 1
  longitudinalCells = Math.max(2, longitudinalCells)
  const gapContribution = (longitudinalCells - 1) * Math.sqrt(3) * p.armorGap
  const radiusCoefficient = 3 * (longitudinalCells - 1) + 2
  const fitScale = (targetEnvelope - gapContribution) / (p.armorRadius * radiusCoefficient)
  p.armorLongitudinalScale = clamp(fitScale, p.armorMinLongitudinalScale, p.armorMaxLongitudinalScale)
  p.armorRadiusX = p.armorRadius * p.armorLongitudinalScale
  p.armorPitchX = 3 * p.armorRadiusX + Math.sqrt(3) * p.armorGap
  p.armorCellsPerRow = [longitudinalCells, longitudinalCells - 1, longitudinalCells]
  p.armorGridCenterX = p.clipLength / 2
  p.armorEnvelopeLength = envelopeAt(longitudinalCells, p.armorLongitudinalScale)

  return p
}

function sampledRange (a, b, count) {
  const out = []
  for (let i = 0; i <= count; i++) out.push(a + (b - a) * i / count)
  return out
}

function archOuterY (x, p) {
  const t = clamp((x - p.shellStartX) / (p.shellEndX - p.shellStartX), 0, 1)
  return p.archEndOuterY + p.archRise * Math.sin(Math.PI * t)
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

function cylinderAt (height, radius, x, y, z0, segments) {
  return Manifold.cylinder(height, radius, radius, segments).translate([x, y, z0])
}

function radialStrip (angleDeg, radius0, radius1, thickness, z0, z1, segments) {
  const angle = angleDeg * Math.PI / 180
  const direction = [Math.cos(angle), Math.sin(angle)]
  return extrudePathStrip([
    [radius0 * direction[0], radius0 * direction[1]],
    [radius1 * direction[0], radius1 * direction[1]]
  ], thickness, z0, z1, segments)
}

function rotateTranslateAboutHinge (part, angleDeg, p) {
  return part.rotate([0, 0, angleDeg]).translate([p.hingeCenterX, p.hingeCenterY, 0])
}

function regularHexagon (centerX, centerZ, radius, longitudinalScale) {
  const points = []
  for (let i = 0; i < 6; i++) {
    const angle = i * Math.PI / 3
    points.push([
      centerX + radius * longitudinalScale * Math.cos(angle),
      centerZ + radius * Math.sin(angle)
    ])
  }
  return points
}

function clipPolygonAtMinZ (points, minZ = 0) {
  const clipped = []
  for (let i = 0; i < points.length; i++) {
    const current = points[i]
    const previous = points[(i + points.length - 1) % points.length]
    const currentInside = current[1] >= minZ - 1e-9
    const previousInside = previous[1] >= minZ - 1e-9
    if (currentInside !== previousInside) {
      const t = (minZ - previous[1]) / (current[1] - previous[1])
      clipped.push([previous[0] + t * (current[0] - previous[0]), minZ])
    }
    if (currentInside) clipped.push(current)
  }
  return clipped
}

const dxfPolylineCache = new Map()

function readClosedDxfPolylines (filename) {
  if (dxfPolylineCache.has(filename)) return dxfPolylineCache.get(filename)
  const lines = fs.readFileSync(filename, 'utf8').split(/\r?\n/)
  const polylines = []
  let activePolyline = null
  let activeVertex = null
  const flushVertex = () => {
    if (activePolyline && activeVertex && Number.isFinite(activeVertex.x) && Number.isFinite(activeVertex.y)) {
      activePolyline.push([activeVertex.x, activeVertex.y])
    }
    activeVertex = null
  }
  const flushPolyline = () => {
    flushVertex()
    if (activePolyline && activePolyline.length >= 3) polylines.push(activePolyline)
    activePolyline = null
  }
  for (let i = 0; i + 1 < lines.length; i += 2) {
    const code = lines[i].trim()
    const value = lines[i + 1].trim()
    if (code === '0') {
      if (value === 'POLYLINE') {
        flushPolyline()
        activePolyline = []
      } else if (value === 'VERTEX' && activePolyline) {
        flushVertex()
        activeVertex = { x: NaN, y: NaN }
      } else if (value === 'SEQEND') {
        flushPolyline()
      }
      continue
    }
    if (!activeVertex) continue
    if (code === '10') activeVertex.x = Number(value)
    if (code === '20') activeVertex.y = Number(value)
  }
  flushPolyline()
  if (polylines.length === 0) throw new Error(`no closed polylines found in watermark DXF ${filename}`)
  dxfPolylineCache.set(filename, polylines)
  return polylines
}

function watermarkCellCenter (p) {
  const candidates = armorCellCenters(p).filter(cell => !cell.clippedAtBed)
  candidates.sort((a, b) => {
    const da = Math.abs(a.x - p.armorGridCenterX)
    const db = Math.abs(b.x - p.armorGridCenterX)
    if (Math.abs(da - db) > 1e-9) return da - db
    return b.row - a.row
  })
  if (candidates.length === 0) throw new Error('no complete armor cell is available for the watermark')
  return candidates[0]
}

function watermarkPlacementCenter (p) {
  const cell = watermarkCellCenter(p)
  return { ...cell, z: cell.z + 0.07 }
}

function makeWatermarkCutter (p) {
  const dxfPath = path.join(__dirname, 'assets', 'just-innovation-watermark', 'exports', 'dxf', 'just-innovation-compact.dxf')
  const center = watermarkPlacementCenter(p)
  const contours = readClosedDxfPolylines(dxfPath).map(polyline => polyline.map(([x, z]) => [center.x + x, center.z + z]))
  const cutter = new CrossSection(contours, 'EvenOdd').extrude(p.watermarkDepth + 0.10)
  const warpedCutter = cutter.warp(vertex => {
    const x = vertex[0]
    const z = vertex[1]
    const depth = vertex[2]
    vertex[0] = x
    vertex[1] = archOuterY(x, p) + p.armorRise + 0.05 - depth
    vertex[2] = z
  })
  return { cutter: warpedCutter, center, dxfPath }
}

function armorCellCenters (p) {
  const centers = []
  for (let row = 0; row < 3; row++) {
    const count = p.armorCellsPerRow[row]
    for (let column = 0; column < count; column++) {
      centers.push({
        row,
        column,
        x: p.armorGridCenterX + (column - (count - 1) / 2) * p.armorPitchX,
        z: row * p.armorPitchZ,
        clippedAtBed: row === 0
      })
    }
  }
  return centers
}

function makeArmor (p) {
  const parts = []
  for (const center of armorCellCenters(p)) {
    const wholeFootprint = regularHexagon(center.x, center.z, p.armorRadius, p.armorLongitudinalScale)
    const footprint = center.clippedAtBed ? clipPolygonAtMinZ(wholeFootprint) : wholeFootprint
    parts.push(prismAlongY(
      footprint,
      x => archOuterY(x, p) - p.armorEmbed,
      x => archOuterY(x, p) + p.armorRise
    ))
  }
  return Manifold.union(parts)
}

function makeArchShell (p) {
  const samples = p.quality === 'final' ? 56 : 28
  const xs = sampledRange(p.shellStartX, p.shellEndX, samples)
  const outer = xs.map(x => [x, archOuterY(x, p)])
  const inner = [...xs].reverse().map(x => [x, archInnerY(x, p)])
  return extrudePolygon([...outer, ...inner], 0, p.bodyWidth)
}

function makeUpperHingeAndWeb (p) {
  const segments = p.quality === 'final' ? 48 : 24
  const middleZ0 = p.hingeOuterKnuckleLength + p.hingeAxialClearance
  const sleeveOuter = cylinderAt(
    p.hingeMiddleLength,
    p.hingeSleeveOuterRadius,
    p.hingeCenterX,
    p.hingeCenterY,
    middleZ0,
    segments
  )
  const sleeveBore = cylinderAt(
    p.hingeMiddleLength + 0.4,
    p.hingeSleeveInnerRadius,
    p.hingeCenterX,
    p.hingeCenterY,
    middleZ0 - 0.2,
    segments
  )
  const sleeve = sleeveOuter.subtract(sleeveBore)
  const webX = p.shellStartX + 1.6
  const web = extrudePolygon([
    [p.hingeCenterX + 2.1, p.hingeCenterY + 2.4],
    [webX, archOuterY(webX, p) - 0.2],
    [webX, archInnerY(webX, p) + 0.2],
    [p.hingeCenterX + 2.6, p.hingeCenterY + 1.1]
  ], middleZ0, middleZ0 + p.hingeMiddleLength)
  const stopAngleDeg = p.hingeFullOpenAngleDeg - 105.0
  const stop = radialStrip(stopAngleDeg, p.hingeSleeveOuterRadius - 0.35, 7.0, 1.4, middleZ0, middleZ0 + 2.0, segments)
    .translate([p.hingeCenterX, p.hingeCenterY, 0])
  return Manifold.union(sleeve, web, stop)
}

function makeUpperTeeth (p) {
  const parts = []
  const startX = p.shellStartX + 12.0
  const endX = p.shellEndX - 11.0
  const span = Math.max(12.0, endX - startX)
  const count = Math.max(4, Math.floor(span / 6.0) + 1)
  const pitch = count > 1 ? span / (count - 1) : 0
  for (let i = 0; i < count; i++) {
    const x = startX + i * pitch
    const baseY = archInnerY(x, p) + 0.18
    const length = 4.0 + (i % 2) * 0.65
    parts.push(extrudePolygon([
      [x - 1.65, baseY],
      [x + 1.65, baseY],
      [x + 0.62, baseY - length],
      [x - 0.62, baseY - length]
    ], 0, 12.0))
  }
  return Manifold.union(parts)
}

function makeUpperCatch (p) {
  const topBridge = extrudePolygon([
    [p.shellEndX - 0.8, archInnerY(p.shellEndX, p) - 0.2],
    [p.clipLength, 14.2],
    [p.clipLength, 16.2],
    [p.shellEndX - 0.8, archOuterY(p.shellEndX, p) + 0.2]
  ], 0, 10.8)
  const catchPost = extrudePolygon([
    [p.clipLength - 1.0, 9.3],
    [p.clipLength - 0.4, 9.3],
    [p.clipLength - 0.4, 14.5],
    [p.clipLength - 1.0, 14.5]
  ], 0, 9.8)
  const catchLip = extrudePolygon([
    [p.clipLength - 7.2, 9.3],
    [p.clipLength - 0.8, 9.3],
    [p.clipLength - 0.8, 10.6],
    [p.clipLength - 6.5, 10.6]
  ], 0, 9.8)
  return Manifold.union(topBridge, catchPost, catchLip)
}

function makeUpperBody (p, includeCatch = true) {
  const parts = [
    makeArchShell(p),
    makeArmor(p),
    makeUpperHingeAndWeb(p),
    makeUpperTeeth(p)
  ]
  if (includeCatch) parts.push(makeUpperCatch(p))
  let body = Manifold.union(parts)
  if (p.includeWatermark) body = body.subtract(makeWatermarkCutter(p).cutter).simplify(1e-4)
  return body
}

function railBottomLocalY (u, p) {
  const t = clamp((u - p.lowerRailStartLocalX) / (p.lowerRailEndLocalX - p.lowerRailStartLocalX), 0, 1)
  return -7.0 + 0.25 * t
}

function railTopLocalY (u, p) {
  const t = clamp((u - p.lowerRailStartLocalX) / (p.lowerRailEndLocalX - p.lowerRailStartLocalX), 0, 1)
  return -4.15 + 0.20 * t
}

function railWidthLocal (u, p) {
  const leftFullEnd = p.lowerRailStartLocalX + 4.0
  const leftTaperEnd = leftFullEnd + 5.0
  const rightFullStart = p.lowerRailEndLocalX - 4.0
  const rightTaperStart = rightFullStart - 5.0
  if (u <= leftFullEnd || u >= rightFullStart) return p.bodyWidth
  if (u < leftTaperEnd) return p.bodyWidth + (u - leftFullEnd) * (p.railCentralWidth - p.bodyWidth) / 5.0
  if (u <= rightTaperStart) return p.railCentralWidth
  return p.railCentralWidth + (u - rightTaperStart) * (p.bodyWidth - p.railCentralWidth) / 5.0
}

function makeLowerRailLocal (p) {
  const s = p.lowerRailStartLocalX
  const e = p.lowerRailEndLocalX
  const stations = [s, s + 4, s + 9, e - 9, e - 4, e]
  const sections = []
  for (let i = 0; i < stations.length - 1; i++) {
    const x0 = stations[i]
    const x1 = stations[i + 1]
    sections.push(prismAlongZ([
      [x0, railBottomLocalY(x0, p)],
      [x1, railBottomLocalY(x1, p)],
      [x1, railTopLocalY(x1, p)],
      [x0, railTopLocalY(x0, p)]
    ], x => railWidthLocal(x, p)))
  }
  return Manifold.union(sections)
}

function makeLowerTeethLocal (p) {
  const parts = []
  const start = p.lowerRailStartLocalX + 10.0
  const end = p.lowerRailEndLocalX - 13.0
  const span = Math.max(10.0, end - start)
  const count = Math.max(4, Math.floor(span / 5.7) + 1)
  const pitch = count > 1 ? span / (count - 1) : 0
  for (let i = 0; i < count; i++) {
    const u = start + i * pitch
    const base = railTopLocalY(u, p) - 0.18
    const height = 6.0 + (i % 3) * 0.65
    parts.push(extrudePolygon([
      [u - 1.85, base],
      [u + 1.85, base],
      [u + 0.62, base + height],
      [u - 0.62, base + height]
    ], 0, 12.0))
  }
  return Manifold.union(parts)
}

function makeLowerLatchLocal (p) {
  const e = p.lowerRailEndLocalX
  const referenceLargeEndX = 85.0 - p.hingeCenterX - 5.0
  const closedAngleRad = p.hingeClosedAngleDeg * Math.PI / 180
  const lengthYOffset = -(e - referenceLargeEndX) * Math.tan(closedAngleRad)
  const path = [
    [e - 20.0, railTopLocalY(e - 20.0, p) - 0.85],
    [e - 15.0, -4.25 + 0.20 * lengthYOffset],
    [e - 10.0, -2.7 + 0.50 * lengthYOffset],
    [e - 5.0, 2.2 + 0.80 * lengthYOffset],
    [e - 0.8, 5.65 + lengthYOffset]
  ]
  const tongue = extrudePathStrip(path, p.latchTongueThickness, 0, p.latchWidth, p.quality === 'final' ? 28 : 16)
  const hook = extrudePolygon([
    [e - 1.7, 5.0 + lengthYOffset],
    [e + 3.4, 5.85 + lengthYOffset],
    [e + 3.0, 6.6 + lengthYOffset],
    [e - 1.1, 6.0 + lengthYOffset]
  ], 0, p.latchWidth)
  const thumbPad = extrudePolygon([
    [e - 8.2, 3.8 + lengthYOffset],
    [e - 2.0, 4.7 + lengthYOffset],
    [e - 2.4, 6.35 + lengthYOffset],
    [e - 7.3, 5.65 + lengthYOffset]
  ], 0, p.latchWidth + 2.4)
  return Manifold.union(tongue, hook, thumbPad)
}

function makeLowerHingeLocal (p) {
  const segments = p.quality === 'final' ? 48 : 24
  const lowerKnuckle = cylinderAt(p.hingeOuterKnuckleLength, p.hingeOuterRadius, 0, 0, 0, segments)
  const upperZ0 = p.bodyWidth - p.hingeOuterKnuckleLength
  const upperKnuckle = cylinderAt(p.hingeOuterKnuckleLength, p.hingeOuterRadius, 0, 0, upperZ0, segments)
  const pin = cylinderAt(p.bodyWidth, p.hingePinRadius, 0, 0, 0, segments)
  const connectorPath = [[2.6, -3.15], [p.lowerRailStartLocalX + 1.0, -4.65]]
  const lowerConnector = extrudePathStrip(connectorPath, 2.4, 0, p.hingeOuterKnuckleLength, segments)
  const upperConnector = extrudePathStrip(connectorPath, 2.4, upperZ0, p.bodyWidth, segments)
  const stop = radialStrip(-90.0, p.hingeSleeveOuterRadius + 1.05, 7.0, 1.4, p.hingeOuterKnuckleLength - 0.6, p.hingeOuterKnuckleLength + p.hingeAxialClearance + 1.6, segments)
  return Manifold.union(lowerKnuckle, upperKnuckle, pin, lowerConnector, upperConnector, stop)
}

function makeLowerBodyLocal (p, includeLatch = true) {
  const parts = [
    makeLowerHingeLocal(p),
    makeLowerRailLocal(p),
    makeLowerTeethLocal(p)
  ]
  if (includeLatch) parts.push(makeLowerLatchLocal(p))
  return Manifold.union(parts)
}

function buildAssembly (raw = {}, angleOverride = null) {
  const p = deriveParameters(raw)
  const upper = makeUpperBody(p)
  const lowerLocal = makeLowerBodyLocal(p)
  const angleDeg = angleOverride === null ? p.hingeExportAngleDeg : angleOverride
  const lower = rotateTranslateAboutHinge(lowerLocal, angleDeg, p)
  const assembly = Manifold.union(upper, lower)
  return { p, upper, lowerLocal, lower, assembly, angleDeg }
}

function makeHingeLatchCoupon (raw = {}) {
  const p = deriveParameters(raw)
  const q = { ...p, clipLength: 36.0 }
  const segments = p.quality === 'final' ? 48 : 24
  const middleZ0 = p.hingeOuterKnuckleLength + p.hingeAxialClearance
  const upperSleeve = cylinderAt(p.hingeMiddleLength, p.hingeSleeveOuterRadius, 5.0, 10.0, middleZ0, segments)
    .subtract(cylinderAt(p.hingeMiddleLength + 0.4, p.hingeSleeveInnerRadius, 5.0, 10.0, middleZ0 - 0.2, segments))
  const upperBar = Manifold.cube([23.8, 3.0, p.bodyWidth]).translate([10.0, 12.2, 0])
  const upperWeb = extrudePolygon([[7.2, 11.2], [11.4, 12.5], [11.4, 14.9], [7.1, 13.2]], middleZ0, middleZ0 + p.hingeMiddleLength)
  const couponCatch = Manifold.cube([5.0, 4.0, 9.8]).translate([29.0, 11.2, 0])
  const upper = Manifold.union(upperSleeve, upperBar, upperWeb, couponCatch)

  const outerLower = cylinderAt(p.hingeOuterKnuckleLength, p.hingeOuterRadius, 0, 0, 0, segments)
  const outerUpper = cylinderAt(p.hingeOuterKnuckleLength, p.hingeOuterRadius, 0, 0, p.bodyWidth - p.hingeOuterKnuckleLength, segments)
  const pin = cylinderAt(p.bodyWidth, p.hingePinRadius, 0, 0, 0, segments)
  const lowerBar = Manifold.cube([24.0, 3.0, p.bodyWidth]).translate([4.8, -6.7, 0])
  const connectors = Manifold.union(
    extrudePathStrip([[2.6, -3.1], [6.2, -5.2]], 2.4, 0, p.hingeOuterKnuckleLength, segments),
    extrudePathStrip([[2.6, -3.1], [6.2, -5.2]], 2.4, p.bodyWidth - p.hingeOuterKnuckleLength, p.bodyWidth, segments)
  )
  const tongue = extrudePathStrip([[17.0, -5.2], [22.0, -3.5], [27.0, -0.4], [29.5, 1.0]], p.latchTongueThickness, 0, p.latchWidth, segments)
  const hook = extrudePolygon([[28.3, 0.3], [32.3, 1.1], [31.9, 2.6], [28.0, 1.8]], 0, p.latchWidth)
  const lowerLocal = Manifold.union(outerLower, outerUpper, pin, lowerBar, connectors, tongue, hook)
  const lower = lowerLocal.rotate([0, 0, p.hingeExportAngleDeg]).translate([5.0, 10.0, 0])
  return { assembly: Manifold.union(upper, lower).simplify(1e-5), upper, lower, p: q }
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
  for (let i = 0; i < mesh.numTri; i++) triangles.push([mesh.triVerts[i * 3], mesh.triVerts[i * 3 + 1], mesh.triVerts[i * 3 + 2]])
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

function writeBinaryStl (filename, mesh, label) {
  const out = Buffer.alloc(84 + mesh.triangles.length * 50)
  out.write(label.slice(0, 80), 0, 'ascii')
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

function write3mf (filename, mesh, modelName, releaseState) {
  const vertexXml = mesh.vertices.map(vertex => `        <vertex x="${vertex[0]}" y="${vertex[1]}" z="${vertex[2]}"/>`).join('\n')
  const triangleXml = mesh.triangles.map(triangle => `        <triangle v1="${triangle[0]}" v2="${triangle[1]}" v3="${triangle[2]}"/>`).join('\n')
  const modelXml = `<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <metadata name="Title">${xmlEscape(modelName)}</metadata>
  <metadata name="Designer">OpenAI Codex</metadata>
  <metadata name="Description">${releaseState === 'DRAFT' ? 'DRAFT revision-6 print-in-place hair clip candidate' : 'Final revision-6 print-in-place hair clip'}; two intentionally disconnected moving bodies.</metadata>
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
  <build><item objectid="1"/></build>
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

function writeGeometry (manifold, basename, outputDir, include3mf = false, releaseState = DEFAULTS.releaseState) {
  fs.mkdirSync(outputDir, { recursive: true })
  const mesh = meshData(manifold)
  const stlPath = path.join(outputDir, `${basename}.stl`)
  writeBinaryStl(stlPath, mesh, `${releaseState} honeycomb PETG hair clip r6 ${basename}`)
  let threeMfPath = null
  if (include3mf) {
    threeMfPath = path.join(outputDir, `${basename}.3mf`)
    write3mf(threeMfPath, mesh, basename, releaseState)
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

function angleIntersectionVolumes (upper, lowerLocal, p) {
  const angles = []
  for (let angle = p.hingeFullOpenAngleDeg + 1; angle <= p.hingeClosedAngleDeg - 1; angle += 3) angles.push(angle)
  for (const angle of [p.hingeClosedAngleDeg - 2, p.hingeClosedAngleDeg - 1, p.hingeClosedAngleDeg - 0.5]) {
    if (angle > p.hingeFullOpenAngleDeg && angle < p.hingeClosedAngleDeg && !angles.includes(angle)) angles.push(angle)
  }
  if (!angles.includes(p.hingeExportAngleDeg)) angles.push(p.hingeExportAngleDeg)
  angles.sort((a, b) => a - b)
  return angles.map(angleDeg => {
    const lower = rotateTranslateAboutHinge(lowerLocal, angleDeg, p)
    return { angleDeg, intersectionVolumeMm3: upper.intersect(lower).volume() }
  })
}

function generatePreset (name, raw, outputDir, includeCoupon) {
  const assemblyData = buildAssembly({ ...raw, preset: name })
  const p = assemblyData.p
  const upperKinematicCore = makeUpperBody(p, false)
  const lowerKinematicCore = makeLowerBodyLocal(p, false)
  const kinematicCoreVolumes = angleIntersectionVolumes(upperKinematicCore, lowerKinematicCore, p)
  const latchApproachVolumes = angleIntersectionVolumes(assemblyData.upper, assemblyData.lowerLocal, p)
  const fileStatePrefix = p.releaseState === 'DRAFT' ? 'DRAFT-' : ''
  const prefix = `${fileStatePrefix}masculine-honeycomb-hair-clip-r6-${name.replace('_', '-')}`
  const result = {
    preset: name,
    parameters: {
      clipLengthMm: p.clipLength,
      archRiseMm: p.archRise,
      bodyWidthMm: p.bodyWidth,
      armorEnvelopeWidthMm: p.armorEnvelopeWidth,
      shellThicknessMm: p.shellThickness,
      railCentralWidthMm: p.railCentralWidth
    },
    hinge: {
      type: 'captured-print-in-place-rotational-pivot',
      movingBodyCount: 2,
      pinDiameterMm: p.hingePinDiameter,
      radialClearanceMm: p.hingeRadialClearance,
      diametralClearanceMm: 2 * p.hingeRadialClearance,
      axialClearanceEachSideMm: p.hingeAxialClearance,
      outerKnuckleLengthMm: p.hingeOuterKnuckleLength,
      middleSleeveLengthMm: p.hingeMiddleLength,
      exportedAngleDeg: p.hingeExportAngleDeg,
      fullOpenAngleDeg: p.hingeFullOpenAngleDeg,
      closedAngleDeg: p.hingeClosedAngleDeg,
      usefulTravelDeg: p.hingeClosedAngleDeg - p.hingeFullOpenAngleDeg,
      hardStop: true,
      hardStopContactVolumeAtFullOpenMm3: assemblyData.upper.intersect(rotateTranslateAboutHinge(assemblyData.lowerLocal, p.hingeFullOpenAngleDeg, p)).volume(),
      terminalClosedIntersectionVolumeMm3: assemblyData.upper.intersect(rotateTranslateAboutHinge(assemblyData.lowerLocal, p.hingeClosedAngleDeg, p)).volume(),
      sampledKinematicCoreIntersectionVolumes: kinematicCoreVolumes,
      sampledLatchApproachIntersectionVolumes: latchApproachVolumes.filter(item => item.angleDeg >= p.hingeClosedAngleDeg - 3),
      kinematicCoreCollisionFree: kinematicCoreVolumes.every(item => item.intersectionVolumeMm3 < 1e-6),
      latchSnapDeflectionScreeningMm: 1.0,
      latchCantileverLengthMm: 20.0,
      latchEstimatedOuterFiberStrain: 1.5 * p.latchTongueThickness * 1.0 / (20.0 * 20.0)
    },
    armor: {
      layout: 'three-row-true-staggered-honeycomb-lattice',
      rowCount: 3,
      cellsPerRow: p.armorCellsPerRow,
      totalCellCount: p.armorCellsPerRow.reduce((sum, value) => sum + value, 0),
      buildSideHalfCellCount: p.armorCellsPerRow[0],
      nonBedSideWholeCellCount: p.armorCellsPerRow[2],
      acrossFlatsMm: p.armorAcrossFlats,
      longitudinalScale: p.armorLongitudinalScale,
      pitchXmm: p.armorPitchX,
      pitchZmm: p.armorPitchZ,
      nominalGrooveMm: p.armorGap,
      raisedHeightMm: p.armorRise,
      envelopeLengthMm: p.armorEnvelopeLength,
      envelopeWidthMm: p.armorEnvelopeWidth,
      uniformOrientation: true,
      dedicatedRotatedSideRow: false,
      standaloneEndBlocks: false
    },
    lowerRail: {
      centralWidthMm: p.railCentralWidth,
      fullEndWidthMm: p.bodyWidth
    },
    assembly: writeGeometry(assemblyData.assembly, prefix, outputDir, true, p.releaseState),
    upperBody: {
      connectedBodies: assemblyData.upper.decompose().length,
      volumeMm3: assemblyData.upper.volume()
    },
    lowerBody: {
      connectedBodies: assemblyData.lower.decompose().length,
      volumeMm3: assemblyData.lower.volume()
    },
    watermark: {
      included: p.includeWatermark,
      status: p.includeWatermark
        ? (p.releaseState === 'FINAL' ? 'approved-final-release' : 'release-candidate-pending-user-approval')
        : 'omitted-for-diagnostic-control',
      assetId: p.watermarkAssetId,
      profile: p.watermarkProfile,
      operation: 'recessed',
      depthMm: p.watermarkDepth,
      surface: 'smooth outer face of one complete central honeycomb cell',
      placementCenterXzMm: [watermarkPlacementCenter(p).x, watermarkPlacementCenter(p).z],
      actualEnvelopeMm: [11.4232449531, 10.0],
      selectedSafeRectangleMm: [15.6, 14.0],
      edgeClearanceMm: 2.0,
      residualHostWallMm: 2.9,
      assetPath: 'assets/just-innovation-watermark/exports/dxf/just-innovation-compact.dxf',
      markedPart: 'upper-body armor cell',
      couponCoverage: 'test artifact; intentionally unmarked and covered by the marked product assembly'
    }
  }
  if (includeCoupon) {
    const coupon = makeHingeLatchCoupon(p)
    result.coupon = writeGeometry(coupon.assembly, `${fileStatePrefix}hair-clip-hinge-latch-coupon-r6`, outputDir, false, p.releaseState)
    result.coupon.upperLowerIntersectionVolumeMm3 = coupon.upper.intersect(coupon.lower).volume()
  }
  const metricsPath = path.join(outputDir, `generation-metrics-r6-${name}.json`)
  fs.writeFileSync(metricsPath, JSON.stringify(result, null, 2) + '\n')
  result.metricsPath = metricsPath
  return result
}

function parseNumberArg (name) {
  const prefix = `--${name}=`
  const arg = process.argv.find(value => value.startsWith(prefix))
  if (!arg) return null
  const value = Number(arg.slice(prefix.length))
  if (!Number.isFinite(value)) throw new Error(`${name} must be numeric`)
  return value
}

function main () {
  const quality = process.argv.includes('--preview') ? 'preview' : 'final'
  const releaseState = process.argv.includes('--draft') ? 'DRAFT' : 'FINAL'
  const outputArg = process.argv.find(arg => arg.startsWith('--output-dir='))
  const outputDir = outputArg ? path.resolve(outputArg.slice('--output-dir='.length)) : DEFAULTS.outputDir
  const presetArg = process.argv.find(arg => arg.startsWith('--preset='))
  const preset = presetArg ? presetArg.slice('--preset='.length) : DEFAULTS.preset
  if (!(preset in PRESETS)) throw new Error(`unknown preset ${preset}; choose ${Object.keys(PRESETS).join(', ')}`)
  const raw = {
    ...DEFAULTS,
    ...PRESETS[preset],
    quality,
    releaseState,
    outputDir,
    preset,
    includeWatermark: !process.argv.includes('--without-watermark')
  }
  const clipLength = parseNumberArg('clip-length')
  const archRise = parseNumberArg('arch-rise')
  const hingePinDiameter = parseNumberArg('hinge-pin-diameter')
  const hingeRadialClearance = parseNumberArg('hinge-radial-clearance')
  const hingeAxialClearance = parseNumberArg('hinge-axial-clearance')
  if (clipLength !== null) raw.clipLength = clipLength
  if (archRise !== null) raw.archRise = archRise
  if (hingePinDiameter !== null) raw.hingePinDiameter = hingePinDiameter
  if (hingeRadialClearance !== null) raw.hingeRadialClearance = hingeRadialClearance
  if (hingeAxialClearance !== null) raw.hingeAxialClearance = hingeAxialClearance

  if (process.argv.includes('--all-presets')) {
    const results = {}
    for (const [name, values] of Object.entries(PRESETS)) {
      const presetDir = path.join(outputDir, name)
      results[name] = generatePreset(name, { ...raw, ...values }, presetDir, name === 'large')
    }
    const summaryPath = path.join(outputDir, 'generation-metrics-r6-all-presets.json')
    fs.mkdirSync(outputDir, { recursive: true })
    fs.writeFileSync(summaryPath, JSON.stringify({ revision: 6, releaseState, results }, null, 2) + '\n')
    process.stdout.write(JSON.stringify({ revision: 6, releaseState, summaryPath, presets: Object.keys(results) }, null, 2) + '\n')
    return
  }

  const result = generatePreset(preset, raw, outputDir, true)
  if (process.argv.includes('--diagnostic-poses')) {
    const closed = buildAssembly(raw, raw.hingeClosedAngleDeg)
    const fullOpen = buildAssembly(raw, raw.hingeFullOpenAngleDeg)
    const diagnosticPrefix = releaseState === 'DRAFT' ? 'DRAFT-' : ''
    writeGeometry(closed.assembly, `${diagnosticPrefix}diagnostic-r6-${preset}-closed`, outputDir, false, releaseState)
    writeGeometry(fullOpen.assembly, `${diagnosticPrefix}diagnostic-r6-${preset}-full-open-stop`, outputDir, false, releaseState)
  }
  const diagnosticAngle = parseNumberArg('diagnostic-angle')
  if (diagnosticAngle !== null) {
    const diagnostic = buildAssembly(raw, diagnosticAngle)
    const diagnosticPrefix = releaseState === 'DRAFT' ? 'DRAFT-' : ''
    writeGeometry(diagnostic.assembly, `${diagnosticPrefix}diagnostic-r6-${preset}-angle-${String(diagnosticAngle).replace('.', '_')}`, outputDir, false, releaseState)
  }
  const report = {
    generator: 'hair_clip.mjs',
    kernel: 'Manifold 3D 3.5.1',
    revision: 6,
    releaseState,
    units: 'mm',
    result
  }
  fs.writeFileSync(path.join(outputDir, 'generation-metrics.json'), JSON.stringify(report, null, 2) + '\n')
  process.stdout.write(JSON.stringify(report, null, 2) + '\n')
}

main()
