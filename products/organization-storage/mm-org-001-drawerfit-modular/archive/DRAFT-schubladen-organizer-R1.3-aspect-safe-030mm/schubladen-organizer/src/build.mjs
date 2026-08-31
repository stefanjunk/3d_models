#!/usr/bin/env node

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import modeling from '@jscad/modeling'
import serializer3mf from '@jscad/3mf-serializer'
import serializerStl from '@jscad/stl-serializer'

const { measurements, modifiers, transforms } = modeling
const { serialize: serialize3mf } = serializer3mf
const { serialize: serializeStl } = serializerStl

import { buildComb, buildFitCoupon, buildModules, buildReliefCoupon } from './model.mjs'
import { readReliefManifest } from './relief.mjs'

const { measureBoundingBox, measureVolume } = measurements
const { generalize } = modifiers
const { translate } = transforms

const here = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(here, '..')

function parseArgs () {
  const args = process.argv.slice(2)
  const qualityIndex = args.indexOf('--quality')
  return { quality: qualityIndex >= 0 ? args[qualityIndex + 1] : 'final' }
}

function readJson (p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'))
}

function blobableToBuffer (parts) {
  const buffers = parts.map(part => {
    if (typeof part === 'string') return Buffer.from(part)
    if (part instanceof ArrayBuffer) return Buffer.from(new Uint8Array(part))
    if (ArrayBuffer.isView(part)) return Buffer.from(part.buffer, part.byteOffset, part.byteLength)
    return Buffer.from(part)
  })
  return Buffer.concat(buffers)
}

function writeStl (target, geometry) {
  const prepared = generalize({ snap: true, triangulate: true }, geometry)
  const data = serializeStl({ binary: true }, prepared)
  fs.writeFileSync(target, blobableToBuffer(data))
}

function write3mf (target, geometries) {
  const prepared = geometries.map(geometry => generalize({ snap: true, triangulate: true }, geometry))
  const data = serialize3mf({ compress: true, unit: 'millimeter', metadata: true }, ...prepared)
  fs.writeFileSync(target, blobableToBuffer(data))
}

function localize (geometry, bounds) {
  return translate([-bounds[0], -bounds[2], 0], geometry)
}

function geometryStats (geometry) {
  const bounds = measureBoundingBox(geometry)
  return {
    bounds,
    size: bounds[1].map((value, index) => value - bounds[0][index]),
    volume_mm3: measureVolume(geometry)
  }
}

function main () {
  const args = parseArgs()
  const paramsPath = path.join(root, 'config', 'model-params.json')
  const params = readJson(paramsPath)
  const manifestPath = path.resolve(path.dirname(paramsPath), params.relief.manifest)
  const manifest = readReliefManifest(manifestPath)
  const preview = args.quality === 'preview'
  const segments = preview ? params.export.segments_preview : params.export.segments_final
  const outputDir = path.join(root, 'output', 'DRAFT')
  const reportDir = path.join(root, 'reports')
  fs.mkdirSync(outputDir, { recursive: true })
  fs.mkdirSync(reportDir, { recursive: true })

  const modules = buildModules(params, manifest, { segments, withRelief: !preview })
  const report = {
    status: 'DRAFT',
    quality: args.quality,
    engine: '@jscad/modeling',
    params: path.relative(root, paramsPath),
    relief_manifest: path.relative(root, manifestPath),
    modules: []
  }

  for (const module of modules) {
    const geometry = preview ? module.smooth : module.textured
    const local = localize(geometry, module.def.bounds)
    const filename = `DRAFT-${module.def.id}${preview ? '-smooth-preview' : '-textured'}.stl`
    writeStl(path.join(outputDir, filename), local)
    report.modules.push({ id: module.def.id, file: filename, ...geometryStats(local) })
  }

  const comb = buildComb(params, segments)
  const fitCoupon = buildFitCoupon(params, segments)
  const reliefCoupon = buildReliefCoupon(params, manifest)
  writeStl(path.join(outputDir, 'DRAFT-screwdriver-comb.stl'), comb)
  writeStl(path.join(outputDir, 'DRAFT-drawer-fit-corner-coupon.stl'), fitCoupon)
  writeStl(path.join(outputDir, 'DRAFT-relief-depth-coupon.stl'), reliefCoupon)
  report.accessories = {
    comb: geometryStats(comb),
    fit_coupon: geometryStats(fitCoupon),
    relief_coupon: geometryStats(reliefCoupon)
  }

  const assemblyGeometries = modules.map(module => preview ? module.smooth : module.textured)
  write3mf(path.join(outputDir, `DRAFT-organizer-${preview ? 'smooth-preview' : 'textured'}-assembly.3mf`), [...assemblyGeometries, comb])
  fs.writeFileSync(path.join(reportDir, `build-${args.quality}.json`), JSON.stringify(report, null, 2) + '\n')
  console.log(JSON.stringify({ status: 'ok', quality: args.quality, modules: report.modules.length, output: path.relative(root, outputDir) }))
}

main()
