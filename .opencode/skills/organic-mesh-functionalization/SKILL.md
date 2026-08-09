---
name: organic-mesh-functionalization
description: Add, replace, align, and validate parametric functional geometry inside high-resolution organic STL/OBJ/3MF/GLB meshes while preserving protected decorative surfaces. Use for AI-generated or scanned meshes that need cavities, openings, stairs, doors, compartments, soles, mounting interfaces, inserts, or other printable functional features using Blender, OpenSCAD, CadQuery, FreeCAD, Trimesh, Manifold, voxel/SDF methods, or hybrid workflows.
license: MIT
compatibility: opencode
metadata:
  domain: mesh-cad-hybrid-dfam
  manufacturing: fdm-fff-resin-optional
  inputs: stl-obj-3mf-glb-ply-scan-ai-mesh
  outputs: editable-functional-source-step-stl-3mf-validation-report
  version: 1.0.0
  complements: functional-3d-design
---

# Organic mesh functionalization operating procedure

## Purpose

Turn an existing dense, non-parametric organic mesh into a functional 3D-printable design without treating its decorative surface as disposable. Preserve the source mesh, define where change is allowed, generate the functional geometry parametrically, combine the representations with the least destructive method, and prove that the result satisfies both geometric and functional acceptance criteria.

This skill is standalone. When `functional-3d-design` is also installed, load it for material, fastener, print-vs-buy, slicer, mechanical-feature, and physical-test decisions.

## Never edit the only copy

Create these artifacts before changing geometry:

- immutable source mesh and hash;
- `operation-plan.yaml` with units, coordinate system, intended change, protected region, transition band, and acceptance tests;
- low-resolution proxy mesh when the source is too dense for interactive work;
- transform/landmark file that records scale, origin, axes, and alignment;
- baseline mesh report.

Do not silently apply automatic repair, remesh, decimation, smoothing, or unit scaling to the archival source. Every destructive preprocessing step must produce a new file and a before/after report.

## Model the intervention, not only the final shape

Every modification must define four zones:

1. **Functional region of interest (ROI)** — material may be removed, replaced, or added.
2. **Protected region** — visible surface or critical interface that must remain within a stated deviation.
3. **Transition band** — controlled overlap where blending, flange, fillet, sealing land, or sacrificial cleanup is allowed.
4. **Keep-out region** — thin details, limbs, texture, existing cavities, moving clearances, or safety-sensitive geometry that cutters and inserts must not enter.

Prefer a local operation over a whole-model remesh. The default protected-surface tolerance for a decorative FDM model is not universal: derive it from nozzle, layer height, visible texture scale, and the user's acceptance criteria.

## Required workflow

1. **Triage input** — inspect units, bounds, face count, body count, watertightness, winding, duplicate/degenerate faces, holes, self-intersection risk, and whether the mesh represents a surface or a solid.
2. **Establish coordinates** — define landmarks, main axes, datum planes, and handedness. Apply object scale before dimensioning cutters.
3. **Choose preservation strategy** — exact mesh Boolean, local remesh, shell patch, split-and-replace, separate assembly, or conformal interface.
4. **Create parametric functional geometry** — use OpenSCAD/CadQuery/FreeCAD/Blender Python according to representation needs. Keep parameters and export tolerances explicit.
5. **Fit and align** — use datums first, landmarks second, PCA/ICP only as an aid. Record the final 4×4 transform.
6. **Preflight the Boolean** — valid closed operands, real volumetric overlap, non-coplanar intersections, cutter overshoot, positive volume, and sufficient residual wall.
7. **Execute on a copy** — preserve the source, cutter, insert, intermediate fragments, and logs.
8. **Validate topology and intent** — watertightness, components, open boundaries, volume, sections, protected-surface deviation, overcut/undercut, collisions, trapped bodies, and assembly clearances.
9. **Validate printing and function** — orientation, support access, wall/feature size, drainage, material, interface coupon, and physical functional test.
10. **Package evidence** — source mesh hash, parameters, transformations, functional CAD source/STEP, final 3MF/STL, reports, previews, slicer profile, and decision log.

## Tool routing

Read `references/tool-selection.md` and use `scripts/route_operation.py` when uncertain.

- **Blender** is the default host for dense organic meshes, segmentation, local sculpt/remesh, visual inspection, Shrinkwrap, and mesh Booleans.
- **CadQuery** is the default generator for precise parametrically defined inserts, stairs, doors, flanges, mounts, hinge features, and STEP masters. Do not force a dense STL through face-per-triangle B-Rep conversion.
- **OpenSCAD** is suitable when the source mesh is already clean and the functional operation is simple CSG with primitive or 2D-extruded cutters. It is not the repair stage.
- **FreeCAD** is useful for interactive assembly, STEP-based functional parts, Mesh Workbench inspection/repair, measured placement, drawings, and FEM. Avoid converting a multi-million-triangle mesh to a Part shape unless a tested reduction strategy makes it practical.
- **Trimesh + Manifold3D** is preferred for deterministic headless inspection and robust Boolean operations on already valid closed meshes.
- **Voxel/SDF** methods are preferred for badly intersecting organic topology, uniform offsets, complex hollowing, or highly blended replacement boundaries; localize them to the ROI whenever possible.
- **Hybrid** is the normal answer: parametric B-Rep source for functional components, tessellated only at the handoff, then mesh integration and validation.

## Preservation strategy selection

Use the least destructive option that meets the requirement:

- **Separate insert/assembly**: best when serviceability, different material, replacement, or Boolean risk matters.
- **Subtractive cavity plus insert**: robust for electronics, compartments, stair cores, mounting pockets, and replaceable soles.
- **Window/patch replacement**: cut a controlled opening, retain a rim, and attach a parametric door or patch.
- **Split-and-rebuild**: remove everything on one side of a datum or fitted surface, retain a transition band, and replace that region.
- **Conformal shell/interface**: derive a fitted surface from the organic mesh, offset it, then add a flange, gasket land, or bonded interface.
- **Direct union**: only when both meshes are valid, overlap is intentional, and the seam can be verified.
- **Local voxel fusion**: use when exact surface intersections remain unstable; protect fine decoration outside the local volume.

Read `references/replacement-patterns.md` before choosing a primitive. A cylinder is appropriate only when the preserved shell has enough radial clearance everywhere. Use a capsule, rounded box, loft, spline extrusion, fitted offset surface, convex envelope, or compound cutter when it better matches the available volume and stress/print constraints.

## Boolean rules

Read `references/boolean-best-practices.md`.

- Both operands should be closed, consistently oriented positive volumes for a solid Boolean.
- Never rely on surfaces that merely touch. Add a documented overshoot/overlap epsilon appropriate to model scale.
- Avoid long coplanar coincident faces; move or extend the cutter so intersections cross cleanly.
- Keep cutters simpler and lower-resolution than the preserved mesh unless detail is functionally required.
- Use one logical operation at a time and validate each intermediate result.
- Prefer a union of cutters followed by one subtraction over hundreds of serial cuts, but preserve individual diagnostic cutters.
- When a Boolean fails, do not increase tolerances blindly. Inspect operand validity, overlap, scale, local triangle quality, duplicate/internal shells, and near-zero residual walls.
- A successful Boolean return is not proof that the intended region was changed and only that region.

## Alignment and fitting

Read `references/alignment-and-fitting.md`.

Use this priority:

1. known units and explicit dimensions;
2. datum plane/axis and measured landmarks;
3. cross-section fitting or primitive fit in a selected ROI;
4. coarse PCA alignment;
5. landmark Kabsch transform;
6. ICP only for final local refinement when the surfaces truly correspond.

Record transforms. Do not use global object scaling as a substitute for a uniform wall offset. Do not infer a shoe's internal fit only from its decorative external shell.

## Validation contract

At minimum, validate:

- final mesh loads and contains expected bodies;
- watertightness/solid state when a closed print is required;
- winding and positive volume;
- no unexpected disconnected fragments;
- intended openings are open and unintended holes are absent;
- protected source surface remains within allowed deviation outside the ROI/transition band;
- the cut reaches the intended target but not keep-out geometry;
- residual walls and interface lands meet declared minima;
- functional parts have clearances and no collisions in every required state;
- cross-sections show no hidden slivers, internal membranes, duplicate shells, or blocked passages;
- output fits the build volume and slicer preview matches intended cavities/openings.

Use:

```bash
python scripts/inspect_mesh.py input.stl --json-out baseline.json
python scripts/estimate_memory.py --mesh input.stl --voxel-mm 0.4
python scripts/validate_edit.py source.stl result.stl --plan operation-plan.yaml --json-out edit-report.json
python scripts/section_report.py result.stl --axis z --positions 20 40 60 --json-out sections.json
```

The supplied protected-surface comparison is a sampling-based geometric check, not a proof of exact surface identity. For critical work, combine it with visual overlays and tool-specific diagnostics.

## High-resolution and memory policy

Read `references/memory-and-performance.md` before voxelizing or loading multiple copies.

- Make a proxy for alignment and planning; retain the full-resolution source for final local operations.
- Crop to the ROI plus transition margin before voxel/SDF work.
- Use `float32` scalar fields and broadcasting/chunked slabs rather than full `float64` meshgrids.
- Estimate memory before allocation. Dense voxel memory grows cubically as voxel size shrinks.
- Preserve a non-remeshed exterior whenever possible. Voxel Remesh reconstructs the surface and can erase fine decoration.
- Decimation is allowed for proxies and may be allowed in hidden regions; quantify deviation before using it on visible surfaces.
- Do not keep every cached normal, proximity tree, voxel field, and duplicate mesh alive simultaneously in long-running agents.

## Example-specific routing

### Decorative dice tower shell

- Fit/declare a tower axis and conservative inner radius from multiple cross-sections.
- Subtract an interior cylinder or tapered loft that leaves the minimum wall at every sampled height.
- Create roof entry and courtyard exit as separate overshooting cutters.
- Generate staircase/baffles parametrically in CadQuery/OpenSCAD/Blender Python; prefer a separate insert during prototyping.
- Validate clear dice path, no internal membranes, wall thickness, entry/exit dimensions, and repeated drop tests.

### AI-generated barefoot shoe shell

- Treat textile-looking geometry and sole as segmentation targets, not materials inferred from appearance alone.
- Define a fitted sole-interface surface or transition band; a single horizontal cut is valid only when the interface is truly planar.
- Remove the upper and old sole interior while retaining a controlled outsole/rand if desired.
- Generate the new parametric sole separately, then bond, mechanically retain, or mesh-union it with deliberate overlap.
- Validate foot volume, zero-drop intent, flex zones, attachment edge, symmetry/handedness, and printable wall/textile replacement strategy.

### Toy unicorn compartment

- Choose a low-curvature belly region with sufficient wall thickness and distance from legs/details.
- Use a capsule/rounded-box compartment, not a sharp box that creates thin corner walls.
- Cut a window with a retained seating rim; generate a separate door with hinge/latch/clearance or a captive snap fit.
- Validate door sweep, pinch/edge risks, retained wall, loose fragments, and child-use requirements separately from geometry.

Detailed plans are in `examples/` and `references/example-workflows.md`.

## Evidence-driven self-learning

Read `references/self-learning.md`. Record operation parameters, tool versions, validation results, slicer evidence, and physical outcomes. Promote a reusable intervention pattern only after deterministic checks and relevant physical tests pass. Failed Booleans and protected-surface breaches are valuable regression cases; do not "learn" by silently relaxing tolerances.

## Subagents and external skills

Use a fast coding/research subagent for bounded tasks such as mesh-report interpretation, formula checks, OpenSCAD syntax fixes, transform calculations, source lookup, and test generation. Keep architecture, destructive operations, acceptance criteria, and final review in the primary agent. A model such as GPT-5.3 Codex Spark can be configured in the included microtask agent example; never delegate an unbounded high-resolution Boolean job without memory and output limits.

Load external skills or MCPs only when they add an actual capability: Blender control, FreeCAD/CadQuery execution, OpenSCAD rendering, slicer CLI, or parts libraries. Pin versions and treat arbitrary code execution as privileged. Read `references/external-integrations.md`.

## Stop conditions

Stop and redesign the method when:

- the source cannot be interpreted as a valid volume and the intended inside/outside is ambiguous;
- the requested residual wall is smaller than both mesh uncertainty and practical print resolution;
- segmentation cannot distinguish the part to remove from protected decoration;
- Boolean results vary materially with tiny epsilon changes;
- the operation requires global remesh but the user requires preservation of sub-voxel detail;
- alignment lacks enough independent constraints;
- a functional/safety requirement cannot be tested with the available model and evidence.

Do not hide these limits. Offer a separate insert, larger transition band, local manual segmentation, higher-quality source, scan landmarks, or a redesigned interface.
