# MM-ORG-004 — Modular Desktop Tray System

Parametric, support-conscious FDM tray modules for dry indoor desktop organization. This package implements research idea `SKU-002` and remains a DRAFT digital engineering candidate until the exact slicer profile and physical interface tests are complete.

## Controlled outputs

- `config/model-parameters.json`: source-of-truth dimensions and interface allowances
- `cad/build.py`: deterministic CadQuery generator and exporter
- `exports/master/`: editable-neutral STEP masters
- `exports/manufacturing/`: oriented STL parts
- `exports/3mf/`: multi-object DRAFT print set
- `exports/coupons/`: small interface coupon
- `reports/`: build, mesh, optimization and result evidence

The three trays intentionally use different corner treatments while sharing the same underside connector socket. The removable bow-tie link is trapped by the desk surface after bottom-side insertion; its fit is provisional until printed.

## Scope boundary

Not for food, liquids, hot tools, children, load-rated use, or commercial release. No physical print or fit result is claimed.
