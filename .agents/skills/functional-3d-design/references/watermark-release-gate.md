# metriMade.com watermark release gate

Use the versioned generator package `MM-WM-001-R2`: in this workspace its canonical source is `tools/metrimade-watermark/`; a packaged skill carries the same pinned core under `assets/metrimade-watermark/`. Verify the revision and use exactly one source. Generate three purpose-built tiers; never obtain a smaller tier by scaling another:

| Tier | Visible content | Selection priority |
|---|---|---:|
| Full | owned logo, `metriMade.com`, `<PRODUCT_ID> · v<VERSION>` | 1 |
| Compact | owned logo, stacked `metriMade.com`, `<PRODUCT_ID>`, `v<VERSION>` | 2 |
| Micro | owned logo, stacked `<PRODUCT_ID>`, `v<VERSION>`; no visible domain | 3 |

Generate every tier from the immutable release identity. Never redraw the mark, substitute live text, edit identity text independently, or shorten/hash the human-readable product ID or version. Full and Compact retain the visible domain. Micro is a documented last resort when the selector proves that neither larger tier fits the measured safe region; retain the controlled domain in 3MF metadata and/or the provenance sidecar. The bundled asset is digitally validated but remains `DIGITAL_PRODUCTION_CANDIDATE_PHYSICAL_TEST_PENDING`; a passed coupon for the selected tier on the intended production process is mandatory before release approval.

## Mandatory coverage and migration

- Mark every independently distributed printable product or SKU on at least one durable primary body.
- For a multipart assembly, mark the main body and every separately saleable/reusable part that has a safe region. Record tiny or internal unmarked parts as covered by the marked assembly; the release must never contain no mark.
- Prefer a flat, nonfunctional, low-stress underside. Keep the mark out of holes, rails, seals, mating planes, threads, snap/flexure roots, high-stress zones, deliberate textures, and required bed-contact lands.
- Do not overwrite or silently rebuild historical releases carrying a JuSt Innovation or `MM-WM-001-R1` mark. Introduce `MM-WM-001-R2` only through a new product revision, retain the historical release, and rerun affected checks.

## Generate the exact product profile

Copy the complete workspace `tools/metrimade-watermark/` package, or the packaged skill's `assets/metrimade-watermark/` core, into the project as `assets/metrimade-watermark/`. Then generate the tiers from `project.id` and `project.revision`:

```bash
python assets/metrimade-watermark/tools/generate_watermark.py \
  --product-id MM-ORG-001 \
  --version 1.0.0 \
  --layout all \
  --output-root assets/metrimade-watermark/generated
```

Generation requires Inter Variable, OpenSCAD, ImageMagick, `fontTools`, and `trimesh`. It fails for a missing or malformed uppercase hyphenated product ID, a non-SemVer version, an unavailable dependency, an unknown layout, or invalid output geometry. Retain each tier's generated SVG, DXF, SCAD wrapper, mirrored STL cutter, coupon STL, PNG, metadata JSON, icon source, and `manifest.sha256` together.

Each generated tier size depends on the trace lines and is authoritative. Do not scale, crop, distort, reduce gaps, or remove required content. If Micro does not fit safely, use another surface or revise the product geometry.

## Select a process-safe placement

Measure the largest obstruction-free rectangle in CAD and run the selector against the generated metadata:

```bash
python scripts/select_watermark.py \
  --metadata assets/metrimade-watermark/generated \
  --surface-width 80 --surface-height 45 \
  --host-wall 2.0 --nozzle 0.4 --layer-height 0.2
```

The selector accepts one metadata JSON, repeated `--metadata` arguments, or a directory containing the generated tiers. It permits only 0° or 90° placement at scale 1.0 and chooses the highest-priority tier that fits. Default edge clearance is the larger of 2.0 mm or two nozzle diameters. Require a host wall of at least 1.20 mm and a remaining wall of at least 0.80 mm after engraving. Qualified depth is 0.40–0.80 mm; the generated default is 0.40 mm. Treat `BLOCK` as final for that candidate region.

## Integrate the exact geometry

- **OpenSCAD:** use the selected tier's generated SCAD wrapper directly or copy `source/metrimade-watermark.scad`, pass the selected SVG and its metadata width, and call `metrimade_watermark_cutter()` in a `difference()`.
- **CadQuery / FreeCAD:** import the generated closed DXF or SVG wires without scaling, extrude inward by the generated depth with a small Boolean overlap, and cut the host solid.
- **Blender:** import the generated SVG at millimetre scale, convert/extrude it as a cutter, apply transforms, and use an exact Boolean difference before mesh validation.

The generated STL cutter is mirrored in X so the finished underside reads normally. Verify the actual exported underside directly; a top-view CAD screenshot is not evidence. The cutter must remove material upward/inward and must not create geometry below the original bed datum.

## Validate before asking for final approval

Record asset revision, selected layout tier and priority, domain visibility, exact product ID/version, generated metadata and manifest hashes, actual envelope, rotation, position, surface, depth, edge/feature clearances, local wall before/after, marked-part coverage, printer/nozzle/material/profile, and production-geometry revision/hash in `design-spec.yaml` or linked evidence. When Micro is selected, retain the selector report proving Full and Compact did not fit and record where the controlled domain remains digitally available. The watermark identity must match the release manifest, filenames/package, and catalog identity.

Show all of the following from the actual production candidate:

1. orthographic finished-underside view with readable orientation and every identity line required by the selected tier;
2. dimensioned close-up with edge and feature clearances;
3. section showing recess depth, unchanged bed datum, and residual wall;
4. slicer preview of all watermark-bearing layers with no lost strokes, closed gaps, or ambiguous characters;
5. updated mesh/B-Rep validation;
6. a passed coupon generated from the selected tier for the exact intended printer, nozzle, layer profile, material/color, first-layer settings, and bed surface.

If the manufacturing export uses mesh simplification, select and validate its physical-tolerance policy before adding the mark. After the mark is cut, apply that policy only as a derived export operation with the complete watermark, surrounding bed datum, and all functional interfaces protected. Compare the final export against the marked high-fidelity reference. Any lost stroke, closed gap, identity mismatch, depth change, bed-contact loss, or host-wall violation blocks approval.

Set `workflow.watermark_approval.status: pending` only after the generated profile, placement evidence, slicer preview, and coupon result exist. After explicit approval, record it and run:

```bash
python scripts/validate_design_spec.py design-spec.yaml --require-final-approval
```

Do not emit a final package when this command fails. Later changes to product ID/version, marked geometry, export/simplification policy, orientation, printer/nozzle/material/profile, or marked-part coverage invalidate approval and require this gate again.

## Reporting prominence

Treat this gate as supporting release evidence, not as the product outcome. Keep one watermark item near the end of the working task list. In the complete release review and final handoff, present the actual 3D model, its functions, validation, print readiness, and deliverables first. If this gate passes, reduce its final status to one compact **Kennzeichnung** bullet or at most two short lines. Give it more space only when it blocks release or when the user asks for watermark details.
