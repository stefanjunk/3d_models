#!/usr/bin/env python3
"""Rebuild one parametric surface variant without mutating the selected profile."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

from src.surface_profiles import resolve_surface_profile, surface_choices


ROOT = Path(__file__).resolve().parent


def require_python_packages() -> None:
    missing = [name for name in ("numpy", "PIL") if importlib.util.find_spec(name) is None]
    if missing:
        raise SystemExit("Missing Python dependencies. Run: python3 -m pip install -r requirements.txt")


def ensure_node_dependencies() -> None:
    if (ROOT / "node_modules" / "manifold-3d").is_dir():
        return
    print("Installing locked Node.js dependencies (first rebuild only)...", flush=True)
    subprocess.run(["npm", "ci"], cwd=ROOT, check=True, shell=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface", choices=surface_choices(ROOT), help="default comes from config/surface-texture.json")
    args = parser.parse_args()
    surface_id, _, _ = resolve_surface_profile(ROOT, args.surface)
    require_python_packages()
    ensure_node_dependencies()
    subprocess.run([
        sys.executable,
        str(ROOT / "src" / "build_pipeline.py"),
        "--surface",
        surface_id,
    ], cwd=ROOT, check=True, shell=False)
    renders = (
        (f"DRAFT-R1.6-{surface_id}-model-preview.png", "overall"),
        (f"DRAFT-R1.6-{surface_id}-hardware-closeup.png", "hardware-front"),
        (f"DRAFT-R1.6-{surface_id}-texture-coupon.png", "coupon"),
    )
    for filename, view in renders:
        subprocess.run([
            sys.executable,
            str(ROOT / "src" / "render_stl.py"),
            str(ROOT / "reports" / filename),
            "--view",
            view,
            "--surface",
            surface_id,
        ], cwd=ROOT, check=True, shell=False)
    subprocess.run([sys.executable, str(ROOT / "src" / "watermark_evidence.py")], cwd=ROOT, check=True, shell=False)
    subprocess.run([
        sys.executable,
        str(ROOT / "src" / "package_release.py"),
        "--surface",
        surface_id,
    ], cwd=ROOT, check=True, shell=False)
    print(f"Rebuild complete for surface={surface_id}. See output/DRAFT, reports, and the profile-specific ZIP file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
