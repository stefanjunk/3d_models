# OpenCode integration

## Discovery

The canonical project-local path is:

```text
.opencode/skills/parametric-freeform-surfacing/SKILL.md
```

The `name` value in frontmatter exactly matches the directory name and uses lowercase alphanumeric characters plus hyphens. The frontmatter contains only portable skill fields: `name`, `description`, `license`, `compatibility`, and string-valued metadata.

## Command

The optional project command is:

```text
.opencode/commands/design-freeform-surface.md
```

It uses `$ARGUMENTS` and does not hard-code a provider or model. The user's configured OpenCode agent/model therefore remains authoritative.

## Portable paths

Scripts do not assume a repository root. Set:

```bash
export PFS_SKILL=.opencode/skills/parametric-freeform-surfacing
```

or point it to the global installation. Example generators locate the skill scripts relative to their own files and can also be copied with the complete skill directory.

## External tools

The skill never auto-installs, clones, or executes an unreviewed external library. `environment_check.py` reports optional Python packages and executables. When a requested backend is unavailable, generate the complete source and mark the backend-specific validation `NOT_RUN`.

## Existing skill family

Install this directory beside existing skills. Do not merge its `SKILL.md` into another skill, because separate discovery descriptions improve routing and keep the context loaded for a task smaller. Use `integration/ROUTING_ADDENDUM.md` when maintaining a shared orchestrator or combined GPT instruction set.
