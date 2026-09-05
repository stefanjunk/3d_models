#!/usr/bin/env python3
"""Revalidate every portfolio P2 package and write a compact portfolio audit."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

BUSINESS = Path(__file__).resolve().parents[1]
WORKSPACE = BUSINESS.parent
PORTFOLIO = BUSINESS / "02-portfolio" / "product-portfolio.csv"
PLAN = BUSINESS / "02-portfolio" / "p2-stage-source-plan.json"
DEFAULT_JSON = BUSINESS / "02-portfolio" / "p2-stage-audit.json"
DEFAULT_MARKDOWN = BUSINESS / "02-portfolio" / "p2-stage-audit.md"
FDM_CLI = WORKSPACE / ".agents/skills/validate-printable-3d-projects/scripts/fdm_ci.py"


def relative(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE.resolve()).as_posix()


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("manifest root is not an object")
    return value


def validate_manifest(path: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-B", str(FDM_CLI), "validate-p2-stage", str(path)],
        cwd=WORKSPACE,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        report = json.loads(completed.stdout)
    except Exception as exc:
        return {
            "status": "FAIL",
            "checks": [],
            "metrics": {},
            "error": f"validator output is not JSON: {type(exc).__name__}: {exc}; stderr={completed.stderr}",
        }
    if completed.returncode != 0 and report.get("status") != "FAIL":
        report["status"] = "FAIL"
        report["error"] = f"validator exited {completed.returncode}: {completed.stderr}"
    return report


def artifact_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    artifacts = manifest.get("artifacts", {})
    print_set = artifacts.get("print_set_3mf", {})
    return {
        "description_en": artifacts.get("description_en", {}).get("path"),
        "concept_image": artifacts.get("concept_image", {}).get("path"),
        "concept_approval_state": artifacts.get("concept_image", {}).get(
            "approval_state"
        ),
        "rendered_image": artifacts.get("rendered_image", {}).get("path"),
        "print_set_3mf": print_set.get("path"),
        "declared_print_objects": sum(
            item.get("quantity", 0)
            for item in print_set.get("print_parts", [])
            if isinstance(item, dict) and isinstance(item.get("quantity"), int)
        ),
        "orientation": print_set.get("orientation", {}).get("status"),
        "support_mode": print_set.get("supports", {}).get("mode"),
    }


def run_audit() -> dict[str, Any]:
    with PORTFOLIO.open(newline="", encoding="utf-8") as handle:
        portfolio = list(csv.DictReader(handle))
    p2_rows = [row for row in portfolio if row["Lifecycle_Stage"].startswith("P2")]
    results: list[dict[str, Any]] = []
    for order, row in enumerate(p2_rows, 1):
        root = WORKSPACE / row["Source_Path"]
        manifest_path = root / "p2-stage" / "p2-manifest.json"
        item: dict[str, Any] = {
            "order": order,
            "record_id": row["Record_ID"],
            "sku": row["Working_SKU"],
            "name": row["Product_or_Model"],
            "lifecycle_stage": row["Lifecycle_Stage"],
            "manifest": relative(manifest_path),
        }
        if not manifest_path.is_file():
            item.update({"status": "FAIL", "error": "P2 manifest is missing"})
            results.append(item)
            continue
        try:
            manifest = load_manifest(manifest_path)
            item.update(artifact_summary(manifest))
            identity = manifest.get("product", {})
            if (
                identity.get("record_id") != row["Record_ID"]
                or identity.get("sku") != row["Working_SKU"]
            ):
                item.update(
                    {
                        "status": "FAIL",
                        "error": "portfolio and manifest identity differ",
                    }
                )
                results.append(item)
                continue
            report = validate_manifest(manifest_path)
            item["status"] = report.get("status", "FAIL")
            item["failed_checks"] = [
                check.get("id")
                for check in report.get("checks", [])
                if check.get("status") == "FAIL"
            ]
            if report.get("error"):
                item["error"] = report["error"]
        except Exception as exc:
            item.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
        results.append(item)

    demotions = []
    if PLAN.is_file():
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        demotions = [
            {
                "order": item["order"],
                "record_id": item["record_id"],
                "sku": item["sku"],
                "name": item["name"],
                "from_stage": item["lifecycle_stage"],
                "to_stage": next(
                    (
                        row["Lifecycle_Stage"]
                        for row in portfolio
                        if row["Record_ID"] == item["record_id"]
                    ),
                    None,
                ),
                "reason": item["reason"],
            }
            for item in plan.get("products", [])
            if item.get("action") == "demote"
        ]

    counts = Counter(item["status"] for item in results)
    return {
        "schema_version": "1.0",
        "as_of": "2026-09-05",
        "portfolio": relative(PORTFOLIO),
        "status": "PASS" if results and counts.get("PASS") == len(results) else "FAIL",
        "summary": {
            "portfolio_p2_products": len(p2_rows),
            "passed": counts.get("PASS", 0),
            "failed": counts.get("FAIL", 0),
            "retrospective_concepts": sum(
                item.get("concept_approval_state") == "retrospective-unapproved"
                for item in results
            ),
            "demoted_during_remediation": len(demotions),
        },
        "products": results,
        "demotions": demotions,
        "limitations": [
            "P2 is a digital-candidate gate; this audit does not prove physical fit, finish, strength, safety, rights clearance or commercial readiness.",
            "A complete-object declaration is revision-specific and remains subject to product-owner review when product scope changes.",
        ],
    }


def write_markdown(path: Path, audit: dict[str, Any]) -> None:
    summary = audit["summary"]
    lines = [
        "# P2 stage artifact audit",
        "",
        f"Status: **{audit['status']}** · {summary['passed']}/{summary['portfolio_p2_products']} portfolio P2 products pass · {summary['failed']} fail.",
        "",
        "Every passing row has a hash-bound English product description, whole-product concept image, current-model render, and complete revision-specific 3MF with an explicit orientation and support decision.",
        "",
        "| # | SKU | Status | Objects | Concept state | Support | Manifest |",
        "|---:|---|---|---:|---|---|---|",
    ]
    for item in audit["products"]:
        lines.append(
            f"| {item['order']} | `{item['sku']}` | {item['status']} | {item.get('declared_print_objects', '—')} | "
            f"{item.get('concept_approval_state', '—')} | {item.get('support_mode', '—')} | `{item['manifest']}` |"
        )
    lines.extend(["", "## P2 corrections", ""])
    for item in audit["demotions"]:
        lines.append(
            f"- `{item['sku']}`: `{item['from_stage']}` → `{item['to_stage']}` — {item['reason']}"
        )
    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {item}" for item in audit["limitations"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    audit = run_audit()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_markdown(args.markdown_out, audit)
    print(json.dumps({"status": audit["status"], **audit["summary"]}, indent=2))
    return 0 if audit["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
