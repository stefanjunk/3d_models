#!/usr/bin/env python3
"""Create a project scaffold for an organic mesh functionalization job."""
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
        raise SystemExit(f"Target is not empty: {target}; use --force to merge")
    target.mkdir(parents=True, exist_ok=True)
    for d in ["source", "proxy", "functional", "cutters", "intermediates", "exports", "transforms", "validation", "previews", "tests"]:
        (target / d).mkdir(exist_ok=True)
    for f in ["operation-plan.yaml", "acceptance-tests.yaml", "decision-log.md"]:
        shutil.copy2(TEMPLATE_ROOT / f, target / f)
    print(target.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
