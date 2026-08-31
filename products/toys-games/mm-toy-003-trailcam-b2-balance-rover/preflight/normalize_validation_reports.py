#!/usr/bin/env python3
"""Bind specialist preflight reports to exact input hashes for fdm_ci."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()


def input_record(path: Path) -> dict:
    payload = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload)}


def normalize(report_path: Path, tool: str, input_paths: list[Path], limitation: str) -> None:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    passed = bool(report.get("passed")) and not report.get("errors")
    report.update({
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": "wrapper-1.0.0",
        "status": "PASS" if passed else "FAIL",
        "inputs": [input_record(path) for path in [SELF, *input_paths]],
        "checks": [{
            "id": "specialist-validation",
            "status": "PASS" if passed else "FAIL",
            "required": True,
            "message": "Specialist validator passed and this report is hash-bound to the declared inputs." if passed else "Specialist validator reported errors.",
            "evidence": [],
            "metrics": {},
        }],
        "limitations": [limitation],
    })
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    normalize(
        ROOT / "validation/preflight-validation-v0.1.0-bom.2.json",
        "3d-design-preflight+fdm-ci-wrapper",
        [ROOT / "preflight/preflight-result.json"],
        "Schema validity does not override the preflight HOLD decision or prove physical interfaces.",
    )
    normalize(
        ROOT / "validation/design-spec-preflight-validation-v0.1.0-bom.2.json",
        "functional-3d-design-preflight-link+fdm-ci-wrapper",
        [ROOT / "design-spec.yaml", ROOT / "preflight/preflight-result.json"],
        "Workflow-link validity does not approve manufacturing, powered testing or release.",
    )


if __name__ == "__main__":
    main()
