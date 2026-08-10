---
name: functional-3d-design
description: Use when designing a functional FDM product with loads, motion, wear, purchased hardware, material choices, service life, assembly, or print-versus-buy decisions.
---

# Functional 3D Design

## Core Rule

Decide the mechanical system before choosing CadQuery, OpenSCAD, implicit
geometry, or a component library. Do not start sellable CAD from an unresolved
load path or component decision.

## Human Intake Gate

Before CAD, summarize the requirements, obtain explicit user approval, generate
and save a versioned concept image in the object folder, and obtain explicit
approval of that image. Record paths, approval notes, timestamps, and SHA-256
hashes in `design-intake.json`, then run:

```bash
python3 scripts/validate_design_intake.py design-intake.json \
  --report reports/design-intake.json
```

Only `DESIGN_INTAKE_PASS` allows geometry work. The concept is a visual
reference, not dimensional evidence. Revised requirements invalidate both
approvals; a revised concept invalidates only concept approval.

## Required Sequence

1. Pass the human intake gate.
2. State product intent, commercial status, constraints, environment, and
   customer-facing claims.
3. Decompose the product into mechanical functions.
4. For each function record load case, life requirement, and failure modes.
5. Classify each component as `PRINT`, `BUY`, `INTEGRATE`, `ELIMINATE`, or
   `NEEDS_TEST` using `references/print-vs-buy.md`.
6. Select PLA or PETG by default; justify ABS/ASA, TPU, or PA/CF using
   `references/material-selection.md`.
7. Apply `commercial-cad-provenance` to every library and imported asset.
8. Select standard parts and define interfaces, clearances, assembly order,
   tool access, and replacement access.
9. Assign supported nozzle classes using `fdm-process-envelope`.
10. Define coupons and measurable acceptance criteria.
11. Run `commercial-cad-provenance` and retain its JSON report.
12. Write `design-spec.json` and run:

```bash
python3 scripts/validate_design_spec.py design-spec.json \
  --provenance-report reports/commercial-license.json \
  --manufacturing-profile manufacturing-profile.json
```

13. Only `ENGINEERING_DECISION_PASS` allows detailed CAD implementation.

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

## Evidence-Backed Parts Library

Use `references/self-learning.md`, `scripts/parts_library.py`, and
`scripts/record_test_result.py` to retain local evidence. `qualified-local`
means only that a named revision passed a named plan on the recorded
printer/material/nozzle/profile. It is not universal validation or
certification.

Use `references/simulation-model-fidelity.md` before requesting simulation.
Choose the lowest fidelity that can change a decision and require physical
calibration when printed-material uncertainty controls the result.
