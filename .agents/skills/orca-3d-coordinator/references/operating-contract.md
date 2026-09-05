# Metricreate Orca operating contract

## Runtime topology

Use the existing workspace `/home/stefan/Projekte/3d_models` on `main` as the
coordinator and integration workspace. Keep coordination in the current session;
do not replace it with a new coordinator checkout. Background supervision needs
a running coordinator session. The integration workspace must be clean and
synchronized before merging. Put each delegated write-capable product lead in
a dedicated Orca feature worktree with one explicitly assigned `products/**`
subtree.

| Actor | Write authority | Responsibility |
|---|---|---|
| Coordinator | product creation and main-only edits here on `main`, Orca state, integration, and assignment cleanup | route work, supervise workers, resolve gates, merge/push validated branches, close completed workspaces and delete merged branches |
| Design lead | one named product/phase subtree in one feature worktree | requirements, architecture, CAD/mesh, evidence, feature-branch commit and push |
| Reviewer | read-only | independent geometry, interface, validation, or risk review |
| Human owner | human ledger and external actions | physical print/test, appearance, safety, final/commercial approval |

Do not dispatch two write-capable workers concurrently in the same checkout.
Write-capable leads may run concurrently only in separate feature worktrees
with disjoint product subtrees. Read-only work may run concurrently after the
lead in that worktree has produced an immutable candidate or explicitly paused.
Paths outside the assigned `products/**` subtree, especially `business/**`,
`tools/**`, and root-level agent configuration, remain main-only.

## Route intake and create product workspaces

1. Classify the assignment before creating any Orca workspace. New product
   creation and main-only activities run directly in the existing `main`
   workspace. For a new product, check existing identities, create its product
   folder and initial records, and update relevant portfolio/business records
   here. Review, commit, and push these scoped changes before dispatching its
   subsequent development. Do not create a branch just to register a product,
   edit business data, or change a skill.
2. Direct product work may remain here on `main` when no separate worker is
   needed. For delegated development of an existing/just-created product,
   fetch the latest `origin/main` and use the version-matched Orca CLI's
   `worktree create` with the exact repository, a unique assignment name, and
   `--no-parent --base-branch origin/main` for independent product assignments.
   Lineage and Git base are separate settings; use explicit parent lineage only
   for an assigned dependent workspace. The new worktree gets its own feature branch;
   never check out `main` in a second worktree. Use Orca's workspace operations
   rather than creating an untracked checkout with raw `git worktree add`.
3. Prefer agent-first creation with `--agent codex --prompt ... --json`. The
   initial prompt establishes ownership and tells the worker to await its
   tracked dispatch before editing. Use the returned full worktree ID and
   `startupTerminal.handle`; discover the worker handle with `terminal list`
   if absent. Verify branch, base, clean state, and path scope, then wait for
   `terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json`
   before dispatch so the task reaches a ready agent.
   Do not launch a second agent for the same worktree or send the assignment
   twice. Read the installed guide for supported flags and orchestration setup.
4. Record the product path, assignment/task ID, base commit, feature branch,
   remote branch, complete Orca worktree ID/path, worker terminal handle, and
   coordinator identity. Resolve the current session's coordinator handle
   before dispatch; use explicit handles for messaging and inbox checks when
   this shell cannot infer them. Never borrow an unrelated terminal's identity.
   Route any main-only dependency back here and handle
   it as a scoped, serialized `main` task. Keep this coordinator active to
   receive results and steering rather than ending with a handoff.

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
integration_owner: coordinator in /home/stefan/Projekte/3d_models on main
closeout: coordinator verifies, merges, pushes, and cleans this assignment's branches/workspace
```

Use a manual coordinator loop (`task-create`, worker terminal, `dispatch
--inject`, rolling `check --wait`) when human steering may be needed. An
automatic Orca coordinator run is acceptable only when the same boundaries are
present in its spec and `--worktree` targets the assigned product worktree.

Use rolling waits of at most 60 seconds and retain user steering between waits.
A timeout or empty inbox is a checkpoint, not a reason to redispatch or restart
a worker. Reacquire a stale worker handle through `terminal list` for the exact
recorded worktree; use only its replacement. Match lifecycle messages to the
recorded task, dispatch, and worker. `worker_done` may report failure: inspect
its result and evidence before treating the assignment as merge-ready. A valid
completion already closes its Orca task; do not duplicate that state transition.

## Integrate and clean up each completed product assignment

The workspace owner has assigned routine integration and cleanup to this
coordinator. Execute this sequence without a new permission question once the
assignment meets its acceptance criteria. It is not a portfolio-wide cleanup
instruction and does not authorize merging incomplete work or bypassing a
required human design decision.

1. **Freeze the candidate.** Require `worker_done`, the scoped diff, validation
   evidence/ledger state for the permitted digital target, and the exact pushed
   feature commit. Confirm no further writes are active. Preserve the final
   worker report and required artifacts in the owning product subtree so they
   survive workspace removal; include them in the reviewed, pushed candidate.
2. **Prepare this main workspace.** Fetch and synchronize `main` with
   `origin/main` non-destructively. Require a clean index/worktree and exclusive
   integration ownership. Commit/push only completed coordinator-owned work;
   preserve unrelated dirty files. If they prevent a clean merge, report the
   concrete blocker and retain the candidate. Never stash, reset, or relocate
   user changes to force integration, or move main-only work elsewhere.
3. **Recheck and merge serially.** Verify the complete branch delta since its
   merge base and its intended merge changes are inside the assigned product
   subtree. Check candidate identity and evidence freshness against current
   `main`. Merge one validated branch at a time while preserving its commits;
   do not squash/rewrite the candidate or `main`. Resolve only unambiguous
   conflicts within the authorized scope; send design ambiguity or invalidated
   evidence back for scoped rework. Re-run required checks affected by the
   integration before pushing.
4. **Push and prove integration.** Push `main` to `origin/main`, fetch, and
   verify the reviewed feature tip is an ancestor of `origin/main`. A rejected
   push is not integration: synchronize and recheck before retrying. Keep the
   feature branch/workspace until the remote ancestry check succeeds.
5. **Close the assignment in Orca.** Record the feature tip, integration commit,
   validation result, and any remaining human gate in the durable product
   report and push that record before deletion. Complete the tracked task/run
   using the installed orchestration guide, respecting already completed tasks;
   update the recorded product workspace's status by full ID, and
   close only this assignment's worker/reviewer terminals after verifying they
   have no running work. Keep the coordinator terminal and main workspace open.
6. **Remove only verified, disposable resources.** Recheck exact branch tips,
   worktree ownership, dependents, and tracked, untracked, and ignored files.
   Preserve required local-only artifacts before removal; retain resources
   needed by active tasks or child worktrees. Use Orca `worktree rm` with its
   installed safe options for the recorded worktree ID; never use force removal
   to bypass dirty state. Delete only the assignment's fully integrated remote
   branch and local branch (use Git's merged-branch check, `git branch -d`, if
   Orca has not removed it). Never delete `main`, default/protected branches,
   unrelated branches, or a branch whose tip has advanced beyond integration.
7. **Verify closure.** Check Orca's workspace/terminal inventory, Git worktrees,
   local refs, and the remote branch ref. If a resource is absent already,
   continue idempotently. If deletion fails, report integrated with cleanup
   pending, retain the exact remaining resource IDs, and retry only after its
   blocker is resolved. Report fully closed only after all assignment resources
   are gone. Do not wait for another product to finish before closing this one.

For work performed entirely here on `main`, review and push its scoped commit
and complete its tracking entry; there is no temporary branch/workspace to
delete. Physical print, appearance, and commercial decisions remain separate
human gates even when the digital assignment is integrated and closed.

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
