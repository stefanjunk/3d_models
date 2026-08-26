import assert from 'node:assert/strict'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'
import test from 'node:test'

import {
  planR2ProceduralWoodAccessories,
  planR2DriverProceduralWoodSurfaces,
  planR2ProceduralWoodModuleSurfaces,
  resolveModelParameters
} from './manifold_model.mjs'
import {
  clipProceduralWoodPlan,
  loadProceduralWoodConfig,
  planProceduralWoodRegion,
  validateProceduralWoodConfig
} from './procedural_wood.mjs'

const configPath = fileURLToPath(new URL('../config/wood-texture-params.json', import.meta.url))
const modelParamsPath = fileURLToPath(new URL('../config/model-params.json', import.meta.url))

function configCopy () {
  return structuredClone(loadProceduralWoodConfig(configPath))
}

function modelParamsCopy () {
  return resolveModelParameters(JSON.parse(fs.readFileSync(modelParamsPath, 'utf8')))
}

function planPaths (plan) {
  return [
    ...plan.paths,
    ...plan.knots.flatMap(knot => knot.contours)
  ]
}

function planGroup (plan, id) {
  return plan.groups.find(group => group.id === id)
}

function uniqueSorted (values) {
  return [...new Set(values)].sort()
}

function rectanglesOverlap (first, second) {
  return first.min[0] < second.max[0] && first.max[0] > second.min[0] &&
    first.min[1] < second.max[1] && first.max[1] > second.min[1]
}

function pointInsideRectangle (point, rectangle, tolerance = 1.0e-6) {
  return point[0] >= rectangle.min[0] - tolerance && point[0] <= rectangle.max[0] + tolerance &&
    point[1] >= rectangle.min[1] - tolerance && point[1] <= rectangle.max[1] + tolerance
}

function pointOnPolyline (point, points, tolerance = 2.0e-6) {
  for (let index = 1; index < points.length; index += 1) {
    const start = points[index - 1]
    const end = points[index]
    const delta = [end[0] - start[0], end[1] - start[1]]
    const lengthSquared = delta[0] ** 2 + delta[1] ** 2
    if (lengthSquared === 0) continue
    const fraction = Math.max(0, Math.min(1, (
      (point[0] - start[0]) * delta[0] + (point[1] - start[1]) * delta[1]
    ) / lengthSquared))
    const closest = [start[0] + fraction * delta[0], start[1] + fraction * delta[1]]
    if (Math.hypot(point[0] - closest[0], point[1] - closest[1]) <= tolerance) return true
  }
  return false
}

function sourcePlanForTarget (group, target) {
  return group.plans.find(plan => plan.coherence.source_field_id === target.source_id)
}

test('loads the strict v1 procedural wood source config', () => {
  const config = loadProceduralWoodConfig(configPath)
  assert.equal(config.schema, 'organizer-procedural-wood-texture-v1')
  assert.equal(config.surface_policy.operation, 'engrave-only')
  assert.equal(config.surface_policy.repeat, 'none-deterministic-global-field')
  assert.equal(config.surface_policy.outer_walls, 'smooth-no-geometric-texture')
})

test('validator rejects schema, dimensions, depth, width, and ordering failures', async t => {
  const failures = [
    ['schema', config => { config.schema = 'other-schema' }, /unsupported procedural wood schema/],
    ['non-finite process dimension', config => { config.process.nozzle_mm = Infinity }, /finite and positive/],
    ['non-positive grain dimension', config => { config.grain.path_segment_max_mm = 0 }, /finite and positive/],
    ['floor depth', config => { config.grain.floor_depth_mm = 0.201 }, /exceeds 0.20 mm/],
    ['wall depth', config => { config.grain.inner_wall_depth_mm = 0.161 }, /exceeds 0.16 mm/],
    ['top depth', config => { config.grain.top_depth_mm = 0.201 }, /exceeds 0.20 mm/],
    ['two-line-width rule', config => { config.grain.groove_width_mm = 0.89 }, /two nominal line widths/],
    ['spacing ordering', config => { config.grain.spacing_min_mm = config.grain.spacing_max_mm }, /spacing range/],
    ['wavelength ordering', config => { config.grain.wavelength_min_mm = config.grain.wavelength_max_mm }, /wavelength range/],
    ['drift ordering', config => { config.grain.lateral_drift_min_mm = config.grain.lateral_drift_max_mm }, /drift range/],
    ['drift before spacing', config => { config.grain.lateral_drift_max_mm = config.grain.spacing_min_mm }, /drift must be smaller/],
    ['spacing before wavelength', config => { config.grain.spacing_max_mm = config.grain.wavelength_min_mm }, /spacing must be smaller/]
  ]
  for (const [name, mutate, expected] of failures) {
    await t.test(name, () => {
      const config = configCopy()
      mutate(config)
      assert.throws(() => validateProceduralWoodConfig(config), expected)
    })
  }
})

test('validator enforces exact engrave-only, no-repeat, and smooth outer-wall policy', async t => {
  const failures = [
    ['operation', 'operation', 'emboss', /operation/],
    ['repeat', 'repeat', 'tile', /repeat/],
    ['outer wall', 'outer_walls', 'engraved', /outer_walls/]
  ]
  for (const [name, key, value, expected] of failures) {
    await t.test(name, () => {
      const config = configCopy()
      config.surface_policy[key] = value
      assert.throws(() => validateProceduralWoodConfig(config), expected)
    })
  }
})

test('validator enforces knot count, diameter, placement, and external-input constraints', async t => {
  const failures = [
    ['count', config => { config.knots.assembly_max = 2 }, /assembly_max/],
    ['diameter range', config => { config.knots.placements[0].diameter_mm = 25 }, /diameter_range/],
    ['floor module', config => { config.knots.placements[0].module = 'outer-wall' }, /floor module/],
    ['placement reserve', config => { config.knots.placements[0].center_global_xy_mm = [2, 2] }, /non-negative assembly coordinates/],
    ['forbidden source input', config => { config.heightmap_input = 'wood.png' }, /forbidden external surface input/]
  ]
  for (const [name, mutate, expected] of failures) {
    await t.test(name, () => {
      const config = configCopy()
      mutate(config)
      assert.throws(() => validateProceduralWoodConfig(config), expected)
    })
  }
})

test('saved seed produces byte-stable plans and a changed seed changes the plan', () => {
  const config = configCopy()
  const region = {
    id: 'determinism-floor',
    surface: 'floor',
    rectangle_mm: { min: [10, 20], max: [48, 96] },
    depth_mm: 0.16
  }
  const first = JSON.stringify(planProceduralWoodRegion(config, region))
  const second = JSON.stringify(planProceduralWoodRegion(config, region))
  const changed = JSON.stringify(planProceduralWoodRegion(config, region, { seed: config.seed + 1 }))
  assert.equal(first, second)
  assert.notEqual(first, changed)
})

test('plan-once clipping preserves parent geometry and half-width keepout clearance deterministically', () => {
  const config = configCopy()
  const sourceRegion = {
    id: 'synthetic-global-floor-field',
    surface: 'floor',
    rectangle_mm: { min: [0, 0], max: [40, 80] }
  }
  const allowed = [
    { id: 'before-keepout', rectangle_mm: { min: [0, 0], max: [40, 35] } },
    { id: 'after-keepout', rectangle_mm: { min: [0, 45], max: [40, 80] } }
  ]
  const source = planProceduralWoodRegion(config, sourceRegion)
  const clipped = clipProceduralWoodPlan(source, allowed)
  const repeated = clipProceduralWoodPlan(planProceduralWoodRegion(config, sourceRegion), allowed)
  const changed = clipProceduralWoodPlan(
    planProceduralWoodRegion(config, sourceRegion, { seed: config.seed + 1 }),
    allowed
  )
  assert.equal(JSON.stringify(clipped), JSON.stringify(repeated))
  assert.notEqual(JSON.stringify(clipped), JSON.stringify(changed))
  assert.equal(clipped.policy.coherence_policy, 'plan-once-then-clip')
  assert.equal(clipped.coherence.coherence_policy, 'plan-once-then-clip')
  assert.equal(clipped.coherence.source_field_id, sourceRegion.id)

  const sourceById = new Map(source.paths.map(path => [path.id, path]))
  const clipsByParent = new Map()
  const radius = config.grain.groove_width_mm / 2
  for (const path of clipped.paths) {
    assert.ok(sourceById.has(path.parent_path_id))
    assert.ok(clipped.coherence.parent_path_ids.includes(path.parent_path_id))
    assert.ok(path.points_mm.length >= 2)
    for (let index = 1; index < path.points_mm.length; index += 1) {
      assert.notDeepEqual(path.points_mm[index - 1], path.points_mm[index])
    }
    for (const point of path.points_mm) {
      assert.ok(pointOnPolyline(point, sourceById.get(path.parent_path_id).points_mm))
      assert.ok(point[1] <= 35 - radius + 1.0e-6 || point[1] >= 45 + radius - 1.0e-6)
    }
    if (!clipsByParent.has(path.parent_path_id)) clipsByParent.set(path.parent_path_id, new Set())
    clipsByParent.get(path.parent_path_id).add(path.clip_rectangle_id)
  }
  assert.ok([...clipsByParent.values()].some(ids => (
    ids.has('before-keepout') && ids.has('after-keepout')
  )))
})

test('plans carry constrained width/depth and floor grain runs globally in positive Y', () => {
  const config = configCopy()
  const plan = planProceduralWoodRegion(config, {
    id: 'floor-depth-sample',
    surface: 'floor',
    rectangle_mm: { min: [4, 4], max: [28, 37] },
    depth_mm: 0.12
  })
  assert.deepEqual(plan.region.direction, { mode: 'global-positive-y', vector: [0, 1] })
  assert.equal(plan.policy.operation, 'engrave-only')
  assert.equal(plan.policy.rounded_cutters, true)
  assert.ok(plan.paths.length > 0)
  for (const path of planPaths(plan)) {
    assert.ok(path.width_mm >= 2 * config.process.nominal_line_width_mm)
    assert.equal(path.depth_mm, 0.12)
    assert.ok(path.points_mm[0][1] < path.points_mm.at(-1)[1])
  }
})

test('wall and top plans use a generic local long axis and never create knots', () => {
  const config = configCopy()
  const wall = planProceduralWoodRegion(config, {
    id: 'wall-local',
    surface: 'wall',
    rectangle_mm: { min: [0, 4], max: [48, 18] }
  })
  const top = planProceduralWoodRegion(config, {
    id: 'top-local',
    surface: 'top',
    rectangle_mm: { min: [0, 0], max: [42, 5] }
  })
  assert.deepEqual(wall.region.direction, { mode: 'local-long-axis', vector: [1, 0] })
  assert.deepEqual(top.region.direction, { mode: 'local-long-axis', vector: [1, 0] })
  assert.deepEqual(wall.knots, [])
  assert.deepEqual(top.knots, [])
  assert.throws(() => planProceduralWoodRegion(config, {
    id: 'invalid-wall-knot',
    surface: 'wall',
    rectangle_mm: { min: [0, 0], max: [48, 18] },
    module: 'driver-front',
    include_knots: true
  }), /only on floor/)
})

test('a partial floor knot is absent rather than clipped open or replanned', () => {
  const config = configCopy()
  config.knots.placements[0].center_global_xy_mm = [31, 101]
  config.knots.placements[0].diameter_mm = 24
  validateProceduralWoodConfig(config)
  const rectangle = { min: [30, 100], max: [45, 113] }
  const plan = planProceduralWoodRegion(config, {
    id: 'clipped-floor-knot',
    surface: 'floor',
    rectangle_mm: rectangle,
    module: 'driver-front',
    include_knots: true
  })
  assert.deepEqual(plan.knots, [])
})

test('a fully safe floor knot retains every complete nested closed contour', () => {
  const config = configCopy()
  const rectangle = { min: [30, 104], max: [62, 132] }
  const plan = planProceduralWoodRegion(config, {
    id: 'whole-safe-floor-knot',
    surface: 'floor',
    rectangle_mm: rectangle,
    module: 'driver-front',
    include_knots: true
  })
  assert.equal(plan.knots.length, 1)
  assert.equal(plan.knots[0].contours.length, config.knots.nested_contours)
  const inset = config.grain.groove_width_mm / 2
  const centerlineRectangle = {
    min: rectangle.min.map(value => value + inset),
    max: rectangle.max.map(value => value - inset)
  }
  for (const contour of plan.knots[0].contours) {
    assert.equal(contour.surface, 'floor')
    assert.equal(contour.closed, true)
    assert.deepEqual(contour.points_mm[0], contour.points_mm.at(-1))
    assert.equal(contour.parent_path_id, contour.id)
    assert.ok(contour.points_mm.every(point => pointInsideRectangle(point, centerlineRectangle)))
  }
})

test('serialized plans declare parameter-only engrave metadata and no external dependencies', () => {
  const plan = planProceduralWoodRegion(configCopy(), {
    id: 'dependency-check',
    surface: 'floor',
    rectangle_mm: { min: [0, 0], max: [40, 60] }
  })
  assert.equal(plan.policy.operation, 'engrave-only')
  assert.equal(plan.policy.input_mode, 'parameters-only')
  assert.deepEqual(plan.policy.input_dependencies, [])
  const serialized = JSON.stringify(plan).toLowerCase()
  assert.equal(serialized.includes('raster'), false)
  assert.equal(serialized.includes('heightmap'), false)
  assert.equal(serialized.includes('emboss'), false)
})

test('R2 DRIVER surface plans expose only bounded floor, inner-wall, and top engrave groups', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  for (const moduleId of ['driver-front', 'driver-back']) {
    const plan = planR2DriverProceduralWoodSurfaces(params, config, moduleId)
    assert.equal(plan.schema, 'organizer-r2-procedural-wood-module-plan-v1')
    assert.equal(plan.module.id, moduleId)
    assert.equal(plan.policy.operation, 'engrave-only')
    assert.equal(plan.policy.texture_additions, false)
    assert.deepEqual(plan.groups.map(group => group.id), ['floor', 'inner-wall', 'top'])
    assert.ok(plan.groups.every(group => group.plans.length > 0))

    const namedSurfaces = []
    for (const group of plan.groups) {
      namedSurfaces.push(group.surface)
      for (const surfacePlan of group.plans) {
        namedSurfaces.push(surfacePlan.region.surface)
        assert.equal(surfacePlan.policy.operation, 'engrave-only')
        assert.ok(surfacePlan.paths.length + surfacePlan.knots.length > 0)
        if (group.id === 'floor') {
          assert.deepEqual(surfacePlan.region.direction, { mode: 'global-positive-y', vector: [0, 1] })
        } else {
          assert.deepEqual(surfacePlan.knots, [])
        }
        for (const path of planPaths(surfacePlan)) {
          namedSurfaces.push(path.surface)
          assert.equal(surfacePlan.policy.operation, 'engrave-only')
        }
      }
    }
    for (const surface of namedSurfaces) {
      assert.doesNotMatch(surface, /outside|underside|connector|watermark/i)
    }
  }
})

test('R2 DRIVER knot planning is floor-only and module-scoped', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  const front = planR2DriverProceduralWoodSurfaces(params, config, 'driver-front')
  const back = planR2DriverProceduralWoodSurfaces(params, config, 'driver-back')
  const knotsByGroup = plan => Object.fromEntries(plan.groups.map(group => [
    group.id,
    group.plans.flatMap(surfacePlan => surfacePlan.knots)
  ]))
  const frontKnots = knotsByGroup(front)
  const backKnots = knotsByGroup(back)
  assert.equal(frontKnots.floor.length, 1)
  assert.ok(frontKnots.floor.every(knot => knot.module === 'driver-front'))
  assert.deepEqual(frontKnots['inner-wall'], [])
  assert.deepEqual(frontKnots.top, [])
  assert.deepEqual(backKnots.floor, [])
  assert.deepEqual(backKnots['inner-wall'], [])
  assert.deepEqual(backKnots.top, [])
  assert.throws(
    () => planR2DriverProceduralWoodSurfaces(params, config, 'hardware-front'),
    /only driver-front or driver-back/
  )
})

test('generic R2 planner accepts all four module ids and rejects any other route', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  for (const moduleId of ['driver-front', 'driver-back', 'hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    assert.equal(plan.module.id, moduleId)
    assert.deepEqual(plan.groups.map(group => group.id), ['floor', 'inner-wall', 'top'])
    assert.equal(plan.policy.operation, 'engrave-only')
    assert.equal(plan.policy.texture_additions, false)
    assert.deepEqual(plan.policy.input_dependencies, [])
  }
  assert.throws(
    () => planR2ProceduralWoodModuleSurfaces(params, config, 'hardware-middle'),
    /unknown module id/
  )
})

test('all four modules clip one identical assembly-global floor source field', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  const fields = []
  for (const moduleId of ['driver-front', 'driver-back', 'hardware-front', 'hardware-back']) {
    const floor = planGroup(planR2ProceduralWoodModuleSurfaces(params, config, moduleId), 'floor')
    assert.equal(floor.plans.length, 1)
    const sourcePlan = floor.plans[0]
    assert.equal(sourcePlan.coherence.coherence_policy, 'plan-once-then-clip')
    assert.equal(sourcePlan.policy.coherence_policy, 'plan-once-then-clip')
    assert.equal(sourcePlan.coherence.clip_rectangles.length, floor.targets.length)
    assert.deepEqual(
      uniqueSorted(sourcePlan.coherence.clip_rectangles.map(clip => clip.id)),
      uniqueSorted(floor.targets.map(target => target.region_id))
    )
    fields.push({
      id: sourcePlan.coherence.source_field_id,
      rectangle: sourcePlan.coherence.source_rectangle_mm
    })
  }
  assert.equal(new Set(fields.map(field => field.id)).size, 1)
  assert.equal(fields[0].id, 'assembly-global-organizer-floor')
  assert.equal(new Set(fields.map(field => JSON.stringify(field.rectangle))).size, 1)

  const driverBackFloor = planGroup(
    planR2ProceduralWoodModuleSurfaces(params, config, 'driver-back'),
    'floor'
  )
  assert.ok(driverBackFloor.targets.length > 1)
  assert.ok(driverBackFloor.plans.every(plan => !/driver-back-floor-0[1-4]/.test(plan.region.id)))
  assert.ok(driverBackFloor.plans.every(plan => plan.region.id === 'assembly-global-organizer-floor'))
})

test('hardware plans cover four owned floors and exact visible inner-wall and top classes', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  for (const moduleId of ['hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    assert.equal(plan.module.kind, 'hardware')
    const floor = planGroup(plan, 'floor')
    const innerWall = planGroup(plan, 'inner-wall')
    const top = planGroup(plan, 'top')
    assert.deepEqual(floor.face_classes, ['hardware-compartment-floor'])
    assert.deepEqual(uniqueSorted(floor.targets.map(target => target.source_id)), ['assembly-global-organizer-floor'])
    assert.equal(floor.plans.length, 1)
    assert.equal(floor.plans[0].coherence.clip_rectangles.length, floor.targets.length)
    assert.deepEqual(
      uniqueSorted(innerWall.face_classes),
      uniqueSorted([
        'inner-wall-outer-right',
        'inner-wall-center-divider-negative-x-face',
        'inner-wall-center-divider-positive-x-face',
        'inner-wall-owned-row-negative-y-face',
        'inner-wall-owned-row-positive-y-face',
        `inner-wall-physical-${moduleId.endsWith('front') ? 'front' : 'back'}`
      ])
    )
    assert.deepEqual(
      uniqueSorted(top.face_classes),
      uniqueSorted([
        'top-outer-right-rim',
        'top-center-divider',
        'top-owned-row-divider',
        `top-physical-${moduleId.endsWith('front') ? 'front' : 'back'}-rim`
      ])
    )
    assert.ok(plan.groups.every(group => (
      group.plans.length === uniqueSorted(group.targets.map(target => target.source_id)).length
    )))
    assert.ok(plan.groups.every(group => group.plans.length > 0))
  }
})

test('hardware plans exclude outer, underside, connector, watermark, root, junction, and access-groove surfaces', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  const forbiddenTarget = /external|outside|underside|bed-plane|connector|pass-face|watermark|wall-root|junction-blend|access-groove/i
  for (const moduleId of ['hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    assert.deepEqual(plan.policy.excluded_surface_classes, [
      'external-outer-face',
      'underside-bed-plane',
      'module-split-connector-pass-face',
      'watermark-region',
      'wall-root',
      'junction-blend',
      'access-groove-and-rounded-transition'
    ])
    for (const group of plan.groups) {
      for (const target of group.targets) {
        assert.doesNotMatch(`${target.face_class} ${target.source_id} ${target.region_id}`, forbiddenTarget)
      }
      for (const surfacePlan of group.plans) {
        assert.doesNotMatch(surfacePlan.region.id, forbiddenTarget)
        assert.equal(surfacePlan.policy.operation, 'engrave-only')
        assert.equal(surfacePlan.policy.outer_walls, 'smooth-no-geometric-texture')
      }
    }
  }
})

test('hardware wall bands use floor plus 4 mm and actual wall top minus 2 mm', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  const expectedBottom = params.organizer.floor_thickness + config.grain.wall_bottom_clearance_from_floor_mm
  for (const moduleId of ['hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    for (const target of planGroup(plan, 'inner-wall').targets) {
      assert.equal(target.rectangle_mm.min[1], expectedBottom)
      const usesOuterTop = target.face_class === 'inner-wall-outer-right' || target.face_class.startsWith('inner-wall-physical-')
      const actualTop = usesOuterTop ? params.organizer.outer_wall_height : params.organizer.divider_height
      assert.equal(target.rectangle_mm.max[1], actualTop - config.grain.wall_top_clearance_mm)
    }
  }
})

test('hardware top grooves stay on narrow safe strips centered on each owning wall', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  const stripWidth = config.grain.groove_width_mm + 2 * config.grain.top_centerline_drift_mm
  for (const moduleId of ['hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    for (const target of planGroup(plan, 'top').targets) {
      const shortAxis = ['top-outer-right-rim', 'top-center-divider'].includes(target.face_class) ? 0 : 1
      const actualWidth = target.rectangle_mm.max[shortAxis] - target.rectangle_mm.min[shortAxis]
      assert.ok(Math.abs(actualWidth - stripWidth) < 1.0e-9)
      const sourcePlan = sourcePlanForTarget(planGroup(plan, 'top'), target)
      assert.ok(sourcePlan)
      const clip = sourcePlan.coherence.clip_rectangles.find(item => item.id === target.region_id)
      assert.ok(clip)
      for (const path of sourcePlan.paths.filter(path => path.clip_rectangle_id === target.region_id)) {
        for (const point of path.points_mm) {
          assert.ok(pointInsideRectangle(point, clip.inset_centerline_rectangle_mm))
        }
      }
    }
  }
})

test('hardware-back floor plans keep the 2 mm floor margin while excluding both female connector pass regions', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  const plan = planR2ProceduralWoodModuleSurfaces(params, config, 'hardware-back')
  const floor = planGroup(plan, 'floor')
  const floorPlans = floor.plans
  const margin = config.grain.floor_margin_mm
  const connectorRadius = params.connectors.lug_radius + params.connectors.clearance
  const keepouts = [122, 196].map(x => ({
    min: [x - connectorRadius - margin, params.layout.depth_split],
    max: [x + connectorRadius + margin, params.layout.depth_split + params.connectors.lug_radius + connectorRadius + margin]
  }))
  assert.equal(floorPlans.length, 1)
  assert.ok(floor.targets.some(target => target.rectangle_mm.min[1] === params.layout.depth_split + margin))
  for (const clip of floorPlans[0].coherence.clip_rectangles) {
    for (const keepout of keepouts) assert.equal(rectanglesOverlap(clip.rectangle_mm, keepout), false)
    for (const path of floorPlans[0].paths.filter(path => path.clip_rectangle_id === clip.id)) {
      assert.ok(path.points_mm.every(point => pointInsideRectangle(point, clip.inset_centerline_rectangle_mm)))
    }
  }
})

test('every Y-wall and matching top-strip plan excludes both U-grooves plus the configured 4 mm margin', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  for (const moduleId of ['hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    const grooveTargets = [
      ...planGroup(plan, 'inner-wall').targets,
      ...planGroup(plan, 'top').targets
    ].filter(target => target.access_groove_keepouts_mm.length > 0)
    assert.ok(grooveTargets.length > 0)
    for (const target of grooveTargets) {
      assert.equal(target.access_groove_keepouts_mm.length, 2)
      for (const keepout of target.access_groove_keepouts_mm) {
        assert.equal(keepout.groove_half_width_mm, params.layout.access_groove_width / 2)
        assert.equal(keepout.extra_margin_mm, 4.0)
        assert.ok(Math.abs((keepout.max - keepout.min) - (params.layout.access_groove_width + 2 * 4.0)) < 1.0e-9)
        const [minimum, maximum] = [target.rectangle_mm.min[0], target.rectangle_mm.max[0]]
        assert.ok(maximum <= keepout.min || minimum >= keepout.max)
      }
    }
    const sources = uniqueSorted(grooveTargets.map(target => target.source_id))
    const ownedRowCount = moduleId === 'hardware-front' ? 2 : 1
    assert.equal(sources.filter(source => source.includes('inner-wall-row-divider')).length, 2 * ownedRowCount)
    assert.equal(sources.filter(source => source.includes('top-row-divider')).length, ownedRowCount)
    assert.equal(sources.some(source => source.includes('physical-front')), moduleId === 'hardware-front')
    assert.equal(sources.some(source => source.includes('physical-back')), false)
  }
})

test('split Y-wall and top targets have one plan-once source plan per physical face', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  for (const moduleId of ['hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    for (const groupId of ['inner-wall', 'top']) {
      const group = planGroup(plan, groupId)
      const targetCounts = new Map()
      for (const target of group.targets) {
        targetCounts.set(target.source_id, (targetCounts.get(target.source_id) ?? 0) + 1)
      }
      const splitSources = [...targetCounts].filter(([, count]) => count > 1).map(([sourceId]) => sourceId)
      assert.ok(splitSources.length > 0)
      for (const sourceId of splitSources) {
        const sourcePlans = group.plans.filter(item => item.coherence.source_field_id === sourceId)
        assert.equal(sourcePlans.length, 1)
        const sourcePlan = sourcePlans[0]
        assert.equal(sourcePlan.coherence.coherence_policy, 'plan-once-then-clip')
        assert.equal(sourcePlan.policy.coherence_policy, 'plan-once-then-clip')
        assert.equal(sourcePlan.coherence.clip_rectangles.length, targetCounts.get(sourceId))
        const clipsByParent = new Map()
        for (const path of sourcePlan.paths) {
          if (!clipsByParent.has(path.parent_path_id)) clipsByParent.set(path.parent_path_id, new Set())
          clipsByParent.get(path.parent_path_id).add(path.clip_rectangle_id)
        }
        assert.ok([...clipsByParent.values()].some(clipIds => clipIds.size > 1))
      }
    }
  }
})

test('hardware knots stay floor-only, module-scoped, fully inside one allowed floor patch, and outside mark keepouts', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  for (const moduleId of ['hardware-front', 'hardware-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    const floor = planGroup(plan, 'floor')
    const knots = floor.plans.flatMap(surfacePlan => surfacePlan.knots)
    assert.equal(knots.length, 1)
    assert.ok(knots.every(knot => knot.module === moduleId && knot.surface === 'floor'))
    assert.deepEqual(planGroup(plan, 'inner-wall').plans.flatMap(surfacePlan => surfacePlan.knots), [])
    assert.deepEqual(planGroup(plan, 'top').plans.flatMap(surfacePlan => surfacePlan.knots), [])

    const placement = config.knots.placements.find(item => item.module === moduleId)
    const containingPlans = floor.plans.filter(surfacePlan => surfacePlan.knots.length > 0)
    assert.equal(containingPlans.length, 1)
    const retainedKnot = containingPlans[0].knots[0]
    const clip = containingPlans[0].coherence.clip_rectangles.find(item => item.id === retainedKnot.clip_rectangle_id)
    assert.ok(clip)
    assert.equal(retainedKnot.contours.length, config.knots.nested_contours)
    for (const contour of retainedKnot.contours) {
      assert.equal(contour.closed, true)
      assert.deepEqual(contour.points_mm[0], contour.points_mm.at(-1))
      assert.equal(contour.parent_path_id, contour.id)
      assert.ok(contour.points_mm.every(point => pointInsideRectangle(point, clip.inset_centerline_rectangle_mm)))
    }

    const markCenter = params.watermark.placements_global_xy[moduleId]
    const markEnvelope = params.watermark.actual_envelope
    const markMargin = params.surface_texture.watermark_keepout
    const markRectangle = {
      min: [markCenter[0] - markEnvelope[0] / 2 - markMargin, markCenter[1] - markEnvelope[1] / 2 - markMargin],
      max: [markCenter[0] + markEnvelope[0] / 2 + markMargin, markCenter[1] + markEnvelope[1] / 2 + markMargin]
    }
    assert.ok(floor.plans[0].coherence.clip_rectangles.every(item => !rectanglesOverlap(item.rectangle_mm, markRectangle)))
  }
})

test('driver plans add only the hardware-facing x=92 divider face above connector and bed contact', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  for (const moduleId of ['driver-front', 'driver-back']) {
    const plan = planR2ProceduralWoodModuleSurfaces(params, config, moduleId)
    const innerWall = planGroup(plan, 'inner-wall')
    assert.ok(innerWall.face_classes.includes('inner-wall-hardware-facing-divider'))
    const targets = innerWall.targets.filter(target => target.face_class === 'inner-wall-hardware-facing-divider')
    assert.ok(targets.length >= 1)
    for (const target of targets) {
      assert.deepEqual(target.plane, { axis: 'x', coordinate_mm: 92, normal: 1 })
      assert.ok(target.rectangle_mm.min[1] > params.organizer.floor_thickness)
      assert.equal(target.rectangle_mm.min[1], params.organizer.floor_thickness + config.grain.wall_bottom_clearance_from_floor_mm)
      assert.equal(target.rectangle_mm.max[1], params.organizer.outer_wall_height - config.grain.wall_top_clearance_mm)
      assert.doesNotMatch(target.source_id, /connector|underside|bed|external/i)
    }
    const otherDriverClasses = innerWall.face_classes.filter(faceClass => faceClass !== 'inner-wall-hardware-facing-divider')
    assert.deepEqual(uniqueSorted(otherDriverClasses), uniqueSorted([
      'inner-wall-outer-left',
      'inner-wall-driver-facing-divider',
      `inner-wall-physical-${moduleId.endsWith('front') ? 'front' : 'back'}`
    ]))
  }
})

test('R2 comb plan has exactly seven safe +Y engrave-only top bridge regions and no knots', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  const plan = planR2ProceduralWoodAccessories(params, config)
  const bridges = plan.comb.bridge_regions
  const grooveHalfWidth = config.grain.groove_width_mm / 2
  const expectedPitch = (params.comb.width - 2 * params.comb.slot_radius) / (params.comb.slot_count - 1)

  assert.equal(plan.schema, 'organizer-r2-procedural-wood-accessories-plan-v1')
  assert.equal(plan.policy.operation, 'engrave-only')
  assert.equal(plan.policy.texture_additions, false)
  assert.equal(plan.policy.top_depth_mm, 0.20)
  assert.equal(plan.policy.groove_width_mm, 0.90)
  assert.deepEqual(plan.policy.direction, { mode: 'local-long-axis-positive-y', vector: [0, 1] })
  assert.equal(plan.comb.slot_count, 8)
  assert.equal(plan.comb.slot_radius_mm, params.comb.slot_radius)
  assert.equal(plan.comb.slot_pitch_mm, expectedPitch)
  assert.equal(plan.comb.bridge_count, 7)
  assert.equal(bridges.length, 7)
  assert.deepEqual(plan.policy.excluded_surface_classes, [
    'floor',
    'wall',
    'outer-face',
    'underside-bed-plane',
    'slot-bore-and-cut-face',
    'fit-and-contact-face'
  ])

  for (const [index, bridge] of bridges.entries()) {
    assert.equal(bridge.face_class, 'comb-safe-upward-top-bridge')
    assert.doesNotMatch(bridge.face_class, /floor|wall|outer|underside|slot|fit|contact/i)
    assert.deepEqual(bridge.adjacent_slot_numbers, [index + 1, index + 2])
    assert.ok(bridge.slot_edge_clearance_mm > 0)
    assert.equal(bridge.slot_edge_clearance_mm, config.grain.top_centerline_drift_mm)
    assert.equal(bridge.groove_half_width_mm, grooveHalfWidth)
    assert.equal(
      bridge.centerline_reserve_from_each_slot_boundary_mm,
      grooveHalfWidth + bridge.slot_edge_clearance_mm
    )
    assert.ok(bridge.remaining_safe_width_mm >= config.grain.groove_width_mm)
    assert.equal(bridge.plan.region.surface, 'top')
    assert.deepEqual(bridge.plan.region.direction, { mode: 'local-long-axis', vector: [0, 1] })
    assert.equal(bridge.plan.policy.operation, 'engrave-only')
    assert.deepEqual(bridge.plan.knots, [])
    assert.equal(bridge.plan.paths.length, 1)
    const leftBoundary = bridge.slot_boundaries_x_mm.left_slot_right_edge
    const rightBoundary = bridge.slot_boundaries_x_mm.right_slot_left_edge
    const minimumCenterlineX = leftBoundary + grooveHalfWidth + bridge.slot_edge_clearance_mm
    const maximumCenterlineX = rightBoundary - grooveHalfWidth - bridge.slot_edge_clearance_mm
    for (const path of bridge.plan.paths) {
      assert.equal(path.width_mm, 0.90)
      assert.equal(path.depth_mm, 0.20)
      assert.ok(path.points_mm[0][1] < path.points_mm.at(-1)[1])
      for (const [x] of path.points_mm) {
        assert.ok(x >= minimumCenterlineX - 1.0e-6)
        assert.ok(x <= maximumCenterlineX + 1.0e-6)
      }
    }
  }
})

test('R2 accessory plan keeps every non-comb coupon untextured and avoids relief or watermark parameters', () => {
  const params = modelParamsCopy()
  const config = configCopy()
  delete params.relief
  delete params.watermark
  const plan = planR2ProceduralWoodAccessories(params, config)
  const artifacts = Object.fromEntries(plan.artifacts.map(artifact => [artifact.id, artifact]))

  assert.equal(artifacts['screwdriver-comb'].texture_plans.length, 7)
  assert.deepEqual(artifacts['drawer-fit-corner-coupon'].texture_plans, [])
  assert.deepEqual(artifacts['connector-coupon-male'].texture_plans, [])
  assert.deepEqual(artifacts['connector-coupon-female'].texture_plans, [])
  assert.deepEqual(plan.comb.smooth_keepouts, [
    'comb-slot-bores-and-cut-faces',
    'comb-slot-boundaries-plus-positive-clearance',
    'comb-fit-and-contact-faces',
    'comb-front-back-and-side-outer-faces',
    'comb-underside-and-bed-contact',
    'comb-non-upward-facing-surfaces'
  ])
})
