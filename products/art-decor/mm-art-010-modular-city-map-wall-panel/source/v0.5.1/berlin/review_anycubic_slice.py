#!/usr/bin/env python3
"""Run the canonical Anycubic G-code review with revision 0.5.1 metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS = PRODUCT / "source" / "v0.5.0" / "berlin" / "review_anycubic_site_marker_slice.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-report", type=Path, required=True)
    parser.add_argument("--gcode", type=Path, required=True)
    parser.add_argument("--project-3mf", type=Path, required=True)
    parser.add_argument("--mode", choices=("boundary-crop", "context-outline"), required=True)
    parser.add_argument("--half", choices=("left", "right"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-tools", default="0,1,2,3")
    parser.add_argument("--minimum-tool-changes", type=int, required=True)
    parser.add_argument("--maximum-tool-changes", type=int, required=True)
    parser.add_argument("--expected-maximum-z", type=float, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    with tempfile.TemporaryDirectory(prefix="mm-art-010-051-slice-review-") as temporary:
        intermediate = Path(temporary) / "v050-review.json"
        command = [
            "python",
            str(PREVIOUS),
            "--adapter-report",
            str(args.adapter_report),
            "--gcode",
            str(args.gcode),
            "--project-3mf",
            str(args.project_3mf),
            "--mode",
            args.mode,
            "--half",
            args.half,
            "--output",
            str(intermediate),
            "--expected-tools",
            args.expected_tools,
            "--minimum-tool-changes",
            str(args.minimum_tool_changes),
            "--maximum-tool-changes",
            str(args.maximum_tool_changes),
            "--expected-maximum-z",
            str(args.expected_maximum_z),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0 or not intermediate.is_file():
            raise SystemExit(
                f"canonical G-code review failed with {completed.returncode}:\n"
                f"stdout={completed.stdout}\nstderr={completed.stderr}"
            )
        report = json.loads(intermediate.read_text())
    report["revision"] = "0.5.1"
    report["reviewer"] = {
        "wrapper": str(Path(__file__).resolve()),
        "wrapper_sha256": sha256(Path(__file__).resolve()),
        "review_engine": str(PREVIOUS.resolve()),
        "review_engine_sha256": sha256(PREVIOUS),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "report": str(args.output), "metrics": report["metrics"]}))


if __name__ == "__main__":
    main()
