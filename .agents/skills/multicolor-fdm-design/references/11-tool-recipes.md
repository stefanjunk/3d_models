# Tool recipes

## OpenSCAD: parametric inlays

Use one module per semantic region and a `part` selector:

```scad
module accent_profile() { /* 2D region */ }
module accent() { translate([0,0,top-inlay]) linear_extrude(inlay) accent_profile(); }
module base() { difference() { product(); translate([0,0,top-inlay-eps]) linear_extrude(inlay+2*eps) accent_profile(); } }

if (part == "base") base();
if (part == "accent") accent();
```

Export every part with the same origin. Include `part="all"` only for colored preview, not manufacturing.

## CadQuery/build123d/FreeCAD: named solids

Create a master product and semantic cutters. Build each accent as `product.intersect(accent_volume)` and the base as `product.cut(union(accents))`. Export each solid and an assembly/STEP/3MF handoff. Rebuild exact interfaces after freeform operations.

## Blender: existing textured assets

- OBJ import creates material assignments from MTL; glTF import constructs material nodes.
- Apply transforms before sampling.
- Bake procedural/multiple materials to one base-color image when possible.
- Use `Separate > By Material` if source material slots already correspond to filament regions.
- Repair/open-edge review belongs to the organic-mesh workflow.
- Keep a non-destructive source collection and a conversion collection.

## Bambu Studio: Texture-to-Color Painting fast path

- Use version 2.7 or later with the feature present.
- Prefer one clean mesh with one texture.
- Import one textured model at a time.
- Avoid Draco-compressed GLB for versions where unsupported.
- Convert, remap to the actual palette, clean islands, save 3MF.
- Import into Anycubic Slicer Next and revalidate; do not assume project metadata portability.

## Anycubic Slicer Next

Anycubic Slicer Next is Orca-based and provides Color Painting. Use separate parts for robust parametric models and painting for local corrections. Assign each part/paint color to the intended ACE slot, then inspect the sliced color/tool view and wipe tower.

After saving the authoritative Anycubic 3MF, batch-slice it through the sibling validation skill:

```bash
python3 "$FDM_VALIDATION_SKILL/scripts/fdm_ci.py" slice-anycubic-next \
  model-anycubic.3mf build/anycubic-slice-r1 \
  --json-out reports/anycubic-slice-r1.json
```

The command uses embedded 3MF profiles unless a complete external machine/process/filament set is supplied. It records exact hashes and analyzes G-code, but it neither creates paint data nor proves ACE slot mapping or purge quality. Keep GUI preview and a physical color/purge coupon as separate gates.

## Python helpers

```text
inspect_textured_asset.py   source/UV/material/topology report
quantize_texture.py         fixed-palette Lab/CIEDE2000 conversion
texture_to_voxel_parts.py   texture → explicit color volumes
assemble_multicolor_3mf.py  aligned parts → standard 3MF assembly
validate_multicolor_3mf.py  package and mesh-reference checks
estimate_color_changes.py   layer color occupancy and purge estimate
build_examples.py           deterministic worked examples
```
