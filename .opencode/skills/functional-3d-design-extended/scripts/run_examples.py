#!/usr/bin/env python3
"""Build, validate, and preview the bundled example designs."""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(command: list[str], *, cwd: Path | None = None, timeout: int = 240) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "command": command,
        "cwd": str(cwd) if cwd else None,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-root", type=Path, default=Path.cwd())
    p.add_argument("--all", action="store_true", help="Build all examples (default when no names are supplied)")
    p.add_argument("names", nargs="*")
    p.add_argument("--strict-tools", action="store_true", help="Fail instead of skipping unavailable external tools")
    p.add_argument("--no-preview", action="store_true")
    args = p.parse_args()

    package_root = args.package_root.resolve()
    skill = package_root / ".opencode" / "skills" / "functional-3d-design"
    examples_root = skill / "examples"
    scripts = skill / "scripts"
    generated_root = package_root / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    known = ["honeycomb-wall-shelf", "rounded-desk-organizer", "unicorn-dice-tower", "calibration-coupons"]
    selected = known if args.all or not args.names else args.names
    unknown = sorted(set(selected) - set(known))
    if unknown:
        raise SystemExit(f"Unknown examples: {unknown}")

    have_cq = importlib.util.find_spec("cadquery") is not None
    openscad = shutil.which("openscad")
    report: dict[str, Any] = {
        "package_root": str(package_root),
        "tools": {"cadquery": have_cq, "openscad": openscad},
        "examples": {},
        "passed": True,
    }

    for name in selected:
        ex = examples_root / name
        out = generated_root / name
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        item: dict[str, Any] = {"steps": [], "outputs": [], "passed": True}
        report["examples"][name] = item

        spec_step = run([sys.executable, str(scripts / "validate_design_spec.py"), str(ex / "design-spec.yaml"), "--json-out", str(out / "design-spec-validation.json")])
        item["steps"].append({"name": "validate-design-spec", **spec_step})
        if spec_step["returncode"] != 0:
            item["passed"] = False

        if name in {"honeycomb-wall-shelf", "rounded-desk-organizer"}:
            if not have_cq:
                item["skipped"] = "cadquery not installed"
                item["passed"] = not args.strict_tools
            else:
                build = run([sys.executable, str(ex / "model.py"), "--out", str(out)], cwd=ex, timeout=360)
                item["steps"].append({"name": "build-cadquery", **build})
                if build["returncode"] != 0:
                    item["passed"] = False
        elif name == "unicorn-dice-tower":
            if not openscad:
                item["skipped"] = "openscad not installed"
                item["passed"] = not args.strict_tools
            else:
                build = run([openscad, "-o", str(out / "unicorn-dice-tower.stl"), "model.scad"], cwd=ex, timeout=360)
                item["steps"].append({"name": "build-openscad", **build})
                if build["returncode"] != 0:
                    item["passed"] = False
        else:
            if not openscad:
                item["skipped"] = "openscad not installed"
                item["passed"] = not args.strict_tools
            else:
                for coupon in ["fit", "walls", "engraving", "bridges"]:
                    build = run([
                        openscad,
                        "-D", f'coupon="{coupon}"',
                        "-o", str(out / f"{coupon}-coupon.stl"),
                        "model.scad",
                    ], cwd=ex, timeout=240)
                    item["steps"].append({"name": f"build-{coupon}", **build})
                    if build["returncode"] != 0:
                        item["passed"] = False

        stls = sorted(out.glob("*.stl"))
        item["outputs"] = [str(path.relative_to(package_root)) for path in sorted(out.iterdir()) if path.is_file()]
        for stl in stls:
            validation = run([
                sys.executable,
                str(scripts / "validate_mesh.py"),
                str(stl),
                "--require-watertight",
                "--max-bodies", "1",
                "--json-out", str(stl.with_suffix(".mesh.json")),
                "--quiet",
            ], timeout=240)
            item["steps"].append({"name": f"validate-{stl.name}", **validation})
            if validation["returncode"] != 0:
                item["passed"] = False
            if not args.no_preview and validation["returncode"] == 0:
                preview = run([
                    sys.executable,
                    str(scripts / "mesh_preview.py"),
                    str(stl),
                    "--out", str(stl.with_suffix(".png")),
                ], timeout=240)
                item["steps"].append({"name": f"preview-{stl.name}", **preview})
                if preview["returncode"] != 0:
                    # Preview is helpful but is not geometry evidence.
                    item.setdefault("warnings", []).append(f"preview failed for {stl.name}")

        item["outputs"] = [str(path.relative_to(package_root)) for path in sorted(out.iterdir()) if path.is_file()]
        report["passed"] = report["passed"] and item["passed"]

    report_path = generated_root / "example-build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
