---
name: orca-3d-coordinator
description: Coordinate Metricreate 3D product work from the existing main workspace using the Stably AI Orca CLI, keeping product creation and main-only work local, dispatching isolated product development, and automatically merging and cleaning up completed branches. Use when starting, supervising, steering, pausing, resuming, or completing Codex-driven product workflows in Orca. Do not use for ordinary single-agent CAD work that needs no Orca coordination.
metadata:
  version: 1.1.0
---

# Orca 3D Coordinator

Coordinate from the existing `main` workspace at
`/home/stefan/Projekte/3d_models`. Create new products and perform main-only
activities here. Use the Stably AI Orca CLI for separate product-development
workspaces and their supervision. The coordinator is the assigned integration
owner: after each completed product assignment, integrate its validated work
into `main`, push, then close and clean up its temporary branches and workspaces
without asking for routine merge or cleanup confirmation.

## Load current authority before acting

1. Read the root `AGENTS.md`, confirm the active branch and worktree match the
   assigned path scope, and synchronize non-destructively before any design
   edit. Protected-path work must use `main`; product feature work must use a
   branch based on current `origin/main` and stay inside its assigned subtree.
2. On Linux outside an Orca-managed terminal use `orca-ide`; inside Orca use
   the exported Orca command. Confirm `status --json`.
3. Load the version-matched guides with `skills get orchestration --full` and
   `skills get orca-cli --full`; do not invent Orca flags from memory.
4. For design work, read the applicable 3D skill, mandatory
   `3d-design-preflight`, and `validate-printable-3d-projects` instructions.
   Main-only business or skill maintenance uses its applicable workflow;
   it does not need a product preflight merely because it is coordinated here.

Read [references/operating-contract.md](references/operating-contract.md) before
creating an Orca Run, task DAG, coordinator loop, or scheduled automation.

## Non-negotiable coordination boundaries

- New product creation (identity, product folder, initial documentation, and
  associated portfolio/business registration) happens directly in this `main`
  workspace. Commit and push that creation before branching for subsequent
  delegated product development. Product work that needs no separate worker
  may continue here on `main`.
- Perform all main-only work, including `business/**`, `tools/**`, and skills or
  agent configuration, directly here on `main`. Do not create a separate
  workspace for it; serialize local writes with integration work.
- Create feature branches and Orca/Git worktrees only for explicitly assigned
  development of an existing product under `products/**`. Use the Orca CLI to
  create and manage these workspaces. Never change protected main-only paths
  from a product branch.
- Keep exactly one write-capable design lead per worktree and branch. Multiple
  leads may run concurrently only in separate worktrees with disjoint product
  subtrees; reviewers in an active lead's worktree are read-only.
- The coordinator owns local intake/main-only work, Orca task state, decisions,
  serialized integration, and cleanup. In a delegated assignment, its design
  lead owns product geometry and the feature-branch commit/push; the coordinator
  does not edit that product concurrently.
- Require a schema `1.1` `autonomy-policy.json` bound to the current preflight
  before unattended design. Legacy policies require explicit reauthorization.
- Obey the preflight ceiling: autonomous only for eligible Lane A/B work,
  guided for Lane C/K2, human-led for Lane D/K3, and hold restricted work.
- Never upload to or start a printer. Physical print, fit/function, appearance,
  safety, watermark/final release, publication, and commercial release remain
  human-controlled.
- Preserve dirty user files. Stop if upstream synchronization, path isolation,
  or single-writer-per-worktree ownership cannot be established safely.

## Coordinator behavior

Use Orca Orchestration tasks and dispatches for tracked work. Prefer a shallow
DAG with explicit dependencies:

`preflight -> requirements/concept -> design lead -> read-only review -> deterministic validation -> print candidate -> human gate`

Route intake using the operating contract before creating any workspace. For
delegated product work, create a dedicated Orca feature worktree based on current
`origin/main`, start one design lead, and include the exact allowed `products/**`
subtree in its task. Retain coordinator ownership here and supervise the worker
through Orca tasks/messages; this is supervised coordination, not a full handoff.
Never dispatch two writers to the same checkout. Keep protected-path updates
and branch integration in separate, serialized tasks here on `main`.

At each meaningful transition update the affected product's Orca worktree
comment using its recorded full worktree ID, with the product, stage, result,
and next gate. Do not use `active` from this coordinator to select a worker's
workspace. Create a `decision_gate` only when the
policy assigns the decision to a human or a consequential unknown prevents safe
progress. Do not interrupt the agent merely to report routine progress.

Human steering changes the active task specification. Send the instruction to
the design lead, record it in the product decision log, mark affected evidence
stale, and repeat only the invalidated stages. A stop or pause request takes
priority over new dispatches.

Use Orca Automations only for scheduled intake or read-only health reviews.
They may create or wake the coordinator, but they must not independently start
design edits, create worktrees, approve human stages, upload artifacts, or start
a printer.

## Completion

A coordinated product feature phase is merge-ready only when the worker reports
`worker_done`, required deterministic checks pass, the approval ledgers validate
through the permitted target, the diff contains only the assigned product
subtree, and the phase commit is pushed to its remote feature branch. Merge-ready
is an intermediate state: the coordinator must execute the operating contract's
integration and cleanup sequence after each completed product assignment. Work
is integrated only after its commit is verified on `origin/main`; cleanup is
complete only after the assignment's temporary Orca workspace and merged local
and remote branches are gone. Preserve blocked or still-needed work and report
the exact remaining step. A main-only phase remains complete only after its
commit is pushed to `origin/main`. Report the actual model state and next human
gate; Git integration does not constitute physical or commercial approval.
