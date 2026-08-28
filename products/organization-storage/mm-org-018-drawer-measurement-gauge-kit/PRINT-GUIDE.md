# Print and use guide

Reference branch: Anycubic Kobra 3 Max, 0.4 mm nozzle, 0.20 mm Standard profile and Anycubic PLA. Every part prints on its broad 3.0 mm face with supports off. The exact ten-object preflight produced 15 layers, a 4,641 s estimate and 26,511.16 mm³ extrusion volume without native object warnings.

## Print and calibrate first

1. Print the calibration frame before relying on the rest of the kit.
2. Let parts condition for 24 hours in the measurement environment.
3. Remove only loose strings or brim. Do not file, sand, heat or scale a protected measurement surface.
4. With independent calipers, measure the frame's 130 mm length, 32 mm width, 3 mm thickness, 80 × 12 mm internal window, 10 mm circle and 10 mm square at three positions/directions where possible.
5. Record signed error as `actual − nominal`. If error is unacceptable, fix and requalify the print process; do not hide it with an undocumented CAD scale factor.
6. Measure every radius tile used and every comb finger used. Record actual values in the worksheet.

## Radius tiles

Hole mapping: 1 = R2, 2 = R4, 3 = R6, 4 = R8, 5 = R10, 6 = R12, all in millimetres.

Place the tile's rounded lower-left cutaway into the drawer corner with both straight tangent legs aligned to the drawer sides. Start at R2 and move upward. Record the smallest tile that seats fully without force; the next smaller tile is the interference bound, and the next larger tile is the clearance bound. Do not choose the largest fitting tile—larger cutaways are progressively looser.

## Taper and width at height

Stand one height card on its y = 0 base at each side of the drawer; flip one card so the ledges face inward. Rest a rigid ruler on matching one-hole, two-hole or three-hole ledges: 15, 35 or 55 mm respectively. Measure at front, middle and rear where accessible. Repeat at least twice and keep the smallest credible reading.

The cards do not replace calipers and do not create a calibrated span. Their only job is to hold a repeatable height datum.

## Clearance comb

Finger order from left to right is nominally 0.8/1.0/1.2/1.4/1.6/1.8/2.0 mm. Measure actual width first. Insert without force between a representative straight test piece and drawer wall; record the widest finger that enters freely and the narrowest that binds. This is a preference/fit coupon, not a certified feeler gauge.

Use `tests/drawer-measurement-worksheet.md` and `tests/physical-test-plan.md`. No G-code is retained and no printer upload or print-start action is authorized.
