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

function random01 (seed, ...keys) {
  return hash32([seed, ...keys].join('|')) / 0x100000000
}

function lerp (range, t) {
  return range[0] + (range[1] - range[0]) * t
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

function ribbonCutter (path, width, depth, overlap, pointAt, closed = false) {
  if (path.length < (closed ? 3 : 2)) return null
  const profileCross = [-0.5, -0.25, 0, 0.25, 0.5]
  const profileDepth = [overlap, -0.72 * depth, -depth, -0.72 * depth, overlap]
  const profileSize = profileCross.length
  const properties = new Float32Array(path.length * profileSize * 3)
  const put = (index, point) => {
    properties[index * 3] = point[0]
    properties[index * 3 + 1] = point[1]
    properties[index * 3 + 2] = point[2]
  }
  for (let index = 0; index < path.length; index += 1) {
    const previous = path[index === 0 ? (closed ? path.length - 1 : 0) : index - 1]
    const next = path[index === path.length - 1 ? (closed ? 0 : path.length - 1) : index + 1]
    const tangentU = next.u - previous.u
    const tangentV = next.v - previous.v
    const length = Math.hypot(tangentU, tangentV) || 1
    const perpendicularU = -tangentV / length
    const perpendicularV = tangentU / length
    for (let profile = 0; profile < profileSize; profile += 1) {
      const side = profileCross[profile] * width
      put(index * profileSize + profile, pointAt(
        path[index].u + perpendicularU * side,
        path[index].v + perpendicularV * side,
        profileDepth[profile]
      ))
    }
  }

  const triangles = []
  const push = (a, b, c) => triangles.push(a, b, c)
  const spanCount = closed ? path.length : path.length - 1
  for (let span = 0; span < spanCount; span += 1) {
    const next = (span + 1) % path.length
    for (let profile = 0; profile < profileSize; profile += 1) {
      const profileNext = (profile + 1) % profileSize
      const a = span * profileSize + profile
      const b = span * profileSize + profileNext
      const c = next * profileSize + profileNext
      const d = next * profileSize + profile
      push(a, b, c)
      push(a, c, d)
    }
  }
  if (!closed) {
    for (let profile = 1; profile < profileSize - 1; profile += 1) {
      push(0, profile + 1, profile)
      const last = (path.length - 1) * profileSize
      push(last, last + profile, last + profile + 1)
    }
  }
  if (signedMeshVolume(properties, triangles) < 0) reverseTriangles(triangles)
  return Manifold.ofMesh(new Mesh({
    numProp: 3,
    vertProperties: properties,
    triVerts: new Uint32Array(triangles),
    tolerance: 1.0e-6
  }))
}

function axisFrame (patch) {
  const grainAxis = patch.grainAxis ?? 'u'
  if (grainAxis === 'v') {
    return {
      along0: patch.v0,
      along1: patch.v1,
      cross0: patch.u0,
      cross1: patch.u1,
      toUv: (along, cross) => ({ u: cross, v: along })
    }
  }
  return {
    along0: patch.u0,
    along1: patch.u1,
    cross0: patch.v0,
    cross1: patch.v1,
    toUv: (along, cross) => ({ u: along, v: cross })
  }
}

function overlapsRect (u, v, radius, rect) {
  return u + radius > rect.u0 - EPS && u - radius < rect.u1 + EPS &&
    v + radius > rect.v0 - EPS && v - radius < rect.v1 + EPS
}

function blocked (point, radius, patch, additionalKeepouts = []) {
  const margin = patch.edgeMargin ?? 0
  if (point.u - radius < patch.u0 + margin || point.u + radius > patch.u1 - margin) return true
  if (point.v - radius < patch.v0 + margin || point.v + radius > patch.v1 - margin) return true
  return [...(patch.keepouts ?? []), ...additionalKeepouts].some(rect => overlapsRect(point.u, point.v, radius, rect))
}

function knotFeaturesForPatch (patch, surfaceConfig, textureConfig) {
  const config = surfaceConfig.knots
  if (!config?.enabled || patch.allowKnots === false) return []
  if (!patch.forceKnot && random01(textureConfig.seed, patch.key, 'knot', 'present') > config.probability_per_patch) return []
  const diameterScale = patch.knotScale ?? 1
  const diameter = lerp(config.diameter_mm, random01(textureConfig.seed, patch.key, 'knot', 'diameter')) * diameterScale
  const aspect = lerp(config.aspect_ratio, random01(textureConfig.seed, patch.key, 'knot', 'aspect'))
  const a = diameter / 2
  const b = a / aspect
  const clearance = config.clearance_mm + Math.max(...config.width_mm)
  const edgeMargin = surfaceConfig.edge_margin_mm
  const availableU = patch.u1 - patch.u0 - 2 * (edgeMargin + a + clearance)
  const availableV = patch.v1 - patch.v0 - 2 * (edgeMargin + b + clearance)
  if (availableU <= 0 || availableV <= 0) return []
  const centerU = patch.u0 + edgeMargin + a + clearance + availableU * random01(textureConfig.seed, patch.key, 'knot', 'u')
  const centerV = patch.v0 + edgeMargin + b + clearance + availableV * random01(textureConfig.seed, patch.key, 'knot', 'v')
  const bound = Math.max(a, b) + clearance
  if (blocked({ u: centerU, v: centerV }, bound, { ...patch, edgeMargin: surfaceConfig.edge_margin_mm })) return []
  const angle = Math.PI * random01(textureConfig.seed, patch.key, 'knot', 'angle')
  const depth = lerp(config.depth_mm, random01(textureConfig.seed, patch.key, 'knot', 'depth')) * (patch.depthScale ?? 1)
  const width = lerp(config.width_mm, random01(textureConfig.seed, patch.key, 'knot', 'width')) * (patch.widthScale ?? 1)
  const features = []
  const contourCount = Math.max(1, Math.round(config.contours))
  for (let contour = 0; contour < contourCount; contour += 1) {
    const factor = 1 - 0.26 * contour
    const points = []
    for (let segment = 0; segment < config.segments; segment += 1) {
      const theta = 2 * Math.PI * segment / config.segments
      const waviness = 1 + 0.045 * Math.sin(3 * theta + 5 * angle) + 0.025 * Math.sin(7 * theta + angle)
      const localU = a * factor * waviness * Math.cos(theta)
      const localV = b * factor * waviness * Math.sin(theta)
      points.push({
        u: centerU + localU * Math.cos(angle) - localV * Math.sin(angle),
        v: centerV + localU * Math.sin(angle) + localV * Math.cos(angle)
      })
    }
    features.push({ path: points, width, depth: depth * (1 - 0.08 * contour), closed: true, kind: 'knot-contour' })
  }
  features.keepout = { u0: centerU - bound, u1: centerU + bound, v0: centerV - bound, v1: centerV + bound }
  features.knotCount = 1
  return features
}

function grainFeaturesForPatch (patch, surfaceConfig, textureConfig, knotKeepouts = []) {
  const config = surfaceConfig.grain
  const frame = axisFrame(patch)
  const pitch = config.pitch_mm * (patch.pitchScale ?? 1)
  const margin = surfaceConfig.edge_margin_mm
  const phaseKey = patch.continuityKey ?? patch.key
  const centerOnly = patch.centerGrain === true
  const lineStart = centerOnly ? 0 : Math.floor(frame.cross0 / pitch) - 1
  const lineEnd = centerOnly ? 0 : Math.ceil(frame.cross1 / pitch) + 1
  const features = []
  const lineIds = new Set()
  for (let line = lineStart; line <= lineEnd; line += 1) {
    if (!centerOnly && random01(textureConfig.seed, phaseKey, 'grain', line, 'present') > config.probability) continue
    const jitter = (random01(textureConfig.seed, phaseKey, 'grain', line, 'jitter') - 0.5) * 2 * config.cross_jitter_fraction * pitch
    const baseCross = centerOnly ? (frame.cross0 + frame.cross1) / 2 : (line + 0.5) * pitch + jitter
    const width = lerp(config.width_mm, random01(textureConfig.seed, phaseKey, 'grain', line, 'width')) * (patch.widthScale ?? 1)
    const depth = lerp(config.depth_mm, random01(textureConfig.seed, phaseKey, 'grain', line, 'depth')) * (patch.depthScale ?? 1)
    const amplitude = lerp(config.amplitude_mm, random01(textureConfig.seed, phaseKey, 'grain', line, 'amplitude')) * (patch.amplitudeScale ?? 1)
    const wavelength = lerp(config.wavelength_mm, random01(textureConfig.seed, phaseKey, 'grain', line, 'wavelength'))
    const phase = 2 * Math.PI * random01(textureConfig.seed, phaseKey, 'grain', line, 'phase')
    const secondaryPhase = 2 * Math.PI * random01(textureConfig.seed, phaseKey, 'grain', line, 'phase2')
    const length = frame.along1 - frame.along0
    const steps = Math.max(2, Math.ceil(length / config.segment_length_mm))
    let run = []
    const flush = () => {
      if (run.length >= 2) {
        features.push({ path: run, width, depth, closed: false, kind: 'grain' })
        lineIds.add(line)
      }
      run = []
    }
    for (let step = 0; step <= steps; step += 1) {
      const along = frame.along0 + length * step / steps
      const primary = amplitude * Math.sin(2 * Math.PI * along / wavelength + phase)
      const secondary = amplitude * config.secondary_amplitude_ratio * Math.sin(2 * Math.PI * along / (0.43 * wavelength) + secondaryPhase)
      const point = frame.toUv(along, baseCross + primary + secondary)
      const testPatch = { ...patch, edgeMargin: margin }
      if (blocked(point, width / 2, testPatch, knotKeepouts)) flush()
      else run.push(point)
    }
    flush()
  }
  features.lineCount = lineIds.size
  return features
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
    return { shape, stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, grooves: 0, grain_lines: 0, knots: 0 } }
  }
  const knotFeatures = knotFeaturesForPatch(patch, surfaceConfig, textureConfig)
  const knotKeepouts = knotFeatures.keepout ? [knotFeatures.keepout] : []
  const grainFeatures = grainFeaturesForPatch(patch, surfaceConfig, textureConfig, knotKeepouts)
  const features = [...grainFeatures, ...knotFeatures]
  const cutters = features.map(feature => ribbonCutter(
    feature.path,
    feature.width,
    feature.depth,
    textureConfig.boolean_overlap_mm,
    patch.pointAt,
    feature.closed
  ))
  const combined = balancedUnionAndDispose(cutters, textureConfig.memory_strategy.feature_union_batch)
  if (!combined) {
    return { shape, stats: { representation: textureConfig.representation, surface: surfaceName, key: patch.key, grooves: 0, grain_lines: 0, knots: 0 } }
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
      grooves: features.length,
      grain_lines: grainFeatures.lineCount ?? 0,
      grain_runs: grainFeatures.length,
      knots: knotFeatures.knotCount ?? 0,
      knot_contours: knotFeatures.length,
      depth_min_mm: Math.min(...features.map(item => item.depth)),
      depth_max_mm: Math.max(...features.map(item => item.depth))
    }
  }
}

export function summarizeTextureStats (patchStats) {
  const bySurface = {}
  for (const stat of patchStats) {
    const entry = bySurface[stat.surface] ?? {
      patches: 0,
      grooves: 0,
      grain_lines: 0,
      grain_runs: 0,
      knots: 0,
      knot_contours: 0,
      depth_min_mm: null,
      depth_max_mm: 0
    }
    entry.patches += 1
    entry.grooves += stat.grooves
    entry.grain_lines += stat.grain_lines ?? 0
    entry.grain_runs += stat.grain_runs ?? 0
    entry.knots += stat.knots ?? 0
    entry.knot_contours += stat.knot_contours ?? 0
    if (stat.grooves > 0) {
      entry.depth_min_mm = entry.depth_min_mm === null ? stat.depth_min_mm : Math.min(entry.depth_min_mm, stat.depth_min_mm)
      entry.depth_max_mm = Math.max(entry.depth_max_mm, stat.depth_max_mm)
    }
    bySurface[stat.surface] = entry
  }
  return {
    representation: patchStats[0]?.representation ?? 'deterministic-vector-grain-and-knot-grooves',
    patches: patchStats.length,
    grooves: patchStats.reduce((sum, stat) => sum + stat.grooves, 0),
    grain_lines: patchStats.reduce((sum, stat) => sum + (stat.grain_lines ?? 0), 0),
    knots: patchStats.reduce((sum, stat) => sum + (stat.knots ?? 0), 0),
    by_surface: bySurface
  }
}
