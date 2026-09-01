# Orca-supervised autonomous 3D coordination

## Decision

Metricreate uses a persistent Codex coordinator inside Orca. Orca
**Orchestration tasks** are the primary execution and monitoring unit. Orca
**Automations** are optional schedulers for read-only reviews or intake and are
not allowed to grant engineering authority.

The implementation deliberately does not use the Codex App Server.

## Operating model

```text
Human brief
    -> Orca coordinator
        -> preflight and risk ceiling
        -> one Codex design lead on main
        -> bounded read-only reviewers
        -> deterministic CAD/mesh/slicer validation
        -> digital print candidate
    -> human print, fit, appearance, safety and release gates
    -> measured feedback and scoped learning candidate
```

The design lead uses the workspace Codex configuration (`gpt-5.6-sol`,
`xhigh`). It may iterate without asking for routine choices when a schema `1.1`
autonomy policy assigns the stage to the agent. Orca keeps the task status,
terminal activity, diff, model artifacts, validation reports, and decision
gates observable.

## Preflight routing

| Result | Maximum delegation |
|---|---|
| Lane A/B, K0-K1, R3+, no failed gate | autonomous to digital print candidate |
| Lane C or K2 | guided; human requirements/concept and print-candidate decision |
| Lane D or K3 | expert-in-the-loop/manual approvals |
| Lane E, K4, R0-R2, failed gate, HOLD/CONCEPT_ONLY | hold or manual evidence acquisition only |

The policy generator binds the exact preflight SHA-256. Any later preflight
change makes validation fail until a new project revision and policy are
authorized. Existing schema `1.0` policies and their ledgers remain unchanged;
they must be migrated per product rather than rewritten globally.

## Initial pilot

`MM-PER-001 NameForm Bookends` is the first bound pilot. Its validated
`Lane C · R3 · K1 · GO_WITH_CONTROLS` preflight limits it to `guided`: the
agent may execute and validate source, mesh, interfaces, and slicer preflight,
while requirements, concept, print-candidate acceptance, physical testing, and
release remain human decisions.

## Orca rules

- Use the existing `main` workspace; never create Orca worktrees for this repo.
- One write-capable design lead at a time; reviewers are read-only.
- Use orchestration tasks/dispatches for supervised work and human gates.
- Use worktree comments for a one-line stage summary.
- Use Automations only with an existing workspace and initially disabled or
  read-only.
- Printer upload/start, external publication, and human ledger decisions are
  never delegated.

The executable agent contract is maintained in
`.agents/skills/orca-3d-coordinator/`.
