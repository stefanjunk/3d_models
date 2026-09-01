#!/usr/bin/env python3
"""Package one Berlin half as an Anycubic Slicer Next project 3MF.

The generic standards-only 3MF writer remains useful for interchange tests, but
Anycubic Slicer Next 1.3.9.4 rejects that package before reading its meshes.
This target-slicer handoff asks Anycubic itself to create the project container,
then normalizes the four filament arrays and moves the assembled part into the
centre of the configured build plate without changing the source STL geometry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PARAMETERS = json.loads((HERE / "berlin-parameters.json").read_text(encoding="utf-8"))
EXPORT = PRODUCT / "exports" / "v0.3.0" / "berlin"

PART_NAMES = ["bone-white", "nardo-grey", "black", "orange"]
PALETTE_NAMES = ["Bone White", "Nardo Grey", "Black", "Orange"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_bed_bounds(machine_profile: Path) -> tuple[float, float, float, float]:
    profile = json.loads(machine_profile.read_text(encoding="utf-8"))
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


def write_filament_profiles(base_profile: Path, directory: Path) -> list[Path]:
    base = json.loads(base_profile.read_text(encoding="utf-8"))
    palette = PARAMETERS["palette"]
    outputs = []
    for index, name in enumerate(PALETTE_NAMES, start=1):
        data = dict(base)
        profile_name = f"MM-ART-010 Berlin {name}"
        color = palette[name]
        data.update(
            {
                "name": profile_name,
                "from": "user",
                "is_custom_defined": "1",
                "setting_id": f"MMART010-{index}",
                "filament_id": f"MMART010-{index}",
                "filament_settings_id": [profile_name],
                "filament_colour": [color],
                "default_filament_colour": [color],
            }
        )
        path = directory / f"filament-{index}.json"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        outputs.append(path)
    return outputs


def normalize_project_3mf(
    project_path: Path,
    *,
    translate_x: float,
    translate_y: float,
) -> dict[str, object]:
    temporary_path = project_path.with_suffix(".normalized.tmp")
    colors = [PARAMETERS["palette"][name] for name in PALETTE_NAMES]
    profile_names = [f"MM-ART-010 Berlin {name}" for name in PALETTE_NAMES]
    old_transform = b'transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"'
    new_transform = (
        f'transform="1 0 0 0 1 0 0 0 1 {translate_x:.6f} {translate_y:.6f} 0" printable="1"'
    ).encode("ascii")
    extruders: list[int] = []

    with zipfile.ZipFile(project_path) as source, zipfile.ZipFile(
        temporary_path, "w", compression=zipfile.ZIP_DEFLATED
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
                settings["filament_colour"] = colors
                settings["default_filament_colour"] = colors
                settings["default_filament_profile"] = profile_names
                settings["filament_settings_id"] = profile_names
                data = (json.dumps(settings, indent=4, ensure_ascii=False) + "\n").encode("utf-8")
            elif info.filename == "Metadata/model_settings.config":
                text = data.decode("utf-8")
                extruders = [int(value) for value in re.findall(r'key="extruder" value="(\d+)"', text)]
            target.writestr(info, data)

    if extruders != [1, 2, 3, 4]:
        temporary_path.unlink(missing_ok=True)
        raise ValueError(f"expected extruder assignments [1, 2, 3, 4], got {extruders}")
    temporary_path.replace(project_path)
    return {
        "build_translation_mm": [translate_x, translate_y, 0.0],
        "extruder_assignments": extruders,
        "filament_profile_names": profile_names,
        "display_colors": colors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--half", choices=("left", "right"), required=True)
    parser.add_argument("--slicer", type=Path, required=True)
    parser.add_argument("--machine-profile", type=Path, required=True)
    parser.add_argument("--process-profile", type=Path, required=True)
    parser.add_argument("--filament-profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    inputs = [EXPORT / f"berlin-{args.half}-{name}.stl" for name in PART_NAMES]
    required_paths = [args.slicer, args.machine_profile, args.process_profile, args.filament_profile, *inputs]
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        raise SystemExit(f"missing required input(s): {missing}")
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.output}")
    if args.report.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.report}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    min_x, min_y, max_x, max_y = parse_bed_bounds(args.machine_profile)
    local_width = PARAMETERS["panel"]["split_x"] - PARAMETERS["panel"]["seam_gap"] / 2
    panel_height = PARAMETERS["panel"]["height"]
    translate_x = min_x + ((max_x - min_x) - local_width) / 2
    translate_y = min_y + ((max_y - min_y) - panel_height) / 2

    with tempfile.TemporaryDirectory(prefix=f"mm-art-010-{args.half}-3mf-") as temporary:
        temp = Path(temporary)
        profiles = write_filament_profiles(args.filament_profile, temp)
        command = [
            str(args.slicer.resolve()),
            "--datadir",
            str(temp / "datadir"),
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
            str(args.output.resolve()),
            *(str(path.resolve()) for path in inputs),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        if completed.returncode != 0 or not args.output.is_file() or args.output.stat().st_size == 0:
            args.output.unlink(missing_ok=True)
            raise SystemExit(
                f"Anycubic project export failed with {completed.returncode}:\n"
                f"stdout={completed.stdout}\nstderr={completed.stderr}"
            )

    normalized = normalize_project_3mf(
        args.output,
        translate_x=translate_x,
        translate_y=translate_y,
    )
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": PARAMETERS["revision"],
        "half": args.half,
        "status": "PASS",
        "representation": "Anycubic Slicer Next target-project 3MF",
        "output": {
            "path": str(args.output.resolve()),
            "bytes": args.output.stat().st_size,
            "sha256": sha256(args.output),
        },
        "source_parts": [
            {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in inputs
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
        "normalization": normalized,
        "limitations": [
            "The project carries four volume assignments and palette colors; the final ACE slot mapping and wipe-tower preview remain human-controlled.",
            "The target-slicer project uses vendor package extensions that the standards-only repository 3MF validator does not currently resolve.",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
