#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import load_palette, save_json
from three_mf import write_multicolor_3mf
from validate_multicolor_3mf import validate as validate_3mf


def run(command: list[str], *, cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def build_openscad_example(skill_root: Path, example_name: str, part_names: list[str], output_root: Path) -> dict[str, Any]:
    openscad = shutil.which("openscad")
    if not openscad:
        raise RuntimeError("OpenSCAD executable not found")
    example = skill_root / "examples" / example_name
    out = output_root / example_name
    parts_dir = out / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    palette = load_palette(example / "palette.yaml")
    if len(palette) != len(part_names):
        raise ValueError(f"Palette/part count mismatch for {example_name}")
    parts = []
    for item, part_name in zip(palette, part_names, strict=True):
        path = parts_dir / f"{part_name}.stl"
        run([openscad, "-o", str(path), "-D", f'part="{part_name}"', str(example / "model.scad")])
        parts.append({
            "id": item["id"],
            "material_name": item["name"],
            "display_hex": item["display_hex"],
            "temporary_slot": item.get("temporary_slot"),
            "path": str(path.resolve()),
        })
    manifest = {"version": 1, "source": str((example / "model.scad").resolve()), "parts": parts}
    manifest_path = out / "parts-manifest.json"
    save_json(manifest_path, manifest)
    preview = out / "preview.png"
    run([sys.executable, str(skill_root / "scripts/render_parts_preview.py"), str(manifest_path), "--output", str(preview), "--elev", "82", "--azim", "-90"])
    model_3mf = out / f"{example_name}.3mf"
    assembly_report = write_multicolor_3mf(parts, model_3mf, title=example_name, thumbnail=preview)
    validation = validate_3mf(model_3mf)
    save_json(out / "3mf-validation.json", validation)
    run([
        sys.executable,
        str(skill_root / "scripts/estimate_color_changes.py"),
        "--parts-manifest", str(manifest_path),
        "--layer-height", "0.2",
        "--json-out", str(out / "change-budget.json"),
    ])
    return {
        "example": example_name,
        "output": str(out.resolve()),
        "parts": len(parts),
        "3mf_valid": validation["valid"],
        "assembly": assembly_report,
        "preview": str(preview.resolve()),
    }


def build_textured_example(skill_root: Path, output_root: Path) -> dict[str, Any]:
    name = "03-textured-obj-to-four-color-3mf"
    example = skill_root / "examples" / name
    out = output_root / name
    source = out / "source"
    parts_dir = out / "color-parts"
    source.mkdir(parents=True, exist_ok=True)
    run([sys.executable, str(example / "generate_source.py"), "--output-dir", str(source)])
    obj = source / "textured-cylinder.obj"
    texture = source / "texture.png"
    palette = example / "palette.yaml"
    run([sys.executable, str(skill_root / "scripts/inspect_textured_asset.py"), str(obj), "--json-out", str(out / "source-inspection.json")])
    run([
        sys.executable,
        str(skill_root / "scripts/quantize_texture.py"),
        str(texture),
        "--palette", str(palette),
        "--output", str(out / "texture-quantized.png"),
        "--heatmap", str(out / "texture-deltae.png"),
        "--report", str(out / "quantization-report.json"),
        "--minimum-island-pixels", "8",
    ])
    run([
        sys.executable,
        str(skill_root / "scripts/texture_to_voxel_parts.py"),
        str(obj),
        "--palette", str(palette),
        "--pitch", "1.25",
        "--shell-depth", "2.5",
        "--base-color", "body_orange",
        "--minimum-component-voxels", "3",
        "--output-dir", str(parts_dir),
        "--report", str(out / "partition-report.json"),
    ])
    manifest_path = parts_dir / "parts-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    normalized_parts = []
    for part in manifest["parts"]:
        item = dict(part)
        item["path"] = str((parts_dir / part["path"]).resolve())
        normalized_parts.append(item)
    preview = out / "preview.png"
    run([sys.executable, str(skill_root / "scripts/render_parts_preview.py"), str(manifest_path), "--output", str(preview), "--elev", "24", "--azim", "-58"])
    model_3mf = out / f"{name}.3mf"
    assembly_report = write_multicolor_3mf(normalized_parts, model_3mf, title=name, thumbnail=preview)
    validation = validate_3mf(model_3mf)
    save_json(out / "3mf-validation.json", validation)
    run([
        sys.executable,
        str(skill_root / "scripts/estimate_color_changes.py"),
        "--parts-manifest", str(manifest_path),
        "--layer-height", "0.25",
        "--purge-matrix", str(skill_root / "assets/templates/purge-matrix.example.yaml"),
        "--json-out", str(out / "change-budget.json"),
    ])
    return {
        "example": name,
        "output": str(out.resolve()),
        "parts": len(normalized_parts),
        "3mf_valid": validation["valid"],
        "assembly": assembly_report,
        "preview": str(preview.resolve()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build all three deterministic multicolor examples.")
    parser.add_argument("--output-root", type=Path, default=Path("build/examples"))
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    args.output_root.mkdir(parents=True, exist_ok=True)
    results = [
        build_openscad_example(skill_root, "01-parametric-inlay-nameplate", ["base", "border", "lettering", "icon"], args.output_root),
        build_openscad_example(skill_root, "02-four-color-fox-badge", ["base", "white", "black", "blue"], args.output_root),
        build_textured_example(skill_root, args.output_root),
    ]
    report = {"skill": "multicolor-fdm-design", "examples": results, "all_valid": all(item["3mf_valid"] for item in results)}
    output = args.json_out or args.output_root / "build-summary.json"
    save_json(output, report)
    print(json.dumps(report, indent=2))
    return 0 if report["all_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
