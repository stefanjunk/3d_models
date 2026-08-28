# Print and use guide

Reference preflight: Anycubic Kobra 3 Max, 0.4 mm nozzle, 0.20 mm Standard and Anycubic PLA. The combined three-object plate slices in 160 layers with a 16,739 s estimate and 128,291.60 mm³ extrusion volume. Native slicing reports no object warning, one tool and no tool changes.

## Measure before generating

1. Measure the maximum cartridge depth, thickness and height at three locations. Include wrappers or protrusions that must enter the rack.
2. Use the largest credible value in the envelope preset. Tape width is inventory metadata, not a slot dimension.
3. Set the desired count and per-side clearance. The supplied examples use 0.50 mm per side and 1.00 mm rear depth clearance.
4. Generate the coupon and rack again after any parameter change.

## Print order

1. Print the clearance coupon base-down with supports off.
2. Test only a lower cartridge corner in the one-hole, two-hole and three-hole bays: 0.30, 0.50 and 0.70 mm per side. Select the smallest bay that inserts and removes without force after cooling.
3. Transfer that result to `slot_clearance_mm`, regenerate, then print one rack broad base down. A brim is optional only if local first-layer adhesion requires it.
4. Do not sand or scale protected slot or connector surfaces without recording the change.

## Use

Insert cartridges with their most stable lower edge on the base and rest the rear face on the inclined stop. The low front rail exposes most of the body for retrieval. Apply a narrow adhesive label in each rectangular recess and use the paired circular recesses for two inventory states, for example available/reorder. Avoid permanent brand text in the CAD source.

Join racks front-aligned by sliding the right-side planar tabs into the next rack's left sockets. Different preset depths share absolute connector datums at Y=25 and 55 mm. Treat the nominal 0.25 mm joint clearance as a hypothesis until printed.

Complete `tests/physical-test-plan.md` before making compatibility, durability or stability claims. No G-code is retained and no printer upload or print-start action is authorized.
