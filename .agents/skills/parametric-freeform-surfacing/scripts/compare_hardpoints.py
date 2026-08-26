#!/usr/bin/env python3
"""Compare named hardpoint points, axes, and planes before/after freeform operations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from surface_geometry import write_json


def named(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    result = {}
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            result[item["name"]] = item
    return result


def vector(value: Any, label: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != (3,) or not np.isfinite(array).all():
        raise ValueError(f"{label} must be a finite 3-vector")
    return array


def angle_deg(a: np.ndarray, b: np.ndarray, undirected: bool = False) -> float:
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    dot = float(np.clip(np.dot(a, b), -1.0, 1.0))
    if undirected:
        dot = abs(dot)
    return float(np.degrees(np.arccos(dot)))


def compare(baseline: dict[str, Any], current: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    records = []
    success = True

    for kind in ("points", "axes", "planes"):
        before = named(baseline.get(kind, []))
        after = named(current.get(kind, []))
        for missing in sorted(set(before) - set(after)):
            records.append({"kind": kind[:-1], "name": missing, "status": "MISSING_CURRENT"})
            success = False
        for extra in sorted(set(after) - set(before)):
            records.append({"kind": kind[:-1], "name": extra, "status": "EXTRA_CURRENT"})
            success = False
        for name in sorted(set(before) & set(after)):
            b, c = before[name], after[name]
            if kind == "points":
                bp = vector(b.get("position"), f"points.{name}.position")
                cp = vector(c.get("position"), f"points.{name}.position")
                drift = float(np.linalg.norm(cp - bp))
                passed = drift <= args.point_tol
                record = {"kind": "point", "name": name, "drift_mm": drift, "tolerance_mm": args.point_tol, "status": "PASS" if passed else "FAIL"}
            elif kind == "axes":
                bs, be = vector(b.get("start"), f"axes.{name}.start"), vector(b.get("end"), f"axes.{name}.end")
                cs, ce = vector(c.get("start"), f"axes.{name}.start"), vector(c.get("end"), f"axes.{name}.end")
                bdir, cdir = be - bs, ce - cs
                if np.linalg.norm(bdir) <= 1e-12 or np.linalg.norm(cdir) <= 1e-12:
                    raise ValueError(f"Axis {name} has zero length")
                position_drift = float(np.linalg.norm((cs + ce) / 2.0 - (bs + be) / 2.0))
                angular_drift = angle_deg(bdir, cdir, undirected=True)
                length_drift = abs(float(np.linalg.norm(cdir) - np.linalg.norm(bdir)))
                passed = position_drift <= args.axis_pos_tol and angular_drift <= args.axis_angle_tol and length_drift <= args.axis_length_tol
                record = {
                    "kind": "axis", "name": name,
                    "midpoint_drift_mm": position_drift, "midpoint_tolerance_mm": args.axis_pos_tol,
                    "angular_drift_deg": angular_drift, "angular_tolerance_deg": args.axis_angle_tol,
                    "length_drift_mm": length_drift, "length_tolerance_mm": args.axis_length_tol,
                    "status": "PASS" if passed else "FAIL",
                }
            else:
                bo, co = vector(b.get("origin"), f"planes.{name}.origin"), vector(c.get("origin"), f"planes.{name}.origin")
                bn, cn = vector(b.get("normal"), f"planes.{name}.normal"), vector(c.get("normal"), f"planes.{name}.normal")
                if np.linalg.norm(bn) <= 1e-12 or np.linalg.norm(cn) <= 1e-12:
                    raise ValueError(f"Plane {name} has zero normal")
                angular_drift = angle_deg(bn, cn, undirected=True)
                offset = abs(float(np.dot(co - bo, bn / np.linalg.norm(bn))))
                passed = offset <= args.plane_offset_tol and angular_drift <= args.plane_angle_tol
                record = {
                    "kind": "plane", "name": name,
                    "normal_offset_mm": offset, "offset_tolerance_mm": args.plane_offset_tol,
                    "angular_drift_deg": angular_drift, "angular_tolerance_deg": args.plane_angle_tol,
                    "status": "PASS" if passed else "FAIL",
                }
            records.append(record)
            success = success and passed

    return {"success": success, "records": records}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare named hardpoints before and after FFD/SubD/SDF/smoothing.")
    parser.add_argument("baseline", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("--point-tol", type=float, default=0.10)
    parser.add_argument("--axis-pos-tol", type=float, default=0.10)
    parser.add_argument("--axis-angle-tol", type=float, default=0.10)
    parser.add_argument("--axis-length-tol", type=float, default=0.10)
    parser.add_argument("--plane-offset-tol", type=float, default=0.10)
    parser.add_argument("--plane-angle-tol", type=float, default=0.10)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    result = compare(baseline, current, args)
    report = {"baseline": str(args.baseline), "current": str(args.current), **result}
    if args.report:
        write_json(args.report, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
