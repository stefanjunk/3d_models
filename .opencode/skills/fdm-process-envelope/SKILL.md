---
name: fdm-process-envelope
description: Use when a commercial FDM model must declare support for 0.4, 0.6, or 0.8 mm nozzles, PLA/PETG or specialist materials, minimum features, fits, snaps, and customer qualification requirements.
---

# Generic FDM Process Envelope

## Core Rule

Qualify geometry classes, not arbitrary printers. A universal STL claim is
invalid when a critical feature depends on slicer compensation, calibration,
material, orientation, or line-width behavior.

## Nozzle Classes

Read `references/nozzle-classes.json`. Evaluate each advertised class
independently. A product may recommend 0.6 mm while supporting 0.4 mm and
excluding 0.8 mm.

## Material Defaults

- PLA: economical static indoor baseline
- PETG: primary functional baseline where ductility is useful
- ABS/ASA: conditional for heat/outdoor/environmental needs
- TPU: conditional for flexible functions
- PA/CF: conditional specialist material; require drying and hardened nozzle

## Workflow

1. Declare minimum designed wall and feature dimensions from source parameters.
2. Record whether the model contains press fits, snap-fits, flexures, gears,
   seals, or load-bearing interfaces.
3. Run `scripts/evaluate_process_envelope.py` for each nozzle/material claim.
4. Generate the required coupons from `references/coupon-matrix.md`.
5. Keep printer/slicer compensation outside the master geometry until physical
   calibration justifies a documented variant.

## Completion Gate

`SUPPORTED` is a conservative geometry-screen result. `CONDITIONAL` requires
the listed coupons and customer process qualification. `UNSUPPORTED` requires
redesign or removal of that nozzle/material claim.
