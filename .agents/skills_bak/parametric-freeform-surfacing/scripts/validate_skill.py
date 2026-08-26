#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
import re
from pathlib import Path
from typing import Any

import yaml

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise ValueError("SKILL.md frontmatter must be a mapping")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate OpenCode skill structure and compile Python helpers.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    checks: dict[str, Any] = {}
    skill_file = root / "SKILL.md"
    try:
        frontmatter = load_frontmatter(skill_file)
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        checks["frontmatter"] = frontmatter
        if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
            errors.append("frontmatter.name must match lowercase-hyphen skill naming")
        elif name != root.name:
            errors.append(f"frontmatter.name {name!r} does not match directory {root.name!r}")
        if not isinstance(description, str) or not 1 <= len(description) <= 1024:
            errors.append("frontmatter.description must be 1..1024 characters")
        for field in ("license", "compatibility", "metadata"):
            if field not in frontmatter:
                errors.append(f"Missing frontmatter field: {field}")
        metadata = frontmatter.get("metadata", {})
        if not isinstance(metadata, dict) or any(not isinstance(value, str) for value in metadata.values()):
            errors.append("frontmatter.metadata must be a string-to-string mapping for portable OpenCode compatibility")
    except Exception as exc:
        errors.append(f"SKILL.md: {type(exc).__name__}: {exc}")

    required_paths = [
        root / "references" / "00-scope-and-routing.md",
        root / "references" / "08-validation-acceptance.md",
        root / "references" / "09-examples.md",
        root / "assets" / "templates" / "surfacing-spec.yaml",
        root / "assets" / "schemas" / "surfacing-spec.schema.json",
        root / "scripts" / "surface_geometry.py",
        root / "scripts" / "run_examples.py",
    ]
    for path in required_paths:
        if not path.is_file():
            errors.append(f"Missing required path: {path.relative_to(root)}")

    compiled: list[str] = []
    python_paths = list((root / "scripts").rglob("*.py")) + list((root / "templates").rglob("*.py"))
    for path in sorted(python_paths):
        try:
            py_compile.compile(str(path), doraise=True)
            compiled.append(path.relative_to(root).as_posix())
        except Exception as exc:
            errors.append(f"Python compile failed for {path.relative_to(root)}: {exc}")
    checks["compiled_scripts"] = compiled

    try:
        schema = json.loads((root / "assets" / "schemas" / "surfacing-spec.schema.json").read_text(encoding="utf-8"))
        checks["schema_title"] = schema.get("title")
    except Exception as exc:
        errors.append(f"Schema JSON: {type(exc).__name__}: {exc}")

    report = {"root": str(root), "valid": not errors, "errors": errors, "checks": checks}
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
