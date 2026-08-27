#!/usr/bin/env python3
"""Create a fail-closed digital print-candidate report from retained evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "validation/print-candidate-report.json"
REPORTS = [
    ROOT / "validation/parametric-source-report.json",
    ROOT / "validation/mesh-generation-report.json",
    ROOT / "validation/interface-report.json",
    ROOT / "validation/fdm-mesh-caddy.json",
    ROOT / "validation/fdm-mesh-nameplate.json",
    ROOT / "validation/fdm-mesh-coupon-holder.json",
    ROOT / "validation/fdm-mesh-coupon-plate.json",
    ROOT / "validation/fdm-3mf.json",
    ROOT / "validation/slicer-preflight-anycubic-kobra3max-pla.json",
    ROOT / "validation/approvals-through-slicer.json",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    evidence = []
    checks = []
    for path in REPORTS:
        if not path.is_file():
            checks.append(
                {
                    "id": f"evidence:{path.stem}",
                    "status": "FAIL",
                    "required": True,
                    "message": "Required report is missing",
                    "metrics": {"path": str(path.relative_to(ROOT))},
                    "evidence": [],
                }
            )
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        passed = data.get("status") == "PASS" or data.get("passed") is True
        evidence.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": digest(path),
                "size_bytes": path.stat().st_size,
                "reported_status": data.get("status", data.get("passed")),
            }
        )
        checks.append(
            {
                "id": f"evidence:{path.stem}",
                "status": "PASS" if passed else "FAIL",
                "required": True,
                "message": "Required report passes" if passed else "Required report does not pass",
                "metrics": {"path": str(path.relative_to(ROOT))},
                "evidence": [],
            }
        )
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    payload = {
        "schema_version": "1.0",
        "tool": "MM-ORG-010-print-candidate-finalizer",
        "tool_version": "0.1.0-draft.1",
        "status": status,
        "profile": "draft",
        "inputs": evidence,
        "checks": checks,
        "metrics": {
            "digital_print_candidate": status == "PASS",
            "physical_validation": "DEFERRED",
            "watermark": "NOT_INTEGRATED_RELEASE_BLOCKER",
            "commercial_release": "BLOCKED",
        },
        "limitations": [
            "A passing digital candidate does not prove physical fit, stability, edge comfort, material behavior or appearance.",
            "The retained slicer result uses a workspace Kobra 3 Max / Anycubic PLA reference profile.",
            "No printer upload or print-start action is authorized or performed.",
        ],
        "required_capabilities": [],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "output": str(OUTPUT)}, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
