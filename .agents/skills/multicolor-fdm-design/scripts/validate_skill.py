#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

import yaml

from common import save_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate multicolor-fdm-design package structure and Python helpers.")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    checks: dict[str, object] = {}

    skill_file = root / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        errors.append("SKILL.md frontmatter missing or malformed")
        frontmatter = {}
    else:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    checks["frontmatter"] = frontmatter
    if frontmatter.get("name") != root.name:
        errors.append(f"Frontmatter name {frontmatter.get('name')!r} does not match directory {root.name!r}")

    required = [
        "SKILL.md", "README.md", "LICENSE",
        "assets/schemas/multicolor-job.schema.json",
        "assets/templates/multicolor-job.yaml",
        "assets/templates/filament-palette.yaml",
        "references/00-scope-and-routing.md",
        "references/04-textured-asset-to-multicolor-3mf.md",
        "references/13-sources.md",
        "scripts/quantize_texture.py",
        "scripts/texture_to_voxel_parts.py",
        "scripts/assemble_multicolor_3mf.py",
        "scripts/validate_multicolor_3mf.py",
        "scripts/build_examples.py",
        "examples/01-parametric-inlay-nameplate/model.scad",
        "examples/02-four-color-fox-badge/model.scad",
        "examples/03-textured-obj-to-four-color-3mf/generate_source.py",
    ]
    missing = [item for item in required if not (root / item).exists()]
    checks["missing_required"] = missing
    if missing:
        errors.append(f"Missing required files: {missing}")

    parsed = []
    for script in sorted((root / "scripts").glob("*.py")) + sorted((root / "examples").glob("*/**/*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            parsed.append(str(script.relative_to(root)))
        except Exception as exc:
            errors.append(f"Python syntax failed for {script}: {exc}")
    checks["parsed_python"] = parsed

    try:
        from validate_job import main as _unused  # noqa: F401
        import jsonschema
        import json
        schema = json.loads((root / "assets/schemas/multicolor-job.schema.json").read_text(encoding="utf-8"))
        job = yaml.safe_load((root / "assets/templates/multicolor-job.yaml").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(job)
        checks["template_valid"] = True
    except Exception as exc:
        checks["template_valid"] = False
        errors.append(f"Template/schema validation failed: {exc}")

    report = {"skill_root": str(root), "valid": not errors, "errors": errors, "checks": checks}
    if args.json_out:
        save_json(args.json_out, report)
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
