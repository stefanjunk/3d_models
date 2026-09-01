#!/usr/bin/env python3
"""Fail closed when a mode half contains a floating backer or composite body."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report_path = (
        PRODUCT
        / "validation"
        / "v0.4.0"
        / "berlin"
        / args.candidate
        / "build-report.json"
    )
    if not report_path.is_file():
        raise SystemExit(f"missing build report: {report_path}")
    if args.output.exists():
        raise SystemExit(f"refusing destructive overwrite of {args.output}")

    build = json.loads(report_path.read_text())
    checks = []
    for mode in ("boundary_crop", "context_outline"):
        mode_report = build.get("modes", {}).get(mode, {})
        for half in ("left", "right"):
            half_report = mode_report.get("halves", {}).get(half, {})
            bridge = half_report.get("aperture_island_control", {})
            composite = half_report.get("composite", {})
            bone = half_report.get("colors", {}).get("bone-white", {})
            bone_regular = (
                bone.get("connected_components") == 1
                and bone.get("watertight") is True
                and bone.get("positive_volume") is True
                and bone.get("boundary_edges") == 0
                and bone.get("nonmanifold_edges") == 0
                and bone.get("degenerate_faces") == 0
                and bone.get("duplicate_faces") == 0
            )
            composite_regular = (
                composite.get("connected_components") == 1
                and composite.get("watertight") is True
                and composite.get("positive_volume") is True
                and composite.get("boundary_edges") == 0
                and composite.get("nonmanifold_edges") == 0
                and composite.get("degenerate_faces") == 0
                and composite.get("duplicate_faces") == 0
            )
            passed = (
                bridge.get("retained_raster_components") == 1
                and bone_regular
                and composite_regular
            )
            checks.append(
                {
                    "mode": mode,
                    "half": half,
                    "status": "PASS" if passed else "FAIL",
                    "aperture_bridge_count": bridge.get("bridge_count"),
                    "retained_raster_components": bridge.get(
                        "retained_raster_components"
                    ),
                    "bone_components": bone.get("connected_components"),
                    "bone_regular": bone_regular,
                    "composite_components": composite.get(
                        "connected_components"
                    ),
                    "composite_regular": composite_regular,
                }
            )
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    result = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "candidate": args.candidate,
        "status": status,
        "criterion": "every printed half remains one connected positive backer and one regular composite after light-through apertures",
        "checks": checks,
        "source_report": str(report_path.relative_to(PRODUCT)),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": status, "output": str(args.output)}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
