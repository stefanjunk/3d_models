---
name: orca-3d-coordinator
description: Coordinate supervised autonomous Metricreate 3D-design work through Orca Runs, tasks, Codex terminals, validation gates, and human interventions while preserving the repository's main-only policy. Use when starting, supervising, steering, pausing, or resuming one or more Codex-driven 3D product workflows in Orca. Do not use for ordinary single-agent CAD work that needs no Orca coordination.
---

# Orca 3D Coordinator

Coordinate one accountable Codex design lead and bounded read-only reviewers so
a product can progress autonomously to its permitted digital gate while the
human can monitor, steer, interrupt, or approve it in Orca.

## Load current authority before acting

1. Read the root `AGENTS.md`, confirm branch `main` tracks `origin/main`, and
   synchronize non-destructively before any design edit.
2. On Linux outside an Orca-managed terminal use `orca-ide`; inside Orca use
   the exported Orca command. Confirm `status --json`.
3. Load the version-matched guides with `skills get orchestration --full` and
   `skills get orca-cli --full`; do not invent Orca flags from memory.
4. Read the applicable 3D skill, mandatory `3d-design-preflight`, and
   `validate-printable-3d-projects` instructions.

Read [references/operating-contract.md](references/operating-contract.md) before
creating an Orca Run, task DAG, coordinator loop, or scheduled automation.

## Non-negotiable coordination boundaries

- Never create an Orca/Git worktree or non-`main` branch in this repository.
- Keep exactly one write-capable design lead active. Reviewers and calculators
  are read-only or receive one explicitly disjoint file scope.
- The coordinator owns Orca task state and decisions, not product geometry. The
  design lead owns product-file edits and the phase commit/push.
- Require a schema `1.1` `autonomy-policy.json` bound to the current preflight
  before unattended design. Legacy policies require explicit reauthorization.
- Obey the preflight ceiling: autonomous only for eligible Lane A/B work,
  guided for Lane C/K2, human-led for Lane D/K3, and hold restricted work.
- Never upload to or start a printer. Physical print, fit/function, appearance,
  safety, watermark/final release, publication, and commercial release remain
  human-controlled.
- Preserve dirty user files. Stop if upstream synchronization or single-writer
  ownership cannot be established safely.

## Coordinator behavior

Use Orca Orchestration tasks and dispatches for tracked work. Prefer a shallow
DAG with explicit dependencies:

`preflight -> requirements/concept -> design lead -> read-only review -> deterministic validation -> print candidate -> human gate`

At each meaningful transition update the active Orca worktree comment with the
product, stage, result, and next gate. Create a `decision_gate` only when the
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

A coordinated design phase is complete only when the worker reports
`worker_done`, required deterministic checks pass, the approval ledgers validate
through the permitted target, the diff contains only phase-owned files, and the
phase commit is pushed to `origin/main`. Report the actual model state and next
human gate; never describe a digital candidate as physically qualified.
