#!/usr/bin/env python3
"""Gate externally measured reference/candidate mesh simplification metrics."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


REQUIRED_MESH = ("faces", "body_count", "watertight", "winding_consistent", "volume_mm3")
REQUIRED_COMPARISON = ("max_surface_error_mm", "rms_surface_error_mm", "max_protected_error_mm")
REQUIRED_LIMITS = (
    "max_surface_error_mm",
    "max_rms_surface_error_mm",
    "max_protected_error_mm",
    "max_abs_volume_delta_pct",
    "min_triangle_reduction_pct",
)
RELIEF_STARTING_LIMITS = {
    "min_relief_correlation": 0.98,
    "max_relief_contrast_loss_pct": 5.0,
    "max_rms_nozzle_fraction": 0.05,
}


def finite_number(value: Any, name: str, *, nonnegative: bool = True) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{name} must be a finite number")
    parsed = float(value)
    if nonnegative and parsed < 0:
        raise ValueError(f"{name} cannot be negative")
    return parsed


def require_fields(obj: dict[str, Any], fields: tuple[str, ...], prefix: str) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        raise ValueError(f"{prefix} missing fields: {', '.join(missing)}")


def pct_change(reference: float, candidate: float) -> float:
    if reference == 0:
        return 0.0 if candidate == 0 else math.inf
    return 100.0 * (candidate - reference) / abs(reference)


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    for field in ("reference", "candidate", "comparison", "limits"):
        if not isinstance(data.get(field), dict):
            raise ValueError(f"{field} must be an object")
    reference = data["reference"]
    candidate = data["candidate"]
    comparison = data["comparison"]
    limits = dict(data["limits"])
    require_fields(reference, REQUIRED_MESH, "reference")
    require_fields(candidate, REQUIRED_MESH, "candidate")
    require_fields(comparison, REQUIRED_COMPARISON, "comparison")
    require_fields(limits, REQUIRED_LIMITS, "limits")

    ref_faces = int(finite_number(reference["faces"], "reference.faces"))
    cand_faces = int(finite_number(candidate["faces"], "candidate.faces"))
    if ref_faces <= 0 or cand_faces <= 0:
        raise ValueError("reference.faces and candidate.faces must be positive")
    ref_volume = finite_number(reference["volume_mm3"], "reference.volume_mm3")
    cand_volume = finite_number(candidate["volume_mm3"], "candidate.volume_mm3")
    if ref_volume <= 0 or cand_volume <= 0:
        raise ValueError("reference and candidate volumes must be positive")

    reduction_pct = 100.0 * (ref_faces - cand_faces) / ref_faces
    volume_delta_pct = pct_change(ref_volume, cand_volume)
    max_error = finite_number(comparison["max_surface_error_mm"], "comparison.max_surface_error_mm")
    rms_error = finite_number(comparison["rms_surface_error_mm"], "comparison.rms_surface_error_mm")
    protected_error = finite_number(comparison["max_protected_error_mm"], "comparison.max_protected_error_mm")

    checks: dict[str, dict[str, Any]] = {}

    def add(name: str, actual: Any, limit: Any, passed: bool) -> None:
        checks[name] = {"actual": actual, "limit": limit, "passed": bool(passed)}

    add("triangle_reduction", reduction_pct, {">=": limits["min_triangle_reduction_pct"]}, reduction_pct >= float(limits["min_triangle_reduction_pct"]))
    add("body_count", candidate["body_count"], {"==": reference["body_count"]}, candidate["body_count"] == reference["body_count"])
    add("watertight", candidate["watertight"], {"==": True}, candidate["watertight"] is True)
    add("winding_consistent", candidate["winding_consistent"], {"==": True}, candidate["winding_consistent"] is True)
    add("max_surface_error_mm", max_error, {"<=": limits["max_surface_error_mm"]}, max_error <= float(limits["max_surface_error_mm"]))
    rms_limit = float(limits["max_rms_surface_error_mm"])
    relief_validation = data.get("relief_validation") is True
    if relief_validation:
        process = data.get("process")
        if not isinstance(process, dict):
            raise ValueError("process must be an object when relief_validation=true")
        nozzle = finite_number(process.get("nozzle_mm"), "process.nozzle_mm")
        if nozzle <= 0:
            raise ValueError("process.nozzle_mm must be positive")
        for name, default in RELIEF_STARTING_LIMITS.items():
            limits.setdefault(name, default)
        rms_nozzle_limit = nozzle * finite_number(
            limits["max_rms_nozzle_fraction"], "limits.max_rms_nozzle_fraction"
        )
        rms_limit = min(rms_limit, rms_nozzle_limit)
    add("rms_surface_error_mm", rms_error, {"<=": rms_limit}, rms_error <= rms_limit)
    add("max_protected_error_mm", protected_error, {"<=": limits["max_protected_error_mm"]}, protected_error <= float(limits["max_protected_error_mm"]))
    add("abs_volume_delta_pct", abs(volume_delta_pct), {"<": limits["max_abs_volume_delta_pct"]}, abs(volume_delta_pct) < float(limits["max_abs_volume_delta_pct"]))

    optional_pairs = [
        ("bed_contact_area_mm2", "max_bed_contact_loss_pct", "bed_contact_loss_pct"),
        ("relief_span_mm", "max_relief_amplitude_loss_pct", "relief_amplitude_loss_pct"),
    ]
    for metric, limit_name, check_name in optional_pairs:
        if metric in reference or metric in candidate or limit_name in limits:
            if metric not in reference or metric not in candidate or limit_name not in limits:
                raise ValueError(f"{metric} and {limit_name} must be supplied together")
            ref = finite_number(reference[metric], f"reference.{metric}")
            cand = finite_number(candidate[metric], f"candidate.{metric}")
            loss_pct = -pct_change(ref, cand)
            add(check_name, loss_pct, {"<=": limits[limit_name]}, loss_pct <= float(limits[limit_name]))

    if relief_validation:
        correlation = finite_number(
            comparison.get("relief_correlation"),
            "comparison.relief_correlation",
            nonnegative=False,
        )
        contrast_loss = finite_number(
            comparison.get("relief_contrast_loss_pct"), "comparison.relief_contrast_loss_pct"
        )
        if correlation < -1 or correlation > 1:
            raise ValueError("comparison.relief_correlation must be in [-1, 1]")
        add(
            "relief_correlation",
            correlation,
            {">=": limits["min_relief_correlation"]},
            correlation >= float(limits["min_relief_correlation"]),
        )
        add(
            "relief_contrast_loss_pct",
            contrast_loss,
            {"<": limits["max_relief_contrast_loss_pct"]},
            contrast_loss < float(limits["max_relief_contrast_loss_pct"]),
        )

    passed = all(check["passed"] for check in checks.values())
    return {
        "passed": passed,
        "decision": "ACCEPT_CANDIDATE" if passed else "REJECT_CANDIDATE",
        "metrics": {
            "triangle_reduction_pct": reduction_pct,
            "volume_delta_pct": volume_delta_pct,
            "effective_rms_limit_mm": rms_limit,
        },
        "applied_limits": limits,
        "checks": checks,
        "limitations": [
            "Input surface-error, protected-region, bed-contact, and relief metrics must be measured independently.",
            "A passing report does not replace exact-slicer inspection or application-specific physical tests.",
            "Relief correlation/contrast must use registered paired heights inside the actual relief mask, excluding unrelated flat background.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-reject", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = evaluate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(encoded, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    return 2 if args.fail_on_reject and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
