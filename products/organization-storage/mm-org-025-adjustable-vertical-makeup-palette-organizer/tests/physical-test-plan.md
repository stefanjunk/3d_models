# Deferred physical test plan

Owner status: intentionally deferred until printing. None of these criteria is digitally proven.

1. Print fit key and slot gauge first with the intended PETG, orientation, and profile. Select the narrowest station that accepts ten insert/remove cycles by hand without whitening, fracture, or tool force.
2. If the selected station is not 2.9 mm, update `base.slot_width_mm`, rebuild every artifact, and invalidate old downstream hashes.
3. Load six inert blanks matching the recorded palette envelopes and masses. Verify each has at least 1.0 mm free retrieval clearance and does not bind at hinge protrusions.
4. Place the organizer on the intended dry surface. Push each blank at its top edge from front, rear, and both sides; reject visible tip initiation or base lift during normal retrieval motions.
5. Run 100 insertion/removal cycles for each blank and inspect palette-case finish and printed contact edges under raking light. Reject sharp ridges, visible scratching, or transfer.
6. Run 500 divider remove/reinsert cycles across representative stations. Reject cracked tongues, rail cracks, retention loss, or a slot-width change over 0.2 mm.
7. Keep the loaded organizer for 7 days at indoor ambient conditions, away from sunlight and heated tools. Reject creep that causes divider disengagement or retrieval binding.

Record material manufacturer/product/color/batch, drying, nozzle, machine, layer height, orientation, slicer/profile version, room conditions, blank dimensions/mass, and measurement method.
