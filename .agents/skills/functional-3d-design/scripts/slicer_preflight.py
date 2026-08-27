#!/usr/bin/env python3
"""Create a safe slicer dry-run command; never uploads or starts a print."""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh", type=Path)
    p.add_argument("--profile", type=Path, help="PrusaSlicer .ini profile (legacy backend).")
    p.add_argument(
        "--slicer",
        choices=["prusa-slicer", "prusaslicer", "AnycubicSlicerNext", "anycubic-slicer-next"],
        default="prusa-slicer",
    )
    p.add_argument("--output", type=Path, default=Path("preflight.gcode"))
    p.add_argument("--output-dir", type=Path, default=Path("preflight-anycubic-next"))
    p.add_argument("--machine-profile", type=Path)
    p.add_argument("--process-profile", type=Path)
    p.add_argument("--filament-profile", action="append", type=Path, default=[])
    p.add_argument("--timeout-s", type=int, default=600)
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()

    anycubic = args.slicer in {"AnycubicSlicerNext", "anycubic-slicer-next"}
    executable_name = "AnycubicSlicerNext" if anycubic else args.slicer
    exe = shutil.which(executable_name)
    if anycubic:
        validation_cli = (
            Path(__file__).resolve().parents[2]
            / "validate-printable-3d-projects"
            / "scripts"
            / "fdm_ci.py"
        )
        cmd = [
            sys.executable,
            str(validation_cli),
            "slice-anycubic-next",
            str(args.mesh),
            str(args.output_dir),
            "--slicer",
            exe or executable_name,
            "--timeout-s",
            str(args.timeout_s),
        ]
        if args.machine_profile:
            cmd.extend(["--machine-profile", str(args.machine_profile)])
        if args.process_profile:
            cmd.extend(["--process-profile", str(args.process_profile)])
        for filament in args.filament_profile:
            cmd.extend(["--filament-profile", str(filament)])
        required_paths = [args.mesh, validation_cli]
        supplied_profiles = any((args.machine_profile, args.process_profile, args.filament_profile))
        complete_profiles = bool(args.machine_profile and args.process_profile and args.filament_profile)
        if args.mesh.suffix.lower() != ".3mf" or supplied_profiles:
            required_paths.extend([path for path in [args.machine_profile, args.process_profile, *args.filament_profile] if path])
        missing_configuration = (args.mesh.suffix.lower() != ".3mf" or supplied_profiles) and not complete_profiles
    else:
        cmd = [exe or args.slicer, "--load", str(args.profile), "--export-gcode", "--output", str(args.output), str(args.mesh)]
        required_paths = [args.mesh, args.profile] if args.profile else [args.mesh]
        missing_configuration = args.profile is None

    report = {
        "command": shlex.join(cmd),
        "backend": "anycubic-slicer-next" if anycubic else "prusa-slicer",
        "slicer_found": bool(exe),
        "execute_requested": args.execute,
        "safety": "This command only exports local G-code. Inspect it in a viewer; no upload/start action is implemented.",
    }
    if missing_configuration:
        report["error"] = (
            "Anycubic mesh slicing requires --machine-profile, --process-profile, and at least one --filament-profile"
            if anycubic else "PrusaSlicer requires --profile"
        )
        print(json.dumps(report, indent=2))
        return 1
    if args.execute:
        if not exe:
            report["error"] = "slicer executable not found"
            print(json.dumps(report, indent=2))
            return 1
        missing = [str(path) for path in required_paths if not path.exists()]
        if missing:
            report["error"] = "required path not found"
            report["missing"] = missing
            print(json.dumps(report, indent=2))
            return 1
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        report["returncode"] = proc.returncode
        if anycubic:
            try:
                report["result"] = json.loads(proc.stdout)
            except json.JSONDecodeError:
                report["stdout"] = proc.stdout[-4000:]
                report["stderr"] = proc.stderr[-4000:]
        else:
            report["stdout"] = proc.stdout[-4000:]
            report["stderr"] = proc.stderr[-4000:]
        print(json.dumps(report, indent=2))
        return proc.returncode
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
