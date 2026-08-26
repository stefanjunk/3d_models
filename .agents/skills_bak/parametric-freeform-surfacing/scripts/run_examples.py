#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build all deterministic freeform surfacing examples.")
    parser.add_argument("--output", type=Path, default=Path("build/examples"))
    parser.add_argument("--quality", choices=("draft", "print"), default="draft")
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    args.output.mkdir(parents=True, exist_ok=True)
    examples = ("barefoot-shoe", "organic-bowl", "rc-car-sporty-envelope")
    results = []
    failed = False
    for name in examples:
        source = skill_root / "examples" / name
        output = args.output / name
        command = [
            sys.executable,
            str(source / "generate.py"),
            "--parameters",
            str(source / "parameters.yaml"),
            "--output",
            str(output),
            "--quality",
            args.quality,
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        result = {
            "name": name,
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "validation": str(output / "validation.json"),
        }
        results.append(result)
        print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        if completed.returncode != 0:
            failed = True
    summary = {"quality": args.quality, "output": str(args.output), "success": not failed, "examples": results}
    summary_path = args.summary or (args.output / "summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {summary_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
