#!/usr/bin/env python3
"""Review the exact coupon slice through the canonical revision 0.5.1 wrapper."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REVIEW = HERE / "review_anycubic_slice.py"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-report", type=Path, required=True)
    parser.add_argument("--gcode", type=Path, required=True)
    parser.add_argument("--project-3mf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--minimum-tool-changes", type=int, required=True)
    parser.add_argument("--maximum-tool-changes", type=int, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    with tempfile.TemporaryDirectory(prefix="mm-art-010-051-coupon-review-") as temporary:
        intermediate = Path(temporary) / "coupon-review.json"
        completed = subprocess.run(
            [
                "python",
                str(REVIEW),
                "--adapter-report",
                str(args.adapter_report),
                "--gcode",
                str(args.gcode),
                "--project-3mf",
                str(args.project_3mf),
                "--mode",
                "boundary-crop",
                "--half",
                "left",
                "--output",
                str(intermediate),
                "--expected-tools",
                "0,3",
                "--minimum-tool-changes",
                str(args.minimum_tool_changes),
                "--maximum-tool-changes",
                str(args.maximum_tool_changes),
                "--expected-maximum-z",
                "3.0",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0 or not intermediate.is_file():
            raise SystemExit(
                f"coupon G-code review failed with {completed.returncode}:\n"
                f"stdout={completed.stdout}\nstderr={completed.stderr}"
            )
        report = json.loads(intermediate.read_text())
    report["mode"] = "metrimade-logo-coupon"
    report["half"] = None
    report["candidate"] = "logo-coupon-r1"
    report["scope"] = "native Anycubic coupon project import, executable layer consistency, 3.0 mm height and tools 1/4 routing"
    report["limitations"].append(
        "Physical 2.0 m recognition remains a human coupon gate."
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "report": str(args.output), "metrics": report["metrics"]}))


if __name__ == "__main__":
    main()
