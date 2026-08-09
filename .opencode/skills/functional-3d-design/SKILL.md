---
name: functional-3d-design
description: Use when designing a functional FDM product with loads, motion, wear, purchased hardware, material choices, service life, assembly, or print-versus-buy decisions.
---

# Functional 3D Design

## Core Rule

Decide the mechanical system before choosing CadQuery, OpenSCAD, implicit
geometry, or a component library. Do not start sellable CAD from an unresolved
load path or component decision.

## Required Sequence

1. State product intent, commercial status, constraints, environment, and
   customer-facing claims.
2. Decompose the product into mechanical functions.
3. For each function record load case, life requirement, and failure modes.
4. Classify each component as `PRINT`, `BUY`, `INTEGRATE`, `ELIMINATE`, or
   `NEEDS_TEST` using `references/print-vs-buy.md`.
5. Select PLA or PETG by default; justify ABS/ASA, TPU, or PA/CF using
   `references/material-selection.md`.
6. Apply `commercial-cad-provenance` to every library and imported asset.
7. Select standard parts and define interfaces, clearances, assembly order,
   tool access, and replacement access.
8. Assign supported nozzle classes using `fdm-process-envelope`.
9. Define coupons and measurable acceptance criteria.
10. Run `commercial-cad-provenance` and retain its JSON report.
11. Write `design-spec.json` and run:

```bash
python3 scripts/validate_design_spec.py design-spec.json \
  --provenance-report reports/commercial-license.json \
  --manufacturing-profile manufacturing-profile.json
```

11. Only `ENGINEERING_DECISION_PASS` allows detailed CAD implementation.

## Print-vs-Buy Principle

Print custom geometry. Buy precision, wear surfaces, highly cycled springs,
bearings, shafts, belts, seals, and standard fasteners unless a documented
low-risk use case justifies printing. Prefer eliminating components through an
integrated boss, flexure, captive nut, or snap-fit only when the resulting
failure mode is testable and commercially supportable.

## Output

Use `references/design-spec-template.json` as the starting artifact. Unresolved
loads, life, license, material, nozzle support, or test criteria are blockers,
not silent assumptions.

## Completion Gate

`ENGINEERING_DECISION_PASS` authorizes implementation, not commercial release.
Release still requires dimensional, assembly, mesh, FDM, slicer, coupon, and
physical qualification gates appropriate to the claims.
