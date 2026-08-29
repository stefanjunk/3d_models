# OpenQuad CF5 integration review

Date: 2026-08-29

## Evidence result

- The archive and extracted package are byte-for-byte/file-for-file consistent.
- The package's numerical rules pass: estimated takeoff mass is 539.8 g,
  adjacent propeller-tip gap is 32.9 mm and deck-to-prop XY clearance is 10.2 mm.
- All 13 checked OpenSCAD/analysis parameter pairs agree and delimiters are sane.
- A temporary OpenSCAD 2021.01 render check produced all seven selectable print
  parts, and each transient STL passed load, watertight, winding and
  positive-volume audit. These files were deliberately not adopted as controlled
  manufacturing outputs before requirements/concept approval.
- No controlled exported mesh, exact slicer result, physical coupon, propulsion
  test or flight evidence exists.
- The package's own `PRELIMINARY / NOT FLIGHT PROVEN` warning is correct.

## Improvements captured at requirements level

- Promote FPV from an optional BOM branch to the controlled air/ground reference
  stack: RunCam Phoenix 2 SE V2, SpeedyBee TX800 and analog goggles/display.
- Keep ELRS control independent from video; verify LBT/legal settings, antenna
  placement, carbon shadowing and VTX cooling on the assembled aircraft.
- Generate an arm-fit coupon before any full set and measure the exact carbon
  tube, motor, stack, battery, camera and VTX units.
- After approval, export controlled/hashes meshes and add exact slicer, clamp
  proof, accelerometer/vibration and restrained propulsion evidence before a
  qualified first-hover review.
- Treat the 2.175 mm clamp-hole-to-channel web and 2.3 mm outer-edge web as
  physically test-dependent minimums, not proven safety margins.
- Compare the 539.8 g hybrid candidate with a conventional carbon frame before
  committing to flight hardware; the hybrid is valuable for local fabrication
  but is not automatically the lighter or safer option.

No CAD was changed because the guided workflow still requires explicit
requirements and concept approval.
