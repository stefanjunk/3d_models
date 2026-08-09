#!/usr/bin/env python3
"""Report installed mesh/CAD executables and Python capabilities."""
from __future__ import annotations

import importlib.util
import shutil
import sys

from common import dump_json


def module(name: str) -> dict[str, object]:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return {"installed": False}
    try:
        mod = __import__(name)
        return {"installed": True, "version": getattr(mod, "__version__", None)}
    except Exception as exc:
        return {"installed": True, "import_error": str(exc)}


def main() -> int:
    report = {
        "python": sys.version,
        "executables": {name: shutil.which(name) for name in ["blender", "openscad", "FreeCADCmd", "freecadcmd"]},
        "modules": {name: module(name) for name in ["numpy", "scipy", "trimesh", "manifold3d", "skimage", "yaml", "cadquery"]},
    }
    report["capabilities"] = {
        "headless_mesh_validation": report["modules"]["trimesh"]["installed"],
        "manifold_boolean": report["modules"]["manifold3d"]["installed"],
        "blender_boolean": bool(report["executables"]["blender"]),
        "openscad_csg": bool(report["executables"]["openscad"]),
        "cadquery_functional_parts": report["modules"]["cadquery"]["installed"],
    }
    print(dump_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
