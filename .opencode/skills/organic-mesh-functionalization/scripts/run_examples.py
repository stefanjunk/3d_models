#!/usr/bin/env python3
"""Generate the parametric functional parts for included examples."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import dump_json


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--output-root", type=Path, default=Path("generated/examples"))
    p.add_argument("--all", action="store_true")
    p.add_argument("--example", choices=["dice-tower", "barefoot-shoe", "unicorn-compartment"])
    args = p.parse_args()
    names = ["dice-tower", "barefoot-shoe", "unicorn-compartment"] if args.all else [args.example]
    if not names or names == [None]:
        p.error("Use --all or --example")
    scripts = {
        "dice-tower": "functional_parts.py",
        "barefoot-shoe": "sole_generator.py",
        "unicorn-compartment": "compartment_parts.py",
    }
    reports = []
    for name in names:
        out = args.output_root / name
        script = args.skill_root / "examples" / name / scripts[name]
        proc = subprocess.run([sys.executable, str(script), "--out", str(out)], text=True, capture_output=True)
        reports.append({"example": name, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "output": str(out)})
    result = {"examples": reports, "passed": all(x["returncode"] == 0 for x in reports)}
    print(dump_json(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
