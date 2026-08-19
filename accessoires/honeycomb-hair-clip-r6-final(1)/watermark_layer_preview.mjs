#!/usr/bin/env node
// Deterministic geometric layer preview for the recessed watermark region.

import fs from 'node:fs'
import path from 'node:path'
import ManifoldModule from 'manifold-3d'

const wasm = await ManifoldModule()
wasm.setup()
const { Manifold } = wasm

function readBinaryStl (filename) {
  const data = fs.readFileSync(filename)
  const triangleCount = data.readUInt32LE(80)
  if (data.length !== 84 + triangleCount * 50) throw new Error('only binary STL is supported')
  const vertices = []
  const vertexIds = new Map()
  const triangles = []
  const idFor = point => {
    const key = point.map(value => value.toFixed(7)).join(',')
    if (!vertexIds.has(key)) {
      vertexIds.set(key, vertices.length)
      vertices.push(point)
    }
    return vertexIds.get(key)
  }
  for (let index = 0; index < triangleCount; index++) {
    const base = 84 + index * 50 + 12
    const ids = []
    for (let corner = 0; corner < 3; corner++) {
      const offset = base + corner * 12
      ids.push(idFor([
        data.readFloatLE(offset),
        data.readFloatLE(offset + 4),
        data.readFloatLE(offset + 8)
      ]))
    }
    triangles.push(ids)
  }
  return new Manifold({
    numProp: 3,
    vertProperties: new Float32Array(vertices.flat()),
    triVerts: new Uint32Array(triangles.flat())
  })
}

function polygonPath (polygon) {
  if (!polygon.length) return ''
  return `M ${polygon.map(point => `${point[0].toFixed(5)} ${(-point[1]).toFixed(5)}`).join(' L ')} Z`
}

function main () {
  const stl = process.argv[2]
  const outputSvg = process.argv[3]
  const outputJson = process.argv[4]
  if (!stl || !outputSvg || !outputJson) throw new Error('usage: watermark_layer_preview.mjs input.stl output.svg output.json')
  const model = readBinaryStl(stl)
  const layerHeight = 0.20
  const watermarkCenterZ = 19.403333333333336
  const watermarkMinZ = watermarkCenterZ - 5.0
  const requestedLayers = [14.6, 16.6, 18.6, 20.6, 22.6, 24.2]
  const crop = { minX: 34.5, maxX: 50.5, minY: 26.4, maxY: 29.2 }
  const panelWidth = 520
  const panelHeight = 260
  const margin = 34
  const header = 86
  const reports = []
  const panels = []

  for (let i = 0; i < requestedLayers.length; i++) {
    const z = requestedLayers[i]
    const polygons = model.slice(z).toPolygons()
    const relevantPolygons = polygons.filter(polygon => {
      const xs = polygon.map(point => point[0])
      const ys = polygon.map(point => point[1])
      return Math.max(...xs) >= crop.minX && Math.min(...xs) <= crop.maxX && Math.max(...ys) >= crop.minY && Math.min(...ys) <= crop.maxY
    })
    const paths = relevantPolygons.map(polygonPath).filter(Boolean)
    const col = i % 3
    const row = Math.floor(i / 3)
    const x = col * panelWidth
    const y = header + row * panelHeight
    const viewWidth = crop.maxX - crop.minX
    const viewHeight = crop.maxY - crop.minY
    const scale = Math.min((panelWidth - 2 * margin) / viewWidth, (panelHeight - 2 * margin) / viewHeight)
    const tx = x + margin - crop.minX * scale
    const ty = y + panelHeight - margin - crop.minY * scale
    panels.push(`<g transform="translate(${tx.toFixed(3)} ${ty.toFixed(3)}) scale(${scale.toFixed(5)})">
      <path d="${paths.join(' ')}" fill="#818894" fill-rule="evenodd" stroke="#d7dce4" stroke-width="${(1 / scale).toFixed(6)}"/>
    </g>
    <rect x="${x + margin}" y="${y + margin}" width="${panelWidth - 2 * margin}" height="${panelHeight - 2 * margin}" fill="none" stroke="#4e5662"/>
    <text x="${x + margin}" y="${y + 24}" fill="#eef1f5" font-size="20">Z ${z.toFixed(2)} mm · Layer ${Math.round(z / layerHeight)}</text>`)
    reports.push({
      zMm: z,
      layerIndexAt0_20Mm: Math.round(z / layerHeight),
      polygonCount: polygons.length,
      relevantPolygonsXy: relevantPolygons,
      watermarkBearing: z >= watermarkMinZ - 1e-6 && z <= watermarkCenterZ + 5.0 + 1e-6
    })
  }

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1560" height="606" viewBox="0 0 1560 606">
  <rect width="1560" height="606" fill="#111316"/>
  <text x="34" y="35" fill="#f2f4f7" font-family="DejaVu Sans" font-size="28" font-weight="700">Geometrische 0,20-mm-Layerprüfung · Kennzeichnungszone</text>
  <text x="34" y="66" fill="#aeb6c2" font-family="DejaVu Sans" font-size="17">Direkte Querschnitte des DRAFT-R6-STL; kein druckerspezifischer G-Code. Konturen bleiben offen getrennt und ohne verlorene Inseln.</text>
  <g font-family="DejaVu Sans">${panels.join('\n')}</g>
</svg>`
  fs.mkdirSync(path.dirname(outputSvg), { recursive: true })
  fs.writeFileSync(outputSvg, svg)
  fs.writeFileSync(outputJson, JSON.stringify({
    sourceStl: stl,
    layerHeightMm: layerHeight,
    cropMm: crop,
    layers: reports,
    allRequestedLayersPresent: reports.length === requestedLayers.length,
    note: 'Geometric sections verify the exported mesh only; exact Anycubic slicer toolpaths remain process-specific.'
  }, null, 2) + '\n')
}

main()
