#!/usr/bin/env python3
"""Build MM-ART-010 revision 0.5.1 with the approved metriMade marker.

The validated revision 0.5.0 generator owns all map, split, interface, light,
Z-band and manufacturing-mesh logic. This thin revision wrapper changes only
the immutable site-marker parameter set and writes into a new v0.5.1 output
namespace so earlier candidates can never be overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import trimesh

from micro_repair_composite import repair_mesh


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PREVIOUS_GENERATOR = PRODUCT / "source" / "v0.5.0" / "berlin" / "build_berlin_site_marker.py"
PARAMETERS = HERE / "site-marker-parameters.json"
COMPOSITE_BUILDER = HERE / "rebuild_composite_blender.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_previous_generator():
    spec = importlib.util.spec_from_file_location("mm_art_010_build_v051", PREVIOUS_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load previous generator: {PREVIOUS_GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_revision_composite_repair(previous) -> None:
    """Wrap the prior fail-closed rebuild with an audited micro-repair."""

    original_rebuild = previous.BASE.rebuild_composite

    def rebuild_composite(color_paths, raw_path, final_path):
        pre_repair_metrics, trace = original_rebuild(
            color_paths, raw_path, final_path
        )
        pre_repair_hash = sha256(final_path)
        source = trimesh.load_mesh(final_path, process=True)
        repaired, repair_trace = repair_mesh(source)
        repaired.export(final_path)
        final_metrics = previous.BASE.roundtrip_stl_metrics(final_path)
        required_final = {
            "watertight": True,
            "positive_volume": True,
            "connected_components": 1,
            "boundary_edges": 0,
            "nonmanifold_edges": 0,
            "degenerate_faces": 0,
            "duplicate_faces": 0,
        }
        failed = {
            key: {"expected": expected, "actual": final_metrics.get(key)}
            for key, expected in required_final.items()
            if final_metrics.get(key) != expected
        }
        if failed:
            raise ValueError(f"serialized micro-repaired composite failed: {failed}")
        trace["pre_repair_final"] = {
            "sha256": pre_repair_hash,
            "metrics": pre_repair_metrics,
        }
        trace["micro_repair"] = repair_trace
        trace["final_sha256"] = sha256(final_path)
        trace["final_metrics"] = final_metrics
        return final_metrics, trace

    previous.BASE.rebuild_composite = rebuild_composite


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    if not args.candidate.replace("-", "").isalnum():
        raise SystemExit("candidate must contain only letters, digits and hyphens")

    previous = load_previous_generator()
    previous.BASE.BLENDER_COMPOSITE_SCRIPT = COMPOSITE_BUILDER
    install_revision_composite_repair(previous)
    parameters = json.loads(PARAMETERS.read_text())
    if parameters.get("revision") != "0.5.1":
        raise SystemExit("site-marker parameters are not revision 0.5.1")
    if parameters.get("approval", {}).get("concept") != "approved":
        raise SystemExit("concept approval is not recorded")

    previous.SITE_PARAMETERS_PATH = PARAMETERS
    previous.SITE_PARAMETERS = parameters
    coordinate, geocode_path, geocode = previous.load_location()
    artwork_mask, artwork_path, renderer = previous.render_artwork_mask()
    artwork_cfg = parameters["site_marker"]["artwork"]
    if sha256(artwork_path) != artwork_cfg["asset_sha256"]:
        raise SystemExit("approved metriMade asset hash mismatch")
    provenance_path = previous.resolve_parameter_path(artwork_cfg["provenance"])
    if sha256(provenance_path) != artwork_cfg["provenance_sha256"]:
        raise SystemExit("metriMade provenance hash mismatch")

    required = [
        Path(__file__).resolve(),
        PREVIOUS_GENERATOR,
        PARAMETERS,
        COMPOSITE_BUILDER,
        provenance_path,
        previous.BASE_SCRIPT,
        previous.BASE.PARAMETERS_PATH,
        previous.BASE.INTERFACE_PARAMETERS_PATH,
        previous.BASE.BLENDER,
        previous.BLENDER_COMPOSITE_SCRIPT,
        previous.PALETTE_CATALOG_PATH,
        geocode_path,
        artwork_path,
        previous.BASE.SOURCE / "source-manifest.json",
        previous.BASE.SOURCE / "boundary.geojson",
        previous.BASE.SOURCE / "roads-major.geojson",
        previous.BASE.SOURCE / "roads-accent.geojson",
        previous.BASE.SOURCE / "rail.geojson",
        previous.BASE.SOURCE / "waterways.geojson",
        previous.BASE.PLACEMENT_DIR / "boundary-crop-placement.json",
        previous.BASE.PLACEMENT_DIR / "context-outline-placement.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing source or gate input(s): {missing}")
    if json.loads((previous.BASE.SOURCE / "source-manifest.json").read_text()).get("status") != "PASS":
        raise SystemExit("base source manifest is not PASS")

    export_root = PRODUCT / "exports" / "v0.5.1" / "berlin" / args.candidate
    validation_root = PRODUCT / "validation" / "v0.5.1" / "berlin" / args.candidate
    if export_root.exists() or validation_root.exists():
        raise SystemExit("refusing destructive overwrite of an existing candidate directory")
    export_root.mkdir(parents=True)
    (validation_root / "renders").mkdir(parents=True)

    mode_reports = {}
    for mode in previous.MODES:
        mode_export = export_root / mode.replace("_", "-")
        mode_export.mkdir()
        mode_reports[mode] = previous.build_mode(
            mode,
            mode_export,
            validation_root / "renders",
            artwork_mask,
            coordinate,
        )
    status = "PASS" if all(item["status"] == "PASS" for item in mode_reports.values()) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.5.1",
        "candidate": args.candidate,
        "status": status,
        "representation": "two display modes, two permanent halves per mode and four disjoint semantic tool solids per half; canonical stacked metriMade marker in tool 4",
        "unchanged_base_geometry": {
            "revision": "0.5.0/r7 pipeline over 0.4.0 map authority",
            "generator": str(PREVIOUS_GENERATOR.relative_to(PRODUCT)),
            "generator_sha256": sha256(PREVIOUS_GENERATOR),
            "base_map_generator": str(previous.BASE_SCRIPT.relative_to(PRODUCT)),
            "base_map_generator_sha256": sha256(previous.BASE_SCRIPT),
            "parameters": str(previous.BASE.PARAMETERS_PATH.relative_to(PRODUCT)),
            "parameters_sha256": sha256(previous.BASE.PARAMETERS_PATH),
            "composite_cleanup": str(COMPOSITE_BUILDER.relative_to(PRODUCT)),
            "composite_cleanup_sha256": sha256(COMPOSITE_BUILDER),
        },
        "site_marker": {
            "parameters": str(PARAMETERS.relative_to(PRODUCT)),
            "parameters_sha256": sha256(PARAMETERS),
            "artwork_id": artwork_cfg["asset_id"],
            "artwork": str(artwork_path.relative_to(PRODUCT.parents[2])),
            "artwork_sha256": sha256(artwork_path),
            "provenance": str(provenance_path.relative_to(PRODUCT.parents[2])),
            "provenance_sha256": sha256(provenance_path),
            "geocode": str(geocode_path.relative_to(PRODUCT)),
            "geocode_sha256": sha256(geocode_path),
            "coordinate_epsg25833": coordinate,
            "address": geocode["address_input"],
            "renderer": renderer,
            "semantic_tool": int(parameters["site_marker"]["relief"]["semantic_tool"]),
            "recognition_distance_target_mm": parameters["site_marker"]["viewing_intent"]["recognition_distance_mm"],
        },
        "selected_palette": {
            "preset": previous.SELECTED_PALETTE,
            "catalog": str(previous.PALETTE_CATALOG_PATH.relative_to(PRODUCT)),
            "catalog_sha256": sha256(previous.PALETTE_CATALOG_PATH),
            "tools": [previous.PALETTE[index] for index in sorted(previous.PALETTE)],
        },
        "tool_z_bands_mm": previous.BASE.Z_BANDS,
        "manufacturing_raster_pitch_mm": previous.BASE.RASTER_PITCH_MM,
        "marker_raster_pitch_mm": previous.MARKER_RASTER_PITCH_MM,
        "upper_color_edge_inset_mm": previous.BASE.UPPER_COLOR_EDGE_INSET_MM,
        "modes": mode_reports,
        "shared_secondary_parts": {
            "seam_connector": "exports/v0.3.0/interfaces/seam-connector-c025.stl",
            "upper_hanger": "exports/v0.3.0/interfaces/upper-hanger-18mm.stl",
            "lower_standoff": "exports/v0.3.0/interfaces/lower-standoff-18mm.stl",
            "reuse_basis": "map, seam, mounting and backlight authorities are unchanged; only the front marker asset/envelope changed",
        },
        "mesh_policy": {
            "status": "not-beneficial for additional post-build decimation",
            "tool_simplify_tolerances_mm": previous.TOOL_SIMPLIFY_MM,
            "protected_regions": [
                "metriMade marker silhouette and relief top",
                "outer perimeter and center seam",
                "rear connector and mounting pockets",
                "light apertures and retained bridges",
                "bed-contact plane",
            ],
            "triangle_target_per_main_half": 750000,
            "triangle_stop_per_main_half": 1500000,
            "peak_memory_gib": 4.0,
            "max_mesh_mib_per_main_half": 75.0,
            "max_exact_slice_seconds_per_half": 600,
        },
        "limitations": [
            "DRAFT digital candidate; physical 2 m logo recognition and connector/socket compensation remain coupon controlled.",
            "Exact ACE slots, purge matrix, wall anchors, physical load, lit appearance, brand clearance, rear release watermark and final release are not approved.",
            "A replacement address or artwork must be regenerated and fully revalidated.",
        ],
    }
    report_path = validation_root / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    manifest = {
        "schema_version": "1.0",
        "generator": str(Path(__file__).resolve().relative_to(PRODUCT)),
        "generator_sha256": sha256(Path(__file__).resolve()),
        "build_report": str(report_path.relative_to(PRODUCT)),
        "build_report_sha256": sha256(report_path),
    }
    (validation_root / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(report_path), "export_root": str(export_root)}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
