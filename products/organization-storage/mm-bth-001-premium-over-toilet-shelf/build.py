#!/usr/bin/env python3
"""Build revision-bound DRAFT STL/STEP files and an assembly preview."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil

import cadquery as cq
import trimesh

from src.image_relief import generate_image_relief
from src.over_toilet_shelf import build_model, load_config, make_assembly_compound


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_part(part: cq.Workplane, stl_path: Path, step_path: Path, config: dict) -> None:
    cq.exporters.export(
        part,
        str(stl_path),
        tolerance=float(config["export"]["stl_tolerance"]),
        angularTolerance=float(config["export"]["stl_angular_tolerance"]),
    )
    cq.exporters.export(part, str(step_path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "parameters.json")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "output" / "rev-0.2.0-draft"
    )
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    config_path = args.config.resolve()
    output = args.output.resolve()
    if args.clean and output.exists():
        shutil.rmtree(output)
    stl_dir = output / "stl"
    step_dir = output / "step"
    reports_dir = output / "reports"
    previews_dir = output / "preview"
    three_mf_dir = output / "3mf"
    for directory in (stl_dir, step_dir, reports_dir, previews_dir, three_mf_dir):
        directory.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)
    result = build_model(config)
    manifest_parts: list[dict[str, object]] = []
    for record in result.print_parts:
        stl_path = stl_dir / f"{record.name}.stl"
        step_path = step_dir / f"{record.name}.step"
        export_part(record.solid, stl_path, step_path, config)
        bounds = record.solid.val().BoundingBox()
        manifest_parts.append(
            {
                "name": record.name,
                "quantity": record.quantity,
                "material": record.material,
                "orientation": record.orientation,
                "category": record.category,
                "stl": str(stl_path.relative_to(output)),
                "step": str(step_path.relative_to(output)),
                "bounds_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
            }
        )

    assembly = make_assembly_compound(result.assembly_parts)
    assembly_stl_path = previews_dir / "premium_over_toilet_shelf_assembly.stl"
    assembly_step_path = previews_dir / "premium_over_toilet_shelf_assembly.step"
    cq.exporters.export(
        assembly,
        str(assembly_stl_path),
        tolerance=0.18,
        angularTolerance=0.22,
    )
    cq.exporters.export(assembly, str(assembly_step_path))

    image_relief_report = None
    relief_source: Path | None = None
    relief = config["personalization"]["image_relief"]
    if relief["enabled"]:
        source = Path(relief["source_image"])
        if not source.is_absolute():
            source = (config_path.parent / source).resolve()
        if not source.exists():
            raise FileNotFoundError(f"Image-relief source not found: {source}")
        relief_source = source
        header = config["personalization"]["header"]
        image_relief_report = generate_image_relief(
            source,
            stl_dir / "personalized_header_image_relief_print.stl",
            reports_dir / "personalized_header_heightmap_16bit.png",
            previews_dir / "personalized_header_heightmap_preview.png",
            reports_dir / "image_relief_report.json",
            float(header["insert_width"]),
            float(header["insert_height"]),
            float(header["insert_base_thickness"]),
            float(relief["depth"]),
            float(relief["sample_pitch"]),
            relief["mode"],
            bool(relief["invert"]),
            relief["fit"],
            reports_dir / "personalized_header_image_relief_assembly_local.stl",
            int(relief["triangle_budget"]),
            float(relief["memory_budget_gib"]),
            float(relief["max_mesh_mib"]),
            float(relief["max_slicer_seconds"]),
        )
        manifest_parts.append(
            {
                "name": "personalized_header_image_relief_print",
                "quantity": 1,
                "material": "decorative PLA/PETG",
                "orientation": "rear face on bed",
                "category": "decor",
                "stl": "stl/personalized_header_image_relief_print.stl",
                "step": None,
                "bounds_mm": [
                    image_relief_report["bounds_mm"][1][0] - image_relief_report["bounds_mm"][0][0],
                    image_relief_report["bounds_mm"][1][1] - image_relief_report["bounds_mm"][0][1],
                    image_relief_report["bounds_mm"][1][2] - image_relief_report["bounds_mm"][0][2]
                ],
            }
        )
        assembly_mesh = trimesh.load(assembly_stl_path, force="mesh", process=True)
        relief_mesh = trimesh.load(
            reports_dir / "personalized_header_image_relief_assembly_local.stl",
            force="mesh",
            process=True,
        )
        relief_mesh.apply_translation(result.derived["header_insert_assembly_translation"])
        trimesh.util.concatenate([assembly_mesh, relief_mesh]).export(assembly_stl_path)

    tracked_sources = [
        config_path,
        ROOT / "build.py",
        ROOT / "validate.py",
        ROOT / "render_preview.py",
        ROOT / "src" / "over_toilet_shelf.py",
        ROOT / "src" / "image_relief.py",
        ROOT / "tests" / "test_variants.py",
        ROOT / "design-plan.json",
        ROOT / "design-spec.yaml",
        ROOT / "decision-log.md",
        ROOT / "README_DE.md",
        ROOT / "BOM.csv",
        ROOT / "ASSEMBLY.md",
        ROOT / "PRINTING.md",
        ROOT / "test-plan.yaml",
        ROOT / "requirements.txt",
        ROOT / "assets" / "concept" / "premium_over_toilet_shelf_r0.2.0_concept.png",
    ]
    if relief_source is not None:
        tracked_sources.append(relief_source)
    source_hashes = {
        str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path): sha256(path)
        for path in tracked_sources
        if path.exists()
    }
    config_reference = (
        str(config_path.relative_to(ROOT)) if config_path.is_relative_to(ROOT) else str(config_path)
    )
    artifact_paths = [assembly_stl_path, assembly_step_path]
    for record in manifest_parts:
        artifact_paths.append(output / record["stl"])
        if record.get("step"):
            artifact_paths.append(output / record["step"])
    if image_relief_report is not None:
        artifact_paths.append(Path(image_relief_report["build_master_16bit"]))
    artifact_hashes = {
        str(path.relative_to(output)): sha256(path)
        for path in artifact_paths
        if path.exists()
    }

    assembly_body_names = [record.name for record in result.assembly_parts] + (
        ["header_image_relief"] if relief["enabled"] else []
    )
    manifest_derived = dict(result.derived)
    manifest_derived["print_part_file_count"] = len(manifest_parts)
    manifest_derived["assembly_body_count"] = len(assembly_body_names)
    manifest = {
        "schema_version": 2,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "project_revision": config.get("project", {}).get("revision"),
        "spec_revision": config.get("project", {}).get("spec_revision"),
        "geometry_revision": config.get("project", {}).get("geometry_revision"),
        "release_status": "DRAFT",
        "coordinate_datum": "rear frame plane Y=0; +Y toward user; finished floor Z=0; X centered",
        "installation": {
            "mode": config["installation"]["mode"],
            "overall_envelope_mm": result.derived["overall_envelope_mm"],
            "shelf_top_datums_mm": result.derived["shelf_z_values"],
            "floor_contact_count": result.derived["floor_contact_count"],
            "wall_restraint_count": result.derived["wall_restraint_count"],
            "wall_restraint_nominal_lower_hole_z_mm": result.derived[
                "wall_restraint_nominal_lower_hole_z"
            ],
        },
        "config": config_reference,
        "config_absolute": str(config_path),
        "source_hashes_sha256": source_hashes,
        "artifact_hashes_sha256": artifact_hashes,
        "tool_versions": {
            "python": platform.python_version(),
            "cadquery": getattr(cq, "__version__", importlib.metadata.version("cadquery")),
            "trimesh": importlib.metadata.version("trimesh"),
            "pillow": importlib.metadata.version("Pillow"),
        },
        "derived": manifest_derived,
        "parts": manifest_parts,
        "assembly_body_names": assembly_body_names,
        "assembly": {
            "stl": str(assembly_stl_path.relative_to(output)),
            "step": str(assembly_step_path.relative_to(output)),
            "stl_includes_selected_image_relief": bool(relief["enabled"]),
            "step_includes_selected_image_relief": False,
            "step_scope": "parametric BRep assembly; image relief remains STL-only",
        },
        "exact_slicer_project": {
            "directory": "3mf",
            "status": "PENDING_EXACT_TARGET_PROFILE",
            "note": "No synthetic 3MF is generated by the CAD builder; save the exact reviewed slicer project here.",
        },
        "image_relief": image_relief_report,
        "remaining_release_scope": [
            "exact target slicer and 3MF",
            "process-matched fit and module-seam coupons",
            "measured site and wall-anchor verification",
            "physical creep, proof, cycle, drawer, and anti-tip tests",
            "optimization and manufacturing-mesh decision",
            "JuSt Innovation watermark and final approval",
        ],
    }
    (reports_dir / "build_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    with (reports_dir / "print_parts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["name", "quantity", "material", "orientation", "category", "bounds_mm"],
        )
        writer.writeheader()
        for part in manifest_parts:
            writer.writerow({key: part[key] for key in writer.fieldnames})
    print(f"Exported {len(manifest_parts)} printable part files to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
