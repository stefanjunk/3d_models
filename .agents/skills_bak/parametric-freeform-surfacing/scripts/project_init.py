#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a source-first freeform surfacing project directory.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    destination = args.project.resolve()
    if destination.exists() and any(destination.iterdir()) and not args.force:
        raise SystemExit(f"Refusing to initialize non-empty directory: {destination} (use --force)")
    destination.mkdir(parents=True, exist_ok=True)
    skill_root = Path(__file__).resolve().parents[1]
    for directory in ("source", "references", "exports", "previews", "validation", "profiles", "tests"):
        (destination / directory).mkdir(exist_ok=True)
    shutil.copy2(skill_root / "assets" / "templates" / "surfacing-spec.yaml", destination / "surfacing-spec.yaml")
    (destination / "parameters.yaml").write_text("# Product-specific semantic parameters\n{}\n", encoding="utf-8")
    (destination / "hardpoints.json").write_text("{\n  \"points\": [],\n  \"axes\": [],\n  \"planes\": []\n}\n", encoding="utf-8")
    (destination / "README.md").write_text(
        "# Freeform surfacing project\n\n"
        "Edit `surfacing-spec.yaml`, `parameters.yaml`, and `hardpoints.json` before generating geometry.\n",
        encoding="utf-8",
    )
    (destination / "CHANGELOG.md").write_text("# Changelog\n\n", encoding="utf-8")
    print(f"Initialized {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
