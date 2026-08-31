import fs from 'node:fs'

import modeling from '@jscad/modeling'

const { booleans, primitives } = modeling

const { cuboid } = primitives
const { union, subtract } = booleans

const EPS = 1.0e-6

export function readReliefManifest (path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'))
}

export function boxFromBounds (x0, x1, y0, y1, z0, z1) {
  if (x1 - x0 <= EPS || y1 - y0 <= EPS || z1 - z0 <= EPS) return null
  return cuboid({
    size: [x1 - x0, y1 - y0, z1 - z0],
    center: [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]
  })
}

export function balancedUnion (items, batchSize = 24) {
  let queue = items.filter(Boolean)
  if (queue.length === 0) return null
  while (queue.length > 1) {
    const next = []
    for (let i = 0; i < queue.length; i += batchSize) {
      const batch = queue.slice(i, i + batchSize)
      next.push(batch.length === 1 ? batch[0] : union(...batch))
    }
    queue = next
  }
  return queue[0]
}

export function applyReliefBodies (base, bodies) {
  const additions = balancedUnion(bodies.additions)
  const cutters = balancedUnion(bodies.cutters)
  let result = base
  if (additions) result = union(result, additions)
  if (cutters) result = subtract(result, cutters)
  return result
}

function repeatCount (length, period) {
  return Math.max(1, Math.ceil(length / period))
}

function clippedRect (u0, u1, v0, v1, target) {
  const cu0 = Math.max(u0, target.u0)
  const cu1 = Math.min(u1, target.u1)
  const cv0 = Math.max(v0, target.v0)
  const cv1 = Math.min(v1, target.v1)
  if (cu1 - cu0 <= EPS || cv1 - cv0 <= EPS) return null
  return [cu0, cu1, cv0, cv1]
}

function forEachMappedRun (manifest, target, tileScale, callback) {
  const tileW = manifest.tile_width_mm * tileScale
  const tileH = manifest.tile_height_mm * tileScale
  const pitchX = manifest.pitch_x_mm * tileScale
  const pitchY = manifest.pitch_y_mm * tileScale
  const countU = repeatCount(target.u1 - target.u0, tileW)
  const countV = repeatCount(target.v1 - target.v0, tileH)
  for (let tv = 0; tv < countV; tv += 1) {
    for (let tu = 0; tu < countU; tu += 1) {
      const tileOriginU = target.u0 + tu * tileW
      const tileOriginV = target.v0 + tv * tileH
      for (const run of manifest.runs) {
        const u0 = tileOriginU + run.x0 * pitchX
        const u1 = tileOriginU + run.x1 * pitchX
        // Image row zero is mapped to the high V edge of each tile.
        const v0 = tileOriginV + tileH - (run.row + 1) * pitchY
        const v1 = v0 + pitchY
        const clipped = clippedRect(u0, u1, v0, v1, target)
        if (clipped) callback(run.level, clipped)
      }
    }
  }
}

export function floorReliefBodies (manifest, rect, zSurface, relief) {
  const additions = []
  const cutters = []
  const target = { u0: rect.x0, u1: rect.x1, v0: rect.y0, v1: rect.y1 }
  forEachMappedRun(manifest, target, relief.tile_scale, (level, [x0, x1, y0, y1]) => {
    if (level === 'emboss') {
      additions.push(boxFromBounds(
        x0, x1, y0, y1,
        zSurface - relief.boolean_overlap,
        zSurface + relief.emboss_depth
      ))
    } else {
      cutters.push(boxFromBounds(
        x0, x1, y0, y1,
        zSurface - relief.engrave_depth,
        zSurface + relief.boolean_overlap
      ))
    }
  })
  return { additions, cutters }
}

export function wallXReliefBodies (manifest, spec, relief) {
  const additions = []
  const cutters = []
  const target = { u0: spec.y0, u1: spec.y1, v0: spec.z0, v1: spec.z1 }
  forEachMappedRun(manifest, target, relief.tile_scale, (level, [y0, y1, z0, z1]) => {
    if (level === 'emboss') {
      const x0 = spec.normal > 0 ? spec.x - relief.boolean_overlap : spec.x - relief.emboss_depth
      const x1 = spec.normal > 0 ? spec.x + relief.emboss_depth : spec.x + relief.boolean_overlap
      additions.push(boxFromBounds(x0, x1, y0, y1, z0, z1))
    } else {
      const x0 = spec.normal > 0 ? spec.x - relief.engrave_depth : spec.x - relief.boolean_overlap
      const x1 = spec.normal > 0 ? spec.x + relief.boolean_overlap : spec.x + relief.engrave_depth
      cutters.push(boxFromBounds(x0, x1, y0, y1, z0, z1))
    }
  })
  return { additions, cutters }
}

export function wallYReliefBodies (manifest, spec, relief) {
  const additions = []
  const cutters = []
  const target = { u0: spec.x0, u1: spec.x1, v0: spec.z0, v1: spec.z1 }
  forEachMappedRun(manifest, target, relief.tile_scale, (level, [x0, x1, z0, z1]) => {
    if (level === 'emboss') {
      const y0 = spec.normal > 0 ? spec.y - relief.boolean_overlap : spec.y - relief.emboss_depth
      const y1 = spec.normal > 0 ? spec.y + relief.emboss_depth : spec.y + relief.boolean_overlap
      additions.push(boxFromBounds(x0, x1, y0, y1, z0, z1))
    } else {
      const y0 = spec.normal > 0 ? spec.y - relief.engrave_depth : spec.y - relief.boolean_overlap
      const y1 = spec.normal > 0 ? spec.y + relief.boolean_overlap : spec.y + relief.engrave_depth
      cutters.push(boxFromBounds(x0, x1, y0, y1, z0, z1))
    }
  })
  return { additions, cutters }
}

export function mergeReliefBodies (...groups) {
  return {
    additions: groups.flatMap(group => group.additions),
    cutters: groups.flatMap(group => group.cutters)
  }
}
