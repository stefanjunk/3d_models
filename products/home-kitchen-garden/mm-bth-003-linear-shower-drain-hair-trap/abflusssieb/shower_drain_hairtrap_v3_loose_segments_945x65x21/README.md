# MM-BTH-003 — Linear Shower Drain Hair Trap

Status: **DRAFT production candidate; digitally validated, not physically released**.

## Official identity

- Product ID: **MM-BTH-003**
- Official designation: **Linear Shower Drain Hair Trap**
- Design revision: **3.1.0-draft.1**

## Approved geometry

- Installed envelope: **945.0 × 65.0 × 21.0 mm**
- **16** loose single segments at **52.5 mm**, one catcher each
- **1** loose marked double segment at **105.0 mm**, two catchers
- **17 parts / 18 catchers / no connectors**
- Nominal equation: `16 × 52.5 + 1 × 105.0 = 945.0 mm`
- 55 holes per catcher; 990 across the complete row

The marked double segment is placed between eight singles on each side in the assembly reference. Its left inner side wall carries the exact `MM-WM-001-R1` profile `metriMade.com / MM-BTH-003 · v3.1.0-draft.1` recessed **0.4 mm** at scale 1.0. A rigid local-X reflection sets the correct left-to-right reading direction from the drain cavity; it does not resize or redraw the profile. The 3.0 mm wall retains **2.6 mm**.

## Manufacturing files

- `exports/manufacturing/DRAFT-MM-BTH-003-3.1.0-draft.1-single-52p5mm-on-end.stl` — print **16 copies**
- `exports/manufacturing/DRAFT-MM-BTH-003-3.1.0-draft.1-double-105mm-marked-on-end.stl` — print **1 copy**
- Both files are already rotated +90° about assembly Y onto one complete U-profile end.
- `exports/master/DRAFT-MM-BTH-003-3.1.0-draft.1-17-part-assembly-reference.step` — 17-part nominal assembly reference
- `exports/master/DRAFT-MM-BTH-003-3.1.0-draft.1-single-52p5mm-master.step` and `exports/master/DRAFT-MM-BTH-003-3.1.0-draft.1-double-105mm-marked-master.step` — assembly-orientation STEP masters

## Selected slicer evidence

Anycubic Slicer Next 1.3.9.4 is the selected slicer. Validation uses the local Kobra 3 Max 0.4 mm user profiles `0.20mm PETG Tool @AC K3 Max` and `SUNLU PETG Black new @Anycubic Kobra 3 Max 0.4 nozzle`. The actual printer unit/firmware, nozzle identity, filament color/batch, and physical results still require recording.

## Release boundary

Do not treat this DRAFT as a released product. Before release, print the canonical watermark coupon and representative parts in the named PETG process; inspect watermark readability, installed fit, cumulative gaps, sharp edges, drainage, cleaning, and hair retention. Printer upload/start is not authorized by this project.
