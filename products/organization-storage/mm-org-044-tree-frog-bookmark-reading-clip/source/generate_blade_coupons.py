#!/usr/bin/env python3
"""Generate an exact-process page-blade thickness coupon series; not a product release."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import cadquery as cq
from cadquery import exporters


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def token(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", "p")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parameters", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    parameter_path = args.parameters.resolve()
    params = json.loads(parameter_path.read_text(encoding="utf-8"))
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []

    blade_length = float(params["blade_length_mm"])
    blade_width = float(params["blade_width_mm"])
    root_length = float(params["root_length_mm"])
    root_width = float(params["root_width_mm"])
    root_thickness = float(params["root_thickness_mm"])
    corner_radius = float(params["blade_corner_radius_mm"])
    blade_center_y = blade_length / 2.0
    root_center_y = -root_length / 2.0 + 0.5

    for thickness_value in params["blade_thickness_series_mm"]:
        thickness = float(thickness_value)
        blade = (
            cq.Workplane("XY")
            .box(blade_width, blade_length, thickness, centered=(True, True, False))
            .translate((0.0, blade_center_y, 0.0))
            .edges("|Z")
            .fillet(corner_radius)
        )
        root = (
            cq.Workplane("XY")
            .box(root_width, root_length, root_thickness, centered=(True, True, False))
            .translate((0.0, root_center_y, 0.0))
        )
        coupon = root.union(blade)
        stem = f"blade-coupon-{token(thickness)}mm"
        step_path = output_dir / f"{stem}.step"
        stl_path = output_dir / f"{stem}.stl"
        exporters.export(coupon, str(step_path))
        exporters.export(coupon, str(stl_path), tolerance=0.02, angularTolerance=0.1)
        outputs.append({
            "thickness_mm": thickness,
            "step": {"path": str(step_path), "sha256": sha256(step_path), "bytes": step_path.stat().st_size},
            "stl": {"path": str(stl_path), "sha256": sha256(stl_path), "bytes": stl_path.stat().st_size},
        })

    report = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "UNQUALIFIED_COUPON_SERIES",
        "parameters": {"path": str(parameter_path), "sha256": sha256(parameter_path), "values": params},
        "outputs": outputs,
        "release_blockers": ["no coupon has been printed", "paper samples are not declared", "no page-marking result", "no permanent-set or 100-cycle result"],
    }
    report_path = output_dir / "blade-coupon-series-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
