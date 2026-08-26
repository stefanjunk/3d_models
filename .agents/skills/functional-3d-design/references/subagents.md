# Subagent and model routing

## Why delegate

Delegation should reduce cost/context and improve parallelism without transferring unreviewed engineering authority.

## Fast subagent tasks

Good bounded tasks:

- classify tool/material/nozzle choices from an explicit spec;
- search a known parts library;
- extract dimensions from a supplier table;
- run one deterministic script and summarize output;
- add a single parameter or assertion;
- generate a small test matrix;
- compare two mesh validation reports;
- inspect upstream API documentation.

Return a structured result with assumptions, inputs, outputs, and files touched.

## Capable/frontier agent tasks

Keep with the primary agent:

- incomplete requirements and architecture;
- load-path and failure-mode analysis;
- cross-tool CAD/mesh decisions;
- final print-vs-buy decision;
- safety and standards interpretation;
- simulation fidelity and boundary conditions;
- final validation and release.

## GPT-5.3-Codex-Spark example

The package includes `config-examples/cad-microtask-spark.md` with:

```yaml
model: openai/gpt-5.3-codex-spark
```

Use only if that provider/model ID is available. Spark is optimized for rapid targeted coding iterations and uses a lightweight default work style; explicitly tell it to run the relevant check. Do not use it as the only reviewer for a long, ambiguous mechanical design.

## Context isolation

OpenCode custom commands can set `subtask: true`. The included review and microtask commands create child sessions, keeping raw exploration and routine calculations out of the primary design context.

## Recommended task envelope

A fast task should normally have:

- one objective;
- no more than a few files;
- explicit acceptance command;
- no unresolved safety decision;
- a compact output schema.
