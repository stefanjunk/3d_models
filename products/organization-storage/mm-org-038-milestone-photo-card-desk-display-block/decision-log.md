# Decision log

- 2026-08-28: selected portfolio `SKU-180` after MM-ORG-037 reached synchronized digital print-candidate status; its weighted implementation score was `85.0`.
- 2026-08-28: current-market research found reviewed photo-block products, milestone and employee-anniversary use, replaceable-photo demand, and complaints about small blocks and rotating metal clips; retained demand magnitude, willingness to pay, and realized market fit as hypotheses.
- 2026-08-28: rejected purchased clips and magnets. Selected a one-piece dual-rail base with two rigid tapered slots to reduce BOM, assembly, pinch, rotation, and sourcing risks.
- 2026-08-28: selected a `150 x 52 x 22 mm` envelope with a `120 x 10 mm` rear photo slot and a right-offset `50 x 8 mm` front milestone-card slot. Two low bridges join the rails while leaving an open center that reduces material.
- 2026-08-28: selected a shared `2.8 mm` top gap, `0.2 mm` floor gap, and `8°` back tilt for the intended `0.25–1.2 mm` stock range. This is a geometric target; actual coating, stiffness, extrusion width, and surface finish remain physical variables.
- 2026-08-28: created a `75 x 24 x 14 mm` gauge that reproduces both exact groove depths and taper instead of treating a successful full print as fit evidence.
- 2026-08-28: selected the unscaled R2 Full identity at priority 1. Its `80.292 x 12.8 mm` envelope fits the rear-rail underside with `2.0 mm` edge clearance, and the `0.4 mm` recess leaves `11.6 mm` before the rear slot floor.
- 2026-08-28: used only the neutral `YOUR MOMENT` placeholder and recorded a no-retention privacy workflow for customer photos, names, dates, and card artwork.
- 2026-08-28: strict topology checks passed for three one-component watertight meshes and strict package checks passed for the one-object base and two-object coupon 3MFs.
- 2026-08-28: retained the one-piece rail-and-bridge layout after it reduced CAD volume by `38.29%` versus an equally marked solid-envelope proxy while preserving both rails, groove floors, bridges, marking land, and desk contact.
- 2026-08-28: preserved the initial coupon slice run-001 relative-path failure as diagnostic evidence and moved to fresh absolute-path run-002 output without rewriting or hiding the failed run.
- 2026-08-28: exact Anycubic Slicer Next 1.3.9.4 run-002 slices passed without native warnings or generated support. Both G-codes use tool 0 with no tool changes; parsed peak flows are `13.00013` and `13.00002 mm³/s`, within the bounded `13.3 mm³/s` audit ceiling around the exact profile's `13 mm³/s` declaration.
- 2026-08-28: reached digital print-candidate status with strict aggregate validation PASS and autonomous approval through print candidate. Actual card fit and marking, loaded stability, 100 swaps, hidden margin, final preview, mark legibility, appearance, safety, privacy workflow, and commercial release remain human-controlled.
