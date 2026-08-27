import {
  applyProceduralTexturePatch as applyCarbon,
  summarizeTextureStats as summarizeCarbon
} from './textures/carbon.mjs'
import {
  applyProceduralTexturePatch as applyCarbonWave,
  summarizeTextureStats as summarizeCarbonWave
} from './textures/carbon_wave.mjs'
import {
  applyProceduralTexturePatch as applySteel,
  summarizeTextureStats as summarizeSteel
} from './textures/steel.mjs'
import {
  applyProceduralTexturePatch as applyMicroCast,
  summarizeTextureStats as summarizeMicroCast
} from './textures/micro_cast.mjs'
import {
  applyProceduralTexturePatch as applyWalnut,
  summarizeTextureStats as summarizeWalnut
} from './textures/walnut.mjs'

const adapters = {
  carbon: { apply: applyCarbon, summarize: summarizeCarbon },
  'carbon-wave': { apply: applyCarbonWave, summarize: summarizeCarbonWave },
  'micro-cast': { apply: applyMicroCast, summarize: summarizeMicroCast },
  steel: { apply: applySteel, summarize: summarizeSteel },
  walnut: { apply: applyWalnut, summarize: summarizeWalnut }
}

function zeroStats (patch, surfaceName, textureConfig) {
  return {
    representation: textureConfig.representation,
    surface: surfaceName,
    key: patch.key,
    features: 0
  }
}

export function applyProceduralTexturePatch (shape, patch, surfaceName, textureConfig) {
  if (!textureConfig.enabled || textureConfig.profile_id === 'plain') {
    return { shape, stats: zeroStats(patch, surfaceName, textureConfig) }
  }
  const adapter = adapters[textureConfig.profile_id]
  if (!adapter) throw new Error(`unsupported surface profile: ${textureConfig.profile_id}`)
  return adapter.apply(shape, patch, surfaceName, textureConfig)
}

export function summarizeTextureStats (patchStats, textureConfig) {
  if (!textureConfig.enabled || textureConfig.profile_id === 'plain') {
    return {
      profile_id: textureConfig.profile_id,
      representation: textureConfig.representation,
      patches: 0,
      features: 0,
      by_surface: {}
    }
  }
  const adapter = adapters[textureConfig.profile_id]
  if (!adapter) throw new Error(`unsupported surface profile: ${textureConfig.profile_id}`)
  return {
    profile_id: textureConfig.profile_id,
    ...adapter.summarize(patchStats)
  }
}
