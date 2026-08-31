#!/usr/bin/env python3
"""Create one profile-bearing Anycubic 3MF for the R7-C01 coupon."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-stl", required=True, type=Path)
    parser.add_argument("--output-3mf", required=True, type=Path)
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--machine-profile", required=True, type=Path)
    parser.add_argument("--process-profile", required=True, type=Path)
    parser.add_argument("--filament-profile", required=True, type=Path)
    parser.add_argument("--slicer", default=shutil.which("AnycubicSlicerNext"))
    args = parser.parse_args()

    source = args.source_stl.resolve()
    output = args.output_3mf.resolve()
    state = args.state_dir.resolve()
    report_path = args.report.resolve()
    profiles = [args.machine_profile.resolve(), args.process_profile.resolve(), args.filament_profile.resolve()]
    slicer = Path(args.slicer).resolve() if args.slicer else None
    required = [source, *profiles]
    if slicer is None:
        raise SystemExit("AnycubicSlicerNext executable not found")
    required.append(slicer)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"Missing required input(s): {missing}")
    if output.exists() or (state.exists() and any(state.iterdir())):
        raise SystemExit("Refusing to overwrite an existing 3MF or non-empty slicer state directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    state.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    help_run = subprocess.run([str(slicer), "--help"], capture_output=True, text=True, check=False)
    version_match = re.search(r"AnycubicSlicerNext-([^:\s]+)", help_run.stdout + help_run.stderr)
    command = [
        str(slicer),
        "--datadir", str(state),
        "--load-settings", f"{profiles[1]};{profiles[0]}",
        "--load-filaments", str(profiles[2]),
        "--load-defaultfila",
        "--ensure-on-bed",
        "--arrange", "1",
        "--export-3mf", str(output),
        str(source),
    ]
    run = subprocess.run(command, capture_output=True, text=True, check=False, cwd=state)
    passed = run.returncode == 0 and output.is_file() and output.stat().st_size > 0
    report = {
        "schema_version": "1.0",
        "status": "PASS" if passed else "FAIL",
        "tool": "Anycubic Slicer Next native project exporter",
        "slicer": {**record(slicer), "version": version_match.group(1) if version_match else "unknown"},
        "source": record(source),
        "profiles": {
            "machine": record(profiles[0]),
            "process": record(profiles[1]),
            "filament": record(profiles[2]),
        },
        "output": record(output) if output.is_file() else None,
        "invocation": command,
        "return_code": run.returncode,
        "stdout": run.stdout,
        "stderr": run.stderr,
        "limitations": [
            "This is a measurement coupon, not the purge-diverter product model.",
            "The embedded Anycubic PETG profile is a reproducible provisional profile; the operator must select the actually loaded filament before printing.",
            "The project may contain a generation timestamp and is not expected to be byte-identical across reruns.",
            "No printer upload or print-start action is performed.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(report_path), "output": str(output)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
