#!/usr/bin/env python3
"""Aggregate one or more run_examples reports into a concise validation summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("reports", nargs="+")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    combined = {
        "reports": [],
        "examples": {},
        "passed": True,
        "note": "Geometry/source validation does not replace slicer review or physical functional tests.",
    }
    for name in args.reports:
        path = Path(name)
        data = json.loads(path.read_text(encoding="utf-8"))
        combined["reports"].append(str(path))
        combined["passed"] = combined["passed"] and bool(data.get("passed"))
        for ex_name, ex in data.get("examples", {}).items():
            failures = [step["name"] for step in ex.get("steps", []) if step.get("returncode") not in (0, None)]
            combined["examples"][ex_name] = {
                "passed": bool(ex.get("passed")),
                "step_count": len(ex.get("steps", [])),
                "output_count": len(ex.get("outputs", [])),
                "failed_steps": failures,
                "outputs": ex.get("outputs", []),
            }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(combined, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(combined, indent=2))
    return 0 if combined["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
