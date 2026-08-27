# Printing Guide

**Revision 0.2.0 DRAFT.** No load or manufacturing release is implied.

## Start Profile

- Structural material: PETG, dry filament recommended.
- Nozzle: 0.6 mm.
- Line width: 0.68 mm.
- Layer height: 0.30 mm structural, 0.20-0.24 mm optional for decor inserts.
- Structural walls: 4 perimeters.
- Shelf top/bottom skin: geometry is modeled; use at least 5 top and bottom layers where applicable.
- Infill: provisional 15-20% gyroid for frame and modules. Exact slicing is still required; thin 2.8 mm module plates may have no reliable independent infill core.
- Local modifier: 5-6 walls around M4/M5 holes, segment pins, bracket roots and insert pockets.
- Supports: normally none. Inspect text, diamond finish and hanger return in the exact slicer.

## Orientations

- Seven side segments per side and shelf brackets: largest side face on the bed. Segment footprint is about 246.1 x 240 mm; verify brim/skirt clearance on the exact usable bed.
- Shelf tiles: exported with the smooth top face on the bed; ribs point upward during printing.
- Bins and drawer: bottom down.
- Drawer housing: exported rear-wall-down with the open front facing up; do not rotate it back to bottom-down.
- Fascias/header inserts: choose rear-face-down for raised relief and front-face-down for recessed/bed-imprint finishes; the exported orientation is a safe default, not a universal aesthetic choice.
- Four PETG feet, four TPU pads and all joiner plates: flat.
- Height-adjustable wall-restraint spacers: largest 34 x 80 mm face on the bed.
- Wide drawer housing, drawer and bin: print the exported left/right halves in their recorded orientation; do not recombine them before slicing.

## Mandatory Coupons

1. Print `fit_coupon_020_030_040_050_print.stl` in the frame material and orientation.
2. Select the smallest clearance that assembles by hand without cracking or permanent looseness.
3. Update `frame.connector_clearance` and `shelf.fit_clearance` before the full build.
4. Print `wide_module_m3_seam_coupon_print.stl` with the exact selected M3 inserts/nuts and screws before printing wide modules. Verify that the plate sits flat on both boss/contact faces without a gap before applying assembly torque.
5. Print `floor_foot_tpu_lock_coupon_print.stl` in production PETG/TPU and qualify receiver fit, four-nub pad retention, M4 foot lock, rocking and pad shear/pull-off.
6. Qualify the supplier-specific M4 heat-set and M5 through-bolt features on a process-matched sample or sacrificial frame offcut.
7. For image relief, print the header insert before printing the backer/frame.

## Exact slicer gate

No supported slicer CLI was available when the DRAFT geometry was generated. Save the reviewed project under `output/rev-0.2.0-draft/3mf/` and record slicer/version, printer/material/profile hash, time, model/support material, layers, walls, infill, seams, bridges, supports, retractions, warnings and peak volumetric flow. The 3MF is a release blocker.

## Load Label

Until physical validation is complete, use only:

> Prototype. No load rating.

After the documented tests pass, the intended label is:

> Maximum 4 kg per shelf, evenly distributed. No concentrated loads, sitting, leaning or climbing.

PETG creep is temperature- and process-dependent. Do not infer a rating from the CAD calculation alone.
