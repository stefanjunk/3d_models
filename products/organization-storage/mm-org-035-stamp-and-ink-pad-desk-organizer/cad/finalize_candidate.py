#!/usr/bin/env python3
"""Finalize MM-ORG-035 after the current chain reaches slicer preflight."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.2"
REPORT_PATHS = [
    "validation/parametric-source-report.json",
    "validation/mesh-generation-report.json",
    "validation/interface-report.json",
    "reports/optimization-comparison.json",
    "validation/fdm-mesh-square-final.json",
    "validation/fdm-mesh-rectangular-final.json",
    "validation/fdm-mesh-square-coupon-final.json",
    "validation/fdm-mesh-rectangular-coupon-final.json",
    "validation/fdm-3mf-full-final.json",
    "validation/fdm-3mf-coupons-final.json",
    "validation/slicer-preflight-report.json",
    "validation/current-approvals-through-slicer.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def main() -> None:
    loaded = {path: json.loads((ROOT / path).read_text()) for path in REPORT_PATHS}
    checks = [check(f"report:{path}", report["status"] == "PASS", f"{path} reports PASS") for path, report in loaded.items()]
    jobs = loaded["validation/slicer-preflight-report.json"]["metrics"]
    checks.extend([
        check("coupon-and-full-jobs", set(jobs) == {"fit-coupons", "full-duo"}, "Coupon and complete product plates have exact slicer evidence"),
        check("warning-free", all(not item["metrics"].get("warnings") for item in loaded["validation/slicer-preflight-report.json"]["checks"] if item["id"].endswith(":native-warning")), "Final native slicer warning lists are empty"),
        check("physical-deferred", True, "Case fit, label view, removal, stability, cycles, staining, cleaning, and appearance remain human-controlled"),
    ])
    report = {
        "schema_version": "1.0", "tool": "MM-ORG-035-finalize-digital-print-candidate", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": [record(ROOT / path) for path in REPORT_PATHS], "checks": checks,
        "metrics": {
            "digital_print_candidate": True,
            "physical_validation": "DEFERRED",
            "commercial_release": "BLOCKED",
            "jobs": jobs,
            "both_jobs_estimate_seconds": sum(job["estimate_seconds"] for job in jobs.values()),
            "both_jobs_density_conversion_g": sum(job["density_conversion_g"] for job in jobs.values()),
            "support_generation": "disabled_by_exact_process_profile",
        },
        "limitations": [
            "The two case envelopes are maximum intended ranges, not universal brand-compatibility claims.",
            "Printer flow error and undocumented case variation can change fit.",
            "Use replaceable scrap paper on the stamp-rest tray; no wet-ink or chemical compatibility is claimed.",
            "The final slicer layer, seam, support, and bed-placement review and all physical tests remain human-controlled.",
            "No printer upload or print-start action was performed.",
        ],
        "required_capabilities": [],
    }
    target = ROOT / "validation/print-candidate-report.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "metrics": report["metrics"]}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
