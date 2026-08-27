# Evidence-gated self-learning and extension

## Goal

Improve future 3D work from measurements, failures, accepted solutions, and user
corrections without treating one result as universal truth or expanding the core
design skill indefinitely.

The full source of truth is
`libraries/3d-learning/3D-LEARNING-ARCHITECTURE.md`. Use the sibling
`3d-skill-maintainer` to author and review learning records.

## Separation of concerns

- Skills contain procedure.
- Knowledge contains sourced facts.
- Patterns contain reusable parametric solution structures.
- Experience contains scoped observations and explanation candidates.
- Evals contain explicit expected outcomes and failure conditions.
- Benchmarks contain coupon models and measurements.
- Scripts contain deterministic validation and retrieval logic.

Keep product-specific raw evidence under the owning `products/...` directory.
The shared learning library stores normalized records and links, not copied CAD,
photos, meshes, G-code, or large reports.

## What to record

For every meaningful test or correction:

- project and part revision, source commit, and trace path;
- feature type, geometry class, design parameters, named datums, and constraints;
- printer/unit, firmware, slicer/version, profile name/hash;
- nozzle diameter, material, geometry, hotend, and wear state;
- exact filament manufacturer, product, variant, color, batch, and conditioning;
- orientation, layer height, line width, walls, infill, cooling, speed, and MVS;
- measurement method, resolution, uncertainty, and environment;
- expected value, actual value, pass/fail, and failure mode;
- photos, raw data, and report paths;
- observation count, geometry count, and context breadth.

Use `unknown` or `null` when a value is not known. Never invent the scope.

## Two related status systems

Parts-library status remains:

- `concept`: source or idea only;
- `experimental`: generated/printed with incomplete evidence;
- `qualified-local`: passed a named plan on one recorded local process;
- `deprecated`: failed, unsafe, or superseded.

Learning-record maturity is independent:

- `E0`: observed once;
- `E1`: repeated under equivalent conditions;
- `E2`: repeated on multiple geometries;
- `E3`: tested across multiple machine/material/nozzle contexts;
- `E4`: validated explanation, measured evidence, targeted/regression passes,
  and approved human review.

A `qualified-local` part may still support only an E0 or E1 lesson. Neither term
means certified.

## Workflow

1. Preserve the complete product trace and raw evidence.
2. Run `3d-skill-maintainer` reflection and create a scoped candidate.
3. Separate observed result from causal hypothesis and alternatives.
4. Convert every actionable user correction into a targeted eval.
5. Validate and audit the store:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py validate
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py audit
```

6. Test the explanation with controlled coupons or deterministic checks.
7. Run `promotion-check` for the proposed maturity. It never mutates records.
8. Propose the smallest durable change: knowledge, pattern, eval, script, or
   stable procedure in a skill.
9. Run targeted and regression tests, obtain the required human review, update
   versions/changelog, and complete the Git synchronization in root `AGENTS.md`.

## User-correction rule

A correction is not itself a universal lesson. Preserve original proposal,
correction, and accepted result. Derive the general failure condition.

Example:

```text
Correction: fasteners were placed on the wrong side.
Do not learn: fasteners always belong on the right.
Create eval: machine-relative handedness must be resolved against an explicit
coordinate frame and reference view before export.
```

## Product-specific authority

For conflicting filament or component guidance, the exact physical
product/batch label outranks a broader family page. Record both sources and the
conflict. Do not silently average ranges or transfer a result across similarly
named formulations.

## Just-in-time retrieval

Filter structured metadata before semantic/text ranking. The order is scope,
feature, evidence, similarity, recency. Return only three to five relevant
validated records by default. Load candidates only for experiment planning and
label them unvalidated.

## Local parts-library commands

These remain valid for qualifying reusable part geometry:

```bash
python scripts/parts_library.py init
python scripts/parts_library.py search drawer
python scripts/parts_library.py add --entry templates/part-entry.json
python scripts/record_test_result.py --part-id my-part --result tests/result.json
python scripts/parts_library.py promote --part-id my-part --status qualified-local
```

The promotion command refuses local qualification without validation and test
evidence. Repository-wide lessons additionally require the E0–E4 policy.

## Extension rule

When a repeated finding warrants a production change:

1. link its evidence records;
2. add a targeted eval reproducing the behavior;
3. propose the rule or pattern at the narrowest valid scope;
4. run targeted and general regression suites;
5. obtain human approval;
6. version the changed artifact and record reason, evidence, eval, and results;
7. commit and push only the completed phase files.

Preserve failures and rejected explanations. They prevent repetition and remain
useful negative knowledge when retrieved within their scope.
