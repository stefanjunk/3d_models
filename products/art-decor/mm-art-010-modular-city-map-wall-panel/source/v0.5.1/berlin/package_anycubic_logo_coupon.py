#!/usr/bin/env python3
"""Package the two-volume logo coupon with product tools 1 and 4."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PACKAGE_PROJECT = HERE / "package_anycubic_project.py"
PREVIOUS = PRODUCT / "source" / "v0.5.0" / "berlin" / "package_anycubic_site_marker_project.py"
PALETTE = "berlin_oak_mint_midnight_sky"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize(raw: Path, output: Path, tx: float, ty: float, colors: list[dict], source_names: list[str]) -> dict:
    display_colors = [entry["display_hex"] for entry in colors]
    profile_names = [f"MM-ART-010 Berlin {entry['name']}" for entry in colors]
    volume_names = ["Tool 1 Coupon Base — Oak", "Tool 4 Coupon Logo — Sky Blue"]
    old_transform = b'transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"'
    new_transform = (
        f'transform="1 0 0 0 1 0 0 0 1 {tx:.6f} {ty:.6f} 0" printable="1"'
    ).encode("ascii")
    extruders: list[int] = []
    with zipfile.ZipFile(raw) as source, zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == "3D/3dmodel.model":
                if data.count(old_transform) != 1:
                    raise ValueError("expected one identity build transform in coupon project")
                data = data.replace(old_transform, new_transform)
            elif info.filename == "Metadata/project_settings.config":
                settings = json.loads(data)
                for key, value in list(settings.items()):
                    if key.startswith("filament_") and isinstance(value, list):
                        if len(value) == 1:
                            settings[key] = value * 4
                        elif len(value) == 2:
                            settings[key] = [value[0], value[1], value[1], value[1]]
                settings["filament_colour"] = display_colors
                settings["default_filament_colour"] = display_colors
                settings["default_filament_profile"] = profile_names
                settings["filament_settings_id"] = profile_names
                data = (json.dumps(settings, indent=4, ensure_ascii=False) + "\n").encode()
            elif info.filename == "Metadata/model_settings.config":
                text = data.decode("utf-8")
                original = [
                    int(value)
                    for value in re.findall(r'key="extruder" value="(\d+)"', text)
                ]
                if original not in ([1, 2], [1, 4]):
                    raise ValueError(f"expected coupon source tools [1, 2] or [1, 4], got {original}")
                if original == [1, 2]:
                    desired = iter((1, 4))
                    text = re.sub(
                        r'key="extruder" value="\d+"',
                        lambda match: f'key="extruder" value="{next(desired)}"',
                        text,
                    )
                for source_name, volume_name in zip(source_names, volume_names, strict=True):
                    text = text.replace(
                        f'key="name" value="{source_name}"',
                        f'key="name" value="{volume_name}"',
                    )
                extruders = [
                    int(value)
                    for value in re.findall(r'key="extruder" value="(\d+)"', text)
                ]
                data = text.encode("utf-8")
            target.writestr(info, data)
    if extruders != [1, 4]:
        raise ValueError(f"expected final coupon tool assignments [1, 4], got {extruders}")
    return {
        "build_translation_mm": [tx, ty, 0.0],
        "extruder_assignments": extruders,
        "filament_profile_names": profile_names,
        "volume_names": volume_names,
        "display_colors": display_colors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--slicer", type=Path, required=True)
    parser.add_argument("--machine-profile", type=Path, required=True)
    parser.add_argument("--process-profile", type=Path, required=True)
    parser.add_argument("--filament-profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    previous = load_module(PREVIOUS, "mm_art_010_coupon_package_v050")
    current = load_module(PACKAGE_PROJECT, "mm_art_010_coupon_package_v051")
    export_root = PRODUCT / "exports" / "v0.5.1" / "berlin" / args.candidate
    inputs = [
        export_root / "metrimade-logo-coupon-tool1-oak-base.stl",
        export_root / "metrimade-logo-coupon-tool4-sky-blue-logo.stl",
    ]
    required = [args.slicer, args.machine_profile, args.process_profile, args.filament_profile, *inputs]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing required input(s): {missing}")
    if args.output.exists() or args.report.exists():
        raise SystemExit("refusing destructive overwrite of coupon 3MF or report")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    _, colors = previous.load_palette(PALETTE)
    metrics = [previous.serialized_mesh_metrics(path) for path in inputs]
    if not all(item["watertight"] and item["positive_volume"] for item in metrics):
        raise SystemExit("coupon source STL failed serialized mesh checks")
    bed_min_x, bed_min_y, bed_max_x, bed_max_y = previous.parse_bed_bounds(args.machine_profile)
    source_min, source_max = previous.source_bounds(inputs)
    tx = (bed_min_x + bed_max_x - source_min[0] - source_max[0]) / 2.0
    ty = (bed_min_y + bed_max_y - source_min[1] - source_max[1]) / 2.0

    with tempfile.TemporaryDirectory(prefix="mm-art-010-051-coupon-anycubic-") as temporary:
        temporary_dir = Path(temporary)
        all_profiles = current.write_filament_profiles(
            args.filament_profile, temporary_dir, PALETTE, colors
        )
        profiles = [all_profiles[0], all_profiles[3]]
        raw = temporary_dir / "raw-coupon-project.3mf"
        command = [
            str(args.slicer.resolve()),
            "--datadir",
            str(temporary_dir / "datadir"),
            "--load-settings",
            f"{args.process_profile.resolve()};{args.machine_profile.resolve()}",
            "--load-filaments",
            ";".join(str(path) for path in profiles),
            "--load-filament-ids",
            "1,2",
            "--arrange",
            "0",
            "--assemble",
            "--export-3mf",
            str(raw),
            *(str(path.resolve()) for path in inputs),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0 or not raw.is_file() or raw.stat().st_size == 0:
            raise SystemExit(
                f"Anycubic coupon export failed with {completed.returncode}:\n"
                f"stdout={completed.stdout}\nstderr={completed.stderr}"
            )
        normalization = normalize(
            raw, args.output, tx, ty, colors, [path.name for path in inputs]
        )

    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1",
        "candidate": args.candidate,
        "status": "PASS",
        "representation": "native Anycubic project 3MF with two coupon volumes assigned to product tools 1 and 4",
        "output": {
            "path": str(args.output.resolve()),
            "bytes": args.output.stat().st_size,
            "sha256": sha256(args.output),
        },
        "source_bounds_mm": [source_min.tolist(), source_max.tolist()],
        "source_parts": [
            {
                "tool": tool,
                "filament": colors[tool - 1],
                "path": str(path.resolve()),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "mesh": mesh,
            }
            for tool, path, mesh in zip((1, 4), inputs, metrics, strict=True)
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
            "The coupon intentionally prints only Oak and Sky Blue while retaining the product's tool numbers 1 and 4.",
            "Final physical ACE slot identity, purge and 2.0 m recognition remain human-controlled.",
            "No printer upload or print start is performed.",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "output": str(args.output), "report": str(args.report)}))


if __name__ == "__main__":
    main()
