#!/usr/bin/env python3
"""Create a safe slicer dry-run command; never uploads or starts a print."""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh", type=Path)
    p.add_argument("--profile", type=Path, required=True)
    p.add_argument("--slicer", choices=["prusa-slicer", "prusaslicer"], default="prusa-slicer")
    p.add_argument("--output", type=Path, default=Path("preflight.gcode"))
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()
    exe = shutil.which(args.slicer)
    cmd = [exe or args.slicer, "--load", str(args.profile), "--export-gcode", "--output", str(args.output), str(args.mesh)]
    report = {
        "command": shlex.join(cmd),
        "slicer_found": bool(exe),
        "execute_requested": args.execute,
        "safety": "This command only exports local G-code. Inspect it in a viewer; no upload/start action is implemented.",
    }
    if args.execute:
        if not exe:
            report["error"] = "slicer executable not found"
            print(json.dumps(report, indent=2))
            return 1
        if not args.mesh.exists() or not args.profile.exists():
            report["error"] = "mesh or profile not found"
            print(json.dumps(report, indent=2))
            return 1
        import subprocess
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        report["returncode"] = proc.returncode
        report["stdout"] = proc.stdout[-4000:]
        report["stderr"] = proc.stderr[-4000:]
        print(json.dumps(report, indent=2))
        return proc.returncode
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
