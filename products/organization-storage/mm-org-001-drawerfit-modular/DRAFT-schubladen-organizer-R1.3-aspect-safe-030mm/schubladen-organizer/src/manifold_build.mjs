#!/usr/bin/env node

import fs from 'node:fs'
import crypto from 'node:crypto'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { Manifold } from 'manifold-3d/manifoldCAD'

import {
  buildCombManifold,
  buildConnectorCouponManifold,
  buildFitCouponManifold,
  buildModulesManifold,
  buildProceduralWoodCouponManifold,
  buildR2AccessoriesManifolds,
  buildR2ProceduralWoodModuleManifold,
  buildReliefCouponManifold,
  resolveModelParameters
} from './manifold_model.mjs'
import { loadProceduralWoodConfig } from './procedural_wood.mjs'
import { sanitizeMeshForFloat32 } from './mesh_export.mjs'
import { watermarkOutline } from './watermark.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const R2_MODULE_IDS = [
  'driver-front',
  'driver-back',
  'hardware-front',
  'hardware-back'
]

function parseArgs () {
  const args = process.argv.slice(2)
  const valueAfter = (name, fallback = null) => {
    const index = args.indexOf(name)
    return index >= 0 ? args[index + 1] : fallback
  }
  return {
    quality: valueAfter('--quality', 'final'),
    module: valueAfter('--module'),
    r2Module: valueAfter('--r2-module'),
    r2ModuleFlag: args.includes('--r2-module'),
    r2Accessories: args.includes('--r2-accessories'),
    accessories: args.includes('--accessories'),
    woodCoupon: args.includes('--wood-coupon')
  }
}

function readJson (file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'))
}

function sha256File (file) {
  const hash = crypto.createHash('sha256')
  const fd = fs.openSync(file, 'r')
  const buffer = Buffer.allocUnsafe(1024 * 1024)
  try {
    while (true) {
      const bytesRead = fs.readSync(fd, buffer, 0, buffer.length, null)
      if (bytesRead === 0) break
      hash.update(buffer.subarray(0, bytesRead))
    }
  } finally {
    fs.closeSync(fd)
  }
  return hash.digest('hex')
}

function fileIdentity (file) {
  return {
    path: path.relative(root, file),
    sha256: sha256File(file)
  }
}

function r2InputIdentities (paramsPath, textureConfigPath) {
  return {
    design_spec: fileIdentity(path.join(root, 'design-spec.yaml')),
    model_params: fileIdentity(paramsPath),
    wood_config: fileIdentity(textureConfigPath),
    build_source: fileIdentity(path.join(root, 'src', 'manifold_build.mjs')),
    mesh_export: fileIdentity(path.join(root, 'src', 'mesh_export.mjs')),
    model_source: fileIdentity(path.join(root, 'src', 'manifold_model.mjs')),
    wood_planner: fileIdentity(path.join(root, 'src', 'procedural_wood.mjs'))
  }
}

function writeHeader (fd, headerText, triangleCount) {
  const header = Buffer.alloc(84)
  header.write(headerText.slice(0, 80), 0, 'ascii')
  header.writeUInt32LE(triangleCount, 80)
  fs.writeSync(fd, header)
}

function pointFromMesh (mesh, vertexId) {
  const offset = vertexId * mesh.numProp
  return [
    mesh.vertProperties[offset],
    mesh.vertProperties[offset + 1],
    mesh.vertProperties[offset + 2]
  ]
}

function writeIndexedMeshCache (file, mesh) {
  const fd = fs.openSync(file, 'w')
  try {
    const header = Buffer.alloc(16)
    header.write('MSH1', 0, 'ascii')
    header.writeUInt32LE(mesh.numVert, 4)
    header.writeUInt32LE(mesh.numTri, 8)
    header.writeUInt32LE(3, 12)
    fs.writeSync(fd, header)
    const chunkVertices = 65536
    for (let first = 0; first < mesh.numVert; first += chunkVertices) {
      const count = Math.min(chunkVertices, mesh.numVert - first)
      const buffer = Buffer.allocUnsafe(count * 12)
      for (let index = 0; index < count; index += 1) {
        const source = (first + index) * mesh.numProp
        const target = index * 12
        buffer.writeFloatLE(mesh.vertProperties[source], target)
        buffer.writeFloatLE(mesh.vertProperties[source + 1], target + 4)
        buffer.writeFloatLE(mesh.vertProperties[source + 2], target + 8)
      }
      fs.writeSync(fd, buffer)
    }
    const chunkTriangles = 65536
    for (let first = 0; first < mesh.numTri; first += chunkTriangles) {
      const count = Math.min(chunkTriangles, mesh.numTri - first)
      const buffer = Buffer.allocUnsafe(count * 12)
      for (let index = 0; index < count; index += 1) {
        const source = (first + index) * 3
        const target = index * 12
        buffer.writeUInt32LE(mesh.triVerts[source], target)
        buffer.writeUInt32LE(mesh.triVerts[source + 1], target + 4)
        buffer.writeUInt32LE(mesh.triVerts[source + 2], target + 8)
      }
      fs.writeSync(fd, buffer)
    }
  } finally {
    fs.closeSync(fd)
  }
}

function writeBinaryStl (file, manifold, headerText, simplifyTolerance = 0, meshCacheFile = null) {
  const exportManifold = simplifyTolerance > 0 ? manifold.simplify(simplifyTolerance) : manifold
  const roundedMesh = exportManifold.getMesh()
  roundedMesh.merge()
  const reconstructed = Manifold.ofMesh(roundedMesh)
  const rawMesh = reconstructed.getMesh()
  const sanitized = sanitizeMeshForFloat32(rawMesh)
  const mesh = sanitized.mesh
  const fd = fs.openSync(file, 'w')
  const chunkTriangles = 32768
  try {
    writeHeader(fd, headerText, mesh.numTri)
    for (let first = 0; first < mesh.numTri; first += chunkTriangles) {
      const count = Math.min(chunkTriangles, mesh.numTri - first)
      const buffer = Buffer.allocUnsafe(count * 50)
      for (let index = 0; index < count; index += 1) {
        const triangle = first + index
        const ids = [
          mesh.triVerts[triangle * 3],
          mesh.triVerts[triangle * 3 + 1],
          mesh.triVerts[triangle * 3 + 2]
        ]
        const points = ids.map(id => pointFromMesh(mesh, id))
        const ab = points[1].map((value, axis) => value - points[0][axis])
        const ac = points[2].map((value, axis) => value - points[0][axis])
        const normal = [
          ab[1] * ac[2] - ab[2] * ac[1],
          ab[2] * ac[0] - ab[0] * ac[2],
          ab[0] * ac[1] - ab[1] * ac[0]
        ]
        const length = Math.hypot(...normal) || 1
        const offset = index * 50
        for (let axis = 0; axis < 3; axis += 1) buffer.writeFloatLE(normal[axis] / length, offset + axis * 4)
        for (let vertex = 0; vertex < 3; vertex += 1) {
          for (let axis = 0; axis < 3; axis += 1) {
            buffer.writeFloatLE(points[vertex][axis], offset + 12 + (vertex * 3 + axis) * 4)
          }
        }
        buffer.writeUInt16LE(0, offset + 48)
      }
      fs.writeSync(fd, buffer)
    }
  } finally {
    fs.closeSync(fd)
  }
  if (meshCacheFile) writeIndexedMeshCache(meshCacheFile, mesh)
  const result = {
    triangles: mesh.numTri,
    vertices: mesh.numVert,
    dropped_zero_area_triangles: sanitized.report.dropped_zero_area_triangles,
    float32_sanitization: sanitized.report
  }
  reconstructed.delete()
  if (exportManifold !== manifold) exportManifold.delete()
  return result
}

function statsWithoutMeshCopy (manifold, meshStats) {
  const bounds = manifold.boundingBox()
  return {
    status: manifold.status(),
    bounds,
    size_mm: bounds.max.map((value, axis) => value - bounds.min[axis]),
    volume_mm3: manifold.volume(),
    triangles: meshStats.triangles,
    vertices: meshStats.vertices
  }
}

function memoryReport (mode) {
  let maxRssMib
  let measurement
  try {
    const status = fs.readFileSync('/proc/self/status', 'utf8')
    const match = /^VmHWM:\s+(\d+)\s+kB$/m.exec(status)
    if (!match) throw new Error('VmHWM is unavailable')
    maxRssMib = Number(match[1]) / 1024
    measurement = '/proc/self/status VmHWM; peak resident set for this isolated Linux Node/WASM process'
  } catch {
    maxRssMib = process.resourceUsage().maxRSS / 1024
    measurement = 'process.resourceUsage().maxRSS fallback; peak resident set for this isolated Node/WASM process'
  }
  return {
    mode,
    pid: process.pid,
    max_rss_mib: maxRssMib,
    measurement
  }
}

function baseReport (params, paramsPath, manifestPath, preview, markOutline) {
  return {
    status: 'DRAFT',
    quality: preview ? 'preview' : 'final',
    engine: 'manifold-3d',
    revision: params.model_revision,
    execution_strategy: 'one-module-per-process; one-relief-surface-at-a-time',
    params: path.relative(root, paramsPath),
    resolved_wall_thickness_mm: {
      base: params.organizer.base_wall_thickness,
      outer: params.organizer.outer_wall_thickness,
      divider: params.organizer.divider_thickness
    },
    relief_manifest: path.relative(root, manifestPath),
    watermark: preview
      ? { enabled: false }
      : {
          enabled: true,
          asset_id: params.watermark.asset_id,
          variant: params.watermark.variant,
          dxf: params.watermark.dxf,
          source_bounds: markOutline.source_bounds,
          actual_envelope_mm: markOutline.actual_envelope_mm,
          scale: params.watermark.uniform_scale,
          depth_mm: params.watermark.depth,
          residual_floor_mm: params.organizer.floor_thickness - params.watermark.depth
        },
    modules: []
  }
}

function main () {
  const args = parseArgs()
  if (args.r2ModuleFlag && !args.r2Module) throw new Error(`--r2-module requires one of: ${R2_MODULE_IDS.join(', ')}`)
  const routeCount = [Boolean(args.module), args.r2ModuleFlag, args.r2Accessories, args.accessories, args.woodCoupon].filter(Boolean).length
  if (routeCount > 1) throw new Error('--module, --r2-module, --r2-accessories, --accessories, and --wood-coupon are mutually exclusive')
  if (args.quality === 'final' && routeCount === 0) {
    throw new Error('final builds must select exactly one --module, --r2-module, --r2-accessories, --accessories, or --wood-coupon; use python3 src/build_pipeline.py')
  }
  const paramsPath = path.join(root, 'config', 'model-params.json')
  const params = resolveModelParameters(readJson(paramsPath))
  const preview = args.quality === 'preview'
  const segments = preview ? params.export.segments_preview : params.export.segments_final

  if (args.r2ModuleFlag) {
    if (!R2_MODULE_IDS.includes(args.r2Module)) {
      throw new Error(`--r2-module supports only: ${R2_MODULE_IDS.join(', ')}`)
    }
    if (!params.surface_texture?.enabled) throw new Error('--r2-module requires enabled surface_texture parameters')
    if (params.surface_texture.representation !== 'procedural-vector-wood-grooves') {
      throw new Error('--r2-module requires procedural-vector-wood-grooves representation')
    }
    if (params.surface_texture.apply_outer_walls !== false) throw new Error('--r2-module requires smooth outer wall faces')
    const textureConfigPath = path.resolve(path.dirname(paramsPath), params.surface_texture.config)
    const textureConfig = loadProceduralWoodConfig(textureConfigPath)
    const outputDir = path.join(root, 'output', 'DRAFT')
    const reportDir = path.join(root, 'reports')
    const cacheDir = path.join(reportDir, 'mesh-cache')
    fs.mkdirSync(outputDir, { recursive: true })
    fs.mkdirSync(reportDir, { recursive: true })
    fs.mkdirSync(cacheDir, { recursive: true })
    const built = buildR2ProceduralWoodModuleManifold(params, textureConfig, args.r2Module, { segments })
    const globalBounds = built.solid.boundingBox()
    if (Math.abs(globalBounds.min[2]) > 1.0e-6) throw new Error('R2 module assembly geometry no longer preserves bed plane z=0')
    const localTranslation = [-built.def.bounds[0], -built.def.bounds[2], 0]
    const local = built.solid.translate(localTranslation)
    const outputFile = path.join(outputDir, `DRAFT-R2-${args.r2Module}-procedural-wood-unmarked.stl`)
    const cacheFile = path.join(cacheDir, `R2-${args.r2Module}-procedural-wood-unmarked.meshbin`)
    const meshStats = writeBinaryStl(
      outputFile,
      local,
      `DRAFT R2 ${args.r2Module} procedural wood unmarked`,
      params.export.stl_simplify_tolerance_mm,
      cacheFile
    )
    const metrics = statsWithoutMeshCopy(local, meshStats)
    if (Math.abs(metrics.bounds.min[2]) > 1.0e-6) throw new Error('R2 module local export no longer preserves bed plane z=0')
    const report = {
      status: 'DRAFT',
      quality: args.quality,
      engine: 'manifold-3d',
      revision: params.model_revision,
      route: 'r2-procedural-wood-module-only',
      execution_strategy: 'one-module-per-process; one-planned-surface-patch-per-boolean',
      params: path.relative(root, paramsPath),
      surface_texture_config: path.relative(root, textureConfigPath),
      surface_texture_config_identity: {
        schema: textureConfig.schema,
        representation: textureConfig.representation,
        seed: textureConfig.seed
      },
      surface_plan_identity: {
        schema: built.plan.schema,
        revision: built.plan.revision,
        module_id: built.plan.module.id,
        group_ids: built.plan.groups.map(group => group.id)
      },
      relief_loaded: false,
      watermark: { loaded: false, applied: false },
      module: {
        id: built.def.id,
        file: path.relative(root, outputFile),
        mesh_cache: path.relative(root, cacheFile),
        file_bytes: fs.statSync(outputFile).size,
        mesh_cache_bytes: fs.statSync(cacheFile).size,
        global_bounds_before_translation: globalBounds,
        local_translation_mm: localTranslation,
        ...metrics,
        export_mesh: meshStats,
        surface_plan: built.plan
      },
      identities: {
        inputs: r2InputIdentities(paramsPath, textureConfigPath),
        artifacts: {
          stl: fileIdentity(outputFile),
          mesh_cache: fileIdentity(cacheFile)
        }
      },
      process_memory: null,
      resource_budget: null
    }
    const reportFile = path.join(reportDir, `build-final-R2-${args.r2Module}-procedural-wood-unmarked.json`)
    JSON.stringify(report)
    report.process_memory = memoryReport(`r2-module:${args.r2Module}`)
    const peakBudget = textureConfig.resource_budget.max_peak_rss_mib_per_module
    report.resource_budget = {
      max_peak_rss_mib_per_module: peakBudget,
      measured_max_rss_mib: report.process_memory.max_rss_mib,
      status: report.process_memory.max_rss_mib <= peakBudget ? 'PASS' : 'FAIL'
    }
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + '\n')
    local.delete()
    built.solid.delete()
    if (report.resource_budget.status === 'FAIL') {
      const message = `R2 module resource budget exceeded: ${report.process_memory.max_rss_mib.toFixed(3)} MiB > ${peakBudget.toFixed(3)} MiB for ${args.r2Module}; DRAFT artifact and report retained`
      console.error(message)
      console.log(JSON.stringify({
        status: 'budget-error',
        quality: args.quality,
        r2_module: args.r2Module,
        file: report.module.file,
        report: path.relative(root, reportFile),
        process_memory: report.process_memory,
        resource_budget: report.resource_budget
      }))
      process.exitCode = 1
      return
    }
    console.log(JSON.stringify({
      status: 'ok',
      quality: args.quality,
      r2_module: args.r2Module,
      file: report.module.file,
      file_bytes: report.module.file_bytes,
      triangles: meshStats.triangles,
      mesh_cache: report.module.mesh_cache,
      bounds: metrics.bounds,
      volume_mm3: metrics.volume_mm3,
      process_memory: report.process_memory,
      resource_budget: report.resource_budget
    }))
    return
  }

  if (args.r2Accessories) {
    if (!params.surface_texture?.enabled) throw new Error('--r2-accessories requires enabled surface_texture parameters')
    if (params.surface_texture.representation !== 'procedural-vector-wood-grooves') {
      throw new Error('--r2-accessories requires procedural-vector-wood-grooves representation')
    }
    if (params.surface_texture.apply_comb_top_faces !== true) {
      throw new Error('--r2-accessories requires enabled comb top-face texture')
    }
    const textureConfigPath = path.resolve(path.dirname(paramsPath), params.surface_texture.config)
    const textureConfig = loadProceduralWoodConfig(textureConfigPath)
    const outputDir = path.join(root, 'output', 'DRAFT')
    const reportDir = path.join(root, 'reports')
    fs.mkdirSync(outputDir, { recursive: true })
    fs.mkdirSync(reportDir, { recursive: true })
    const built = buildR2AccessoriesManifolds(params, textureConfig, { segments })
    const filenames = {
      'screwdriver-comb': 'DRAFT-R2-screwdriver-comb-procedural-wood-unmarked.stl',
      'drawer-fit-corner-coupon': 'DRAFT-R2-drawer-fit-corner-coupon.stl',
      'connector-coupon-male': 'DRAFT-R2-connector-coupon-male.stl',
      'connector-coupon-female': 'DRAFT-R2-connector-coupon-female.stl'
    }
    const report = {
      status: 'DRAFT',
      quality: args.quality,
      engine: 'manifold-3d',
      revision: params.model_revision,
      route: 'r2-accessories-only',
      execution_strategy: 'accessories-only; one-comb-top-bridge-per-boolean; fit-and-connector-coupons-untextured',
      params: path.relative(root, paramsPath),
      surface_texture_config: path.relative(root, textureConfigPath),
      surface_texture_config_identity: {
        schema: textureConfig.schema,
        representation: textureConfig.representation,
        seed: textureConfig.seed
      },
      surface_plan_identity: {
        schema: built.plan.schema,
        revision: built.plan.revision,
        comb_bridge_region_ids: built.plan.comb.bridge_regions.map(region => region.id),
        artifact_ids: built.plan.artifacts.map(artifact => artifact.id)
      },
      relief_loaded: false,
      watermark: { loaded: false, applied: false },
      comb_smooth_keepouts: built.plan.comb.smooth_keepouts,
      comb_texture_plan: built.plan,
      artifacts: {},
      identities: {
        inputs: r2InputIdentities(paramsPath, textureConfigPath),
        artifacts: {}
      },
      process_memory: null,
      resource_budget: null
    }
    for (const artifact of built.artifacts) {
      const filename = filenames[artifact.id]
      if (!filename) throw new Error(`R2 accessory output name is unavailable for ${artifact.id}`)
      const outputFile = path.join(outputDir, filename)
      const meshStats = writeBinaryStl(
        outputFile,
        artifact.solid,
        `DRAFT R2 ${artifact.id} procedural wood unmarked`,
        params.export.stl_simplify_tolerance_mm
      )
      const metrics = statsWithoutMeshCopy(artifact.solid, meshStats)
      if (Math.abs(metrics.bounds.min[2]) > 1.0e-6) {
        throw new Error(`R2 accessory ${artifact.id} no longer preserves bed plane z=0`)
      }
      if (metrics.bounds.min[0] < -1.0e-6 || metrics.bounds.min[1] < -1.0e-6) {
        throw new Error(`R2 accessory ${artifact.id} is not in non-negative local bed coordinates`)
      }
      if (artifact.id === 'screwdriver-comb') {
        const expectedMaximum = [params.comb.width, params.comb.depth, params.comb.height]
        for (let axis = 0; axis < 3; axis += 1) {
          if (Math.abs(metrics.bounds.min[axis]) > 1.0e-6 || Math.abs(metrics.bounds.max[axis] - expectedMaximum[axis]) > 1.0e-6) {
            throw new Error('R2 comb texture changed the approved comb bounds')
          }
        }
      }
      report.artifacts[artifact.id] = {
        file: path.relative(root, outputFile),
        file_bytes: fs.statSync(outputFile).size,
        ...metrics,
        export_mesh: meshStats,
        texture_plan_count: built.plan.artifacts.find(item => item.id === artifact.id).texture_plans.length,
        textured: artifact.id === 'screwdriver-comb'
      }
      report.identities.artifacts[artifact.id] = fileIdentity(outputFile)
    }
    JSON.stringify(report)
    report.process_memory = memoryReport('r2-accessories')
    const peakBudget = textureConfig.resource_budget.max_peak_rss_mib_per_module
    report.resource_budget = {
      source_config_key: 'resource_budget.max_peak_rss_mib_per_module',
      max_peak_rss_mib: peakBudget,
      measured_max_rss_mib: report.process_memory.max_rss_mib,
      status: report.process_memory.max_rss_mib <= peakBudget ? 'PASS' : 'FAIL'
    }
    const reportFile = path.join(reportDir, 'build-final-R2-accessories-procedural-wood-unmarked.json')
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + '\n')
    for (const artifact of built.artifacts) artifact.solid.delete()
    if (report.resource_budget.status === 'FAIL') {
      console.error(`R2 accessories resource budget exceeded: ${report.process_memory.max_rss_mib.toFixed(3)} MiB > ${peakBudget.toFixed(3)} MiB; DRAFT artifacts and report retained`)
      console.log(JSON.stringify({
        status: 'budget-error',
        quality: args.quality,
        r2_accessories: true,
        report: path.relative(root, reportFile),
        artifacts: report.artifacts,
        process_memory: report.process_memory,
        resource_budget: report.resource_budget
      }))
      process.exitCode = 1
      return
    }
    console.log(JSON.stringify({
      status: 'ok',
      quality: args.quality,
      r2_accessories: true,
      report: path.relative(root, reportFile),
      artifacts: report.artifacts,
      process_memory: report.process_memory,
      resource_budget: report.resource_budget
    }))
    return
  }

  if (args.woodCoupon) {
    if (!params.surface_texture?.enabled) throw new Error('--wood-coupon requires enabled surface_texture parameters')
    if (params.surface_texture.representation !== 'procedural-vector-wood-grooves') {
      throw new Error('--wood-coupon requires procedural-vector-wood-grooves representation')
    }
    if (params.surface_texture.apply_outer_walls !== false) throw new Error('--wood-coupon requires smooth outer walls')
    const textureConfigPath = path.resolve(path.dirname(paramsPath), params.surface_texture.config)
    const textureConfig = loadProceduralWoodConfig(textureConfigPath)
    const outputDir = path.join(root, 'output', 'DRAFT')
    const reportDir = path.join(root, 'reports')
    fs.mkdirSync(outputDir, { recursive: true })
    fs.mkdirSync(reportDir, { recursive: true })
    const built = buildProceduralWoodCouponManifold(params, textureConfig)
    const outputFile = path.join(outputDir, 'DRAFT-R2-procedural-wood-coupon.stl')
    const meshStats = writeBinaryStl(
      outputFile,
      built.solid,
      'DRAFT R2 procedural wood coupon manifold-3d',
      params.export.stl_simplify_tolerance_mm
    )
    const metrics = statsWithoutMeshCopy(built.solid, meshStats)
    if (Math.abs(metrics.bounds.min[2]) > 1.0e-6) throw new Error('wood coupon no longer preserves bed plane z=0')
    const report = {
      status: 'DRAFT',
      quality: args.quality,
      engine: 'manifold-3d',
      revision: params.model_revision,
      route: 'wood-coupon-only',
      params: path.relative(root, paramsPath),
      surface_texture_config: path.relative(root, textureConfigPath),
      relief_loaded: false,
      watermark: { loaded: false, applied: false },
      coupon: {
        file: path.relative(root, outputFile),
        file_bytes: fs.statSync(outputFile).size,
        ...metrics,
        export_mesh: meshStats,
        plan: built.plan
      },
      identities: {
        inputs: r2InputIdentities(paramsPath, textureConfigPath),
        artifacts: {
          stl: fileIdentity(outputFile)
        }
      },
      process_memory: memoryReport('wood-coupon')
    }
    fs.writeFileSync(path.join(reportDir, 'build-final-wood-coupon.json'), JSON.stringify(report, null, 2) + '\n')
    built.solid.delete()
    console.log(JSON.stringify({
      status: 'ok',
      quality: args.quality,
      wood_coupon: true,
      file: report.coupon.file,
      triangles: meshStats.triangles,
      process_memory: report.process_memory
    }))
    return
  }

  const manifestPath = path.resolve(path.dirname(paramsPath), params.relief.manifest)
  const manifest = readJson(manifestPath)
  const watermarkPath = path.resolve(path.dirname(paramsPath), params.watermark.dxf)
  const markOutline = watermarkOutline(watermarkPath, params.watermark)
  const outputDir = path.join(root, 'output', 'DRAFT')
  const reportDir = path.join(root, 'reports')
  const cacheDir = path.join(reportDir, 'mesh-cache')
  fs.mkdirSync(outputDir, { recursive: true })
  fs.mkdirSync(reportDir, { recursive: true })
  fs.mkdirSync(cacheDir, { recursive: true })
  console.error(`Building ${params.model_revision} at ${manifest.pitch_x_mm.toFixed(4)} x ${manifest.pitch_y_mm.toFixed(4)} mm relief pitch`)

  const report = baseReport(params, paramsPath, manifestPath, preview, markOutline)
  if (args.module || preview) {
    const modules = buildModulesManifold(params, manifest, {
      segments,
      withRelief: !preview,
      withWatermark: !preview,
      watermarkOutline: markOutline,
      moduleIds: args.module ? [args.module] : undefined
    })
    for (const item of modules) {
      const global = preview ? item.smooth : item.textured
      const local = global.translate([-item.def.bounds[0], -item.def.bounds[2], 0])
      const filename = `DRAFT-${item.def.id}${preview ? '-smooth-preview' : '-textured'}.stl`
      const cacheFile = preview ? null : path.join(cacheDir, `${item.def.id}.meshbin`)
      const meshStats = writeBinaryStl(
        path.join(outputDir, filename),
        local,
        `DRAFT ${item.def.id} manifold-3d`,
        params.export.stl_simplify_tolerance_mm,
        cacheFile
      )
      report.modules.push({
        id: item.def.id,
        file: filename,
        mesh_cache: cacheFile ? path.relative(root, cacheFile) : null,
        ...statsWithoutMeshCopy(local, meshStats),
        export_mesh: meshStats
      })
      local.delete()
      global.delete()
    }
    report.process_memory = memoryReport(args.module || 'preview-all')
    const reportName = args.module ? `build-${args.quality}-${args.module}.json` : `build-${args.quality}.json`
    fs.writeFileSync(path.join(reportDir, reportName), JSON.stringify(report, null, 2) + '\n')
    console.log(JSON.stringify({ status: 'ok', quality: args.quality, module: args.module, process_memory: report.process_memory }))
    return
  }

  const comb = buildCombManifold(params, segments)
  const fit = buildFitCouponManifold(params)
  const relief = buildReliefCouponManifold(params, manifest)
  const connector = buildConnectorCouponManifold(params, segments)
  const accessoryEntries = [
    ['comb', comb, 'DRAFT-screwdriver-comb.stl'],
    ['fit_coupon', fit, 'DRAFT-drawer-fit-corner-coupon.stl'],
    ['relief_coupon', relief, 'DRAFT-relief-depth-coupon.stl'],
    ['connector_coupon_male', connector.male, 'DRAFT-connector-coupon-male.stl'],
    ['connector_coupon_female', connector.female, 'DRAFT-connector-coupon-female.stl']
  ]
  report.accessories = {}
  for (const [name, solid, filename] of accessoryEntries) {
    const meshStats = writeBinaryStl(
      path.join(outputDir, filename),
      solid,
      `DRAFT ${name} manifold-3d`,
      params.export.stl_simplify_tolerance_mm
    )
    report.accessories[name] = { file: filename, ...statsWithoutMeshCopy(solid, meshStats), export_mesh: meshStats }
    solid.delete()
  }
  report.process_memory = memoryReport('accessories')
  fs.writeFileSync(path.join(reportDir, 'build-final-accessories.json'), JSON.stringify(report, null, 2) + '\n')
  console.log(JSON.stringify({ status: 'ok', quality: args.quality, accessories: true, process_memory: report.process_memory }))
}

main()
