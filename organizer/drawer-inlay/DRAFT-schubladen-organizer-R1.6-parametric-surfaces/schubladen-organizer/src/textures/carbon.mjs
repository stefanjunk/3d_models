import { Manifold, Mesh } from 'manifold-3d/manifoldCAD'

const EPS = 1.0e-6

function positiveModulo (value, divisor) {
  return ((value % divisor) + divisor) % divisor
}

function capsuleBounds (halfLength, halfWidth, angle) {
  const straight = Math.max(0, halfLength - halfWidth)
  return {
    u: straight * Math.abs(Math.cos(angle)) + halfWidth,
    v: straight * Math.abs(Math.sin(angle)) + halfWidth
  }
}

function overlapsRect (cell, rect) {
  return cell.u + cell.boundU > rect.u0 - EPS &&
    cell.u - cell.boundU < rect.u1 + EPS &&
    cell.v + cell.boundV > rect.v0 - EPS &&
    cell.v - cell.boundV < rect.v1 + EPS
}

function cellFitsPatch (cell, patch, edgeMargin) {
  if (cell.u - cell.boundU < patch.u0 + edgeMargin) return false
  if (cell.u + cell.boundU > patch.u1 - edgeMargin) return false
  if (cell.v - cell.boundV < patch.v0 + edgeMargin) return false
  if (cell.v + cell.boundV > patch.v1 - edgeMargin) return false
  return !(patch.keepouts ?? []).some(rect => overlapsRect(cell, rect))
}

function orientedLenticularCutter (cell, overlap, pointAt, normal) {
  const segments = Math.max(12, Math.round(cell.segments))
  const rings = Math.max(2, Math.round(cell.radialRings))
  const bottomCenter = 0
  const firstRing = 1
  const topRing = firstRing + rings * segments
  const topCenter = topRing + segments
  const vertexCount = topCenter + 1
  const properties = new Float32Array(vertexCount * 3)
  const put = (index, point) => {
    properties[index * 3] = point[0]
    properties[index * 3 + 1] = point[1]
    properties[index * 3 + 2] = point[2]
  }
  const halfCapSegments = segments / 2
  const straight = Math.max(0, cell.a - cell.b)
  const outline = []
  for (let segment = 0; segment < halfCapSegments; segment += 1) {
    const theta = -Math.PI / 2 + Math.PI * segment / halfCapSegments
    outline.push([straight + cell.b * Math.cos(theta), cell.b * Math.sin(theta)])
  }
  for (let segment = 0; segment < halfCapSegments; segment += 1) {
    const theta = Math.PI / 2 + Math.PI * segment / halfCapSegments
    outline.push([-straight + cell.b * Math.cos(theta), cell.b * Math.sin(theta)])
  }
  const rotatedPoint = (radial, segment, offset) => {
    const localU = radial * outline[segment][0]
    const localV = radial * outline[segment][1]
    const c = Math.cos(cell.angle)
    const s = Math.sin(cell.angle)
    return pointAt(
      cell.u + localU * c - localV * s,
      cell.v + localU * s + localV * c,
      offset
    )
  }

  put(bottomCenter, pointAt(cell.u, cell.v, -cell.depth))
  for (let ring = 1; ring <= rings; ring += 1) {
    const radial = ring / rings
    const lenticular = Math.pow(Math.max(0, 1 - radial * radial), 1.35)
    const offset = -cell.depth * lenticular
    for (let segment = 0; segment < segments; segment += 1) {
      put(firstRing + (ring - 1) * segments + segment, rotatedPoint(radial, segment, offset))
    }
  }
  for (let segment = 0; segment < segments; segment += 1) {
    put(topRing + segment, rotatedPoint(1, segment, overlap))
  }
  put(topCenter, pointAt(cell.u, cell.v, overlap))

  const triangles = []
  const push = (a, b, c) => triangles.push(a, b, c)
  for (let segment = 0; segment < segments; segment += 1) {
    const next = (segment + 1) % segments
    push(bottomCenter, firstRing + next, firstRing + segment)
  }
  for (let ring = 1; ring < rings; ring += 1) {
    const inner = firstRing + (ring - 1) * segments
    const outer = firstRing + ring * segments
    for (let segment = 0; segment < segments; segment += 1) {
      const next = (segment + 1) % segments
      push(inner + segment, inner + next, outer + next)
      push(inner + segment, outer + next, outer + segment)
    }
  }
  const bottomOuter = firstRing + (rings - 1) * segments
  for (let segment = 0; segment < segments; segment += 1) {
    const next = (segment + 1) % segments
    push(bottomOuter + segment, bottomOuter + next, topRing + next)
    push(bottomOuter + segment, topRing + next, topRing + segment)
    push(topCenter, topRing + segment, topRing + next)
  }

  const origin = pointAt(cell.u, cell.v, 0)
  const pointU = pointAt(cell.u + 1, cell.v, 0)
  const pointV = pointAt(cell.u, cell.v + 1, 0)
  const cross = [
    (pointU[1] - origin[1]) * (pointV[2] - origin[2]) - (pointU[2] - origin[2]) * (pointV[1] - origin[1]),
    (pointU[2] - origin[2]) * (pointV[0] - origin[0]) - (pointU[0] - origin[0]) * (pointV[2] - origin[2]),
    (pointU[0] - origin[0]) * (pointV[1] - origin[1]) - (pointU[1] - origin[1]) * (pointV[0] - origin[0])
  ]
  const forward = cross[0] * normal[0] + cross[1] * normal[1] + cross[2] * normal[2] > 0
  if (!forward) {
    for (let index = 0; index < triangles.length; index += 3) {
      const swap = triangles[index + 1]
      triangles[index + 1] = triangles[index + 2]
      triangles[index + 2] = swap
    }
  }
  return Manifold.ofMesh(new Mesh({
    numProp: 3,
    vertProperties: properties,
    triVerts: new Uint32Array(triangles),
    tolerance: 1.0e-6
  }))
}

function standardCellsForPatch (patch, surfaceConfig) {
  const twill = surfaceConfig.twill
  const pitchScale = patch.pitchScale ?? 1
  const pitch = twill.pitch_mm * pitchScale
  const angle = twill.angle_deg * Math.PI / 180
  const halfLength = twill.tow_length_mm * pitchScale / 2
  const halfWidth = twill.tow_width_mm * Math.sqrt(pitchScale) / 2
  const cells = []
  const ix0 = Math.floor(patch.u0 / pitch) - 1
  const ix1 = Math.ceil(patch.u1 / pitch) + 1
  const iy0 = Math.floor(patch.v0 / pitch) - 1
  const iy1 = Math.ceil(patch.v1 / pitch) + 1
  for (let iy = iy0; iy <= iy1; iy += 1) {
    for (let ix = ix0; ix <= ix1; ix += 1) {
      const phase = positiveModulo(ix - iy + twill.phase_cells, 4)
      const over = phase < 2
      const cellAngle = over ? angle : -angle
      const bounds = capsuleBounds(halfLength, halfWidth, cellAngle)
      const cell = {
        u: (ix + 0.5) * pitch,
        v: (iy + 0.5) * pitch,
        a: halfLength,
        b: halfWidth,
        boundU: bounds.u,
        boundV: bounds.v,
        angle: cellAngle,
        depth: (over ? twill.over_depth_mm : twill.under_depth_mm) * (patch.depthScale ?? 1),
        layer: over ? 'over' : 'under',
        segments: twill.segments,
        radialRings: twill.radial_rings
      }
      if (cellFitsPatch(cell, patch, surfaceConfig.edge_margin_mm)) cells.push(cell)
    }
  }
  return cells
}

function centerlineCellsForPatch (patch, surfaceConfig) {
  const twill = surfaceConfig.twill
  const alongV = patch.grainAxis === 'v'
  const along0 = alongV ? patch.v0 : patch.u0
  const along1 = alongV ? patch.v1 : patch.u1
  const cross = alongV ? (patch.u0 + patch.u1) / 2 : (patch.v0 + patch.v1) / 2
  const pitch = twill.pitch_mm * (patch.pitchScale ?? 1)
  const baseAngle = twill.angle_deg * Math.PI / 180
  const halfLength = twill.tow_length_mm * (patch.pitchScale ?? 1) / 2
  const halfWidth = twill.tow_width_mm * Math.sqrt(patch.pitchScale ?? 1) / 2
  const cells = []
  const first = Math.floor(along0 / pitch) - 1
  const last = Math.ceil(along1 / pitch) + 1
  for (let index = first; index <= last; index += 1) {
    const phase = positiveModulo(index + twill.phase_cells, 4)
    const over = phase < 2
    const relativeAngle = over ? baseAngle : -baseAngle
    const angle = alongV ? Math.PI / 2 + relativeAngle : relativeAngle
    const bounds = capsuleBounds(halfLength, halfWidth, angle)
    const cell = {
      u: alongV ? cross : (index + 0.5) * pitch,
      v: alongV ? (index + 0.5) * pitch : cross,
      a: halfLength,
      b: halfWidth,
      boundU: bounds.u,
      boundV: bounds.v,
      angle,
      depth: (over ? twill.over_depth_mm : twill.under_depth_mm) * (patch.depthScale ?? 1),
      layer: over ? 'over' : 'under',
      segments: twill.segments,
      radialRings: twill.radial_rings
    }
    if (cellFitsPatch(cell, patch, surfaceConfig.edge_margin_mm)) cells.push(cell)
  }
  return cells
}

function balancedUnionAndDispose (items, batchSize) {
  let queue = items.filter(Boolean)
  if (queue.length === 0) return null
  while (queue.length > 1) {
    const next = []
    for (let index = 0; index < queue.length; index += batchSize) {
      const batch = queue.slice(index, index + batchSize)
      if (batch.length === 1) next.push(batch[0])
      else {
        const combined = Manifold.union(batch)
        for (const item of batch) item.delete()
        next.push(combined)
      }
    }
    queue = next
  }
  return queue[0]
}

export function applyProceduralTexturePatch (shape, patch, surfaceName, textureConfig) {
  const surfaceConfig = textureConfig.surfaces[surfaceName]
  if (!textureConfig.enabled || !surfaceConfig?.enabled) {
    return {
      shape,
      stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, tow_cells: 0, over_cells: 0, under_cells: 0 }
    }
  }
  const cells = patch.centerGrain
    ? centerlineCellsForPatch(patch, surfaceConfig)
    : standardCellsForPatch(patch, surfaceConfig)
  const cutters = cells.map(cell => orientedLenticularCutter(
    cell,
    textureConfig.boolean_overlap_mm,
    patch.pointAt,
    patch.normal
  ))
  const combined = balancedUnionAndDispose(cutters, textureConfig.memory_strategy.feature_union_batch)
  if (!combined) {
    return {
      shape,
      stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, tow_cells: 0, over_cells: 0, under_cells: 0 }
    }
  }
  const result = shape.subtract(combined)
  shape.delete()
  combined.delete()
  return {
    shape: result,
    stats: {
      representation: textureConfig.representation,
      surface: surfaceName,
      key: patch.key,
      tow_cells: cells.length,
      over_cells: cells.filter(cell => cell.layer === 'over').length,
      under_cells: cells.filter(cell => cell.layer === 'under').length,
      depth_min_mm: Math.min(...cells.map(cell => cell.depth)),
      depth_max_mm: Math.max(...cells.map(cell => cell.depth))
    }
  }
}

export function summarizeTextureStats (patchStats) {
  const bySurface = {}
  for (const stat of patchStats) {
    const entry = bySurface[stat.surface] ?? {
      patches: 0,
      tow_cells: 0,
      over_cells: 0,
      under_cells: 0,
      depth_min_mm: null,
      depth_max_mm: 0
    }
    entry.patches += 1
    entry.tow_cells += stat.tow_cells
    entry.over_cells += stat.over_cells
    entry.under_cells += stat.under_cells
    if (stat.tow_cells > 0) {
      entry.depth_min_mm = entry.depth_min_mm === null ? stat.depth_min_mm : Math.min(entry.depth_min_mm, stat.depth_min_mm)
      entry.depth_max_mm = Math.max(entry.depth_max_mm, stat.depth_max_mm)
    }
    bySurface[stat.surface] = entry
  }
  return {
    representation: patchStats[0]?.representation ?? 'deterministic-2x2-twill-lenticular-cell-field',
    patches: patchStats.length,
    tow_cells: patchStats.reduce((sum, stat) => sum + stat.tow_cells, 0),
    over_cells: patchStats.reduce((sum, stat) => sum + stat.over_cells, 0),
    under_cells: patchStats.reduce((sum, stat) => sum + stat.under_cells, 0),
    by_surface: bySurface
  }
}
