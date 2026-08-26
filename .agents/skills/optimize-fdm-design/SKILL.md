---
name: optimize-fdm-design
description: Optimize functional and hybrid FDM/FFF models for lower print time and material while preserving required stability, fit, durability, sealing, and appearance. Use for organizers, trays, clips, docks, stands, racks, relief-backed products, housings, brackets, mechanisms, ducts, and low-pressure fluid systems; for redesigns involving shells, ribs, windows, gussets, local reinforcement, exposed infill/no-wall lattice regions, nozzle/layer changes, support elimination, or slicer A/B comparisons. Do not use as the primary sculpting workflow for purely decorative art, figurines, or toys without functional requirements.
---

# Optimize FDM design

Reduce print time and deposited material by changing the load path, process, and toolpaths deliberately. Preserve explicit acceptance criteria; do not equate lower mass with a successful design.

This skill uses the portable `SKILL.md` plus relative-resource layout supported by ChatGPT Work, OpenCode, and other Agent-Skills-compatible runtimes. Its scripts require only Python 3's standard library.

## Read only what the task needs

- General shells, ribs, windows, floors, gussets, and support-free patterns: `references/pattern-catalog.md`
- Exposed infill/no-wall grids as intentional porous or decorative geometry: `references/exposed-infill-patterns.md`
- Organizers, trays, clips, docks, cosmetic storage, relief panels, and Mahjong products: `references/application-families.md`
- Loaded mechanisms, fasteners, housings, ducts, and water/filter systems: `references/mechanical-and-fluid-systems.md`
- Slicer A/B tests, Pareto comparison, coupons, and release evidence: `references/experiments-and-acceptance.md`
- Worked design studies and script input: `references/examples.md`
- Research provenance and limits of the evidence: `references/evidence-and-sources.md`

## Scope and routing

Use this skill with `functional-3d-design` when creating or revising a functional model. Obey that skill's requirements/concept approvals before changing visible geometry or interfaces. If the user asks only for an investigation, measure and propose variants without editing the model.

Use `design-printable-surface-textures` for carbon/wood/fabric/stone/metal appearance, vector or procedural texture, slicer Fuzzy Skin/top paths, custom surface paths, and material/finish selection. Keep this skill authoritative for structural efficiency and for the complete framed exposed-infill manufacturing contract.

If the surface-texture decision selects localized continuous-tone image relief, use `3d-print-heightmap-relief` alongside this skill. Preserve its 16-bit source/build masters while reducing manufacturing-mesh complexity separately.

For organic art, figurines, and toys, use the appropriate organic/reconstruction skill as the primary workflow. Apply only the relevant subset here: orientation, support removal, hollowing or shells, nozzle/layer/flow limits, mesh complexity, stability, impact zones, and small-part safety. Slicer infill optimizes only the enclosed interior; it does not automatically fix excessive outer volume, supports, fragile limbs, dense meshes, or poor orientation.

## Hard rules

1. **Establish an exact baseline before optimizing.** Record model revision, printer, nozzle, material, orientation, slicer/version/profile, time, model/support material, layer count, and warnings.
2. **Write protected requirements first.** Preserve fits, datums, rails, stops, seals, wetted walls, relief/cosmetic surfaces, hand-contact edges, load paths, fastener interfaces, bed faces, and required mass or anti-tip behavior.
3. **Optimize under constraints, not by mass alone.** Treat print time and material as objectives; treat function, stiffness, strength, fatigue, impact, sealing, dimensional fit, serviceability, and appearance as pass/fail or bounded constraints.
4. **Prefer continuous extrusion load paths.** Use shells, closed sections, ribs, straps, gussets, and local pads before raising global infill.
5. **Do not replace one large wall with hundreds of tiny cells without slicing both.** Every opening adds perimeters, corners, accelerations, and often retractions. Few large windows with deliberate ribs are usually the first variant to test.
6. **Model important thin features for the intended line width.** Use `scripts/plan_shell_ribs.py`, then verify the exact slicer paths; variable-width wall generators may choose different paths.
7. **Keep reinforcement local.** Use CAD pads/ribs or slicer modifiers around bosses, bearings, clips, rail ends, and load introduction. Do not pay for the same strength everywhere.
8. **Protect anisotropic weak directions.** Orientation and layer adhesion can dominate any infill change. Split or reorient a part when it creates a better continuous load path.
9. **Eliminate supports geometrically where practical.** Prefer chamfers, arches, teardrops, short bridges, split parts, and accessible sacrificial features over large generated support volumes.
10. **Respect volumetric flow.** A larger nozzle/layer is faster only until the exact filament/hotend flow limit becomes the bottleneck.
11. **Keep fluid-containment walls continuous and inspectable.** Do not expose sparse infill or create inaccessible wet cavities. Use external ribs and uniform multi-perimeter walls; leak-test the exact process.
12. **Never claim retained strength from geometry intuition alone.** Use calculations/FEM for comparative decisions and coupons/prototypes for process-dependent acceptance.
13. **Map protected geometry before removing material.** Name structural runners/rails, perimeter frames, smooth sliding/contact surfaces, stops, interface pads, and their connecting load paths; openings and ribs must route around them.
14. **Check thin plates before tuning infill.** Estimate whether wall stacks from both faces already consume the full plate thickness, then inspect the exact slicer paths. If no reliable core remains, infill percentage is not a meaningful material lever.
15. **Treat exposed infill as a manufacturing-defined lattice.** Keep the solid frame and `LATTICE_ENVELOPE` as distinguishable parts/volumes of one multi-part object until slicing, so the slicer can assign different settings. Do not Boolean-union away that identity before toolpath generation. Disable walls and top/bottom skins only for the lattice part, design a verified frame connection, preserve the exact 3MF/profile, and validate every generated layer. Never assign critical fits, sealing, safe edges, or primary load paths to wallless infill.

## Mandatory workflow

### 1. Freeze the baseline and objective

Record:

- exact manufacturing profile and model orientation;
- model and support mass/volume, estimated time, layer count, tool changes/retractions when available, and slicer computation time;
- triangle count/file size separately from estimated print time;
- functional loads, interfaces, environment, cycles, leak/flow needs, cosmetic surfaces, and risk class;
- target reductions and maximum permitted performance change.

Do not infer print-time savings from CAD volume alone. Time depends on path length, layer count, acceleration, cooling/minimum-layer time, flow, supports, and travel.

### 2. Partition the model by role

Mark each region as one or more of:

- protected interface or datum;
- primary load path;
- stability/anti-tip mass;
- sealed or wetted barrier;
- visible/cosmetic or relief surface;
- top-skin support;
- intentionally porous/exposed lattice field;
- redundant bulk;
- generated support driver;
- replaceable wear/service part.

Only redundant bulk and avoidable support are immediate removal candidates. A hidden wall is not automatically redundant.

For exposed infill, preserve two manufacturing identities even when the result is one physical print: a normally sliced structural/frame part and an infill-only lattice part. Place both in the same project frame and group them as one multi-part object; connect their toolpaths through a slicer-verified shared interface or capture band.

Store a protected-geometry map before generating lightweight variants. For drawer/organizer products it must explicitly name guide runners, top/bottom edge frames, front/handle zones, rear stops, smooth sliding faces, divider junctions, and anti-tip mass where applicable.

### 3. Choose levers in the right order

Evaluate these levers, stopping when the target is met:

1. remove unnecessary printed parts or substitute standard hardware;
2. change orientation/splitting to reduce supports and align layers;
3. select nozzle, line width, layer height, and speed within measured flow and detail limits;
4. replace bulk with shells, closed sections, large windows plus straps, ribbed skins, or gussets;
5. reinforce only local interfaces and known load paths;
6. use exposed infill as an intentional visual/porous lattice only inside a framed, named, slicer-verified region;
7. use sparse/adaptive enclosed infill only where top skins or distributed loads need it;
8. reduce mesh complexity when it burdens import/slicing/controller paths, without confusing that with deposited-material savings.

Read the relevant pattern and application reference before changing geometry.

### 4. Generate at least three comparable candidates

Normally compare:

- `A — process only`: unchanged CAD, nozzle/layer/profile changes;
- `B — geometry only`: same print profile, structural lightweighting/support removal;
- `C — combined`: best compatible process and geometry changes.

Add a conservative and aggressive geometry variant when structural uncertainty is material. Change one lever family at a time so the cause of an improvement remains traceable.

### 5. Slice every candidate with the exact profile

Inspect more than the summary:

- wall path count, gap fill, thin features, bridges, top-skin support, seams, and local modifiers;
- time by feature when available, model/support material, travel/retractions, layer count, and peak volumetric flow;
- whether small openings or modeled lattices increased perimeter time;
- whether 0% infill leaves unsupported roofs or disconnected skins;
- whether an exposed-infill region has exactly the intended missing walls/skins, continuous frame anchors, aperture pattern, crossings, and layer-to-layer bonds;
- whether opposing wall stacks already consume a thin plate, leaving no genuine infill core;
- whether a nozzle change erases text, relief, clearances, clips, or small radii.

Save the 3MF/profile identity for the baseline and selected candidate.

### 6. Verify performance at useful fidelity

Use hand calculations or comparative FEM for likely critical sections. Print the smallest process-matched coupon that isolates an uncertain wall/rib joint, clip, boss, rail, bridge, seal, or relief. Escalate to a subassembly/full prototype for interactions such as drawers, anti-tip behavior, fluid separation, maintenance, and dynamic mechanisms.

Do not compare specimens printed in different orientations, materials, drying states, nozzles, or profiles as though geometry were the only variable.

### 7. Select a Pareto candidate

Use:

```bash
python scripts/compare_variants.py examples/desk-organizer-variants.json --markdown
```

Reject candidates that fail any protected constraint. Among feasible variants, retain the Pareto set for time and material; let the user choose when one is faster and another is lighter or stiffer. Do not hide a performance trade-off inside a single arbitrary score.

### 8. Release with evidence

Report before/after geometry, time, model/support material, slicer load, nozzle/layer/flow assumptions, checks, coupons/tests, and remaining uncertainty. Preserve the editable baseline and optimized source. Do not overwrite the only high-fidelity or unsimplified master.

## Core pattern selection

| Situation | First pattern to test | Avoid by default |
|---|---|---|
| Large tray/organizer wall | Thin continuous shell plus rounded ribs | Thick wall containing sparse infill |
| Hidden drawer side/back | Few large radiused windows plus diagonal/edge straps | Dense small honeycomb/loch raster |
| Broad floor | Closed thin skin with underside ribs and edge beam | Thick solid slab |
| Long stand/rack beam | Hollow box/hat section with local diaphragms | Solid rectangular bar |
| Boss or rail end | Local pad, gusset, and extra perimeters/modifier | Global high infill |
| Horizontal roof | Arch/chamfer/ribs or split part | Large inaccessible support field |
| Wet/filter chamber | Uniform multi-perimeter barrier with external ribs | Wetted infill cavities or hidden leak paths |
| Relief panel | Thin backer, perimeter frame, sparse rear ribs, adaptive relief mesh | Uniform dense relief grid over flat areas |
| Porous/decorative screen | Framed exposed-infill region with saved slicer contract | Unframed wallless infill or assuming the CAD/STL contains the pattern |

## Quantification helpers

Plan path-compatible nominal sections:

```bash
python scripts/plan_shell_ribs.py \
  --nozzle-mm 0.6 --line-width-mm 0.68 --layer-height-mm 0.30 \
  --shell-lines 3 --rib-lines 2 --sealed-lines 4 \
  --floor-layers 4 --plate-thickness-mm 2.72 \
  --wall-lines-per-side 2 --speed-mm-s 45
```

The wall formula approximates classic constant-width extrusion spacing. With a plate thickness it also reports whether two opposing wall stacks leave a full-line-width infill core. Treat its output as a CAD starting point and verify it in the exact slicer's wall generator.

Compare measured candidates with `scripts/compare_variants.py`. Keep input metrics auditable; the script rejects infeasible variants before calculating the Pareto set.

## Deliverable contract

Always provide:

- baseline model/profile identity and measured slicer metrics;
- protected regions and acceptance limits;
- candidate table with isolated lever families;
- selected patterns and why they match the actual load/support/flow path;
- exact wall/rib/floor path assumptions and slicer confirmation;
- for exposed infill, distinguishable envelope/frame parts within one multi-part object, complete per-part settings, their physical connection method, exact 3MF/profile, layer preview, and coupon result;
- before/after print time, model material, support material, and mesh/slicing metrics;
- calculation, simulation, coupon, prototype, or leak-test evidence appropriate to risk;
- rejected variants and the specific constraint they failed;
- selected Pareto candidate or a clear user decision point;
- editable source plus the unchanged baseline and selected manufacturing export.

## Safety boundary

Stop for qualified engineering review before optimizing pressure vessels, lifting/climbing parts, vehicle control, mains/fire protection, medical devices, weapons, or child-safety-critical products. Lightweighting raises consequence sensitivity; never convert an unverified prototype into a load rating.

## Deterministic validation handoff

Before selecting a candidate, load the sibling `validate-printable-3d-projects` skill and apply `assets/validation-profile.json`. Hash the immutable baseline, each parameter set, generated mesh, exact slicer profile, G-code, and measurement report. Use deterministic sweeps for candidate generation; audit every mesh, compare protected geometry to the baseline, and derive time/material/tool-change metrics from G-code. Strength, sealing, fatigue, appearance, and exposed-infill bonding remain explicit simulation, coupon, or physical gates. Required `NOT_RUN`, `REVIEW_REQUIRED`, stale evidence, or a failed gate blocks release.

At project start, read the project autonomy policy before changing artifacts. Record only `AUTO_APPROVED` or `BLOCKED` in the agent ledger and only for stages assigned to the agent. Never write `HUMAN_APPROVED`; strength, sealing, fatigue, appearance, safety, and commercial stages remain in the separate human ledger. Workflow autonomy does not authorize dependency installation, upload, or printer start.
