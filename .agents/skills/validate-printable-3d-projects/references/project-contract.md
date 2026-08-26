# Validation project contract

## Top-level fields

- `schema_version`: currently `1.0`.
- `project`: ID, revision, units, risk class, and optional build volume.
- `artifacts`: immutable inputs and outputs addressed by ID.
- `checks`: built-in validators or external evidence reports.
- `release`: approval and review requirements.

Project autonomy is stored in a separate `autonomy-policy.json`; approval provenance is stored in separate agent and human ledgers. Register them as artifacts when an `approvals` check is part of the project.

## Artifacts

Every artifact needs:

- a unique `id`;
- a project-relative `path`;
- a semantic `kind` such as `mesh`, `3mf`, `gcode`, `report`, `source`, or `image`;
- optionally an expected `sha256` and `revision`.

When `sha256` is present, any mismatch fails before downstream checks run.

In a `release` run, every required artifact must declare `sha256`. Use `freeze-project` to create a separate locked contract beside the editable source contract; review the diff before treating it as approved.

## Check types

### `mesh`

References one mesh artifact and embeds a mesh policy. Use exact expected body counts, topology requirements, bed dimensions, and complexity limits.

### `mesh_compare`

References master and candidate artifacts. Declare seeded sample count and physical error/volume/bounds thresholds.

At least one acceptance threshold is mandatory for a release decision. Indexed triangle distance is required by default in the release profile; a nearest-vertex fallback remains diagnostic.

### `gcode`

References final slicer G-code. Declare tool-change, bed-bound, extrusion, and flow limits when meaningful.

Arc moves and volumetric extrusion are surfaced explicitly. If they make a declared bounds/flow/extrusion assertion incomplete, that assertion is `NOT_RUN`.

### `3mf`

References a 3MF artifact. Set whether each mesh object must be watertight and positively oriented.

For manufacturing release, start from `assets/policies/fdm-release-3mf.json`. Structural ZIP/XML validity alone is not a printability proof.

### `interfaces`

References an interface contract JSON containing part paths and pairwise or motion checks.

Translation motion checks are discretized. They return `REVIEW_REQUIRED` unless the contract explicitly accepts the declared step resolution; preserve a physical fit/motion gate for critical assemblies.

### `external_report`

References a report artifact produced by another specialist script. Provide `expected_inputs` as artifact IDs. The aggregate gate verifies report input hashes.

### `physical` or `review`

Records evidence that cannot be generated automatically. Until `status` is explicitly `PASS` with an evidence artifact, it remains `REVIEW_REQUIRED`.

### `approvals`

References `policy_artifact`, `agent_ledger_artifact`, an optional `human_ledger_artifact`, and `target_stage`. The aggregate check verifies the policy hash, evidence freshness, event chains, actor/decision consistency, and all stages through the target. A later human target may also name `human_secret_path`; never register or package that secret as an artifact.

The legacy `release.required_approvals` map remains available for simple manually maintained contracts. Use `approvals` ledgers when the system must prove whether the agent or a human approved each workflow stage.

## Profiles

`draft` permits required `REVIEW_REQUIRED` and `NOT_RUN` to remain visible without labelling the model release-ready. `release` blocks both. `FAIL` always blocks.
