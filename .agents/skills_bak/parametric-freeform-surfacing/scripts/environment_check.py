#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Any


def module_status(name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(name)
        return {"available": True, "version": str(getattr(module, "__version__", "unknown"))}
    except Exception as exc:  # environment report should not fail on optional packages
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Report core and optional surfacing backends without installing anything.")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    modules = {name: module_status(name) for name in ("numpy", "yaml", "scipy", "trimesh", "cadquery", "build123d", "geomdl", "pygem")}
    executables = {name: shutil.which(name) for name in ("blender", "FreeCADCmd", "freecadcmd", "openscad", "hython", "Rhino")}
    core_ok = modules["numpy"]["available"] and modules["yaml"]["available"]
    report = {
        "python": {"version": sys.version.split()[0], "implementation": platform.python_implementation()},
        "core_ok": core_ok,
        "modules": modules,
        "executables": executables,
        "policy": "Optional backends are reported only; missing tools must produce NOT_RUN evidence, not invented success.",
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if core_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
