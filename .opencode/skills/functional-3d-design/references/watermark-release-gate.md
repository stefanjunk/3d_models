# JuSt Innovation watermark release gate

Use the bundled proprietary production outlines under `assets/just-innovation-watermark/`. The approved asset is `JSI-WM-001-R1`: a standard 32 × 10 mm JuSt Innovation lockup and a compact hexagonal JS mark measuring 10 mm across flats (11.423 × 10 mm envelope). Do not recreate it with a font.

## Mandatory coverage

- Mark every independently distributed printable product or SKU on at least one durable primary body.
- For a multipart assembly, mark the main body and every separately saleable/reusable part that has a safe region. Record tiny or internal unmarked parts as covered by the marked assembly; the release must never contain no mark.
- Prefer a recessed mark on the print-bed-facing underside. If that surface cannot accept the minimum compact mark safely, use another noncritical external surface and document it. If no safe surface exists, block release and request a design/placement decision.
- Keep the mark out of holes, rails, seals, mating planes, threads, snap/flexure roots, high-stress zones, deliberate textures, and required bed-contact lands.

## Select a process-safe size

Measure the largest obstruction-free rectangle in CAD. Then run:

```bash
python scripts/select_watermark.py \
  --surface-width 80 --surface-height 45 \
  --host-wall 2.0 --nozzle 0.4 --layer-height 0.2
```

The selector preserves the approved aspect ratio and scales up for nozzle capability and host size. It prefers the full standard mark on sufficiently large products and otherwise uses the compact mark. It never shrinks below the process-safe production size. Default recess depth is 0.40 mm and default edge clearance is the larger of 2.0 mm or two nozzle diameters.

Treat `BLOCK` as final: choose a larger safe region, another orientation/surface, or a finer validated nozzle/profile. Do not distort the mark, reduce clear gaps, crop it, or omit it. Require host thickness of at least `max(1.20 mm, depth + 2 × nozzle)` at the cut and retain any larger structural wall requirement.

## Integrate the exact geometry

- **OpenSCAD:** copy the complete asset folder so `source/just-innovation-watermark.scad` retains its relative DXF paths; call `jsi_watermark_cutter()` in a `difference()`.
- **CadQuery / FreeCAD:** import the selected closed DXF wires, apply the selector's uniform scale and rotation, extrude them inward by the selected depth with a small Boolean overlap, and cut the host solid.
- **Blender:** import the selected SVG, preserve millimetre scale, convert/extrude it as a cutter, apply transforms, and use an exact Boolean difference before mesh validation.
- For curved fallback surfaces, map/project the outlines without changing local stroke/gap limits. Validate distortion and depth over the full mark.

Orient the source so the mark reads normally when the finished underside is viewed from outside. A top-view CAD screenshot is not evidence; verify the exported underside directly. The cutter must remove material upward/inward and must not create any geometry below the original bed datum.

## Validate before asking for final approval

Record asset ID, profile, nominal and actual envelope, uniform scale, rotation, position, surface, depth, edge/feature clearances, local wall before/after, marked-part coverage, nozzle/profile, and geometry revision/hash in `design-spec.yaml` or linked evidence.

Show all of the following from the actual production candidate:

1. orthographic finished-underside view with readable orientation;
2. dimensioned close-up with edge and feature clearances;
3. section showing 0.40 mm recess, unchanged bed datum, and residual wall;
4. slicer preview of the first watermark-bearing layers with no lost strokes or closed gaps;
5. updated mesh/B-Rep validation and, for a new nozzle/material/profile, a small coupon plan or result.

Set `workflow.watermark_approval.status: pending` only after these artifacts exist. After explicit approval, record them and run:

```bash
python scripts/validate_design_spec.py design-spec.yaml --require-final-approval
```

Do not emit a final package when this command fails. Later changes to the marked geometry, orientation, print profile, or watermark invalidate approval and require this gate again.
