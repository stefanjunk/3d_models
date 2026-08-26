# OpenCode integration and patches for the existing skill family

Install this specialist beside the existing skills rather than merging all instructions into `functional-3d-design`.

## Routing addendum row

Add to the family MECE table:

| Module | Owns | Does not own |
|---|---|---|
| Multicolor FDM design | semantic filament regions, actual-filament palettes, parametric color solids/inlays, texture-to-color conversion, multi-part 3MF, purge/change optimization, final color validation | general mechanical design, protected source-mesh editing, freeform envelope creation, image-to-depth relief |

## Composite sequence patch

For a new product:

```text
functional contract and hardpoints
→ exact/freeform geometry and print split
→ optional height-map relief
→ multicolor region architecture
→ standard 3MF and destination-slicer mapping
→ purge/change and physical validation
```

For a textured AI/scan asset:

```text
organic-mesh preservation contract
→ repair/functional edits
→ bake one printable color source
→ multicolor palette quantization
→ paint handoff or explicit solid partitions
→ 3MF/slicer validation
```

## Suggested companion text

### `functional-3d-design`

Add under tool/specialist routing:

> Load `multicolor-fdm-design` when color assignment affects geometry, part decomposition, 3MF output, texture conversion, purge waste, or a multi-filament accessory. Keep mechanical requirements and material suitability here; delegate color architecture and multicolor validation.

### `organic-mesh-functionalization`

Add:

> After source preservation, repair, and functional edits are complete, load `multicolor-fdm-design` to convert UV textures, vertex colors, or source materials into printable filament regions. Do not let color conversion overwrite the immutable source.

### `parametric-freeform-surfacing`

Add:

> Freeze or validate the envelope and tessellation before generating color partitions. Multicolor regions may follow semantic panels, rails, section coordinates, or UV fields but must not silently deform exact hardpoints.

### `3d-print-heightmap-relief`

Add:

> Route to `multicolor-fdm-design` when an image should also control filament color. Relief grayscale remains continuous depth data; color quantization is a separate fixed-palette derivative.
