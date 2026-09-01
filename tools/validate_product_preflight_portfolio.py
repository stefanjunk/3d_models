#!/usr/bin/env python3
"""Validate portfolio-wide purpose, preflight, links, and archive evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_ROOT = REPO_ROOT / "products"
AUDIT_PATH = PRODUCTS_ROOT / "PRODUCT-PREFLIGHT-AUDIT-2026-08-31.json"

sys.path.insert(0, str(REPO_ROOT / ".agents/skills/3d-design-preflight/scripts"))
sys.path.insert(0, str(REPO_ROOT / "tools"))

from validate_preflight import validate_document  # noqa: E402
import backfill_product_preflights as backfill  # noqa: E402


def product_dirs() -> list[Path]:
    return sorted(
        product
        for family in PRODUCTS_ROOT.iterdir()
        if family.is_dir()
        for product in family.iterdir()
        if product.is_dir()
        and product.name.startswith(("mm-", "unregistered-"))
    )


def main() -> int:
    errors: list[str] = []
    products = product_dirs()

    try:
        audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        audit = {}
        errors.append(f"audit load failed: {exc}")

    if audit.get("product_count") != len(products):
        errors.append(f"audit product_count {audit.get('product_count')!r} != discovered {len(products)}")
    if audit.get("purpose_document_count") != len(products):
        errors.append("audit purpose count does not cover every product")
    if audit.get("preflight_document_count") != len(products):
        errors.append("audit preflight count does not cover every product")
    if audit.get("archive_verification_errors"):
        errors.append(f"audit records archive errors: {audit['archive_verification_errors']}")

    audit_entries = {entry.get("product"): entry for entry in audit.get("products", [])}
    for product in products:
        key = product.relative_to(PRODUCTS_ROOT).as_posix()
        purpose_path = product / "PURPOSE.md"
        result_path = product / "preflight/preflight-result.json"
        input_path = product / "preflight/preflight-input.yaml"
        report_path = product / "preflight/preflight-report.md"
        spec_path = product / "design-spec.yaml"

        if not purpose_path.exists():
            errors.append(f"{key}: PURPOSE.md missing")
        else:
            purpose = purpose_path.read_text(encoding="utf-8")
            if not purpose.startswith("# Purpose — ") or "TODO" in purpose:
                errors.append(f"{key}: purpose is not explicit or still contains TODO")

        for path in (result_path, input_path, report_path, spec_path):
            if not path.exists():
                errors.append(f"{key}: missing {path.relative_to(product)}")
        if not result_path.exists() or not spec_path.exists():
            continue

        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{key}: invalid preflight JSON: {exc}")
            continue
        schema_errors, _ = validate_document(
            result,
            expected_project_id=result.get("traceability", {}).get("project_id"),
            expected_project_revision=result.get("traceability", {}).get("project_revision"),
        )
        errors.extend(f"{key}: {error}" for error in schema_errors)
        trace = result.get("traceability", {})
        mode = trace.get("mode")
        if mode not in {"RETROSPECTIVE", "PROSPECTIVE"}:
            errors.append(f"{key}: unsupported preflight mode {mode!r}")
        if mode == "RETROSPECTIVE" and "backfill_missing_preflight" not in trace.get("change_triggers", []):
            errors.append(f"{key}: missing retrospective backfill traceability")
        if not trace.get("basis_refs"):
            errors.append(f"{key}: no preflight basis refs")

        try:
            spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{key}: invalid design-spec YAML: {exc}")
            continue
        linked = (spec.get("workflow") or {}).get("preflight") if isinstance(spec, dict) else None
        if not isinstance(linked, dict):
            errors.append(f"{key}: workflow.preflight link missing")
        else:
            expected = {
                "status": "current",
                "mode": mode,
                "artifact": "preflight/preflight-result.json",
                "assessment_id": result.get("assessment_id"),
                "assessment_version": result.get("assessment_version"),
                "assessed_project_revision": trace.get("project_revision"),
            }
            for field, value in expected.items():
                if linked.get(field) != value:
                    errors.append(f"{key}: workflow.preflight.{field} mismatch")

        entry = audit_entries.get(key)
        if entry is None:
            errors.append(f"{key}: absent from portfolio audit")
        else:
            expected_scorecard = {
                "complexity": result.get("complexity", {}).get("class"),
                "score_0_100": result.get("complexity", {}).get("score_0_100"),
                "readiness": result.get("readiness", {}).get("level"),
                "criticality": result.get("criticality", {}).get("level"),
                "lane": result.get("decision", {}).get("lane"),
                "confidence": result.get("decision", {}).get("confidence"),
                "release": result.get("decision", {}).get("design_release"),
            }
            if entry.get("scorecard") != expected_scorecard:
                errors.append(f"{key}: aggregate audit scorecard is stale")
            if entry.get("project_id") != trace.get("project_id") or str(entry.get("revision")) != str(trace.get("project_revision")):
                errors.append(f"{key}: aggregate audit identity/revision is stale")
            if key in backfill.ROOT_REVIEW_EXCEPTIONS and entry.get("archive", {}).get("root_status") != "REVIEW_REQUIRED":
                errors.append(f"{key}: dirty/ambiguous root exception not preserved")

    errors.extend(backfill.verify_archive_moves())
    for key in backfill.ARCHIVE_MOVES:
        readme = PRODUCTS_ROOT / key / "archive/README.md"
        if not readme.exists():
            errors.append(f"{key}: archive/README.md missing")

    dry_run = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/backfill_product_preflights.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if dry_run.returncode != 0:
        errors.append(f"backfill dry-run failed: {dry_run.stderr or dry_run.stdout}")
    else:
        try:
            dry_report = json.loads(dry_run.stdout)
            if dry_report.get("changed_files") != 0:
                errors.append(f"backfill is not idempotent: {dry_report.get('changed_files')} files would change")
        except json.JSONDecodeError as exc:
            errors.append(f"backfill dry-run output invalid: {exc}")

    report = {
        "validator": "product-preflight-portfolio",
        "products": len(products),
        "purpose_documents": sum((product / "PURPOSE.md").exists() for product in products),
        "preflight_results": sum((product / "preflight/preflight-result.json").exists() for product in products),
        "archive_moves_verified": sum(len(items) for items in backfill.ARCHIVE_MOVES.values()),
        "documented_root_exceptions": len(backfill.ROOT_REVIEW_EXCEPTIONS),
        "errors": errors,
        "passed": not errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
