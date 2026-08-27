#!/usr/bin/env python3
"""Validate continuous tone transfer, structural reserve, STL heights, and 3MF packaging."""

from __future__ import annotations

import base64
import json
import struct
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(base_file: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base_file.parent / path).resolve()


def stl_z_values(path: Path) -> np.ndarray:
    with path.open("rb") as handle:
        header = handle.read(84)
    count = struct.unpack_from("<I", header, 80)[0]
    dtype = np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])
    records = np.memmap(path, dtype=dtype, mode="r", offset=84, shape=(count,))
    return records["vertices"][..., 2].reshape(-1)


def scan_3mf(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        names = sorted(archive.namelist())
        object_count = 0
        item_count = 0
        model_prefix = b""
        carry = b""
        with archive.open("3D/3dmodel.model") as model:
            while True:
                block = model.read(1024 * 1024)
                if not block:
                    break
                if len(model_prefix) < 4096:
                    model_prefix += block[: 4096 - len(model_prefix)]
                data = carry + block
                object_count += data.count(b"<object ") - carry.count(b"<object ")
                item_count += data.count(b"<item ") - carry.count(b"<item ")
                carry = data[-16:]
        bad_file = archive.testzip()
    return {
        "zip_entries": names,
        "crc_pass": bad_file is None,
        "core_namespace": CORE_NS.encode("utf-8") in model_prefix,
        "objects": object_count,
        "build_items": item_count,
    }


def main() -> None:
    params = read_json(ROOT / "config" / "model-params.json")
    relief_cfg_path = ROOT / "config" / "relief-config.json"
    relief_cfg = read_json(relief_cfg_path)
    job_path = resolve(relief_cfg_path, relief_cfg["relief_job"])
    job = read_json(job_path)
    manifest_path = resolve(relief_cfg_path, relief_cfg["manifest_output"])
    manifest = read_json(manifest_path)
    metadata_path = resolve(job_path, job["outputs"]["heightmap_metadata"])
    build_metadata = read_json(metadata_path)
    aspect_diagnostic = read_json(ROOT / "reports" / "aspect-diagnostic.json")
    source_path = resolve(job_path, job["outputs"]["heightmap"])
    encoded = base64.b64decode(manifest["samples_u16_base64"])
    samples = np.frombuffer(encoded, dtype="<u2")
    source = np.asarray(Image.open(source_path))
    floor = float(params["organizer"]["floor_thickness"])
    engrave = float(params["relief"]["engrave_depth"])
    emboss = float(params["relief"]["emboss_depth"])
    module_reports = []
    for path in sorted((ROOT / "output" / "DRAFT").glob("DRAFT-*-textured.stl")):
        z_values = stl_z_values(path)
        band = np.asarray(z_values[(z_values >= floor - engrave - 1.0e-5) & (z_values <= floor + emboss + 1.0e-5)])
        unique = np.unique(band)
        module_reports.append(
            {
                "file": path.name,
                "floor_relief_vertex_samples": int(len(band)),
                "floor_band_unique_float32_z": int(len(unique)),
                "floor_band_min_z_mm": float(np.min(unique)),
                "floor_band_max_z_mm": float(np.max(unique)),
            }
        )
        del z_values, band, unique

    three_mf = ROOT / "output" / "DRAFT" / params["export"]["assembly_filename"]
    three_mf_scan = scan_3mf(three_mf)
    package_report = read_json(ROOT / "reports" / "three-mf-package.json")
    source_unique = int(np.unique(source).size)
    geometry_unique = int(np.unique(samples).size)
    minimum_residual = {
        "floor_mm": floor - engrave,
        "double_sided_divider_mm": params["organizer"]["base_wall_thickness"] - 2 * params["relief"]["wall_engrave_depth"],
        "inner_outer_wall_mm": params["organizer"]["base_wall_thickness"]
        - params["relief"]["outer_panel_recess"]
        - params["relief"]["outer_wall_engrave_depth"]
        - params["relief"]["wall_engrave_depth"],
    }
    report = {
        "status": "PASS",
        "revision": params["model_revision"],
        "source_asset_id": job["source"]["asset_id"],
        "relief_job": str(job_path.relative_to(ROOT)),
        "height_transfer": {
            "source_dtype": str(source.dtype),
            "source_grid": [int(source.shape[1]), int(source.shape[0])],
            "source_unique_u16_values": source_unique,
            "surface_build_pitch_mm": [build_metadata["pitch_x_mm"], build_metadata["pitch_y_mm"]],
            "surface_build_dpi": [build_metadata["dpi_x"], build_metadata["dpi_y"]],
            "geometry_grid": manifest["grid"],
            "geometry_pitch_mm": [manifest["pitch_x_mm"], manifest["pitch_y_mm"]],
            "geometry_sample_count": int(samples.size),
            "geometry_unique_u16_values": geometry_unique,
            "manifest_retained_height_bits": manifest["statistics"]["retained_height_bits"],
            "additional_height_level_quantization": manifest["statistics"]["additional_height_level_quantization"],
            "thresholds_or_depth_classes": False,
            "mapping": manifest["height_mapping"],
            "stl_coordinate_encoding": "IEEE-754 Float32 required by binary STL",
        },
        "physical_aspect": {
            "validation": build_metadata["aspect_validation"],
            "source_tile_mm": build_metadata["tile_mm"],
            "geometry_domain_mm": [manifest["tile_width_mm"], manifest["tile_height_mm"]],
            "diagnostic": aspect_diagnostic,
        },
        "physical_relief": {
            "engrave_depth_mm": engrave,
            "emboss_depth_mm": emboss,
            "extreme_to_extreme_span_mm": engrave + emboss,
            "nominal_layer_height_mm": job["printer"]["layer_height_mm"],
            "minimum_residual_material_mm": minimum_residual,
            "wall_thickness_increase_required": min(minimum_residual.values()) < 2.0,
        },
        "exported_stl_evidence": module_reports,
        "three_mf": {
            "file": three_mf.name,
            **three_mf_scan,
            "assembly_bounds_mm": package_report["assembly_bounds_mm"],
        },
        "acceptance": {
            "manifest_is_continuous_u16": manifest["representation"] == "continuous-heightfield-u16",
            "surface_build_is_16_bit": source.dtype == np.uint16 and build_metadata["bit_depth"] == 16,
            "surface_build_is_127_ppi": abs(build_metadata["dpi_x"] - 127.0) < 0.01,
            "geometry_pitch_is_030_mm": abs(manifest["pitch_x_mm"] - 0.30) < 1.0e-6,
            "physical_aspect_metadata_pass": build_metadata["aspect_validation"]["passed"] is True,
            "circle_square_aspect_diagnostic_pass": aspect_diagnostic["status"] == "PASS",
            "more_than_three_geometry_heights": geometry_unique > 3,
            "every_module_has_more_than_three_exported_floor_heights": all(item["floor_band_unique_float32_z"] > 3 for item in module_reports),
            "minimum_residual_material_at_least_2_mm": min(minimum_residual.values()) >= 2.0,
            "three_mf_four_named_objects": three_mf_scan["objects"] == 4 and three_mf_scan["build_items"] == 4,
            "three_mf_crc_and_namespace": three_mf_scan["crc_pass"] and three_mf_scan["core_namespace"],
        },
    }
    report["status"] = "PASS" if all(report["acceptance"].values()) else "FAIL"
    destination = ROOT / "reports" / "continuous16-validation.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "geometry_unique_u16_values": geometry_unique, "modules": module_reports}, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
