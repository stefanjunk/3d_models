#!/usr/bin/env python3
"""Author one revision 0.5.1 Berlin half as a native Anycubic 3MF."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS = PRODUCT / "source" / "v0.5.0" / "berlin" / "package_anycubic_site_marker_project.py"
PART_SUFFIXES = [
    "tool1-base",
    "tool2-relief",
    "tool3-streets",
    "tool4-boundary-marker",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_previous():
    spec = importlib.util.spec_from_file_location("mm_art_010_package_v050", PREVIOUS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load previous packager: {PREVIOUS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_filament_profiles(base_profile: Path, directory: Path, preset: str, colors: list[dict]) -> list[Path]:
    base = json.loads(base_profile.read_text())
    outputs = []
    for entry in colors:
        index = int(entry["order"])
        data = dict(base)
        profile_name = f"MM-ART-010 Berlin {entry['name']}"
        color = entry["display_hex"]
        data.update(
            {
                "name": profile_name,
                "from": "user",
                "is_custom_defined": "1",
                "setting_id": f"MMART010-051-{preset}-{index}",
                "filament_id": f"MMART010-051-{preset}-{index}",
                "filament_settings_id": [profile_name],
                "filament_colour": [color],
                "default_filament_colour": [color],
            }
        )
        path = directory / f"filament-{index}.json"
        path.write_text(json.dumps(data, indent=2) + "\n")
        outputs.append(path)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--mode", choices=("boundary-crop", "context-outline"), required=True)
    parser.add_argument("--half", choices=("left", "right"), required=True)
    parser.add_argument("--palette", default="berlin_oak_mint_midnight_sky")
    parser.add_argument("--slicer", type=Path, required=True)
    parser.add_argument("--machine-profile", type=Path, required=True)
    parser.add_argument("--process-profile", type=Path, required=True)
    parser.add_argument("--filament-profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    previous = load_previous()
    _, colors = previous.load_palette(args.palette)
    export_root = PRODUCT / "exports" / "v0.5.1" / "berlin" / args.candidate / args.mode
    prefix = f"berlin-{args.mode}-{args.half}"
    inputs = [export_root / f"{prefix}-{suffix}.stl" for suffix in PART_SUFFIXES]
    required = [
        args.slicer,
        args.machine_profile,
        args.process_profile,
        args.filament_profile,
        *inputs,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing required input(s): {missing}")
    if args.output.exists() or args.report.exists():
        raise SystemExit("refusing destructive overwrite of existing 3MF or report")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    mesh_metrics = [previous.serialized_mesh_metrics(path) for path in inputs]
    if not all(item["watertight"] and item["positive_volume"] for item in mesh_metrics):
        raise SystemExit("one or more source STL tool bodies failed serialized mesh checks")
    bed_min_x, bed_min_y, bed_max_x, bed_max_y = previous.parse_bed_bounds(args.machine_profile)
    source_min, source_max = previous.source_bounds(inputs)
    width = float(source_max[0] - source_min[0])
    height = float(source_max[1] - source_min[1])
    if width > bed_max_x - bed_min_x or height > bed_max_y - bed_min_y:
        raise SystemExit(f"source bounds {width:.3f} x {height:.3f} mm exceed configured bed")
    translate_x = (bed_min_x + bed_max_x - source_min[0] - source_max[0]) / 2.0
    translate_y = (bed_min_y + bed_max_y - source_min[1] - source_max[1]) / 2.0

    with tempfile.TemporaryDirectory(prefix="mm-art-010-051-anycubic-") as temporary:
        temporary_dir = Path(temporary)
        profiles = write_filament_profiles(
            args.filament_profile, temporary_dir, args.palette, colors
        )
        raw_project = temporary_dir / "raw-vendor-project.3mf"
        command = [
            str(args.slicer.resolve()),
            "--datadir",
            str(temporary_dir / "datadir"),
            "--load-settings",
            f"{args.process_profile.resolve()};{args.machine_profile.resolve()}",
            "--load-filaments",
            ";".join(str(path) for path in profiles),
            "--load-filament-ids",
            "1,2,3,4",
            "--arrange",
            "0",
            "--assemble",
            "--export-3mf",
            str(raw_project),
            *(str(path.resolve()) for path in inputs),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0 or not raw_project.is_file() or raw_project.stat().st_size == 0:
            raise SystemExit(
                f"Anycubic project export failed with {completed.returncode}:\n"
                f"stdout={completed.stdout}\nstderr={completed.stderr}"
            )
        normalization = previous.normalize_project(
            raw_project,
            args.output,
            translate_x,
            translate_y,
            colors,
            [path.name for path in inputs],
        )

    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1",
        "candidate": args.candidate,
        "mode": args.mode,
        "half": args.half,
        "palette_preset": args.palette,
        "palette_catalog_sha256": sha256(previous.PALETTE_CATALOG_PATH),
        "status": "PASS",
        "representation": "native Anycubic Slicer Next project 3MF with four aligned named mesh volumes",
        "output": {
            "path": str(args.output.resolve()),
            "bytes": args.output.stat().st_size,
            "sha256": sha256(args.output),
        },
        "source_bounds_mm": [source_min.tolist(), source_max.tolist()],
        "source_parts": [
            {
                "tool": index,
                "filament": colors[index - 1],
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "mesh": metrics,
            }
            for index, (path, metrics) in enumerate(
                zip(inputs, mesh_metrics, strict=True), start=1
            )
        ],
        "toolchain": {
            "packager": str(Path(__file__).resolve()),
            "packager_sha256": sha256(Path(__file__).resolve()),
            "slicer": str(args.slicer.resolve()),
            "slicer_sha256": sha256(args.slicer),
            "machine_profile": str(args.machine_profile.resolve()),
            "machine_profile_sha256": sha256(args.machine_profile),
            "process_profile": str(args.process_profile.resolve()),
            "process_profile_sha256": sha256(args.process_profile),
            "base_filament_profile": str(args.filament_profile.resolve()),
            "base_filament_profile_sha256": sha256(args.filament_profile),
        },
        "normalization": normalization,
        "limitations": [
            "Final physical ACE slot identity and directed purge review remain human-controlled.",
            "The generic Anycubic PLA profile is provisional for the four SUNLU PLA-family rolls.",
            "No printer upload or print start is performed by this script.",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "output": str(args.output), "report": str(args.report)}))


if __name__ == "__main__":
    main()
