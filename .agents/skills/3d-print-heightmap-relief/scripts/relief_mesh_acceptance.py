#!/usr/bin/env python3
"""Gate externally measured relief reference/manufacturing mesh metrics."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


STARTING_LIMITS = {
    "max_abs_volume_delta_pct": 0.1,
    "min_relief_correlation": 0.98,
    "max_relief_contrast_loss_pct": 5.0,
    "max_rms_nozzle_fraction": 0.05,
}


def number(value: Any, name: str, *, positive: bool = False) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{name} must be a finite number")
    parsed = float(value)
    if positive and parsed <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return parsed


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    for field in ("process", "reference", "candidate", "comparison"):
        if not isinstance(data.get(field), dict):
            raise ValueError(f"{field} must be an object")
    process = data["process"]
    reference = data["reference"]
    candidate = data["candidate"]
    comparison = data["comparison"]
    limits = {**STARTING_LIMITS, **data.get("limits", {})}

    nozzle = number(process.get("nozzle_mm"), "process.nozzle_mm", positive=True)
    ref_volume = number(reference.get("volume_mm3"), "reference.volume_mm3", positive=True)
    cand_volume = number(candidate.get("volume_mm3"), "candidate.volume_mm3", positive=True)
    rms = number(comparison.get("rms_surface_error_mm"), "comparison.rms_surface_error_mm")
    correlation = number(comparison.get("relief_correlation"), "comparison.relief_correlation")
    contrast_loss = number(comparison.get("relief_contrast_loss_pct"), "comparison.relief_contrast_loss_pct")
    if rms < 0 or contrast_loss < 0 or not -1 <= correlation <= 1:
        raise ValueError("RMS/contrast loss cannot be negative and correlation must be in [-1, 1]")

    volume_delta_pct = 100.0 * (cand_volume - ref_volume) / ref_volume
    rms_limit_mm = nozzle * number(limits["max_rms_nozzle_fraction"], "limits.max_rms_nozzle_fraction", positive=True)
    checks = {
        "abs_volume_delta_pct": {
            "actual": abs(volume_delta_pct),
            "limit": {"<": limits["max_abs_volume_delta_pct"]},
            "passed": abs(volume_delta_pct) < float(limits["max_abs_volume_delta_pct"]),
        },
        "relief_correlation": {
            "actual": correlation,
            "limit": {">=": limits["min_relief_correlation"]},
            "passed": correlation >= float(limits["min_relief_correlation"]),
        },
        "relief_contrast_loss_pct": {
            "actual": contrast_loss,
            "limit": {"<": limits["max_relief_contrast_loss_pct"]},
            "passed": contrast_loss < float(limits["max_relief_contrast_loss_pct"]),
        },
        "rms_surface_error_mm": {
            "actual": rms,
            "limit": {"<=": rms_limit_mm, "nozzle_fraction": limits["max_rms_nozzle_fraction"]},
            "passed": rms <= rms_limit_mm,
        },
    }

    for boolean_field in ("watertight", "winding_consistent"):
        if boolean_field in candidate:
            checks[boolean_field] = {
                "actual": candidate[boolean_field],
                "limit": {"==": True},
                "passed": candidate[boolean_field] is True,
            }
    if "body_count" in reference or "body_count" in candidate:
        checks["body_count"] = {
            "actual": candidate.get("body_count"),
            "limit": {"==": reference.get("body_count")},
            "passed": candidate.get("body_count") == reference.get("body_count"),
        }

    passed = all(item["passed"] for item in checks.values())
    return {
        "passed": passed,
        "decision": "ACCEPT_MANUFACTURING_MESH" if passed else "REJECT_MANUFACTURING_MESH",
        "limits": limits,
        "metrics": {"volume_delta_pct": volume_delta_pct, "rms_limit_mm": rms_limit_mm},
        "checks": checks,
        "measurement_contract": {
            "registration": "Compare aligned meshes in the same physical surface coordinates.",
            "relief_mask": "Use the actual relief mask; exclude unrelated flat background.",
            "correlation": "Pearson correlation of paired reference/candidate relief heights after mean removal.",
            "contrast": "Percent loss of the same robust height span (recommended P95-P5) in reference and candidate.",
        },
        "limitations": [
            "The script gates supplied measurements; it does not sample or register meshes.",
            "Exact-slicer inspection and a process-matched coupon remain separate release checks.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-reject", action="store_true")
    args = parser.parse_args()
    try:
        report = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
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
