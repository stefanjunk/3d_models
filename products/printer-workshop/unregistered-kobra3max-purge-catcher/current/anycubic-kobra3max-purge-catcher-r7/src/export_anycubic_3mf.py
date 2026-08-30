#!/usr/bin/env python3
"""Export target-slicer project 3MF files from the audited R7 STL bodies."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


PROJECTS = {
    "purge-catcher-body": ["models/stl/moving-catcher-balanced-draft.stl"],
    "wiper-datum-plate": ["models/stl/datum-plate-draft.stl"],
    "mount-pattern-gauge": ["models/stl/mount-pattern-gauge.stl"],
    "slide-clearance-coupon": [
        "models/stl/lateral-slide-male.stl",
        "models/stl/lateral-slide-female-c020.stl",
        "models/stl/lateral-slide-female-c030.stl",
        "models/stl/lateral-slide-female-c040.stl",
    ],
    "latch-cycle-coupon": [
        "models/stl/latch-cycle-fixed.stl",
        "models/stl/latch-cycle-flex.stl",
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict:
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def require_empty_or_missing(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--machine-profile", required=True, type=Path)
    parser.add_argument("--process-profile", required=True, type=Path)
    parser.add_argument("--filament-profile", required=True, type=Path)
    parser.add_argument("--slicer", default=shutil.which("AnycubicSlicerNext"))
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    slicer = Path(args.slicer).resolve() if args.slicer else None
    profiles = [
        args.machine_profile.resolve(),
        args.process_profile.resolve(),
        args.filament_profile.resolve(),
    ]
    required = [build_dir, *profiles]
    if slicer is None:
        raise SystemExit("AnycubicSlicerNext executable not found")
    required.append(slicer)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing required input(s): {missing}")

    output_dir = build_dir / "models" / "3mf" / "anycubic"
    state_root = build_dir / "anycubic-export-state"
    require_empty_or_missing(output_dir)
    require_empty_or_missing(state_root)

    help_run = subprocess.run(
        [str(slicer), "--help"], capture_output=True, text=True, check=False
    )
    version_match = re.search(r"AnycubicSlicerNext-([^:\s]+)", help_run.stdout + help_run.stderr)
    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "tool": "Anycubic Slicer Next native project exporter",
        "slicer": {
            **file_record(slicer),
            "version": version_match.group(1) if version_match else "unknown",
        },
        "profiles": {
            "machine": file_record(profiles[0]),
            "process": file_record(profiles[1]),
            "filament": file_record(profiles[2]),
        },
        "exports": {},
        "limitations": [
            "The target slicer embeds a generation timestamp, so project 3MF byte identity is not expected across reruns.",
            "Each exported 3MF must pass a fresh slice-anycubic-next run before use.",
            "No upload or print-start action is performed.",
        ],
    }

    for name, relative_inputs in PROJECTS.items():
        inputs = [build_dir / relative for relative in relative_inputs]
        missing_inputs = [str(path) for path in inputs if not path.is_file()]
        if missing_inputs:
            raise SystemExit(f"Missing generated STL input(s): {missing_inputs}")
        state_dir = state_root / name
        state_dir.mkdir(parents=True)
        output = output_dir / f"ANYCUBIC-R7-{name}.3mf"
        command = [
            str(slicer),
            "--datadir",
            str(state_dir),
            "--load-settings",
            f"{profiles[1]};{profiles[0]}",
            "--load-filaments",
            str(profiles[2]),
            "--load-defaultfila",
            "--ensure-on-bed",
            "--arrange",
            "1",
            "--export-3mf",
            str(output),
            *map(str, inputs),
        ]
        run = subprocess.run(command, capture_output=True, text=True, check=False)
        passed = run.returncode == 0 and output.is_file() and output.stat().st_size > 0
        report["exports"][name] = {
            "status": "PASS" if passed else "FAIL",
            "return_code": run.returncode,
            "inputs": [file_record(path) for path in inputs],
            "output": file_record(output) if output.is_file() else None,
            "invocation": command,
            "stdout": run.stdout,
            "stderr": run.stderr,
        }
        if not passed:
            report["status"] = "FAIL"

    report_path = build_dir / "reports" / "anycubic-3mf-export.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(report_path)}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
