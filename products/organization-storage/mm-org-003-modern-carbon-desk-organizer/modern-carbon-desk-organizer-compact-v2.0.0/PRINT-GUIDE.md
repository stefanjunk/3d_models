# Provisional print guide

This guide is a starting profile, not completed slicer or physical evidence.

## Planned process

- material: ordinary PLA for indoor evaluation; Tough PLA is reasonable for later functional trials
- nozzle: 0.4 mm
- layer height: 0.20 mm
- nominal line width: 0.45 mm
- walls: 3 perimeters minimum
- top/bottom: 4 layers minimum where the slicer generates skins
- infill: 10–15% gyroid or equivalent for non-modeled interior regions
- supports: none intended in the documented orientations
- brim: optional for the housing if the printer shows edge lift

## Orientations and quantities

| Part | Quantity | Bed orientation |
|---|---:|---|
| housing | 1 | rear wall on the bed; the two openings point upward in machine Z |
| drawer | 2 | drawer bottom on the bed |
| top sorter | 1 | sorter bottom on the bed |
| fit coupon | 1 first | largest flat face on the bed |
| texture coupon | 1 first | integrated foot on the bed; textured wall vertical like the product |

Put each unique production part on its own plate. Print the drawer twice. Do not treat the inventory-strip placement encoded in the DRAFT 3MF as a ready-to-print plate arrangement.

## Recommended qualification order

1. Slice and print the fit coupon with the intended printer, filament and profile. Select the fit that moves freely without visible lateral rattle.
2. Print the texture coupon. Reject groove scales that snag, close up, or produce fragile ridges.
3. If coupon results differ from the nominal 0.45 mm drawer-side or 0.35 mm stack clearances, update `model-parameters.json` and rebuild all unchanged production artifacts. The 0.45 mm value is not qualified until this step passes.
4. Print housing, one drawer and sorter; check travel and stack registration before printing the second drawer.
5. Print the second drawer and test the unchanged assembly.

## Open checks

- exact slicer build-volume/orientation confirmation
- G-code support-island and first-layer inspection
- print time and deposited mass
- 500 drawer cycles
- 0.75 kg target load per drawer and loaded anti-tip behavior
- base flatness, stack retention, edge snagging and appearance under several light angles

The 1,046 g figure in `reports/optimization-comparison.json` is CAD solid volume multiplied by PLA density. It is not a slicer estimate of deposited material and must not be used as a purchase or runtime claim.
