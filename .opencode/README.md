# 3D OpenCode Runtime

Start OpenCode with `/workspace/3d_models` as the project:

```bash
opencode /workspace/3d_models
```

The `3d-design` primary agent uses semantic worker roles. Model bindings are an
implementation detail and can be changed without rewriting routing prompts.

| Role | Model | Purpose |
|---|---|---|
| `3d-design` | `kilo/openai/gpt-5.6-luna` | Cheap orchestration, deterministic operations, user communication |
| `small-general` | `kilo/openai/gpt-5.6-luna` | Extraction, normalization, classification, concise evidence reports |
| `small-coding` | `openai/gpt-5.3-codex-spark` | Narrow, well-specified source changes and ordinary local repair |
| `medium-general` | `kilo/openai/gpt-5.6-terra` | Method choice, acceptance criteria, diagnosis, manufacturing tradeoffs |
| `medium-coding` | `kilo/qwen/qwen3.6-27b` | Normal CadQuery, OpenSCAD, implicit, mesh, and Python implementation |
| `frontier` | `kilo/openai/gpt-5.6-sol` | Escalation-only architecture and structural failure analysis |

Workers are flat: they cannot launch more workers. Only `3d-design` may ask
the user questions. The root-level legacy agent at
`/workspace/.opencode/agent/3d-design-agent.md` remains unchanged as a fallback
when OpenCode is started from `/workspace`.

Configuration-time files are loaded once. Quit and restart OpenCode after
changing `opencode.json`, an agent, or the shared policy.

If the operating system reports `inotify_add_watch ... No space left on
device` while opening this large repository, launch the session with:

```bash
OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER=1 opencode /workspace/3d_models
```

This disables OpenCode's experimental whole-repository watcher for that
process; it does not change model files.

## Escalation

```text
small -> medium -> frontier
```

Frontier is not a default planner. The coding retry budget is one same-tier
ordinary repair. A second equivalent failure goes to `medium-general` for
diagnosis; only a structural or representational problem goes to `frontier`.

## Commercial Product Flow

Commercial products start from `.opencode/templates/commercial-product/` and
must pass these gates before detailed CAD:

```text
COMMERCIAL_LICENSE_PASS
        +
ENGINEERING_DECISION_PASS
        |
        v
CAD -> assembly -> dimensions -> mesh -> FDM -> slicer -> coupons -> release
```

The production allowlist accepts permissive licenses and CC-BY with complete
automatic attribution. Copyleft, Share-Alike, Non-Commercial, No-Derivatives,
unknown, and asset-level unverified sources are blocked. The repository-level
license of an asset catalog is not sufficient.

The generic FDM target classes are 0.4, 0.6, and 0.8 mm nozzles. PLA and PETG
are the primary economical materials; ABS/ASA, TPU, and PA/CF are conditional
specialist materials. Products declare supported classes and ship coupons for
critical fits and mechanisms rather than claiming universal printer support.

Reusable original CadQuery interfaces live under
`libraries/commercial-components/` and are MIT-licensed. They require explicit
caller-supplied dimensions and provenance; they do not embed standards tables
or third-party CAD.

## Deferred Work

Custom deterministic OpenCode tools are intentionally deferred. Existing
skill scripts and project validators remain the deterministic source of truth.
