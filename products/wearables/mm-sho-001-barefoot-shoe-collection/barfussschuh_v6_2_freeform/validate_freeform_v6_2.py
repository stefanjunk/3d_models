#!/usr/bin/env python3
"""Specialist fairness, hardpoint, collar, and tessellation checks for V6.2."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

import numpy as np
import yaml
from scipy.signal import find_peaks

try:
    import pymeshlab
except ImportError:
    pymeshlab = None


HERE = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_generator():
    path = HERE / "generate_v6_2.py"
    spec = importlib.util.spec_from_file_location("mm_sho_001_v6_2_generator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def check(check_id: str, passed: bool, message: str, metrics: dict) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics,
        "evidence": [],
    }


def self_intersection_metrics(paths: list[Path]) -> tuple[str, dict]:
    if pymeshlab is None:
        return "NOT_RUN", {
            "backend": "pymeshlab",
            "reason": "PyMeshLab is unavailable",
            "artifacts": {},
        }
    try:
        backend_version = package_version("pymeshlab")
    except PackageNotFoundError:
        backend_version = "unknown"
    artifacts = {}
    failures = []
    for path in paths:
        mesh_set = pymeshlab.MeshSet()
        mesh_set.load_new_mesh(str(path))
        mesh_set.apply_filter("compute_selection_by_self_intersections_per_face")
        mesh = mesh_set.current_mesh()
        selection = np.asarray(mesh.face_selection_array(), dtype=bool)
        selected_count = int(np.count_nonzero(selection))
        metrics = {
            "path": str(path.relative_to(HERE)),
            "sha256": sha256_file(path),
            "selected_self_intersecting_faces": selected_count,
        }
        if selected_count:
            vertices = np.asarray(mesh.vertex_matrix(), dtype=float)
            faces = np.asarray(mesh.face_matrix(), dtype=np.int64)
            centroids = vertices[faces].mean(axis=1)[selection]
            metrics["selected_centroid_bounds_mm"] = [
                np.min(centroids, axis=0).tolist(),
                np.max(centroids, axis=0).tolist(),
            ]
            failures.append(metrics["path"])
        artifacts[path.name] = metrics
    return ("PASS" if not failures else "FAIL"), {
        "backend": "pymeshlab",
        "backend_version": backend_version,
        "filter": "compute_selection_by_self_intersections_per_face",
        "failures": failures,
        "artifacts": artifacts,
    }


def fairness_metrics(model, curves_dir: Path) -> dict:
    curves_dir.mkdir(parents=True, exist_ok=True)
    y = np.linspace(0.0, model.length, 4001)
    rails = [-0.90, -0.65, -0.35, 0.0, 0.35, 0.65, 0.90]
    semantic_y = np.unique(np.concatenate((model.sole_s, model.upper_s)) * model.length)
    semantic_tolerance_mm = 0.60
    results = {}
    for rail in rails:
        r = np.full_like(y, rail)
        points = model.surface_point(y, r)
        visible = model.collar_rho(y, r) >= 1.0
        visible_indices = np.flatnonzero(visible)
        segments = np.split(visible_indices, np.flatnonzero(np.diff(visible_indices) > 1) + 1)
        name = f"guide-r-{rail:+.2f}".replace("+", "p").replace("-", "m").replace(".", "p")
        export_points = points.copy()
        export_points[~visible] = np.nan
        np.savetxt(
            curves_dir / f"{name}.csv",
            export_points,
            delimiter=",",
            header="x,y,z",
            comments="",
            fmt="%.9f",
        )
        curvature = np.full(len(y), np.nan, dtype=float)
        peaks = []
        curve_length = 0.0
        for segment in segments:
            if len(segment) < 5:
                continue
            segment_y = y[segment]
            segment_points = points[segment]
            first = np.gradient(segment_points, segment_y, axis=0)
            second = np.gradient(first, segment_y, axis=0)
            speed = np.linalg.norm(first, axis=1)
            segment_curvature = np.linalg.norm(np.cross(first, second), axis=1) / np.maximum(
                speed**3,
                1.0e-12,
            )
            curvature[segment] = segment_curvature
            segment_peaks, _ = find_peaks(segment_curvature, prominence=0.005)
            peaks.extend(int(segment[index]) for index in segment_peaks)
            curve_length += float(np.linalg.norm(np.diff(segment_points, axis=0), axis=1).sum())
        collar_fairing = np.zeros(len(y), dtype=bool)
        if np.any(visible):
            collar_fairing[visible] = (
                model.band_distance(y[visible], r[visible], points[visible])
                <= model.collar_fairing_width + 1.0e-9
            )
        explained_semantic = [
            int(index)
            for index in peaks
            if np.min(np.abs(semantic_y - y[index])) <= semantic_tolerance_mm
        ]
        explained_collar = [
            int(index)
            for index in peaks
            if collar_fairing[index] and index not in explained_semantic
        ]
        central = [
            int(index)
            for index in peaks
            if 0.14 * model.length <= y[index] <= 0.88 * model.length
            and index not in explained_semantic
            and index not in explained_collar
        ]
        finite_curvature = curvature[np.isfinite(curvature)]
        results[f"r={rail:+.2f}"] = {
            "csv": str((curves_dir / f"{name}.csv").relative_to(HERE)),
            "point_count": int(np.count_nonzero(visible)),
            "visible_segment_count": int(sum(len(segment) >= 5 for segment in segments)),
            "opening_samples_excluded": int(np.count_nonzero(~visible)),
            "length_mm": curve_length,
            "curvature_rms_1_per_mm": float(np.sqrt(np.mean(finite_curvature**2))),
            "curvature_max_1_per_mm": float(np.max(finite_curvature)),
            "all_prominent_extrema": int(len(peaks)),
            "unexplained_central_extrema": int(len(central)),
            "unexplained_central_curvature_max_1_per_mm": float(max((curvature[index] for index in central), default=0.0)),
            "unexplained_central_y_mm": [float(y[index]) for index in central],
            "explained_semantic_extrema": int(len(explained_semantic)),
            "explained_semantic_y_mm": [float(y[index]) for index in explained_semantic],
            "explained_collar_fairing_extrema": int(len(explained_collar)),
            "explained_collar_fairing_y_mm": [float(y[index]) for index in explained_collar],
            "semantic_station_tolerance_mm": semantic_tolerance_mm,
            "explained_transition_zones": [
                [0.0, 0.14 * model.length],
                [0.88 * model.length, model.length],
            ],
        }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=HERE / "parameters.yaml")
    parser.add_argument("--generation-report", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    parameters_path = args.parameters.resolve()
    params = yaml.safe_load(parameters_path.read_text())
    revision = str(params["revision"])
    generation_path = (
        args.generation_report.resolve()
        if args.generation_report is not None
        else HERE / "validation" / f"generation-report-{revision}.json"
    )
    json_out = (
        args.json_out.resolve()
        if args.json_out is not None
        else HERE / "validation" / f"freeform-validation-{revision}.json"
    )
    generation = json.loads(generation_path.read_text())
    generator = load_generator()
    model = generator.FreeformUpper(params)

    checks = []
    binding_pass = (
        generation.get("project_id") == params["project_id"]
        and generation.get("revision") == revision
        and generation.get("parameters", {}).get("sha256") == sha256_file(parameters_path)
    )
    checks.append(
        check(
            "revision-and-input-binding",
            binding_pass,
            "Generated geometry is bound to the approved project revision and parameter hash",
            {
                "expected_project_id": params["project_id"],
                "reported_project_id": generation.get("project_id"),
                "expected_revision": revision,
                "reported_revision": generation.get("revision"),
                "expected_parameters_sha256": sha256_file(parameters_path),
                "reported_parameters_sha256": generation.get("parameters", {}).get("sha256"),
            },
        )
    )

    self_intersection_status, self_intersection_report = self_intersection_metrics(
        [HERE / item["path"] for item in generation["files"].values()]
    )
    checks.append(
        {
            "id": "mesh-self-intersections",
            "status": self_intersection_status,
            "required": True,
            "message": "Generated meshes contain no selected self-intersecting faces",
            "metrics": self_intersection_report,
            "evidence": [],
        }
    )
    method = generation["method"]
    method_pass = (
        method["name"] == "direct-c2-freeform-domain-loft"
        and method.get("sole_interface_interpolation") == "pchip-v6.1-compatible"
        and not method["voxel_grid"]
        and not method["distance_field"]
        and not method["marching_cubes"]
        and not method["global_remesh"]
    )
    checks.append(check("direct-freeform-method", method_pass, "Upper uses the approved direct freeform route", method))

    construction = generation["construction"]
    drift = float(generation["maximum_interface_drift_mm"])
    checks.append(
        check(
            "protected-sole-interface",
            drift <= 0.20,
            "Sole/lip attachment hardpoints remain within the approved drift",
            {"maximum_drift_mm": drift, "limit_mm": 0.20},
        )
    )

    rear_reserve = float(construction["collar_rear_reserve_mm"])
    rear_reserve_min = float(params["freeform"]["collar_rear_reserve_min"])
    heel_ratio = float(construction["heel_rise_transition_ratio"])
    heel_ratio_min = float(params["freeform"]["heel_rise_transition_ratio_min"])
    front_boundary_drift = float(construction["collar_front_boundary_drift_from_v6_1_mm"])
    collar_loop_counts = {
        name: int(construction[name]["collar_loops"])
        for name in ("fuzzy_shell", "infill_envelope", "reinforcement_frame")
    }
    collar_geometry_pass = (
        rear_reserve >= rear_reserve_min
        and heel_ratio >= heel_ratio_min
        and abs(front_boundary_drift) <= 0.20
        and all(value == 1 for value in collar_loop_counts.values())
    )
    checks.append(
        check(
            "draft2-collar-and-heel-geometry",
            collar_geometry_pass,
            "Draft-2 retains the approved rear reserve, extended heel rise, and one closed collar loop",
            {
                "rear_reserve_mm": rear_reserve,
                "rear_reserve_min_mm": rear_reserve_min,
                "heel_rise_transition_ratio": heel_ratio,
                "heel_rise_transition_ratio_min": heel_ratio_min,
                "heel_rise_transition_length_mm": float(construction["heel_rise_transition_length_mm"]),
                "front_boundary_drift_from_v6_1_mm": front_boundary_drift,
                "front_boundary_drift_limit_mm": 0.20,
                "opening_width_at_center_mm": float(construction["collar_opening_width_at_center_mm"]),
                "collar_loop_counts": collar_loop_counts,
            },
        )
    )

    collar_height_targets = construction["collar_edge_height_target_mm"]
    collar_height_measured = construction["collar_edge_height_measured_mm"]
    collar_height_error = {
        key: float(collar_height_measured[key]) - float(collar_height_targets[key])
        for key in ("front", "side", "rear")
    }
    checks.append(
        check(
            "collar-edge-height-profile",
            max(abs(value) for value in collar_height_error.values()) <= 0.05,
            "The faired collar loop reaches the approved front, side, and rear height profile",
            {
                "target_mm": collar_height_targets,
                "measured_mm": collar_height_measured,
                "error_mm": collar_height_error,
                "limit_mm": 0.05,
                "fairing_width_mm": float(construction["collar_fairing_width_mm"]),
            },
        )
    )

    fuzzy = construction["fuzzy_shell"]
    infill = construction["infill_envelope"]
    frame = construction["reinforcement_frame"]
    wall_pass = (
        fuzzy["constructed_wall_min_mm"] >= 1.40 - 1.0e-9
        and fuzzy["collar_constructed_wall_mm"] >= 2.60 - 1.0e-9
        and infill["constructed_wall_min_mm"] >= 1.40 - 1.0e-9
        and infill["constructed_wall_max_mm"] >= 4.50 - 1.0e-9
        and frame["collar_constructed_wall_mm"] >= 2.60 - 1.0e-9
    )
    checks.append(
        check(
            "collar-wall-contract",
            wall_pass,
            "Thin shell and reinforcement frame reach the approved collar wall",
            {
                "fuzzy_base_wall_mm": fuzzy["constructed_wall_min_mm"],
                "fuzzy_collar_wall_mm": fuzzy["collar_constructed_wall_mm"],
                "infill_end_closure_wall_min_mm": infill["constructed_wall_min_mm"],
                "infill_nominal_wall_max_mm": infill["constructed_wall_max_mm"],
                "frame_collar_wall_mm": frame["collar_constructed_wall_mm"],
                "base_minimum_mm": 1.40,
                "collar_minimum_mm": 2.60,
            },
        )
    )

    collar_edge_max = max(
        float(construction[name]["collar_outer_edge_max_mm"])
        for name in ("fuzzy_shell", "infill_envelope", "reinforcement_frame")
    )
    checks.append(
        check(
            "collar-tessellation",
            collar_edge_max <= 0.65,
            "Collar boundary tessellation remains below the approved edge target",
            {"maximum_edge_mm": collar_edge_max, "limit_mm": 0.65},
        )
    )

    visible_max = max(
        float(construction[name]["visible_outer_edge_max_mm"])
        for name in ("fuzzy_shell", "infill_envelope", "reinforcement_frame")
    )
    checks.append(
        check(
            "visible-tessellation",
            visible_max <= 1.25,
            "Visible freeform triangles remain below the approved edge target",
            {"maximum_edge_mm": visible_max, "limit_mm": 1.25},
        )
    )

    topology_failures = []
    budget_failures = []
    face_stop = int(params["tessellation"]["manufacturing_triangle_stop"])
    byte_stop = int(float(params["tessellation"]["maximum_mesh_mib"]) * 1024 * 1024)
    for item in generation["files"].values():
        if not (
            item["components"] == 1
            and item["watertight"]
            and item["winding_consistent"]
            and item["is_volume"]
            and item["volume_mm3"] > 0.0
            and item.get("degenerate_faces", 0) == 0
        ):
            topology_failures.append(item["path"])
        if item["faces"] > face_stop or item["bytes"] > byte_stop:
            budget_failures.append(item["path"])
    checks.append(
        check(
            "manufacturing-mesh-topology",
            not topology_failures,
            "Every generated mesh is a single watertight positive volume without degenerate faces",
            {"failures": topology_failures, "artifact_count": len(generation["files"])},
        )
    )
    checks.append(
        check(
            "manufacturing-mesh-budget",
            not budget_failures,
            "Generated meshes remain inside the declared triangle and file-size stop budgets",
            {
                "failures": budget_failures,
                "triangle_stop": face_stop,
                "maximum_mesh_bytes": byte_stop,
            },
        )
    )

    opening_reduction = float(construction["maximum_opening_reduction_each_side_mm"])
    checks.append(
        check(
            "collar-opening-preservation",
            opening_reduction <= 0.80,
            "Rounded free edge does not constrict the opening beyond the approved limit",
            {"maximum_reduction_each_side_mm": opening_reduction, "limit_mm": 0.80},
        )
    )

    curves = fairness_metrics(model, HERE / "source" / "curves")
    max_extrema = max(item["unexplained_central_extrema"] for item in curves.values())
    max_curvature = max(item["unexplained_central_curvature_max_1_per_mm"] for item in curves.values())
    fairness_pass = max_extrema <= 4 and max_curvature <= 0.05
    checks.append(
        check(
            "guide-curve-fairness",
            fairness_pass,
            "Central guide curves contain no unexplained high-frequency curvature oscillation",
            {
                "curves": curves,
                "maximum_unexplained_extrema": max_extrema,
                "extrema_limit": 4,
                "maximum_unexplained_curvature_1_per_mm": max_curvature,
                "curvature_limit_1_per_mm": 0.05,
                "note": "Tight heel/toe closure extrema are declared semantic transition features, not surface noise.",
            },
        )
    )

    file_failures = []
    for item in generation["files"].values():
        path = HERE / item["path"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            file_failures.append(item["path"])
    checks.append(
        check(
            "generation-artifact-freshness",
            not file_failures,
            "Generated artifacts match the hashes in the generation report",
            {"stale_or_missing": file_failures, "artifact_count": len(generation["files"])},
        )
    )

    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "schema_version": "1.0",
        "tool": "MM-SHO-001-freeform-validation",
        "tool_version": "1.0.0",
        "status": status,
        "profile": "draft",
        "inputs": [
            {
                "path": str(parameters_path.relative_to(HERE)),
                "sha256": sha256_file(parameters_path),
                "size_bytes": parameters_path.stat().st_size,
            },
            {
                "path": str(generation_path.relative_to(HERE)),
                "sha256": sha256_file(generation_path),
                "size_bytes": generation_path.stat().st_size,
            },
            {
                "path": "generate_v6_2.py",
                "sha256": sha256_file(HERE / "generate_v6_2.py"),
                "size_bytes": (HERE / "generate_v6_2.py").stat().st_size,
            },
        ],
        "checks": checks,
        "metrics": {
            "maximum_interface_drift_mm": drift,
            "maximum_visible_edge_mm": visible_max,
            "maximum_unexplained_curvature_1_per_mm": max_curvature,
            "maximum_unexplained_extrema": max_extrema,
            "collar_rear_reserve_mm": rear_reserve,
            "heel_rise_transition_ratio": heel_ratio,
            "maximum_collar_edge_mm": collar_edge_max,
        },
        "limitations": [
            "Numerical fairness does not replace highlight/zebra review.",
            "Constructed offset distance is not a physical TPU wall measurement.",
            "Comfort, fit, flex life, skin compatibility, and appearance remain human/physical gates.",
        ],
        "required_capabilities": ["numpy", "scipy", "yaml", "pymeshlab-self-intersection"],
    }
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(json_out), "checks": len(checks)}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
