#!/usr/bin/env python3
"""Validate the selected R1.6 surface profile and protected organizer core."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from surface_profiles import resolve_surface_profile, surface_choices


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
    return float(surface.get("maximum_depth_mm", 0.0)) if surface.get("enabled") else 0.0


def maximum_protrusion(surface: dict) -> float:
    return float(surface.get("maximum_protrusion_mm", 0.0)) if surface.get("enabled") else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface", choices=surface_choices(ROOT))
    args = parser.parse_args()
    surface_id, _, texture = resolve_surface_profile(ROOT, args.surface)
    params = read_json(ROOT / "config" / "model-params.json")
    build = read_json(ROOT / "reports" / "build-final.json")
    mesh = read_json(ROOT / "reports" / "mesh-validation.json")
    package = read_json(ROOT / "reports" / "three-mf-package.json")
    checks: dict[str, bool] = {}

    checks["selected_profile_matches_build"] = build.get("surface_profile") == surface_id
    checks["procedural_representation"] = texture["representation"] in {
        "deterministic-2x2-twill-lenticular-cell-field",
        "deterministic-reference-basket-weave-tow-cell-field",
        "deterministic-additive-band-limited-micro-cast-facet-field",
        "deterministic-vector-grain-and-knot-grooves",
        "deterministic-multiscale-analytic-dimple-field",
        "none-parametric-baseline",
    }
    checks["image_relief_inactive"] = "relief" not in params
    expected_enabled = surface_id != "plain"
    surface_policy = texture.get("surface_policy", {})
    required_enabled = surface_policy.get(
        "required_enabled", ["floor", "inner_walls", "wall_tops"] if expected_enabled else []
    )
    required_disabled = surface_policy.get(
        "required_disabled", ["floor", "inner_walls", "wall_tops", "outer_walls"] if not expected_enabled else ["outer_walls"]
    )
    checks["expected_surface_enablement"] = (
        all(bool(texture["surfaces"][name]["enabled"]) for name in required_enabled)
        and all(not bool(texture["surfaces"][name]["enabled"]) for name in required_disabled)
    )
    checks["outer_walls_smooth"] = not texture["surfaces"]["outer_walls"]["enabled"]

    floor_depth = maximum_depth(texture["surfaces"]["floor"])
    wall_depth = maximum_depth(texture["surfaces"]["inner_walls"])
    top_depth = maximum_depth(texture["surfaces"]["wall_tops"])
    protrusions = {
        name: maximum_protrusion(texture["surfaces"][name])
        for name in ("floor", "inner_walls", "wall_tops")
    }
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

    metric = texture["coverage_metric"]
    coverage: dict[str, dict] = {}
    observed_protrusions = {"floor": 0.0, "inner_walls": 0.0, "wall_tops": 0.0}
    triangle_budget = int(texture["memory_strategy"]["review_triangles_per_module"])
    mesh_stop_bytes = int(float(texture["memory_strategy"]["mesh_stop_mib_per_module"]) * 1024 * 1024)
    for module in build["modules"]:
        by_surface = module["texture_stats"].get("by_surface", {})
        coverage[module["id"]] = {
            name: int(by_surface.get(name, {}).get(metric, 0))
            for name in ("floor", "inner_walls", "wall_tops")
        }
        for name in observed_protrusions:
            observed_protrusions[name] = max(
                observed_protrusions[name],
                float(by_surface.get(name, {}).get("height_max_mm", 0.0)),
            )
    checks["expected_texture_coverage"] = all(
        value > 0 if texture["surfaces"][name]["enabled"] else value == 0
        for module in coverage.values()
        for name, value in module.items()
    )
    checks["observed_protrusion_within_profile"] = all(
        observed_protrusions[name] <= protrusions[name] + 1.0e-6
        for name in observed_protrusions
    )
    checks["micro_cast_raised_only_no_recesses"] = surface_id != "micro-cast" or (
        floor_depth == 0.0
        and wall_depth == 0.0
        and top_depth == 0.0
        and texture["surfaces"]["floor"].get("operation") == "additive-raised-only"
        and texture["surfaces"]["inner_walls"].get("operation") == "additive-raised-only"
    )
    checks["micro_cast_wall_tops_smooth"] = surface_id != "micro-cast" or (
        not texture["surfaces"]["wall_tops"]["enabled"]
        and protrusions["wall_tops"] == 0.0
        and top_depth == 0.0
    )
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
        connector_hashes[filename] = {"expected_r1_4": expected, "actual_r1_6": actual, "unchanged": actual == expected}
    checks["connectors_byte_identical_to_r1_4"] = all(item["unchanged"] for item in connector_hashes.values())

    peak = float(build["peak_module_process_rss_mib"])
    checks["memory_stop_gate"] = peak <= float(texture["memory_strategy"]["stop_peak_rss_mib"])
    assembly = ROOT / package["file"]
    with zipfile.ZipFile(assembly) as archive:
        bad = archive.testzip()
    checks["three_mf_crc"] = bad is None and package["status"] == "PASS" and package.get("surface_profile") == surface_id

    appearance = {
        "carbon": "Carbon twill recognition, angle-dependent sheen, cleanability, and comfort require the supplied process-matched coupon.",
        "carbon-wave": "Reference-derived 0/90 basket-weave recognition, horizontal tow dominance, directional sheen, cleanability, and comfort require the supplied process-matched coupon.",
        "micro-cast": "Matte line masking, raised micro-cast continuity, cleanability, and the absence of visually objectionable horizontal pits require the supplied process-matched coupon.",
        "walnut": "Walnut realism, directional sheen, cleanability, and comfort require the supplied process-matched coupon.",
        "steel": "Forged-steel appearance, sheen, cleanability, and comfort require the supplied process-matched coupon.",
        "plain": "The plain profile proves zero optional surface geometry; final material appearance remains slicer- and filament-dependent.",
    }[surface_id]
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "revision": params["model_revision"],
        "surface_profile": surface_id,
        "representation": texture["representation"],
        "seed": texture["seed"],
        "checks": checks,
        "coverage_metric": metric,
        "nominal_maximum_depths_mm": {"floor": floor_depth, "inner_walls": wall_depth, "wall_tops": top_depth},
        "nominal_maximum_protrusions_mm": protrusions,
        "observed_maximum_protrusions_mm": observed_protrusions,
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
            "reason": "No exact target slicer executable/profile is available in this environment; inspect the supplied 3MF with the intended printer profile.",
        },
        "mesh_simplification_gate": {
            "status": "not-beneficial",
            "policy": "retain deterministic manufacturing meshes; no global lossy decimation",
            "reason": "Functional interfaces, bed plane, watermark, and shallow selected surface geometry remain protected.",
        },
        "limitations": [
            appearance,
            "Connector geometry is unchanged; the previously reported physical non-fit remains unresolved until a real connector coupon is measured.",
        ],
    }
    destination = ROOT / "reports" / "surface-texture-validation.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
