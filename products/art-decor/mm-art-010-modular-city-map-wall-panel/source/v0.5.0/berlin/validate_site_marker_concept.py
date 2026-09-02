#!/usr/bin/env python3
"""Validate the revision 0.5.0 address transform and concept marker envelope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from shapely import affinity
from shapely.geometry import box, shape
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
ADDRESS = PRODUCT / "source-data" / "v0.5.0" / "berlin" / "metri-create-headquarters-address.json"
PARAMETERS = HERE / "site-marker-parameters.json"
BOUNDARY = PRODUCT / "source-data" / "v0.4.0" / "berlin" / "boundary.geojson"
PLACEMENTS = {
    "boundary_crop": PRODUCT / "source" / "v0.4.0" / "berlin" / "placements" / "boundary-crop-placement.json",
    "context_outline": PRODUCT / "source" / "v0.4.0" / "berlin" / "placements" / "context-outline-placement.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_boundary():
    data = json.loads(BOUNDARY.read_text())
    return unary_union([shape(feature["geometry"]) for feature in data["features"]])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    address = json.loads(ADDRESS.read_text())
    parameters = json.loads(PARAMETERS.read_text())["site_marker"]
    source_point = address["geocode"]["coordinate"]
    width = parameters["placement"]["width_mm"]
    height = parameters["placement"]["resolved_height_mm"]
    half_width = width / 2
    half_height = height / 2
    errors: list[str] = []
    modes = {}
    boundary = load_boundary()

    for mode, placement_path in PLACEMENTS.items():
        placement = json.loads(placement_path.read_text())
        transform = placement["transform"]
        scale = transform["uniform_scale_mm_per_source_m"]
        translate = transform["translate_mm"]
        x = source_point[0] * scale + translate[0]
        y = source_point[1] * scale + translate[1]
        recorded = address["resolved_panel_coordinates_mm"][mode]
        transform_error = max(abs(x - recorded[0]), abs(y - recorded[1]))
        if transform_error > 0.001:
            errors.append(f"{mode}: frozen panel coordinate differs by {transform_error:.6f} mm")

        marker_box = box(x - half_width, y - half_height, x + half_width, y + half_height)
        seam_clearance = 300.0 - marker_box.bounds[2]
        if seam_clearance < parameters["placement"]["minimum_clearance_to_center_seam_mm"]:
            errors.append(f"{mode}: seam clearance {seam_clearance:.3f} mm is below the concept minimum")

        if mode == "boundary_crop":
            retained = affinity.translate(affinity.scale(boundary, xfact=scale, yfact=scale, origin=(0, 0)), xoff=translate[0], yoff=translate[1])
        else:
            bounds = placement["outer_bounds_mm"]
            retained = box(*bounds)
        within_retained = retained.contains(marker_box)
        perimeter_clearance = marker_box.distance(retained.boundary) if within_retained else 0.0
        if not within_retained:
            errors.append(f"{mode}: marker envelope is not wholly inside the retained body")
        if perimeter_clearance < 5.0:
            errors.append(f"{mode}: marker perimeter clearance {perimeter_clearance:.3f} mm is below 5 mm")

        mount_clearances = []
        for name, center in placement["socket_centers_global_mm"].items():
            clearance = marker_box.distance(box(center[0] - 12, center[1] - 12, center[0] + 12, center[1] + 12))
            mount_clearances.append({"name": name, "clearance_mm": clearance})
            if clearance < 12.0:
                errors.append(f"{mode}: marker is too close to protected mount {name}")

        modes[mode] = {
            "calculated_center_mm": [x, y],
            "recorded_center_mm": recorded,
            "coordinate_error_mm": transform_error,
            "envelope_bounds_mm": list(marker_box.bounds),
            "within_retained_body": within_retained,
            "perimeter_clearance_mm": perimeter_clearance,
            "center_seam_clearance_mm": seam_clearance,
            "mount_clearances": mount_clearances,
            "placement_sha256": sha256(placement_path),
        }

    source_grid_feature_mm = 18.0 / 248.0 * width
    if source_grid_feature_mm < parameters["relief"]["minimum_printable_stroke_mm"]:
        errors.append("scaled 18-unit source-grid feature is below the printable minimum")
    if parameters["relief"]["semantic_tool"] not in (1, 2, 3, 4):
        errors.append("site marker must reuse one of four existing tools")

    result = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.0-concept",
        "status": "PASS" if not errors else "FAIL",
        "address_source_sha256": sha256(ADDRESS),
        "parameter_source_sha256": sha256(PARAMETERS),
        "source_grid_feature_mm": source_grid_feature_mm,
        "minimum_printable_feature_mm": parameters["relief"]["minimum_printable_stroke_mm"],
        "semantic_tool": parameters["relief"]["semantic_tool"],
        "modes": modes,
        "open_production_checks": [
            "boolean overlap with actual light apertures and semantic map bodies",
            "watertight union into tool 4 and reconstructed composite",
            "exact Anycubic Slicer Next layers and tool mapping",
            "physical logo readability and purge contamination",
        ],
        "errors": errors,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
