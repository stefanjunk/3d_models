# Autonomy and approval provenance

Choose workflow autonomy before the agent creates or changes project artifacts. The policy is project-scoped, hash-bound, and separate from OpenCode or operating-system tool permissions. For unattended coordination, create schema `1.1` by binding the policy to the validated current preflight. Schema `1.0` policies remain compatible for existing ledgers but are not sufficient for a new unattended Orca run.

## Modes

| Mode | Agent authority | Human boundary |
|---|---|---|
| `manual` | no stage approval | every stage |
| `guided` | parametric source through slicer preflight | requirements, concept, print candidate, and later stages |
| `autonomous-to-print-candidate` | requirements through a deterministically checked print candidate | physical print and every later stage |
| `custom` | only stages explicitly edited to `agent` | every remaining stage |

The preflight supplies a hard ceiling, independent of the requested mode:

| Preflight result | Maximum mode |
|---|---|
| Lane A/B, K0-K1, R3+, no failed gate, `GO`/`GO_WITH_CONTROLS` | `autonomous-to-print-candidate` |
| Lane C or K2 with R3+ and no failed gate | `guided` |
| Lane D, K3, R0-R2, any failed gate, `HOLD`, `CONCEPT_ONLY`, Lane E, or K4 | `manual` |

Requesting a more permissive mode fails without writing a policy.

Generate the initial policy rather than asking a model to recreate its structure:

```bash
python3 scripts/fdm_ci.py init-autonomy example-part autonomy-policy.json \
  --mode autonomous-to-print-candidate --authorized-by project-owner \
  --preflight preflight/preflight-result.json
python3 scripts/fdm_ci.py validate-autonomy autonomy-policy.json
```

`--authorized-by` records the human who selected the mode and delegated only the declared workflow stages. The bound policy stores the preflight path, assessment identity, risk classification, autonomy ceiling, and exact SHA-256. A changed or replaced preflight therefore blocks policy validation until the owner deliberately creates and authorizes a new policy. `init-autonomy` refuses to overwrite an existing policy unless the caller explicitly supplies `--force`. After the first ledger event, changing the policy invalidates the ledgers because every ledger and event names the policy and its SHA-256.

## Standard stage boundary

The standard sequence is:

1. `requirements-normalization`
2. `concept`
3. `decomposition`
4. `parametric-source`
5. `mesh-generation`
6. `interface-validation`
7. `slicer-preflight`
8. `print-candidate`
9. `physical-print`
10. `fit-and-function`
11. `appearance`
12. `safety`
13. `commercial-release`

The autonomous print-candidate mode assigns stages 1–8 to the agent and stages 9–13 to humans. The agent may generate local CAD, meshes, 3MF, G-code, previews, and reports. It may not infer that a physical print occurred, approve safety or legal claims, upload to a printer, or start a printer.

## Agent decisions

Use `agent-approvals.json` only for agent events. Early semantic stages require an explicit attestation. The `concept` stage additionally requires the versioned whole-product concept image as evidence; the command hashes the file into the ledger and blocks when no supported image is supplied. Technical stages require one or more JSON validation reports with overall `PASS`, no non-PASS required checks, and SHA-256-bound inputs.

```bash
python3 scripts/fdm_ci.py approve-agent-stage \
  autonomy-policy.json validation/agent-approvals.json concept \
  --agent-id opencode-agent-1 --model-id local-27b \
  --evidence concept/concept-product-v0.1.0-r1.png \
  --attestation "Concept satisfies the normalized requirements contract"

python3 scripts/fdm_ci.py approve-agent-stage \
  autonomy-policy.json validation/agent-approvals.json print-candidate \
  --agent-id opencode-agent-1 --model-id local-27b \
  --evidence validation/mesh-report.json \
  --evidence validation/interface-report.json \
  --evidence validation/gcode-report.json
```

The command derives the result. It does not accept a requested decision:

- `AUTO_APPROVED`: the policy assigns the stage to the agent and every required condition passed;
- `BLOCKED`: a prior stage, report, input hash, backend, or required check is missing or non-PASS.

A blocked attempt is retained in the hash chain. A later corrected attempt adds a new event; it does not rewrite history. The agent command refuses human stages without changing the ledger.

## Human decisions

Human approvals use `human-approvals.json`, a separate command, and a frozen request containing evidence hashes. The agent may prepare the request; the user executes the approval command manually.

```bash
python3 scripts/fdm_ci.py request-human-approval \
  autonomy-policy.json physical-print example-part \
  validation/physical-print-request.json \
  --evidence tests/physical-print-observation.pdf
```

The default policy requires HMAC proof. Create and keep the secret outside every directory and environment readable by the agent. Run the following approval manually, not through the agent:

```bash
python3 scripts/fdm_ci.py approve-human-stage \
  autonomy-policy.json validation/physical-print-request.json \
  validation/human-approvals.json \
  --human-id operator-name \
  --agent-ledger validation/agent-approvals.json \
  --secret-file /user-controlled/location/fdm-approval.key \
  --key-id operator-key-1
```

For environments where cryptographic separation is impossible, set `human_approval_proof` to `manual-assertion`. This records who asserted the decision but does not prove that an agent could not have invoked the command. HMAC proves possession of the verifier-selected secret, not a legal identity. If the agent can read the secret, it is not a trustworthy human boundary.

## Validation and project integration

Validate all events and every stage through a chosen boundary:

```bash
python3 scripts/fdm_ci.py validate-approvals \
  autonomy-policy.json validation/agent-approvals.json \
  --target-stage print-candidate

python3 scripts/fdm_ci.py validate-approvals \
  autonomy-policy.json validation/agent-approvals.json \
  --human-ledger validation/human-approvals.json \
  --human-secret-file /user-controlled/location/fdm-approval.key \
  --target-stage physical-print
```

The `approvals` check type can embed the first command in `validation-project.json`. The template does so for `print-candidate`. Add the human ledger and verifier secret only to a later, manually run validation contract. Never register the secret itself as a project artifact or copy it into the downloadable project package.

Each event records:

- stage and derived decision;
- `decided_by.type` (`agent` or `human`), ID, and model ID where applicable;
- authority and current policy hash;
- evidence paths and SHA-256 values;
- previous event ID and event ID;
- reasons for a blocked attempt;
- optional human proof.

`validate-approvals` recomputes event IDs, chain links, authority, evidence hashes, stage order, actor/decision consistency, and required signatures. Feed a local model the aggregate report and `metrics.stage_state`, not the full ledger or script source.

## Workflow approval is not system permission

The policy's `tool_policy` is a declared workflow boundary. It cannot override OpenCode permissions, sandboxing, operating-system access, or printer controls. Configure those independently in the host runtime.

For autonomous print-candidate work, the template permits local workspace writes and local build/export/test commands. Network access, dependency installation, destructive overwrites, and external uploads remain `ask` or `deny`; printer upload and printer start are denied. If the host runtime is more restrictive, the host wins. If it is more permissive, the agent must still obey the project policy.

Never use a global “approve everything” switch for printer start, credential access, arbitrary package installation, deletion, or external publication. Those actions are not required to reach a local print candidate.
