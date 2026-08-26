#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import subprocess
import sys

from _relief_utils import read_json, sha256_file, write_json


def resolve(job_dir: Path, value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value)
    return p if p.is_absolute() else job_dir / p


def main() -> int:
    p = argparse.ArgumentParser(description="Rebuild a relief job from its immutable source master; optionally register a replacement first.")
    p.add_argument("job_json")
    p.add_argument("--source", help="Replacement raw source image")
    p.add_argument("--register-source", action="store_true", help="Register --source into the canonical 16-bit source master before rebuilding")
    p.add_argument("--source-kind", default="supplied")
    p.add_argument("--source-fit", choices=["contain", "cover", "crop", "stretch"])
    p.add_argument("--allow-aspect-distortion", action="store_true")
    p.add_argument("--run-geometry", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    job_path = Path(args.job_json).resolve()
    job_dir = job_path.parent
    job = read_json(job_path)
    scripts = Path(__file__).resolve().parent

    source_cfg = job["source"]
    target = job["target"]
    image = job["image"]
    relief = job["relief"]
    build = job["build"]

    source_spec = resolve(job_dir, source_cfg["spec"])
    source_master = resolve(job_dir, source_cfg["master"])
    source_manifest = resolve(job_dir, source_cfg["manifest"])
    heightmap = resolve(job_dir, build["heightmap"])
    heightmap_meta = resolve(job_dir, build["heightmap_metadata"])
    preview = resolve(job_dir, build.get("preview"))
    build_manifest = resolve(job_dir, build.get("manifest"))

    if args.source and not args.register_source:
        raise SystemExit("A raw replacement requires --register-source. This prevents accidentally bypassing source-master normalization.")

    if args.register_source:
        if not args.source:
            raise SystemExit("--register-source requires --source")
        reg = [
            sys.executable, str(scripts / "register_source_master.py"),
            str(Path(args.source).resolve()), str(source_master),
            "--spec", str(source_spec),
            "--source-kind", args.source_kind,
        ]
        if args.source_fit:
            reg += ["--fit", args.source_fit]
        if args.allow_aspect_distortion:
            reg.append("--allow-aspect-distortion")
        print("REGISTER:", shlex.join(reg))
        if not args.dry_run:
            subprocess.run(reg, check=True)

    if not source_master or not source_master.is_file():
        raise SystemExit(f"Source master does not exist: {source_master}. Register a source first.")
    if not source_manifest or not source_manifest.is_file():
        raise SystemExit(f"Source manifest does not exist: {source_manifest}. Re-register the source master.")

    prep = [
        sys.executable, str(scripts / "prepare_heightmap.py"),
        str(source_master), str(heightmap),
        "--source-manifest", str(source_manifest),
        "--size-mm", f"{target['width_mm']}x{target['height_mm']}",
        "--pitch-mm", f"{target['pitch_x_mm']}x{target['pitch_y_mm']}",
        "--axis-mode", str(target.get("axis_mode", "xy-z")),
        "--fit", str(image.get("fit_mode", "contain")),
        "--image-class", str(image.get("class", "subject")),
        "--surface-type", str(target.get("surface_type", "plane")),
        "--placement-mode", str(target.get("placement_mode", "single_patch")),
        "--aspect-policy", str(image.get("aspect_policy", "preserve")),
        "--aspect-tolerance-pct", str(image.get("aspect_tolerance_pct", 1.0)),
        "--black-point", str(image.get("black_point", 0.0)),
        "--white-point", str(image.get("white_point", 1.0)),
        "--gamma", str(image.get("gamma", 1.0)),
        "--background", str(image.get("background", 0.0)),
    ]
    if image.get("tile_mm"):
        prep += ["--tile-mm", f"{image['tile_mm'][0]}x{image['tile_mm'][1]}"]
    if image.get("invert"):
        prep.append("--invert")
    if image.get("allow_aspect_distortion") or args.allow_aspect_distortion:
        prep.append("--allow-aspect-distortion")
    if preview:
        prep += ["--preview", str(preview)]
    print("PREPARE:", shlex.join(prep))
    if not args.dry_run:
        subprocess.run(prep, check=True)

    if not args.dry_run:
        built_meta = read_json(heightmap_meta)
        bm = {
            "schema": "heightmap-relief-build-manifest-v2.4",
            "job_path": str(job_path),
            "job_sha256": sha256_file(job_path),
            "source_master": str(source_master),
            "source_master_sha256": sha256_file(source_master),
            "source_manifest": str(source_manifest),
            "heightmap": str(heightmap),
            "heightmap_sha256": sha256_file(heightmap),
            "heightmap_metadata": str(heightmap_meta),
            "aspect_validation": built_meta.get("aspect_validation"),
            "relief": relief,
            "complexity_budget": job.get("complexity_budget"),
            "mesh_acceptance": job.get("mesh_acceptance"),
            "mesh_artifacts": {
                "reference_mesh": job.get("geometry", {}).get("reference_mesh_path"),
                "manufacturing_mesh": job.get("geometry", {}).get("manufacturing_mesh_path"),
                "comparison_report": job.get("geometry", {}).get("comparison_report_path"),
                "budget_report": job.get("geometry", {}).get("budget_report_path"),
                "slicer_report": job.get("geometry", {}).get("slicer_report_path"),
            },
        }
        if build_manifest:
            write_json(build_manifest, bm)

    if args.run_geometry:
        geo = job.get("geometry", {})
        command = geo.get("command") or []
        if not command:
            raise SystemExit("--run-geometry requested but geometry.command is empty in relief-job.json")
        mapping = {
            "heightmap": str(heightmap),
            "processed_image": str(heightmap),
            "heightmap_metadata": str(heightmap_meta),
            "build_manifest": str(build_manifest) if build_manifest else "",
            "source": str(source_master),
            "source_image": str(source_master),
            "source_manifest": str(source_manifest),
            "job": str(job_path),
            "job_json": str(job_path),
            "job_dir": str(job_dir),
            "output_model": str(resolve(job_dir, geo.get("output_path")) or ""),
            "reference_mesh": str(resolve(job_dir, geo.get("reference_mesh_path")) or ""),
            "manufacturing_mesh": str(resolve(job_dir, geo.get("manufacturing_mesh_path")) or ""),
            "mesh_comparison_report": str(resolve(job_dir, geo.get("comparison_report_path")) or ""),
            "mesh_budget_report": str(resolve(job_dir, geo.get("budget_report_path")) or ""),
            "slicer_report": str(resolve(job_dir, geo.get("slicer_report_path")) or ""),
            "mode": str(relief.get("mode", "engrave")),
            "depth_mm": str(relief.get("depth_mm", 0.4)),
        }
        rendered = [str(x).format(**mapping) for x in command]
        cwd = resolve(job_dir, geo.get("cwd", ".")) or job_dir
        print("GEOMETRY:", shlex.join(rendered))
        if not args.dry_run:
            subprocess.run(rendered, cwd=cwd, check=True)

    if not args.dry_run:
        meta = read_json(heightmap_meta)
        av = meta.get("aspect_validation", {})
        print(
            f"Rebuild complete. Physical aspect error={av.get('error_pct', 'n/a')}% "
            f"passed={av.get('passed', 'n/a')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
