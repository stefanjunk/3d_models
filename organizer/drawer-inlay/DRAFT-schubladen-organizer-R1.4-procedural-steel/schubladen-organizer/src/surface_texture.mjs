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

function random01 (seed, key, band, ix, iy, channel) {
  return hash32(`${seed}|${key}|${band}|${ix}|${iy}|${channel}`) / 0x100000000
}

function lerp (range, t) {
  return range[0] + (range[1] - range[0]) * t
}

function ellipseBounds (a, b, angle) {
  const c = Math.cos(angle)
  const s = Math.sin(angle)
  return {
    u: Math.sqrt(a * a * c * c + b * b * s * s),
    v: Math.sqrt(a * a * s * s + b * b * c * c)
  }
}

function overlapsRect (candidate, rect) {
  return candidate.u + candidate.boundU > rect.u0 - EPS &&
    candidate.u - candidate.boundU < rect.u1 + EPS &&
    candidate.v + candidate.boundV > rect.v0 - EPS &&
    candidate.v - candidate.boundV < rect.v1 + EPS
}

function separatedFromAccepted (candidate, accepted, factor) {
  for (const prior of accepted) {
    const distance = Math.hypot(candidate.u - prior.u, candidate.v - prior.v)
    if (distance < factor * (candidate.radius + prior.radius)) return false
  }
  return true
}

function orientedDimpleCutter (dimple, overlap, pointAt, normal) {
  const segments = Math.max(12, Math.round(dimple.segments))
  const rings = Math.max(2, Math.round(dimple.radialRings))
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
  const rotatedPoint = (radial, theta, offset) => {
    const localX = dimple.a * radial * Math.cos(theta)
    const localY = dimple.b * radial * Math.sin(theta)
    const c = Math.cos(dimple.angle)
    const s = Math.sin(dimple.angle)
    return pointAt(
      dimple.u + localX * c - localY * s,
      dimple.v + localX * s + localY * c,
      offset
    )
  }

  put(bottomCenter, pointAt(dimple.u, dimple.v, -dimple.depth))
  for (let ring = 1; ring <= rings; ring += 1) {
    const radial = ring / rings
    const depthFraction = Math.pow(Math.max(0, 1 - radial * radial), 1.55)
    const offset = -dimple.depth * depthFraction
    for (let segment = 0; segment < segments; segment += 1) {
      put(firstRing + (ring - 1) * segments + segment, rotatedPoint(radial, 2 * Math.PI * segment / segments, offset))
    }
  }
  for (let segment = 0; segment < segments; segment += 1) {
    put(topRing + segment, rotatedPoint(1, 2 * Math.PI * segment / segments, overlap))
  }
  put(topCenter, pointAt(dimple.u, dimple.v, overlap))

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

  const origin = pointAt(dimple.u, dimple.v, 0)
  const pu = pointAt(dimple.u + 1, dimple.v, 0)
  const pv = pointAt(dimple.u, dimple.v + 1, 0)
  const cross = [
    (pu[1] - origin[1]) * (pv[2] - origin[2]) - (pu[2] - origin[2]) * (pv[1] - origin[1]),
    (pu[2] - origin[2]) * (pv[0] - origin[0]) - (pu[0] - origin[0]) * (pv[2] - origin[2]),
    (pu[0] - origin[0]) * (pv[1] - origin[1]) - (pu[1] - origin[1]) * (pv[0] - origin[0])
  ]
  const forward = cross[0] * normal[0] + cross[1] * normal[1] + cross[2] * normal[2] > 0
  if (!forward) {
    for (let index = 0; index < triangles.length; index += 3) {
      const tmp = triangles[index + 1]
      triangles[index + 1] = triangles[index + 2]
      triangles[index + 2] = tmp
    }
  }
  return Manifold.ofMesh(new Mesh({
    numProp: 3,
    vertProperties: properties,
    triVerts: new Uint32Array(triangles),
    tolerance: 1.0e-6
  }))
}

function dimplesForPatch (patch, surfaceConfig, textureConfig) {
  const accepted = []
  const dimples = []
  const margin = surfaceConfig.edge_margin_mm ?? 0
  const keepouts = patch.keepouts ?? []
  for (const band of surfaceConfig.bands) {
    const pitch = band.pitch_mm
    const ix0 = Math.floor(patch.u0 / pitch) - 1
    const ix1 = Math.ceil(patch.u1 / pitch) + 1
    const iy0 = Math.floor(patch.v0 / pitch) - 1
    const iy1 = Math.ceil(patch.v1 / pitch) + 1
    for (let iy = iy0; iy <= iy1; iy += 1) {
      for (let ix = ix0; ix <= ix1; ix += 1) {
        if (random01(textureConfig.seed, patch.key, band.name, ix, iy, 'present') > band.probability) continue
        const jitter = band.jitter_fraction * pitch
        const u = (ix + 0.5) * pitch + (random01(textureConfig.seed, patch.key, band.name, ix, iy, 'u') - 0.5) * 2 * jitter
        const v = (iy + 0.5) * pitch + (random01(textureConfig.seed, patch.key, band.name, ix, iy, 'v') - 0.5) * 2 * jitter
        const diameter = lerp(band.diameter_mm, random01(textureConfig.seed, patch.key, band.name, ix, iy, 'diameter'))
        const aspect = lerp(band.aspect_ratio, random01(textureConfig.seed, patch.key, band.name, ix, iy, 'aspect'))
        const radius = diameter / 2
        const a = radius * Math.sqrt(aspect)
        const b = radius / Math.sqrt(aspect)
        const angle = 2 * Math.PI * random01(textureConfig.seed, patch.key, band.name, ix, iy, 'angle')
        const bounds = ellipseBounds(a, b, angle)
        const candidate = {
          u,
          v,
          a,
          b,
          angle,
          radius: Math.max(a, b),
          boundU: bounds.u,
          boundV: bounds.v,
          depth: lerp(band.depth_mm, random01(textureConfig.seed, patch.key, band.name, ix, iy, 'depth')) * (patch.depthScale ?? 1),
          segments: band.segments,
          radialRings: band.radial_rings,
          band: band.name
        }
        if (candidate.u - candidate.boundU < patch.u0 + margin || candidate.u + candidate.boundU > patch.u1 - margin) continue
        if (candidate.v - candidate.boundV < patch.v0 + margin || candidate.v + candidate.boundV > patch.v1 - margin) continue
        if (keepouts.some(rect => overlapsRect(candidate, rect))) continue
        if (!separatedFromAccepted(candidate, accepted, band.spacing_factor)) continue
        accepted.push(candidate)
        dimples.push(candidate)
      }
    }
  }
  return dimples
}

function balancedUnionAndDispose (items, batchSize) {
  let queue = items.filter(Boolean)
  if (queue.length === 0) return null
  while (queue.length > 1) {
    const next = []
    for (let index = 0; index < queue.length; index += batchSize) {
      const batch = queue.slice(index, index + batchSize)
      if (batch.length === 1) {
        next.push(batch[0])
      } else {
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
    return { shape, stats: { surface: surfaceName, key: patch.key, dimples: 0 } }
  }
  const dimples = dimplesForPatch(patch, surfaceConfig, textureConfig)
  const cutters = dimples.map(dimple => orientedDimpleCutter(
    dimple,
    textureConfig.boolean_overlap_mm,
    patch.pointAt,
    patch.normal
  ))
  const combined = balancedUnionAndDispose(cutters, textureConfig.memory_strategy.dimple_union_batch)
  if (!combined) return { shape, stats: { surface: surfaceName, key: patch.key, dimples: 0 } }
  const result = shape.subtract(combined)
  shape.delete()
  combined.delete()
  return {
    shape: result,
    stats: {
      surface: surfaceName,
      key: patch.key,
      dimples: dimples.length,
      depth_min_mm: dimples.length ? Math.min(...dimples.map(item => item.depth)) : 0,
      depth_max_mm: dimples.length ? Math.max(...dimples.map(item => item.depth)) : 0,
      bands: Object.fromEntries([...new Set(dimples.map(item => item.band))].map(name => [name, dimples.filter(item => item.band === name).length]))
    }
  }
}

export function summarizeTextureStats (patchStats) {
  const bySurface = {}
  for (const stat of patchStats) {
    const entry = bySurface[stat.surface] ?? { patches: 0, dimples: 0, depth_min_mm: null, depth_max_mm: 0 }
    entry.patches += 1
    entry.dimples += stat.dimples
    if (stat.dimples > 0) {
      entry.depth_min_mm = entry.depth_min_mm === null ? stat.depth_min_mm : Math.min(entry.depth_min_mm, stat.depth_min_mm)
      entry.depth_max_mm = Math.max(entry.depth_max_mm, stat.depth_max_mm)
    }
    bySurface[stat.surface] = entry
  }
  return {
    representation: 'deterministic-multiscale-analytic-dimple-field',
    patches: patchStats.length,
    dimples: patchStats.reduce((sum, stat) => sum + stat.dimples, 0),
    by_surface: bySurface
  }
}
