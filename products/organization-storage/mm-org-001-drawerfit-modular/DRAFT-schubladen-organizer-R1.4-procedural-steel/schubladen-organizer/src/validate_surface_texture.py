#!/usr/bin/env python3
"""Validate procedural texture coverage, protected interfaces, budgets, and 3MF."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_CONNECTOR_HASHES = {
    "DRAFT-connector-coupon-male.stl": "996c6ef061463fb6c57e5ea31cf2c27fa9c425a2e501428f53030a1d0e6c57a4",
    "DRAFT-connector-coupon-female.stl": "6834bfccc6cf07aac31455583f76e6e8f99417d3c63d29a5e3dc5308179d0676",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    params = read_json(ROOT / "config" / "model-params.json")
    texture = read_json(ROOT / "config" / "surface-texture.json")
    build = read_json(ROOT / "reports" / "build-final.json")
    mesh = read_json(ROOT / "reports" / "mesh-validation.json")
    package = read_json(ROOT / "reports" / "three-mf-package.json")
    checks: dict[str, bool] = {}

    checks["procedural_representation"] = texture["representation"] == "deterministic-multiscale-analytic-dimple-field"
    checks["image_relief_inactive"] = "relief" not in params and "image" not in (ROOT / "rebuild.py").read_text(encoding="utf-8").lower()
    checks["approved_surfaces_enabled"] = all(texture["surfaces"][name]["enabled"] for name in ("floor", "inner_walls", "wall_tops"))
    checks["outer_walls_smooth"] = not texture["surfaces"]["outer_walls"]["enabled"]

    floor_depth = max(max(item["depth_mm"]) for item in texture["surfaces"]["floor"]["bands"])
    wall_depth = max(max(item["depth_mm"]) for item in texture["surfaces"]["inner_walls"]["bands"])
    top_depth = max(max(item["depth_mm"]) for item in texture["surfaces"]["wall_tops"]["bands"])
    minimum = texture["protected_regions"]["minimum_residual_wall_mm"]
    reserves = {
        "floor_below_top_texture_mm": params["organizer"]["floor_thickness"] - floor_depth,
        "floor_below_watermark_mm": params["organizer"]["floor_thickness"] - params["watermark"]["depth"],
        "double_sided_divider_mm": params["organizer"]["base_wall_thickness"] - 2 * wall_depth,
        "single_sided_outer_wall_mm": params["organizer"]["base_wall_thickness"] - wall_depth,
        "wall_top_vertical_reserve_mm": params["organizer"]["divider_height"] - top_depth,
    }
    checks["wall_reserves"] = all(value >= minimum for key, value in reserves.items() if key != "wall_top_vertical_reserve_mm")
    checks["connector_keepout_defined"] = texture["protected_regions"]["connector_margin_mm"] >= 3.0
    checks["wall_top_comfort_band_defined"] = texture["protected_regions"]["wall_top_smooth_edge_mm"] >= 0.55

    coverage = {}
    triangle_budget = texture["memory_strategy"]["review_triangles_per_module"]
    for module in build["modules"]:
        by_surface = module["texture_stats"]["by_surface"]
        coverage[module["id"]] = {
            name: int(by_surface.get(name, {}).get("dimples", 0))
            for name in ("floor", "inner_walls", "wall_tops")
        }
    checks["all_modules_floor_textured"] = all(item["floor"] > 0 for item in coverage.values())
    checks["all_modules_inner_walls_textured"] = all(item["inner_walls"] > 0 for item in coverage.values())
    checks["all_modules_wall_tops_textured"] = all(item["wall_tops"] > 0 for item in coverage.values())
    checks["triangle_budget"] = all(module["triangles"] <= triangle_budget for module in build["modules"])
    checks["mesh_validation"] = bool(mesh["pass"])

    connector_hashes = {}
    for filename, expected in EXPECTED_CONNECTOR_HASHES.items():
        path = ROOT / "output" / "DRAFT" / filename
        actual = sha256_file(path)
        connector_hashes[filename] = {"expected_r1_3": expected, "actual_r1_4": actual, "unchanged": actual == expected}
    checks["connectors_byte_identical_to_r1_3"] = all(item["unchanged"] for item in connector_hashes.values())

    peak = float(build["peak_module_process_rss_mib"])
    checks["memory_stop_gate"] = peak <= float(texture["memory_strategy"]["stop_peak_rss_mib"])
    assembly = ROOT / package["file"]
    with zipfile.ZipFile(assembly) as archive:
        bad = archive.testzip()
    checks["three_mf_crc"] = bad is None and package["status"] == "PASS"

    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "revision": params["model_revision"],
        "representation": texture["representation"],
        "seed": texture["seed"],
        "checks": checks,
        "nominal_depths_mm": {"floor": floor_depth, "inner_walls": wall_depth, "wall_tops": top_depth},
        "minimum_residual_wall_mm": minimum,
        "calculated_reserves_mm": reserves,
        "coverage_dimples": coverage,
        "connector_regression": connector_hashes,
        "peak_module_process_rss_mib": peak,
        "target_peak_rss_mib": texture["memory_strategy"]["target_peak_rss_mib"],
        "stop_peak_rss_mib": texture["memory_strategy"]["stop_peak_rss_mib"],
        "triangle_review_gate_per_module": triangle_budget,
        "three_mf": {"file": str(assembly.relative_to(ROOT)), "crc_bad_file": bad},
        "limitations": [
            "Visual realism, directional sheen, and cleanability still require the supplied process-matched coupon.",
            "Connector geometry is unchanged; the previously reported physical fit remains unqualified until a real coupon is measured."
        ]
    }
    destination = ROOT / "reports" / "surface-texture-validation.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
