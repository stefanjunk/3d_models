#!/usr/bin/env python3
"""One-command procedural texture geometry build, validation, and packaging.

Usage:
    python3 rebuild.py

All geometry, texture, protected-region, output, and memory settings are read
from the versioned project parameter files.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def require_python_packages() -> None:
    missing = [name for name in ("numpy", "PIL") if importlib.util.find_spec(name) is None]
    if missing:
        raise SystemExit(
            "Missing Python dependencies. Run: python3 -m pip install -r requirements.txt"
        )


def ensure_node_dependencies() -> None:
    if (ROOT / "node_modules" / "manifold-3d").is_dir():
        return
    print("Installing locked Node.js dependencies (first rebuild only)...", flush=True)
    subprocess.run(["npm", "ci"], cwd=ROOT, check=True, shell=False)


def main() -> int:
    require_python_packages()
    ensure_node_dependencies()
    subprocess.run(
        [sys.executable, str(ROOT / "src" / "build_pipeline.py")],
        cwd=ROOT,
        check=True,
        shell=False,
    )
    renders = (
        ("DRAFT-R1.5-procedural-walnut-model-preview.png", "overall"),
        ("DRAFT-R1.5-procedural-walnut-hardware-closeup.png", "hardware-front"),
        ("DRAFT-R1.5-procedural-walnut-texture-coupon.png", "coupon"),
    )
    for filename, view in renders:
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "src" / "render_stl.py"),
                str(ROOT / "reports" / filename),
                "--view",
                view,
            ],
            cwd=ROOT,
            check=True,
            shell=False,
        )
    subprocess.run(
        [sys.executable, str(ROOT / "src" / "watermark_evidence.py")],
        cwd=ROOT,
        check=True,
        shell=False,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "src" / "package_release.py")],
        cwd=ROOT,
        check=True,
        shell=False,
    )
    print("Rebuild complete. See output/DRAFT, reports, and the revisioned ZIP file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
