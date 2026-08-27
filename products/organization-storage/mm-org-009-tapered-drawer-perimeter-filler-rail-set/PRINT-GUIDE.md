# DRAFT print guide — MM-ORG-009 / 0.1.0-draft.1

## Measure and regenerate

1. Measure each side gap beside the organizer near the drawer front and rear. Keep the organizer square in its intended position.
2. The gauge widens linearly from 2 to 26 mm over 80 mm. Its paired edge notches indicate 6, 10, 14, 18, 22 and 26 mm from tip to handle. Use calipers for the final value when available.
3. Enter the four measured gaps in `config/model-parameters.json`. The generator subtracts 0.5 mm at the organizer and 0.6 mm at the drawer wall by default; do not pre-subtract them.
4. Regenerate and confirm the reported effective front/rear widths are positive and plausible.

## Conservative starting profile

- Material: unfilled PLA from the exact supplier/printer profile; dry indoor service only.
- Nozzle: 0.4 mm brass or other supplier-approved nozzle.
- Layer height: 0.20 mm.
- Line width: 0.45 mm starting value.
- Walls: 3 perimeters.
- Top/bottom: 5 layers starting value.
- Infill: 10% gyroid/cubic starting value; the important shell/ribs are modeled explicitly.
- Nominal speed: 45 mm/s starting point, approximately 4.05 mm³/s at the stated width/layer.
- Temperature and cooling: use the exact filament/printer profile, not a generic temperature copied from this document.

## Orientation and support

- Rails: keep the exported orientation, with longitudinal walls and cross-ribs on the bed and the open hidden underside facing down.
- Gauge: largest flat face on the bed.
- Generated support: none. Inspect the first roof bridge layer over every rib bay; the modeled unsupported span is below 12 mm.
- Brim: normally unnecessary for the gauge; consider a narrow brim for the 210 mm rails only if the exact PLA/profile shows corner lift.

## Required checks before a full pair

Print the gauge first. Confirm width reading, loose clearance, surface contact and edge quality. Then print one customized rail and verify placement/removal before committing to the second. Do not force a tight rail into a finished drawer.

The included 3MF is a geometry-only DRAFT package, not an exact printer/material/slicer project. No compatible slicer CLI/profile was available in this workspace, so estimated time, material, first-layer paths and G-code remain deliberately unclaimed.
