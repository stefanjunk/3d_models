# 3D Design System Policy

This policy governs every agent in the `/workspace/3d_models` OpenCode runtime.
The primary agent coordinates work; workers perform bounded reasoning or
implementation. Existing project layouts take precedence when modifying a
model.

## Repository Boundary

- Treat `/workspace/3d_models` as the only model repository.
- Run `git status --short --branch` before editing and preserve unrelated work.
- Model artifacts, reports, and source changes must stay inside this repository.
- Do not edit `/workspace/opencode.json`, `/workspace/.opencode`, website
  repositories, shared skills, or this repository's `opencode.json` and
  `.opencode` runtime files during ordinary model work.
- Do not commit, push, publish, or delete user models unless explicitly asked.

## Design Contract

- Use millimeters. Record tolerances, material, nozzle, fit intent, load
  direction, manufacturing assumptions, and unresolved physical tests.
- For new commercial projects, start from
  `.opencode/templates/commercial-product/`. Preserve `design-spec.json`,
  `components.json`, `provenance.json`, `manufacturing-profile.json`,
  `parameters.json`, `bom.json`, `reports/evidence.json`, source files,
  `exports/`, `previews/`, and a concise `README.md`.
- Put authoritative design values in `parameters.json` or one clearly marked
  parameter block. Do not duplicate magic numbers.
- Convert requests into functions, load cases, life requirements, failure
  modes, component decisions, dimensions, interfaces, constraints, and
  measurable acceptance criteria before substantial implementation.
- Ask one concise user question only when a missing value materially changes
  the design. Only the primary agent may ask the user.

## Commercial And Engineering Gates

For commercial products, detailed CAD is forbidden until both gates pass:

1. `COMMERCIAL_LICENSE_PASS`: Load `commercial-cad-provenance`; validate
   library code, embedded data, and every imported asset separately. Allow
   permissive licenses and CC-BY with complete attribution. Block copyleft,
   Share-Alike, Non-Commercial, No-Derivatives, unknown, and asset-level
   unverified sources. Prefer self-authored geometry when rights are unclear.
2. `ENGINEERING_DECISION_PASS`: Load `functional-3d-design`; document product
   functions, loads, service life, failure modes, and `PRINT`, `BUY`,
   `INTEGRATE`, `ELIMINATE`, or `NEEDS_TEST` decisions. `NEEDS_TEST` blocks
   detailed release CAD.

Print custom geometry. Buy precision, wear surfaces, bearings, shafts, belts,
seals, highly cycled springs, and standard fasteners unless a documented,
low-risk case and test plan justify otherwise.

Use original interface/envelope geometry from `commercial-component-interfaces`
when third-party component CAD is unavailable or not commercial-safe. Record
the factual dimensional source; do not copy blocked CAD geometry.

## Modeling Methods

Choose the smallest sufficient method and record the decision in the project
README or report.

- **CadQuery:** exact bores, mating faces, threads or PC4 interfaces, flanges,
  mounting patterns, datums, controlled fillets and chamfers, assemblies, or
  required STEP output. Preserve STEP as the editable master and STL as a
  tessellated derivative.
- **OpenSCAD:** understandable primitive CSG, adapters, holders, organizers,
  enclosures, hole patterns, and straightforward extrusion without demanding
  freeform surfaces or STEP output.
- **Implicit NumPy/SDF:** organic, pressure-driven, image-derived, cellular,
  porous, gyroid, graded, or topology-changing geometry. Use
  `field[z, y, x]`, negative inside, explicit millimeter spacing, a documented
  iso-level, and an empty boundary margin.
- **Hybrid:** exact functional interfaces plus organic, cellular, or imported
  mesh regions. Preserve provenance for every representation and do not call a
  final mesh a STEP-equivalent master.

Use Blender or direct mesh services only for primarily artistic, textile-like,
sculptural, or character work when the normal toolset is demonstrably
insufficient. Explain the exception first.

## Required Skills

Load the applicable skill before writing source or claiming its gate:

- CadQuery: `cadquery-functional-geometry` and `cadquery-llm-skill`
- OpenSCAD: `openscad`
- Implicit geometry: `implicit-3d-modeling`
- Exported mesh validation: `mesh-validation`
- FDM assessment: `fdm-printability`
- Bounded design experiments only: `parameter-sweep`
- Commercial dependency or CAD provenance: `commercial-cad-provenance`
- Functional products, mechanisms, hardware, loads, or life: `functional-3d-design`
- Generic 0.4/0.6/0.8 mm and material claims: `fdm-process-envelope`
- Snap-fits and flexures: `snap-fit-design`
- Original bearing/shaft/insert/screw interfaces: `commercial-component-interfaces`
- Pinned parametric CadQuery hardware: `cq-warehouse-commercial`
- Pinned OpenSCAD reuse: `bosl2-commercial`
- Precision and retention joints: `fdm-joints-and-fits`
- Gears, belts, chains, pulleys, or torque transmission: `power-transmission-design`

## Generic FDM Product Envelope

- Qualify nozzle/material classes, not arbitrary customer printers.
- Treat 0.6 mm as the preferred general functional class, 0.4 mm as the fine
  detail class, and 0.8 mm as the large robust geometry class. Do not promise
  all three unless every critical feature passes independently.
- Use PLA as the economical static indoor baseline and PETG as the primary
  economical functional baseline. Activate ABS/ASA, TPU, or PA/CF only from a
  documented environment or mechanical need.
- Fits, inserts, snaps, flexures, gears, and seals require representative
  coupons. Compensation values do not transfer between nozzle, material,
  orientation, slicer, or printer without new evidence.
- Never advertise universal FDM-printer compatibility. Ship customer-facing
  process limits and coupons instead.

## Build And Validation Loop

1. Inspect the nearest project README, design spec, components, provenance,
   parameters, source, exports, reports, previews, and repository state.
2. Decompose functions and document loads, life, failure modes, environment,
   and customer-facing claims.
3. Decide print/buy/integrate/eliminate and define the assembly and test plan.
4. Pass commercial provenance and engineering decision gates.
5. Select material/nozzle classes, coupons, interfaces, and modeling method.
6. Generate a low-cost preview before expensive final output.
7. Check extents, orientation, clearances, assembly order, tool access,
   topology, and feature placement.
8. Generate final source and exports only after the preview is plausible.
9. Reload each exported mesh from disk and run `mesh-validation`.
10. Run `fdm-process-envelope` and `fdm-printability` with declared assumptions.
11. Inspect multi-angle previews and slicer layers; inspect orthogonal slices
    for implicit fields.
12. Compare measured bounds and critical dimensions with acceptance criteria.
13. Qualify coupons and physical tests for every supported commercial claim.
14. Package source, parameters, BOM, notices, exports, coupons, previews,
    reports, and README only after applicable gates pass.

## Validation Truthfulness

- Source that was not executed is not validated.
- A Python mesh does not validate an analogous OpenSCAD implementation.
- Watertightness does not prove printability, fit, strength, comfort, or safety.
- Automated normal checks do not replace slicer layer review.
- Mesh repair must write a new file and retain before/after evidence.
- Never silently smooth, fill large holes, delete components, remesh, or
  decimate.
- For fitted, wearable, load-bearing, or safety-relevant parts, require a
  physical test print before final manufacturing approval.
- Commercial release claims for fits, snaps, flexures, gears, seals, or
  purchased-part interfaces require the documented coupons or physical tests.
- A repository-level license does not prove the license of an individual STEP,
  STL, 3MF, mesh, or CAD asset.
- If a required executable or package is missing, report the exact blocker.
  Never casually modify the global Python environment.
- Use `PASS`, `CONCERNS`, or `BLOCKED`; never claim completion from source
  generation alone.

## Evidence

Final evidence must identify changed files, the selected method, authoritative
parameters and assumptions, commands actually run, exports and measured
extents, mesh and FDM verdicts, previews inspected, unvalidated claims,
remaining risks, and required physical tests.

For commercial products it must also include load/life decisions, BOM,
provenance verdict, attribution files, supported/conditional/unsupported
nozzle-material combinations, coupons, customer qualification requirements,
and the distinction between `DIGITAL_PASS` and physical release approval.
