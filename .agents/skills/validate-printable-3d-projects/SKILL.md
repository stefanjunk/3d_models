---
name: validate-printable-3d-projects
description: Validate, regression-test, gate, and package FDM/FFF CAD, mesh, 3MF, G-code, multicolor, relief, texture, interface, motion, and mold artifacts with deterministic scripts and machine-readable evidence. Use when a printable 3D project needs fail-closed checks, artifact freshness, parameter sweeps, slicer/G-code metrics, OpenCode portability checks, or a single release decision across multiple 3D-design skills.
---

# Validate Printable 3D Projects

Make scripts—not model prose—the authority for measurable acceptance.

Use this skill beside the specialist 3D-design skills. Let those skills define design intent and domain-specific thresholds; use this skill to execute checks, join evidence to exact artifact hashes, and issue a deterministic gate result.

## Core contract

1. Create `validation-project.json` from `assets/validation-project.template.json`.
2. Record immutable artifact paths, roles, revisions, and expected hashes.
3. Declare every required check with explicit thresholds and `required: true`.
4. Run checks through `scripts/fdm_ci.py`; do not rewrite validation code inside a product project.
5. Treat `PASS`, `FAIL`, `NOT_RUN`, and `REVIEW_REQUIRED` as distinct states.
6. A required `NOT_RUN` or `REVIEW_REQUIRED` blocks a release profile.
7. Never convert a warning, render, successful import, or model assertion into a pass without executing the associated check.

## Autonomy contract

At project start, create and validate `autonomy-policy.json`. For unattended development, bind the policy to the validated current preflight with `init-autonomy --preflight ...`. The command derives a maximum autonomy ceiling: Lane A/B with K0-K1 and R3+ may use `autonomous-to-print-candidate`; Lane C or K2 is limited to `guided`; Lane D/K3 and every hold, gate failure, R0-R2, Lane E, or K4 case is limited to `manual`. Physical printing, fit/function, appearance, safety, and commercial release stay human-controlled.

Keep `agent-approvals.json` and `human-approvals.json` separate. The agent command derives `AUTO_APPROVED` or `BLOCKED` and refuses human stages. A human approval is recorded through a frozen request and, by default, a verifier-selected HMAC key kept outside agent-readable paths. Read `references/autonomy-and-approvals.md` before enabling stage auto approval.

The `concept` stage is never evidence-free. Whether its assigned authority is
an agent or a human, its approval evidence must include the existing
product-concept image itself so the ledger binds its SHA-256. Auto approval can
review that image but cannot replace it with an attestation or a Step1X source
plate.

Workflow autonomy never expands OpenCode, shell, network, upload, or printer permissions. The default policy denies printer upload/start and destructive overwrite.

## Quick start

Resolve this skill directory and run:

```bash
python3 scripts/fdm_ci.py doctor --json-out reports/environment.json
python3 scripts/fdm_ci.py slice-anycubic-next model.stl build/anycubic-slice \
  --machine-profile printer.json --process-profile process.json \
  --filament-profile filament.json --json-out reports/anycubic-slice.json
python3 scripts/fdm_ci.py init-autonomy example-part autonomy-policy.json \
  --mode autonomous-to-print-candidate --authorized-by project-owner \
  --preflight preflight/preflight-result.json
python3 scripts/fdm_ci.py validate-project validation-project.json \
  --profile draft --json-out reports/validation-summary.json
python3 scripts/fdm_ci.py validate-p2-stage p2-stage/p2-manifest.json \
  --json-out p2-stage/p2-validation.json
```

For release:

```bash
python3 scripts/fdm_ci.py freeze-project \
  validation-project.json validation-project.lock.json
python3 scripts/fdm_ci.py validate-project validation-project.lock.json \
  --profile release --json-out reports/release-summary.json
```

`freeze-project` writes a separate file and refuses to overwrite the source. The CLI returns non-zero for `FAIL`, for missing required capabilities, and for release-blocking review items.

## Available deterministic commands

- `doctor`: report Python modules, executable backends, versions, and capability groups.
- `audit-mesh`: topology, dimensions, components, bed fit, complexity, and optional sampled wall thickness.
- `compare-meshes`: seeded bidirectional surface-distance, bounds, and volume regression.
- `check-interfaces`: exact or conservative overlap, separation, and motion-sweep checks from a contract.
- `analyze-gcode`: layers, tools, extrusion, bounds, approximate time and peak flow from local G-code.
- `slice-anycubic-next`: isolated local Anycubic Slicer Next CLI export with exact source/profile/binary/output hashes, native-result checks, and G-code analysis; no upload/start capability.
- `validate-3mf`: package/XML/reference/material/mesh structure.
- `author-anycubic-3mf`: non-overwriting local destination-slicer project
  authoring from the complete set of already oriented sources and exact
  machine/process/filament profiles; verifies the embedded support switch.
- `validate-p2-stage`: fail-closed lifecycle check for the revision-bound
  English description, whole-product concept image, current-model render, and
  complete oriented/support-planned 3MF print set.
- `run-sweep`: deterministic default/min/max/pairwise parameter execution with artifact checks.
- `validate-skill`: OpenCode/portable layout, references, Python AST syntax, and dependency declaration checks without writing into the installed skill.
- `validate-profile`: validate a companion skill's artifact roles, check declarations, manual gates, and fail-closed release policy.
- `init-autonomy`: generate a project-scoped `manual`, `guided`, `autonomous-to-print-candidate`, or `custom` policy.
- `validate-autonomy`: validate stage authority, fail-closed evidence rules, and tool boundaries.
- `approve-agent-stage`: derive and hash-chain `AUTO_APPROVED` or `BLOCKED`; never write human approval.
- `request-human-approval`: freeze a human-stage request and evidence hashes.
- `approve-human-stage`: write the separate human ledger with manual assertion or HMAC proof.
- `validate-approvals`: verify chain integrity, actors, policy/evidence hashes, proof, and stage completion.
- `freeze-project`: write a separate JSON contract with current artifact SHA-256 hashes; never overwrite the source contract.
- `validate-project`: execute and aggregate declared checks, hashes, approvals, external reports, and physical-review gates.

Run `python3 scripts/fdm_ci.py COMMAND --help` for exact inputs.

Use `assets/policies/` as editable starting points, not universal printer values. A release comparison without an explicit acceptance threshold returns `REVIEW_REQUIRED`. Required exact geometry checks return `NOT_RUN` when only an approximate backend is available.

## Status semantics

| Status | Meaning | Release behavior |
|---|---|---|
| `PASS` | Executed and inside threshold | allowed |
| `FAIL` | Executed and outside threshold or invalid input | blocked |
| `NOT_RUN` | Backend/evidence unavailable | blocked when required |
| `REVIEW_REQUIRED` | Numerical automation cannot decide | blocked when required |

Do not use an overall score. One failed protected constraint blocks the candidate.

## Companion routing

- `functional-3d-design`: owns requirements, risk, interfaces, materials, and physical-test strategy.
- `decompose-printable-designs`: owns component authority and interface contracts.
- `organic-mesh-functionalization`: owns protected ROI and source-preservation tolerances.
- `reconstruct-printable-3d-from-images`: owns evidence, camera, silhouettes, and visual thresholds.
- `parametric-freeform-surfacing`: owns continuity, fairness, hardpoints, and parameter ranges.
- `multicolor-fdm-design`: owns color bodies, palette, purge limits, and final slicer mapping.
- `design-printable-surface-textures`: owns texture representation, mapping scale, seams, and coupons.
- `3d-print-heightmap-relief`: owns heightmap scale, relief metrics, and mesh budgets.
- `optimize-fdm-design`: owns baseline/candidate design and protected constraints.
- `casting-negative-molds`: owns pull vectors, parting, shrinkage, and casting-process gates.
- `commercialize-3d-models`: owns commercial evidence and legal/safety approval routing.

## Required reading

- Read `references/project-contract.md` when creating or editing the validation manifest.
- Read `references/validation-architecture.md` when integrating another skill or CI system.
- Read `references/opencode-runtime.md` for installation, dependency, and read-only portability.
- Read `references/anycubic-slicer-next.md` before using the Anycubic Slicer Next CLI adapter or comparing its G-code across runs.
- Read `references/autonomy-and-approvals.md` before selecting autonomy or recording an approval.

## Safety boundary

Automated geometry and manufacturing checks do not certify strength, safety, food contact, electrical suitability, legal clearance, or product compliance. Preserve physical and qualified-human review gates for consequence-critical work.
