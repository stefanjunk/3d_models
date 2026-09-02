#!/usr/bin/env python3
"""Author one Berlin 0.5.0 half as a native Anycubic four-volume 3MF."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import trimesh
import yaml

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PALETTE_CATALOG_PATH = PRODUCT / "palette-catalog.yaml"
PART_SUFFIXES = [
    "tool1-base",
    "tool2-relief",
    "tool3-streets",
    "tool4-boundary-marker",
]
SEMANTIC_NAMES = [
    "Tool 1 Base",
    "Tool 2 Relief and Areas",
    "Tool 3 Street Network",
    "Tool 4 Boundary Accents and Site Marker",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_bed_bounds(machine_profile: Path) -> tuple[float, float, float, float]:
    profile = json.loads(machine_profile.read_text())
    points = profile.get("printable_area")
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError("machine profile has no usable printable_area polygon")
    coordinates = []
    for point in points:
        match = re.fullmatch(r"\s*([-+0-9.]+)x([-+0-9.]+)\s*", str(point))
        if not match:
            raise ValueError(f"unrecognized printable_area point: {point!r}")
        coordinates.append((float(match.group(1)), float(match.group(2))))
    xs = [point[0] for point in coordinates]
    ys = [point[1] for point in coordinates]
    return min(xs), min(ys), max(xs), max(ys)


def serialized_mesh_metrics(path: Path) -> dict:
    raw = trimesh.load_mesh(path, process=False)
    mesh = trimesh.Trimesh(
        vertices=np.asarray(raw.vertices, dtype=np.float64),
        faces=np.asarray(raw.faces, dtype=np.int64),
        process=True,
    )
    return {
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
        "volume_mm3": float(mesh.volume),
        "bounds_mm": np.asarray(mesh.bounds, dtype=float).tolist(),
    }


def source_bounds(paths: list[Path]) -> tuple[np.ndarray, np.ndarray]:
    bounds = [np.asarray(trimesh.load_mesh(path, process=False).bounds) for path in paths]
    stacked = np.stack(bounds)
    return np.min(stacked[:, 0, :], axis=0), np.max(stacked[:, 1, :], axis=0)


def load_palette(preset: str) -> tuple[dict, list[dict]]:
    catalog = yaml.safe_load(PALETTE_CATALOG_PATH.read_text())
    if preset not in catalog["presets"]:
        raise ValueError(f"palette preset is not registered: {preset}")
    colors = sorted(catalog["presets"][preset]["colors"], key=lambda item: item["order"])
    if [entry["order"] for entry in colors] != [1, 2, 3, 4]:
        raise ValueError("palette must define exactly tools 1 through 4")
    return catalog, colors


def write_filament_profiles(
    base_profile: Path, directory: Path, preset: str, colors: list[dict]
) -> list[Path]:
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
                "setting_id": f"MMART010-050-{preset}-{index}",
                "filament_id": f"MMART010-050-{preset}-{index}",
                "filament_settings_id": [profile_name],
                "filament_colour": [color],
                "default_filament_colour": [color],
            }
        )
        path = directory / f"filament-{index}.json"
        path.write_text(json.dumps(data, indent=2) + "\n")
        outputs.append(path)
    return outputs


def normalize_project(
    raw_project: Path,
    final_project: Path,
    translate_x: float,
    translate_y: float,
    colors: list[dict],
    source_names: list[str],
) -> dict:
    display_colors = [entry["display_hex"] for entry in colors]
    profile_names = [f"MM-ART-010 Berlin {entry['name']}" for entry in colors]
    volume_names = [
        f"{semantic} — {entry['name']}"
        for semantic, entry in zip(SEMANTIC_NAMES, colors, strict=True)
    ]
    old_transform = b'transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"'
    new_transform = (
        f'transform="1 0 0 0 1 0 0 0 1 {translate_x:.6f} '
        f'{translate_y:.6f} 0" printable="1"'
    ).encode("ascii")
    extruders: list[int] = []
    with zipfile.ZipFile(raw_project) as source, zipfile.ZipFile(
        final_project, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == "3D/3dmodel.model":
                if data.count(old_transform) != 1:
                    raise ValueError("expected one identity build transform in Anycubic project")
                data = data.replace(old_transform, new_transform)
            elif info.filename == "Metadata/project_settings.config":
                settings = json.loads(data)
                for key, value in list(settings.items()):
                    if key.startswith("filament_") and isinstance(value, list) and len(value) == 1:
                        settings[key] = value * 4
                settings["filament_colour"] = display_colors
                settings["default_filament_colour"] = display_colors
                settings["default_filament_profile"] = profile_names
                settings["filament_settings_id"] = profile_names
                data = (json.dumps(settings, indent=4, ensure_ascii=False) + "\n").encode()
            elif info.filename == "Metadata/model_settings.config":
                text = data.decode("utf-8")
                extruders = [
                    int(value)
                    for value in re.findall(r'key="extruder" value="(\d+)"', text)
                ]
                for source_name, volume_name in zip(
                    source_names, volume_names, strict=True
                ):
                    text = text.replace(
                        f'key="name" value="{source_name}"',
                        f'key="name" value="{volume_name}"',
                    )
                data = text.encode("utf-8")
            target.writestr(info, data)
    if extruders != [1, 2, 3, 4]:
        raise ValueError(f"expected extruder assignments [1, 2, 3, 4], got {extruders}")
    return {
        "build_translation_mm": [translate_x, translate_y, 0.0],
        "extruder_assignments": extruders,
        "filament_profile_names": profile_names,
        "volume_names": volume_names,
        "display_colors": display_colors,
    }


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

    catalog, colors = load_palette(args.palette)
    export_root = PRODUCT / "exports" / "v0.5.0" / "berlin" / args.candidate / args.mode
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

    mesh_metrics = [serialized_mesh_metrics(path) for path in inputs]
    if not all(item["watertight"] and item["positive_volume"] for item in mesh_metrics):
        raise SystemExit("one or more source STL tool bodies failed serialized mesh checks")
    bed_min_x, bed_min_y, bed_max_x, bed_max_y = parse_bed_bounds(args.machine_profile)
    source_min, source_max = source_bounds(inputs)
    width = float(source_max[0] - source_min[0])
    height = float(source_max[1] - source_min[1])
    if width > bed_max_x - bed_min_x or height > bed_max_y - bed_min_y:
        raise SystemExit(f"source bounds {width:.3f} x {height:.3f} mm exceed configured bed")
    translate_x = (bed_min_x + bed_max_x - source_min[0] - source_max[0]) / 2.0
    translate_y = (bed_min_y + bed_max_y - source_min[1] - source_max[1]) / 2.0

    with tempfile.TemporaryDirectory(prefix="mm-art-010-050-anycubic-") as temporary:
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
        normalization = normalize_project(
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
        "revision": "0.5.0",
        "candidate": args.candidate,
        "mode": args.mode,
        "half": args.half,
        "palette_preset": args.palette,
        "palette_catalog_sha256": sha256(PALETTE_CATALOG_PATH),
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
            "The native project embeds volume tools and palette names/colors; final physical ACE slot identity and directed purge review remain human-controlled.",
            "The generic Anycubic PLA profile is provisional for all four SUNLU PLA-family rolls; physical conditioning and process qualification remain open.",
            "No printer upload or print start is performed by this script.",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "output": str(args.output), "report": str(args.report)}))


if __name__ == "__main__":
    main()
