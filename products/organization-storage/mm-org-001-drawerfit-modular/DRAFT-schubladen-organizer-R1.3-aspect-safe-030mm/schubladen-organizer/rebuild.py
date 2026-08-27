#!/usr/bin/env python3
"""One-command relief image registration, preparation, geometry build, and validation.

Usage:
    python3 rebuild.py /path/to/new-texture.png

All physical sizes, PPI/pitch values, relief depths, mappings, output names, and
memory-efficiency settings are read from the versioned project parameter files.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_python_packages(*, r2: bool = False) -> None:
    required = ("numpy",) if r2 else ("numpy", "PIL")
    missing = [name for name in required if importlib.util.find_spec(name) is None]
    if missing:
        raise SystemExit(
            "Missing Python dependencies. Run: python3 -m pip install -r requirements.txt"
        )


def ensure_node_dependencies() -> None:
    if (ROOT / "node_modules" / "manifold-3d").is_dir():
        return
    print("Installing locked Node.js dependencies (first rebuild only)...", flush=True)
    subprocess.run(["npm", "ci"], cwd=ROOT, check=True, shell=False)


def select_rebuild_route(model_revision: str) -> str:
    return "r2-procedural-wood-draft" if model_revision.startswith("R2-procedural-wood") else "legacy-r1-relief"


def validate_r2_arguments(image: Path | None, prepare_only: bool) -> None:
    if image is not None or prepare_only:
        raise ValueError(
            "R2 procedural wood has no raster/heightmap preparation route; "
            "positional images and --prepare-only are rejected. Run `python3 rebuild.py` with no image."
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace the texture image and rebuild the complete organizer from saved parameters."
    )
    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        help="New PNG/JPEG/TIFF texture. Omit to rebuild from the registered source master.",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Register/process the image and regenerate the continuous heightfield, but skip CAD exports.",
    )
    args = parser.parse_args()

    params = load_json(ROOT / "config" / "model-params.json")
    route = select_rebuild_route(str(params.get("model_revision", "")))
    if route == "r2-procedural-wood-draft":
        try:
            validate_r2_arguments(args.image, args.prepare_only)
        except ValueError as exc:
            parser.error(str(exc))
        require_python_packages(r2=True)
        ensure_node_dependencies()
        subprocess.run(
            [sys.executable, str(ROOT / "src" / "build_pipeline.py")],
            cwd=ROOT,
            check=True,
            shell=False,
        )
        print(
            "R2 DRAFT rebuild complete. No raster/heightmap or release ZIP route was called; "
            "see reports/build-pipeline-R2-procedural-wood-unmarked.json."
        )
        return 0

    # Explicit legacy non-R2 image/heightmap branch.
    require_python_packages()
    relief_cfg_path = ROOT / "config" / "relief-config.json"
    relief_cfg = load_json(relief_cfg_path)
    job_path = (relief_cfg_path.parent / relief_cfg["relief_job"]).resolve()

    command = [sys.executable, str(ROOT / "src" / "prepare_relief.py"), "--job", str(job_path)]
    if args.image:
        image = args.image.expanduser().resolve()
        if not image.is_file():
            raise SystemExit(f"Texture image not found: {image}")
        command.extend(["--source", str(image)])
    subprocess.run(command, cwd=ROOT, check=True, shell=False)

    metadata_path = (job_path.parent / load_json(job_path)["outputs"]["heightmap_metadata"]).resolve()
    subprocess.run(
        [sys.executable, str(ROOT / "src" / "validate_aspect_ratio.py"), str(metadata_path)],
        cwd=ROOT,
        check=True,
        shell=False,
    )

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "src" / "vectorize_heightmap.py"),
            str(relief_cfg_path),
            str((relief_cfg_path.parent / relief_cfg["manifest_output"]).resolve()),
            "--preview",
            str((relief_cfg_path.parent / relief_cfg["preview_output"]).resolve()),
        ],
        cwd=ROOT,
        check=True,
        shell=False,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "src" / "validate_aspect_diagnostic.py"), "--job", str(job_path)],
        cwd=ROOT,
        check=True,
        shell=False,
    )

    if args.prepare_only:
        print("Prepared and aspect-validated the source, 16-bit build heightmap, and geometry manifest.")
        return 0

    ensure_node_dependencies()
    subprocess.run([sys.executable, str(ROOT / "src" / "build_pipeline.py")], cwd=ROOT, check=True, shell=False)
    subprocess.run([sys.executable, str(ROOT / "src" / "package_release.py")], cwd=ROOT, check=True, shell=False)
    print("Rebuild complete. See output/DRAFT, reports/build-pipeline.json, and the revisioned ZIP.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
