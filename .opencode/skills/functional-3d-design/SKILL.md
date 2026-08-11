---
name: functional-3d-design
description: Design, generate, validate, test, and package parametric functional FDM/FFF parts using OpenSCAD, CadQuery, FreeCAD, Blender, purchased standard components, and evidence-backed print settings. Use for new parts, redesigns, assemblies, print-vs-buy decisions, material/nozzle selection, tolerances, snap-fits, gears, shelves, organizers, toys, and reusable parts-library work.
---

# Functional 3D design operating procedure

## Purpose

Create source-controlled, parameterized designs whose geometry, material, purchased components, print configuration, and verification evidence are traceable. Optimize for the user's objective rather than maximizing printed content by default.

## Start every design with an explicit contract

Create or update `design-spec.yaml`. Capture, or clearly state assumptions for:

- function, dimensions, interfaces, target environment, load, speed, cycle count, and service life;
- risk class: `decorative`, `normal-functional`, `structural`, or `safety-critical`;
- fabrication preference: `integrated-print`, `balanced-hybrid`, or `standard-hardware`;
- printer/build volume, nozzle, material availability, enclosure, hardened nozzle, and drying capability;
- target formats and whether STEP, editable source, assembly, drawings, FEM, or organic mesh editing are required;
- acceptance criteria and test method.

If the user does not choose a fabrication preference, use `balanced-hybrid` and record the assumption. Do not hide uncertainty behind arbitrary dimensions.

## Mandatory requirements, concept, and watermark approvals

For every new design and every revision that changes function, geometry, interfaces, risk, manufacturing, or appearance, read `references/requirements-concept-approval.md` and enforce all three gates:

1. **Requirements approval** — synthesize the user's input directly into `design-spec.yaml`, then present a concise structured requirements review. Distinguish `user-stated`, `inferred`, `recommended`, and `unresolved` items. Ask only consequential questions and include a recommended choice with its trade-off. Request explicit approval or corrections. Do not generate a concept image, CAD geometry, source code, or manufacturing export before approval.
2. **Concept approval** — after requirements approval, record the approved specification revision and create a concept image that visualizes that revision. Show the views and functional details needed to judge the design; keep exact dimensions and requirements in the accompanying text because image labels are not authoritative. Map visible features back to the approved requirements and request explicit approval or corrections. Do not start production CAD or exports before approval.
3. **Final watermark approval** — after production geometry is stable, read `references/watermark-release-gate.md`, insert the bundled JuSt Innovation watermark into the actual model, and rerun affected geometry and manufacturing checks. Show a dimensioned underside view, a local section, and a slicer/layer preview before requesting explicit final approval. Do not publish, package, or label manufacturing exports as final before this gate is approved; validation exports must be marked `DRAFT`.

Record all gate states under `workflow` in `design-spec.yaml`. If a correction changes an approved requirement, mark the requirements gate `changes-requested`, invalidate concept and watermark approval, update the specification, and repeat the affected gates. If feedback changes only the concept depiction, repeat concept and watermark approval. If feedback changes only watermark size or placement without changing the approved design, repeat only the watermark gate. Informational questions and requests that do not change the design do not reopen the gates.

## Mandatory deliverables

A completed design should contain, as applicable:

1. `design-spec.yaml` and a decision log;
2. a printed/purchased/hybrid decomposition and BOM;
3. parameterized source code;
4. native or neutral CAD output, preferably STEP for precise functional geometry;
5. 3MF or STL for manufacturing;
6. geometry validation report;
7. print profile and orientation rationale;
8. simulation or calculation report when it changes a decision;
9. coupon and physical-test plan;
10. JuSt Innovation watermark placement, sizing, validation, and approval evidence;
11. evidence and version metadata for parts-library promotion.

A render is not proof of function. A slicable mesh is not proof of strength.

## Tool routing

Use `scripts/select_tool.py` and read `references/tool-selection.md` when the route is not obvious. Apply `references/cad-coding-standard.md` to generated source and read `references/organic-mesh-workflow.md` for existing organic meshes.

- **CadQuery**: default for dimensional functional parts, B-Rep/STEP, fillets, holes, interfaces, and assemblies.
- **OpenSCAD**: simple CSG, 2D profiles, repeating patterns, text/relief, compact parameters, and reliable CLI generation.
- **FreeCAD**: interactive STEP editing, drawings, assemblies, FEM/CalculiX, and human-in-the-loop refinement.
- **Blender**: organic meshes, scans, sculpting, remesh, visual texture/relief, mesh repair, and presentation.
- **Hybrid**: use precise CAD for interfaces and Blender/SDF/mesh tools for organic or high-density surface fields.

Do not convert a dense organic STL into a face-per-triangle B-Rep unless there is a demonstrated need. Do not model thousands of decorative cells as individual B-Rep booleans when an implicit, mesh, or texture route is more stable.

## Print-vs-buy and part consolidation

Read `references/print-vs-buy.md` and run `scripts/print_vs_buy.py` for ambiguous components.

- Printing is favored for custom shape, housings, adapters, ducts, low-speed large gears, compliant features, cable routing, integrated spacers, and low-volume personalization.
- Purchased parts are favored for precision, wear, fatigue, sealing, electrical contact, certified anchoring, high speed, or high stored energy.
- Favor integrated printing when it reduces assembly without creating inaccessible supports, impossible maintenance, poor orientation, or a single expensive failure point.
- Typical hybrid choices are printed body plus metal screws/inserts, steel shafts, bearings, springs, O-rings, magnets, belts, and wall anchors.

Never invent a safe load rating for a purchased or printed part without test evidence and the actual installation conditions.

## Materials and print configuration

Read `references/materials.md` and `references/nozzles-layers-slicer.md`. Use:

```bash
python scripts/select_material.py --help
python scripts/recommend_print_profile.py --help
```

Rules:

- Treat PLA+ / Tough PLA and branded blends as supplier-specific, not a standardized material class.
- Use the exact filament manufacturer's profile and datasheet as the authority for temperature, drying, enclosure, abrasion, and service limits.
- Use a hardened or otherwise abrasion-resistant nozzle for abrasive carbon, glass, glow, metal, and many mineral-filled filaments.
- Keep default layer height below 75% of nozzle diameter; only approach 80% after flow and bonding validation.
- Prefer walls/perimeters and load-oriented geometry before simply increasing infill.
- Respect maximum volumetric flow; a larger nozzle does not guarantee faster printing if the hotend cannot melt the requested flow.
- Calibrate dimensional compensation, holes, bridges, supports, and fit on the exact printer/material/nozzle combination.

Use 0.4 mm for balanced detail, 0.6 mm as the default functional/filled-filament option, and 0.8 mm for large coarse structural parts unless the acceptance criteria require otherwise.

## Mechanical features

Read `references/mechanical-features.md` and `references/design-patterns.md` before creating threads, snap-fits, flexures, hinges, gears, shafts, bearings, or seals.

- Prefer heat-set inserts, captive nuts, or through-bolts for repeated fastener cycles.
- Prefer a purchased metal pin or screw as a hinge axis for durable hinges.
- Use printed snap-fits and flexures only with an explicit material, orientation, strain calculation, cycle target, root radius, and coupon.
- Generate involute gears with a library; do not approximate teeth by eye.
- Buy high-speed/high-load gears, precision shafts, rolling bearings, belts, springs, and O-rings unless the design explicitly justifies a printed alternative.

The supplied calculators are preliminary design aids, not certification tools.

## Design and validation flow

Follow this order:

1. **Requirements and risk review** — create the measurable specification, expose assumptions and recommendations, and obtain explicit requirements approval.
2. **Concept visualization** — visualize the approved specification, check requirement-to-feature correspondence, and obtain explicit concept approval.
3. **Functional decomposition** — printed parts, purchased parts, interfaces, assembly order, maintenance.
4. **Tool route** — choose the simplest representation that preserves required editability and precision.
5. **Calibration check** — identify missing printer/material data and generate coupons first where needed.
6. **Parametric source** — named parameters, units in millimetres, assertions, deterministic exports.
7. **Geometry checks** — dimensions, body count, manifold/watertight state, normals, wall/feature rules, collisions.
8. **Manufacturing checks** — orientation, support access, bridging, overhangs, seams, bed fit, material volume, slicer dry run.
9. **Engineering checks** — hand calculations, kinematics, contact, FEM, thermal/flow analysis only at useful fidelity.
10. **Watermark integration** — select the standard or compact JuSt Innovation profile for the largest safe print-bed-facing underside region, subtract it at the approved depth, and verify host-wall reserve and finished-underside reading direction.
11. **Candidate verification** — rerun geometry/manufacturing checks on the watermarked body and gather coupon, interface, subassembly, prototype, or field evidence as appropriate.
12. **Final release approval** — present the actual watermarked candidate and evidence, obtain explicit approval, then run `scripts/validate_design_spec.py design-spec.yaml --require-final-approval` before final packaging.
13. **Revision and learning** — store measured results, failure mode, printer/material/profile hash, and promote only evidenced designs.

Read `references/validation-testing.md` and `references/simulation-model-fidelity.md` for the verification ladder and appropriate analysis fidelity.

## Subagent strategy

Read `references/automation-architecture.md` for role boundaries, child-session contracts, MCP permissions, and CI design.


Use fast subagents for bounded, independently checkable work:

- extracting dimensions and interfaces;
- searching an existing parts library;
- tool/material/nozzle classification;
- running a calculator or parameter sweep;
- summarizing a validation report;
- checking upstream documentation;
- making a small targeted source edit with an explicit test.

Use a frontier/capable agent for architecture, ambiguous loading, cross-tool geometry, failure analysis, safety review, and final acceptance. Do not ask a small agent to silently make the final engineering decision.

The included `cad-microtask` subagent inherits the current model. An optional configuration pins `openai/gpt-5.3-codex-spark`; use it only when available through the configured provider. Spark is appropriate for short, targeted edits and calculations, not the complete long-horizon design loop.

## External libraries and skills

Before creating a standard part from scratch, consult `references/parts-and-libraries.md` and `references/external-integrations.md`.

Preferred sources include:

- `cq_warehouse` / `bd_warehouse` for standard hardware and interfaces;
- `cq_gears`, BOSL2, or FreeCAD Gears for gears;
- NopSCADlib for OpenSCAD "vitamins";
- step.parts for off-the-shelf STEP geometry;
- CadQuery LLM skill and CadQuery MCP for B-Rep generation/rendering;
- FreeCAD and Blender MCPs only with reviewed permissions.

Record source, version/commit, license, supplier part number, and whether geometry is reference-only or manufacturing-authoritative.

## Self-learning and local parts library

Read `references/self-learning.md`. Use `scripts/parts_library.py` and `scripts/record_test_result.py`.

Statuses are:

- `concept`: unbuilt idea;
- `experimental`: geometry generated or printed, not sufficiently tested;
- `qualified-local`: passed defined tests on a recorded local process;
- `deprecated`: superseded or failed.

Never promote from `experimental` to `qualified-local` without geometry validation, a linked test record, and the printer/material/nozzle/profile identity. A locally qualified part is not universally certified.

## Recommended extensions

Read `references/recommended-extensions.md` when adapting the package to a real printer fleet. Prioritize a process-specific calibration registry, slicer adapter, geometric regression checks, material test database, and evidence-backed standard-interface catalog.

## Safety and stopping rules

Stop and request human engineering review before claiming readiness for:

- life support, medical treatment, pressure vessels, mains electricity, fire protection, lifting, climbing, vehicle control, weapons, or child-safety certification;
- structural wall loads without wall/anchor verification;
- food-contact or biocompatibility claims based only on filament marketing;
- high-temperature or chemical exposure without the exact material data;
- autonomous printer upload/start.

Preserve the editable source and report failed checks honestly. Prefer a small test coupon over speculative simulation when material/process uncertainty dominates.

A missing, unreadable, mirrored, protruding, structurally unsafe, or unapproved JuSt Innovation watermark is a release blocker. Never silently omit it or substitute a typed brand name for the bundled production outlines.
