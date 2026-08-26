import { Manifold, Mesh } from 'manifold-3d/manifoldCAD'

const EPS = 1.0e-6

function hash32 (value) {
  let hash = 2166136261
  const text = String(value)
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  hash += hash << 13
  hash ^= hash >>> 7
  hash += hash << 3
  hash ^= hash >>> 17
  hash += hash << 5
  return hash >>> 0
}

function random01 (seed, key, scale, ix, iy) {
  return hash32(`${seed}|${key}|${scale}|${ix}|${iy}`) / 0x100000000
}

function clamp01 (value) {
  return Math.max(0, Math.min(1, value))
}

function smoothstep (value) {
  const t = clamp01(value)
  return t * t * (3 - 2 * t)
}

function valueNoise (seed, key, u, v, scale) {
  const x = u / scale
  const y = v / scale
  const ix = Math.floor(x)
  const iy = Math.floor(y)
  const fx = smoothstep(x - ix)
  const fy = smoothstep(y - iy)
  const n00 = random01(seed, key, scale, ix, iy)
  const n10 = random01(seed, key, scale, ix + 1, iy)
  const n01 = random01(seed, key, scale, ix, iy + 1)
  const n11 = random01(seed, key, scale, ix + 1, iy + 1)
  const nx0 = n00 + (n10 - n00) * fx
  const nx1 = n01 + (n11 - n01) * fx
  return nx0 + (nx1 - nx0) * fy
}

function distanceOutsideRect (u, v, rect) {
  const du = Math.max(rect.u0 - u, 0, u - rect.u1)
  const dv = Math.max(rect.v0 - v, 0, v - rect.v1)
  return Math.hypot(du, dv)
}

function edgeDistance (u, v, patch) {
  let distance = Math.min(u - patch.u0, patch.u1 - u, v - patch.v0, patch.v1 - v)
  for (const rect of patch.keepouts ?? []) distance = Math.min(distance, distanceOutsideRect(u, v, rect))
  return Math.max(0, distance)
}

function heightAt (u, v, patch, surfaceConfig, textureConfig) {
  const field = surfaceConfig.field
  const continuity = patch.continuityKey ?? patch.key
  const coarse = valueNoise(textureConfig.seed, continuity, u, v, field.coarse_scale_mm)
  const fine = valueNoise(textureConfig.seed + 101, continuity, u, v, field.fine_scale_mm)
  const cellPitch = field.cell_pitch_mm * (patch.pitchScale ?? 1)
  const node = random01(
    textureConfig.seed + 211,
    continuity,
    'facet-node',
    Math.round(u / cellPitch),
    Math.round(v / cellPitch)
  )
  const fineWeight = 1 - field.coarse_weight - field.node_weight
  const mixed = field.coarse_weight * coarse + fineWeight * fine + field.node_weight * node
  const raw = field.height_min_mm + (field.height_max_mm - field.height_min_mm) * mixed
  const fade = smoothstep(edgeDistance(u, v, patch) / field.fade_distance_mm)
  const height = field.edge_height_mm + (raw - field.edge_height_mm) * fade
  return height * (patch.depthScale ?? 1)
}

function tileOverlapsKeepout (u0, u1, v0, v1, keepouts, clearance) {
  return keepouts.some(rect =>
    u1 > rect.u0 - clearance + EPS && u0 < rect.u1 + clearance - EPS &&
    v1 > rect.v0 - clearance + EPS && v0 < rect.v1 + clearance - EPS
  )
}

function reverseTriangles (triangles) {
  for (let index = 0; index < triangles.length; index += 3) {
    const swap = triangles[index + 1]
    triangles[index + 1] = triangles[index + 2]
    triangles[index + 2] = swap
  }
}

function orientedFacetTile (tile, embed, pointAt, normal) {
  const properties = new Float32Array(8 * 3)
  const put = (index, point) => {
    properties[index * 3] = point[0]
    properties[index * 3 + 1] = point[1]
    properties[index * 3 + 2] = point[2]
  }
  put(0, pointAt(tile.u0, tile.v0, tile.h00))
  put(1, pointAt(tile.u1, tile.v0, tile.h10))
  put(2, pointAt(tile.u1, tile.v1, tile.h11))
  put(3, pointAt(tile.u0, tile.v1, tile.h01))
  put(4, pointAt(tile.u0, tile.v0, -embed))
  put(5, pointAt(tile.u1, tile.v0, -embed))
  put(6, pointAt(tile.u1, tile.v1, -embed))
  put(7, pointAt(tile.u0, tile.v1, -embed))

  const triangles = tile.parity === 0
    ? [0, 1, 2, 0, 2, 3]
    : [0, 1, 3, 1, 2, 3]
  triangles.push(
    4, 6, 5, 4, 7, 6,
    0, 4, 5, 0, 5, 1,
    1, 5, 6, 1, 6, 2,
    2, 6, 7, 2, 7, 3,
    3, 7, 4, 3, 4, 0
  )

  const origin = pointAt(tile.u0, tile.v0, 0)
  const pointU = pointAt(tile.u0 + 1, tile.v0, 0)
  const pointV = pointAt(tile.u0, tile.v0 + 1, 0)
  const cross = [
    (pointU[1] - origin[1]) * (pointV[2] - origin[2]) - (pointU[2] - origin[2]) * (pointV[1] - origin[1]),
    (pointU[2] - origin[2]) * (pointV[0] - origin[0]) - (pointU[0] - origin[0]) * (pointV[2] - origin[2]),
    (pointU[0] - origin[0]) * (pointV[1] - origin[1]) - (pointU[1] - origin[1]) * (pointV[0] - origin[0])
  ]
  const forward = cross[0] * normal[0] + cross[1] * normal[1] + cross[2] * normal[2] > 0
  if (!forward) reverseTriangles(triangles)

  return Manifold.ofMesh(new Mesh({
    numProp: 3,
    vertProperties: properties,
    triVerts: new Uint32Array(triangles),
    tolerance: 1.0e-6
  }))
}

function facetsForPatch (patch, surfaceConfig, textureConfig) {
  const field = surfaceConfig.field
  const pitch = field.cell_pitch_mm * (patch.pitchScale ?? 1)
  const margin = surfaceConfig.edge_margin_mm ?? 0
  const ix0 = Math.ceil((patch.u0 + margin) / pitch)
  const ix1 = Math.floor((patch.u1 - margin) / pitch) - 1
  const iy0 = Math.ceil((patch.v0 + margin) / pitch)
  const iy1 = Math.floor((patch.v1 - margin) / pitch) - 1
  const facets = []
  for (let iy = iy0; iy <= iy1; iy += 1) {
    for (let ix = ix0; ix <= ix1; ix += 1) {
      const u0 = ix * pitch
      const u1 = (ix + 1) * pitch
      const v0 = iy * pitch
      const v1 = (iy + 1) * pitch
      if (tileOverlapsKeepout(u0, u1, v0, v1, patch.keepouts ?? [], field.keepout_clearance_mm)) continue
      facets.push({
        u0,
        u1,
        v0,
        v1,
        h00: heightAt(u0, v0, patch, surfaceConfig, textureConfig),
        h10: heightAt(u1, v0, patch, surfaceConfig, textureConfig),
        h11: heightAt(u1, v1, patch, surfaceConfig, textureConfig),
        h01: heightAt(u0, v1, patch, surfaceConfig, textureConfig),
        parity: random01(
          textureConfig.seed + 313,
          patch.continuityKey ?? patch.key,
          'facet-diagonal',
          ix,
          iy
        ) < 0.5 ? 0 : 1
      })
    }
  }
  return facets
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
    return { shape, stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, facets: 0 } }
  }
  const facets = facetsForPatch(patch, surfaceConfig, textureConfig)
  const solids = facets.map(facet => orientedFacetTile(facet, textureConfig.embed_mm, patch.pointAt, patch.normal))
  const combined = balancedUnionAndDispose(solids, textureConfig.memory_strategy.facet_union_batch)
  if (!combined) {
    return { shape, stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, facets: 0 } }
  }
  const result = shape.add(combined)
  shape.delete()
  combined.delete()
  const heights = facets.flatMap(item => [item.h00, item.h10, item.h11, item.h01])
  return {
    shape: result,
    stats: {
      representation: textureConfig.representation,
      operation: surfaceConfig.operation,
      surface: surfaceName,
      key: patch.key,
      facets: facets.length,
      height_min_mm: Math.min(...heights),
      height_max_mm: Math.max(...heights)
    }
  }
}

export function summarizeTextureStats (patchStats) {
  const bySurface = {}
  for (const stat of patchStats) {
    const entry = bySurface[stat.surface] ?? { patches: 0, facets: 0, height_min_mm: null, height_max_mm: 0 }
    entry.patches += 1
    entry.facets += stat.facets
    if (stat.facets > 0) {
      entry.height_min_mm = entry.height_min_mm === null ? stat.height_min_mm : Math.min(entry.height_min_mm, stat.height_min_mm)
      entry.height_max_mm = Math.max(entry.height_max_mm, stat.height_max_mm)
    }
    bySurface[stat.surface] = entry
  }
  return {
    representation: patchStats[0]?.representation ?? 'deterministic-additive-band-limited-micro-cast-facet-field',
    operation: 'additive-raised-only',
    patches: patchStats.length,
    facets: patchStats.reduce((sum, stat) => sum + stat.facets, 0),
    by_surface: bySurface
  }
}
