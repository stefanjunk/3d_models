---
name: parametric-freeform-surfacing
description: Create, reconstruct, fair, parameterize, validate, and FDM-prepare smooth aesthetic curves and freeform product envelopes using B-splines/NURBS, section lofts, SubD, free-form deformation, morph targets, and local SDF blends. Use when a new shoe, vessel, vehicle body, enclosure, furniture part, or decorative product looks boxy or faceted; when hardpoints must remain exact while the visible shell becomes organic; or when an AI/scan reference must become an editable parametric surface rather than remain a dense mesh.
license: MIT
compatibility: OpenCode with project file access and Python 3.10+. NumPy and PyYAML are the core runtime; SciPy, Trimesh, CadQuery, build123d, geomdl, PyGeM, Blender, Rhino/Grasshopper, FreeCAD, Houdini, or nTop are optional backends.
metadata:
  version: "1.0.0"
  domain: "parametric freeform surfacing for additive manufacturing"
  manufacturing: "fdm-fff-first"
  inputs: "dimensions, hardpoints, guide curves, sections, sketches, reference images, reference meshes"
  outputs: "editable curves, aesthetic envelope, STEP when available, OBJ/STL/3MF handoff, fairness and printability reports"
  complements: "functional-3d-design, organic-mesh-functionalization, 3d-print-heightmap-relief"
---

# Parametric Freeform Surfacing

Create **editable, smooth product form**, not a box with large fillets and not an opaque AI mesh.

Use millimetres. Respond in the user's language. Keep functional dimensions and aesthetic form coupled by explicit named constraints, not by hidden vertex edits.

Set the skill path before using the supplied helpers:

```bash
# Project-local OpenCode installation
export PFS_SKILL=.opencode/skills/parametric-freeform-surfacing

# Typical global installation
# export PFS_SKILL=~/.config/opencode/skills/parametric-freeform-surfacing
```

## Ownership and companion routing

This skill owns:

- fair centerlines, silhouettes, rails, section curves, and curvature-controlled transitions;
- B-spline/NURBS, section loft, Gordon/network-surface, SubD, FFD/cage, morph-target, and local SDF strategies;
- the split between an exact functional core and an aesthetic envelope;
- fitting an editable envelope to an AI, scan, sketch, or image reference;
- continuity, fairness, tessellation, hardpoint-drift, and FDM surface-quality validation.

Load `functional-3d-design` as well for loads, interfaces, fasteners, tolerances, materials, nozzle/slicer choices, BOMs, assemblies, and physical tests.

Load `organic-mesh-functionalization` when the authoritative artifact is an existing dense STL/OBJ/GLB/3MF whose visible surface must be preserved during modification. This skill may reconstruct or deform a reference mesh, but it does not replace the source-preservation/ROI contract of that skill.

Load `3d-print-heightmap-relief` only after the mapping surface and seam policy are stable.

Read `references/00-scope-and-routing.md` before a composite workflow.

## Required design contract

Create `surfacing-spec.yaml` from `assets/templates/surfacing-spec.yaml`. Establish or explicitly assume:

- product family, intended visual language, scale, units, symmetry, and manufacturing route;
- authoritative hardpoints, interfaces, keep-out volumes, datum planes, and protected regions;
- the semantic parameters users may change, with valid ranges and dependencies;
- target continuity for every visible transition: G0, G1, G2, or intentionally sharp;
- reference provenance and whether it is a target, a protected source, or only inspiration;
- expected source and delivery formats, including whether STEP/B-Rep is mandatory;
- printer, nozzle, layer-height range, visible faces, build orientation, and surface acceptance criteria;
- validation thresholds for curvature oscillation, hardpoint drift, wall thickness, topology, and tessellation.

Validate the file:

```bash
python3 "$PFS_SKILL/scripts/validate_spec.py" surfacing-spec.yaml
```

## Core architecture: hardpoints plus aesthetic envelope

Default to three layers:

1. **Functional skeleton/core** — datums, joint axes, mounting faces, holes, sockets, clearances, load paths, wall targets, and print splits.
2. **Aesthetic envelope** — fair curves and surfaces controlled by a small set of semantic parameters.
3. **Late exact features** — regenerate holes, planar seats, threads, connectors, bearing fits, and split interfaces after freeform deformation or smoothing.

Do not smooth critical geometry and then trust it by visual inspection. Rebuild or revalidate exact features after every non-rigid envelope operation.

## Method selection

Use `scripts/route_method.py` and read the corresponding reference.

```bash
python3 "$PFS_SKILL/scripts/route_method.py" \
  --input new-parametric --hardpoints exact --editability high \
  --style-variants yes --local-blends yes --json route.json
```

Default choices:

- **B-spline/NURBS + loft/network surface** — dimensioned product shells, shoe outlines, vehicle silhouettes, vessels, STEP/B-Rep handoff, and controlled G1/G2 transitions.
- **SubD** — fast visual shaping with a sparse quad cage; convert or combine with exact CAD only at a deliberate handoff.
- **FFD/lattice or morph targets** — parameterize a good master shape or a retopologized AI/scan reference while holding hardpoint zones fixed.
- **Local SDF/implicit blend** — soften unions, ribs, branches, grips, and chassis transitions that are awkward as patch networks. Apply locally and restore exact features afterward.
- **Hybrid** — normal for products: B-Rep core, NURBS/SubD envelope, optional FFD variants, local SDF blends, then exact feature regeneration.

OpenSCAD-style primitive CSG is not the default for a premium visible shell. It remains useful for fixtures, coupons, patterns, and mathematically generated profiles.

## Curve and surface rules

1. Use semantic stations and few well-placed control points before adding degrees of freedom.
2. Approximate noisy data; do not force a spline through every scan or mesh vertex.
3. Parameterize corresponding sections consistently. Toe, heel, shoulder, beltline, rim peaks, and seams must use matching indices or landmarks.
4. Align closed-section seams before lofting. Test reversed orientation and cyclic shifts.
5. Prefer cubic or quintic curves for visible form. Use rational weights only where they add controlled conic behavior.
6. Specify continuity intentionally. G1 removes a tangent kink; G2 is the normal target for visible highlight flow; sharp/creased edges remain explicit design features.
7. Inspect curvature graphs, zebra/highlight flow, silhouettes, and sections. Smooth shading is not geometric evidence.
8. Keep source surfaces authoritative and derive print meshes with explicit chord, angle, and edge-length tolerances.

Read:

- `references/01-curve-fairness-continuity.md`
- `references/02-bspline-nurbs-lofts.md`
- `references/03-subd-ffd-morphs.md`
- `references/04-sdf-implicit-blending.md`

## AI and reference geometry

Treat AI output as one of these, never ambiguously:

- **visual target** — fit editable guide curves/sections to it;
- **master with stable topology** — drive controlled FFD or morph variants;
- **protected production mesh** — switch to `organic-mesh-functionalization`;
- **concept only** — extract proportions and style, not literal geometry.

Do not claim that a text-to-CAD or image-to-3D result preserves constraints merely because it looks correct. Record residual fit error, constraint satisfaction, topology, and parameter response. Read `references/05-ai-assisted-parametricization.md`.

## Deterministic helper commands

Fair and inspect a guide curve:

```bash
python3 "$PFS_SKILL/scripts/fair_curve.py" input.csv output.csv \
  --method regularized --strength 18 --preserve-ends \
  --report validation/curve-fairing.json

python3 "$PFS_SKILL/scripts/analyze_curve.py" output.csv \
  --report validation/curve-analysis.json

# Optional: fit an actual SciPy parametric B-spline and record knots/controls
python3 "$PFS_SKILL/scripts/fit_bspline.py" input.csv output-bspline.csv \
  --degree 3 --smoothing 2.0 --report validation/bspline-fit.json
```

Extract semantic closed sections from an AI/scan reference mesh (optional Trimesh backend):

```bash
python3 "$PFS_SKILL/scripts/extract_mesh_sections.py" source/reference.glb sections/ \
  --axis x --count 10 --points 128 --report validation/reference-sections.json
```

Loft equalized, seam-aligned closed sections:

```bash
python3 "$PFS_SKILL/scripts/loft_sections.py" sections/ exports/envelope.obj \
  --points-per-section 96 --stl exports/envelope.stl \
  --report validation/loft.json

# Optional CadQuery/OpenCascade STEP backend
python3 "$PFS_SKILL/scripts/backends/cadquery_loft_to_step.py" sections/ \
  exports/envelope.step --stl exports/envelope-cq.stl \
  --report validation/cadquery-loft.json
```

Apply a bounded FFD cage to an OBJ master:

```bash
python3 "$PFS_SKILL/scripts/ffd_deform.py" source/master.obj \
  assets/ffd-config.json exports/variant.obj \
  --report validation/ffd.json

python3 "$PFS_SKILL/scripts/compare_hardpoints.py" \
  validation/hardpoints-before.json validation/hardpoints-after.json \
  --point-tol 0.10 --axis-pos-tol 0.10 --axis-angle-tol 0.10 \
  --report validation/hardpoint-drift.json
```

Build the three supplied examples:

```bash
python3 "$PFS_SKILL/scripts/run_examples.py" --output build/examples
```

## Validation contract

A successful render or a watertight STL is insufficient. At minimum verify:

- all authoritative hardpoints remain within their declared tolerance;
- the parameter sweep produces no self-intersections, inverted sections, or abrupt style changes;
- visible guide curves have no unexplained curvature spikes or excess curvature extrema;
- intended joins satisfy the declared continuity target using the chosen CAD tool's continuity analysis;
- the envelope has the expected body count, normals, volume, and manifold/watertight state when it is meant to be a solid;
- minimum wall and local feature sizes survive tessellation and slicing;
- chord/normal/edge tolerances are recorded and visually checked on silhouettes and shallow curves;
- print orientation, layer stepping, seams, supports, bridges, and variable layer-height regions are reviewed in the slicer;
- AI/reference fitting error is reported separately from print-mesh tessellation error.

Use `references/08-validation-acceptance.md` and `references/06-fdm-surface-quality.md`.

## Non-negotiable rules

- Do not use a chain of boxes, straight extrusions, and constant-radius fillets as the only strategy when the visible form must be organic or sporty.
- Do not interpolate every noisy sample or add control points until a curve visually stops moving.
- Do not loft unregistered closed sections.
- Do not use smooth shading, subdivision preview, or render lighting as proof of geometric smoothness.
- Do not deform bores, bearing seats, mating planes, joint axes, or calibrated clearances without rebuilding and rechecking them.
- Do not globally voxelize or remesh a detailed source when a local blend, cage, or fitted envelope can solve the problem.
- Do not convert a dense mesh to a face-per-triangle B-Rep.
- Do not claim G2/Class-A quality without continuity or highlight-flow evidence from a tool that can measure it.
- Do not claim a print is smooth from CAD alone; inspect the exported triangles and sliced layers.

## Delivery layout

```text
project/
├── README.md
├── surfacing-spec.yaml
├── parameters.yaml
├── hardpoints.json
├── source/                 # curves, sections, CAD/SubD/FFD/SDF source
├── references/             # immutable visual or mesh targets + provenance
├── exports/                # STEP when available, then 3MF/OBJ/STL
├── previews/               # silhouettes, sections, curvature/zebra views
├── validation/             # fairness, hardpoint, topology, tessellation reports
├── profiles/               # printer/material/nozzle/slicer decisions
├── tests/                  # parameter sweeps, coupons, physical checks
└── CHANGELOG.md
```

Use `references/09-examples.md` for the barefoot shoe, organic bowl, and RC car patterns.
