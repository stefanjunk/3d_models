---
name: functional-3d-design
description: Design, generate, optimize, validate, test, and package parametric functional FDM/FFF parts using OpenSCAD, CadQuery, FreeCAD, Blender, purchased standard components, and evidence-backed print settings. Use for new parts, redesigns, assemblies, print-vs-buy decisions, material/nozzle selection, tolerances, snap-fits, gears, shelves, organizers, toys, print-time/material reduction, manufacturing-mesh simplification, and reusable parts-library work.
---

# Functional 3D design operating procedure

Create source-controlled, parameterized designs whose geometry, material,
purchased components, print configuration, and verification evidence are
traceable. Keep the actual 3D model, its function, and its manufacturing
readiness as the primary outcome. Optimize for the user's objective rather than
maximizing printed content.

A render is not proof of function. A slicable mesh is not proof of strength.

Resolve every bundled path relative to this `SKILL.md`.

## Read only what the task needs

- Full gate ladder, project structure, and definition of done: `references/design-process.md`
- Preflight linkage and staleness rules: `references/preflight-integration.md`
- Requirements/concept approval mechanics: `references/requirements-concept-approval.md`
- Choosing between CadQuery/OpenSCAD/FreeCAD/Blender: `references/tool-selection.md`, then `references/cad-coding-standard.md` for generated source
- Filament family trade-offs: `references/materials.md`
- Nozzle, layer, line width, orientation, flow: `references/nozzles-layers-slicer.md`
- Threads, snap-fits, hinges, gears, bearings, seals: `references/mechanical-features.md` and `references/design-patterns.md`
- Print-vs-buy judgement: `references/print-vs-buy.md`
- Mesh burden and simplification policy: `references/mesh-simplification.md`
- Verification ladder and analysis fidelity: `references/validation-testing.md`, `references/simulation-model-fidelity.md`
- Existing organic mesh as input: `references/organic-mesh-workflow.md`
- Standard-part libraries and MCP integrations: `references/parts-and-libraries.md`, `references/external-integrations.md`
- Subagent roles and CI boundaries: `references/automation-architecture.md`
- Learning capture and the parts library: `references/self-learning.md`
- Final report structure: `references/final-model-result-report.md`
- Adapting the package to a real printer fleet: `references/recommended-extensions.md`

Load a reference when its task is actually in scope. Do not preload the set.

## Mandatory preflight

Before requirements approval, concept generation, CAD/source creation, or
manufacturing export, invoke the sibling `3d-design-preflight` skill. Document
the assessment at `preflight/preflight-result.json`, validate it with that
skill's validator, and link it under `workflow.preflight` in `design-spec.yaml`.

For a new independently managed product, also complete the SKU, product folder,
portfolio CSV/XLSX, and license-chain intake described in `product-intake.md`
inside the `3d-design-preflight` skill's own `references/` directory. A
component, colorway, preform, or revision inside an existing product keeps the
owning SKU unless it will be independently offered, versioned, supported, and
retired.

For an existing design with no preflight, create a `RETROSPECTIVE` backfill from
recorded evidence before the next design change; never claim it existed
historically. Mark the assessment `stale` and update it when any assessed input
changes. `HOLD`, `CONCEPT_ONLY`, and Lane D/E remain binding.

## Design contract

Create or update `design-spec.yaml` with, or explicit assumptions for: function,
dimensions, interfaces, environment, load, speed, cycle count, service life;
risk class (`decorative`, `normal-functional`, `structural`, `safety-critical`);
fabrication preference (`integrated-print`, `balanced-hybrid`,
`standard-hardware`); printer/build volume, nozzle, material, enclosure,
hardened nozzle, drying; target formats; acceptance criteria and test method.

Default to `balanced-hybrid` and record the assumption. Do not hide uncertainty
behind arbitrary dimensions.

## Three approval gates

Record every gate state under `workflow` in `design-spec.yaml`.

1. **Requirements** — synthesize the user's input into `design-spec.yaml`, then
   review it, distinguishing `user-stated`, `inferred`, `recommended`, and
   `unresolved`. Ask only consequential questions, each with a recommended
   choice and its trade-off.
2. **Concept** — visualize the approved specification revision and map visible
   features back to requirements. Image labels are not authoritative; keep exact
   dimensions in the text.
3. **Final release** — only after the production model is verified. Load the
   sibling `metrimade-release-marking` skill, which owns the mark entirely.

The hash-bound autonomy policy decides which gate an agent may record through
the agent ledger; otherwise request explicit human approval. Do not generate a
concept image, CAD geometry, source, or manufacturing export before the assigned
approval is recorded. Only a schema `1.1` policy created with
`init-autonomy --preflight ...` is eligible for unattended Orca coordination.
Final release, physical printing, fit/function, appearance, safety, and
commercial stages remain human-controlled.

If a correction changes an approved requirement, mark the preflight `stale` when
an assessed input is affected, set the requirements gate `changes-requested`,
invalidate concept and marking approval, and repeat the affected gates.

## Process limits that decide first-pass quality

These are starting values from the exact-profile references, not qualified local
results. Anything that determines a fit must come from the calibration gate
below.

| Quantity | Working value |
|---|---|
| Default nozzle | 0.4 mm balanced detail · 0.6 mm functional/filled default · 0.8 mm large coarse |
| Layer height | ≤ 75% of nozzle as the normal ceiling; 80% only after flow and bonding validation |
| Typical layer range | 0.4 mm → 0.10–0.28 · 0.6 mm → 0.18–0.42 · 0.8 mm → 0.28–0.60 |
| Line width | 105–120% of nozzle diameter, from the tested profile |
| Walls | 2 lines cosmetic skin · ≥ 3 functional shell · more where load or insert stress demands |
| Overhang | 45° is a conservative geometric starting guideline, not a machine limit |
| Volumetric flow | `line_width × layer_height × speed`; limit by measured maximum volumetric speed |
| Snap cantilever | `strain ≈ 1.5 × thickness × deflection / length²` with a generous root fillet |

Rules that do not depend on calibration:

- Prefer walls, perimeters, and load-oriented geometry before raising infill.
- Use a hardened or abrasion-resistant nozzle for carbon, glass, glow, metal,
  and mineral-filled filaments; prefer 0.6 mm or larger unless the supplier
  explicitly supports 0.4 mm.
- Treat PLA+ / Tough PLA and branded blends as supplier-specific, never a
  standardized material class. The exact manufacturer profile and datasheet is
  the authority for temperature, drying, enclosure, abrasion, and service limits.
- Never use an upper printing temperature as a service-temperature rating.
- Avoid zero-thickness knife edges and details below a stable extrusion path.

## Calibration gate — query before choosing any fit

Every clearance, hole diameter, insert boss, bridge span, and snap strain must
come from a locally qualified measurement, not from a default or an estimate.
Query the registry before the geometry that depends on it exists:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py calibration \
  --machine "Anycubic Kobra 3 Max" --material "SUNLU PETG" --nozzle 0.6 \
  --quantity xy_clearance_sliding --quantity hole_delta_vertical
```

The command exits non-zero and names the qualifying coupon whenever a value is
`UNQUALIFIED` or the process identity is unknown. When that happens:

1. do not invent, average, or carry over a value from another process;
2. print the named coupon on the exact machine/material/nozzle/profile;
3. record the outcome as a `benchmark-measurement` under
   `libraries/3d-learning/benchmarks/measurements/`;
4. update `libraries/3d-learning/knowledge/processes/fff-calibration-registry.yaml`
   with the value, its evidence path, and its maturity;
5. only then commit the dependent geometry.

Absence of a registry value is never evidence that no compensation is needed.
`scripts/fit_clearance.py` and the other calculators are preliminary design
aids, not substitutes for this gate.

## Capture obligation

A design task is not complete until every physical measurement it produced is
written back. For each coupon, fit test, or prototype:

- record the outcome as a `benchmark-measurement`, including method,
  instrument resolution, and stated uncertainty;
- update the calibration registry for any quantity it qualifies;
- convert every actionable user correction into a targeted eval in the same
  design phase;
- invoke the sibling `3d-skill-maintainer` for lesson/pattern candidates.

Never record a value with an invented scope; use `unknown`. A blank measurement
worksheet is an incomplete design, not a finished one. Promotion beyond E0 needs
review; capture does not.

## Tool routing

Use `scripts/select_tool.py` when the route is not obvious.

- **CadQuery** — dimensional functional parts, B-Rep/STEP, fillets, holes, interfaces, assemblies.
- **OpenSCAD** — simple CSG, 2D profiles, repeating patterns, text/relief, reliable CLI generation.
- **FreeCAD** — interactive STEP editing, drawings, assemblies, FEM/CalculiX.
- **Blender** — organic meshes, scans, sculpting, remesh, visual relief, mesh repair.
- **Hybrid** — precise CAD for interfaces, mesh/SDF tools for organic or dense surface fields.
- **Step1X image-to-3D** — after concept approval and interface freeze, via the sibling `step1x-image-to-3d` skill. Exact interfaces and manufacturing authority stay here.

Do not convert a dense organic STL into a face-per-triangle B-Rep, and do not
model thousands of decorative cells as individual B-Rep booleans, without a
demonstrated need.

## Print-vs-buy

Run `scripts/print_vs_buy.py` for ambiguous components. Print for custom shape,
housings, adapters, ducts, low-speed large gears, compliant features, and
low-volume personalization. Buy for precision, wear, fatigue, sealing,
electrical contact, certified anchoring, high speed, or high stored energy —
rolling bearings, precision shafts, belts, springs, O-rings, high-load gears.

Prefer heat-set inserts, captive nuts, or through-bolts for repeated fastener
cycles, and a purchased metal pin or screw as a durable hinge axis. Generate
involute gears with a library; never approximate teeth by eye. Never invent a
safe load rating without test evidence and the actual installation conditions.

## Efficiency and mesh burden

Every manufacturing model must pass an efficiency and mesh-complexity decision
even when no change is applied. Invoke `optimize-fdm-design` where applicable;
it owns the patterns and the Pareto comparison.

Establish an exact slicer baseline and protect fits, load paths, sealing/wetted
walls, bed faces, appearance/relief, and stability mass. Record `applied`,
`not-beneficial`, or `not-applicable` per manufacturing mesh, judged by physical
surface error and protected regions rather than a triangle percentage. Keep the
unsimplified `master_mesh` and selected `manufacturing_mesh` at separate
immutable paths, set triangle/memory/mesh-size/slicer-time budgets before dense
or relief generation, keep the geometric report separate from
`slicer_resolution_check`, and rerun every affected engineering and coupon check
afterwards.

The check and its evidence are mandatory; a lossy transformation with no
measured benefit is prohibited.

## Gate ladder

Follow `references/design-process.md` for the full ladder. In order: preflight →
requirements → concept → architecture and decomposition → tool route →
**calibration gate** → parametric source → geometry checks → manufacturing
baseline and exact-profile slicer dry run → engineering characterization →
efficiency and mesh gate → selected-candidate verification → release marking →
final derived export and regression checks → release approval and packaging →
capture and learning → final model result report.

For Anycubic printers, route the slicer dry run through the sibling validation
skill's `slice-anycubic-next` command so source/profile/output hashes and native
slicer status are retained.

Before final packaging, run:

```bash
python scripts/validate_design_spec.py design-spec.yaml \
  --require-current-preflight --require-final-approval
```

## Final model result report

Read `references/final-model-result-report.md` before completing any design
task. Always end with a report about the actual model and delivered package,
even when draft or blocked: outcome first, then geometry and functions,
validation evidence, print readiness, deliverables, and remaining limitations.
Keep marking to a compact late **Kennzeichnung** note, and close on the model's
readiness or the next useful action.

## Subagent strategy

Use fast subagents for bounded, independently checkable work — dimension
extraction, parts-library search, classification, a calculator or sweep, a
report summary, or a small targeted source edit with an explicit test. Use a
capable agent for architecture, ambiguous loading, cross-tool geometry, failure
analysis, safety review, and final acceptance. Never ask a small agent to
silently make the final engineering decision.

## Parts library statuses

`concept` → `experimental` → `qualified-local` → `deprecated`. Never promote to
`qualified-local` without geometry validation, a linked test record, and the
printer/material/nozzle/profile identity. A locally qualified part is not
universally certified.

## Safety and stopping rules

Stop and request human engineering review before claiming readiness for life
support, medical treatment, pressure vessels, mains electricity, fire
protection, lifting, climbing, vehicle control, weapons, or child-safety
certification; for structural wall loads without wall/anchor verification; for
food-contact or biocompatibility claims based only on filament marketing; for
high-temperature or chemical exposure without exact material data; or for
autonomous printer upload/start.

Preserve the editable source and report failed checks honestly. Prefer a small
test coupon over speculative simulation when material or process uncertainty
dominates.

## Deterministic validation handoff

Use the sibling `validate-printable-3d-projects` skill as the release
orchestrator and apply `assets/validation-profile.json`, whose
`risk_class_requirements` set the minimum check and manual-gate set for the
declared risk class. Register the preflight result, source, parameters,
dependencies, mesh/3MF, slicer profile, G-code, interface contracts, coupons,
and reports with hashes in `validation-project.json`. Existing calculators are
component checks, not release proof. A missing, stale, or release-blocking
preflight; a required `NOT_RUN` or `REVIEW_REQUIRED`; stale evidence; a missing
marking approval; or a failed physical gate blocks release.

At project start, read the project autonomy policy before changing artifacts.
Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger, and only for
stages assigned to the agent. Never write `HUMAN_APPROVED`. Workflow autonomy
does not authorize dependency installation, upload, or printer start.
