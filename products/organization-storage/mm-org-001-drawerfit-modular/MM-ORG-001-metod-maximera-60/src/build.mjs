#!/usr/bin/env node

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { Manifold } from 'manifold-3d/manifoldCAD'

import {
  buildComb,
  buildCombInterfaceCoupon,
  buildConnectorCouponFemale,
  buildConnectorCouponMale,
  buildFitCornerCoupon,
  buildModules,
  resolveParameters
} from './model.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

function readJson (file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'))
}

function pointFromMesh (mesh, vertexId) {
  const offset = vertexId * mesh.numProp
  return [mesh.vertProperties[offset], mesh.vertProperties[offset + 1], mesh.vertProperties[offset + 2]]
}

function writeMeshCache (file, mesh) {
  const fd = fs.openSync(file, 'w')
  try {
    const header = Buffer.alloc(16)
    header.write('MSH1', 0, 'ascii')
    header.writeUInt32LE(mesh.numVert, 4)
    header.writeUInt32LE(mesh.numTri, 8)
    header.writeUInt32LE(3, 12)
    fs.writeSync(fd, header)
    const vertices = Buffer.allocUnsafe(mesh.numVert * 12)
    for (let index = 0; index < mesh.numVert; index += 1) {
      const source = index * mesh.numProp
      vertices.writeFloatLE(mesh.vertProperties[source], index * 12)
      vertices.writeFloatLE(mesh.vertProperties[source + 1], index * 12 + 4)
      vertices.writeFloatLE(mesh.vertProperties[source + 2], index * 12 + 8)
    }
    fs.writeSync(fd, vertices)
    const faces = Buffer.allocUnsafe(mesh.numTri * 12)
    for (let index = 0; index < mesh.numTri; index += 1) {
      faces.writeUInt32LE(mesh.triVerts[index * 3], index * 12)
      faces.writeUInt32LE(mesh.triVerts[index * 3 + 1], index * 12 + 4)
      faces.writeUInt32LE(mesh.triVerts[index * 3 + 2], index * 12 + 8)
    }
    fs.writeSync(fd, faces)
  } finally {
    fs.closeSync(fd)
  }
}

function writeBinaryStl (file, manifold, headerText, cacheFile = null) {
  const sourceMesh = manifold.getMesh()
  sourceMesh.merge()
  const reconstructed = Manifold.ofMesh(sourceMesh)
  const mesh = reconstructed.getMesh()
  const fd = fs.openSync(file, 'w')
  try {
    const header = Buffer.alloc(84)
    header.write(headerText.slice(0, 80), 0, 'ascii')
    header.writeUInt32LE(mesh.numTri, 80)
    fs.writeSync(fd, header)
    const record = Buffer.allocUnsafe(50)
    for (let triangle = 0; triangle < mesh.numTri; triangle += 1) {
      const ids = [mesh.triVerts[triangle * 3], mesh.triVerts[triangle * 3 + 1], mesh.triVerts[triangle * 3 + 2]]
      const points = ids.map(id => pointFromMesh(mesh, id))
      const ab = points[1].map((value, axis) => value - points[0][axis])
      const ac = points[2].map((value, axis) => value - points[0][axis])
      const normal = [ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2], ab[0] * ac[1] - ab[1] * ac[0]]
      const length = Math.hypot(...normal) || 1
      for (let axis = 0; axis < 3; axis += 1) record.writeFloatLE(normal[axis] / length, axis * 4)
      for (let vertex = 0; vertex < 3; vertex += 1) {
        for (let axis = 0; axis < 3; axis += 1) record.writeFloatLE(points[vertex][axis], 12 + (vertex * 3 + axis) * 4)
      }
      record.writeUInt16LE(0, 48)
      fs.writeSync(fd, record)
    }
  } finally {
    fs.closeSync(fd)
  }
  if (cacheFile) writeMeshCache(cacheFile, mesh)
  const bounds = reconstructed.boundingBox()
  const result = {
    manifold_status: reconstructed.status(),
    triangles: mesh.numTri,
    vertices: mesh.numVert,
    volume_mm3: reconstructed.volume(),
    bounds_min_mm: bounds.min,
    bounds_max_mm: bounds.max,
    size_mm: bounds.max.map((value, axis) => value - bounds.min[axis])
  }
  reconstructed.delete()
  return result
}

function localize (solid, bounds) {
  return solid.translate([-bounds[0], -bounds[2], 0])
}

function main () {
  const paramsPath = path.join(root, 'config', 'model-params.json')
  const p = resolveParameters(readJson(paramsPath))
  const outputDir = path.join(root, 'output', 'DRAFT')
  const reportDir = path.join(root, 'reports')
  const cacheDir = path.join(reportDir, 'mesh-cache')
  fs.mkdirSync(outputDir, { recursive: true })
  fs.mkdirSync(reportDir, { recursive: true })
  fs.mkdirSync(cacheDir, { recursive: true })

  const report = {
    status: p.status,
    product_id: p.product_id,
    specification_revision: p.specification_revision,
    geometry_revision: p.geometry_revision,
    engine: 'manifold-3d 3.5.1 / JavaScript',
    surface: 'plain',
    watermark: 'blocked-not-applied',
    parameters: path.relative(root, paramsPath),
    modules: [],
    accessories: {}
  }

  const modules = buildModules(p)
  for (const item of modules) {
    const local = localize(item.solid, item.def.bounds)
    const filename = `DRAFT-MM-ORG-001-${item.def.id}-v0.1.0-draft.1.stl`
    const cacheFile = path.join(cacheDir, `${item.def.id}.meshbin`)
    const stats = writeBinaryStl(path.join(outputDir, filename), local, `DRAFT MM-ORG-001 ${item.def.id}`, cacheFile)
    report.modules.push({
      id: item.def.id,
      row: item.def.row,
      column: item.def.column,
      assembly_translation_mm: [item.def.bounds[0], item.def.bounds[2], 0],
      manufacturing_file: `output/DRAFT/${filename}`,
      mesh_cache: path.relative(root, cacheFile),
      ...stats
    })
    local.delete()
    item.solid.delete()
  }

  const comb = buildComb(p)
  const combFile = 'DRAFT-MM-ORG-001-screwdriver-comb-v0.1.0-draft.1.stl'
  const combCache = path.join(cacheDir, 'screwdriver-comb.meshbin')
  report.accessories.screwdriver_comb = {
    manufacturing_file: `output/DRAFT/${combFile}`,
    mesh_cache: path.relative(root, combCache),
    assembly_translation_mm: [p.organizer.wall_thickness + p.comb.side_clearance_each, p.comb.assembled_y, p.organizer.floor_thickness],
    ...writeBinaryStl(path.join(outputDir, combFile), comb, 'DRAFT MM-ORG-001 screwdriver comb', combCache)
  }
  comb.delete()

  const accessories = [
    ['comb_interface_coupon', buildCombInterfaceCoupon(p), 'DRAFT-MM-ORG-001-comb-interface-coupon.stl'],
    ['drawer_fit_corner_coupon', buildFitCornerCoupon(p), 'DRAFT-MM-ORG-001-drawer-fit-corner-coupon.stl'],
    ['connector_coupon_male', buildConnectorCouponMale(p), 'DRAFT-MM-ORG-001-connector-coupon-male.stl']
  ]
  for (const clearance of p.connectors.coupon_clearances_per_side) {
    const code = Math.round(clearance * 100).toString().padStart(3, '0')
    accessories.push([
      `connector_coupon_female_c${code}`,
      buildConnectorCouponFemale(p, clearance),
      `DRAFT-MM-ORG-001-connector-coupon-female-c${code}.stl`
    ])
  }
  for (const [id, solid, filename] of accessories) {
    report.accessories[id] = {
      manufacturing_file: `output/DRAFT/${filename}`,
      ...writeBinaryStl(path.join(outputDir, filename), solid, `DRAFT MM-ORG-001 ${id}`)
    }
    solid.delete()
  }

  report.summary = {
    module_count: report.modules.length,
    assembly_object_count: report.modules.length + 1,
    connector_mating_locations: p.connectors.mating_location_count,
    hardware_compartment_count: p.layout.hardware_compartments,
    estimated_total_model_volume_mm3: report.modules.reduce((sum, item) => sum + item.volume_mm3, 0) + report.accessories.screwdriver_comb.volume_mm3,
    solid_volume_equivalent_mass_g_at_configured_density: (report.modules.reduce((sum, item) => sum + item.volume_mm3, 0) + report.accessories.screwdriver_comb.volume_mm3) / 1000 * p.manufacturing.density_g_cm3,
    mass_note: 'solid-volume equivalent only; actual filament and print time require the exact slicer profile'
  }
  report.process_memory = {
    max_rss_mib: process.resourceUsage().maxRSS / 1024,
    measurement: 'process.resourceUsage().maxRSS'
  }
  fs.writeFileSync(path.join(reportDir, 'build-report.json'), JSON.stringify(report, null, 2) + '\n')
  console.log(JSON.stringify({ status: 'ok', modules: report.modules.length, accessories: Object.keys(report.accessories).length, solid_volume_equivalent_mass_g: report.summary.solid_volume_equivalent_mass_g_at_configured_density, max_rss_mib: report.process_memory.max_rss_mib }))
}

main()
