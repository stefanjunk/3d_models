from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .common import check, report
from .profile import validate_profile as validate_companion_profile

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESOURCE_RE = re.compile(r"(?:`|\()((?:scripts|assets|references|examples|templates|integration)/[^`\s\)]+)")
IMPORT_TO_PACKAGE = {
    "numpy": "numpy",
    "trimesh": "trimesh",
    "scipy": "scipy",
    "PIL": "Pillow",
    "skimage": "scikit-image",
    "yaml": "PyYAML",
    "jsonschema": "jsonschema",
    "cv2": "opencv-python-headless",
    "manifold3d": "manifold3d",
    "rtree": "rtree",
}


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def validate(root: Path, runtime: str = "portable", profile: str = "release") -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return report("validate-skill", [check("skill-entrypoint", "FAIL", f"Missing {skill_md}")], inputs=[skill_md], profile=profile)
    text = skill_md.read_text(encoding="utf-8")
    fm = _frontmatter(text)
    name, description = fm.get("name"), fm.get("description")
    checks.append(check("frontmatter-name", "PASS" if isinstance(name, str) and bool(NAME_RE.fullmatch(name)) else "FAIL", f"Skill name: {name!r}"))
    checks.append(check("frontmatter-description", "PASS" if isinstance(description, str) and 1 <= len(description) <= 1024 else "FAIL", f"Description length: {len(description or '')}"))
    skill_chars = len(text)
    context_budget_chars = 24000
    checks.append(check("skill-context-budget", "PASS" if skill_chars <= context_budget_chars else "REVIEW_REQUIRED", f"SKILL.md characters {skill_chars}; compact-instruction budget {context_budget_chars}", required=False, metrics={"characters": skill_chars, "rough_tokens_at_4_chars": (skill_chars + 3) // 4}))
    if runtime == "opencode":
        checks.append(check("opencode-directory-name", "PASS" if root.name == name else "FAIL", f"Directory {root.name!r}; frontmatter name {name!r}"))
    elif runtime == "portable" and root.name != name:
        checks.append(check("logical-directory-name", "REVIEW_REQUIRED", f"Materialized directory {root.name!r} differs from logical name {name!r}; package as {name!r} for OpenCode", required=False))

    missing_resources = []
    for value in sorted(set(RESOURCE_RE.findall(text))):
        rel = value.rstrip(".,;:")
        if "*" in rel:
            continue
        if not (root / rel).exists():
            missing_resources.append(rel)
    checks.append(check("resource-references", "PASS" if not missing_resources else "FAIL", "All explicit SKILL.md resource paths exist" if not missing_resources else "Missing: " + ", ".join(missing_resources), metrics={"missing": missing_resources}))

    syntax_errors = []
    imports: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            syntax_errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
    checks.append(check("python-ast", "PASS" if not syntax_errors else "FAIL", f"Parsed {len(list(root.rglob('*.py')))} Python file(s) without bytecode writes" if not syntax_errors else "; ".join(syntax_errors), metrics={"errors": syntax_errors}))

    requirement_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in root.rglob("requirements*.txt"))
    undeclared = []
    for imported, package in IMPORT_TO_PACKAGE.items():
        if imported in imports and re.search(rf"(?im)^\s*{re.escape(package)}(?:\[.*?\])?\s*[=<>~!]", requirement_text) is None:
            undeclared.append(package)
    checks.append(check("dependency-declarations", "PASS" if not undeclared else "REVIEW_REQUIRED", "Detected third-party imports are represented in requirements files" if not undeclared else "No requirements declaration found for: " + ", ".join(sorted(undeclared)), required=False, metrics={"undeclared": sorted(undeclared)}))

    test_files = list(root.glob("tests/test_*.py")) + list(root.glob("tests/*_test.py"))
    checks.append(check("test-suite-present", "PASS" if test_files else "REVIEW_REQUIRED", f"Test files: {len(test_files)}", required=False))

    escaping_symlinks = []
    for path in root.rglob("*"):
        if path.is_symlink():
            try:
                path.resolve().relative_to(root.resolve())
            except ValueError:
                escaping_symlinks.append(path.relative_to(root).as_posix())
    checks.append(check("symlink-containment", "PASS" if not escaping_symlinks else "FAIL", "All symlinks remain inside the skill" if not escaping_symlinks else "Escaping symlinks: " + ", ".join(escaping_symlinks), metrics={"escaping": escaping_symlinks}))

    command_errors = []
    for command_path in sorted((root / "opencode" / "commands").glob("*.md")) if (root / "opencode" / "commands").is_dir() else []:
        command_text = command_path.read_text(encoding="utf-8")
        if re.search(r"(?im)^\s*(?:model|provider)\s*:", command_text):
            command_errors.append(f"{command_path.relative_to(root)} hard-codes model/provider")
        if "$ARGUMENTS" not in command_text:
            command_errors.append(f"{command_path.relative_to(root)} does not forward $ARGUMENTS")
    checks.append(check("opencode-command-portability", "PASS" if not command_errors else "FAIL", "OpenCode command payloads are model/provider-neutral" if not command_errors else "; ".join(command_errors), metrics={"errors": command_errors}))

    validation_profile = root / "assets" / "validation-profile.json"
    profile_result = None
    if validation_profile.is_file():
        profile_result = validate_companion_profile(validation_profile, profile=profile)
        checks.append(check("deterministic-validation-profile", profile_result["status"], f"Companion validation profile returned {profile_result['status']}", required=True))
    return report(
        "validate-skill",
        checks,
        inputs=[skill_md],
        profile=profile,
        metrics={"runtime": runtime, "logical_name": name, "python_imports": sorted(imports), "skill_characters": skill_chars, "validation_profile": profile_result},
        limitations=["Dependency declaration matching is static and does not prove the environment can import optional backends."],
    )
