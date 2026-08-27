---
name: 3d-skill-maintainer
description: Convert 3D-design, FFF/FDM print, validation, measurement, and user-feedback traces into scoped lesson candidates, design-pattern candidates, targeted evals, duplicate/conflict reports, and reviewed patch proposals. Use after meaningful 3D project revisions, print tests, calibration coupons, user corrections, recurring failures, or successful solutions that may be reusable; also use to retrieve only the most relevant validated local experience before a design. Do not use it to silently promote observations or rewrite production skills.
---

# 3D Skill Maintainer

## Purpose

Curate evidence-backed learning without growing production skills into knowledge
dumps. Treat skills as procedure, knowledge as sourced facts, patterns as
reusable solutions, experiences as observations, evals as expectations,
benchmarks as measurements, and scripts as deterministic checks.

The source of truth is `libraries/3d-learning/`. Read its
`3D-LEARNING-ARCHITECTURE.md` for governance or schema questions.

## Authority boundary

You may create and revise raw trace manifests, lesson/pattern candidates,
targeted evals, conflict reports, and proposed patches. You must not:

- mark human review as approved;
- move a candidate to `validated` without explicit approval;
- directly modify a production skill from one success/failure;
- generalize beyond machine/material/nozzle/geometry evidence;
- remove negative or conflicting evidence;
- weaken an eval to make a proposal pass.

## Workflow

1. **Synchronize Git.** Follow root `AGENTS.md` before touching learning or 3D
   artifacts. Preserve unrelated worktree changes.
2. **Locate evidence.** Read the owning product trace, requirement revision,
   design parameters, validation results, print profile, measurements, and exact
   user correction. Keep raw evidence in the owning product directory.
3. **Normalize scope.** Record feature, process, machine, exact material,
   nozzle, orientation, slicer/profile, geometry, environment, and measurement
   method. Use `unknown`, never a guessed value.
4. **Separate observation and explanation.** State expected versus actual,
   outcome, causal hypothesis, plausible alternatives, and whether the mechanism
   is validated.
5. **Create a candidate.** Copy
   `libraries/3d-learning/templates/lesson-candidate.yaml`; allocate the next ID
   with `scripts/learning_records.py next-id`. Start at E0 unless existing
   evidence demonstrably satisfies a higher gate.
6. **Create an eval for each correction.** Encode the general expected behavior
   and failure condition, not a local directional answer or magic dimension.
7. **Audit duplicates/conflicts.** Run `validate` and `audit`; link overlapping
   records. Unresolved overlapping contradictions block promotion.
8. **Validate the explanation.** Prefer controlled coupons and deterministic
   outcome checks. Preserve failed attempts.
9. **Check promotion only.** Run `promotion-check --target E#`. A passing report
   is necessary but does not grant approval or mutate files.
10. **Propose the smallest durable change.** Choose knowledge, pattern, eval,
    script, or—only for broadly procedural behavior—production skill. Link
    evidence and version impact.
11. **Run targeted and regression evals.** Use the sibling
    `validate-printable-3d-projects` skill for CAD/mesh/release evidence.
12. **Human review, Git commit, push.** Apply an approved promotion, update the
    changelog, validate again, stage only phase files, consider LFS, commit, and
    push as required by `AGENTS.md`.

## Maturity language

- E0: “Observed once in this recorded scope.”
- E1: “Repeated under equivalent recorded conditions.”
- E2: “Repeated across multiple geometries in the recorded process scope.”
- E3: “Repeated across multiple recorded machine/material/nozzle contexts.”
- E4: “Validated rule within the explicitly stated applicability and
  exclusions.”

Never replace these with an unqualified universal claim.

## Just-in-time retrieval

Before reusing local experience, filter metadata first and only then rank:

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py retrieve \
  --process FFF --machine "Anycubic Kobra 3 Max" \
  --material "Elegoo Rapid PETG" --nozzle 0.6 \
  --feature press-fit --query "cylindrical clearance" --limit 5
```

Default retrieval includes validated lessons only. Use `--include-candidates`
solely for experiment planning and label every returned candidate as
unvalidated.

## Commands

```bash
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py validate
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py audit
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py next-id
python .agents/skills/3d-skill-maintainer/scripts/learning_records.py \
  promotion-check path/to/EXP-00001.yaml --target E1
```

Read `references/record-authoring.md` when authoring a record and
`references/promotion-and-retrieval.md` when reviewing maturity, conflicts, or
retrieval results.

## Required output

Report candidate/eval IDs, exact scope, evidence level, confidence, unresolved
conflicts, validation results, proposed target store, and any human decision
still required. Do not call a candidate “learned” merely because it was saved.
