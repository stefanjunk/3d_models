#!/usr/bin/env python3
"""Render all sample STLs/previews, split components, and write validation reports."""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog" / "catalog.json"
LOGS = ROOT / "validation" / "logs"
REPORTS = ROOT / "validation" / "samples"
PREVIEW_LOCK = threading.Lock()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_command(cmd: list[str], timeout: int) -> tuple[int, str, str, float]:
    start = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr, time.perf_counter() - start


def render_mesh_preview(stl_path: Path, preview_path: Path, max_faces: int = 35000) -> float:
    """Render a deterministic mesh preview without an X/OpenGL display."""
    start = time.perf_counter()
    cache_dir = Path(tempfile.gettempdir()) / "fdm-mechanics-matplotlib-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))
    with PREVIEW_LOCK:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        mesh = trimesh.load(stl_path, force="mesh", process=False)
        if not isinstance(mesh, trimesh.Trimesh):
            raise RuntimeError(f"Could not load mesh for preview: {stl_path}")
        if len(mesh.faces) > max_faces:
            indices = np.linspace(0, len(mesh.faces) - 1, max_faces, dtype=int)
        else:
            indices = np.arange(len(mesh.faces))
        triangles = mesh.vertices[mesh.faces[indices]]
        normals = mesh.face_normals[indices]
        light = np.array([-0.4, -0.6, 1.0], dtype=float)
        light /= np.linalg.norm(light)
        intensity = np.clip(0.30 + 0.70 * np.maximum(0.0, normals @ light), 0.22, 1.0)
        base_color = np.array([0.35, 0.58, 0.78])

        fig = plt.figure(figsize=(8, 6), dpi=100)
        axis = fig.add_subplot(111, projection="3d")
        collection = Poly3DCollection(triangles, linewidths=0.02, alpha=1.0)
        collection.set_facecolor(np.clip(intensity[:, None] * base_color[None, :], 0.0, 1.0))
        collection.set_edgecolor("none")
        axis.add_collection3d(collection)
        center = mesh.bounds.mean(axis=0)
        radius = max(mesh.extents) / 2 if max(mesh.extents) > 0 else 1.0
        axis.set_xlim(center[0] - radius, center[0] + radius)
        axis.set_ylim(center[1] - radius, center[1] + radius)
        axis.set_zlim(center[2] - radius, center[2] + radius)
        axis.set_box_aspect((1, 1, 1))
        axis.view_init(elev=28, azim=-135)
        axis.set_axis_off()
        fig.tight_layout(pad=0)
        fig.savefig(preview_path, bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
    return time.perf_counter() - start


def split_components(stl_path: Path, parts_dir: Path, expected_names: list[str]) -> dict[str, Any]:
    mesh = trimesh.load(stl_path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError(f"Could not load mesh from {stl_path}")
    components = list(mesh.split(only_watertight=False))
    # Stable order: print-plate rows first, then left to right. For overlapping PIP bodies,
    # larger volume first gives deterministic ordering.
    components.sort(key=lambda c: (round(float(c.centroid[1]) / 12.0), float(c.centroid[0]), -abs(float(c.volume))))
    parts_dir.mkdir(parents=True, exist_ok=True)
    for old in parts_dir.glob("part_*.stl"):
        old.unlink()
    info = []
    for index, component in enumerate(components, 1):
        original_bounds = np.asarray(component.bounds, dtype=float)
        original_centroid = np.asarray(component.centroid, dtype=float)
        translated = component.copy()
        translated.apply_translation(-original_bounds[0])
        out = parts_dir / f"part_{index:02d}.stl"
        translated.export(out, file_type="stl")
        name = f"Einzelkörper {index:02d}"
        info.append(
            {
                "index": index,
                "suggested_name": name,
                "file": out.name,
                "original_bounds_mm": original_bounds.round(5).tolist(),
                "original_centroid_mm": original_centroid.round(5).tolist(),
                "translation_to_origin_mm": (-original_bounds[0]).round(5).tolist(),
                "extents_mm": np.asarray(component.extents).round(5).tolist(),
                "faces": int(len(component.faces)),
                "vertices": int(len(component.vertices)),
                "watertight": bool(component.is_watertight),
                "winding_consistent": bool(component.is_winding_consistent),
                "euler_number": int(component.euler_number),
                "volume_mm3": float(abs(component.volume)),
                "surface_area_mm2": float(component.area),
                "sha256": sha256(out),
            }
        )
    degenerate = int(np.count_nonzero(mesh.area_faces < 1e-10))
    return {
        "combined": {
            "watertight": bool(mesh.is_watertight),
            "winding_consistent": bool(mesh.is_winding_consistent),
            "components": len(components),
            "faces": int(len(mesh.faces)),
            "vertices": int(len(mesh.vertices)),
            "euler_number": int(mesh.euler_number),
            "volume_mm3": float(abs(mesh.volume)),
            "surface_area_mm2": float(mesh.area),
            "bounds_mm": np.asarray(mesh.bounds).round(5).tolist(),
            "extents_mm": np.asarray(mesh.extents).round(5).tolist(),
            "z_min_mm": float(mesh.bounds[0][2]),
            "degenerate_faces": degenerate,
            "sha256": sha256(stl_path),
        },
        "components": info,
        "expected_component_names": expected_names,
        "component_name_count_matches": len(expected_names) == len(components),
    }


def build_one(record: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    sample_dir = ROOT / "samples" / record["relative_directory"]
    model = sample_dir / "model.scad"
    stl = sample_dir / "print_plate.stl"
    preview = sample_dir / "preview.png"
    parts_dir = sample_dir / "parts"
    sample_log = LOGS / record["id"]
    sample_report = REPORTS / f"{record['id']}.json"
    sample_log.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "id": record["id"],
        "title_de": record["title_de"],
        "variant_label_de": record["variant_label_de"],
        "relative_directory": record["relative_directory"],
        "status": "started",
        "errors": [],
    }
    try:
        if not args.skip_existing or not stl.exists() or stl.stat().st_size < 256:
            cmd = ["openscad", "-o", str(stl), "-D", f"render_fn={args.render_fn}", "-D", 'view="plate"', str(model)]
            rc, out, err, duration = run_command(cmd, args.timeout)
            (sample_log / "stl.stdout.txt").write_text(out, encoding="utf-8")
            (sample_log / "stl.stderr.txt").write_text(err, encoding="utf-8")
            result["stl_render_seconds"] = duration
            result["stl_command"] = cmd
            if rc != 0 or not stl.exists() or stl.stat().st_size < 256:
                raise RuntimeError(f"OpenSCAD STL render failed with exit code {rc}")
        else:
            result["stl_render_seconds"] = 0.0
            result["stl_reused"] = True

        component_report = split_components(stl, parts_dir, record["part_names"])
        (sample_dir / "components.json").write_text(json.dumps(component_report, ensure_ascii=False, indent=2), encoding="utf-8")
        result.update(component_report)

        if args.skip_previews:
            if not preview.exists() or preview.stat().st_size < 256:
                raise RuntimeError("Preview preservation requested, but no usable preview exists")
            result["preview_render_seconds"] = 0.0
            result["preview_preserved"] = True
        elif args.preview_backend == "mesh":
            for stale_log in (sample_log / "preview.stdout.txt", sample_log / "preview.stderr.txt"):
                if stale_log.exists():
                    stale_log.unlink()
            with tempfile.TemporaryDirectory(prefix=f"fdm-preview-{record['id']}-") as tmp:
                assembly_stl = Path(tmp) / "assembly.stl"
                cmd = [
                    "openscad",
                    "-o",
                    str(assembly_stl),
                    "-D",
                    f"render_fn={args.preview_fn}",
                    "-D",
                    'view="assembly"',
                    str(model),
                ]
                rc, out, err, assembly_duration = run_command(cmd, args.timeout)
                (sample_log / "preview-assembly.stdout.txt").write_text(out, encoding="utf-8")
                (sample_log / "preview-assembly.stderr.txt").write_text(err, encoding="utf-8")
                if rc != 0 or not assembly_stl.exists() or assembly_stl.stat().st_size < 256:
                    raise RuntimeError(f"OpenSCAD assembly STL render failed with exit code {rc}")
                mesh_duration = render_mesh_preview(assembly_stl, preview)
            result["preview_render_seconds"] = assembly_duration + mesh_duration
            result["preview_command"] = cmd
            result["preview_backend"] = "openscad-assembly-stl-plus-matplotlib-agg"
        elif not args.skip_existing or not preview.exists() or preview.stat().st_size < 256:
            xvfb = shutil.which("xvfb-run")
            base = ["openscad", "-o", str(preview), "--imgsize", args.imgsize, "--viewall", "--autocenter", "--projection", "o", "--camera", args.camera, "-D", f"render_fn={args.preview_fn}", "-D", 'view="assembly"', str(model)]
            cmd = ([xvfb, "-a"] + base) if xvfb else base
            rc, out, err, duration = run_command(cmd, args.timeout)
            (sample_log / "preview.stdout.txt").write_text(out, encoding="utf-8")
            (sample_log / "preview.stderr.txt").write_text(err, encoding="utf-8")
            result["preview_render_seconds"] = duration
            result["preview_command"] = cmd
            if rc != 0 or not preview.exists() or preview.stat().st_size < 256:
                raise RuntimeError(f"OpenSCAD preview render failed with exit code {rc}")
        else:
            result["preview_render_seconds"] = 0.0
            result["preview_reused"] = True

        combined = result["combined"]
        checks = {
            "combined_watertight": bool(combined["watertight"]),
            "combined_winding_consistent": bool(combined["winding_consistent"]),
            "all_components_watertight": all(c["watertight"] for c in result["components"]),
            "all_components_positive_volume": all(c["volume_mm3"] > 0.01 for c in result["components"]),
            "no_degenerate_faces": combined["degenerate_faces"] == 0,
            "on_or_above_build_plate": combined["z_min_mm"] >= -0.03,
            "fits_220mm_bed": max(combined["extents_mm"][0], combined["extents_mm"][1]) <= 220.0,
            "component_count_matches_documentation": bool(result["component_name_count_matches"]),
        }
        result["checks"] = checks
        result["status"] = "passed" if all(checks.values()) else "warning"
    except subprocess.TimeoutExpired as exc:
        result["status"] = "failed"
        result["errors"].append(f"Timeout after {exc.timeout} seconds")
    except Exception as exc:  # noqa: BLE001
        result["status"] = "failed"
        result["errors"].append(str(exc))
        result["traceback"] = traceback.format_exc()
    sample_report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--render-fn", type=int, default=48)
    parser.add_argument("--preview-fn", type=int, default=28)
    parser.add_argument("--imgsize", default="800,600")
    parser.add_argument("--camera", default="0,0,0,58,0,28,165")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--skip-previews",
        action="store_true",
        help="Preserve existing previews when a headless OpenGL renderer is unavailable",
    )
    parser.add_argument(
        "--preview-backend",
        choices=("openscad", "mesh"),
        default="openscad",
        help="Use OpenSCAD assembly PNGs or a headless assembly-STL mesh preview",
    )
    parser.add_argument("--ids", default="", help="Comma-separated sample IDs")
    parser.add_argument(
        "--summary",
        default="validation/build-summary.json",
        help="Project-relative path for the aggregate build report",
    )
    args = parser.parse_args()

    LOGS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    records = json.loads(CATALOG.read_text(encoding="utf-8"))
    if args.ids:
        wanted = {x.strip().zfill(3) for x in args.ids.split(",") if x.strip()}
        records = [r for r in records if r["id"] in wanted]

    results: list[dict[str, Any]] = []
    with futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        pending = {pool.submit(build_one, record, args): record for record in records}
        for future in futures.as_completed(pending):
            record = pending[future]
            try:
                result = future.result()
            except Exception as exc:  # defensive wrapper
                result = {"id": record["id"], "status": "failed", "errors": [repr(exc)]}
            results.append(result)
            combined = result.get("combined", {})
            print(
                f"[{result['id']}] {result['status']:<7} "
                f"parts={combined.get('components', '-')} faces={combined.get('faces', '-')} "
                f"stl={result.get('stl_render_seconds', 0):.1f}s png={result.get('preview_render_seconds', 0):.1f}s",
                flush=True,
            )

    results.sort(key=lambda r: r["id"])
    summary = {
        "samples_requested": len(records),
        "passed": sum(r.get("status") == "passed" for r in results),
        "warning": sum(r.get("status") == "warning" for r in results),
        "failed": sum(r.get("status") == "failed" for r in results),
        "results": results,
    }
    summary_path = ROOT / args.summary
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["samples_requested", "passed", "warning", "failed"]}, ensure_ascii=False))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
