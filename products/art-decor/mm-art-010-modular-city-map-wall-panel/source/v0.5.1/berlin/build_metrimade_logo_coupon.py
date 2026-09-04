#!/usr/bin/env python3
"""Build the process-matched Oak/Sky Blue metriMade recognition coupon."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import manifold3d as m3d
import numpy as np
from PIL import Image
from shapely.geometry import box
from skimage import measure


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS = PRODUCT / "source" / "v0.5.0" / "berlin" / "build_berlin_site_marker.py"
SITE_PARAMETERS = HERE / "site-marker-parameters.json"
COUPON_PARAMETERS = HERE / "logo-coupon-parameters.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_previous():
    spec = importlib.util.spec_from_file_location("mm_art_010_coupon_v051", PREVIOUS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load marker generator: {PREVIOUS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mask_to_section(mask: np.ndarray, pitch: float, physical_height: float) -> m3d.CrossSection:
    padded = np.pad(mask.astype(np.uint8), 1)
    raw = measure.find_contours(padded, 0.5, fully_connected="high")
    contours: list[np.ndarray] = []
    for contour in raw:
        contour = measure.approximate_polygon(contour, tolerance=0.65)
        if len(contour) < 4:
            continue
        rows = contour[:, 0] - 1.0
        columns = contour[:, 1] - 1.0
        xy = np.column_stack((columns * pitch, physical_height - rows * pitch))
        if len(xy) >= 3:
            contours.append(xy.astype(np.float64))
    section = m3d.CrossSection(contours, m3d.FillRule.EvenOdd).simplify(0.03)
    if section.is_empty() or section.area() <= 0:
        raise ValueError("coupon logo produced no positive manufacturing section")
    return section


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    if not args.candidate.replace("-", "").isalnum():
        raise SystemExit("candidate must contain only letters, digits and hyphens")

    marker = load_previous()
    marker.SITE_PARAMETERS_PATH = SITE_PARAMETERS
    marker.SITE_PARAMETERS = json.loads(SITE_PARAMETERS.read_text())
    parameters = json.loads(COUPON_PARAMETERS.read_text())
    coupon = parameters["coupon"]
    width = float(coupon["width_mm"])
    height = float(coupon["height_mm"])
    pitch = float(coupon["manufacturing_raster_pitch_mm"])
    logo_width = float(coupon["logo_width_mm"])
    logo_height = float(coupon["logo_height_mm"])
    base_top = float(coupon["base_thickness_mm"])
    logo_top = base_top + float(coupon["logo_relief_mm"])
    clear_x = (width - logo_width) / 2.0
    clear_y = (height - logo_height) / 2.0
    if min(clear_x, clear_y) < float(coupon["minimum_clear_space_mm"]):
        raise SystemExit("coupon does not satisfy the declared logo clear space")

    export_root = PRODUCT / "exports" / "v0.5.1" / "berlin" / args.candidate
    validation_root = PRODUCT / "validation" / "v0.5.1" / "berlin" / args.candidate
    if export_root.exists() or validation_root.exists():
        raise SystemExit("refusing destructive overwrite of an existing coupon candidate")
    export_root.mkdir(parents=True)
    validation_root.mkdir(parents=True)

    artwork_mask, artwork_path, renderer = marker.render_artwork_mask()
    logo_size = (max(1, round(logo_width / pitch)), max(1, round(logo_height / pitch)))
    logo_image = Image.fromarray((artwork_mask * 255).astype(np.uint8)).resize(
        logo_size, Image.Resampling.NEAREST
    )
    canvas_size = (round(width / pitch), round(height / pitch))
    canvas = Image.new("L", canvas_size, 0)
    left = round((canvas.width - logo_image.width) / 2.0)
    top = round((canvas.height - logo_image.height) / 2.0)
    canvas.paste(logo_image, (left, top))
    manufacturing_mask = np.asarray(canvas, dtype=np.uint8) >= 128
    logo_section = mask_to_section(manufacturing_mask, pitch, height)

    radius = float(coupon["corner_radius_mm"])
    base_shape = box(radius, radius, width - radius, height - radius).buffer(
        radius, resolution=12
    )
    base_section = marker.BASE.to_cross_section(base_shape)
    logo_section = logo_section ^ base_section
    base = marker.BASE.extrude_section(base_section, 0.0, base_top)
    logo = marker.BASE.extrude_section(logo_section, base_top, logo_top)
    composite = (base + logo).simplify(0.015)
    overlap = float((base ^ logo).volume())

    outputs = {
        "base": export_root / "metrimade-logo-coupon-tool1-oak-base.stl",
        "logo": export_root / "metrimade-logo-coupon-tool4-sky-blue-logo.stl",
        "composite": export_root / "metrimade-logo-coupon-composite.stl",
    }
    for key, solid in (("base", base), ("logo", logo), ("composite", composite)):
        marker.BASE.manifold_to_trimesh(solid).export(outputs[key])

    preview = np.zeros((canvas.height, canvas.width, 3), dtype=np.uint8)
    preview[:, :] = (198, 170, 122)
    preview[manufacturing_mask] = (105, 199, 229)
    Image.fromarray(preview).resize((840, 880), Image.Resampling.NEAREST).save(
        validation_root / "metrimade-logo-coupon-top-preview.png"
    )

    metrics = {key: marker.BASE.roundtrip_stl_metrics(path) for key, path in outputs.items()}
    checks = {
        "all_meshes_watertight": all(item["watertight"] for item in metrics.values()),
        "all_meshes_positive_volume": all(item["positive_volume"] for item in metrics.values()),
        "all_meshes_without_degenerate_faces": all(item["degenerate_faces"] == 0 for item in metrics.values()),
        "all_meshes_without_duplicate_faces": all(item["duplicate_faces"] == 0 for item in metrics.values()),
        "tool_volumes_disjoint": abs(overlap) <= 1e-6,
        "logo_relief_matches_product": abs((logo_top - base_top) - 0.6) <= 1e-9,
        "logo_size_matches_product": abs(logo_width - 54.0) <= 1e-9 and abs(logo_height - 57.176471) <= 1e-9,
        "clear_space_satisfied": min(clear_x, clear_y) >= float(coupon["minimum_clear_space_mm"]),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1",
        "candidate": args.candidate,
        "status": status,
        "purpose": "physical 2.0 m recognition and Oak/Sky Blue process coupon for the approved front marker",
        "parameters": {
            "path": str(COUPON_PARAMETERS.relative_to(PRODUCT)),
            "sha256": sha256(COUPON_PARAMETERS),
            "values": coupon,
        },
        "source": {
            "site_marker_parameters": str(SITE_PARAMETERS.relative_to(PRODUCT)),
            "site_marker_parameters_sha256": sha256(SITE_PARAMETERS),
            "artwork": str(artwork_path.resolve()),
            "artwork_sha256": sha256(artwork_path),
            "renderer": renderer,
        },
        "geometry": {
            "logo_manufacturing_area_mm2": float(logo_section.area()),
            "clear_space_mm": {"x": clear_x, "y": clear_y},
            "tool_overlap_mm3": overlap,
            "z_bands_mm": {"base": [0.0, base_top], "logo": [base_top, logo_top]},
        },
        "checks": checks,
        "artifacts": {
            key: {
                "path": str(path.relative_to(PRODUCT)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "mesh": metrics[key],
            }
            for key, path in outputs.items()
        },
        "physical_gate": {
            "status": "REVIEW_REQUIRED",
            "distance_mm": 2000.0,
            "condition": coupon["physical_acceptance"],
        },
        "limitations": [
            "Digital geometry cannot prove 2.0 m human recognition.",
            "The coupon tests the 0.6 mm logo relief on a flat Oak base; the map has locally varying supporting color bands.",
            "No printer upload or print start is performed.",
        ],
    }
    report_path = validation_root / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(report_path), "export_root": str(export_root)}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
