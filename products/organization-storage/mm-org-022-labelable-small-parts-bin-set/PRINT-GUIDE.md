# Print guide — draft candidate

1. Print `exports/coupons/DRAFT-MM-ORG-022-label-slot-gauge-0.1.0-draft.1.stl` first and select the smallest slot that accepts the actual label card without buckling.
2. Print one narrow bin and verify the label, pickup ramp and frame clearance before committing to a full set.
3. Reference process: Anycubic Kobra 3 Max, 0.4 mm nozzle, 0.20 mm Standard profile, Anycubic PLA, flat/base-down, no supports.
4. Do not rescale. Keep labels at or below 0.4 mm thickness for the nominal 0.7 mm CAD slot; customize the parameter if the gauge selects otherwise.
5. Electronics preset: six narrow bins and one wide bin. Sewing preset: two narrow and four medium bins. Each uses one matrix frame.
6. Inspect the front rails, grip opening and ramp in layer preview. Reject any missing thin wall, fused slot, lifted corner or sharp burr.
7. Follow `tests/physical-test-plan.md`; record the exact filament, color/batch, nozzle and profile in `tests/measurement-worksheet.md`.

No G-code is included or sent to a printer automatically.
