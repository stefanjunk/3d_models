# Workspace Agent Instructions

## 1. Git synchronization, protected paths, and product feature branches

### Branch and path policy

- `main` is the default integration branch and the only branch on which shared repository policy, business data, tooling, and agent configuration may be changed.
- Main-only paths include `AGENTS.md`, `business/**`, `tools/**`, `.agents/**`, `.claude/**`, `.codex/**`, `.opencode/**`, equivalent root-level agent-configuration directories, and root-level companion instructions such as `CLAUDE.md`.
- Product work under `products/**` may be changed directly on `main` or on a dedicated feature branch. Prefer one feature branch and one Orca/Git worktree per product when multiple products are developed concurrently.
- A product feature branch may change only its explicitly assigned product subtree under `products/**`. Use one product per branch unless the human owner explicitly authorizes a multi-product scope. Do not include main-only paths or unrelated product changes in the branch.
- If product work requires a change to a main-only path, record or report that dependency and handle it as a separate task on `main`; do not widen the feature-branch diff.
- Multiple write-capable product leads may run concurrently only in separate worktrees, on separate feature branches, and with disjoint product subtrees. Keep exactly one write-capable lead per worktree and branch; reviewers in that worktree remain read-only while the lead is active.
- Never check out the same branch in multiple worktrees. Never force-push or rewrite `main` history. Integrate concurrent work non-destructively and stage only the current task's files.

### Start of a design or design phase

- Synchronize the repository with its upstream remote before changing design artifacts.
- Inspect the current branch, upstream, and `git status` first, and confirm that the branch and worktree match the assigned path scope.
- For main-only work, confirm that the current branch is exactly `main`, that it tracks `origin/main`, and that it is synchronized non-destructively before editing.
- For product feature work, create or use a dedicated branch and worktree based on the current `origin/main`. Set the branch upstream on its first push, and keep the branch limited to the assigned `products/**` subtree.
- Preserve all existing user and agent changes. Never discard, overwrite, reset, or silently hide a dirty worktree to make synchronization succeed.
- Fetch and integrate upstream changes with an appropriate non-destructive workflow, such as `git pull` or an equivalent fetch plus merge/rebase operation.
- If local changes, conflicts, authentication, path ownership, or branch state prevent safe synchronization or isolation, stop design edits and report the exact blocker.

### End of every completed design phase

- Review the diff and validation evidence before staging.
- Stage only the files that belong to the completed phase; do not include unrelated user changes.
- Consider Git LFS before staging large binary CAD, mesh, image, archive, 3MF, or other manufacturing artifacts. Follow existing `.gitattributes` and repository conventions. Do not rewrite existing Git history to migrate files into LFS without explicit approval.
- For a main-only phase, create a descriptive commit directly on `main` and push it to `origin/main`.
- For a product feature phase, verify that every changed path is inside the assigned product subtree, create a descriptive commit on the feature branch, push it to its matching remote branch, and report it as merge-ready. The product worker must not merge its own branch into `main` unless it is also the explicitly assigned integration owner.
- Integrate merge-ready product branches into `main` one at a time from a clean, synchronized integration worktree. Recheck the branch path scope and required validation evidence before merging, then push the updated `main` to `origin/main`.
- Confirm that the appropriate branch push succeeded. A feature phase is not integrated until its commit is present on `origin/main`; do not describe a branch-only candidate as integrated or released.

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

## 3. Exact FDM slicer workflow

- For Anycubic FDM work, use the sibling `validate-printable-3d-projects` command `fdm_ci.py slice-anycubic-next` as the supported headless Anycubic Slicer Next adapter.
- Slice STL/OBJ only with explicit machine, process, and filament JSON profiles. A 3MF may use its embedded profiles; if external profiles are supplied, require the complete set.
- Write every run to a new output directory. Preserve the source, slicer version, executable/profile/input hashes, native `result.json`, exact G-code hash, and G-code analysis report.
- Anycubic Slicer Next embeds a generation timestamp and may also vary path segmentation or ordering between same-scope runs. Do not demand raw or normalized byte identity and do not rewrite manufacturing G-code to hide differences; retain each exact artifact, compare exact-input reports and approved metric tolerances, and review diagnostic path diffs separately.
- Required slicer absence, unreadable version, missing profile, failed native result, or missing G-code is fail-closed. Final layer, support, seam, tool/color, and purge review remains human-controlled.
- The adapter may export local files only. Printer upload and print start are outside this workflow and require separate explicit human action.
