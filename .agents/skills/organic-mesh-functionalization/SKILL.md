---
name: organic-mesh-functionalization
description: Add precise parametric or functional geometry to high-resolution organic AI-generated meshes. Use for hollowing, cutting openings, replacing regions, fitting inserts, adding compartments, stairs, hinges, soles, mounts, ducts, threads, or other engineered features to STL/OBJ/GLB meshes while preserving ornamented surfaces and validating topology, wall thickness, fit, printability, and unintended changes. Covers Blender, CadQuery, FreeCAD, OpenSCAD, Trimesh, Manifold3D, voxel/SDF workflows, hybrids, memory control, and automated acceptance tests.
license: MIT
compatibility: opencode and portable Agent Skills clients; optional Blender, OpenSCAD, FreeCAD, CadQuery, Trimesh, Manifold3D
metadata:
  audience: "3D-printing and computational-design agents"
  workflow: "organic mesh plus parametric functional geometry"
  primary-tools: "Blender, Trimesh, Manifold3D, CadQuery"
---

# Organic Mesh Functionalization

Use this skill when an existing model is primarily an organic triangle mesh—often generated from images—and must receive functional, measurable, repeatable geometry without losing its visible surface character.

## Core principle

Treat the project as two coupled representations:

1. **Organic source mesh:** visual exterior, ornament, sculpture, textile-like or anatomical form.
2. **Parametric functional geometry:** cutters, inserts, interfaces, cavities, stairs, flanges, hinges, closures, channels, soles, mounts, or test gauges.

Do not force the entire organic mesh into parametric CAD. Create precise functional geometry separately, register it to the mesh, combine them with an appropriate mesh or volume method, and verify the result quantitatively.

## Required first actions

1. Preserve the original file unchanged and record its checksum, units, bounds, vertex count, face count, connected components, watertightness, and volume.
2. Read or create a machine-readable specification using `assets/project-spec.template.yaml`.
3. Establish a named coordinate frame and at least three stable landmarks. Never infer semantic front/up solely from file axes.
4. Define:
   - **protected region:** surface that must remain unchanged;
   - **edit region / ROI:** where changes are permitted;
   - **interface region:** where organic and functional geometry meet;
   - **functional voids:** spaces that must remain empty;
   - **minimum walls, clearances, and overlap allowances**.
5. Choose the method using `references/method-selection.md` before changing geometry.
6. Build a low-resolution proxy for placement and iteration. Execute the final operation on the full-resolution source only after the plan passes proxy validation.

## Non-negotiable rules

- Never overwrite the source mesh.
- Never rely on visual inspection alone.
- Never apply a full-model remesh merely to fix a local Boolean unless loss of detail is explicitly accepted.
- Never scale an inner copy to create constant wall thickness; use an offset, Solidify, or SDF distance operation.
- Never place cutter faces exactly coplanar or tangent to target faces. Extend cutters through the target and use a documented epsilon.
- Never convert a multi-million-triangle mesh to B-Rep unless a small test proves the result remains tractable.
- Never run FEM directly on the decorative production mesh. Build a simplified analysis surrogate.
- Keep cutters and inserts as separate named artifacts even after the final mesh is exported.

## Default tool routing

| Input and task | Preferred route |
|---|---|
| Raw organic STL/OBJ/GLB, local cavity or opening | Blender Boolean Exact/Manifold, then Trimesh validation |
| Dirty, self-intersecting AI mesh | Blender voxel remesh or SDF/OpenVDB repair, preferably limited to ROI |
| Precise cutter, insert, staircase, hinge, flange, sole core | CadQuery, export STEP plus STL/3MF |
| Existing STEP/B-Rep or moderate repaired mesh | FreeCAD or CadQuery |
| Clean manifold mesh and simple primitive subtraction | OpenSCAD acceptable |
| Very complex hollowing, constant offset, graded cells | SDF/voxel/OpenVDB pipeline |
| High-volume automated mesh Booleans on valid solids | Manifold3D through Trimesh |

Read the matching tool reference before implementing:

- `references/tools/blender.md`
- `references/tools/cadquery.md`
- `references/tools/freecad.md`
- `references/tools/openscad.md`
- `references/hybrid-workflows.md`

## Generic workflow

### Phase 0 — Intake and baseline

Run:

```bash
python scripts/inspect_mesh.py source.stl --json reports/source.json
```

Record units explicitly. STL has no reliable unit metadata. If size is uncertain, compare known dimensions or request one real measurement.

Create a preview proxy. Preserve silhouette and the edit interface more accurately than distant ornament. Store the decimation settings in the project record.

### Phase 1 — Functional decomposition

Break the desired modification into separate solids:

- **removal cutters**: cavity, portal, top opening, textile removal volume;
- **preserved shell**: exterior skin or decorative band to retain;
- **replacement envelope**: volume removed and replaced;
- **functional inserts**: stairs, sole core, compartment liner, hinge blocks;
- **clearance cutters**: moving-part gaps, dice path clearance, glue gap;
- **test gauges**: coupons or interface-only test pieces.

Prefer one unioned cutter per Boolean stage rather than hundreds of sequential cuts.

### Phase 2 — Registration and fit

Use stable landmarks and cross-sections. Fit simple geometry only when the object genuinely resembles it:

- cylinder for towers, handles, limbs, bottles;
- box or rounded box for compartments and electronics;
- capsule for elongated organic cavities;
- loft through measured cross-sections for shoes and irregular tunnels;
- offset shell for uniform wall thickness;
- custom SDF for blended organic transitions.

Validate the fitted primitive against multiple sections, not only the bounding box. Read `references/alignment-and-fitting.md`.

### Phase 3 — Dry run on proxy

Generate separate preview files:

- source proxy;
- cutters;
- inserts;
- expected retained body;
- expected removed volume;
- combined preview.

Inspect orthographic views and section cuts through every critical interface. Do not continue if the cutter touches a protected wall or if the interface is narrower than the minimum printable wall plus registration uncertainty.

### Phase 4 — Execute with a fallback ladder

1. Direct Boolean on a valid manifold mesh.
2. Repair normals, tiny holes, duplicate faces, and separate components; retry.
3. Simplify or remesh only the ROI; retry.
4. Switch solver: Blender Exact/Manifold or Manifold3D.
5. Convert the operation to a narrow-band SDF/voxel operation.
6. Redesign the interface or split the model into printable assemblies.

Do not repeatedly apply random repair commands. Preserve reports from each attempt.

### Phase 5 — Add functional geometry

Keep exact parts parametric. Prefer mechanical retention plus adhesive over adhesive alone where possible. Add fillets at load-bearing transitions, but perform filleting in the CAD insert before mesh union when possible.

For moving parts, create separate bodies and explicit clearances. Never fuse a door or hinge pin into the main body unless a print-in-place joint is deliberately designed and tested.

### Phase 6 — Validation gates

Run both topology and change-preservation checks:

```bash
python scripts/inspect_mesh.py result.stl --json reports/result.json --require-watertight --max-components 1
python scripts/validate_edit.py source.stl result.stl \
  --roi assets/edit-roi.json \
  --max-outside-p95 0.20 \
  --max-outside-max 1.00 \
  --json reports/edit-validation.json
```

A result is not accepted until all applicable gates pass:

1. **Topology:** manifold/watertight target, consistent winding, expected component count, positive volume.
2. **Preservation:** surface outside ROI remains within tolerance.
3. **Functional geometry:** openings, cavity dimensions, clearances, wall thickness, path continuity, door motion, or sole interface meet specification.
4. **Manufacturing:** printable wall/detail size, overhangs, trapped supports, drainage, orientation, bed fit.
5. **Use-case test:** physical or simulation test appropriate to the part.

Read `references/validation.md`.

### Phase 7 — Package reproducibly

Deliver at minimum:

```text
source/                 original reference or checksum record
parameters/             YAML/JSON parameter files
cutters/                STEP/STL/3MF cutter solids
inserts/                STEP plus print mesh
result/                  final 3MF/STL and optional blend/FCStd
reports/                 baseline, validation, slicer, screenshots
scripts/                 exact commands used
README.md                coordinate frame, units, assembly and test notes
```

## Memory and performance policy

Before a dense voxel/SDF operation, run:

```bash
python scripts/estimate_voxel_memory.py --mesh source.stl --voxel 0.30 --buffers 6
```

If projected peak memory exceeds 60% of available RAM, change the plan. Prefer ROI cropping, sparse OpenVDB, a narrow-band field, float32/bool grids, chunking, or a larger voxel size. Read `references/memory-performance.md`.

## Case-specific routes

### Dice tower

Use the decorative shell only as the protected exterior. Fit a tower axis from several horizontal cross-sections. Create:

- an inner cylindrical or lofted cutter with explicit remaining wall thickness;
- top and bottom portal cutters extending fully through the shell;
- a separate parametric staircase or baffle insert;
- a dice clearance body representing the largest supported die plus margin.

Validate wall thickness around the full circumference, portal edge strength, uninterrupted dice path, overhang/support strategy, and a physical drop test. Use `examples/dice-tower/`.

### Barefoot shoe

Do not classify textile versus sole only by color or a single Z plane unless the input is known to support it. Identify the sole seam from geometry, materials, connected components, cross-sections, or manual landmarks. Choose one route:

- **complete replacement:** remove everything inside a replacement envelope and fit a new sole;
- **skin-preserving core replacement:** retain a thin decorative outsole/sidewall shell and replace its interior with a parametric sole core;
- **reference-only rebuild:** use the AI mesh only to derive outline and upper interface, then rebuild the sole entirely.

Validate toe-box shape, zero drop if required, sole thickness, flex zones, upper attachment flange, no hidden voids, and left/right symmetry policy. Use `examples/barefoot-shoe/`.

### Unicorn compartment

Create a rounded cavity or capsule that respects minimum wall thickness. Generate the door opening, compartment liner, door, lip, hinge/latch, and clearance cutters as separate parametric bodies. Prefer a seam aligned with natural belly contours. Validate door sweep, pin clearance, latch retention, choking hazards, wall thickness, and sharp edges. Use `examples/unicorn-compartment/`.

## Script usage

- `scripts/inspect_mesh.py`: baseline and final topology/geometry report.
- `scripts/validate_edit.py`: compare source and result outside the permitted ROI.
- `scripts/estimate_voxel_memory.py`: estimate dense field memory and suggested chunking.
- `scripts/blender_functionalize.py`: config-driven Blender headless Boolean pipeline.
- `scripts/cadquery_primitives.py`: generate precise cutters/inserts from JSON.
- `scripts/run_pipeline.sh`: example orchestration.

Run scripts with `--help`. Pin dependency versions in a project lockfile before production use.

## Failure reporting

When a step fails, report:

- exact tool and version;
- input mesh statistics;
- operation and solver;
- cutter overlap and epsilon;
- peak memory if known;
- error message;
- last valid artifact;
- which fallback was attempted;
- whether exterior detail loss occurred.

Never claim success merely because a preview renders.

## Deterministic validation handoff

Before release, load the sibling `validate-printable-3d-projects` skill and apply `assets/validation-profile.json`. Hash the original mesh, ROI/masks, cutters, insert/interface contracts, edited mesh, manufacturing mesh, slicer profile, G-code, and reports. Run mesh audits, seeded original-versus-edit comparisons, exact interface checks where available, motion sweeps, and G-code checks. Preserve high-resolution ROI/exterior-deviation reports as hash-bound external evidence; approximate fallbacks must return `REVIEW_REQUIRED`, not `PASS`. Any required `NOT_RUN`, stale report, or failed physical fit gate blocks release.

At project start, read the project autonomy policy before changing artifacts. Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger and only for stages assigned to the agent. Never write `HUMAN_APPROVED`; physical fit, appearance, safety, and commercial stages remain in the separate human ledger. Workflow autonomy does not authorize dependency installation, upload, or printer start.
