---
name: functional-3d-design
description: Design, generate, optimize, validate, test, and package parametric functional FDM/FFF parts using OpenSCAD, CadQuery, FreeCAD, Blender, purchased standard components, and evidence-backed print settings. Use for new parts, redesigns, assemblies, print-vs-buy decisions, material/nozzle selection, tolerances, snap-fits, gears, shelves, organizers, toys, print-time/material reduction, manufacturing-mesh simplification, and reusable parts-library work.
---

# Functional 3D design operating procedure

## Purpose

Create source-controlled, parameterized designs whose geometry, material, purchased components, print configuration, and verification evidence are traceable. Optimize for the user's objective rather than maximizing printed content by default. Keep the actual 3D model, its function, and its manufacturing readiness as the primary outcome; treat branding as a subordinate release constraint.

## Start every design with the mandatory preflight

Before requirements approval, concept generation, CAD/source creation, or
manufacturing export, invoke the sibling `3d-design-preflight` skill and read
`references/preflight-integration.md`. Document the current assessment at
`preflight/preflight-result.json`, validate it with the sibling validator, and
link it under `workflow.preflight` in `design-spec.yaml`.

If the work creates a new independently managed product, also read the sibling
preflight skill's `references/product-intake.md` and complete its SKU, correct
product-folder, portfolio CSV/XLSX, and license-chain intake before generating
design assets. A component, colorway, Step1X preform, or revision inside an
existing product keeps the owning SKU unless it will be independently offered,
versioned, supported, and retired.

For an existing design with no preflight, create a `RETROSPECTIVE` backfill from
the current recorded evidence before making the next design change. Do not
claim that it existed historically, and do not infer missing historical facts.
If a relevant scope, variant, requirement, interface, evidence, risk, process,
or test input changed, mark the linked assessment `stale` and update it before
continuing. A schema-valid `current` assessment is required, but its
`HOLD`/`CONCEPT_ONLY` decision and Lane D/E restrictions still control what work
may proceed.

## Start every design with an explicit contract

After the initial preflight decision permits the next step, create or update
`design-spec.yaml`. Capture, or clearly state assumptions for:

- function, dimensions, interfaces, target environment, load, speed, cycle count, and service life;
- risk class: `decorative`, `normal-functional`, `structural`, or `safety-critical`;
- fabrication preference: `integrated-print`, `balanced-hybrid`, or `standard-hardware`;
- printer/build volume, nozzle, material availability, enclosure, hardened nozzle, and drying capability;
- target formats and whether STEP, editable source, assembly, drawings, FEM, or organic mesh editing are required;
- acceptance criteria and test method.

If the user does not choose a fabrication preference, use `balanced-hybrid` and record the assumption. Do not hide uncertainty behind arbitrary dimensions.

## Requirements, concept, and final release authority

For every new design and every revision that changes function, geometry, interfaces, risk, manufacturing, or appearance, read `references/requirements-concept-approval.md` and enforce all three gates:

1. **Requirements approval** — synthesize the user's input directly into `design-spec.yaml`, then perform a concise structured requirements review. Distinguish `user-stated`, `inferred`, `recommended`, and `unresolved` items. Ask only consequential questions and include a recommended choice with its trade-off. When the current hash-bound autonomy policy assigns `requirements-normalization` to the agent, the agent may record the approval through the agent ledger after the contract and preflight pass; otherwise request explicit human approval or corrections. Do not generate a concept image, CAD geometry, source code, or manufacturing export before the assigned approval is recorded.
2. **Concept approval** — after requirements approval, record the approved specification revision and create a concept image that visualizes that revision. Show the views and functional details needed to judge the design; keep exact dimensions and requirements in the accompanying text because image labels are not authoritative. Map visible features back to the approved requirements. When the current hash-bound policy assigns `concept` to the agent, the agent may record approval through the agent ledger; otherwise request explicit human approval or corrections. Do not start production CAD or exports before the assigned approval is recorded.
3. **Final release approval** — after the production model is stable and verified, read `references/watermark-release-gate.md`, generate the canonical workspace `metriMade.com` watermark from the exact product ID and version, and insert it as the last planned design-feature/solid-geometry change. A previously validated derived-export tessellation/simplification policy may run afterward only with the mark and protected geometry locked and all affected checks repeated. Present the release candidate with the model result, function, validation, and deliverables first. Include watermark evidence as a compact secondary release note. Do not publish, package, or label manufacturing exports as final before this gate is approved; validation exports must be marked `DRAFT`.

Only a schema `1.1` autonomy policy created with `init-autonomy --preflight ...` is eligible for unattended Orca coordination. Its preflight hash and risk-derived autonomy ceiling are binding. Legacy `1.0` policies remain readable but require project-specific reauthorization before unattended work. Final watermark/release, physical printing, fit/function, appearance, safety, and commercial stages remain human-controlled.

Record all gate states under `workflow` in `design-spec.yaml`. If a correction changes an approved requirement, mark the preflight `stale` when it affects a preflight input, mark the requirements gate `changes-requested`, invalidate concept and watermark approval, update the assessment and specification, and repeat the affected gates. If feedback changes only the concept depiction, repeat concept and watermark approval. If feedback changes only watermark size or placement without changing the approved design, repeat only the watermark gate. Informational questions and requests that do not change the design do not reopen the gates.

When maintaining a task list, include exactly one subordinate watermark item near the end, after model design and primary verification. Do not split watermark selection, placement, previews, and approval into the dominant task structure unless the watermark is blocking release.

## Mandatory deliverables

A completed design should contain, as applicable:

1. for a new product, one stable SKU shared by its correct product folder,
   portfolio CSV/XLSX row, design/preflight records, and initialized
   product-local license chain;
2. a schema-valid current `preflight/preflight-result.json` linked from `design-spec.yaml`;
3. `design-spec.yaml` and a decision log;
4. a printed/purchased/hybrid decomposition and BOM;
5. parameterized source code;
6. native or neutral CAD output, preferably STEP for precise functional geometry;
7. 3MF or STL for manufacturing;
8. geometry validation report;
9. print profile and orientation rationale;
10. print-time/material optimization baseline, candidate comparison, and selected or no-change decision;
11. manufacturing-mesh complexity/simplification report for every mesh deliverable;
12. explicit triangle, peak-memory, mesh-file, and exact-slicer budgets for dense/relief jobs, with separate master and manufacturing mesh artifacts;
13. simulation or calculation report when it changes a decision;
14. coupon and physical-test plan;
15. `metriMade.com` watermark generation, product-ID/version identity match, placement, validation, physical coupon, and approval evidence;
16. evidence and version metadata for parts-library promotion;
17. a final model result report that inventories the delivered files and summarizes the actual 3D model.

A render is not proof of function. A slicable mesh is not proof of strength.

## Mandatory final model result report

Read `references/final-model-result-report.md` before completing any design task. Always end the user-facing design process with a report about the actual 3D model and delivered package, even when the result is still draft or blocked. Lead with the design outcome, then cover key geometry and functions, validation evidence, print readiness, deliverables, and remaining limitations. Put the watermark in a late, compact **Kennzeichnung** note of one bullet or at most two short lines when it passes, then close on the model's readiness or next useful action. Expand the mark only when it blocks release or the user explicitly asks about it. Never make watermark status the headline, opening result, final sentence, or dominant conclusion of a successful design handoff.

## Tool routing

Use `scripts/select_tool.py` and read `references/tool-selection.md` when the route is not obvious. Apply `references/cad-coding-standard.md` to generated source and read `references/organic-mesh-workflow.md` for existing organic meshes.

- **CadQuery**: default for dimensional functional parts, B-Rep/STEP, fillets, holes, interfaces, and assemblies.
- **OpenSCAD**: simple CSG, 2D profiles, repeating patterns, text/relief, compact parameters, and reliable CLI generation.
- **FreeCAD**: interactive STEP editing, drawings, assemblies, FEM/CalculiX, and human-in-the-loop refinement.
- **Blender**: organic meshes, scans, sculpting, remesh, visual texture/relief, mesh repair, and presentation.
- **Hybrid**: use precise CAD for interfaces and Blender/SDF/mesh tools for organic or high-density surface fields.
- **Step1X image-to-3D**: after concept approval and interface/decomposition freeze, load `step1x-image-to-3d` for a whole appearance-led draft, bounded organic component, or sacrificial preform. Keep exact interfaces and manufacturing authority in this skill's CAD/validation route.

Do not convert a dense organic STL into a face-per-triangle B-Rep unless there is a demonstrated need. Do not model thousands of decorative cells as individual B-Rep booleans when an implicit, mesh, or texture route is more stable.

## Print-time, material, and mesh efficiency

Use the separate `optimize-fdm-design` skill whenever a functional or hybrid model has meaningful opportunities to reduce print time, material, support, or toolpath burden while preserving stability and other requirements. It supplies the shell/rib/window/gusset patterns, application-family guidance, fluid-system extensions, exact-slicer experiment design, and Pareto comparison workflow. For a user request that is analysis-only, measure and propose candidates without editing the design.

Every manufacturing model must pass an efficiency and mesh-complexity decision even when no change is applied:

- establish an exact slicer baseline and protect fits, load paths, sealing/wetted walls, bed faces, appearance/relief, and stability mass;
- compare process-only, geometry-only, and combined candidates when optimization is material to the objective;
- read `references/mesh-simplification.md`, inspect triangle/file/slicer burden, and record `applied`, `not-beneficial`, or `not-applicable` per manufacturing mesh;
- use a physical surface-error tolerance and protected regions rather than a triangle percentage alone;
- preserve native/high-fidelity source and accept a simplified mesh only after independent topology, geometry, interface, bed-contact, cosmetic/relief, and exact-slicer comparison;
- keep the unsimplified `master_mesh` and selected `manufacturing_mesh` at separate immutable paths;
- for dense/relief work, record triangle target/stop, peak-memory GiB, mesh MiB, and exact-slicer seconds before generation;
- keep the geometric comparison report separate from `slicer_resolution_check`; neither report substitutes for the other;
- rerun every affected engineering/coupon check after a geometry or process optimization.

Optimization is not mandatory for its own sake. The check and evidence are mandatory; a lossy transformation with no measured benefit is prohibited.

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

1. **3D design preflight** — for a new product, first allocate its unique SKU, correct product folder, portfolio CSV/XLSX record, and license-chain workspace; then invoke `3d-design-preflight`, create or backfill the canonical result, validate it, and obey its gates and lane.
2. **Requirements and risk review** — create the measurable specification, expose assumptions and recommendations, obtain the approval assigned by the current hash-bound autonomy policy, and update the preflight if the approved revision changes an assessed input.
3. **Concept visualization** — visualize the approved specification, check requirement-to-feature correspondence, and obtain the human or agent-ledger approval assigned by the current policy.
4. **Functional decomposition** — printed parts, purchased parts, interfaces, assembly order, maintenance.
5. **Tool route** — choose the simplest representation that preserves required editability and precision.
6. **Calibration check** — identify missing printer/material data and generate coupons first where needed.
7. **Parametric source** — named parameters, units in millimetres, assertions, deterministic exports.
8. **Geometry checks** — dimensions, body count, manifold/watertight state, normals, wall/feature rules, collisions.
9. **Manufacturing baseline** — orientation, support access, bridging, overhangs, seams, bed fit, material/support volume, mesh burden, and an exact-profile slicer dry run. For Anycubic printers, route the dry run through the sibling validation skill's `slice-anycubic-next` command (or this skill's `slicer_preflight.py --slicer AnycubicSlicerNext`) so source/profile/output hashes and native slicer status are retained.
10. **Engineering characterization** — hand calculations, kinematics, contact, FEM, thermal/flow analysis only at useful fidelity; establish the baseline constraints that optimization may not violate.
11. **Efficiency and mesh-simplification gate** — invoke `optimize-fdm-design` where applicable; compare process/geometry candidates; inspect every manufacturing mesh using `references/mesh-simplification.md`; set dense-job resource budgets; preserve separate master/manufacturing artifacts; run the geometric gate; then run the independent slicer-resolution gate. Select and validate an export policy or record `not-beneficial`/`not-applicable`. Rerun affected geometry, manufacturing, and engineering checks on the selected candidate.
12. **Selected model candidate verification** — gather coupon, interface, subassembly, prototype, or field evidence for the selected optimized or unchanged production geometry, then update the preflight readiness/evidence if the results change it.
13. **Watermark integration** — as the last planned design-feature/solid-geometry change, generate all exact `MM-WM-001-R2` tiers for the current product ID and version. Use the selector to choose Full, then Compact, then Micro at 0°/90° and scale 1.0. Full and Compact show `metriMade.com`; Micro may omit the domain only when the larger tiers do not fit. Subtract the selected tier at the approved depth and verify identity match, host-wall reserve, tier justification, and finished-underside reading direction.
14. **Final derived mesh export and release regression checks** — apply only the prevalidated tessellation/simplification policy, with protected interfaces, bed datum, and watermark locked; rerun affected mesh, surface-error, wall, bed-contact, mark-readability, and exact-slicer checks.
15. **Final release approval and packaging** — present the model-centered candidate and its deliverables first, include the watermark as a compact release note, obtain explicit approval, then run `scripts/validate_design_spec.py design-spec.yaml --require-current-preflight --require-final-approval` before final packaging.
16. **Revision and learning** — invoke the sibling `3d-skill-maintainer`; preserve the trace, store measured results and failures with exact process scope, turn actionable user corrections into eval candidates, and promote only reviewed evidence-backed explanations.
17. **Final model result report** — finish with the actual model outcome, validation status, print guidance, complete deliverable links, open limitations, one compact marking note, and the next model-focused action or readiness statement.

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

Read `references/self-learning.md`. Use `scripts/parts_library.py` and
`scripts/record_test_result.py` for product-local part qualification. Use the
sibling `3d-skill-maintainer` for repository-wide lesson candidates, design
patterns, evals, conflict checks, and just-in-time retrieval from
`libraries/3d-learning/`.

Statuses are:

- `concept`: unbuilt idea;
- `experimental`: geometry generated or printed, not sufficiently tested;
- `qualified-local`: passed defined tests on a recorded local process;
- `deprecated`: superseded or failed.

Never promote from `experimental` to `qualified-local` without geometry validation, a linked test record, and the printer/material/nozzle/profile identity. A locally qualified part is not universally certified.

Every meaningful user correction must create or link a targeted eval in the same
design phase. A new success or failure starts as a scoped E0 candidate; it must
not directly rewrite this skill, a material reference, or a validated pattern.

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

A missing, unreadable, mirrored, protruding, structurally unsafe, identity-mismatched, physically unqualified, or unapproved metriMade watermark is a release blocker. Never omit the owned logo, product ID, or version; never scale a generated tier down or type/edit identity text independently. The domain may be absent only on the generator-produced R2 Micro tier after the selector records that Full and Compact do not fit.

## Deterministic validation handoff

Use the sibling `validate-printable-3d-projects` skill as the final release orchestrator and apply `assets/validation-profile.json`. Register the current preflight result, source, parameters, dependencies, mesh/3MF, slicer profile, G-code, interface contracts, coupons, and reports with hashes in `validation-project.json`. Run the preflight validator, mesh audits, exact interface checks, motion and parameter sweeps, G-code/3MF checks, report-freshness checks, and named approvals. Existing calculators and validators are component checks, not release proof. A missing, stale, invalid, or release-blocking preflight; required `NOT_RUN` or `REVIEW_REQUIRED`; stale evidence; missing watermark approval; or a failed physical gate blocks release.

For Anycubic Slicer Next specifics, read the dedicated Anycubic reference in the sibling validation skill. Its CLI adapter is the authoritative automated path; final GUI preview remains required for layers, supports, seams, and multicolor tool/purge interpretation.

At project start, read the project autonomy policy before changing artifacts. For unattended Orca work, require schema `1.1`, a matching preflight hash, and a policy mode no more permissive than its recorded autonomy ceiling. Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger and only for stages assigned to the agent. Never write `HUMAN_APPROVED`; physical, safety, appearance, watermark, and commercial stages remain in the separate human ledger. Workflow autonomy does not authorize dependency installation, upload, or printer start.
