#!/usr/bin/env python3
"""Create a non-print inspection assembly that exposes every measured R7 datum."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import trimesh

from generate_r7_z_rider import (
    build_catcher,
    build_datum_plate,
    shape_triangles,
    write_core_3mf,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict:
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def shape_mesh(shape, tolerance: float, angular_tolerance: float) -> trimesh.Trimesh:
    vertices, faces = shape_triangles(shape, tolerance, angular_tolerance)
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)


def guide_box(extents: list[float], center: list[float]) -> trimesh.Trimesh:
    transform = trimesh.transformations.translation_matrix(center)
    return trimesh.creation.box(extents=extents, transform=transform)


def measurement_guides(params: dict) -> list[trimesh.Trimesh]:
    """Disjoint, offset guide bars whose exact lengths are 17/10/37/40 mm."""
    measured = params["measured_datums"]
    pitch = float(measured["screw_pitch_z_mm"])
    purge_z = float(measured["lower_screw_to_purge_deposition_plane_mm"])
    throw_x = float(measured["screw_datum_to_purge_throw_plane_x_mm"])
    rear_y = float(measured["screw_plane_to_rear_wiper_extent_mm"])
    return [
        guide_box([1.0, 1.0, pitch], [-11.5, 3.5, pitch / 2.0]),
        guide_box([1.0, 1.0, purge_z], [-13.5, 3.5, -purge_z / 2.0]),
        guide_box([throw_x, 1.0, 1.0], [throw_x / 2.0, -1.5, -14.5]),
        guide_box([1.0, rear_y, 1.0], [-11.5, -rear_y / 2.0, -1.5]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--machine-profile", required=True, type=Path)
    parser.add_argument("--process-profile", required=True, type=Path)
    parser.add_argument("--filament-profile", required=True, type=Path)
    parser.add_argument("--slicer", default=shutil.which("AnycubicSlicerNext"))
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    params_path = PROJECT_ROOT / "params" / "r7-z-rider-draft2.json"
    params = json.loads(params_path.read_text(encoding="utf-8"))
    manufacturing = params["manufacturing"]
    tolerance = float(manufacturing["stl_linear_tolerance_mm"])
    angular_tolerance = float(manufacturing["stl_angular_tolerance_rad"])
    clearance = float(params["lateral_guides"]["default_clearance_mm"])

    datum_plate, _, _ = build_datum_plate(params)
    catcher, _ = build_catcher(params, clearance)
    plate_mesh = shape_mesh(datum_plate, tolerance, angular_tolerance)
    catcher_mesh = shape_mesh(catcher, tolerance, angular_tolerance)
    guide_meshes = measurement_guides(params)
    assembly_mesh = trimesh.util.concatenate([plate_mesh, catcher_mesh, *guide_meshes])

    core_3mf = build_dir / "models" / "3mf" / "INSPECTION-R7-measured-assembly-reference.3mf"
    reference_stl = build_dir / "models" / "reference" / "INSPECTION-R7-measured-assembly-reference.stl"
    anycubic_3mf = (
        build_dir
        / "models"
        / "3mf"
        / "anycubic"
        / "ANYCUBIC-R7-INSPECTION-measured-assembly-reference.3mf"
    )
    report_path = build_dir / "reports" / "measured-assembly-reference-export.json"
    targets = [core_3mf, reference_stl, anycubic_3mf, report_path]
    existing = [str(path) for path in targets if path.exists()]
    if existing:
        raise SystemExit(f"Refusing to overwrite existing inspection artifact(s): {existing}")
    for path in targets:
        path.parent.mkdir(parents=True, exist_ok=True)

    write_core_3mf(
        core_3mf,
        "R7-DRAFT-2 INSPECTION assembly in measured machine coordinates — DO NOT PRINT",
        [plate_mesh, catcher_mesh, *guide_meshes],
    )
    assembly_mesh.export(reference_stl, file_type="stl")

    slicer = Path(args.slicer).resolve() if args.slicer else None
    profiles = [
        args.machine_profile.resolve(),
        args.process_profile.resolve(),
        args.filament_profile.resolve(),
    ]
    required = [params_path, reference_stl, *profiles]
    if slicer is None:
        raise SystemExit("AnycubicSlicerNext executable not found")
    required.append(slicer)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing required input(s): {missing}")

    state_dir = build_dir / "anycubic-export-state" / "inspection-assembly"
    state_dir.mkdir(parents=True, exist_ok=False)
    command = [
        str(slicer),
        "--datadir",
        str(state_dir),
        "--load-settings",
        f"{profiles[1]};{profiles[0]}",
        "--load-filaments",
        str(profiles[2]),
        "--load-defaultfila",
        "--ensure-on-bed",
        "--arrange",
        "1",
        "--export-3mf",
        str(anycubic_3mf),
        str(reference_stl),
    ]
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    passed = run.returncode == 0 and anycubic_3mf.is_file() and anycubic_3mf.stat().st_size > 0
    help_run = subprocess.run([str(slicer), "--help"], capture_output=True, text=True, check=False)
    version_match = re.search(r"AnycubicSlicerNext-([^:\s]+)", help_run.stdout + help_run.stderr)
    report = {
        "schema_version": "1.0",
        "status": "PASS" if passed else "FAIL",
        "geometry_revision": params["geometry_revision"],
        "purpose": "Visual inspection of datum plate and catcher together in the measured machine coordinate frame",
        "manufacturing_status": "REFERENCE_ONLY_DO_NOT_PRINT",
        "coordinate_system": params["coordinate_system"],
        "measured_datums_mm": params["measured_datums"],
        "measurement_guides": {
            "description": "Four disjoint offset bars; each bar length equals its declared 17/10/37/40 mm datum.",
            "manufacturing_geometry": False,
        },
        "component_count": len(assembly_mesh.split(only_watertight=False)),
        "inputs": {
            "parameters": file_record(params_path),
            "source": file_record(Path(__file__)),
            "machine_profile": file_record(profiles[0]),
            "process_profile": file_record(profiles[1]),
            "filament_profile": file_record(profiles[2]),
        },
        "outputs": {
            "reference_stl": file_record(reference_stl),
            "core_3mf": file_record(core_3mf),
            "anycubic_3mf": file_record(anycubic_3mf) if anycubic_3mf.exists() else None,
        },
        "slicer": {
            "version": version_match.group(1) if version_match else "unknown",
            "return_code": run.returncode,
            "invocation": command,
            "stdout": run.stdout,
            "stderr": run.stderr,
        },
        "limitations": [
            "The Anycubic project may translate the whole assembly onto the bed; relative component geometry is preserved.",
            "This assembly intentionally contains mounted components and is not a manufacturing plate.",
            "Physical fit, screw engagement and machine clearance remain unverified.",
            "No upload or print-start action is performed.",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(report_path)}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
