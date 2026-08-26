# OpenCode installation and portability

This package follows OpenCode's Agent Skills convention: one directory containing an uppercase `SKILL.md` whose YAML frontmatter has a lowercase hyphenated `name` and a specific `description`.

## Install in one project

Copy the complete package, without flattening `assets/`, `references/`, or `scripts/`, to:

```text
<project>/.opencode/skills/reconstruct-printable-3d-from-images/
```

The resulting entry point must be:

```text
<project>/.opencode/skills/reconstruct-printable-3d-from-images/SKILL.md
```

OpenCode also recognizes project-local `.agents/skills/` and `.claude/skills/` layouts. Use one location for this skill in a project so duplicate names do not obscure discovery behavior.

## Install globally

Copy the complete package to:

```text
~/.config/opencode/skills/reconstruct-printable-3d-from-images/
```

OpenCode also recognizes global `~/.agents/skills/` and `~/.claude/skills/` layouts. Prefer the OpenCode-native location unless the same package must be shared with another compatible agent.

## Validate discovery

Check all of the following:

- the file is named exactly `SKILL.md`;
- the containing directory is named exactly `reconstruct-printable-3d-from-images`;
- the frontmatter `name` matches that directory;
- `name` contains only lowercase letters, digits, and single hyphens;
- `description` is present and no longer than 1024 characters;
- no other discovered skill uses the same name;
- the OpenCode `permission.skill` rules allow the name;
- the agent's `skill` tool is enabled.

Ask the agent to load `reconstruct-printable-3d-from-images`. If it is absent, start from a working directory under the intended project, check the paths above, then inspect skill permissions.

## Preserve script portability

OpenCode normally runs tools from the user's project, not necessarily from this skill directory. Treat the directory containing `SKILL.md` as the skill root and resolve every linked resource from there. Do not assume `scripts/preprocess_image.py` is relative to the user's model project.

Keep project evidence and outputs outside the installed skill directory. Copy `assets/reconstruction-brief.yaml` and `assets/view-manifest.example.json` into the model project before editing them. This keeps the installed skill immutable and reusable.

The official format and discovery rules are documented at <https://opencode.ai/docs/skills/>.
