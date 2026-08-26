#!/usr/bin/env python3
"""Fail-closed evidence audit for a commercial 3D model release.

Exit codes:
  0 = PASS
  1 = WARN
  2 = BLOCK
  3 = invalid invocation or unreadable project
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


YES = {"yes", "pass", "passed", "cleared", "approved", "true"}
NO = {"no", "false", "block", "blocked", "failed"}
NA = {"not_applicable", "not applicable", "n/a", "na"}
DECIDED = YES | NO | NA | {"warn", "warning"}
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
SUM_LINE_RE = re.compile(r"^([0-9a-fA-F]{64})  (.+)$")
PLACEHOLDER_RE = re.compile(
    r"\[(?:REPLACE|DETAIL|DATE|NAME|COUNSEL|PRODUCT|PROJECT|RELEASE|"
    r"LEGAL|SELLER|SOURCE|ARTIFACT|ITEM|MARKET|FILE|HASH|ROLE|CLASS|"
    r"STANDARD|ROUTE|METHOD|HAZARD|TEXT|PATH|LIST|AMOUNT|ID|VERSION|"
    r"TERRITORY|TERM|NUMBER|QUANTITY|CHANNEL|CONTACT|COUNTRY|OWNER|"
    r"YES/NO|PASS/WARN/BLOCK)[^\]]*\]",
    re.IGNORECASE,
)


@dataclass
class Finding:
    severity: str
    code: str
    message: str


class Audit:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.findings: list[Finding] = []

    def add(self, severity: str, code: str, message: str) -> None:
        self.findings.append(Finding(severity, code, message))

    def block(self, code: str, message: str) -> None:
        self.add("BLOCK", code, message)

    def warn(self, code: str, message: str) -> None:
        self.add("WARN", code, message)

    def pass_note(self, code: str, message: str) -> None:
        self.add("PASS", code, message)

    def path(self, relative: str, code: str, label: str) -> Path | None:
        if not clean(relative):
            self.block(code, f"{label} is missing or unresolved")
            return None
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            self.block(code, f"{label} escapes project root: {relative}")
            return None
        if not candidate.exists():
            self.block(code, f"{label} does not exist: {relative}")
            return None
        return candidate

    def evidence(self, value: str, code: str, label: str) -> None:
        if not clean(value):
            self.block(code, f"{label} evidence path is missing or unresolved")
            return
        if "://" in value or value.startswith("evidence:"):
            self.warn(code, f"{label} uses external evidence that this audit cannot hash: {value}")
            return
        self.path(value, code, f"{label} evidence")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit rights, provenance, product, and approval evidence."
    )
    parser.add_argument("project", type=Path, help="Clearance project directory")
    parser.add_argument("--report", type=Path, help="Write a Markdown report")
    parser.add_argument("--json-out", type=Path, help="Write machine-readable findings")
    return parser.parse_args()


def norm(value: Any) -> str:
    return str(value or "").strip().lower()


def clean(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text) and "replace" not in text.lower() and text.lower() != "unknown"


def is_yes(value: Any) -> bool:
    return norm(value) in YES


def is_na(value: Any) -> bool:
    return norm(value) in NA


def is_decided(value: Any) -> bool:
    return norm(value) in DECIDED


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(audit: Audit, relative: str, code: str) -> dict[str, Any] | None:
    path = audit.path(relative, code, relative)
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        audit.block(code, f"Cannot parse {relative}: {exc}")
        return None
    if not isinstance(value, dict):
        audit.block(code, f"{relative} must contain a JSON object")
        return None
    return value


def load_csv(
    audit: Audit, relative: str, required_columns: set[str], code: str
) -> list[dict[str, str]]:
    path = audit.path(relative, code, relative)
    if path is None:
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = sorted(required_columns - columns)
            if missing:
                audit.block(code, f"{relative} is missing columns: {', '.join(missing)}")
                return []
            return [dict(row) for row in reader if any(str(v or "").strip() for v in row.values())]
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        audit.block(code, f"Cannot parse {relative}: {exc}")
        return []


def check_status(audit: Audit, value: str, code: str, label: str) -> None:
    status = norm(value)
    if status in NO or status not in (YES | {"warn", "warning"}):
        audit.block(code, f"{label} status is not cleared: {value or 'missing'}")
    elif status in {"warn", "warning"}:
        audit.warn(code, f"{label} is marked WARN and needs documented acceptance")


def check_source_register(audit: Audit, release_types: set[str]) -> None:
    required = {
        "source_id",
        "title",
        "local_path",
        "license_expression",
        "license_evidence_path",
        "sha256",
        "commercial_use",
        "derivatives",
        "ai_input",
        "redistribute_digital",
        "physical_sale",
        "patent_rights",
        "trademark_privacy_publicity",
        "status",
    }
    rows = load_csv(audit, "01-sources/source-register.csv", required, "SRC-000")
    if not rows:
        audit.block("SRC-001", "Source register has no cleared source rows")
        return
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        label = f"source row {number} ({row.get('source_id') or 'no ID'})"
        source_id = (row.get("source_id") or "").strip()
        if not clean(source_id) or source_id in seen:
            audit.block("SRC-002", f"{label} has a missing, placeholder, or duplicate ID")
        seen.add(source_id)
        for field in ("title", "license_expression"):
            if not clean(row.get(field)):
                audit.block("SRC-003", f"{label} has unresolved {field}")
        if not HASH_RE.fullmatch((row.get("sha256") or "").strip()):
            audit.block("SRC-004", f"{label} needs a 64-character SHA-256")
        else:
            source_path = audit.path(
                row.get("local_path") or "", "SRC-004", f"{label} original source"
            )
            if source_path is not None:
                actual = sha256_file(source_path)
                if actual.lower() != (row.get("sha256") or "").strip().lower():
                    audit.block("SRC-004", f"{label} source SHA-256 does not match local_path")
        audit.evidence(
            row.get("license_evidence_path") or "", "SRC-005", f"{label} license"
        )
        check_status(audit, row.get("status") or "", "SRC-006", label)
        if not is_yes(row.get("commercial_use")):
            audit.block("SRC-007", f"{label} does not document commercial-use permission")
        for field in ("derivatives", "ai_input", "patent_rights", "trademark_privacy_publicity"):
            if not is_decided(row.get(field)):
                audit.block("SRC-008", f"{label} has unresolved {field}")
        if "digital" in release_types:
            value = row.get("redistribute_digital")
            if not (is_yes(value) or is_na(value)):
                audit.block(
                    "SRC-009",
                    f"{label} lacks digital redistribution permission or documented not-applicable decision",
                )
        if "physical" in release_types:
            value = row.get("physical_sale")
            if not (is_yes(value) or is_na(value)):
                audit.block(
                    "SRC-010",
                    f"{label} lacks physical-sale permission or documented not-applicable decision",
                )


def check_tool_register(audit: Audit) -> None:
    required = {
        "tool_id",
        "name",
        "version",
        "license_expression",
        "plan",
        "terms_evidence_path",
        "commercial_use",
        "input_confidentiality",
        "output_restrictions",
        "plugins_assets_dependencies",
        "distribution_obligations",
        "status",
    }
    rows = load_csv(audit, "02-tools/tool-register.csv", required, "TOOL-000")
    if not rows:
        audit.block("TOOL-001", "Tool register has no cleared tool rows")
        return
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        label = f"tool row {number} ({row.get('tool_id') or 'no ID'})"
        tool_id = (row.get("tool_id") or "").strip()
        if not clean(tool_id) or tool_id in seen:
            audit.block("TOOL-002", f"{label} has a missing, placeholder, or duplicate ID")
        seen.add(tool_id)
        for field in (
            "name",
            "version",
            "license_expression",
            "plan",
            "input_confidentiality",
            "output_restrictions",
            "plugins_assets_dependencies",
            "distribution_obligations",
        ):
            if not clean(row.get(field)):
                audit.block("TOOL-003", f"{label} has unresolved {field}")
        audit.evidence(
            row.get("terms_evidence_path") or "", "TOOL-004", f"{label} terms"
        )
        if not is_yes(row.get("commercial_use")):
            audit.block("TOOL-005", f"{label} does not document commercial use")
        check_status(audit, row.get("status") or "", "TOOL-006", label)


def check_component_register(audit: Audit, release_types: set[str]) -> None:
    required = {
        "component_id",
        "name",
        "license_expression",
        "license_evidence_path",
        "embedded_in_release",
        "redistribution_rights",
        "physical_use_rights",
        "patent_design_trademark",
        "proof_path",
        "status",
    }
    rows = load_csv(audit, "03-components/component-register.csv", required, "CMP-000")
    if not rows:
        audit.pass_note("CMP-001", "No imported/bought components declared")
        return
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        label = f"component row {number} ({row.get('component_id') or 'no ID'})"
        component_id = (row.get("component_id") or "").strip()
        if not clean(component_id) or component_id in seen:
            audit.block("CMP-002", f"{label} has a missing, placeholder, or duplicate ID")
        seen.add(component_id)
        for field in ("name", "license_expression"):
            if not clean(row.get(field)):
                audit.block("CMP-003", f"{label} has unresolved {field}")
        audit.evidence(
            row.get("license_evidence_path") or "", "CMP-004", f"{label} license"
        )
        audit.evidence(row.get("proof_path") or "", "CMP-005", f"{label} supplier")
        check_status(audit, row.get("status") or "", "CMP-006", label)
        if not is_decided(row.get("embedded_in_release")):
            audit.block("CMP-007", f"{label} has unresolved embedded_in_release")
        if not (is_yes(row.get("patent_design_trademark")) or is_na(row.get("patent_design_trademark"))):
            audit.block("CMP-008", f"{label} lacks patent/design/trademark clearance")
        if "digital" in release_types and is_yes(row.get("embedded_in_release")):
            if not is_yes(row.get("redistribution_rights")):
                audit.block("CMP-009", f"{label} is embedded but lacks redistribution rights")
        elif not is_decided(row.get("redistribution_rights")):
            audit.block("CMP-010", f"{label} has unresolved redistribution_rights")
        if "physical" in release_types and not (
            is_yes(row.get("physical_use_rights")) or is_na(row.get("physical_use_rights"))
        ):
            audit.block("CMP-011", f"{label} lacks physical-use rights")


def check_human_log(audit: Audit) -> None:
    required = {
        "timestamp",
        "contributor",
        "artifact_or_commit",
        "choice_or_change",
        "human_contribution",
        "ai_or_tool_role",
        "evidence_path",
    }
    rows = load_csv(
        audit, "04-authorship/human-contribution-log.csv", required, "AUTH-000"
    )
    if not rows:
        audit.block("AUTH-001", "Human contribution log is empty")
        return
    for number, row in enumerate(rows, start=2):
        label = f"human contribution row {number}"
        for field in required:
            if not clean(row.get(field)):
                audit.block("AUTH-002", f"{label} has unresolved {field}")
        audit.evidence(row.get("evidence_path") or "", "AUTH-003", label)


def check_market_matrix(audit: Audit, target_markets: set[str]) -> None:
    required = {
        "market",
        "channel",
        "release_type",
        "product_classification",
        "ai_classification",
        "ip_searches",
        "product_safety_framework",
        "conformity_and_label",
        "consumer_digital_terms",
        "tax_epr",
        "privacy",
        "export_sanctions",
        "language",
        "official_source",
        "effective_date",
        "evidence_path",
        "owner",
        "status",
    }
    rows = load_csv(audit, "05-clearance/market-matrix.csv", required, "MKT-000")
    covered: set[str] = set()
    for number, row in enumerate(rows, start=2):
        label = f"market row {number} ({row.get('market') or 'no market'})"
        market = (row.get("market") or "").strip().upper()
        if clean(market):
            covered.add(market)
        for field in required - {"status"}:
            if not clean(row.get(field)):
                audit.block("MKT-001", f"{label} has unresolved {field}")
        audit.evidence(row.get("evidence_path") or "", "MKT-004", label)
        check_status(audit, row.get("status") or "", "MKT-002", label)
    for market in sorted(target_markets - covered):
        audit.block("MKT-003", f"Target market has no cleared country/channel row: {market}")


def check_text_placeholders(audit: Audit, relative: str, required: bool = True) -> None:
    path = audit.path(relative, "DOC-001", relative)
    if path is None:
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    match = PLACEHOLDER_RE.search(text)
    if match:
        audit.block("DOC-002", f"{relative} still contains placeholder {match.group(0)}")
    if required and len(text.strip()) < 40:
        audit.block("DOC-003", f"{relative} is unexpectedly empty")


def check_artifacts(audit: Audit, manifest: dict[str, Any]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        audit.block("ART-001", "provenance.json has no final artifacts")
        return
    seen: set[str] = set()
    for index, item in enumerate(artifacts, start=1):
        if not isinstance(item, dict):
            audit.block("ART-002", f"artifact {index} is not an object")
            continue
        relative = str(item.get("path") or "")
        if relative in seen:
            audit.block("ART-003", f"duplicate artifact path: {relative}")
        seen.add(relative)
        path = audit.path(relative, "ART-004", f"artifact {index}")
        for field in ("role", "license"):
            if not clean(item.get(field)):
                audit.block("ART-005", f"artifact {index} has unresolved {field}")
        expected = str(item.get("sha256") or "")
        if not HASH_RE.fullmatch(expected):
            audit.block("ART-006", f"artifact {index} lacks a valid SHA-256")
        elif path is not None:
            actual = sha256_file(path)
            if actual.lower() != expected.lower():
                audit.block(
                    "ART-007",
                    f"artifact hash mismatch for {relative}: expected {expected}, got {actual}",
                )


def check_manifest(
    audit: Audit, project: dict[str, Any], manifest: dict[str, Any], release_types: set[str]
) -> None:
    for field in ("project_id", "release_id", "product_name", "intended_use"):
        if not clean(manifest.get(field)):
            audit.block("MAN-001", f"provenance.json has unresolved {field}")
    for field in ("project_id", "release_id", "product_name"):
        if manifest.get(field) != project.get(field):
            audit.block("MAN-002", f"project.json and provenance.json disagree on {field}")
    manifest_markets = {str(v).upper() for v in manifest.get("target_markets", [])}
    project_markets = {str(v).upper() for v in project.get("target_markets", [])}
    if manifest_markets != project_markets:
        audit.block("MAN-003", "project and manifest target markets differ")
    if set(manifest.get("release_types", [])) != release_types:
        audit.block("MAN-004", "project and manifest release types differ")

    seller = manifest.get("seller") if isinstance(manifest.get("seller"), dict) else {}
    for field in ("legal_name", "country", "postal_address", "electronic_address"):
        if not clean(seller.get(field)):
            audit.block("MAN-005", f"seller.{field} is unresolved")

    classification = (
        manifest.get("product_classification")
        if isinstance(manifest.get("product_classification"), dict)
        else {}
    )
    check_status(
        audit,
        str(classification.get("status") or ""),
        "MAN-006",
        "product classification",
    )
    if not clean(classification.get("classification")):
        audit.block("MAN-007", "product classification text is missing")
    audit.evidence(
        str(classification.get("evidence_path") or ""),
        "MAN-008",
        "product classification",
    )

    ai = manifest.get("ai_use") if isinstance(manifest.get("ai_use"), dict) else {}
    if norm(ai.get("used")) not in {"yes", "no"}:
        audit.block("AI-001", "ai_use.used must be yes or no")
    if norm(ai.get("used")) == "yes":
        if not ai.get("roles") or not ai.get("providers"):
            audit.block("AI-002", "AI use needs roles and providers")
        for field in ("disclosure_text", "human_reviewer"):
            if not clean(ai.get(field)):
                audit.block("AI-003", f"AI use needs {field}")
        if not (is_yes(ai.get("source_originals_retained")) or is_na(ai.get("source_originals_retained"))):
            audit.block("AI-004", "AI source-original retention is unresolved")

    check_artifacts(audit, manifest)

    outgoing = (
        manifest.get("outgoing_licenses")
        if isinstance(manifest.get("outgoing_licenses"), dict)
        else {}
    )
    if not clean(outgoing.get("geometry")):
        audit.block("LIC-001", "Geometry outgoing license is unresolved")
    for field in ("software", "documentation"):
        if not clean(outgoing.get(field)):
            audit.block("LIC-002", f"Outgoing {field} license is unresolved")

    audit.path(str(manifest.get("notices_path") or ""), "LIC-003", "third-party notices")

    watermark = (
        manifest.get("watermark") if isinstance(manifest.get("watermark"), dict) else {}
    )
    for field in ("geometry_mark", "geometry_location", "metadata", "sidecar"):
        value = str(watermark.get(field) or "")
        if not clean(value):
            audit.block("WM-001", f"Watermark/provenance field {field} is unresolved")
        if norm(value) in NA:
            audit.block(
                "WM-002",
                f"Watermark/provenance field {field} needs a written safety/format rationale, not bare N/A",
            )

    clearance = (
        manifest.get("clearance") if isinstance(manifest.get("clearance"), dict) else {}
    )
    for field in (
        "copyright_authorship",
        "patent",
        "design",
        "trademark",
        "privacy_publicity",
    ):
        value = clearance.get(field)
        if not (is_yes(value) or is_na(value)):
            audit.block("CLR-001", f"Clearance {field} is not PASS or not_applicable")
    audit.evidence(
        str(clearance.get("evidence_path") or ""), "CLR-002", "rights clearance"
    )

    compliance = (
        manifest.get("compliance") if isinstance(manifest.get("compliance"), dict) else {}
    )
    for field in (
        "risk_assessment",
        "test_reports",
        "labels_and_instructions",
        "consumer_terms",
        "traceability",
        "technical_file",
    ):
        value = compliance.get(field)
        if not (is_yes(value) or is_na(value)):
            audit.block("COM-001", f"Compliance {field} is not PASS or not_applicable")
    audit.evidence(
        str(compliance.get("evidence_path") or ""), "COM-002", "compliance"
    )
    if "digital" in release_types and is_na(compliance.get("consumer_terms")):
        audit.block("COM-003", "Digital commercial release cannot mark consumer terms N/A without channel-specific counsel decision")
    if "physical" in release_types:
        for field in ("risk_assessment", "test_reports", "labels_and_instructions", "traceability", "technical_file"):
            if not is_yes(compliance.get(field)):
                audit.block("COM-004", f"Physical release requires PASS for {field}")

    export = manifest.get("export") if isinstance(manifest.get("export"), dict) else {}
    if not clean(export.get("classification")):
        audit.block("EXP-001", "Export classification is unresolved")
    if not (is_yes(export.get("screening")) or is_na(export.get("screening"))):
        audit.block("EXP-002", "Export/sanctions screening is unresolved")
    if not is_na(export.get("classification")):
        audit.evidence(
            str(export.get("evidence_path") or ""), "EXP-003", "export classification"
        )

    audit.path(str(manifest.get("approval_path") or ""), "APP-001", "approval record")


def check_evidence_manifest(audit: Audit, approval: dict[str, Any]) -> None:
    relative = str(approval.get("evidence_manifest_path") or "")
    manifest_path = audit.path(relative, "APP-011", "pre-approval evidence manifest")
    if manifest_path is None:
        return
    expected_manifest_hash = str(approval.get("evidence_manifest_sha256") or "")
    if not HASH_RE.fullmatch(expected_manifest_hash):
        audit.block("APP-012", "Approval lacks a valid evidence_manifest_sha256")
    elif sha256_file(manifest_path).lower() != expected_manifest_hash.lower():
        audit.block("APP-013", "Pre-approval evidence manifest hash does not match approval")

    listed: dict[str, str] = {}
    try:
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        audit.block("APP-014", f"Cannot read pre-approval evidence manifest: {exc}")
        return
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        match = SUM_LINE_RE.fullmatch(line)
        if not match:
            audit.block("APP-015", f"Invalid evidence manifest syntax at line {line_number}")
            continue
        expected, member = match.groups()
        if member in listed:
            audit.block("APP-016", f"Duplicate evidence manifest path: {member}")
            continue
        parts = Path(member).parts
        if not parts or parts[0] in {"08-approvals", "09-incidents", "reports", ".git"}:
            audit.block("APP-017", f"Evidence manifest contains excluded/circular path: {member}")
            continue
        member_path = audit.path(member, "APP-018", f"evidence manifest member {member}")
        if member_path is not None:
            actual = sha256_file(member_path)
            if actual.lower() != expected.lower():
                audit.block("APP-019", f"Evidence hash mismatch: {member}")
        listed[member] = expected

    expected_files: set[str] = set()
    for path in audit.root.rglob("*"):
        relative_path = path.relative_to(audit.root)
        if not relative_path.parts:
            continue
        if relative_path.parts[0] in {"08-approvals", "09-incidents", "reports", ".git"}:
            continue
        if path.is_symlink():
            audit.block("APP-020", f"Symlink is not permitted in frozen evidence: {relative_path}")
            continue
        if path.is_file():
            expected_files.add(relative_path.as_posix())
    missing = sorted(expected_files - set(listed))
    for member in missing:
        audit.block("APP-021", f"File is not bound by pre-approval evidence manifest: {member}")
    if not listed:
        audit.block("APP-022", "Pre-approval evidence manifest contains no files")


def check_approval(
    audit: Audit,
    project: dict[str, Any],
    manifest_path: Path,
    release_types: set[str],
) -> None:
    approval = load_json(audit, "08-approvals/release-approval.json", "APP-002")
    if approval is None:
        return
    for field in ("project_id", "release_id"):
        if approval.get(field) != project.get(field):
            audit.block("APP-003", f"Approval and project disagree on {field}")
    actual_hash = sha256_file(manifest_path)
    if str(approval.get("manifest_sha256") or "").lower() != actual_hash:
        audit.block("APP-004", "Approval manifest_sha256 does not match current provenance.json")
    if norm(approval.get("decision")) != "pass":
        audit.block("APP-005", "Overall approval decision is not PASS")
    if not clean(approval.get("approved_at")):
        audit.block("APP-006", "Approval timestamp is unresolved")
    check_evidence_manifest(audit, approval)

    approvers = approval.get("approvers")
    if not isinstance(approvers, list):
        audit.block("APP-007", "Approvers must be an array")
        return
    roles: dict[str, dict[str, Any]] = {
        norm(item.get("role")): item for item in approvers if isinstance(item, dict)
    }
    required_roles = {"engineering", "ip_legal", "business_owner"}
    if "physical" in release_types:
        required_roles.add("safety_compliance")
    for role in sorted(required_roles):
        item = roles.get(role)
        if not item:
            audit.block("APP-008", f"Missing required approver role: {role}")
            continue
        for field in ("name", "authority", "signed_at", "signature_reference"):
            if not clean(item.get(field)):
                audit.block("APP-009", f"Approver {role} has unresolved {field}")
        if norm(item.get("decision")) != "pass":
            audit.block("APP-010", f"Approver {role} decision is not PASS")


def result_status(findings: list[Finding]) -> str:
    if any(item.severity == "BLOCK" for item in findings):
        return "BLOCK"
    if any(item.severity == "WARN" for item in findings):
        return "WARN"
    return "PASS"


def markdown_report(root: Path, status: str, findings: list[Finding]) -> str:
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# Commercial 3D Release Audit",
        "",
        f"- Project: {root}",
        f"- Generated: {generated}",
        f"- Decision: **{status}**",
        "",
        "> Automated evidence check only. PASS is not legal advice, a freedom-to-operate opinion, a conformity certificate, or proof of product safety.",
        "",
        "## Findings",
        "",
        "| Severity | Code | Finding |",
        "|---|---|---|",
    ]
    for item in findings:
        message = item.message.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {item.severity} | {item.code} | {message} |")
    lines.extend(
        [
            "",
            "## Release Rule",
            "",
            "- PASS: automated checks found no required evidence omission; retain competent human approval.",
            "- WARN: resolve or obtain written authorized risk acceptance before release.",
            "- BLOCK: do not publish, upload, sell, manufacture for sale, or ship.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.project.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: project directory does not exist: {root}", file=sys.stderr)
        return 3

    audit = Audit(root)
    project = load_json(audit, "project.json", "PRJ-001")
    manifest = load_json(audit, "07-release/provenance.json", "MAN-000")
    if project is None or manifest is None:
        status = result_status(audit.findings)
    else:
        for field in (
            "project_id",
            "release_id",
            "product_name",
            "seller_country",
            "target_markets",
            "release_types",
            "created_at",
            "intended_use",
            "product_category",
            "safety_critical",
            "status",
        ):
            if not clean(project.get(field)):
                audit.block("PRJ-002", f"project.json has unresolved {field}")
        if norm(project.get("status")) != "ready_for_release":
            audit.block("PRJ-003", "project status must be ready_for_release")
        if norm(project.get("safety_critical")) not in {"yes", "no"}:
            audit.block("PRJ-004", "safety_critical must be yes or no")
        elif norm(project.get("safety_critical")) == "yes":
            audit.warn(
                "PRJ-005",
                "Safety-critical product declared; automated checks cannot replace specialist review/testing",
            )

        release_types = {str(item).lower() for item in project.get("release_types", [])}
        target_markets = {str(item).upper() for item in project.get("target_markets", [])}
        if not release_types or not release_types.issubset({"digital", "physical"}):
            audit.block("PRJ-006", "release_types must contain digital and/or physical")
        if not target_markets:
            audit.block("PRJ-007", "At least one target market is required")

        check_source_register(audit, release_types)
        check_tool_register(audit)
        check_component_register(audit, release_types)
        check_human_log(audit)
        check_market_matrix(audit, target_markets)
        check_manifest(audit, project, manifest, release_types)

        for relative in (
            "05-clearance/RIGHTS-CLEARANCE.md",
            "06-engineering/PRODUCT-TECHNICAL-FILE.md",
            "07-release/COMMERCIAL-MODEL-LICENSE.md",
            "07-release/THIRD-PARTY-NOTICES.md",
            "07-release/AI-DISCLOSURE.md",
        ):
            check_text_placeholders(audit, relative)

        manifest_path = root / "07-release/provenance.json"
        check_approval(audit, project, manifest_path, release_types)
        status = result_status(audit.findings)

    report = markdown_report(root, status, audit.findings)
    if args.report:
        args.report.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        args.report.expanduser().resolve().write_text(report, encoding="utf-8")
    if args.json_out:
        payload = {
            "schema_version": "1.0",
            "project": str(root),
            "status": status,
            "findings": [asdict(item) for item in audit.findings],
        }
        args.json_out.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        args.json_out.expanduser().resolve().write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )

    print(report)
    return {"PASS": 0, "WARN": 1, "BLOCK": 2}[status]


if __name__ == "__main__":
    raise SystemExit(main())
