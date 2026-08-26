#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from _relief_utils import recommend_pitch, write_json


def pair(text: str) -> tuple[float, float]:
    a, b = text.lower().replace(",", "x").split("x", 1)
    return float(a), float(b)


def main() -> int:
    p = argparse.ArgumentParser(description="Initialize a source-swappable relief job with aspect-preserving defaults.")
    p.add_argument("job_dir")
    p.add_argument("--name", required=True)
    p.add_argument("--target-size-mm", required=True, type=pair)
    p.add_argument("--source-size-mm", required=True, type=pair)
    p.add_argument("--authoring-ppi", type=float, help="Source-master PPI. Default: max(300, 1.5x the finer target-build PPI).")
    p.add_argument("--description", required=True)
    p.add_argument("--image-class", default="subject")
    p.add_argument("--surface-type", default="plane")
    p.add_argument("--placement-mode", default="single_patch")
    p.add_argument("--repeating", action="store_true")
    p.add_argument("--seamless-x", action="store_true")
    p.add_argument("--seamless-y", action="store_true")
    p.add_argument("--process", default="fdm")
    p.add_argument("--nozzle-mm", type=float, default=0.4)
    p.add_argument("--layer-height-mm", type=float, default=0.2)
    p.add_argument("--resin-xy-mm", type=float, default=0.05)
    p.add_argument("--axis-mode", default="xy-z")
    p.add_argument("--fit", default=None)
    p.add_argument("--tile-mm", type=pair)
    p.add_argument("--mode", default="engrave", choices=["engrave", "emboss"])
    p.add_argument("--depth-mm", type=float, default=0.4)
    p.add_argument("--wall-thickness-mm", type=float, default=2.0)
    p.add_argument("--triangle-target", required=True, type=int)
    p.add_argument("--triangle-stop", required=True, type=int)
    p.add_argument("--memory-budget-gib", required=True, type=float)
    p.add_argument("--max-mesh-mib", required=True, type=float)
    p.add_argument("--max-slicer-seconds", required=True, type=float)
    p.add_argument("--working-bytes-per-triangle", type=float, default=1024.0)
    args = p.parse_args()

    if not 0 < args.triangle_target < args.triangle_stop:
        p.error("require 0 < --triangle-target < --triangle-stop")
    for name in ("memory_budget_gib", "max_mesh_mib", "max_slicer_seconds", "working_bytes_per_triangle"):
        if getattr(args, name) <= 0:
            p.error(f"--{name.replace('_', '-')} must be greater than zero")

    job_dir = Path(args.job_dir)
    source_dir = job_dir / "source"
    build_dir = job_dir / "build"
    source_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    tw, th = args.target_size_mm
    rec = recommend_pitch(tw, th, args.process, args.nozzle_mm, args.layer_height_mm, args.resin_xy_mm, args.axis_mode)
    authoring_ppi = args.authoring_ppi if args.authoring_ppi is not None else max(300.0, 1.5 * max(rec.dpi_x, rec.dpi_y))

    script_dir = Path(__file__).resolve().parent
    source_spec = source_dir / "source-spec.json"
    prompt_path = source_dir / "generation-prompt.txt"
    cmd = [
        sys.executable, str(script_dir / "plan_ai_source.py"),
        "--size-mm", f"{args.source_size_mm[0]}x{args.source_size_mm[1]}",
        "--authoring-ppi", str(authoring_ppi),
        "--image-class", args.image_class,
        "--description", args.description,
        "--output-json", str(source_spec),
        "--output-prompt", str(prompt_path),
    ]
    if args.seamless_x:
        cmd.append("--seamless-x")
    if args.seamless_y:
        cmd.append("--seamless-y")
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    texture_class = args.image_class.lower() in {"texture", "pattern", "wood", "carbon", "fabric", "stone"}
    fit = args.fit or ("repeat" if args.repeating or texture_class else "contain")

    job = {
        "schema": "heightmap-relief-job-v2.4",
        "name": args.name,
        "source": {
            "spec": "source/source-spec.json",
            "prompt": "source/generation-prompt.txt",
            "master": "source/source-master.png",
            "manifest": "source/source-master.png.source.json",
        },
        "target": {
            "width_mm": tw,
            "height_mm": th,
            "surface_type": args.surface_type,
            "placement_mode": args.placement_mode,
            "axis_mode": args.axis_mode,
            "pitch_x_mm": rec.pitch_x_mm,
            "pitch_y_mm": rec.pitch_y_mm,
            "dpi_x": rec.dpi_x,
            "dpi_y": rec.dpi_y,
        },
        "image": {
            "class": args.image_class,
            "repeating": bool(args.repeating),
            "fit_mode": fit,
            "tile_mm": list(args.tile_mm) if args.tile_mm else None,
            "aspect_policy": "preserve",
            "allow_aspect_distortion": False,
            "aspect_tolerance_pct": 0.75 if not texture_class else 1.5,
            "bit_depth": 16,
            "black_point": 0.0,
            "white_point": 1.0,
            "gamma": 1.0,
            "invert": False,
            "background": 0.0,
        },
        "printer": {
            "process": args.process,
            "nozzle_mm": args.nozzle_mm,
            "layer_height_mm": args.layer_height_mm,
            "resin_xy_mm": args.resin_xy_mm,
        },
        "relief": {
            "mode": args.mode,
            "depth_mm": args.depth_mm,
            "wall_thickness_mm": args.wall_thickness_mm,
        },
        "complexity_budget": {
            "triangle_target": args.triangle_target,
            "triangle_stop": args.triangle_stop,
            "memory_budget_gib": args.memory_budget_gib,
            "working_bytes_per_triangle": args.working_bytes_per_triangle,
            "max_mesh_mib": args.max_mesh_mib,
            "max_slicer_seconds": args.max_slicer_seconds,
        },
        "mesh_acceptance": {
            "max_abs_volume_delta_pct": 0.1,
            "min_relief_correlation": 0.98,
            "max_relief_contrast_loss_pct": 5.0,
            "max_rms_nozzle_fraction": 0.05,
        },
        "build": {
            "heightmap": "build/current-heightmap.png",
            "heightmap_metadata": "build/current-heightmap.png.json",
            "preview": "build/current-heightmap.preview.png",
            "manifest": "build/current-heightmap.build.json",
        },
        "geometry": {
            "reference_mesh_path": "build/reference-master-mesh.stl",
            "manufacturing_mesh_path": "build/manufacturing-mesh.stl",
            "comparison_report_path": "build/relief-mesh-comparison.json",
            "budget_report_path": "build/relief-mesh-budget.json",
            "slicer_report_path": "build/slicer-report.json",
            "output_path": "build/manufacturing-mesh.stl",
            "cwd": ".",
            "command": [],
        },
    }
    write_json(job_dir / "relief-job.json", job)
    print(f"Initialized: {job_dir / 'relief-job.json'}")
    print(f"Generation prompt: {prompt_path}")
    print("Aspect policy: preserve (physical millimetres; no silent stretch)")
    print("Mesh/resource budgets: explicit; reference and manufacturing meshes use separate paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
