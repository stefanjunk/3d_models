#!/usr/bin/env python3
"""Create a design project scaffold from the skill templates."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import TEMPLATE_ROOT


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("name")
    p.add_argument("--directory", type=Path, default=Path.cwd())
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    target = args.directory / args.name
    if target.exists() and any(target.iterdir()) and not args.force:
        raise SystemExit(f"Target is not empty: {target}. Use --force to merge templates.")
    target.mkdir(parents=True, exist_ok=True)
    for directory in ["source", "exports", "profiles", "validation", "tests"]:
        (target / directory).mkdir(exist_ok=True)
    for filename in ["design-spec.yaml", "bom.yaml", "test-plan.yaml", "decision-log.md"]:
        shutil.copy2(TEMPLATE_ROOT / filename, target / filename)
    print(target.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
