#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys


def command_version(command: str, args: list[str]) -> dict:
    path = shutil.which(command)
    if not path:
        return {"available": False, "path": None, "version": None}
    try:
        result = subprocess.run([path, *args], capture_output=True, text=True, timeout=10, check=False)
        version = (result.stdout or result.stderr).strip().splitlines()[0]
    except Exception as exc:  # pragma: no cover
        version = f"error: {exc}"
    return {"available": True, "path": path, "version": version}


def module_version(name: str) -> dict:
    if importlib.util.find_spec(name) is None:
        return {"available": False, "version": None}
    try:
        module = __import__(name)
        version = getattr(module, "__version__", "unknown")
    except Exception as exc:  # pragma: no cover
        version = f"import-error: {exc}"
    return {"available": True, "version": str(version)}


def main() -> int:
    report = {
        "python": sys.version.split()[0],
        "commands": {
            "openscad": command_version("openscad", ["--version"]),
            "freecad": command_version("FreeCADCmd", ["--version"]),
            "blender": command_version("blender", ["--version"]),
            "prusa-slicer": command_version("prusa-slicer", ["--version"]),
            "orca-slicer": command_version("orca-slicer", ["--version"]),
        },
        "python_modules": {
            name: module_version(name)
            for name in ["yaml", "cadquery", "trimesh", "numpy", "skimage", "matplotlib"]
        },
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
