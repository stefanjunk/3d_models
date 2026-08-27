#!/usr/bin/env python3
"""Validate R1.5 wood-texture coverage, protected interfaces, budgets, and 3MF."""

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


def maximum_depth(surface: dict) -> float:
    values = list(surface["grain"]["depth_mm"])
    if surface.get("knots", {}).get("enabled"):
        values.extend(surface["knots"]["depth_mm"])
    return max(float(value) for value in values)


def main() -> None:
    params = read_json(ROOT / "config" / "model-params.json")
    texture = read_json(ROOT / "config" / "surface-texture.json")
    build = read_json(ROOT / "reports" / "build-final.json")
    mesh = read_json(ROOT / "reports" / "mesh-validation.json")
    package = read_json(ROOT / "reports" / "three-mf-package.json")
    checks: dict[str, bool] = {}

    checks["procedural_representation"] = texture["representation"] == "deterministic-vector-grain-and-knot-grooves"
    checks["image_relief_inactive"] = "relief" not in params
    checks["approved_surfaces_enabled"] = all(texture["surfaces"][name]["enabled"] for name in ("floor", "inner_walls", "wall_tops"))
    checks["outer_walls_smooth"] = not texture["surfaces"]["outer_walls"]["enabled"]

    floor_depth = maximum_depth(texture["surfaces"]["floor"])
    wall_depth = maximum_depth(texture["surfaces"]["inner_walls"])
    top_depth = maximum_depth(texture["surfaces"]["wall_tops"])
    minimum = float(texture["protected_regions"]["minimum_residual_wall_mm"])
    base_wall = float(params["organizer"]["base_wall_thickness"])
    reserves = {
        "floor_below_top_texture_mm": float(params["organizer"]["floor_thickness"]) - floor_depth,
        "floor_below_watermark_mm": float(params["organizer"]["floor_thickness"]) - float(params["watermark"]["depth"]),
        "double_sided_divider_mm": base_wall - 2 * wall_depth,
        "single_sided_outer_wall_mm": base_wall - wall_depth,
        "wall_top_vertical_reserve_mm": float(params["organizer"]["divider_height"]) - top_depth,
    }
    checks["wall_reserves"] = all(
        value >= minimum for key, value in reserves.items() if key != "wall_top_vertical_reserve_mm"
    )
    checks["connector_keepout_defined"] = float(texture["protected_regions"]["connector_margin_mm"]) >= 3.0
    checks["wall_top_comfort_band_defined"] = float(texture["protected_regions"]["wall_top_smooth_edge_mm"]) >= 0.55

    coverage: dict[str, dict] = {}
    triangle_budget = int(texture["memory_strategy"]["review_triangles_per_module"])
    mesh_stop_bytes = int(float(texture["memory_strategy"]["mesh_stop_mib_per_module"]) * 1024 * 1024)
    for module in build["modules"]:
        by_surface = module["texture_stats"]["by_surface"]
        coverage[module["id"]] = {
            name: {
                "grooves": int(by_surface.get(name, {}).get("grooves", 0)),
                "grain_lines": int(by_surface.get(name, {}).get("grain_lines", 0)),
                "knots": int(by_surface.get(name, {}).get("knots", 0)),
            }
            for name in ("floor", "inner_walls", "wall_tops")
        }
    checks["all_modules_floor_textured"] = all(item["floor"]["grooves"] > 0 for item in coverage.values())
    checks["all_modules_inner_walls_textured"] = all(item["inner_walls"]["grooves"] > 0 for item in coverage.values())
    checks["all_modules_wall_tops_textured"] = all(item["wall_tops"]["grooves"] > 0 for item in coverage.values())
    checks["sparse_knot_limit"] = all(item["floor"]["knots"] <= 2 for item in coverage.values())
    checks["triangle_budget"] = all(int(module["triangles"]) <= triangle_budget for module in build["modules"])
    checks["mesh_size_budget"] = all(
        (ROOT / "output" / "DRAFT" / module["file"]).stat().st_size <= mesh_stop_bytes
        for module in build["modules"]
    )
    checks["mesh_validation"] = bool(mesh["pass"])

    connector_hashes = {}
    for filename, expected in EXPECTED_CONNECTOR_HASHES.items():
        path = ROOT / "output" / "DRAFT" / filename
        actual = sha256_file(path)
        connector_hashes[filename] = {"expected_r1_4": expected, "actual_r1_5": actual, "unchanged": actual == expected}
    checks["connectors_byte_identical_to_r1_4"] = all(item["unchanged"] for item in connector_hashes.values())

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
        "nominal_maximum_depths_mm": {"floor": floor_depth, "inner_walls": wall_depth, "wall_tops": top_depth},
        "minimum_residual_wall_mm": minimum,
        "calculated_reserves_mm": reserves,
        "coverage": coverage,
        "connector_regression": connector_hashes,
        "peak_module_process_rss_mib": peak,
        "target_peak_rss_mib": texture["memory_strategy"]["target_peak_rss_mib"],
        "stop_peak_rss_mib": texture["memory_strategy"]["stop_peak_rss_mib"],
        "triangle_review_gate_per_module": triangle_budget,
        "mesh_stop_mib_per_module": texture["memory_strategy"]["mesh_stop_mib_per_module"],
        "three_mf": {"file": str(assembly.relative_to(ROOT)), "crc_bad_file": bad},
        "exact_slicer_resolution_check": {
            "status": "BLOCKED",
            "limit_seconds": texture["memory_strategy"]["exact_slicer_stop_seconds"],
            "reason": "No exact target slicer executable/profile is available in this environment; inspect the supplied 3MF with the intended printer profile."
        },
        "mesh_simplification_gate": {
            "status": "not-beneficial",
            "policy": "retain deterministic high-fidelity manufacturing meshes; no lossy decimation",
            "reason": "All module meshes remain below the declared triangle and file-size stop gates; exact connectors, bed plane, watermark, and shallow wood grooves stay protected."
        },
        "limitations": [
            "Wood realism, directional sheen, cleanability, and comfort require the supplied process-matched coupon.",
            "Connector geometry is unchanged; the previously reported physical non-fit remains unresolved until a real connector coupon is measured."
        ]
    }
    destination = ROOT / "reports" / "surface-texture-validation.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
