#!/usr/bin/env python3
"""Run the proven vendor-aware 3MF validator for revision 0.5.1."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS = PRODUCT / "source" / "v0.5.0" / "berlin" / "validate_anycubic_project_geometry.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-3mf", type=Path, required=True)
    parser.add_argument("--packaging-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    with tempfile.TemporaryDirectory(prefix="mm-art-010-051-3mf-validation-") as temporary:
        intermediate = Path(temporary) / "v050-report.json"
        completed = subprocess.run(
            [
                "python",
                str(PREVIOUS),
                "--project-3mf",
                str(args.project_3mf),
                "--packaging-report",
                str(args.packaging_report),
                "--output",
                str(intermediate),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0 or not intermediate.is_file():
            raise SystemExit(
                f"vendor-aware 3MF validation failed with {completed.returncode}:\n"
                f"stdout={completed.stdout}\nstderr={completed.stderr}"
            )
        report = json.loads(intermediate.read_text())
    report["revision"] = "0.5.1"
    report["validator"] = {
        "wrapper": str(Path(__file__).resolve()),
        "wrapper_sha256": sha256(Path(__file__).resolve()),
        "validated_engine": str(PREVIOUS.resolve()),
        "validated_engine_sha256": sha256(PREVIOUS),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "report": str(args.output), "totals": report["totals"]}))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
