from __future__ import annotations

import importlib
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from .common import check, report


MODULE_GROUPS: dict[str, list[str]] = {
    "mesh": ["numpy", "trimesh"],
    "mesh-distance": ["numpy", "trimesh", "scipy", "rtree"],
    "mesh-boolean": ["numpy", "trimesh", "manifold3d"],
    "vision": ["numpy", "PIL", "skimage"],
    "camera": ["numpy", "cv2"],
    "yaml": ["yaml"],
}

EXECUTABLES = ["openscad", "freecadcmd", "FreeCADCmd", "blender", "prusa-slicer", "prusaslicer", "orca-slicer"]


def module_version(name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(name)
        return {"available": True, "version": str(getattr(module, "__version__", "unknown"))}
    except Exception as exc:
        return {"available": False, "version": None, "error": f"{type(exc).__name__}: {exc}"}


def run(required_groups: list[str] | None = None) -> dict[str, Any]:
    required_groups = required_groups or []
    modules = sorted({name for group in MODULE_GROUPS.values() for name in group})
    module_rows = {name: module_version(name) for name in modules}
    groups = {
        group: {
            "available": all(module_rows[name]["available"] for name in names),
            "modules": names,
            "missing": [name for name in names if not module_rows[name]["available"]],
        }
        for group, names in MODULE_GROUPS.items()
    }
    checks = []
    for group in required_groups:
        if group not in groups:
            checks.append(check(f"capability:{group}", "FAIL", "Unknown capability group", required=True))
        elif groups[group]["available"]:
            checks.append(check(f"capability:{group}", "PASS", "Capability group available", required=True))
        else:
            checks.append(
                check(
                    f"capability:{group}",
                    "NOT_RUN",
                    "Missing modules: " + ", ".join(groups[group]["missing"]),
                    required=True,
                )
            )
    if not checks:
        checks.append(check("environment-inventory", "PASS", "Environment inventory completed", required=False))
    result = report("doctor", checks, capabilities=required_groups)
    result["environment"] = {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "modules": module_rows,
        "capability_groups": groups,
        "executables": {name: shutil.which(name) for name in EXECUTABLES},
        "skill_directory_writable": os.access(Path(__file__).resolve().parents[2], os.W_OK),
        "note": "No packages were installed and no executable was invoked.",
    }
    return result
