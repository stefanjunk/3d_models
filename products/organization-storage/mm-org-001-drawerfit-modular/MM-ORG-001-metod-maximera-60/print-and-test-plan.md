# MM-ORG-001 DRAFT print and test plan

## Process lock

Use the same printer, nozzle, filament, drying state, orientation, line width, layer height, perimeter strategy, elephant-foot compensation and cooling for coupons and later modules. Starting geometry assumptions are PETG, `0.4 mm` nozzle, `0.44 mm` line width, `0.20 mm` layer height, floor-down, and no supports. Temperatures, speeds, extrusion multiplier and exact printer profile remain unresolved and must be recorded from the selected filament/printer setup.

## Required order

1. Measure the exact drawer at multiple heights and front/middle/back positions. Record minimum width/depth, corner obstruction/radius, available height and drawer revision. The published accessory envelope is not a substitute.
2. Slice the male connector and all three female coupons. Start physical insertion with `c060`, then `c045`, then `c030`; never force the tighter coupon.
3. Record actual printed dimensions, insertion/removal force qualitatively, visible gap, coplanarity, rocking, stress whitening and damage. Select the smallest clearance that repeatedly seats by hand without damage or objectionable play. If none passes, stop and generate a wider/finer sweep.
4. If the winner is not `0.45 mm`, update `draft_clearance_per_side`, increment the geometry revision and rebuild every module/report/3MF before module printing.
5. Print the comb-interface gauge. It must enter the lane by hand, remain flat and show usable but not excessive side clearance. Then print the actual comb and test all eight slots with the intended screwdriver sample range.
6. Print the drawer-corner coupon and check corner contact/material finish. This coupon does not prove the full 512 × 491 mm envelope; the measurements from step 1 remain mandatory.
7. Slice two representative adjoining hardware modules only after steps 1–6 pass. Use `module-r2-c2` and `module-r2-c3` to inspect one connector-bearing seam that crosses the functional bin field. Check floor coplanarity, wall alignment, snagging and rocking.
8. Only after the representative seam passes, slice and print the remaining modules. Assemble without modification, then run the 5 kg distributed-load and 100 drawer-cycle test.

## Stop rules

- No full nine-module print before connector, comb and measured drawer gates pass.
- No sanding/scaling to convert a failure into a pass; revise source parameters instead.
- No compatibility claim before the exact target drawer/revision passes.
- No watermark until the geometry is frozen and a separate marking coupon is approved.
- No release from a DRAFT file.
