# Workspace Agent Instructions

## 1. Git synchronization for 3D design work

### Start of a design or design phase

- Synchronize the repository with its upstream remote before changing design artifacts.
- Inspect the current branch, upstream, and `git status` first.
- Preserve all existing user and agent changes. Never discard, overwrite, reset, or silently hide a dirty worktree to make synchronization succeed.
- Fetch and integrate upstream changes with an appropriate non-destructive workflow, such as `git pull` or an equivalent fetch plus merge/rebase operation.
- If local changes, conflicts, authentication, or branch state prevent a safe synchronization, stop design edits and report the exact blocker.

### End of every completed design phase

- Review the diff and validation evidence before staging.
- Stage only the files that belong to the completed phase; do not include unrelated user changes.
- Consider Git LFS before staging large binary CAD, mesh, image, archive, 3MF, or other manufacturing artifacts. Follow existing `.gitattributes` and repository conventions. Do not rewrite existing Git history to migrate files into LFS without explicit approval.
- Create a descriptive commit for the phase and push the current branch to its configured upstream.
- Confirm that the push succeeded. Do not describe the phase as synchronized or complete while required changes remain only local.

## 2. Evidence-gated 3D learning

### Capture after design, print, test, or user correction

- Use the `3d-skill-maintainer` skill after meaningful feedback, measurements, failures, successful tests, or repeated design decisions.
- Keep raw project traces, photos, measurements, profiles, and generated artifacts in the owning product folder. Store only scoped records and links in `libraries/3d-learning/`.
- Convert every actionable user correction into an eval candidate in the same phase. Do not convert a correction directly into a universal rule.
- Preserve exact process scope: feature, machine, material/product/color/batch, nozzle diameter/material, orientation, slicer/profile, geometry, environment, and measurement method when relevant.
- Store successes and failures. Distinguish observation from explanation and state uncertainty explicitly.

### Promotion and production changes

- Treat every new experience as a candidate first. Apply maturity levels `E0` through `E4` and the promotion gates documented in `libraries/3d-learning/3D-LEARNING-ARCHITECTURE.md`.
- Do not edit a production skill, knowledge reference, or validated pattern merely because a candidate exists. Require a validated explanation, linked targeted eval, regression results, and human approval at the level required by the promotion policy.
- The `3d-skill-maintainer` may create or update candidates, evals, conflict reports, and proposed patches. It must not silently promote records or directly rewrite production skills.
- Retrieve learning context just in time: filter structured scope first, then rank feature match, evidence level, textual similarity, and recency. Never load the full experience store by default.
- Run `python .agents/skills/3d-skill-maintainer/scripts/learning_records.py validate` before completing a learning-system change.
