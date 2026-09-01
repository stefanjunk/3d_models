---
name: multicolor-fdm-design
description: Design, convert, validate, and optimize multicolor single-nozzle FDM/FFF models and textured OBJ/GLB assets for 3MF handoff. Use for color decomposition, real-filament palette mapping, parametric color solids and inlays, slicer painting, layer changes, texture quantization, purge and color-change optimization, ACE/AMS/MMU-class systems, and multicolor validation.
license: MIT
metadata:
  version: "1.1.0"
  domain: "multicolor fdm design and textured asset conversion"
  manufacturing: "single-nozzle multi-filament fdm-fff"
  compatibility: "OpenCode with project file access and Python 3.10+; optional CAD, mesh, image, and slicer tools improve automation"
  inputs: "parametric CAD, STL, OBJ+MTL+textures, GLB, glTF, 3MF, actual filament palette"
  outputs: "named color solids, standard multi-part 3MF, palette report, purge budget, slicer handoff, validation evidence"
  complements: "functional-3d-design, organic-mesh-functionalization, parametric-freeform-surfacing, 3d-print-heightmap-relief"
---

# Multicolor FDM Design

Create **manufacturable color architecture**, not merely a colorful render.

This skill owns color-region design, actual-filament palette mapping, texture-to-color conversion, multi-part 3MF packaging, color-change budgeting, purge planning, and slicer handoff. It does not replace the companion skills that own the underlying mechanical geometry, protected organic source mesh, freeform envelope, or image-to-depth relief.

If the job creates a new independently managed product, load
`3d-design-preflight` and complete its SKU, correct product-folder, portfolio
CSV/XLSX, license-chain, and prospective-preflight intake first. A multicolor
variant of an existing product normally remains under the owning SKU and
revision history.

Set the skill path before using the supplied helpers:

```bash
# Project-local installation
export MCFDM_SKILL=.opencode/skills/multicolor-fdm-design

# Typical global installation
# export MCFDM_SKILL=~/.config/opencode/skills/multicolor-fdm-design
```

## 1. Route companion work before assigning colors

Read `references/00-scope-and-routing.md` for composite work.

- Load **functional-3d-design** for function, dimensions, interfaces, tolerances, materials, nozzle, orientation, and physical tests.
- Load **organic-mesh-functionalization** when an existing OBJ/GLB/STL is authoritative and its visible surface or topology must be preserved while it is repaired, hollowed, cut, or modified.
- Load **parametric-freeform-surfacing** when a new editable organic envelope, fair curves, lofts, SubD, or reference fitting is required.
- Load **3d-print-heightmap-relief** when image information should become depth rather than filament color.
- Return here after the geometry and mapping surface are stable enough to define printable color regions.

## 2. Create the multicolor contract

Copy `assets/templates/multicolor-job.yaml` to the project and record:

- printer, material changer, nozzle, layer-height range, and maximum simultaneous filaments;
- the **actual loaded filament palette**, including material family, manufacturer/color name, measured or photographed swatch color, opacity, and slot only as a temporary machine mapping;
- source asset, units, transforms, texture files, hashes, and whether source preservation is mandatory;
- selected representation: `layer_change`, `separate_solids`, `slicer_paint`, `texture_paint_handoff`, or `voxel_partitions`;
- minimum printable color width/depth, permitted color error, island cleanup policy, and purge budget;
- expected output: source CAD, named part meshes, standard 3MF, slicer project, preview, and validation report;
- acceptance criteria for geometry, color assignment, estimated changes, purge waste, and physical coupon.

Validate it:

```bash
python3 "$MCFDM_SKILL/scripts/validate_job.py" multicolor-job.yaml
```

## 3. Choose the least fragile color representation

Use this order unless the job proves another route is better:

1. **Layer changes** — best when every color boundary is horizontal; fewest changes and most portable.
2. **Separate watertight solids/parts** — preferred for parametric design, engineering handoff, and reusable 3MF.
3. **Slicer painting** — fast for one-off artistic edits; treat it as slicer-project data, not authoritative CAD.
4. **Texture-to-color painting handoff** — fast for one clean textured OBJ/glTF/GLB; verify the result after every slicer transfer.
5. **Voxel/volume partitioning** — robust headless fallback that converts texture colors into actual non-overlapping solids, at the cost of resolution and mesh size.

Read `references/02-parametric-color-architecture.md`, `references/04-textured-asset-to-multicolor-3mf.md`, and `references/06-3mf-and-slicer-interoperability.md` before committing to a route.

## 4. Non-negotiable design rules

1. **Every intended filament region must be explicit** as a named solid, a documented layer change, or a slicer paint region with a preserved project file.
2. **Prefer actual solids for durable design intent.** A painted slicer surface changes slicing, not the source mesh, and may not export as reusable parts.
3. **Use the real filament palette.** Map source colors to the loaded filaments; do not optimize to arbitrary RGB centroids and then discover that no matching filament exists.
4. **Do not dither by default.** Pixel dithering creates tiny color islands and many transitions. Use broad printable regions unless a deliberate halftone process has been validated.
5. **Color features need volume.** Avoid zero-thickness labels, coplanar duplicate faces, and overlapping bodies. Use inlays, shells, inserts, or disjoint partitions.
6. **Keep each color body manifold and aligned.** Export every part in the same coordinate system and preserve its transform in 3MF components.
7. **Do not assume a 3MF display color maps to an ACE/AMS/MMU slot.** Base-material names and display colors convey design intent; assign physical slots in the destination slicer and inspect the preview.
8. **Use one polymer family by default** for single-nozzle decorative multicolor: PLA with PLA, PETG with PETG, and so on. Mixed families require an intentional interface/support strategy and a coupon.
9. **Design for the line width, not the texture pixel.** As a conservative starting point, use isolated color features at least two extrusion widths across and inlays at least two to three layers deep; prove smaller details with a coupon.
10. **Minimize active colors per layer.** Concentrate accents into narrow Z bands, merge small islands, and avoid checkerboards around the full height.
11. **Purge is directional.** Dark-to-light transitions usually require more purge than light-to-dark. Maintain a transition matrix rather than one global number.
12. **Validate in the final slicer.** Inspect tool/color assignment, line type, every transition layer, wipe tower, flush destination, unsupported islands, thin-wall loss, and actual change count.

## 5. Parametric multicolor design workflow

For new CAD, color is a first-class parameter and body classification:

```text
functional contract and hardpoints
→ base geometry and orientation
→ semantic color regions
→ printable inlay/shell/insert architecture
→ named disjoint solids in one coordinate frame
→ 3MF assembly with portable material intent
→ destination-slicer slot mapping
→ purge/change review
→ coupon and final print
```

Use semantic names such as `body_orange`, `eyes_black`, `muzzle_white`, and `scarf_blue`, not `extruder_1`. Keep machine slots in a separate mapping file. Read `references/02-parametric-color-architecture.md` and `references/03-dfam-dimensions.md`.

## 6. Textured OBJ/GLB to four-color 3MF

Preserve the original mesh, material file, texture images, and hashes. Then choose one of two routes.

### Route A — fast GUI handoff

```text
OBJ/GLB + texture
→ repair and bake to one texture where practical
→ quantize preview to the actual four filaments
→ Bambu Studio Texture-to-Color Painting
→ save 3MF project
→ import into Anycubic Slicer Next
→ reassign four ACE slots
→ reslice and visually verify every color boundary
```

This route is fast but the painted project metadata is not guaranteed to transfer identically between slicers. Keep the source asset and palette report, and use Route B if import loses painting or changes topology.

### Route B — portable solid fallback

```bash
python3 "$MCFDM_SKILL/scripts/inspect_textured_asset.py" model.obj \
  --json-out build/inspect.json

python3 "$MCFDM_SKILL/scripts/quantize_texture.py" texture.png \
  --palette filament-palette.yaml \
  --output build/texture-4c.png \
  --report build/quantization.json

python3 "$MCFDM_SKILL/scripts/texture_to_voxel_parts.py" model.obj \
  --palette filament-palette.yaml \
  --pitch 0.8 --shell-depth 1.6 \
  --output-dir build/color-parts \
  --report build/partition-report.json

python3 "$MCFDM_SKILL/scripts/assemble_multicolor_3mf.py" \
  --parts-manifest build/color-parts/parts-manifest.json \
  --output build/model-4color.3mf

python3 "$MCFDM_SKILL/scripts/validate_multicolor_3mf.py" \
  build/model-4color.3mf --json-out build/3mf-report.json
```

The voxel route produces true color solids but is resolution-limited. Start with a coarse proxy, then reduce pitch only if the memory estimate and print resolution justify it. Read `references/04-textured-asset-to-multicolor-3mf.md`.

## 7. Purge and change optimization

Before slicing a large object, estimate active colors and minimum changes:

```bash
python3 "$MCFDM_SKILL/scripts/estimate_color_changes.py" \
  --parts-manifest build/color-parts/parts-manifest.json \
  --layer-height 0.2 \
  --purge-matrix assets/templates/purge-matrix.example.yaml \
  --json-out build/change-budget.json
```

Use the report to redesign, not only to tune the tower. The most effective waste reduction usually comes from fewer color islands and fewer layers that contain multiple colors. Read `references/07-purge-and-change-optimization.md`.

## 8. Required validation and delivery

A completed job should contain, as applicable:

1. `multicolor-job.yaml` and actual-filament palette;
2. immutable source assets and hashes;
3. editable CAD or conversion source;
4. named, aligned, manifold color solids;
5. standard multi-part 3MF and, when needed, a destination-slicer project;
6. palette/Delta-E report and removed-island report for texture conversions;
7. geometry and 3MF structural validation;
8. estimated active colors per layer, transitions, purge volume, and waste ratio;
9. screenshots or exported reports from the final slicer preview;
10. a color-boundary/purge coupon and physical acceptance notes.

A colorful render is not proof. A 3MF that opens is not proof that its colors map to the intended physical filaments. A slicer preview is not proof that the purge matrix prevents contamination.

## 9. Three included examples

Build and validate all examples:

```bash
python3 "$MCFDM_SKILL/scripts/build_examples.py" \
  --output-root build/examples
```

- `01-parametric-inlay-nameplate` — four named OpenSCAD solids; accents only in the top band to minimize changes.
- `02-four-color-fox-badge` — printable semantic inlays, minimum-feature checks, and a four-part 3MF.
- `03-textured-obj-to-four-color-3mf` — generated UV-textured OBJ/GLB, fixed-palette quantization, voxel color partition, and portable 3MF.

Read `references/12-examples.md` and each example README.

## Deterministic validation handoff

Before release, load the sibling `validate-printable-3d-projects` skill and apply `assets/validation-profile.json`. Hash all color solids, palette/filament mappings, 3MF, slicer profile, G-code, previews, and coupon reports. Require watertight positive-volume parts, deterministic 3MF material/build references, exact overlap/clearance checks where available, and G-code tool-change, bounds, time, and flow checks. Color-boundary contamination, purge sufficiency, filament identity, and final slicer interpretation remain named review or physical gates. A required `NOT_RUN`, `REVIEW_REQUIRED`, stale report, or missing coupon blocks release.

For an already-authored destination-slicer 3MF, use the sibling `fdm_ci.py slice-anycubic-next` adapter for headless batch export and hash-bound G-code checks. Do not use that CLI step to author painting or infer ACE slot correctness; retain the authoritative 3MF and complete the final color/tool/wipe-tower preview in Anycubic Slicer Next.

At project start, read the project autonomy policy before changing artifacts. Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger and only for stages assigned to the agent. Never write `HUMAN_APPROVED`; physical color/purge checks, appearance, safety, and commercial stages remain in the separate human ledger. Workflow autonomy does not authorize dependency installation, upload, or printer start.
