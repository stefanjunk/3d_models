# Assembly — Revision 0.2.0 DRAFT

1. Measure the clear wall width, wall gap/substrate, toilet and cistern envelope, lid/service path, flush control, pipes, baseboard and floor flatness. Regenerate the model if they differ from `parameters.json`.
2. Select the exact M3/M4/M5 hardware and substrate-specific wall anchors. Do not substitute printed wall anchors.
3. Print and qualify `fit_coupon_020_030_040_050_print.stl` and `wide_module_m3_seam_coupon_print.stl` before the frame or modules.
4. Install M4 heat-set inserts in the shelf undersides using the supplier-qualified hole and heat procedure. Protect the shelf top.
5. Assemble each side frame from seven numbered segments. Seat both alignment pins at every seam and lock each seam with two M4 through-bolts, washers and locking nuts.
6. Install one rear and one front PETG foot on each side frame. Engage all four TPU retention nubs per pad, then lock each foot to the lower rail with one M4 x 50 through-bolt, two washers and a locking nut. All four pads must bear without rocking.
7. Bolt shelf brackets to matching 50-mm grid holes with M5 x 45 through-bolts, two washers and locking nuts. The default shelf-top datums are 1050 and 1400 mm from the finished floor. Use identical grid rows left/right.
8. Assemble three shelf tiles per level. Install two underside joiners at each seam with M4 x 16 screws, then bolt each shelf to its brackets from below with M4 x 20 screws. Use washers and the qualified insert engagement.
9. Assemble the center-split drawer housing, drawer and bin with the qualified M3 seam plates. Each 3-mm plate must sit flat on both 6-mm boss tops with no visible gap; do not use screw torque to pull a warped or mismatched seam into contact. Confirm that no screw or plate enters the drawer travel or shelf seating faces.
10. Slide fascia segments into the front capture rails. Lower modules behind the modeled front stop rail, then install the tray and hangers. Verify removal for cleaning and no initial contact with the stop.
11. Seat the header feet in the upper shelf sockets and install either the procedural insert or the separately validated image-relief insert.
12. Place one height-adjustable wall-gap spacer behind each rear side-frame rail. The default axes are Z=1480 and 1530 mm; another adjacent approved 50-mm pair may be used for a measured obstruction.
13. Install two substrate-specific wall screws/anchors per side through spacer and rear rail. The restraint is mandatory; the floor feet alone are not an approved free-standing anti-tip system.
14. Verify level/plumb, four-point floor contact, toilet/lid/pipe/baseboard/flush clearance, fastener/tool access, drawer travel and module removal before any load.

Do not glue primary structural joints. Do not load the DRAFT assembly until the physical sequence in `test-plan.yaml` has passed.
