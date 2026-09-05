# Metricreate Orca operating contract

## Runtime topology

Use a persistent Codex coordinator terminal in a clean `main` integration
workspace. Put each concurrent write-capable product lead in a dedicated Orca
worktree on a feature branch with one explicitly assigned `products/**`
subtree. The coordinator is control-plane and integration owner, not a product
geometry author.

| Actor | Write authority | Responsibility |
|---|---|---|
| Coordinator | Orca task state, short workspace comments, and serialized `main` integration | route work, watch lifecycle messages, resolve or escalate gates, integrate validated product branches |
| Design lead | one named product/phase subtree in one feature worktree | requirements, architecture, CAD/mesh, evidence, feature-branch commit and push |
| Reviewer | read-only | independent geometry, interface, validation, or risk review |
| Human owner | human ledger and external actions | physical print/test, appearance, safety, final/commercial approval |

Do not dispatch two write-capable workers concurrently in the same checkout.
Write-capable leads may run concurrently only in separate feature worktrees
with disjoint product subtrees. Read-only work may run concurrently after the
lead in that worktree has produced an immutable candidate or explicitly paused.
Paths outside the assigned `products/**` subtree, especially `business/**`,
`tools/**`, and root-level agent configuration, remain main-only.

## Intake and policy binding

1. Create and validate `preflight/preflight-result.json`.
2. Select no more autonomy than the preflight permits.
3. Create a new bound policy rather than silently modifying a policy whose hash
   already appears in an approval ledger:

```bash
python3 .agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py \
  init-autonomy PRODUCT-ID path/to/autonomy-policy.json \
  --mode autonomous-to-print-candidate \
  --authorized-by project-owner \
  --preflight path/to/preflight/preflight-result.json
```

If an existing policy has ledger events, preserve it with the owning revision.
Create a new revision/policy identity after preflight or scope changes.

## Orca task contract

Every dispatched task states:

```yaml
objective: one measurable outcome
product_scope: one product folder and revision
branch_scope: one feature branch and Orca worktree based on current origin/main
allowed_changes: exact paths or read-only
forbidden: protected main-only paths, unrelated products, printer upload/start, human approvals
inputs: exact files, policy, profiles, and artifact hashes
acceptance: deterministic command and expected status
completion: worker_done with filesModified and reportPath
```

Use a manual coordinator loop (`task-create`, worker terminal, `dispatch
--inject`, rolling `check --wait`) when human steering may be needed. An
automatic Orca coordinator run is acceptable only when the same boundaries are
present in its spec and `--worktree` targets the assigned product worktree.

## Monitoring surface

Orca should expose five signals without reading the full transcript:

1. workspace comment: `PRODUCT · stage · PASS/BLOCKED · next gate`;
2. orchestration task list: owner, dependency, and lifecycle status;
3. worker terminal: current command and whether it is active, idle, or waiting;
4. repository diff and latest render/model artifact;
5. validation summary and approval-ledger target state.

Use these interventions:

- **Steer:** send a precise constraint change to the active design lead.
- **Pause:** stop new dispatches and let the current non-destructive command
  reach a safe boundary; interrupt immediately only when requested or unsafe.
- **Revise:** invalidate affected approvals/evidence and dispatch a new bounded
  revision task.
- **Stop:** stop the Orca run and retain partial artifacts/status as draft.
- **Approve:** use the separate human approval command; never send approval as
  ordinary terminal text and let an agent record it for the human.

## Automations

Automations are schedulers, not engineering authorities. Appropriate examples
are a disabled test automation, a read-only daily blocked-task digest, or an
intake watcher that prepares a coordinator task. Use an existing workspace so
no worktree is created. Do not schedule autonomous design execution until the
single-writer and preflight-bound policy checks are proven in a pilot.
