# MM-ORG-009 — Tapered Drawer Perimeter Filler Rail Set

This project turns independent left/right front and rear drawer-gap measurements into two loose tapered filler rails. The rails close wedge-shaped perimeter voids around a rectangular organizer without clamps, adhesives or an interference fit. A separate 2–26 mm wedge gauge supports the measurement and clearance step.

Status: `0.1.0-draft.1` digital candidate through interface validation. The editable source, STEP masters, manufacturing STLs and three-object DRAFT 3MF are generated and pass deterministic geometry checks. Exact slicing, real-drawer fit, finish contact, removal cycles, watermark qualification and release approval remain open.

## Customize

Edit `config/model-parameters.json`:

- `left_front_gap`, `left_rear_gap`, `right_front_gap`, `right_rear_gap`: measured physical gaps;
- `length`, `height`: net rail envelope;
- `organizer_clearance`, `wall_clearance`: loose allowances subtracted from every measured gap;
- `end_relief`, `scallop_*`: end/hand-access geometry;
- `side_wall`, `top_skin`, `rib_thickness`, `max_rib_pitch`: manufacturing structure.

The generator rejects dimensions that erase the cavity, lift-scallop wall reserve, build-volume margin or support-free roof-bay rule.

## Build

```bash
python3 -m pytest -q tests/test_parameters.py
python3 cad/build.py
python3 cad/render_preview.py
```

The build is deterministic and writes only below this product folder. STEP and high-fidelity reference meshes stay in `exports/master/`; selected manufacturing meshes stay in `exports/manufacturing/` and `exports/coupons/`.

## Start printing

Print the taper gauge first and follow `PRINT-GUIDE.md`. The default rail values demonstrate the parameter contract; they are not a fit claim for an unmeasured drawer.
