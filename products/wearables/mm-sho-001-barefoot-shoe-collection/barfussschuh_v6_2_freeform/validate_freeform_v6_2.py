#!/usr/bin/env python3
"""Specialist fairness, hardpoint, collar, and tessellation checks for V6.2."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import yaml
from scipy.signal import find_peaks


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


def fairness_metrics(model, curves_dir: Path) -> dict:
    curves_dir.mkdir(parents=True, exist_ok=True)
    y = np.linspace(0.0, model.length, 4001)
    rails = [-0.90, -0.65, -0.35, 0.0, 0.35, 0.65, 0.90]
    results = {}
    for rail in rails:
        r = np.full_like(y, rail)
        points = model.surface_point(y, r)
        name = f"guide-r-{rail:+.2f}".replace("+", "p").replace("-", "m").replace(".", "p")
        np.savetxt(
            curves_dir / f"{name}.csv",
            points,
            delimiter=",",
            header="x,y,z",
            comments="",
            fmt="%.9f",
        )
        first = np.gradient(points, y, axis=0)
        second = np.gradient(first, y, axis=0)
        speed = np.linalg.norm(first, axis=1)
        curvature = np.linalg.norm(np.cross(first, second), axis=1) / np.maximum(speed**3, 1.0e-12)
        peaks, properties = find_peaks(curvature, prominence=0.005)
        central = [
            int(index)
            for index in peaks
            if 0.14 * model.length <= y[index] <= 0.88 * model.length
        ]
        results[f"r={rail:+.2f}"] = {
            "csv": str((curves_dir / f"{name}.csv").relative_to(HERE)),
            "point_count": int(len(points)),
            "length_mm": float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum()),
            "curvature_rms_1_per_mm": float(np.sqrt(np.mean(curvature**2))),
            "curvature_max_1_per_mm": float(np.max(curvature)),
            "all_prominent_extrema": int(len(peaks)),
            "unexplained_central_extrema": int(len(central)),
            "unexplained_central_curvature_max_1_per_mm": float(max((curvature[index] for index in central), default=0.0)),
            "unexplained_central_y_mm": [float(y[index]) for index in central],
            "explained_transition_zones": [
                [0.0, 0.14 * model.length],
                [0.88 * model.length, model.length],
            ],
        }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=HERE / "parameters.yaml")
    parser.add_argument("--generation-report", type=Path, default=HERE / "validation" / "generation-report.json")
    parser.add_argument("--json-out", type=Path, default=HERE / "validation" / "freeform-validation.json")
    args = parser.parse_args()

    parameters_path = args.parameters.resolve()
    generation_path = args.generation_report.resolve()
    params = yaml.safe_load(parameters_path.read_text())
    generation = json.loads(generation_path.read_text())
    generator = load_generator()
    model = generator.FreeformUpper(params)

    checks = []
    method = generation["method"]
    method_pass = (
        method["name"] == "direct-c2-freeform-domain-loft"
        and not method["voxel_grid"]
        and not method["distance_field"]
        and not method["marching_cubes"]
        and not method["global_remesh"]
    )
    checks.append(check("direct-freeform-method", method_pass, "Upper uses the approved direct freeform route", method))

    drift = float(generation["maximum_interface_drift_mm"])
    checks.append(
        check(
            "protected-sole-interface",
            drift <= 0.20,
            "Sole/lip attachment hardpoints remain within the approved drift",
            {"maximum_drift_mm": drift, "limit_mm": 0.20},
        )
    )

    construction = generation["construction"]
    fuzzy = construction["fuzzy_shell"]
    frame = construction["reinforcement_frame"]
    wall_pass = (
        fuzzy["constructed_wall_min_mm"] >= 1.40 - 1.0e-9
        and fuzzy["collar_constructed_wall_mm"] >= 2.60 - 1.0e-9
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
                "frame_collar_wall_mm": frame["collar_constructed_wall_mm"],
                "base_minimum_mm": 1.40,
                "collar_minimum_mm": 2.60,
            },
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
        },
        "limitations": [
            "Numerical fairness does not replace highlight/zebra review.",
            "Constructed offset distance is not a physical TPU wall measurement.",
            "Comfort, fit, flex life, skin compatibility, and appearance remain human/physical gates.",
        ],
        "required_capabilities": ["numpy", "scipy", "yaml"],
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(args.json_out), "checks": len(checks)}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
