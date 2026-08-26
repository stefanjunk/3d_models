# OpenCode runtime

Install the complete directory as:

```text
.opencode/skills/validate-printable-3d-projects/
```

Install companion skills as sibling directories using their frontmatter names. Do not copy only `SKILL.md`; scripts, assets, and references are required.

The core CLI runs from any current working directory. Invoke it by absolute path or set:

```bash
export FDM_VALIDATION_SKILL=.opencode/skills/validate-printable-3d-projects
python3 "$FDM_VALIDATION_SKILL/scripts/fdm_ci.py" doctor
```

The validator never writes into its installed directory. Reports and temporary builds belong in the active model project.

## Dependencies

The manifest, G-code, 3MF, project, and skill-portability checks use the Python standard library. Mesh, distance, collision, wall-thickness, and CAD-format checks use optional capability groups listed by `doctor`.

Create a project virtual environment, install only required groups, then save the actual `doctor` report with every release. Do not let an agent silently install or upgrade the environment.

## Local-model context

Load this `SKILL.md`, the active specialist skill, and only the references explicitly needed for the task. Run scripts without loading their source into the model context. Feed the model the aggregate JSON failures and metrics rather than complete logs.

For autonomous work, initialize `autonomy-policy.json` once and feed the model only the active stage, the policy fields for that stage, and `validate-approvals.metrics.stage_state`. Keep full ledgers and evidence reports as script inputs. This bounds prompt growth even after failed attempts.

Workflow approval is distinct from OpenCode tool permission. The default autonomous policy allows local workspace build/export/test work, keeps network and dependency installation at `ask`, and denies destructive overwrite, printer upload, and printer start. The more restrictive of the project policy and the OpenCode runtime always applies.
