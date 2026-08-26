#!/usr/bin/env python3
"""Revision-routed, one-process-per-module organizer build and validation pipeline."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

try:  # Supports both `python src/build_pipeline.py` and unit-test imports.
    from .validate_r2_procedural_wood import (
        MODULES,
        budget_metrics,
        check_r2_build_freshness,
        r2_stl_names,
    )
except ImportError:
    from validate_r2_procedural_wood import (
        MODULES,
        budget_metrics,
        check_r2_build_freshness,
        r2_stl_names,
    )


ROOT = Path(__file__).resolve().parent.parent
LEGACY_MODULES = MODULES
MAIN_STLS = tuple(ROOT / "output" / "DRAFT" / f"DRAFT-{name}-textured.stl" for name in LEGACY_MODULES)
ACCESSORY_STLS = (
    ROOT / "output" / "DRAFT" / "DRAFT-screwdriver-comb.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-drawer-fit-corner-coupon.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-relief-depth-coupon.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-connector-coupon-male.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-connector-coupon-female.stl",
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def identity(path: Path, root: Path = ROOT) -> dict:
    return {"path": str(path.relative_to(root)), "sha256": sha256_file(path)}


def run(command: list[str], label: str, *, check: bool = True) -> dict:
    print(f"[{label}] {' '.join(command)}", flush=True)
    started = time.monotonic()
    completed = subprocess.run(command, cwd=ROOT, check=False, shell=False)
    event = {
        "label": label,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "returncode": completed.returncode,
    }
    if check and completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, command)
    return event


def select_pipeline_route(model_revision: str) -> str:
    return "r2-procedural-wood-draft" if model_revision.startswith("R2-procedural-wood") else "legacy-r1-relief"


def r2_stl_paths(root: Path = ROOT) -> tuple[Path, ...]:
    return tuple(root / "output" / "DRAFT" / name for name in r2_stl_names())


def require_fresh_r2_build_inputs(root: Path = ROOT) -> dict[str, dict]:
    errors, reports = check_r2_build_freshness(root)
    if errors:
        raise RuntimeError("R2 freshness/hash gate failed:\n- " + "\n- ".join(errors))
    return reports


def validate_r2_stls(events: list[dict], root: Path = ROOT) -> dict:
    expected = r2_stl_paths(root)
    actual = tuple(sorted((root / "output" / "DRAFT").glob("DRAFT-R2-*.stl")))
    if set(actual) != set(expected) or len(actual) != 9:
        raise RuntimeError(
            f"R2 requires exactly nine named STL deliverables; found {[path.name for path in actual]}"
        )
    results: list[dict] = []
    for path in expected:
        relative = path.relative_to(root)
        report_path = root / "reports" / f"R2-mesh-validation-{path.stem}.json"
        events.append(
            run(
                [
                    sys.executable,
                    "src/validate_stl.py",
                    str(relative),
                    "--report",
                    str(report_path.relative_to(root)),
                    "--require-pass",
                ],
                f"validate-r2:{path.stem}",
            )
        )
        report = read_json(report_path)
        if len(report.get("files", [])) != 1:
            raise RuntimeError(f"independent STL validator did not return exactly one result for {relative}")
        results.append(report["files"][0])
    summary = {
        "status": "DRAFT",
        "revision": read_json(root / "config" / "model-params.json")["model_revision"],
        "validator": "independent-stl-edge-audit-v1",
        "weld_tolerance_mm": 1.0e-9,
        "expected_file_count": 9,
        "files": results,
        "pass": len(results) == 9 and all(item["pass"] for item in results),
    }
    write_json(root / "reports" / "R2-procedural-wood-unmarked-mesh-validation.json", summary)
    return summary


def compact_module(report: dict) -> dict:
    module = copy.deepcopy(report["module"])
    module.pop("surface_plan", None)
    module["surface_plan_identity"] = report["surface_plan_identity"]
    module["process_memory"] = report["process_memory"]
    module["resource_budget"] = report["resource_budget"]
    module["identities"] = report["identities"]
    return module


def aggregate_r2_build_reports(root: Path = ROOT) -> dict:
    reports = require_fresh_r2_build_inputs(root)
    params = read_json(root / "config" / "model-params.json")
    wood = read_json(root / "config" / "wood-texture-params.json")
    module_rows = [
        {
            "id": module,
            "triangles": int(reports[module]["module"]["triangles"]),
            "file_bytes": int(reports[module]["module"]["file_bytes"]),
            "peak_rss_mib": float(reports[module]["process_memory"]["max_rss_mib"]),
        }
        for module in MODULES
    ]
    budgets = budget_metrics(module_rows, wood["resource_budget"])
    accessory = copy.deepcopy(reports["accessories"])
    accessory.pop("comb_texture_plan", None)
    coupon = copy.deepcopy(reports["wood-coupon"])
    coupon.get("coupon", {}).pop("plan", None)
    source_paths = [
        root / "reports" / f"build-final-R2-{module}-procedural-wood-unmarked.json"
        for module in MODULES
    ] + [
        root / "reports" / "build-final-R2-accessories-procedural-wood-unmarked.json",
        root / "reports" / "build-final-wood-coupon.json",
    ]
    combined = {
        "status": "DRAFT",
        "quality": "final",
        "engine": "manifold-3d",
        "revision": params["model_revision"],
        "route": "r2-procedural-wood-unmarked-draft",
        "execution_strategy": "four sequential module processes; R2 accessories; wood coupon; no raster/heightmap/release packaging",
        "relief_loaded": False,
        "watermark": {"loaded": False, "applied": False},
        "modules": [compact_module(reports[module]) for module in MODULES],
        "accessories": accessory,
        "wood_coupon": coupon,
        "process_memory": {
            "modules": {module: reports[module]["process_memory"] for module in MODULES},
            "accessories": reports["accessories"]["process_memory"],
            "wood_coupon": reports["wood-coupon"]["process_memory"],
        },
        "budgets": budgets,
        "assembly_envelope": {
            "min": [0.0, 0.0, 0.0],
            "max": [
                float(params["organizer"]["width_x"]),
                float(params["organizer"]["depth_y"]),
                float(params["organizer"]["outer_wall_height"]),
            ],
        },
        "source_reports": [identity(path, root) for path in source_paths],
    }
    write_json(root / "reports" / "build-final-R2-procedural-wood-unmarked.json", combined)
    return combined


def run_r2_pipeline(validate_only: bool) -> int:
    params = read_json(ROOT / "config" / "model-params.json")
    wood = read_json(ROOT / "config" / "wood-texture-params.json")
    events: list[dict] = []
    if not validate_only:
        old_space = int(wood["memory_strategy"].get("node_old_space_mb", 2048))
        node = ["node", f"--max-old-space-size={old_space}", "src/manifold_build.mjs", "--quality", "final"]
        for module in MODULES:
            events.append(run(node + ["--r2-module", module], f"build-r2:{module}"))
        events.append(run(node + ["--r2-accessories"], "build-r2:accessories"))
        events.append(run(node + ["--wood-coupon"], "build-r2:wood-coupon"))

    require_fresh_r2_build_inputs(ROOT)
    topology = validate_r2_stls(events)
    if not validate_only:
        events.append(
            run([sys.executable, "src/package_3mf.py", "--quality", "final", "--r2-unmarked"], "package-r2:3mf")
        )
    build = aggregate_r2_build_reports(ROOT)
    events.append(
        run([sys.executable, "src/validate_r2_procedural_wood.py"], "validate-r2:digital", check=False)
    )
    digital_path = ROOT / "reports" / "R2-procedural-wood-digital-validation.json"
    digital = read_json(digital_path) if digital_path.is_file() else {"status": "FAIL", "errors": ["missing validator report"]}
    pipeline = {
        "status": "PASS" if topology["pass"] and digital.get("status") == "PASS" else "FAIL",
        "artifact_status": "DRAFT",
        "revision": params["model_revision"],
        "route": "r2-procedural-wood-unmarked-draft",
        "validate_only": validate_only,
        "strategy": build["execution_strategy"],
        "aggregate_triangles": build["budgets"]["aggregate_triangles"],
        "aggregate_stl_bytes": build["budgets"]["aggregate_stl_bytes"],
        "triangle_reduction_fraction": build["budgets"]["triangle_reduction_fraction"],
        "byte_reduction_fraction": build["budgets"]["byte_reduction_fraction"],
        "per_module_peak_rss_mib": {
            row["id"]: row["peak_rss_mib"] for row in build["budgets"]["per_module"]
        },
        "slicer_check": {"availability": "UNAVAILABLE", "status": "NOT_RUN", "passed": None},
        "physical_check": {"availability": "UNAVAILABLE", "status": "NOT_RUN", "passed": None},
        "events": events,
        "digital_validation_report": "reports/R2-procedural-wood-digital-validation.json",
        "errors": digital.get("errors", []),
    }
    write_json(ROOT / "reports" / "build-pipeline-R2-procedural-wood-unmarked.json", pipeline)
    print(json.dumps(pipeline, indent=2))
    return 0 if pipeline["status"] == "PASS" else 2


# Explicit legacy R1 branch retained below; R2 never calls these relief/repair validators.
def aggregate_legacy_build_reports() -> dict:
    module_reports = [read_json(ROOT / "reports" / f"build-final-{name}.json") for name in LEGACY_MODULES]
    accessories = read_json(ROOT / "reports" / "build-final-accessories.json")
    params = read_json(ROOT / "config" / "model-params.json")
    combined = {
        "status": "DRAFT",
        "quality": "final",
        "engine": "manifold-3d",
        "revision": params["model_revision"],
        "execution_strategy": "one-module-per-process; one-relief-surface-at-a-time",
        "modules": [report["modules"][0] for report in module_reports],
        "accessories": accessories["accessories"],
        "process_memory": [report["process_memory"] for report in module_reports] + [accessories["process_memory"]],
        "peak_module_process_rss_mib": max(report["process_memory"]["max_rss_mib"] for report in module_reports),
        "assembly_envelope": {
            "min": [0.0, 0.0, 0.0],
            "max": [
                float(params["organizer"]["width_x"]),
                float(params["organizer"]["depth_y"]),
                float(params["organizer"]["outer_wall_height"]),
            ],
        },
    }
    write_json(ROOT / "reports" / "build-final.json", combined)
    return combined


def repair_legacy_outputs(events: list[dict]) -> None:
    repair_reports = []
    repair_targets = MAIN_STLS + (ROOT / "output" / "DRAFT" / "DRAFT-relief-depth-coupon.stl",)
    for path in repair_targets:
        report_path = ROOT / "reports" / f"stl-repair-{path.stem}.json"
        events.append(
            run(
                [
                    sys.executable,
                    "src/repair_stl.py",
                    str(path),
                    "--report",
                    str(report_path),
                    "--mesh-cache-dir",
                    str(ROOT / "reports" / "mesh-cache"),
                ],
                f"repair:{path.stem}",
            )
        )
        repair_reports.extend(read_json(report_path)["files"])
    write_json(ROOT / "reports" / "stl-repair.json", {"repair": "local-degenerate-edge-collapse-v1", "files": repair_reports})


def validate_legacy_outputs(events: list[dict]) -> dict:
    results = []
    for path in MAIN_STLS + ACCESSORY_STLS:
        report_path = ROOT / "reports" / f"mesh-validation-{path.stem}.json"
        events.append(
            run(
                [sys.executable, "src/validate_stl.py", str(path), "--report", str(report_path), "--require-pass"],
                f"validate:{path.stem}",
            )
        )
        results.extend(read_json(report_path)["files"])
    summary = {
        "validator": "independent-stl-edge-audit-v1",
        "weld_tolerance_mm": 1.0e-9,
        "files": results,
        "pass": all(item["pass"] for item in results),
    }
    write_json(ROOT / "reports" / "mesh-validation.json", summary)
    events.append(run([sys.executable, "src/validate_continuous_relief.py"], "validate:continuous-relief-and-3mf"))
    return summary


def run_legacy_pipeline(validate_only: bool) -> int:
    events: list[dict] = []
    if not validate_only:
        relief_cfg = read_json(ROOT / "config" / "relief-config.json")
        old_space = int(relief_cfg["memory_strategy"].get("node_old_space_mb", 4096))
        node = ["node", f"--max-old-space-size={old_space}", "src/manifold_build.mjs", "--quality", "final"]
        for module in LEGACY_MODULES:
            events.append(run(node + ["--module", module], f"build:{module}"))
        events.append(run(node + ["--accessories"], "build:accessories"))
        aggregate_legacy_build_reports()
        repair_legacy_outputs(events)
        events.append(run([sys.executable, "src/package_3mf.py", "--quality", "final"], "package:3mf"))
    validation = validate_legacy_outputs(events)
    build = read_json(ROOT / "reports" / "build-final.json")
    pipeline = {
        "status": "PASS" if validation["pass"] else "FAIL",
        "strategy": build["execution_strategy"],
        "geometry_pitch_mm": read_json(ROOT / "config" / "relief-config.json")["geometry_pitch_mm"],
        "peak_module_process_rss_mib": build["peak_module_process_rss_mib"],
        "events": events,
    }
    write_json(ROOT / "reports" / "build-pipeline.json", pipeline)
    print(json.dumps(pipeline, indent=2))
    return 0 if pipeline["status"] == "PASS" else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    params = read_json(ROOT / "config" / "model-params.json")
    route = select_pipeline_route(str(params.get("model_revision", "")))
    if route == "r2-procedural-wood-draft":
        return run_r2_pipeline(args.validate_only)
    return run_legacy_pipeline(args.validate_only)


if __name__ == "__main__":
    raise SystemExit(main())
