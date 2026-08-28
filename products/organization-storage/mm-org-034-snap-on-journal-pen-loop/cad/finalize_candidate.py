#!/usr/bin/env python3
"""Finalize MM-ORG-034 after the current approval chain reaches slicer preflight."""
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
    "validation/fdm-mesh-clip-s-final.json",
    "validation/fdm-mesh-clip-m-final.json",
    "validation/fdm-mesh-clip-l-final.json",
    "validation/fdm-mesh-tpu-insert-final.json",
    "validation/fdm-mesh-all-tpu-final.json",
    "validation/fdm-mesh-pen-gauge-final.json",
    "validation/fdm-3mf-petg-kit-final.json",
    "validation/fdm-3mf-tpu-kit-final.json",
    "validation/fdm-3mf-pen-gauge-final.json",
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
    preflight = loaded["validation/slicer-preflight-report.json"]
    jobs = preflight["metrics"]
    checks.extend([
        check("three-material-jobs", set(jobs) == {"tpu-gauge", "petg-kit", "tpu-kit"}, "Gauge and both material kits have exact slicer evidence"),
        check("warning-free", all(not item["metrics"].get("warning") for item in preflight["checks"] if item["id"].endswith(":native-warning")), "Final native slicer warning list is empty"),
        check("physical-deferred", True, "Cover and pen fit, surface marking, fatigue, snag/drop, and appearance remain human-controlled"),
    ])
    total_seconds = sum(job["estimate_seconds"] for job in jobs.values())
    total_mass = sum(job["density_conversion_g"] for job in jobs.values())
    report = {
        "schema_version": "1.0", "tool": "MM-ORG-034-finalize-digital-print-candidate", "tool_version": REVISION,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft",
        "inputs": [record(ROOT / path) for path in REPORT_PATHS], "checks": checks,
        "metrics": {
            "digital_print_candidate": True, "physical_validation": "DEFERRED", "commercial_release": "BLOCKED",
            "jobs": jobs, "all_three_jobs_estimate_seconds": total_seconds,
            "all_three_jobs_density_conversion_g": total_mass, "support_generation": "disabled_by_exact_process_profile",
        },
        "limitations": [
            "The 9–16 mm pen range and cover-gap labels are intended ranges, not qualified compatibility claims.",
            "Material hardness, brand, color, batch, drying, extrusion compensation, and cover finish can change fit and fatigue.",
            "The final slicer layer/seam/tool review and all physical tests remain human-controlled.",
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
