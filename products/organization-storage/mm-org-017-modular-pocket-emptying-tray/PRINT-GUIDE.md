# Print guide

Reference setup: Anycubic Kobra 3 Max, 0.4 mm nozzle, 0.20 mm Standard profile and Anycubic PLA. This is the exact digitally checked branch, not a universal material/process qualification.

## Orientation and slicer setup

- Print every part on its broad z = 0 face; bowls open upward.
- Supports: off.
- Keep the 3MF object positions or place individual parts with at least 5 mm separation.
- Use normal wall and bottom settings from the named profile. Do not reduce the modeled 2.4 mm base or 2.0 mm walls in the slicer.
- Brim is normally unnecessary on the reference bed; if your material lifts, add only a removable external brim and re-check the connector edges after removal.

The exact five-object preflight produced 110 layers, a 9,174 s estimate and 55,138.09 mm³ extrusion volume. No native object warning appeared. Preview the layers locally before printing.

## Qualify the connector first

1. Print only the gauge and key if this machine/material/color has not been tested.
2. Let both parts cool completely and remove elephant-foot residue without changing the nominal side faces.
3. Lower the key's trapezoid into each open-edge socket with its handle outside the plate; do not force or hammer it.
4. Socket identity is one hole = 0.15 mm, two holes = 0.25 mm, three holes = 0.35 mm offset.
5. Select the smallest socket that inserts/removes by hand without whitening, cracking or permanent looseness.
6. The production JSON uses 0.25 mm. If another socket wins, change `connector.default_clearance_mm`, regenerate every artifact and repeat digital checks before printing modules.

## Assemble modules

- Put the first module flat on the surface.
- Align the next module's left through-socket over the first module's right tab and lower it vertically at the 56 mm pitch.
- Connect the third module the same way. Do not slide or bend the tab sideways.
- Lift the socket-side module vertically to separate. Do not lift a three-module chain by one end until the physical lift test has passed.

## Use limits

- Adult dry-indoor use only.
- The front ramp is for sweeping loose coins or similar small blunt items by hand; it is not a chute for food, pills or child-accessible parts.
- Keep watches, phone screens and other scratch-sensitive finishes out of bare PLA modules unless your own abrasion test approves the exact finish.
- Stop using a module if the connector cracks, whitens, loosens, develops sharp edges or rocks on the surface.

Follow `tests/physical-test-plan.md` for the intentionally deferred validation.
