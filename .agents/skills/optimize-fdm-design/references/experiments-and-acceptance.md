# Experiments, Pareto comparison, and acceptance

## Contents

- [Baseline discipline](#baseline-discipline)
- [Candidate matrix](#candidate-matrix)
- [Slicer metrics](#slicer-metrics)
- [Engineering and physical metrics](#engineering-and-physical-metrics)
- [Pareto selection](#pareto-selection)
- [Acceptance and release](#acceptance-and-release)

## Baseline discipline

Freeze these before comparing variants:

- source/mesh revision and units;
- printer/firmware, nozzle, hotend, and build surface;
- exact filament product, batch/condition/drying when relevant;
- orientation, layer height, line widths, speeds, flow limits, cooling, support, infill, and wall generator;
- slicer name/version, machine/material/process profile identity, and 3MF project;
- ambient/enclosure conditions for physical tests.

If one variable must change—such as nozzle size—classify it as a process variant. Do not attribute its gains to a geometry edit.

## Candidate matrix

Use a small sequential experiment instead of changing everything at once:

| Candidate | CAD geometry | Process | Purpose |
|---|---|---|---|
| Baseline | current | current | Reference |
| A | current | larger nozzle/layer or tuned profile | Isolate process gain |
| B | shells/ribs/windows | current | Isolate geometry gain |
| C | best B | best compatible A | Combined candidate |
| D optional | conservative B | best A | Lower-risk geometry |
| E optional | aggressive B | best A | Establish trade-off/failure boundary |

Use equal exterior dimensions and protected interfaces. Keep a decision log of each changed parameter.

For patterns with uncertain toolpath cost—small holes, honeycomb, corrugation, modeled lattice, or exposed slicer infill—slice at least one coarse and one fine pattern at equal outer envelope and acceptance constraints. For exposed infill add a medium-pitch candidate because endpoint anchoring and visual regularity may fail non-monotonically.

## Slicer metrics

Record per part and whole job:

- estimated print time and time by feature when available;
- model filament length/volume/mass;
- support/interface/brim/prime material separately;
- layer count and total Z height;
- perimeter, infill, bridge, support, and travel path length when available;
- retractions, seams, tool changes, and very short segments;
- peak/actual volumetric flow and cooling/minimum-layer-time limits;
- triangle count/file size, import time, slice computation time, and warnings;
- missing thin walls, gap fill, unsupported roofs, and bridge/support changes.
- exposed-infill body name, pattern, density/pitch, angle sequence, line width, layer count, frame overlap, missing/extra skins, loose endpoints, and crossing buildup.

Print time is the slicer's estimate for one profile, not a universal machine result. Confirm meaningful changes with actual printer time for a representative coupon or prototype.

## Engineering and physical metrics

Choose only metrics tied to service:

### Organizers and trays

- bottom/side deflection under distributed and point loads;
- divider-root strength and racking;
- drawer fit/travel and rail wear;
- anti-tip with drawers or high items loaded;
- flatness, cleaning, and edge comfort.

### Clips and stands

- insertion/retention force;
- maximum strain and permanent set;
- cycle count and failure mode;
- tip stability and joint backlash.

### Racks and long bars

- midspan deflection, twist, and straightness;
- joint stiffness and repeated assembly;
- rail/contact dimensional stability.

### Fluid/filter systems

- leak/head test duration and level;
- flow rate and head loss;
- separator capture/settling behavior;
- hose-port load, drain effectiveness, cleaning time;
- UV/thermal/freeze exposure plan.

### Relief products

- retained peak-to-valley and robust tonal span;
- seam/subject detail and wall reserve;
- slice/import time and triangle count;
- process-matched texture coupon.

Use multiple specimens when variability affects the decision. One surviving print is not a material allowable.

## Pareto selection

Store comparisons as:

```json
{
  "baseline": "baseline-04",
  "objectives": [
    {"metric": "print_time_min", "goal": "min"},
    {"metric": "material_g", "goal": "min"}
  ],
  "constraints": [
    {"metric": "drawer_deflection_mm", "op": "<=", "value": 1.0},
    {"metric": "passed_mesh_checks", "op": "==", "value": 1}
  ],
  "variants": [
    {"name": "baseline-04", "metrics": {"print_time_min": 2160, "material_g": 2500, "drawer_deflection_mm": 0.6, "passed_mesh_checks": 1}},
    {"name": "combined-06", "metrics": {"print_time_min": 1150, "material_g": 1750, "drawer_deflection_mm": 0.8, "passed_mesh_checks": 1}}
  ]
}
```

Run `scripts/compare_variants.py`. The tool:

1. rejects a variant with a missing/failed constraint;
2. computes objective deltas from the named baseline;
3. finds feasible non-dominated candidates;
4. does not invent a weighted score.

A candidate dominates another only when it is no worse in every objective and strictly better in at least one. Add stiffness, support mass, cost, or energy as additional objectives only when the decision genuinely needs them; otherwise retain them as constraints.

## Acceptance and release

Define pass limits before seeing candidate results. Include:

- exact protected dimensions and fit coupon tolerance;
- maximum deflection/strain or minimum factor/evidence level;
- minimum wall/relief reserve and leak-test requirement;
- acceptable visual/relief difference;
- for exposed infill, allowable aperture range, frame attachment, strand continuity, safe-edge condition, and required airflow/light/flex response;
- maximum support burden and accessible removal;
- mesh/manifold/body-count and slicer-layer checks;
- target time/material reduction.

Do not relax a constraint silently because a variant saves impressive material.

Accept a geometry change only when:

1. source and exported mesh checks pass;
2. exact-slicer toolpaths match the intended structure;
3. all constraints pass with the planned evidence level;
4. the candidate is Pareto-efficient or the user explicitly chooses its trade-off;
5. the source remains parametric and the baseline recoverable;
6. open physical tests and environmental limits are plainly reported.

Reject or revise when:

- savings come primarily from missing walls or unsupported roofs;
- slicer time/material grows due to excessive openings;
- stiffness/sealing/fit evidence is absent at a meaningful risk level;
- the candidate depends on an unverified flow rate or layer bond;
- maintenance, cleaning, or assembly becomes materially worse;
- mesh simplification damages a bed/contact/relief/interface surface.
