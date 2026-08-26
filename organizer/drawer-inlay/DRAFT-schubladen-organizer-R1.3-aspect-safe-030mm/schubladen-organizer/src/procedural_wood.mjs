import fs from 'node:fs'

const UINT32_MAX = 0xffffffff
const FLOOR_DEPTH_LIMIT_MM = 0.20
const WALL_DEPTH_LIMIT_MM = 0.16
const TOP_DEPTH_LIMIT_MM = 0.20
const MODULE_IDS = new Set([
  'driver-front',
  'driver-back',
  'hardware-front',
  'hardware-back'
])

const TOP_LEVEL_KEYS = [
  'schema',
  'representation',
  'units',
  'seed',
  'process',
  'grain',
  'knots',
  'surface_policy',
  'memory_strategy',
  'resource_budget'
]

const GRAIN_KEYS = [
  'groove_width_mm',
  'floor_depth_mm',
  'inner_wall_depth_mm',
  'top_depth_mm',
  'spacing_min_mm',
  'spacing_max_mm',
  'wavelength_min_mm',
  'wavelength_max_mm',
  'lateral_drift_min_mm',
  'lateral_drift_max_mm',
  'path_segment_max_mm',
  'tube_segments',
  'endpoint_segments',
  'segment_overlap_mm',
  'floor_margin_mm',
  'wall_end_margin_mm',
  'wall_bottom_clearance_from_floor_mm',
  'wall_top_clearance_mm',
  'top_end_margin_mm',
  'top_centerline_drift_mm'
]

function assertPlainObject (value, label) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${label} must be an object`)
  }
}

function assertExactKeys (value, allowedKeys, label) {
  const allowed = new Set(allowedKeys)
  const unexpected = Object.keys(value).filter(key => !allowed.has(key))
  const missing = allowedKeys.filter(key => !Object.hasOwn(value, key))
  if (unexpected.length > 0) throw new Error(`${label} has unexpected key: ${unexpected[0]}`)
  if (missing.length > 0) throw new Error(`${label} is missing key: ${missing[0]}`)
}

function assertFinitePositive (value, label) {
  if (!Number.isFinite(value) || value <= 0) throw new Error(`${label} must be finite and positive`)
}

function assertFiniteNonNegative (value, label) {
  if (!Number.isFinite(value) || value < 0) throw new Error(`${label} must be finite and non-negative`)
}

function assertPositiveInteger (value, label, minimum = 1) {
  if (!Number.isInteger(value) || value < minimum) throw new Error(`${label} must be an integer >= ${minimum}`)
}

function assertSeed (value, label) {
  if (!Number.isSafeInteger(value) || value < 0 || value > UINT32_MAX) {
    throw new Error(`${label} must be an unsigned 32-bit integer`)
  }
}

function assertFinitePair (value, label, nonNegative = false) {
  if (!Array.isArray(value) || value.length !== 2) throw new Error(`${label} must contain exactly two values`)
  for (const [index, item] of value.entries()) {
    if (nonNegative) assertFiniteNonNegative(item, `${label}[${index}]`)
    else assertFinitePositive(item, `${label}[${index}]`)
  }
}

function assertNoExternalSurfaceInputs (value, label = 'config', seen = new WeakSet()) {
  if (typeof value === 'string') {
    if (/raster|heightmap|image/i.test(value)) throw new Error(`${label} must not reference raster, heightmap, or image input`)
    return
  }
  if (value === null || typeof value !== 'object') return
  if (seen.has(value)) throw new Error(`${label} must be acyclic JSON data`)
  seen.add(value)
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertNoExternalSurfaceInputs(item, `${label}[${index}]`, seen))
  } else {
    for (const [key, item] of Object.entries(value)) {
      if (/raster|heightmap|image/i.test(key)) throw new Error(`${label}.${key} is a forbidden external surface input`)
      assertNoExternalSurfaceInputs(item, `${label}.${key}`, seen)
    }
  }
  seen.delete(value)
}

function validateProcess (process) {
  assertPlainObject(process, 'process')
  assertExactKeys(process, ['nozzle_mm', 'nominal_line_width_mm', 'layer_height_mm'], 'process')
  for (const key of ['nozzle_mm', 'nominal_line_width_mm', 'layer_height_mm']) {
    assertFinitePositive(process[key], `process.${key}`)
  }
}

function validateGrain (grain, process) {
  assertPlainObject(grain, 'grain')
  assertExactKeys(grain, GRAIN_KEYS, 'grain')
  for (const key of GRAIN_KEYS) assertFinitePositive(grain[key], `grain.${key}`)
  assertPositiveInteger(grain.tube_segments, 'grain.tube_segments', 8)
  assertPositiveInteger(grain.endpoint_segments, 'grain.endpoint_segments', 8)

  if (grain.groove_width_mm < 2 * process.nominal_line_width_mm) {
    throw new Error('grain.groove_width_mm must be at least two nominal line widths')
  }
  if (grain.floor_depth_mm > FLOOR_DEPTH_LIMIT_MM) throw new Error('grain.floor_depth_mm exceeds 0.20 mm')
  if (grain.inner_wall_depth_mm > WALL_DEPTH_LIMIT_MM) throw new Error('grain.inner_wall_depth_mm exceeds 0.16 mm')
  if (grain.top_depth_mm > TOP_DEPTH_LIMIT_MM) throw new Error('grain.top_depth_mm exceeds 0.20 mm')

  if (grain.spacing_min_mm >= grain.spacing_max_mm) throw new Error('grain spacing range must be strictly increasing')
  if (grain.wavelength_min_mm >= grain.wavelength_max_mm) throw new Error('grain wavelength range must be strictly increasing')
  if (grain.lateral_drift_min_mm >= grain.lateral_drift_max_mm) throw new Error('grain drift range must be strictly increasing')
  if (grain.lateral_drift_max_mm >= grain.spacing_min_mm) throw new Error('maximum grain drift must be smaller than minimum spacing')
  if (grain.spacing_max_mm >= grain.wavelength_min_mm) throw new Error('maximum grain spacing must be smaller than minimum wavelength')
  if (grain.path_segment_max_mm > grain.wavelength_min_mm) throw new Error('grain path segments must not exceed the minimum wavelength')
  if (grain.segment_overlap_mm >= grain.groove_width_mm) throw new Error('grain segment overlap must be smaller than groove width')
  if (grain.top_centerline_drift_mm > grain.groove_width_mm / 2) throw new Error('top centerline drift must not exceed half the groove width')
}

function validateKnots (knots, grain) {
  assertPlainObject(knots, 'knots')
  assertExactKeys(knots, ['assembly_max', 'nested_contours', 'diameter_range_mm', 'placements'], 'knots')
  assertPositiveInteger(knots.assembly_max, 'knots.assembly_max')
  assertPositiveInteger(knots.nested_contours, 'knots.nested_contours', 2)
  assertFinitePair(knots.diameter_range_mm, 'knots.diameter_range_mm')
  if (knots.diameter_range_mm[0] >= knots.diameter_range_mm[1]) {
    throw new Error('knots.diameter_range_mm must be strictly increasing')
  }
  if (knots.diameter_range_mm[0] < 4 * grain.groove_width_mm) {
    throw new Error('minimum knot diameter must be at least four groove widths')
  }
  if (!Array.isArray(knots.placements)) throw new Error('knots.placements must be an array')
  if (knots.placements.length > knots.assembly_max) throw new Error('knot placement count exceeds knots.assembly_max')

  for (const [index, placement] of knots.placements.entries()) {
    const label = `knots.placements[${index}]`
    assertPlainObject(placement, label)
    assertExactKeys(placement, [
      'module',
      'center_global_xy_mm',
      'diameter_mm',
      'aspect_y_over_x',
      'rotation_deg'
    ], label)
    if (!MODULE_IDS.has(placement.module)) throw new Error(`${label}.module is not a known floor module`)
    assertFinitePair(placement.center_global_xy_mm, `${label}.center_global_xy_mm`, true)
    assertFinitePositive(placement.diameter_mm, `${label}.diameter_mm`)
    if (placement.diameter_mm < knots.diameter_range_mm[0] || placement.diameter_mm > knots.diameter_range_mm[1]) {
      throw new Error(`${label}.diameter_mm is outside knots.diameter_range_mm`)
    }
    assertFinitePositive(placement.aspect_y_over_x, `${label}.aspect_y_over_x`)
    if (placement.aspect_y_over_x > 1) throw new Error(`${label}.aspect_y_over_x must not exceed 1`)
    if (!Number.isFinite(placement.rotation_deg) || Math.abs(placement.rotation_deg) > 180) {
      throw new Error(`${label}.rotation_deg must be finite and within -180..180`)
    }
    const radius = placement.diameter_mm / 2
    if (placement.center_global_xy_mm[0] < radius || placement.center_global_xy_mm[1] < radius) {
      throw new Error(`${label} must keep its nominal diameter in non-negative assembly coordinates`)
    }
  }

  for (let first = 0; first < knots.placements.length; first += 1) {
    for (let second = first + 1; second < knots.placements.length; second += 1) {
      const a = knots.placements[first]
      const b = knots.placements[second]
      const separation = Math.hypot(
        a.center_global_xy_mm[0] - b.center_global_xy_mm[0],
        a.center_global_xy_mm[1] - b.center_global_xy_mm[1]
      )
      if (separation <= (a.diameter_mm + b.diameter_mm) / 2) {
        throw new Error(`knot placements ${first} and ${second} overlap`)
      }
    }
  }
}

function validateSurfacePolicy (policy) {
  assertPlainObject(policy, 'surface_policy')
  assertExactKeys(policy, [
    'floor_direction',
    'inner_wall_direction',
    'top_direction',
    'outer_walls',
    'operation',
    'repeat',
    'smooth_keepouts'
  ], 'surface_policy')
  const exactValues = {
    floor_direction: 'global-positive-y',
    inner_wall_direction: 'local-long-axis',
    top_direction: 'wall-centerline',
    outer_walls: 'smooth-no-geometric-texture',
    operation: 'engrave-only',
    repeat: 'none-deterministic-global-field'
  }
  for (const [key, expected] of Object.entries(exactValues)) {
    if (policy[key] !== expected) throw new Error(`surface_policy.${key} must equal ${expected}`)
  }
  if (!Array.isArray(policy.smooth_keepouts) || policy.smooth_keepouts.length === 0) {
    throw new Error('surface_policy.smooth_keepouts must be a non-empty array')
  }
  const keepouts = new Set()
  for (const [index, keepout] of policy.smooth_keepouts.entries()) {
    if (typeof keepout !== 'string' || keepout.length === 0) throw new Error(`surface_policy.smooth_keepouts[${index}] must be a non-empty string`)
    if (keepouts.has(keepout)) throw new Error(`surface_policy.smooth_keepouts contains duplicate ${keepout}`)
    keepouts.add(keepout)
  }
}

function validateMemoryStrategy (strategy) {
  assertPlainObject(strategy, 'memory_strategy')
  assertExactKeys(strategy, ['node_old_space_mb', 'one_module_per_process', 'one_surface_patch_per_boolean'], 'memory_strategy')
  assertPositiveInteger(strategy.node_old_space_mb, 'memory_strategy.node_old_space_mb')
  if (strategy.one_module_per_process !== true || strategy.one_surface_patch_per_boolean !== true) {
    throw new Error('memory_strategy process and surface isolation flags must be true')
  }
}

function validateResourceBudget (budget) {
  assertPlainObject(budget, 'resource_budget')
  const keys = [
    'r1_3_baseline_triangles',
    'r1_3_baseline_stl_bytes',
    'r1_3_baseline_peak_rss_mib',
    'triangle_target_total',
    'triangle_stop_total',
    'max_stl_bytes_total',
    'max_peak_rss_mib_per_module',
    'minimum_triangle_and_byte_reduction_fraction'
  ]
  assertExactKeys(budget, keys, 'resource_budget')
  for (const key of keys) assertFinitePositive(budget[key], `resource_budget.${key}`)
  if (budget.triangle_target_total > budget.triangle_stop_total) {
    throw new Error('resource_budget triangle target must not exceed the stop limit')
  }
  if (budget.triangle_stop_total >= budget.r1_3_baseline_triangles) {
    throw new Error('resource_budget triangle stop must be below the R1.3 baseline')
  }
  if (budget.minimum_triangle_and_byte_reduction_fraction >= 1) {
    throw new Error('resource_budget reduction fraction must be smaller than 1')
  }
}

export function validateProceduralWoodConfig (config) {
  assertPlainObject(config, 'config')
  assertNoExternalSurfaceInputs(config)
  assertExactKeys(config, TOP_LEVEL_KEYS, 'config')
  if (config.schema !== 'organizer-procedural-wood-texture-v1') throw new Error('unsupported procedural wood schema')
  if (config.representation !== 'procedural-vector-wood-grooves') throw new Error('unsupported procedural wood representation')
  if (config.units !== 'mm') throw new Error('procedural wood units must be mm')
  assertSeed(config.seed, 'seed')
  validateProcess(config.process)
  validateGrain(config.grain, config.process)
  validateKnots(config.knots, config.grain)
  validateSurfacePolicy(config.surface_policy)
  validateMemoryStrategy(config.memory_strategy)
  validateResourceBudget(config.resource_budget)
  return config
}

export function loadProceduralWoodConfig (file) {
  if (typeof file !== 'string' || file.length === 0) throw new Error('procedural wood config path must be a non-empty string')
  let parsed
  try {
    parsed = JSON.parse(fs.readFileSync(file, 'utf8'))
  } catch (error) {
    throw new Error(`unable to load procedural wood config ${file}: ${error.message}`)
  }
  return validateProceduralWoodConfig(parsed)
}

function hashSeed (seed, text) {
  let value = (seed >>> 0) ^ 0x811c9dc5
  for (let index = 0; index < text.length; index += 1) {
    value ^= text.charCodeAt(index)
    value = Math.imul(value, 0x01000193) >>> 0
  }
  return value >>> 0
}

function seededRandom (seed, key) {
  let state = hashSeed(seed, key)
  return () => {
    state = (state + 0x6d2b79f5) >>> 0
    let value = state
    value = Math.imul(value ^ (value >>> 15), value | 1)
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61)
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296
  }
}

function interpolate (minimum, maximum, fraction) {
  return minimum + (maximum - minimum) * fraction
}

function roundMm (value) {
  return Math.round(value * 1e6) / 1e6
}

function clamp (value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, value))
}

function validateRectangle (rectangle) {
  assertPlainObject(rectangle, 'region.rectangle_mm')
  assertExactKeys(rectangle, ['min', 'max'], 'region.rectangle_mm')
  if (!Array.isArray(rectangle.min) || rectangle.min.length !== 2 || !Array.isArray(rectangle.max) || rectangle.max.length !== 2) {
    throw new Error('region.rectangle_mm min/max must contain exactly two coordinates')
  }
  for (let axis = 0; axis < 2; axis += 1) {
    if (!Number.isFinite(rectangle.min[axis]) || !Number.isFinite(rectangle.max[axis])) {
      throw new Error('region.rectangle_mm coordinates must be finite')
    }
    if (rectangle.max[axis] <= rectangle.min[axis]) throw new Error('region.rectangle_mm must have positive area')
  }
}

function roundedRectangle (rectangle) {
  return {
    min: rectangle.min.map(roundMm),
    max: rectangle.max.map(roundMm)
  }
}

function insetRectangle (rectangle, inset) {
  const result = {
    min: rectangle.min.map(value => value + inset),
    max: rectangle.max.map(value => value - inset)
  }
  if (result.max[0] <= result.min[0] || result.max[1] <= result.min[1]) return null
  return roundedRectangle(result)
}

function samePoint (first, second) {
  return Math.abs(first[0] - second[0]) <= 1.0e-9 && Math.abs(first[1] - second[1]) <= 1.0e-9
}

function deduplicatePoints (points) {
  const result = []
  for (const point of points) {
    const rounded = point.map(roundMm)
    if (!result.length || !samePoint(result.at(-1), rounded)) result.push(rounded)
  }
  return result
}

function polylineLength (points) {
  let length = 0
  for (let index = 1; index < points.length; index += 1) {
    length += Math.hypot(
      points[index][0] - points[index - 1][0],
      points[index][1] - points[index - 1][1]
    )
  }
  return length
}

function clipSegmentToRectangle (start, end, rectangle) {
  let entry = 0
  let exit = 1
  for (let axis = 0; axis < 2; axis += 1) {
    const delta = end[axis] - start[axis]
    if (Math.abs(delta) <= 1.0e-12) {
      if (start[axis] < rectangle.min[axis] || start[axis] > rectangle.max[axis]) return null
      continue
    }
    const first = (rectangle.min[axis] - start[axis]) / delta
    const second = (rectangle.max[axis] - start[axis]) / delta
    entry = Math.max(entry, Math.min(first, second))
    exit = Math.min(exit, Math.max(first, second))
    if (entry > exit) return null
  }
  const pointAt = fraction => start.map((value, axis) => (
    value + (end[axis] - value) * fraction
  ))
  return {
    start: pointAt(entry),
    end: pointAt(exit),
    entry,
    exit
  }
}

function clipPolylineToRectangle (points, rectangle) {
  const fragments = []
  let current = null
  const finish = () => {
    if (!current) return
    current.points = deduplicatePoints(current.points)
    if (current.points.length >= 2) fragments.push(current)
    current = null
  }
  for (let segmentIndex = 0; segmentIndex < points.length - 1; segmentIndex += 1) {
    const clipped = clipSegmentToRectangle(points[segmentIndex], points[segmentIndex + 1], rectangle)
    if (!clipped || samePoint(clipped.start, clipped.end)) {
      finish()
      continue
    }
    if (!current || !samePoint(current.points.at(-1), clipped.start)) {
      finish()
      current = {
        source_position: segmentIndex + clipped.entry,
        points: [clipped.start, clipped.end]
      }
    } else {
      current.points.push(clipped.end)
    }
    if (clipped.exit < 1 - 1.0e-12) finish()
  }
  finish()
  return fragments
}

function pointInsideRectangle (point, rectangle) {
  return point[0] >= rectangle.min[0] - 1.0e-9 && point[0] <= rectangle.max[0] + 1.0e-9 &&
    point[1] >= rectangle.min[1] - 1.0e-9 && point[1] <= rectangle.max[1] + 1.0e-9
}

function validateRegion (region) {
  assertPlainObject(region, 'region')
  const allowed = ['id', 'surface', 'rectangle_mm', 'module', 'include_knots', 'long_axis', 'depth_mm']
  const unexpected = Object.keys(region).filter(key => !allowed.includes(key))
  if (unexpected.length > 0) throw new Error(`region has unexpected key: ${unexpected[0]}`)
  for (const key of ['id', 'surface', 'rectangle_mm']) {
    if (!Object.hasOwn(region, key)) throw new Error(`region is missing key: ${key}`)
  }
  if (typeof region.id !== 'string' || region.id.length === 0) throw new Error('region.id must be a non-empty string')
  if (!['floor', 'wall', 'top'].includes(region.surface)) throw new Error('region.surface must be floor, wall, or top')
  validateRectangle(region.rectangle_mm)
  if (region.module !== undefined && !MODULE_IDS.has(region.module)) throw new Error('region.module is not a known floor module')
  if (region.include_knots !== undefined && typeof region.include_knots !== 'boolean') throw new Error('region.include_knots must be boolean')
  if (region.include_knots && region.surface !== 'floor') throw new Error('knots are allowed only on floor regions')
  if (region.include_knots && region.module === undefined) throw new Error('floor knot planning requires region.module')
  if (region.long_axis !== undefined && ![0, 1].includes(region.long_axis)) throw new Error('region.long_axis must be axis 0 or 1')
  if (region.depth_mm !== undefined) assertFinitePositive(region.depth_mm, 'region.depth_mm')
}

function surfaceDepth (config, region) {
  const configured = {
    floor: config.grain.floor_depth_mm,
    wall: config.grain.inner_wall_depth_mm,
    top: config.grain.top_depth_mm
  }[region.surface]
  const limit = {
    floor: FLOOR_DEPTH_LIMIT_MM,
    wall: WALL_DEPTH_LIMIT_MM,
    top: TOP_DEPTH_LIMIT_MM
  }[region.surface]
  const depth = region.depth_mm ?? configured
  if (depth > configured) throw new Error(`region.depth_mm exceeds configured ${region.surface} depth`)
  if (depth > limit) throw new Error(`region.depth_mm exceeds ${region.surface} depth limit`)
  return depth
}

function planGrainPaths (config, region, seed, longAxis) {
  const grain = config.grain
  const radius = grain.groove_width_mm / 2
  const shortAxis = 1 - longAxis
  const minimum = region.rectangle_mm.min
  const maximum = region.rectangle_mm.max
  const longMinimum = minimum[longAxis] + radius
  const longMaximum = maximum[longAxis] - radius
  const shortMinimum = minimum[shortAxis] + radius
  const shortMaximum = maximum[shortAxis] - radius
  if (longMaximum <= longMinimum || shortMaximum <= shortMinimum) {
    throw new Error('region.rectangle_mm is too small for the configured groove width')
  }

  const random = seededRandom(seed, `grain:${region.id}:${region.surface}`)
  const configuredDrift = region.surface === 'top'
    ? Math.min(grain.lateral_drift_max_mm, grain.top_centerline_drift_mm)
    : grain.lateral_drift_max_mm
  const baseMinimum = shortMinimum + configuredDrift
  const baseMaximum = shortMaximum - configuredDrift
  const positions = []
  if (baseMaximum <= baseMinimum) {
    positions.push((shortMinimum + shortMaximum) / 2)
  } else {
    let position = baseMinimum + random() * Math.min(grain.spacing_min_mm, baseMaximum - baseMinimum)
    while (position <= baseMaximum) {
      positions.push(position)
      position += interpolate(grain.spacing_min_mm, grain.spacing_max_mm, random())
    }
    if (positions.length === 0) positions.push((baseMinimum + baseMaximum) / 2)
  }

  return positions.map((base, index) => {
    const wavelength = interpolate(grain.wavelength_min_mm, grain.wavelength_max_mm, random())
    const requestedDrift = region.surface === 'top'
      ? grain.top_centerline_drift_mm * (0.55 + 0.45 * random())
      : interpolate(grain.lateral_drift_min_mm, grain.lateral_drift_max_mm, random())
    const drift = Math.min(requestedDrift, base - shortMinimum, shortMaximum - base)
    const phase = 2 * Math.PI * random()
    const segmentLength = Math.min(grain.path_segment_max_mm, wavelength / 8)
    const segmentCount = Math.max(1, Math.ceil((longMaximum - longMinimum) / segmentLength))
    const points = []
    for (let step = 0; step <= segmentCount; step += 1) {
      const long = interpolate(longMinimum, longMaximum, step / segmentCount)
      const short = clamp(base + drift * Math.sin(2 * Math.PI * long / wavelength + phase), shortMinimum, shortMaximum)
      const point = longAxis === 0 ? [long, short] : [short, long]
      points.push(point.map(roundMm))
    }
    const id = `${region.id}-grain-${String(index + 1).padStart(2, '0')}`
    return {
      id,
      parent_path_id: id,
      kind: 'grain-centerline',
      surface: region.surface,
      closed: false,
      width_mm: grain.groove_width_mm,
      depth_mm: surfaceDepth(config, region),
      wavelength_mm: roundMm(wavelength),
      lateral_drift_mm: roundMm(drift),
      points_mm: points
    }
  })
}

function closeRoundedPolygon (polygon) {
  const points = []
  for (const point of polygon) {
    const rounded = point.map(roundMm)
    const previous = points[points.length - 1]
    if (!previous || previous[0] !== rounded[0] || previous[1] !== rounded[1]) points.push(rounded)
  }
  if (points.length < 3) return []
  const first = points[0]
  const last = points[points.length - 1]
  if (first[0] !== last[0] || first[1] !== last[1]) points.push([...first])
  return points
}

function planKnotContours (config, region, seed, depth) {
  if (!region.include_knots) return []
  const radius = config.grain.groove_width_mm / 2
  const allowed = {
    min: region.rectangle_mm.min.map(value => value + radius),
    max: region.rectangle_mm.max.map(value => value - radius)
  }
  if (allowed.max[0] <= allowed.min[0] || allowed.max[1] <= allowed.min[1]) return []

  const placements = config.knots.placements.filter(placement => {
    if (placement.module !== region.module) return false
    const outerRadius = placement.diameter_mm / 2
    const [cx, cy] = placement.center_global_xy_mm
    return cx + outerRadius >= allowed.min[0] && cx - outerRadius <= allowed.max[0] &&
      cy + outerRadius >= allowed.min[1] && cy - outerRadius <= allowed.max[1]
  })

  return placements.map((placement, placementIndex) => {
    const random = seededRandom(seed, `knot:${region.id}:${placement.module}:${placementIndex}`)
    const phase = 2 * Math.PI * random()
    const rotation = placement.rotation_deg * Math.PI / 180
    const cosRotation = Math.cos(rotation)
    const sinRotation = Math.sin(rotation)
    const segmentCount = Math.max(24, config.grain.endpoint_segments * 2)
    const contours = []
    for (let contourIndex = 0; contourIndex < config.knots.nested_contours; contourIndex += 1) {
      const contourScale = 1 - 0.18 * contourIndex
      const radiusX = placement.diameter_mm * contourScale / 2
      const radiusY = radiusX * placement.aspect_y_over_x
      const polygon = []
      for (let index = 0; index < segmentCount; index += 1) {
        const angle = 2 * Math.PI * index / segmentCount
        const irregularity = 1 + 0.035 * Math.sin(3 * angle + phase)
        const localX = radiusX * irregularity * Math.cos(angle)
        const localY = radiusY * irregularity * Math.sin(angle)
        polygon.push([
          placement.center_global_xy_mm[0] + localX * cosRotation - localY * sinRotation,
          placement.center_global_xy_mm[1] + localX * sinRotation + localY * cosRotation
        ])
      }
      const complete = closeRoundedPolygon(polygon)
      if (complete.length >= 4 && complete.every(point => pointInsideRectangle(point, allowed))) {
        const id = `${region.id}-knot-${String(placementIndex + 1).padStart(2, '0')}-${String(contourIndex + 1).padStart(2, '0')}`
        contours.push({
          id,
          parent_path_id: id,
          kind: 'knot-contour',
          surface: 'floor',
          closed: true,
          width_mm: config.grain.groove_width_mm,
          depth_mm: depth,
          points_mm: complete
        })
      }
    }
    return {
      id: `${region.id}-knot-${String(placementIndex + 1).padStart(2, '0')}`,
      surface: 'floor',
      module: placement.module,
      center_global_xy_mm: [...placement.center_global_xy_mm],
      contours
    }
  }).filter(knot => knot.contours.length === config.knots.nested_contours)
}

function normalizedClipRectangles (allowedRectangles) {
  if (!Array.isArray(allowedRectangles) || allowedRectangles.length === 0) {
    throw new Error('allowedRectangles must be a non-empty array')
  }
  return allowedRectangles.map((entry, index) => {
    const rectangle = entry?.rectangle_mm ?? entry
    validateRectangle(rectangle)
    const id = entry?.rectangle_mm === undefined
      ? `clip-${String(index + 1).padStart(2, '0')}`
      : entry.id
    if (typeof id !== 'string' || id.length === 0) throw new Error('clip rectangle id must be a non-empty string')
    return { id, rectangle_mm: roundedRectangle(rectangle), input_index: index }
  })
}

export function clipProceduralWoodPlan (sourcePlan, allowedRectangles) {
  assertPlainObject(sourcePlan, 'sourcePlan')
  if (!Array.isArray(sourcePlan.paths) || !Array.isArray(sourcePlan.knots)) {
    throw new Error('sourcePlan must contain paths and knots arrays')
  }
  const width = sourcePlan.groove?.width_mm
  assertFinitePositive(width, 'sourcePlan.groove.width_mm')
  const clips = normalizedClipRectangles(allowedRectangles).map(clip => ({
    ...clip,
    inset_centerline_rectangle_mm: insetRectangle(clip.rectangle_mm, width / 2)
  }))
  const paths = []
  const seen = new Set()
  for (const [pathIndex, path] of sourcePlan.paths.entries()) {
    const parentPathId = path.parent_path_id ?? path.id
    const candidates = []
    for (const clip of clips) {
      if (!clip.inset_centerline_rectangle_mm) continue
      for (const fragment of clipPolylineToRectangle(path.points_mm, clip.inset_centerline_rectangle_mm)) {
        if (polylineLength(fragment.points) + 1.0e-9 < width) continue
        candidates.push({ ...fragment, clip })
      }
    }
    candidates.sort((first, second) => (
      first.source_position - second.source_position || first.clip.input_index - second.clip.input_index
    ))
    let fragmentIndex = 0
    for (const candidate of candidates) {
      const signature = JSON.stringify(candidate.points)
      if (seen.has(`${parentPathId}:${signature}`)) continue
      seen.add(`${parentPathId}:${signature}`)
      fragmentIndex += 1
      paths.push({
        ...path,
        id: `${parentPathId}-fragment-${String(fragmentIndex).padStart(3, '0')}`,
        parent_path_id: parentPathId,
        source_path_order: pathIndex,
        clip_rectangle_id: candidate.clip.id,
        points_mm: candidate.points
      })
    }
  }

  const knots = []
  for (const knot of sourcePlan.knots) {
    const containingClip = clips.find(clip => (
      clip.inset_centerline_rectangle_mm && knot.contours.every(contour => (
        contour.points_mm.every(point => pointInsideRectangle(point, clip.inset_centerline_rectangle_mm))
      ))
    ))
    if (!containingClip) continue
    knots.push({
      ...knot,
      clip_rectangle_id: containingClip.id,
      contours: knot.contours.map(contour => ({
        ...contour,
        parent_path_id: contour.parent_path_id ?? contour.id,
        clip_rectangle_id: containingClip.id,
        points_mm: contour.points_mm.map(point => [...point])
      }))
    })
  }

  const sourceFieldId = sourcePlan.coherence?.source_field_id ?? sourcePlan.region?.id
  const sourceRectangle = sourcePlan.coherence?.source_rectangle_mm ?? sourcePlan.region?.rectangle_mm
  const parentPathIds = [
    ...new Set([
      ...paths.map(path => path.parent_path_id),
      ...knots.flatMap(knot => knot.contours.map(contour => contour.parent_path_id))
    ])
  ]
  return {
    ...sourcePlan,
    policy: {
      ...sourcePlan.policy,
      coherence_policy: 'plan-once-then-clip'
    },
    coherence: {
      coherence_policy: 'plan-once-then-clip',
      source_field_id: sourceFieldId,
      source_rectangle_mm: roundedRectangle(sourceRectangle),
      clip_rectangles: clips.map(clip => ({
        id: clip.id,
        rectangle_mm: clip.rectangle_mm,
        inset_centerline_rectangle_mm: clip.inset_centerline_rectangle_mm
      })),
      parent_path_ids: parentPathIds
    },
    paths,
    knots
  }
}

export function planProceduralWoodRegion (config, region, options = {}) {
  validateProceduralWoodConfig(config)
  validateRegion(region)
  assertPlainObject(options, 'options')
  const unexpectedOptions = Object.keys(options).filter(key => key !== 'seed')
  if (unexpectedOptions.length > 0) throw new Error(`options has unexpected key: ${unexpectedOptions[0]}`)
  const seed = options.seed ?? config.seed
  assertSeed(seed, 'options.seed')
  const dimensions = [
    region.rectangle_mm.max[0] - region.rectangle_mm.min[0],
    region.rectangle_mm.max[1] - region.rectangle_mm.min[1]
  ]
  const longAxis = region.surface === 'floor'
    ? 1
    : (region.long_axis ?? (dimensions[0] >= dimensions[1] ? 0 : 1))
  const depth = surfaceDepth(config, region)
  const direction = longAxis === 0 ? [1, 0] : [0, 1]
  const paths = planGrainPaths(config, region, seed, longAxis)
  const knots = planKnotContours(config, region, seed, depth)

  const sourceRectangle = {
    min: region.rectangle_mm.min.map(roundMm),
    max: region.rectangle_mm.max.map(roundMm)
  }
  const parentPathIds = [
    ...paths.map(path => path.parent_path_id),
    ...knots.flatMap(knot => knot.contours.map(contour => contour.parent_path_id))
  ]

  return {
    schema: 'organizer-procedural-wood-plan-v1',
    representation: config.representation,
    units: 'mm',
    seed,
    region: {
      id: region.id,
      surface: region.surface,
      coordinate_space: region.surface === 'floor' ? 'global-xy-mm' : 'local-uv-mm',
      rectangle_mm: sourceRectangle,
      direction: {
        mode: region.surface === 'floor' ? 'global-positive-y' : 'local-long-axis',
        vector: direction
      }
    },
    policy: {
      operation: 'engrave-only',
      repeat: 'none-deterministic-global-field',
      outer_walls: 'smooth-no-geometric-texture',
      rounded_cutters: true,
      input_mode: 'parameters-only',
      input_dependencies: []
    },
    coherence: {
      coherence_policy: 'plan-once-then-clip',
      source_field_id: region.id,
      source_rectangle_mm: sourceRectangle,
      clip_rectangles: [{
        id: region.id,
        rectangle_mm: sourceRectangle,
        inset_centerline_rectangle_mm: insetRectangle(sourceRectangle, config.grain.groove_width_mm / 2)
      }],
      parent_path_ids: parentPathIds
    },
    groove: {
      width_mm: config.grain.groove_width_mm,
      depth_mm: depth
    },
    paths,
    knots
  }
}
