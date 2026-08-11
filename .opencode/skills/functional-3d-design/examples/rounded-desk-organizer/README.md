# Rounded two-drawer desk organizer

This example demonstrates that **more integration is not always fewer problems**. A one-piece organizer would create long roofs over the drawer cavities. The design therefore uses a one-piece lower carcass, a one-piece divided upper tray, two drawers, and four simple alignment pins.

## Build

```bash
python model.py --out generated
```

The lower carcass has a separate print-oriented STL with its back panel on the bed. STEP files remain in assembled coordinates.

## Material choices

- PLA/PLA+: easiest for normal indoor use away from heat.
- PETG: tougher and more temperature tolerant, but drawer/bridge calibration may need more care.
- ASA: useful for heat/UV only with an appropriate enclosed process.

Drawer clearance is deliberately a parameter. Print a small coupon before committing to the full body.
