# Final model result — MM-ORG-029

## Outcome

`MM-ORG-029 CraftOrbit 4` is a complete, fully parametric **draft digital print candidate** for portfolio SKU-160 (opportunity 87.8, rank 21). The validation aggregate is PASS with 54 required checks passed and two optional physical/commercial blocks intentionally left `REVIEW_REQUIRED`.

The product is limited to dry indoor adult craft supplies. Hot tools, solvents, liquids, food contact, unsupervised child use, transport locking and carrying by the nameplate boss are excluded.

## Delivered system

- Four instances of one 150.4 × 95 × 65 mm maximum-envelope, two-compartment caddy mesh with protected 3.0 mm wall/base and vertical female dovetail.
- One 84 × 84 × 38 mm maximum-envelope shared center cup with four 16/22 × 6 × 25 mm captive dovetail keys built from Z=0.
- Four flat-printed 70 × 24 × 2.0 mm nameplates (`ALEX`, `BLAIR`, `CASEY`, `DEVIN`) in nominal 2.4 × 70.4 mm receiver slots.
- One 0.20/0.40/0.60 mm total-clearance docking gauge and one exact dovetail key; selected nominal production clearance is 0.40 mm total.
- Repository-owned `MM-GRID-5X7-v1` glyph geometry, validated CSV-derived participant batch and exact SVG proof generated from the same normalization/layout source.
- Ten STEP files including the virtual docked assembly, eight selected STL files, one light non-manufacturing variant STL and one eleven-object selected 3MF build plate.

## Digital evidence

- 14 parameter, identity, interface, nesting, content-boundary and exact-proof regressions: PASS.
- Nine independent mesh audits: all selected and variant meshes are watertight, winding-consistent, positive-volume, single-component and below declared budgets.
- The selected 3MF contains eleven valid millimetre mesh objects with no structural warnings and collision-free conservative nesting.
- The first 0.20 mm slice exposed one native floating-cantilever warning because hub keys began at Z=3 mm. Keys and channels were revised to Z=0, every artifact was regenerated, and both retained exact slicer reports are warning-free.
- Exact Anycubic Slicer Next 1.3.9.4 PLA preflights at 0.20/0.28 mm each use one tool and zero tool changes. No G-code was retained.
- Selected 0.20 mm system: 325 layers, 68,944 s estimate and 483,127.77 mm³ extrusion. The 0.28 mm comparison is faster at 59,613 s but rises to 503,236.70 mm³ and retains only 2.14 nominal engraving layers; 0.20 mm is the sole feasible Pareto variant.
- Selected geometric volume is 80.75% below four solid caddy envelopes plus a solid hub. A 2.4 mm caddy shell saves another 14.72% per caddy but remains rejected without physical flex, drop and loaded-docking evidence.
- Digital approval chain through `print-candidate`: PASS and hash-bound.
- Learning capture: new E0 candidate `EXP-00020` plus a targeted warning-regression eval, and existing E0 personalization candidate `EXP-00005` updated with the fifth geometry and a dedicated CSV-name identity eval. The learning store validates with 40 records; no production-rule promotion occurred.

## Remaining physical owner gates

Print the exact key and gauge first and select the lowest repeatable sliding clearance. Then qualify one caddy/hub/nameplate set for insertion force, 750 g representative load, 10° loaded tip, maximum 0.8 mm corner lift, unloaded 100 mm edge drops, 250 docking cycles and 100 nameplate cycles. Only then print and asymmetrically load all four positions.

The customer must approve the exact names before manufacture, and commercial provenance/release remains a separate human gate. Until physical evidence exists, do not claim load capacity, impact life, cycle life, child safety, liquid/chemical resistance or commercial release readiness.
