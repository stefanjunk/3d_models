#!/usr/bin/env node

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { Manifold } from 'manifold-3d/manifoldCAD'

import {
  buildCombManifold,
  buildConnectorCouponManifold,
  buildFitCouponManifold,
  buildModulesManifold,
  buildTextureCouponManifold,
  resolveModelParameters
} from './manifold_model.mjs'
import { watermarkOutline } from './watermark.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

function parseArgs () {
  const args = process.argv.slice(2)
  const valueAfter = (name, fallback = null) => {
    const index = args.indexOf(name)
    return index >= 0 ? args[index + 1] : fallback
  }
  return {
    quality: valueAfter('--quality', 'final'),
    module: valueAfter('--module'),
    surface: valueAfter('--surface'),
    accessories: args.includes('--accessories')
  }
}

function readJson (file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'))
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
  const mesh = reconstructed.getMesh()
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
  const result = { triangles: mesh.numTri, vertices: mesh.numVert, dropped_zero_area_triangles: 0 }
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
  const resources = process.resourceUsage()
  return {
    mode,
    pid: process.pid,
    max_rss_mib: resources.maxRSS / 1024,
    measurement: "process.resourceUsage().maxRSS; peak resident set for this isolated Node/WASM process"
  }
}

function baseReport (params, paramsPath, textureIndexPath, texturePath, preview, markOutline) {
  return {
    status: 'DRAFT',
    quality: preview ? 'preview' : 'final',
    engine: 'manifold-3d',
    revision: params.model_revision,
    execution_strategy: 'one-module-per-process; one-procedural-texture-patch-at-a-time',
    params: path.relative(root, paramsPath),
    resolved_wall_thickness_mm: {
      base: params.organizer.base_wall_thickness,
      outer: params.organizer.outer_wall_thickness,
      divider: params.organizer.divider_thickness
    },
    surface_texture_index: path.relative(root, textureIndexPath),
    surface_texture_config: path.relative(root, texturePath),
    surface_texture: {
      profile_id: params.surface_texture.profile_id,
      representation: params.surface_texture.representation,
      seed: params.surface_texture.seed,
      protected_regions: params.surface_texture.protected_regions,
      outer_walls_textured: params.surface_texture.surfaces.outer_walls.enabled
    },
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
  if (args.module && args.accessories) throw new Error('--module and --accessories are mutually exclusive')
  if (args.quality === 'final' && !args.module && !args.accessories) {
    throw new Error('final builds must select exactly one --module or --accessories; use python3 src/build_pipeline.py')
  }
  const paramsPath = path.join(root, 'config', 'model-params.json')
  const rawParams = readJson(paramsPath)
  const textureIndexPath = path.resolve(path.dirname(paramsPath), rawParams.surface_texture.config)
  const textureIndex = readJson(textureIndexPath)
  const surface = args.surface ?? textureIndex.default_profile
  const relativeTexturePath = textureIndex.profiles[surface]
  if (!relativeTexturePath) throw new Error(`unsupported surface profile: ${surface}`)
  const texturePath = path.resolve(path.dirname(textureIndexPath), relativeTexturePath)
  const textureConfig = readJson(texturePath)
  if (textureConfig.profile_id !== surface) throw new Error(`surface profile id mismatch in ${texturePath}`)
  const params = resolveModelParameters({ ...rawParams, surface_texture: textureConfig })
  const preview = args.quality === 'preview'
  const segments = preview ? params.export.segments_preview : params.export.segments_final
  const watermarkPath = path.resolve(path.dirname(paramsPath), params.watermark.dxf)
  const markOutline = watermarkOutline(watermarkPath, params.watermark)
  const outputDir = path.join(root, 'output', 'DRAFT')
  const reportDir = path.join(root, 'reports')
  const cacheDir = path.join(reportDir, 'mesh-cache')
  fs.mkdirSync(outputDir, { recursive: true })
  fs.mkdirSync(reportDir, { recursive: true })
  fs.mkdirSync(cacheDir, { recursive: true })
  console.error(`Building ${params.model_revision} surface=${surface} with ${params.surface_texture.representation}; seed ${params.surface_texture.seed}`)

  const report = baseReport(params, paramsPath, textureIndexPath, texturePath, preview, markOutline)
  if (args.module || preview) {
    const modules = buildModulesManifold(params, {
      segments,
      withTexture: !preview,
      withWatermark: !preview,
      watermarkOutline: markOutline,
      moduleIds: args.module ? [args.module] : undefined
    })
    for (const item of modules) {
      const global = preview ? item.smooth : item.textured
      const local = global.translate([-item.def.bounds[0], -item.def.bounds[2], 0])
      const filename = `DRAFT-${item.def.id}${preview ? '-smooth-preview' : '-surface'}.stl`
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
        texture_stats: item.texture_stats,
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
  const textureCoupon = buildTextureCouponManifold(params)
  const connector = buildConnectorCouponManifold(params, segments)
  const accessoryEntries = [
    ['comb', comb, 'DRAFT-screwdriver-comb.stl'],
    ['fit_coupon', fit, 'DRAFT-drawer-fit-corner-coupon.stl'],
    ['surface_texture_coupon', textureCoupon, 'DRAFT-surface-texture-coupon.stl'],
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
