# 3D OpenCode Runtime

Start OpenCode from this repository:

```bash
opencode .
```

The `3d-design` primary agent uses semantic worker roles. Model bindings are an
implementation detail and can be changed without rewriting routing prompts.

| Role | Model | Purpose |
|---|---|---|
| `3d-design` | `openai/gpt-5.6-luna` | Approval gates, orchestration, deterministic operations, user communication |
| `small-general` | `openai/gpt-5.3-codex-spark` | Extraction, normalization, classification, concise evidence reports |
| `small-coding` | `openai/gpt-5.3-codex-spark` | Narrow, well-specified source changes and ordinary local repair |
| `medium-general` | `openai/gpt-5.6-terra` | Method choice, acceptance criteria, diagnosis, manufacturing tradeoffs |
| `medium-coding` | `openai/gpt-5.6-terra` | Normal CadQuery, OpenSCAD, implicit, mesh, and Python implementation |
| `cad-researcher` | `openai/gpt-5.6-terra` | External primary-source and supplier research |
| `cad-reviewer` | `openai/gpt-5.6-terra` | Independent read-only evidence review |
| `frontier` | `openai/gpt-5.6-sol` | Bounded architecture and structural-risk plan-freeze review |

Workers are flat: they cannot launch more workers. Only `3d-design` may ask the
user questions. Agents define intelligence and permission tiers; skills define
domain knowledge.

Configuration-time files are loaded once. Quit and restart OpenCode after
changing `opencode.json`, an agent, or the shared policy.

If the operating system reports `inotify_add_watch ... No space left on
device` while opening this large repository, launch the session with:

```bash
OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER=1 opencode .
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
Use at most one read-only frontier call per user request, after a prior medium
analysis identifies one unresolved architectural decision.

## Human Design Intake

Geometry work starts only after two separate human approvals:

```text
requirements summary -> user approval
                    -> versioned concept image -> user approval
                    -> DESIGN_INTAKE_PASS -> engineering/CAD workflow
```

The primary saves the approved summary, versioned image prompt, and concept
image under the object's `references/` folder. `design-intake.json` binds each
approval to SHA-256 hashes. A concept image communicates visual intent; it does
not override dimensions, parameters, loads, or acceptance criteria.

The repository uses the `opencode-gpt-imagegen` plugin and its `gpt_imagegen`
tool. Restart OpenCode after configuration changes so the tool and updated
agents are reloaded.

## Domain Ownership

| Deliverable or operation | Workflow owner |
|---|---|
| Functional product contract, loads, life, BOM, print-vs-buy | `functional-3d-design` |
| Image-derived embossing or engraving | `3d-print-heightmap-relief` |
| Existing dense mesh intervention | `organic-mesh-functionalization` |
| Mold, master, case, parting, or casting process | `casting-negative-molds` |
| Generic triangle-mesh evidence | `mesh-validation` |

One workflow owns the deliverable; supporting skills supply bounded operations.
For example, casting owns a mold made from a scanned heightmapped object while
organic mesh and heightmap relief act as adjuncts.

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

When the optional `libraries/commercial-components/` package is present,
reusable original CadQuery interfaces are MIT-licensed and require explicit
caller-supplied dimensions and provenance. If the package or pinned third-party
lock/bootstrap infrastructure is absent, the corresponding skill reports
`BLOCKED` rather than installing an unpinned substitute.

## Deferred Work

Custom deterministic OpenCode tools are intentionally deferred. Existing
skill scripts and project validators remain the deterministic source of truth.
