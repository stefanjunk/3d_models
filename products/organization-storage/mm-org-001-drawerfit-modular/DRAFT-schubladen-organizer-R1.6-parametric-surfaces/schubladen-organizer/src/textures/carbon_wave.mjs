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

function signedMeshVolume (properties, triangles) {
  let volume6 = 0
  for (let index = 0; index < triangles.length; index += 3) {
    const ia = 3 * triangles[index]
    const ib = 3 * triangles[index + 1]
    const ic = 3 * triangles[index + 2]
    const ax = properties[ia]
    const ay = properties[ia + 1]
    const az = properties[ia + 2]
    const bx = properties[ib]
    const by = properties[ib + 1]
    const bz = properties[ib + 2]
    const cx = properties[ic]
    const cy = properties[ic + 1]
    const cz = properties[ic + 2]
    volume6 += ax * (by * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - by * cx)
  }
  return volume6 / 6
}

function reverseTriangles (triangles) {
  for (let index = 0; index < triangles.length; index += 3) {
    const swap = triangles[index + 1]
    triangles[index + 1] = triangles[index + 2]
    triangles[index + 2] = swap
  }
}

function orientedTowCutter (cell, overlap, pointAt, normal) {
  const segments = Math.max(12, 2 * Math.round(cell.segments / 2))
  const rings = Math.max(3, Math.round(cell.radialRings))
  const bottomCenter = 0
  const firstRing = 1
  const topRing = firstRing + rings * segments
  const topCenter = topRing + segments
  const properties = new Float32Array((topCenter + 1) * 3)
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

  const c = Math.cos(cell.angle)
  const s = Math.sin(cell.angle)
  const mappedPoint = (localU, localV, offset) => pointAt(
    cell.u + localU * c - localV * s,
    cell.v + localU * s + localV * c,
    offset
  )
  const strandOffset = (localV, envelope) => {
    const across = localV / Math.max(2 * cell.b, EPS) + 0.5
    const ripple = 0.5 + 0.5 * Math.cos(2 * Math.PI * cell.strandCount * across)
    return -(cell.edgeDepth + envelope * (cell.baseDepth + cell.strandDepth * ripple - cell.edgeDepth))
  }

  put(bottomCenter, mappedPoint(0, 0, strandOffset(0, 1)))
  for (let ring = 1; ring <= rings; ring += 1) {
    const radial = ring / rings
    const envelope = Math.pow(Math.max(0, 1 - radial * radial), 1.25)
    for (let segment = 0; segment < segments; segment += 1) {
      const localU = radial * outline[segment][0]
      const localV = radial * outline[segment][1]
      put(
        firstRing + (ring - 1) * segments + segment,
        mappedPoint(localU, localV, strandOffset(localV, envelope))
      )
    }
  }
  for (let segment = 0; segment < segments; segment += 1) {
    put(topRing + segment, mappedPoint(outline[segment][0], outline[segment][1], overlap))
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
  if (!forward) reverseTriangles(triangles)

  if (signedMeshVolume(properties, triangles) < 0) reverseTriangles(triangles)
  return Manifold.ofMesh(new Mesh({
    numProp: 3,
    vertProperties: properties,
    triVerts: new Uint32Array(triangles),
    tolerance: 1.0e-6
  }))
}

function cellFromValues (u, v, angle, orientation, blockKey, config, scale, depthScale) {
  const halfLength = config.tow_length_mm * scale / 2
  const halfWidth = config.tow_width_mm * Math.sqrt(scale) / 2
  const bounds = capsuleBounds(halfLength, halfWidth, angle)
  const baseDepth = (orientation === 'horizontal'
    ? config.horizontal_depth_mm
    : config.vertical_depth_mm) * depthScale
  return {
    u,
    v,
    a: halfLength,
    b: halfWidth,
    boundU: bounds.u,
    boundV: bounds.v,
    angle,
    orientation,
    blockKey,
    baseDepth,
    edgeDepth: config.edge_depth_mm * depthScale,
    strandDepth: config.strand_depth_mm * depthScale,
    strandCount: config.strand_count,
    segments: config.segments,
    radialRings: config.radial_rings
  }
}

function basketCellsForPatch (patch, surfaceConfig) {
  const config = surfaceConfig.weave
  const scale = patch.pitchScale ?? 1
  const depthScale = patch.depthScale ?? 1
  const cellPitch = config.cell_pitch_mm * scale
  const blockPitch = 2 * cellPitch
  const offsetU = config.offset_u_mm * scale
  const offsetV = config.offset_v_mm * scale
  const bx0 = Math.floor((patch.u0 - offsetU) / blockPitch) - 1
  const bx1 = Math.ceil((patch.u1 - offsetU) / blockPitch) + 1
  const by0 = Math.floor((patch.v0 - offsetV) / blockPitch) - 1
  const by1 = Math.ceil((patch.v1 - offsetV) / blockPitch) + 1
  const cells = []

  for (let by = by0; by <= by1; by += 1) {
    for (let bx = bx0; bx <= bx1; bx += 1) {
      const horizontal = positiveModulo(bx + by + config.phase_blocks, 2) === 0
      const orientation = horizontal ? 'horizontal' : 'vertical'
      const angle = horizontal ? 0 : Math.PI / 2
      const blockU = offsetU + bx * blockPitch
      const blockV = offsetV + by * blockPitch
      const blockKey = `${bx}:${by}`
      for (let lane = 0; lane < 2; lane += 1) {
        const u = horizontal ? blockU + blockPitch / 2 : blockU + (lane + 0.5) * cellPitch
        const v = horizontal ? blockV + (lane + 0.5) * cellPitch : blockV + blockPitch / 2
        const cell = cellFromValues(u, v, angle, orientation, blockKey, config, scale, depthScale)
        if (cellFitsPatch(cell, patch, surfaceConfig.edge_margin_mm)) cells.push(cell)
      }
    }
  }
  return cells
}

function centerlineCellsForPatch (patch, surfaceConfig) {
  const config = surfaceConfig.weave
  const scale = patch.pitchScale ?? 1
  const depthScale = patch.depthScale ?? 1
  const alongV = patch.grainAxis === 'v'
  const along0 = alongV ? patch.v0 : patch.u0
  const along1 = alongV ? patch.v1 : patch.u1
  const cross = alongV ? (patch.u0 + patch.u1) / 2 : (patch.v0 + patch.v1) / 2
  const repeat = 2 * config.cell_pitch_mm * scale
  const offset = config.offset_u_mm * scale
  const first = Math.floor((along0 - offset) / repeat) - 1
  const last = Math.ceil((along1 - offset) / repeat) + 1
  const cells = []
  for (let index = first; index <= last; index += 1) {
    const along = offset + (index + 0.5) * repeat
    const cell = cellFromValues(
      alongV ? cross : along,
      alongV ? along : cross,
      alongV ? Math.PI / 2 : 0,
      'horizontal',
      `center:${index}`,
      config,
      scale,
      depthScale * (positiveModulo(index + config.phase_blocks, 2) === 0 ? 1 : 0.72)
    )
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
      stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, tow_cells: 0, weave_blocks: 0, horizontal_cells: 0, vertical_cells: 0 }
    }
  }
  const cells = patch.centerGrain
    ? centerlineCellsForPatch(patch, surfaceConfig)
    : basketCellsForPatch(patch, surfaceConfig)
  const cutters = cells.map(cell => orientedTowCutter(
    cell,
    textureConfig.boolean_overlap_mm,
    patch.pointAt,
    patch.normal
  ))
  const combined = balancedUnionAndDispose(cutters, textureConfig.memory_strategy.feature_union_batch)
  if (!combined) {
    return {
      shape,
      stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, tow_cells: 0, weave_blocks: 0, horizontal_cells: 0, vertical_cells: 0 }
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
      weave_blocks: new Set(cells.map(cell => cell.blockKey)).size,
      horizontal_cells: cells.filter(cell => cell.orientation === 'horizontal').length,
      vertical_cells: cells.filter(cell => cell.orientation === 'vertical').length,
      depth_min_mm: Math.min(...cells.map(cell => cell.baseDepth)),
      depth_max_mm: Math.max(...cells.map(cell => cell.baseDepth + cell.strandDepth))
    }
  }
}

export function summarizeTextureStats (patchStats) {
  const bySurface = {}
  for (const stat of patchStats) {
    const entry = bySurface[stat.surface] ?? {
      patches: 0,
      tow_cells: 0,
      weave_blocks: 0,
      horizontal_cells: 0,
      vertical_cells: 0,
      depth_min_mm: null,
      depth_max_mm: 0
    }
    entry.patches += 1
    entry.tow_cells += stat.tow_cells
    entry.weave_blocks += stat.weave_blocks
    entry.horizontal_cells += stat.horizontal_cells
    entry.vertical_cells += stat.vertical_cells
    if (stat.tow_cells > 0) {
      entry.depth_min_mm = entry.depth_min_mm === null ? stat.depth_min_mm : Math.min(entry.depth_min_mm, stat.depth_min_mm)
      entry.depth_max_mm = Math.max(entry.depth_max_mm, stat.depth_max_mm)
    }
    bySurface[stat.surface] = entry
  }
  return {
    representation: patchStats[0]?.representation ?? 'deterministic-reference-basket-weave-tow-cell-field',
    patches: patchStats.length,
    tow_cells: patchStats.reduce((sum, stat) => sum + stat.tow_cells, 0),
    weave_blocks: patchStats.reduce((sum, stat) => sum + stat.weave_blocks, 0),
    horizontal_cells: patchStats.reduce((sum, stat) => sum + stat.horizontal_cells, 0),
    vertical_cells: patchStats.reduce((sum, stat) => sum + stat.vertical_cells, 0),
    by_surface: bySurface
  }
}
