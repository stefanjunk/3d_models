import fs from 'node:fs'

import { CrossSection } from 'manifold-3d/manifoldCAD'

function pairwiseDxf (text) {
  const lines = text.replace(/\r/g, '').split('\n')
  const pairs = []
  for (let index = 0; index + 1 < lines.length; index += 2) {
    pairs.push([Number(lines[index].trim()), lines[index + 1].trim()])
  }
  return pairs
}

export function parseClosedDxfPolylines (path) {
  const pairs = pairwiseDxf(fs.readFileSync(path, 'utf8'))
  const polygons = []
  let inPolyline = false
  let points = []
  let vertex = null
  const flushVertex = () => {
    if (vertex && Number.isFinite(vertex.x) && Number.isFinite(vertex.y)) points.push([vertex.x, vertex.y])
    vertex = null
  }
  const flushPolyline = () => {
    flushVertex()
    if (points.length >= 3) {
      const first = points[0]
      const last = points[points.length - 1]
      if (Math.hypot(first[0] - last[0], first[1] - last[1]) < 1.0e-7) points.pop()
      polygons.push(points)
    }
    points = []
    inPolyline = false
  }
  for (const [code, value] of pairs) {
    if (code === 0) {
      if (value === 'POLYLINE' || value === 'LWPOLYLINE') {
        if (inPolyline) flushPolyline()
        inPolyline = true
        points = []
      } else if (value === 'VERTEX' && inPolyline) {
        flushVertex()
        vertex = {}
      } else if (value === 'SEQEND' && inPolyline) {
        flushPolyline()
      }
      continue
    }
    if (inPolyline && vertex) {
      if (code === 10) vertex.x = Number(value)
      if (code === 20) vertex.y = Number(value)
    }
  }
  if (inPolyline) flushPolyline()
  if (polygons.length === 0) throw new Error(`No closed DXF polylines found in ${path}`)
  return polygons
}

export function watermarkOutline (path, options) {
  const polygons = parseClosedDxfPolylines(path)
  const all = polygons.flat()
  const min = [Math.min(...all.map(point => point[0])), Math.min(...all.map(point => point[1]))]
  const max = [Math.max(...all.map(point => point[0])), Math.max(...all.map(point => point[1]))]
  let section = CrossSection.ofPolygons(polygons, 'EvenOdd')
  section = section.translate([-(min[0] + max[0]) / 2, -(min[1] + max[1]) / 2])
  if (options.mirror_for_bottom_view) section = section.mirror([1, 0])
  section = section.scale(options.uniform_scale)
  if (options.rotation_deg) section = section.rotate(options.rotation_deg)
  return {
    section,
    source_bounds: { min, max },
    actual_envelope_mm: [(max[0] - min[0]) * options.uniform_scale, (max[1] - min[1]) * options.uniform_scale]
  }
}

export function watermarkCutter (outline, placement, depth, overlap) {
  return outline.section
    .translate([placement[0], placement[1]])
    .extrude(depth + overlap)
    .translate([0, 0, -overlap])
}
