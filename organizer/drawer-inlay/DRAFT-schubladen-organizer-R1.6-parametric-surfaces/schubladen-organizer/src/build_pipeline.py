#!/usr/bin/env python3
"""Build one selected surface profile, then validate and package it."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from surface_profiles import formatted_export, resolve_surface_profile, surface_choices


ROOT = Path(__file__).resolve().parent.parent
MODULES = ("driver-front", "driver-back", "hardware-front", "hardware-back")
MAIN_STLS = tuple(ROOT / "output" / "DRAFT" / f"DRAFT-{name}-surface.stl" for name in MODULES)
ACCESSORY_STLS = (
    ROOT / "output" / "DRAFT" / "DRAFT-screwdriver-comb.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-drawer-fit-corner-coupon.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-surface-texture-coupon.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-connector-coupon-male.stl",
    ROOT / "output" / "DRAFT" / "DRAFT-connector-coupon-female.stl",
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run(command: list[str], label: str) -> dict:
    print(f"[{label}] {' '.join(command)}", flush=True)
    started = time.monotonic()
    subprocess.run(command, cwd=ROOT, check=True, shell=False)
    return {"label": label, "elapsed_seconds": round(time.monotonic() - started, 3)}


def aggregate_build_reports(surface_id: str) -> dict:
    module_reports = [read_json(ROOT / "reports" / f"build-final-{name}.json") for name in MODULES]
    accessories = read_json(ROOT / "reports" / "build-final-accessories.json")
    params = read_json(ROOT / "config" / "model-params.json")
    if any(report["surface_texture"]["profile_id"] != surface_id for report in module_reports):
        raise RuntimeError("module reports contain a stale surface profile")
    combined = {
        "status": "DRAFT",
        "quality": "final",
        "engine": "manifold-3d",
        "revision": params["model_revision"],
        "surface_profile": surface_id,
        "execution_strategy": "one-module-per-process; one-procedural-texture-patch-at-a-time",
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


def repair_outputs(events: list[dict]) -> None:
    repair_reports = []
    repair_targets = MAIN_STLS + (ROOT / "output" / "DRAFT" / "DRAFT-surface-texture-coupon.stl",)
    for path in repair_targets:
        report_path = ROOT / "reports" / f"stl-repair-{path.stem}.json"
        events.append(run([
            sys.executable,
            "src/repair_stl.py",
            str(path),
            "--report",
            str(report_path),
            "--mesh-cache-dir",
            str(ROOT / "reports" / "mesh-cache"),
        ], f"repair:{path.stem}"))
        repair_reports.extend(read_json(report_path)["files"])
    write_json(ROOT / "reports" / "stl-repair.json", {"repair": "local-degenerate-edge-collapse-v1", "files": repair_reports})


def validate_outputs(events: list[dict], surface_id: str) -> dict:
    results = []
    for path in MAIN_STLS + ACCESSORY_STLS:
        report_path = ROOT / "reports" / f"mesh-validation-{path.stem}.json"
        events.append(run([
            sys.executable,
            "src/validate_stl.py",
            str(path),
            "--report",
            str(report_path),
            "--require-pass",
        ], f"validate:{path.stem}"))
        results.extend(read_json(report_path)["files"])
    summary = {
        "validator": "independent-stl-edge-audit-v1",
        "weld_tolerance_mm": 1.0e-9,
        "surface_profile": surface_id,
        "files": results,
        "pass": all(item["pass"] for item in results),
    }
    write_json(ROOT / "reports" / "mesh-validation.json", summary)
    events.append(run([
        sys.executable,
        "src/validate_surface_texture.py",
        "--surface",
        surface_id,
    ], "validate:surface-texture-and-interfaces"))
    return summary


def ensure_3mf_ready(events: list[dict], surface_id: str) -> None:
    params = read_json(ROOT / "config" / "model-params.json")
    path = ROOT / "output" / "DRAFT" / formatted_export(params, "assembly_filename_template", surface_id)

    def valid() -> bool:
        if not zipfile.is_zipfile(path):
            return False
        with zipfile.ZipFile(path) as archive:
            return archive.testzip() is None

    if valid():
        return
    events.append(run([
        sys.executable,
        "src/package_3mf.py",
        "--quality",
        "final",
        "--surface",
        surface_id,
    ], "package:3mf-retry"))
    if not valid():
        raise RuntimeError(f"3MF remained invalid after deterministic retry: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--surface", choices=surface_choices(ROOT))
    args = parser.parse_args()
    surface_id, _, texture_cfg = resolve_surface_profile(ROOT, args.surface)
    events: list[dict] = []

    if not args.validate_only:
        old_space = int(texture_cfg["memory_strategy"].get("node_old_space_mb", 2048))
        node = [
            "node",
            f"--max-old-space-size={old_space}",
            "src/manifold_build.mjs",
            "--quality",
            "final",
            "--surface",
            surface_id,
        ]
        for module in MODULES:
            events.append(run(node + ["--module", module], f"build:{module}"))
        events.append(run(node + ["--accessories"], "build:accessories"))
        aggregate_build_reports(surface_id)
        repair_outputs(events)
        events.append(run([
            sys.executable,
            "src/package_3mf.py",
            "--quality",
            "final",
            "--surface",
            surface_id,
        ], "package:3mf"))
        ensure_3mf_ready(events, surface_id)

    validation = validate_outputs(events, surface_id)
    build = read_json(ROOT / "reports" / "build-final.json")
    pipeline = {
        "status": "PASS" if validation["pass"] else "FAIL",
        "strategy": build["execution_strategy"],
        "surface_profile": surface_id,
        "representation": texture_cfg["representation"],
        "peak_module_process_rss_mib": build["peak_module_process_rss_mib"],
        "events": events,
    }
    write_json(ROOT / "reports" / "build-pipeline.json", pipeline)
    print(json.dumps(pipeline, indent=2))
    return 0 if pipeline["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
