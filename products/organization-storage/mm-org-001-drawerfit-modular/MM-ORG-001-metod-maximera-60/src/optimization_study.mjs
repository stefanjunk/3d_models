#!/usr/bin/env node

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { buildComb, buildModules, resolveParameters } from './model.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

function volumeFor (raw, floorThickness) {
  const variant = structuredClone(raw)
  variant.organizer.floor_thickness = floorThickness
  const p = resolveParameters(variant)
  const modules = buildModules(p)
  const comb = buildComb(p)
  const moduleVolume = modules.reduce((sum, item) => sum + item.solid.volume(), 0)
  const combVolume = comb.volume()
  for (const item of modules) item.solid.delete()
  comb.delete()
  return {
    floor_thickness_mm: floorThickness,
    module_volume_mm3: moduleVolume,
    comb_volume_mm3: combVolume,
    total_volume_mm3: moduleVolume + combVolume,
    solid_volume_equivalent_mass_g: (moduleVolume + combVolume) / 1000 * p.manufacturing.density_g_cm3
  }
}

function main () {
  const raw = JSON.parse(fs.readFileSync(path.join(root, 'config', 'model-params.json'), 'utf8'))
  const variants = [2.6, 2.2, 2.0].map(value => volumeFor(raw, value))
  const baseline = variants[0]
  for (const variant of variants) {
    variant.volume_change_percent = 100 * (variant.total_volume_mm3 - baseline.total_volume_mm3) / baseline.total_volume_mm3
    variant.solid_volume_equivalent_mass_change_g = variant.solid_volume_equivalent_mass_g - baseline.solid_volume_equivalent_mass_g
  }
  const report = {
    schema_version: 1,
    status: 'DRAFT_STUDY_NOT_A_DESIGN_PROMOTION',
    product_id: raw.product_id,
    geometry_revision: raw.geometry_revision,
    baseline: {
      floor_thickness_mm: 2.6,
      rationale: 'approved-recommended R1.6-derived plain full-floor baseline'
    },
    protected_in_every_variant: [
      '512 x 491 x 50 mm assembled envelope',
      '3 x 3 manufacturing grid and common-220 bed fit',
      'tool lane, 18-bin layout, wall thickness and wall heights',
      'one connector location per necessary seam segment',
      'eight-slot comb geometry'
    ],
    variants,
    selected_for_active_draft: 2.6,
    selection_reason: 'Thinner full floors also thin every floor-plane connector and wall root. Without connector, handling and loaded-cycle evidence, the material saving does not justify promoting the interface change.',
    connector_density_comparison: {
      inherited_double_location_comparator: 24,
      active_minimal_location_count: raw.connectors.mating_location_count,
      reduction_percent: 50,
      rationale: 'Every one of the twelve necessary seam segments remains connected while avoiding a redundant second tolerance-sensitive feature.'
    },
    exact_slicer_comparison: {
      status: 'NOT_RUN',
      reason: 'No supported slicer executable or exact printer/material profile is available.'
    }
  }
  fs.writeFileSync(path.join(root, 'reports', 'optimization-study.json'), JSON.stringify(report, null, 2) + '\n')
  console.log(JSON.stringify({ status: report.status, variants }))
}

main()
