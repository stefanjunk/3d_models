# Validation architecture

## Responsibility boundary

```text
user + design skill
  -> project-scoped autonomy policy
  -> structured requirements and thresholds
  -> deterministic build/export
  -> deterministic validation commands
  -> immutable JSON reports tied to input hashes
  -> aggregate gate
  -> hash-chained agent decision through the allowed boundary
  -> separate human/physical review after that boundary
```

The language model may recommend a threshold, but the project contract must record its source and approval before a release run. The language model may explain a report, but it cannot change the report status.

## Shared report contract

Every command emits:

- `schema_version`;
- `tool` and `tool_version`;
- `status`;
- exact input paths and SHA-256 values;
- executed checks with stable IDs, status, required flag, message, and metrics;
- limitations and required capabilities;
- deterministic settings such as sample count and random seed.

Do not include wall-clock timestamps in canonical reports. Record run time in CI metadata when needed so identical inputs can produce comparable JSON.

## Fail-closed rules

1. A malformed input is `FAIL`.
2. A missing optional backend is `NOT_RUN`, not `PASS`.
3. A required `NOT_RUN` blocks release.
4. A visual, legal, safety, or physical decision that scripts cannot resolve is `REVIEW_REQUIRED`.
5. A referenced external report must exist, match its expected input hashes, and contain an accepted status.
6. A changed source or artifact hash makes an earlier report stale.
7. Geometry normalization is diagnostic. Preserve raw statistics and never overwrite the input.

## CI sequence

1. `doctor`
2. schema and artifact-hash validation
3. parameterized source generation
4. mesh and interface validation
5. regression comparison against approved masters
6. exact slicer export and G-code analysis
7. physical/review evidence registration
8. stage-ledger validation
9. aggregate release gate

Use exit codes rather than parsing prose.

For a 130k local-model context, execute the scripts outside the prompt. Return only the active stage definition, failed checks, aggregate metrics, and `stage_state`; keep source code, full logs, and complete ledgers out of the model context.
