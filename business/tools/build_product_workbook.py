#!/usr/bin/env python3
"""Build the multi-sheet product portfolio workbook with Python stdlib only."""

from __future__ import annotations

import csv
import datetime as dt
import json
import posixpath
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_CSV = ROOT / "02-portfolio" / "product-portfolio.csv"
RESEARCH_STATUS_CSV = ROOT / "02-portfolio" / "research-ideas-implementation.csv"
RESEARCH_ADDITIONS_CSV = ROOT / "02-portfolio" / "research-ideas-additions.csv"
RESEARCH_ADDITIONS_2_CSV = ROOT / "02-portfolio" / "research-ideas-additions-2.csv"
RESEARCH_R3_VARIANTS_CSV = ROOT / "02-portfolio" / "research-ideas-r3-variants.csv"
RESEARCH_ADDITION_SOURCES_CSV = ROOT / "02-portfolio" / "research-idea-sources-additions.csv"
RESEARCH_PRIORITY_CSV = ROOT / "02-portfolio" / "research-idea-priority.csv"
RESEARCH_PREFLIGHT_CSV = ROOT / "02-portfolio" / "research-idea-preflight-estimates.csv"
READINESS_ADVANCEMENT_CSV = ROOT / "02-portfolio" / "readiness-advancement-register.csv"
TASKS_CSV = ROOT / "07-roadmap" / "mvp-tasks.csv"
OUTPUT = ROOT / "02-portfolio" / "product-portfolio.xlsx"
RESEARCH_WORKBOOK = ROOT.parent / "research" / "market" / "JuSt_Innovation_3D_Print_Commercial_Product_Matrix_2026.xlsx"
PRODUCTS_ROOT = ROOT.parent / "products"
PRODUCT_PREFLIGHT_AUDIT_GLOB = "PRODUCT-PREFLIGHT-AUDIT-*.json"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PREFLIGHT_WEIGHTS = {
    "REQ": 7,
    "CTX": 5,
    "PAR": 10,
    "INT": 20,
    "CPL": 10,
    "MOT": 10,
    "GEO": 7,
    "PHY": 10,
    "MAT": 7,
    "EXT": 7,
    "VER": 7,
}


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


def read_dict_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def exact_target_lane(complexity: str, criticality: str) -> str:
    """Return the likely lane after readiness and hard-gate evidence is sufficient."""
    complexity_level = int(complexity[1:])
    criticality_level = int(criticality[1:])
    if criticality_level >= 4:
        return "E"
    if complexity_level >= 4 or criticality_level >= 3:
        return "D"
    if complexity_level >= 3 or criticality_level >= 2:
        return "C"
    if complexity_level <= 1 and criticality_level == 0:
        return "A"
    return "B"


def preflight_short(scorecard: dict[str, object]) -> str:
    return (
        f"{scorecard['complexity']} \u00b7 {scorecard['readiness']} \u00b7 "
        f"{scorecard['criticality']} \u00b7 Lane {scorecard['lane']} \u00b7 {scorecard['confidence']}"
    )


def load_product_preflight_records() -> list[dict[str, object]]:
    """Load and cross-check the documented preflight for every product directory."""
    audit_paths = sorted(PRODUCTS_ROOT.glob(PRODUCT_PREFLIGHT_AUDIT_GLOB))
    if not audit_paths:
        raise ValueError(f"No product preflight audit matches {PRODUCT_PREFLIGHT_AUDIT_GLOB}")
    with audit_paths[-1].open(encoding="utf-8") as handle:
        audit = json.load(handle)
    entries = audit.get("products", [])
    if audit.get("product_count") != len(entries):
        raise ValueError("Product preflight audit count does not match its product rows")
    audit_products = {str(entry["product"]) for entry in entries}
    product_directories = {
        product.relative_to(PRODUCTS_ROOT).as_posix()
        for family in PRODUCTS_ROOT.iterdir()
        if family.is_dir()
        for product in family.iterdir()
        if product.is_dir()
        and product.name.startswith(("mm-", "unregistered-"))
    }
    if audit_products != product_directories:
        missing = sorted(product_directories.difference(audit_products))
        extra = sorted(audit_products.difference(product_directories))
        raise ValueError(f"Product preflight audit is stale; missing={missing}, extra={extra}")

    records: list[dict[str, object]] = []
    for entry in entries:
        product_root = PRODUCTS_ROOT / str(entry["product"])
        preflight_path = product_root / str(entry["preflight_result"])
        purpose_path = product_root / str(entry["purpose_document"])
        if not preflight_path.is_file() or not purpose_path.is_file():
            raise ValueError(f"Missing purpose or preflight document for {entry['product']}")
        with preflight_path.open(encoding="utf-8") as handle:
            preflight = json.load(handle)
        scorecard = {
            "complexity": preflight["complexity"]["class"],
            "score_0_100": preflight["complexity"]["score_0_100"],
            "readiness": preflight["readiness"]["level"],
            "criticality": preflight["criticality"]["level"],
            "lane": preflight["decision"]["lane"],
            "confidence": preflight["decision"]["confidence"],
            "release": preflight["decision"]["design_release"],
        }
        audit_scorecard_match = scorecard == entry["scorecard"]
        records.append(
            {
                "audit": entry,
                "preflight": preflight,
                "scorecard": scorecard,
                "product_root": product_root,
                "preflight_path": preflight_path,
                "purpose_path": purpose_path,
                "audit_scorecard_match": audit_scorecard_match,
            }
        )
    return records


def add_portfolio_preflight(
    portfolio: list[list[str]], records: list[dict[str, object]]
) -> None:
    columns = [
        "Preflight_Short",
        "Preflight_Target_Lane_After_Evidence",
        "Preflight_Assessment_ID",
        "Preflight_Result_Path",
        "Purpose_Document_Path",
    ]
    source_width = len(portfolio[0])
    source_index = portfolio[0].index("Source_Path")
    by_source = {
        record["product_root"].relative_to(ROOT.parent).as_posix(): record
        for record in records
    }
    portfolio[0].extend(columns)
    for row in portfolio[1:]:
        row.extend([""] * (source_width - len(row)))
        source = str(row[source_index])
        if source not in by_source:
            raise ValueError(f"Portfolio row lacks a product preflight: {source}")
        record = by_source[source]
        scorecard = record["scorecard"]
        preflight = record["preflight"]
        row.extend(
            [
                preflight_short(scorecard),
                exact_target_lane(str(scorecard["complexity"]), str(scorecard["criticality"])),
                str(preflight["assessment_id"]),
                record["preflight_path"].relative_to(ROOT.parent).as_posix(),
                record["purpose_path"].relative_to(ROOT.parent).as_posix(),
            ]
        )


def product_preflight_sheet(records: list[dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = [[
        "Project_ID",
        "Product_Path",
        "Revision",
        "Preflight_Short",
        "PC_0_100",
        "Target_Lane_After_Evidence",
        "Design_Release",
        "Assessment_ID",
        "Assessment_Date",
        "Preflight_Result",
        "Purpose_Document",
        "Audit_Snapshot_Status",
        "Archive_Status",
        "Archived_Entries",
    ]]
    for record in sorted(records, key=lambda item: str(item["audit"]["product"])):
        audit = record["audit"]
        preflight = record["preflight"]
        scorecard = record["scorecard"]
        rows.append(
            [
                preflight.get("traceability", {}).get("project_id", audit["project_id"]),
                f"products/{audit['product']}",
                preflight.get("traceability", {}).get("project_revision", audit["revision"]),
                preflight_short(scorecard),
                scorecard["score_0_100"],
                exact_target_lane(str(scorecard["complexity"]), str(scorecard["criticality"])),
                scorecard["release"],
                preflight["assessment_id"],
                preflight["assessment_date"],
                record["preflight_path"].relative_to(ROOT.parent).as_posix(),
                record["purpose_path"].relative_to(ROOT.parent).as_posix(),
                "CURRENT" if record["audit_scorecard_match"] else "STALE_SCORECARD — LIVE PREFLIGHT USED",
                audit["archive"]["root_status"],
                len(audit["archive"]["moved_entries"]),
            ]
        )
    return rows


def read_research_preflight(path: Path, expected_ids: set[str]) -> dict[str, dict[str, str]]:
    rows = read_dict_csv(path)
    required = {
        "SKU_ID",
        "Preflight_Short",
        "Complexity_Band",
        "Readiness_Band",
        "Criticality_Band",
        "Current_Lane",
        "Target_Lane_After_Evidence",
        "Confidence",
        "Estimate_Status",
        "Basis",
        "Source_Or_Linked_Preflight",
    }
    if not rows or required.difference(rows[0]):
        raise ValueError(f"Research preflight overlay has a missing required column: {path}")
    ids = [row["SKU_ID"] for row in rows]
    if len(rows) != len(expected_ids) or set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError("Research preflight overlay must contain every combined research idea exactly once")
    for row in rows:
        if row["Current_Lane"] not in {"A", "B", "C", "D", "E"}:
            raise ValueError(f"Invalid current lane for {row['SKU_ID']}")
        if "RELEASE APPROVAL" not in row["Estimate_Status"]:
            raise ValueError(f"Research preflight disclaimer missing for {row['SKU_ID']}")
    return {row["SKU_ID"]: row for row in rows}


def add_research_preflight(
    rows: list[list[object]],
    sku_column: str,
    estimates: dict[str, dict[str, str]],
) -> None:
    output_columns = [
        ("Preflight_Short", "Preflight_Short"),
        ("Preflight_Complexity_Band", "Complexity_Band"),
        ("Preflight_Readiness_Band", "Readiness_Band"),
        ("Preflight_Criticality_Band", "Criticality_Band"),
        ("Preflight_Current_Lane", "Current_Lane"),
        ("Preflight_Target_Lane_After_Evidence", "Target_Lane_After_Evidence"),
        ("Preflight_Estimate_Status", "Estimate_Status"),
        ("Preflight_Basis", "Basis"),
        ("Preflight_Source", "Source_Or_Linked_Preflight"),
    ]
    source_width = len(rows[0])
    sku_index = rows[0].index(sku_column)
    rows[0].extend(output_name for output_name, _ in output_columns)
    for row in rows[1:]:
        row.extend([""] * (source_width - len(row)))
        sku_id = str(row[sku_index])
        if sku_id not in estimates:
            raise ValueError(f"Missing research preflight estimate for {sku_id}")
        estimate = estimates[sku_id]
        row.extend(estimate[source_name] for _, source_name in output_columns)


def read_research_status(path: Path) -> dict[str, dict[str, str]]:
    """Load the editable implementation overlay for the imported research matrix."""
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    ids = [row.get("SKU_ID", "") for row in rows]
    if not ids or any(not sku_id for sku_id in ids):
        raise ValueError(f"Research implementation overlay has a missing SKU_ID: {path}")
    if len(ids) != len(set(ids)):
        raise ValueError(f"Research implementation overlay has duplicate SKU_ID values: {path}")
    return {row["SKU_ID"]: row for row in rows}


def normalize_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def validate_research_additions(
    rows: list[list[str]],
    legacy_rows: list[list[object]],
    portfolio_rows: list[list[str]],
    research_status: dict[str, dict[str, str]],
) -> None:
    """Fail closed when the append-only +100 source is incomplete or collides exactly."""
    if not rows:
        raise ValueError(f"Research additions source is empty: {RESEARCH_ADDITIONS_CSV}")
    header = rows[0]
    required = {
        "SKU_ID",
        "Product",
        "Customer_Job",
        "Strategy_Fit",
        "Max_L_mm",
        "Max_W_mm",
        "Max_H_mm",
        "Risk_or_Limit",
        "Opportunity_Score",
        "Source_IDs",
        "Design_Status",
        "Next_Gate",
    }
    missing = sorted(required.difference(header))
    if missing:
        raise ValueError(f"Research additions source is missing columns: {', '.join(missing)}")
    if len(rows) != 101:
        raise ValueError(f"Research additions source must contain exactly 100 ideas; found {len(rows) - 1}")
    if any(len(row) != len(header) for row in rows):
        raise ValueError("Research additions source contains a row with the wrong column count")

    id_index = header.index("SKU_ID")
    product_index = header.index("Product")
    status_index = header.index("Design_Status")
    expected_ids = {f"SKU-{number:03d}" for number in range(101, 201)}
    ids = [row[id_index] for row in rows[1:]]
    if set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError("Research additions must use each ID from SKU-101 through SKU-200 exactly once")
    if any(row[status_index] != "P0 research backlog" for row in rows[1:]):
        raise ValueError("Every research addition must remain P0 research backlog")

    products = [normalize_name(row[product_index]) for row in rows[1:]]
    if any(not product for product in products) or len(products) != len(set(products)):
        raise ValueError("Research additions contain a blank or duplicate normalized product name")
    legacy_header = legacy_rows[0]
    legacy_product_index = legacy_header.index("Product")
    legacy_products = {normalize_name(row[legacy_product_index]) for row in legacy_rows[1:]}
    portfolio_header = portfolio_rows[0]
    portfolio_product_index = portfolio_header.index("Product_or_Model")
    portfolio_sku_index = portfolio_header.index("Working_SKU")
    portfolio_products: dict[str, set[str]] = {}
    for portfolio_row in portfolio_rows[1:]:
        normalized = normalize_name(portfolio_row[portfolio_product_index])
        portfolio_products.setdefault(normalized, set()).add(str(portfolio_row[portfolio_sku_index]))
    collisions = []
    for source_row, product in zip(rows[1:], products):
        sku_id = str(source_row[id_index])
        if product in legacy_products:
            collisions.append(product)
            continue
        if product not in portfolio_products:
            continue
        implementation = research_status.get(sku_id, {})
        mapped = implementation.get("Mapped_Working_SKU", "")
        started = implementation.get("Implementation_Status", "NOT_STARTED") != "NOT_STARTED"
        if not started or mapped not in portfolio_products[product]:
            collisions.append(product)
    collisions = sorted(set(collisions))
    if collisions:
        raise ValueError(f"Research additions duplicate retained research or portfolio names: {', '.join(collisions)}")

    for dimension in ("Max_L_mm", "Max_W_mm", "Max_H_mm"):
        index = header.index(dimension)
        limit = 250 if dimension == "Max_H_mm" else 220
        invalid = [row[id_index] for row in rows[1:] if not row[index].isdigit() or int(row[index]) > limit]
        if invalid:
            raise ValueError(f"{dimension} exceeds the common-printer envelope for: {', '.join(invalid)}")
    score_index = header.index("Opportunity_Score")
    invalid_scores = []
    for row in rows[1:]:
        try:
            score = float(row[score_index])
        except ValueError:
            invalid_scores.append(row[id_index])
            continue
        if not 0 <= score <= 100:
            invalid_scores.append(row[id_index])
    if invalid_scores:
        raise ValueError(f"Invalid opportunity score for: {', '.join(invalid_scores)}")


def validate_structured_research_additions(
    rows: list[list[str]],
    legacy_rows: list[list[object]],
    prior_additions: list[list[str]],
    portfolio_rows: list[list[str]],
) -> None:
    """Validate the strict SKU-201..300 trend and concept-preflight gates."""
    if not rows:
        raise ValueError(f"Structured research additions source is empty: {RESEARCH_ADDITIONS_2_CSV}")
    header = rows[0]
    required = {
        "SKU_ID", "Product", "Purpose", "Strategy_Fit", "Source_IDs", "Design_Status",
        "Max_L_mm", "Max_W_mm", "Max_H_mm", "Trend_Source_Strength_0_30",
        "Trend_Signal_Magnitude_0_30", "Trend_MetriMade_Fit_0_25", "Trend_Whitespace_0_15",
        "Trend_Score_0_100", "Trend_Score_Status", "REQ", "CTX", "PAR", "INT", "CPL",
        "MOT", "GEO", "PHY", "MAT", "EXT", "VER", "PC_0_100", "Complexity",
        "R_Scope", "R_Requirements", "R_Critical_Interfaces", "R_Manufacturing_Profile",
        "R_Verification", "Readiness", "Criticality", "Current_Lane",
        "Target_Lane_After_Evidence", "Confidence", "Design_Release", "Hard_Gates",
        "Preflight_Short", "Preflight_Status",
    }
    missing = sorted(required.difference(header))
    if missing:
        raise ValueError(f"Structured research additions source is missing columns: {', '.join(missing)}")
    if len(rows) != 101 or any(len(row) != len(header) for row in rows):
        raise ValueError("Structured research additions must contain exactly 100 complete idea rows")
    idx = {name: header.index(name) for name in required}
    expected_ids = {f"SKU-{number:03d}" for number in range(201, 301)}
    ids = [row[idx["SKU_ID"]] for row in rows[1:]]
    if set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError("Structured research additions must use each ID from SKU-201 through SKU-300 exactly once")

    legacy_product_index = legacy_rows[0].index("Product")
    prior_product_index = prior_additions[0].index("Product")
    portfolio_product_index = portfolio_rows[0].index("Product_or_Model")
    occupied_names = {
        normalize_name(row[legacy_product_index]) for row in legacy_rows[1:]
    } | {
        normalize_name(row[prior_product_index]) for row in prior_additions[1:]
    } | {
        normalize_name(row[portfolio_product_index]) for row in portfolio_rows[1:]
    }
    new_names = [normalize_name(row[idx["Product"]]) for row in rows[1:]]
    if any(not name for name in new_names) or len(new_names) != len(set(new_names)):
        raise ValueError("Structured research additions contain blank or duplicate normalized product names")
    collisions = sorted(set(new_names).intersection(occupied_names))
    if collisions:
        raise ValueError(f"Structured research additions collide with retained names: {', '.join(collisions)}")

    component_limits = {
        "Trend_Source_Strength_0_30": 30,
        "Trend_Signal_Magnitude_0_30": 30,
        "Trend_MetriMade_Fit_0_25": 25,
        "Trend_Whitespace_0_15": 15,
    }
    readiness_fields = (
        "R_Scope", "R_Requirements", "R_Critical_Interfaces", "R_Manufacturing_Profile", "R_Verification"
    )
    for row in rows[1:]:
        sku_id = row[idx["SKU_ID"]]
        if len(row[idx["Purpose"]].strip()) < 20:
            raise ValueError(f"Structured research purpose is missing or too vague for {sku_id}")
        if row[idx["Design_Status"]] != "P0 research backlog" or row[idx["Design_Release"]] != "CONCEPT_ONLY":
            raise ValueError(f"Structured research row bypasses the concept-only gate: {sku_id}")
        for dimension in ("Max_L_mm", "Max_W_mm", "Max_H_mm"):
            value = float(row[idx[dimension]])
            limit = 250 if dimension == "Max_H_mm" else 220
            if value <= 0 or value > limit:
                raise ValueError(f"{dimension} is outside the common-printer envelope for {sku_id}")
        trend_components = []
        for field, limit in component_limits.items():
            value = float(row[idx[field]])
            if not 0 <= value <= limit:
                raise ValueError(f"{field} is outside its allowed range for {sku_id}")
            trend_components.append(value)
        trend_score = float(row[idx["Trend_Score_0_100"]])
        if abs(sum(trend_components) - trend_score) > 0.01 or trend_score <= 70:
            raise ValueError(f"Trend-score gate or component sum failed for {sku_id}")
        if row[idx["Trend_Score_Status"]] != "DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND":
            raise ValueError(f"Trend-score disclaimer is missing for {sku_id}")

        pc_components = {}
        for field in PREFLIGHT_WEIGHTS:
            value = int(row[idx[field]])
            if not 0 <= value <= 4:
                raise ValueError(f"Preflight component {field} is outside 0–4 for {sku_id}")
            pc_components[field] = value
        pc = round(sum(PREFLIGHT_WEIGHTS[field] * pc_components[field] / 4 for field in PREFLIGHT_WEIGHTS), 2)
        if abs(pc - float(row[idx["PC_0_100"]])) > 0.01:
            raise ValueError(f"PC total is inconsistent for {sku_id}")
        expected_complexity = "C0" if pc <= 14 else "C1" if pc <= 24 else "C2" if pc <= 39 else "C3" if pc <= 59 else "C4" if pc <= 79 else "C5"
        complexity = row[idx["Complexity"]]
        if complexity != expected_complexity or complexity not in {"C0", "C1", "C2"}:
            raise ValueError(f"C<=2 gate failed for {sku_id}")
        if any(row[idx[field]] != "R2" for field in readiness_fields) or row[idx["Readiness"]] != "R2":
            raise ValueError(f"R>=2 evidence gate failed for {sku_id}")
        if row[idx["Criticality"]] != "K1":
            raise ValueError(f"K1 gate failed for {sku_id}")
        if row[idx["Current_Lane"]] != "E" or row[idx["Target_Lane_After_Evidence"]] != "B":
            raise ValueError(f"Current/target lane is inconsistent for {sku_id}")
        if "G3 FAIL" not in row[idx["Hard_Gates"]]:
            raise ValueError(f"Missing fail-closed process gate for {sku_id}")
        expected_short = f"{complexity} · R2 · K1 · Lane E · {row[idx['Confidence']]}"
        if row[idx["Preflight_Short"]] != expected_short:
            raise ValueError(f"Compact preflight is inconsistent for {sku_id}")
        if row[idx["Preflight_Status"]] != "STRUCTURED RESEARCH PREFLIGHT R2 — NOT PRODUCT RELEASE APPROVAL":
            raise ValueError(f"Structured preflight disclaimer is missing for {sku_id}")


def validate_specific_r3_variants(
    rows: list[list[str]],
    parent_ids: set[str],
    occupied_product_names: set[str],
) -> None:
    """Validate named-interface R3 children without promoting their generic parents."""
    if not rows:
        raise ValueError(f"Specific R3 variant source is empty: {RESEARCH_R3_VARIANTS_CSV}")
    header = rows[0]
    required = {
        "SKU_ID", "Parent_SKU_ID", "Product", "Purpose", "Strategy_Fit", "Source_IDs",
        "Design_Status", "Next_Gate", "Trend_Source_Strength_0_30",
        "Trend_Signal_Magnitude_0_30", "Trend_MetriMade_Fit_0_25", "Trend_Whitespace_0_15",
        "Trend_Score_0_100", "Trend_Score_Status", "Process_Profile_Refs", "Acceptance_Criteria",
        "REQ", "CTX", "PAR", "INT", "CPL", "MOT", "GEO", "PHY", "MAT", "EXT", "VER",
        "PC_0_100", "Complexity", "R_Scope", "R_Requirements", "R_Critical_Interfaces",
        "R_Manufacturing_Profile", "R_Verification", "Readiness", "Criticality", "Current_Lane",
        "Target_Lane_After_Evidence", "Confidence", "Design_Release", "Hard_Gates",
        "Preflight_Short", "Preflight_Status",
    }
    missing = sorted(required.difference(header))
    if missing:
        raise ValueError(f"Specific R3 variant source is missing columns: {', '.join(missing)}")
    if len(rows) != 15 or any(len(row) != len(header) for row in rows):
        raise ValueError("Specific R3 variant source must contain exactly 14 complete rows")
    idx = {name: header.index(name) for name in required}
    expected_ids = {f"SKU-{number:03d}" for number in range(301, 315)}
    ids = [row[idx["SKU_ID"]] for row in rows[1:]]
    if set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError("Specific R3 variants must use SKU-301 through SKU-314 exactly once")
    names = [normalize_name(row[idx["Product"]]) for row in rows[1:]]
    if any(not name for name in names) or len(names) != len(set(names)):
        raise ValueError("Specific R3 variants contain blank or duplicate product names")
    collisions = sorted(set(names).intersection(occupied_product_names))
    if collisions:
        raise ValueError(f"Specific R3 variants collide with existing idea/product names: {', '.join(collisions)}")

    component_limits = {
        "Trend_Source_Strength_0_30": 30,
        "Trend_Signal_Magnitude_0_30": 30,
        "Trend_MetriMade_Fit_0_25": 25,
        "Trend_Whitespace_0_15": 15,
    }
    readiness_fields = (
        "R_Scope", "R_Requirements", "R_Critical_Interfaces", "R_Manufacturing_Profile", "R_Verification"
    )
    required_gates = {f"G{number} PASS" for number in range(7)}
    for row in rows[1:]:
        sku_id = row[idx["SKU_ID"]]
        if row[idx["Parent_SKU_ID"]] not in parent_ids:
            raise ValueError(f"Specific R3 variant has an unknown generic parent: {sku_id}")
        if len(row[idx["Purpose"]].strip()) < 20:
            raise ValueError(f"Specific R3 variant purpose is missing or vague: {sku_id}")
        if row[idx["Design_Status"]] != "P0 evidence-backed specific variant":
            raise ValueError(f"Specific R3 variant design status is inconsistent: {sku_id}")
        if row[idx["Design_Release"]] != "GO_WITH_CONTROLS":
            raise ValueError(f"Specific R3 variant bypasses the controlled design gate: {sku_id}")
        trend_components = []
        for field, limit in component_limits.items():
            value = float(row[idx[field]])
            if not 0 <= value <= limit:
                raise ValueError(f"{field} is outside its allowed range for {sku_id}")
            trend_components.append(value)
        trend_score = float(row[idx["Trend_Score_0_100"]])
        if abs(sum(trend_components) - trend_score) > 0.01 or trend_score <= 70:
            raise ValueError(f"Specific R3 variant trend score failed for {sku_id}")
        if row[idx["Trend_Score_Status"]] != "INHERITED DIRECTIONAL PLANNING SCORE — NOT VALIDATED VARIANT DEMAND":
            raise ValueError(f"Specific R3 variant demand disclaimer is missing: {sku_id}")
        pc_components = {field: int(row[idx[field]]) for field in PREFLIGHT_WEIGHTS}
        if any(not 0 <= value <= 4 for value in pc_components.values()):
            raise ValueError(f"Specific R3 variant PC component is outside 0–4: {sku_id}")
        pc = round(sum(PREFLIGHT_WEIGHTS[field] * pc_components[field] / 4 for field in PREFLIGHT_WEIGHTS), 2)
        if abs(pc - float(row[idx["PC_0_100"]])) > 0.01:
            raise ValueError(f"Specific R3 variant PC total is inconsistent: {sku_id}")
        expected_complexity = "C0" if pc <= 14 else "C1" if pc <= 24 else "C2" if pc <= 39 else "C3" if pc <= 59 else "C4" if pc <= 79 else "C5"
        complexity = row[idx["Complexity"]]
        if complexity != expected_complexity or complexity not in {"C1", "C2", "C3"}:
            raise ValueError(f"Specific R3 variant complexity is inconsistent: {sku_id}")
        if any(row[idx[field]] != "R3" for field in readiness_fields) or row[idx["Readiness"]] != "R3":
            raise ValueError(f"Specific R3 variant readiness evidence is inconsistent: {sku_id}")
        if row[idx["Criticality"]] != "K1":
            raise ValueError(f"Specific R3 variant must remain K1: {sku_id}")
        expected_lane = "C" if complexity == "C3" else "B"
        if row[idx["Current_Lane"]] != expected_lane or row[idx["Target_Lane_After_Evidence"]] != expected_lane:
            raise ValueError(f"Specific R3 variant lane is inconsistent: {sku_id}")
        if row[idx["Confidence"]] != "CONDITIONAL":
            raise ValueError(f"Specific R3 variant confidence must remain CONDITIONAL: {sku_id}")
        gates = {gate.strip() for gate in row[idx["Hard_Gates"]].split(";")}
        if not required_gates.issubset(gates):
            raise ValueError(f"Specific R3 variant must pass G0–G6: {sku_id}")
        expected_short = f"{complexity} · R3 · K1 · Lane {expected_lane} · CONDITIONAL"
        if row[idx["Preflight_Short"]] != expected_short:
            raise ValueError(f"Specific R3 variant compact preflight is inconsistent: {sku_id}")
        if row[idx["Preflight_Status"]] != "STRUCTURED SPECIFIC-VARIANT PREFLIGHT R3 — NOT PRODUCT RELEASE APPROVAL":
            raise ValueError(f"Specific R3 variant release disclaimer is missing: {sku_id}")
        if row[idx["Process_Profile_Refs"]] != "business/02-portfolio/research-r3-process-baseline.json":
            raise ValueError(f"Specific R3 variant exact-process reference is missing: {sku_id}")


def validate_readiness_advancement(
    rows: list[list[str]], research_ids: set[str], expected_product_count: int
) -> None:
    """Validate the complete all-idea/all-product advancement triage."""
    if not rows:
        raise ValueError(f"Readiness advancement source is empty: {READINESS_ADVANCEMENT_CSV}")
    header = rows[0]
    required = {
        "Record_Key", "Record_Type", "Record_ID", "Purpose_or_Intended_Use", "Purpose_Documented",
        "Current_Preflight_Short", "Wave", "Advancement_Potential", "Suggested_Target_R", "Bottleneck",
        "Exact_Next_Evidence", "Evidence_Boundary", "Assessment_Status",
    }
    missing = sorted(required.difference(header))
    if missing:
        raise ValueError(f"Readiness advancement source is missing columns: {', '.join(missing)}")
    expected_row_count = 1 + len(research_ids) + expected_product_count
    if len(rows) != expected_row_count or any(len(row) != len(header) for row in rows):
        raise ValueError(
            "Readiness advancement register must cover every research record and product directory"
        )
    idx = {name: header.index(name) for name in required}
    keys = [row[idx["Record_Key"]] for row in rows[1:]]
    if len(keys) != len(set(keys)):
        raise ValueError("Readiness advancement register has duplicate record keys")
    research_records = {row[idx["Record_ID"]] for row in rows[1:] if row[idx["Record_Type"]] == "RESEARCH_IDEA"}
    product_count = sum(row[idx["Record_Type"]] == "PRODUCT_DIRECTORY" for row in rows[1:])
    if research_records != research_ids or product_count != expected_product_count:
        raise ValueError("Readiness advancement register does not cover the complete research/product inventory")
    for row in rows[1:]:
        if row[idx["Purpose_Documented"]] != "YES" or len(row[idx["Purpose_or_Intended_Use"]].strip()) < 12:
            raise ValueError(f"Readiness advancement record lacks an explicit purpose: {row[idx['Record_Key']]}")
        if row[idx["Assessment_Status"]] != "COMPLETE PORTFOLIO TRIAGE — NOT RELEASE APPROVAL":
            raise ValueError(f"Readiness advancement disclaimer is missing: {row[idx['Record_Key']]}")
        for field in ("Current_Preflight_Short", "Wave", "Advancement_Potential", "Suggested_Target_R", "Bottleneck", "Exact_Next_Evidence", "Evidence_Boundary"):
            if not row[idx[field]].strip():
                raise ValueError(f"Readiness advancement field {field} is empty: {row[idx['Record_Key']]}")


def validate_research_priority(
    rows: list[list[str]],
    expected_ids: set[str],
    research_status: dict[str, dict[str, str]],
) -> None:
    """Fail closed when the generated implementation queue is stale or malformed."""
    if not rows:
        raise ValueError(f"Research priority source is empty: {RESEARCH_PRIORITY_CSV}")
    header = rows[0]
    required = {
        "Implementation_Order",
        "New_Build_Rank",
        "Next_Candidate_Rank",
        "SKU_ID",
        "Product",
        "Implementation_Status",
        "Mapped_Working_SKU",
        "Decision_Tier",
        "Priority_Score_0_100",
        "Creation_Effort_1_5",
        "Validation_Effort_1_5",
        "Commercial_Risk_1_5",
        "Trend_Score_0_100",
        "Estimated_Market_Fit_1_5",
        "Market_Evidence_Confidence_1_5",
        "Strategy_Fit_1_5",
        "AM_Differentiation_1_5",
        "Portfolio_Leverage_1_5",
        "Digital_First_Fit_1_5",
        "Economics_1_5",
        "Score_Status",
    }
    missing = sorted(required.difference(header))
    if missing:
        raise ValueError(f"Research priority source is missing columns: {', '.join(missing)}")
    expected_count = len(expected_ids)
    if len(rows) != expected_count + 1 or any(len(row) != len(header) for row in rows):
        raise ValueError(f"Research priority source must contain exactly {expected_count} complete idea rows")

    index = {name: header.index(name) for name in required}
    ids = [row[index["SKU_ID"]] for row in rows[1:]]
    if set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError("Research priority IDs do not match the combined research register")
    orders = [int(row[index["Implementation_Order"]]) for row in rows[1:]]
    if orders != list(range(1, expected_count + 1)):
        raise ValueError(f"Research priority implementation order must be sequential from 1 through {expected_count}")

    five_point_fields = [
        "Creation_Effort_1_5",
        "Validation_Effort_1_5",
        "Commercial_Risk_1_5",
        "Estimated_Market_Fit_1_5",
        "Market_Evidence_Confidence_1_5",
        "Strategy_Fit_1_5",
        "AM_Differentiation_1_5",
        "Portfolio_Leverage_1_5",
        "Digital_First_Fit_1_5",
        "Economics_1_5",
    ]
    for row in rows[1:]:
        sku_id = row[index["SKU_ID"]]
        priority = float(row[index["Priority_Score_0_100"]])
        if not 0 <= priority <= 100:
            raise ValueError(f"Research priority score is outside 0–100 for {sku_id}")
        for field in five_point_fields:
            value = int(row[index[field]])
            if not 1 <= value <= 5:
                raise ValueError(f"Research priority {field} is outside 1–5 for {sku_id}")
        expected_overlay = research_status.get(sku_id, {})
        expected_status = expected_overlay.get("Implementation_Status", "NOT_STARTED")
        expected_working_sku = expected_overlay.get("Mapped_Working_SKU", "")
        if row[index["Implementation_Status"]] != expected_status or row[index["Mapped_Working_SKU"]] != expected_working_sku:
            raise ValueError(f"Research priority implementation mapping is stale for {sku_id}")
        if row[index["Score_Status"]] != "PLANNING ESTIMATE — NOT RELEASE APPROVAL":
            raise ValueError(f"Research priority status disclaimer is missing for {sku_id}")


def add_research_overlay(
    rows: list[list[object]],
    sku_column: str,
    research_status: dict[str, dict[str, str]],
    interpretation: str,
) -> None:
    implementation_columns = [
        "Implementation_Status",
        "Mapped_Working_SKU",
        "Product_Package",
        "Model_Evidence",
        "Workflow_Stage",
        "Implementation_Updated",
        "Implementation_Notes",
    ]
    source_width = len(rows[0])
    sku_index = rows[0].index(sku_column)
    rows[0].extend(implementation_columns + ["Business_Workspace_Interpretation"])
    for row in rows[1:]:
        row.extend([""] * (source_width - len(row)))
        overlay = research_status.get(str(row[sku_index]), {})
        row.extend(
            [
                overlay.get("Implementation_Status", "NOT_STARTED"),
                overlay.get("Mapped_Working_SKU", ""),
                overlay.get("Product_Package", ""),
                overlay.get("Model_Evidence", ""),
                overlay.get("Workflow_Stage", "research-backlog"),
                overlay.get("Implementation_Updated", ""),
                overlay.get("Implementation_Notes", ""),
                interpretation,
            ]
        )


def indexed_rows(
    rows: list[list[object]], key_column: str
) -> dict[str, tuple[int, list[object]]]:
    """Return complete, padded rows keyed by one exact source column."""
    if not rows or key_column not in rows[0]:
        raise ValueError(f"Missing key column {key_column}")
    header = rows[0]
    key_index = header.index(key_column)
    result: dict[str, tuple[int, list[object]]] = {}
    for row_number, source_row in enumerate(rows[1:], start=2):
        row = list(source_row) + [""] * (len(header) - len(source_row))
        key = str(row[key_index])
        if not key or key in result:
            raise ValueError(f"Blank or duplicate {key_column}: {key}")
        result[key] = (row_number, row)
    return result


def namespaced_headers(header: list[object], prefix: str) -> list[str]:
    """Create stable unique raw-data headers without collapsing duplicate columns."""
    counts: dict[str, int] = {}
    result: list[str] = []
    for column_number, value in enumerate(header, start=1):
        base = str(value).strip() or f"Column_{column_number}"
        counts[base] = counts.get(base, 0) + 1
        occurrence = counts[base]
        suffix = "" if occurrence == 1 else f"__{occurrence}"
        result.append(f"{prefix}{base}{suffix}")
    return result


def portfolio_raw_headers(header: list[object], prefix: str) -> list[str]:
    """Keep audit data while exposing only one working-SKU identity column."""
    omitted = {"Record_ID", "Mapped_Working_SKU", "Working_SKU"}
    return [
        output_name
        for source_name, output_name in zip(header, namespaced_headers(header, prefix))
        if str(source_name) not in omitted
    ]


def source_value(header: list[object], row: list[object] | None, *names: str) -> object:
    """Return the first populated exact-name value from a source row."""
    if row is None:
        return ""
    for name in names:
        for index, header_value in enumerate(header):
            if header_value == name and index < len(row) and row[index] not in (None, ""):
                return row[index]
    return ""


def numeric_value(value: object) -> object:
    """Type known comparison fields as numbers so spreadsheet sorting is numeric."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    text = str(value).strip()
    if not text:
        return ""
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)", text):
        return float(text)
    return value


def build_unified_portfolio(
    portfolio: list[list[object]],
    product_preflights: list[list[object]],
    research_sources: list[tuple[str, list[list[object]], str]],
    research_priority: list[list[object]],
    research_economics: list[list[object]],
    readiness_advancement: list[list[object]],
) -> list[list[object]]:
    """Build one lossless, filterable product-and-idea register from stable keys."""
    product_by_path = indexed_rows(portfolio, "Source_Path")
    preflight_by_path = indexed_rows(product_preflights, "Product_Path")
    priority_by_sku = indexed_rows(research_priority, "SKU_ID")
    economics_by_sku = indexed_rows(research_economics, "SKU ID")
    advancement_by_key = indexed_rows(readiness_advancement, "Record_Key")

    idea_by_sku: dict[str, tuple[str, int, list[object], list[object]]] = {}
    idea_raw_columns: list[str] = []
    for sheet_name, rows, key_column in research_sources:
        raw_headers = portfolio_raw_headers(rows[0], "Idea__")
        for column in raw_headers:
            if column not in idea_raw_columns:
                idea_raw_columns.append(column)
        for sku_id, (row_number, row) in indexed_rows(rows, key_column).items():
            if sku_id in idea_by_sku:
                raise ValueError(f"Research idea appears in multiple source sheets: {sku_id}")
            idea_by_sku[sku_id] = (sheet_name, row_number, rows[0], row)

    advancement_header = readiness_advancement[0]
    advancement_rows = [row for _, row in advancement_by_key.values()]
    advancement_record_type_index = advancement_header.index("Record_Type")
    advancement_record_id_index = advancement_header.index("Record_ID")
    advancement_path_index = advancement_header.index("Product_Path")
    research_ids = {
        str(row[advancement_record_id_index])
        for row in advancement_rows
        if row[advancement_record_type_index] == "RESEARCH_IDEA"
    }
    product_paths = {
        str(row[advancement_path_index])
        for row in advancement_rows
        if row[advancement_record_type_index] == "PRODUCT_DIRECTORY"
    }
    if research_ids != set(idea_by_sku) or research_ids != set(priority_by_sku):
        raise ValueError("Unified portfolio research keys do not match idea and priority sources")
    if set(economics_by_sku) != {f"SKU-{number:03d}" for number in range(1, 101)}:
        raise ValueError("Unified portfolio economics source must contain SKU-001 through SKU-100")
    if set(product_by_path).difference(product_paths):
        raise ValueError("Product register contains a path absent from readiness advancement")
    if set(preflight_by_path) != product_paths:
        raise ValueError("Product preflight paths do not match readiness advancement")

    core_columns = [
        "Unified_Record_Key",
        "Record_Type",
        "Portfolio_Status",
        "Working_SKU",
        "Product",
        "Product_Family_or_Category",
        "Purpose_or_Customer_Job",
        "Product_Path",
        "Origin_Class",
        "Strategy_Fit",
        "Lifecycle_Stage",
        "Implementation_Status",
        "Workflow_Stage",
        "Design_Status",
        "Priority",
        "Decision_Tier",
        "Launch_Wave",
        "Commercial_Existing",
        "Digital_Offer_or_Mode",
        "Printed_Offer_or_Mode",
        "Website_Status",
        "Preflight_Short",
        "Complexity",
        "Readiness",
        "Criticality",
        "Current_Lane",
        "Target_Lane_After_Evidence",
        "Suggested_Target_R",
        "R_Scope",
        "R_Requirements",
        "R_Critical_Interfaces",
        "R_Manufacturing_Profile",
        "R_Verification",
        "PC_0_100",
        "Confidence",
        "Design_Release",
        "Preflight_Status",
        "Advancement_Potential",
        "Trend_Score_0_100",
        "Priority_Score_0_100",
        "Opportunity_Score_0_100",
        "Risk_Score_1_5",
        "Estimated_Market_Fit_1_5",
        "Market_Evidence_Confidence_1_5",
        "Creation_Effort_1_5",
        "Validation_Effort_1_5",
        "Commercial_Risk_1_5",
        "Strategy_Fit_1_5",
        "AM_Differentiation_1_5",
        "Portfolio_Leverage_1_5",
        "Digital_First_Fit_1_5",
        "Economics_1_5",
        "Max_L_mm",
        "Max_W_mm",
        "Max_H_mm",
        "Size_Class",
        "Part_Strategy",
        "Primary_Material",
        "Secondary_BOM",
        "Printer_Class",
        "Enclosure",
        "Supports",
        "Difficulty",
        "Mass_g",
        "Print_Time_h",
        "Hands_on_min",
        "Manufacturing_Economics",
        "Digital_Price_or_Band_EUR",
        "Printed_Price_Band_EUR",
        "Modeled_Local_COGS_EUR",
        "Minimum_Net_Price_EUR",
        "Recommended_Net_Price_EUR",
        "Recommended_Gross_Price_EUR",
        "Contribution_EUR",
        "Contribution_Margin",
        "Packaging_EUR",
        "Royalty_License_EUR",
        "Material_EUR_per_kg",
        "Material_Cost_EUR",
        "Machine_Cost_EUR",
        "Labor_Cost_EUR",
        "QA_Reserve_EUR",
        "Customer_Inputs",
        "Parametric_Variables",
        "Validation_or_Test",
        "Risk_or_Limit",
        "Source_IDs",
        "Next_Gate",
        "Bottleneck",
        "Exact_Next_Evidence",
        "Evidence_Boundary",
        "Notes",
    ]
    product_raw_columns = portfolio_raw_headers(portfolio[0], "Product__")
    preflight_raw_columns = portfolio_raw_headers(product_preflights[0], "Preflight__")
    priority_raw_columns = portfolio_raw_headers(research_priority[0], "Priority__")
    economics_raw_columns = portfolio_raw_headers(research_economics[0], "Economics__")
    advancement_raw_columns = portfolio_raw_headers(readiness_advancement[0], "Advancement__")
    raw_columns = (
        product_raw_columns
        + preflight_raw_columns
        + idea_raw_columns
        + priority_raw_columns
        + economics_raw_columns
        + advancement_raw_columns
    )
    output: list[list[object]] = [core_columns + raw_columns]

    def raw_block(
        source_header: list[object], source_row: list[object] | None, prefix: str, columns: list[str]
    ) -> list[object]:
        if source_row is None:
            return [""] * len(columns)
        values = dict(zip(namespaced_headers(source_header, prefix), source_row))
        return [values.get(column, "") for column in columns]

    for _, advancement_row in advancement_by_key.values():
        advancement = dict(zip(advancement_header, advancement_row))
        record_type = str(advancement["Record_Type"])
        record_id = str(advancement["Record_ID"])
        product_path = str(advancement["Product_Path"])

        product_row: list[object] | None = None
        if product_path in product_by_path:
            _, product_row = product_by_path[product_path]
        preflight_row: list[object] | None = None
        if product_path in preflight_by_path:
            _, preflight_row = preflight_by_path[product_path]

        idea_header: list[object] = []
        idea_row: list[object] | None = None
        if record_id in idea_by_sku:
            _, _, idea_header, idea_row = idea_by_sku[record_id]

        priority_row: list[object] | None = None
        if record_id in priority_by_sku:
            _, priority_row = priority_by_sku[record_id]
        economics_row: list[object] | None = None
        if record_id in economics_by_sku:
            _, economics_row = economics_by_sku[record_id]

        product_header = portfolio[0]
        preflight_header = product_preflights[0]
        priority_header = research_priority[0]
        economics_header = research_economics[0]

        lifecycle = source_value(product_header, product_row, "Lifecycle_Stage")
        implementation = source_value(priority_header, priority_row, "Implementation_Status")
        workflow = source_value(idea_header, idea_row, "Workflow_Stage")
        design_status = source_value(idea_header, idea_row, "Design_Status", "Design Status")
        working_sku = source_value(product_header, product_row, "Working_SKU") or record_id
        if record_type == "PRODUCT_DIRECTORY":
            portfolio_status = lifecycle or "PRODUCT DIRECTORY — NOT IN PRODUCT REGISTER"
        else:
            if implementation == "MODEL_EXISTS" and workflow and workflow != "research-backlog":
                portfolio_status = str(workflow).replace("-", " ")
            else:
                portfolio_status = "P0 Research idea"

        confidence = source_value(idea_header, idea_row, "Confidence")
        if not confidence:
            compact_parts = str(advancement["Current_Preflight_Short"]).split(" · ")
            confidence = compact_parts[-1] if len(compact_parts) == 5 else ""

        canonical = [
            advancement["Record_Key"],
            record_type,
            portfolio_status,
            working_sku,
            source_value(product_header, product_row, "Product_or_Model")
            or source_value(idea_header, idea_row, "Product")
            or advancement["Product"],
            source_value(product_header, product_row, "Category")
            or source_value(idea_header, idea_row, "Product_Family", "Product Family"),
            advancement["Purpose_or_Intended_Use"],
            product_path,
            source_value(product_header, product_row, "Origin_Class"),
            source_value(product_header, product_row, "Strategy_Fit")
            or source_value(idea_header, idea_row, "Strategy_Fit"),
            lifecycle,
            implementation,
            workflow,
            design_status,
            source_value(product_header, product_row, "Priority"),
            source_value(priority_header, priority_row, "Decision_Tier"),
            source_value(idea_header, idea_row, "Launch_Wave", "Launch Wave"),
            source_value(product_header, product_row, "Commercial_Existing"),
            source_value(product_header, product_row, "Digital_Offer")
            or source_value(idea_header, idea_row, "Offer_Mode"),
            source_value(product_header, product_row, "Printed_Offer")
            or source_value(idea_header, idea_row, "Offer_Mode"),
            source_value(product_header, product_row, "Website_Status"),
            advancement["Current_Preflight_Short"],
            advancement["Complexity"],
            advancement["Readiness"],
            advancement["Criticality"],
            advancement["Current_Lane"],
            source_value(preflight_header, preflight_row, "Target_Lane_After_Evidence")
            or source_value(priority_header, priority_row, "Preflight_Target_Lane_After_Evidence"),
            advancement["Suggested_Target_R"],
            source_value(idea_header, idea_row, "R_Scope"),
            source_value(idea_header, idea_row, "R_Requirements"),
            source_value(idea_header, idea_row, "R_Critical_Interfaces"),
            source_value(idea_header, idea_row, "R_Manufacturing_Profile"),
            source_value(idea_header, idea_row, "R_Verification"),
            numeric_value(
                source_value(preflight_header, preflight_row, "PC_0_100")
                or source_value(idea_header, idea_row, "PC_0_100")
            ),
            confidence,
            source_value(preflight_header, preflight_row, "Design_Release")
            or source_value(idea_header, idea_row, "Design_Release"),
            source_value(idea_header, idea_row, "Preflight_Status")
            or source_value(priority_header, priority_row, "Preflight_Estimate_Status"),
            advancement["Advancement_Potential"],
            numeric_value(
                advancement["Trend_Score_0_100"]
                or source_value(priority_header, priority_row, "Trend_Score_0_100")
                or source_value(idea_header, idea_row, "Trend_Score_0_100", "Trend Score")
            ),
            numeric_value(
                advancement["Priority_Score_0_100"]
                or source_value(priority_header, priority_row, "Priority_Score_0_100")
            ),
            numeric_value(source_value(idea_header, idea_row, "Opportunity_Score", "Opportunity Score")),
            numeric_value(source_value(idea_header, idea_row, "Risk_Score", "Risk Score")),
            numeric_value(source_value(priority_header, priority_row, "Estimated_Market_Fit_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Market_Evidence_Confidence_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Creation_Effort_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Validation_Effort_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Commercial_Risk_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Strategy_Fit_1_5")),
            numeric_value(source_value(priority_header, priority_row, "AM_Differentiation_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Portfolio_Leverage_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Digital_First_Fit_1_5")),
            numeric_value(source_value(priority_header, priority_row, "Economics_1_5")),
            numeric_value(source_value(idea_header, idea_row, "Max_L_mm", "Max L mm")),
            numeric_value(source_value(idea_header, idea_row, "Max_W_mm", "Max W mm")),
            numeric_value(source_value(idea_header, idea_row, "Max_H_mm", "Max H mm")),
            source_value(idea_header, idea_row, "Size_Class", "Size Class")
            or source_value(economics_header, economics_row, "Size Class"),
            source_value(idea_header, idea_row, "Part_Strategy", "Part Strategy"),
            source_value(idea_header, idea_row, "Primary_Material", "Primary Material")
            or source_value(economics_header, economics_row, "Material"),
            source_value(idea_header, idea_row, "Secondary_BOM", "Secondary BOM"),
            source_value(idea_header, idea_row, "Printer_Class", "Printer Class"),
            source_value(idea_header, idea_row, "Enclosure"),
            source_value(idea_header, idea_row, "Supports"),
            source_value(idea_header, idea_row, "Difficulty"),
            numeric_value(source_value(economics_header, economics_row, "Mass g")),
            numeric_value(source_value(economics_header, economics_row, "Print Time h")),
            numeric_value(source_value(economics_header, economics_row, "Hands-on min")),
            source_value(idea_header, idea_row, "Manufacturing Economics"),
            source_value(idea_header, idea_row, "Digital_Price_Band_EUR", "Digital SKU Price €")
            or source_value(economics_header, economics_row, "Digital SKU Price €"),
            source_value(idea_header, idea_row, "Printed_Price_Band_EUR"),
            numeric_value(
                source_value(idea_header, idea_row, "Modeled Local COGS €")
                or source_value(economics_header, economics_row, "Total Local COGS €")
            ),
            numeric_value(source_value(economics_header, economics_row, "Minimum Net Price €")),
            numeric_value(source_value(economics_header, economics_row, "Recommended Net Price €")),
            numeric_value(
                source_value(idea_header, idea_row, "Recommended Gross Price €")
                or source_value(economics_header, economics_row, "Recommended Gross Price €")
            ),
            numeric_value(source_value(economics_header, economics_row, "Contribution €")),
            numeric_value(
                source_value(idea_header, idea_row, "Contribution Margin")
                or source_value(economics_header, economics_row, "Contribution Margin")
            ),
            numeric_value(source_value(economics_header, economics_row, "Packaging €")),
            numeric_value(source_value(economics_header, economics_row, "Royalty / License €")),
            numeric_value(source_value(economics_header, economics_row, "Material €/kg")),
            numeric_value(source_value(economics_header, economics_row, "Material Cost €")),
            numeric_value(source_value(economics_header, economics_row, "Machine Cost €")),
            numeric_value(source_value(economics_header, economics_row, "Labor Cost €")),
            numeric_value(source_value(economics_header, economics_row, "QA Reserve €")),
            source_value(idea_header, idea_row, "Customer_Inputs", "Customer Inputs"),
            source_value(idea_header, idea_row, "Parametric_Variables", "Parametric Variables"),
            source_value(idea_header, idea_row, "Validation / Test", "Verification_Plan"),
            source_value(idea_header, idea_row, "Risk_or_Limit", "Intended-use Limits"),
            source_value(idea_header, idea_row, "Source_IDs", "Source IDs"),
            source_value(product_header, product_row, "Next_Gate")
            or source_value(idea_header, idea_row, "Next_Gate", "Next Gate"),
            advancement["Bottleneck"],
            advancement["Exact_Next_Evidence"],
            advancement["Evidence_Boundary"],
            source_value(product_header, product_row, "Notes")
            or source_value(idea_header, idea_row, "Notes"),
        ]
        if len(canonical) != len(core_columns):
            raise AssertionError("Unified portfolio canonical column count mismatch")

        idea_values = raw_block(idea_header, idea_row, "Idea__", idea_raw_columns)
        output.append(
            canonical
            + raw_block(product_header, product_row, "Product__", product_raw_columns)
            + raw_block(preflight_header, preflight_row, "Preflight__", preflight_raw_columns)
            + idea_values
            + raw_block(priority_header, priority_row, "Priority__", priority_raw_columns)
            + raw_block(economics_header, economics_row, "Economics__", economics_raw_columns)
            + raw_block(advancement_header, advancement_row, "Advancement__", advancement_raw_columns)
        )

    expected_output_count = 1 + len(idea_by_sku) + len(product_paths)
    if len(output) != expected_output_count or any(len(row) != len(output[0]) for row in output):
        raise ValueError("Unified portfolio must contain every complete, width-stable research and product record")
    working_sku_index = output[0].index("Working_SKU")
    working_skus = [str(row[working_sku_index]) for row in output[1:]]
    if any(not sku for sku in working_skus) or len(working_skus) != len(set(working_skus)):
        raise ValueError("Unified portfolio Working_SKU values must be populated and unique")
    return output


def read_xlsx_sheet(path: Path, sheet_name: str) -> list[list[object]]:
    """Read cached/constant values from a simple XLSX sheet without third-party packages."""
    ns = {"m": MAIN_NS, "r": REL_NS}
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", ns):
                shared.append("".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        target = None
        for sheet in workbook.find("m:sheets", ns) or []:
            if sheet.attrib.get("name") == sheet_name:
                target = targets[sheet.attrib[f"{{{REL_NS}}}id"]].lstrip("/")
                break
        if target is None:
            raise KeyError(f"Sheet not found: {sheet_name}")
        if not target.startswith("xl/"):
            target = posixpath.normpath("xl/" + target)
        root = ET.fromstring(archive.read(target))
        result: list[list[object]] = []
        for row in root.findall(".//m:sheetData/m:row", ns):
            values: dict[int, object] = {}
            for cell in row.findall("m:c", ns):
                reference = cell.attrib.get("r", "A1")
                letters = re.match(r"[A-Z]+", reference)
                index = 0
                for char in letters.group(0) if letters else "A":
                    index = index * 26 + ord(char) - 64
                cell_type = cell.attrib.get("t")
                value_node = cell.find("m:v", ns)
                if cell_type == "inlineStr":
                    value = "".join(node.text or "" for node in cell.findall(".//m:t", ns))
                elif value_node is None:
                    value = ""
                elif cell_type == "s":
                    value = shared[int(value_node.text or 0)]
                elif cell_type == "b":
                    value = "Yes" if value_node.text == "1" else "No"
                else:
                    raw = value_node.text or ""
                    try:
                        value = float(raw) if "." in raw else int(raw)
                    except ValueError:
                        value = raw
                values[index] = value
            if values:
                result.append([values.get(i, "") for i in range(1, max(values) + 1)])
        return result


def col_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def style_for(value: object, row_index: int) -> int:
    if row_index == 1:
        return 1
    text = str(value).upper()
    if text in {"COMPLETE", "YES", "PASS", "P7 LIVE", "P6 STAGED", "P5 COMMERCIAL RELEASE"} or text.startswith(("0 FINISH", "1 NEXT")):
        return 3
    if "BLOCK" in text or text in {"EXCLUDED", "VERY HIGH"}:
        return 5
    if text.startswith(("P0 ", "P1 ", "2 VALIDATE", "4 HOLD")) or text in {"HOLD", "UNKNOWN", "NOT STARTED", "NOT_STARTED"}:
        return 4
    return 6


def cell_xml(row: int, col: int, value: object) -> str:
    ref = f"{col_name(col)}{row}"
    style = style_for(value, row)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
    text = escape("" if value is None else str(value))
    return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'


def sheet_xml(rows: list[list[object]], freeze_columns: int = 0) -> str:
    row_count = max(1, len(rows))
    col_count = max((len(row) for row in rows), default=1)
    max_lengths = [8] * col_count
    for row in rows[:250]:
        for idx, value in enumerate(row):
            sample = max((len(line) for line in str(value).splitlines()), default=0)
            max_lengths[idx] = max(max_lengths[idx], sample)
    widths = []
    for idx, length in enumerate(max_lengths, start=1):
        width = min(max(length + 2, 10), 48)
        widths.append(f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>')
    xml_rows = []
    for row_idx, values in enumerate(rows, start=1):
        cells = "".join(cell_xml(row_idx, col_idx, value) for col_idx, value in enumerate(values, start=1))
        height = ' ht="34" customHeight="1"' if row_idx == 1 else ""
        xml_rows.append(f'<row r="{row_idx}"{height}>{cells}</row>')
    last = f"{col_name(col_count)}{row_count}"
    auto_filter = f'<autoFilter ref="A1:{last}"/>' if len(rows) > 1 else ""
    if freeze_columns:
        top_left = f"{col_name(freeze_columns + 1)}2"
        pane = (
            f'<pane xSplit="{freeze_columns}" ySplit="1" topLeftCell="{top_left}" '
            'activePane="bottomRight" state="frozen"/>'
        )
    else:
        pane = '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<dimension ref="A1:{last}"/>'
        f'<sheetViews><sheetView workbookViewId="0">{pane}</sheetView></sheetViews>'
        '<sheetFormatPr defaultRowHeight="18"/>'
        f'<cols>{"".join(widths)}</cols><sheetData>{"".join(xml_rows)}</sheetData>{auto_filter}'
        '<pageMargins left="0.25" right="0.25" top="0.5" bottom="0.5" header="0.2" footer="0.2"/>'
        '</worksheet>'
    )


def main() -> None:
    portfolio = read_csv(PORTFOLIO_CSV)
    product_preflight_records = load_product_preflight_records()
    add_portfolio_preflight(portfolio, product_preflight_records)
    all_product_preflights = product_preflight_sheet(product_preflight_records)
    tasks = read_csv(TASKS_CSV)
    header = portfolio[0]
    role_index = header.index("Initial_Portfolio_Role")
    initial = [header] + [row for row in portfolio[1:] if row[role_index].startswith("Initial launch")]

    stages = [
        ["Stage", "Meaning", "Commercially existing?", "Public sale"],
        ["P0 Idea", "Research concept only; no controlled product source", "No", "No"],
        ["P1 Model present", "Local source or mesh exists; quality/rights may be unknown", "No", "No"],
        ["P2 Digital candidate", "Controlled revision and digital geometry evidence", "No", "No"],
        ["P3 Physical prototype", "Slicer/profile and at least one exact-revision physical prototype/coupon", "No", "No"],
        ["P4 Product qualified", "Physical, rights, safety and claims evidence complete for scope", "No", "No"],
        ["P5 Commercial release", "Signed release/customer/economics/media package", "Yes", "Staging only"],
        ["P6 Staged", "Exact release and transaction/fulfillment flow passed in staging", "Yes", "Staging only"],
        ["P7 Live", "Production release approved and monitored", "Yes", "Yes"],
        ["HOLD", "Deferred/off-strategy/disproportionate risk", "No", "No"],
        ["EXCLUDED", "Forbidden input, including external-directory downloads", "No", "No"],
    ]

    external_paths = [
        "research/third-party/art-models",
        "products/toys-games/mm-toy-001-rubber-ball-toy-popper/external",
        "research/third-party/boats",
        "products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray/external",
        "products/printer-workshop/mm-tool-003-kobra3max-camera-arm/external",
        "research/third-party/clips/external",
        "research/third-party/dough-cutters/external",
        "research/third-party/fidgets/external",
        "research/third-party/gravity-knife-fidgets/external",
        "research/third-party/music-boxes/external",
        "research/third-party/organization-storage",
        "research/third-party/puzzles",
        "research/third-party/shoes/external",
        "research/third-party/stamps/external",
        "products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf/external",
    ]
    exclusions = [["Path", "Status", "Reason", "Re-entry rule"]] + [
        [path, "EXCLUDED", "User-defined unknown-source download; never a portfolio candidate", "New documented source acquisition plus explicit business decision"]
        for path in external_paths
    ]

    research_items = [
        (1, "Personalized name/word bookends", 4.85, "Initial", "MM-PER-001"),
        (2, "Shelf-fit bins", 4.70, "Initial", "MM-ORG-002"),
        (3, "Personalized entryway panel", 4.55, "Later", "Wall/mount gate"),
        (4, "Modular utility-rail modules", 4.55, "Later", "Interface/load gate"),
        (5, "Narrow gap pullout cart", 4.35, "Later", "Large printed/assembly gate"),
        (6, "Headboard organizer", 4.35, "Later", "Mount/retention gate"),
        (7, "Windowsill shelf", 4.35, "Later", "Load/heat/fit gate"),
        (8, "System-furniture shelf add-ons", 4.30, "Next", "Physical furniture-revision fit"),
        (9, "Under-bed boxes", 4.15, "Later", "Large-volume/printed fulfillment"),
        (10, "Wardrobe interior", 4.15, "Later", "System/fit expansion"),
        (11, "Balcony table", 4.15, "Hold", "Structural/weather gate"),
        (12, "Over-toilet shelf", 4.05, "Hold", "Existing digital candidate; structural gate"),
        (13, "Decorative charging station", 4.05, "Later", "Electrical/device heat boundary"),
        (14, "Radiator/window shelf", 4.00, "Hold", "Heat/load/mount gate"),
        (15, "Washing-machine shelf", 3.95, "Hold", "Vibration/load/tip gate"),
        (16, "Plant wall shelf", 3.90, "Hold", "Wall/load/water gate"),
        (17, "Sloped-ceiling shoe rack", 3.85, "Later", "Large modular system"),
        (18, "Drill-free bathroom organizer", 3.85, "Later", "Wet retention/adhesive gate"),
        (19, "Over-door organizer", 3.70, "Later", "Door fit/load/surface gate"),
        (20, "Wall folding desk", 3.65, "Hold", "Structural hardware and wall gate"),
    ]
    research = [["Research_Rank", "Concept", "Research_Score", "Timeline", "Decision_or_Gate"]] + [list(row) for row in research_items]

    legacy_product_matrix = read_xlsx_sheet(RESEARCH_WORKBOOK, "Product Matrix")
    legacy_unit_economics = read_xlsx_sheet(RESEARCH_WORKBOOK, "Unit Economics")
    legacy_family_strategy = read_xlsx_sheet(RESEARCH_WORKBOOK, "Family Strategy")
    legacy_sources = read_xlsx_sheet(RESEARCH_WORKBOOK, "Sources")
    additional_research = read_csv(RESEARCH_ADDITIONS_CSV)
    structured_research = read_csv(RESEARCH_ADDITIONS_2_CSV)
    specific_r3_variants = read_csv(RESEARCH_R3_VARIANTS_CSV)
    readiness_advancement = read_csv(READINESS_ADVANCEMENT_CSV)
    additional_sources = read_csv(RESEARCH_ADDITION_SOURCES_CSV)
    research_status = read_research_status(RESEARCH_STATUS_CSV)
    validate_research_additions(additional_research, legacy_product_matrix, portfolio, research_status)
    validate_structured_research_additions(structured_research, legacy_product_matrix, additional_research, portfolio)
    legacy_sku_index = legacy_product_matrix[0].index("SKU ID")
    additional_sku_index = additional_research[0].index("SKU_ID")
    structured_sku_index = structured_research[0].index("SKU_ID")
    prior_research_ids = {
        str(row[legacy_sku_index]) for row in legacy_product_matrix[1:]
    } | {
        str(row[additional_sku_index]) for row in additional_research[1:]
    } | {
        str(row[structured_sku_index]) for row in structured_research[1:]
    }
    occupied_product_names = {
        normalize_name(row[legacy_product_matrix[0].index("Product")]) for row in legacy_product_matrix[1:]
    } | {
        normalize_name(row[additional_research[0].index("Product")]) for row in additional_research[1:]
    } | {
        normalize_name(row[structured_research[0].index("Product")]) for row in structured_research[1:]
    } | {
        normalize_name(row[portfolio[0].index("Product_or_Model")]) for row in portfolio[1:]
    }
    validate_specific_r3_variants(specific_r3_variants, prior_research_ids, occupied_product_names)
    if additional_sources[0] != legacy_sources[0]:
        raise ValueError("Additional research-source schema does not match the retained source register")
    legacy_source_ids = {str(row[0]) for row in legacy_sources[1:]}
    additional_source_ids = [str(row[0]) for row in additional_sources[1:]]
    if len(additional_source_ids) != len(set(additional_source_ids)) or legacy_source_ids.intersection(additional_source_ids):
        raise ValueError("Additional research-source IDs are duplicate or collide with the retained source register")
    research_sources = legacy_sources + additional_sources[1:]
    valid_source_ids = {str(row[0]) for row in research_sources[1:]}
    used_source_ids: set[str] = set()
    for research_rows in (additional_research, structured_research, specific_r3_variants):
        source_index = research_rows[0].index("Source_IDs")
        used_source_ids.update(
            source_id.strip()
            for row in research_rows[1:]
            for source_id in str(row[source_index]).split(";")
            if source_id.strip()
        )
    unknown_source_ids = sorted(used_source_ids.difference(valid_source_ids))
    if unknown_source_ids:
        raise ValueError(f"Research additions reference unknown source IDs: {', '.join(unknown_source_ids)}")
    research_priority = read_csv(RESEARCH_PRIORITY_CSV)
    variant_sku_index = specific_r3_variants[0].index("SKU_ID")
    combined_research_ids = prior_research_ids | {
        str(row[variant_sku_index]) for row in specific_r3_variants[1:]
    }
    validate_research_priority(research_priority, combined_research_ids, research_status)
    validate_readiness_advancement(
        readiness_advancement, combined_research_ids, len(product_preflight_records)
    )
    research_preflight = read_research_preflight(RESEARCH_PREFLIGHT_CSV, combined_research_ids)
    add_research_overlay(
        legacy_product_matrix,
        "SKU ID",
        research_status,
        "Research hypothesis; implementation fields are controlled by research-ideas-implementation.csv",
    )
    add_research_overlay(
        additional_research,
        "SKU_ID",
        research_status,
        "New research hypothesis checked 2026-08-27; not a selected, qualified or released product",
    )
    add_research_overlay(
        structured_research,
        "SKU_ID",
        research_status,
        "Trend-screened research hypothesis checked 2026-08-31; structured R2 concept preflight, not a selected, qualified or released product",
    )
    add_research_overlay(
        specific_r3_variants,
        "SKU_ID",
        research_status,
        "Named-interface child checked 2026-08-31; R3 nominal design inputs only, not physical qualification, demand proof or release",
    )
    add_research_preflight(legacy_product_matrix, "SKU ID", research_preflight)
    add_research_preflight(additional_research, "SKU_ID", research_preflight)
    add_research_preflight(structured_research, "SKU_ID", research_preflight)
    add_research_preflight(specific_r3_variants, "SKU_ID", research_preflight)
    add_research_preflight(research_priority, "SKU_ID", research_preflight)
    for imported in (legacy_unit_economics, legacy_family_strategy):
        imported[0].append("Business_Workspace_Interpretation")
        for row in imported[1:]:
            row.extend([""] * (len(imported[0]) - 1 - len(row)))
            row.append("Research hypothesis only; not an existing, qualified, staged or live product")

    unified_portfolio = build_unified_portfolio(
        portfolio,
        all_product_preflights,
        [
            ("Research Ideas 100", legacy_product_matrix, "SKU ID"),
            ("Research Ideas +100", additional_research, "SKU_ID"),
            ("Research Ideas +200", structured_research, "SKU_ID"),
            ("Research Variants R3", specific_r3_variants, "SKU_ID"),
        ],
        research_priority,
        legacy_unit_economics,
        readiness_advancement,
    )

    stages_present: dict[str, int] = {}
    for row in portfolio[1:]:
        stage = row[header.index("Lifecycle_Stage")]
        stages_present[stage] = stages_present.get(stage, 0) + 1
    additional_strategy_index = additional_research[0].index("Strategy_Fit")
    structured_strategy_index = structured_research[0].index("Strategy_Fit")
    variant_strategy_index = specific_r3_variants[0].index("Strategy_Fit")
    additional_core_count = sum(
        1 for row in additional_research[1:] if str(row[additional_strategy_index]).startswith("Core")
    ) + sum(
        1 for row in structured_research[1:] if str(row[structured_strategy_index]).startswith("Core")
    ) + sum(
        1 for row in specific_r3_variants[1:] if str(row[variant_strategy_index]).startswith("Core")
    )
    priority_header = research_priority[0]
    priority_tier_index = priority_header.index("Decision_Tier")
    next_rank_index = priority_header.index("Next_Candidate_Rank")
    priority_sku_index = priority_header.index("SKU_ID")
    priority_product_index = priority_header.index("Product")
    finish_current_count = sum(
        1 for row in research_priority[1:] if row[priority_tier_index].startswith("0 FINISH")
    )
    next_candidate_rows = [
        row for row in research_priority[1:] if row[priority_tier_index].startswith("1 NEXT")
    ]
    first_new_candidate = next(
        row for row in next_candidate_rows if row[next_rank_index] == "1"
    )
    linked_preflight_count = sum(
        1
        for estimate in research_preflight.values()
        if estimate["Estimate_Status"].startswith("LINKED CURRENT")
    )
    structured_preflight_count = sum(
        1
        for estimate in research_preflight.values()
        if estimate["Estimate_Status"].startswith("STRUCTURED RESEARCH PREFLIGHT R2")
    )
    specific_r3_preflight_count = sum(
        1
        for estimate in research_preflight.values()
        if estimate["Estimate_Status"].startswith("STRUCTURED SPECIFIC-VARIANT PREFLIGHT R3")
    )
    preliminary_preflight_count = (
        len(research_preflight) - linked_preflight_count - structured_preflight_count - specific_r3_preflight_count
    )
    structured_trend_index = structured_research[0].index("Trend_Score_0_100")
    structured_trend_scores = [float(row[structured_trend_index]) for row in structured_research[1:]]
    variant_complexity_index = specific_r3_variants[0].index("Complexity")
    variant_complexity_counts = {
        complexity: sum(1 for row in specific_r3_variants[1:] if row[variant_complexity_index] == complexity)
        for complexity in ("C1", "C2", "C3")
    }
    stale_audit_scorecards = sum(not bool(record["audit_scorecard_match"]) for record in product_preflight_records)
    summary = [
        ["Metric", "Value", "Interpretation"],
        ["Review date", "2026-08-31", "Repository-evidence snapshot"],
        ["Unified portfolio records", len(unified_portfolio) - 1, f"Single filterable list: {len(product_preflight_records)} product directories plus {len(combined_research_ids)} planned products and research ideas; every row has one unique Working_SKU"],
        ["Curated product source records", len(portfolio) - 1, "Existing product-family source is retained in product-portfolio.csv; no duplicate Product Register worksheet"],
        ["Product directories with documented preflight", len(product_preflight_records), "Every current products/<family>/<product> directory; exact C/R/K/lane/confidence and source paths are joined into Portfolio"],
        ["Stale aggregate-audit scorecards", stale_audit_scorecards, "Live product preflight is used; any mismatch is exposed in Portfolio audit columns and the dated aggregate audit must be refreshed separately"],
        ["Curated product rows with documented preflight", len(portfolio) - 1, "Exact current product scorecards are joined from their version-controlled sources into Portfolio"],
        ["Product directories with explicit purpose", sum(1 for record in product_preflight_records if record["purpose_path"].is_file()), "Purpose paths are listed beside every product preflight"],
        ["Initial launch SKUs", len(initial) - 1, "Fixed target scope"],
        ["Legacy research concepts retained", len(legacy_product_matrix) - 1, "Research sheet now carries a controlled implementation overlay"],
        ["First research addendum", len(additional_research) - 1, "Append-only P0 hypotheses; preserved separately from the product portfolio"],
        ["Trend-screened research addendum", len(structured_research) - 1, "SKU-201–300; each has explicit purpose, directional trend >70 and a structured concept preflight"],
        ["Named-interface R3 variants", len(specific_r3_variants) - 1, "SKU-301–314; separate children with cited E3 nominals and an exact research process baseline; generic parents remain unchanged"],
        ["R3 variant complexity split", f"C1={variant_complexity_counts['C1']}; C2={variant_complexity_counts['C2']}; C3={variant_complexity_counts['C3']}", "R3 is nominal design-input maturity, not physical qualification or demand proof"],
        ["Trend-screened score range", f"{min(structured_trend_scores):g}–{max(structured_trend_scores):g}", "Directional 0–100 planning score; not validated demand"],
        ["Additional ideas at core/core-adjacent fit", additional_core_count, "Research allocation only; active development remains constrained by the 70% core-capacity rule"],
        ["Total research concepts", len(combined_research_ids), "Original 300 plus 14 append-only named-interface variants"],
        ["Addendum scoring", "Opportunity/trend 0–100; risk 1–5", "Scores and price bands prioritize tests only; they are not approved demand, margin or release claims"],
        ["Research source records", len(research_sources) - 1, "Source records support direction only; per-concept demand validation is still required"],
        ["Research ideas with mapped models", sum(1 for row in research_status.values() if row.get("Implementation_Status") == "MODEL_EXISTS"), "Physical validation remains a later human gate"],
        ["Ranked research ideas", len(research_priority) - 1, "Comparable implementation planning queue; not release approval"],
        ["Research ideas linked to current product preflights", linked_preflight_count, "Exact scorecard copied from the mapped product; still not release approval"],
        ["Research ideas with structured R2 concept preflights", structured_preflight_count, "SKU-201–300: K1 and C<=2; current Lane E while the exact manufacturing-process gate remains open"],
        ["Research ideas with specific R3 preflights", specific_r3_preflight_count, "Named-interface children only; all are CONDITIONAL and require independent coupon/device/host validation"],
        ["Research ideas with preliminary preflight bands", preliminary_preflight_count, "C and K are planning bands; R0\u2013R1 and current Lane E remain until interface/process/test evidence exists"],
        ["Readiness advancement records", len(readiness_advancement) - 1, f"Complete triage for {len(combined_research_ids)} research ideas plus {len(product_preflight_records)} product directories, with purpose, bottleneck and exact next evidence"],
        ["Research target lane", "Separate planning field", "Expected design path after evidence closure; it never replaces the current lane or a release gate"],
        ["Finish-current research models", finish_current_count, "Close slicer, physical, rights and commercial evidence before expanding CAD work"],
        ["Gated next-candidate pool", len(next_candidate_rows), "Candidate pool only; demand-test and select at most one new CAD workstream"],
        ["First gated new candidate", f"{first_new_candidate[priority_sku_index]} — {first_new_candidate[priority_product_index]}", "Highest-ranked unstarted idea passing effort, validation, risk, strategy, market-fit and evidence-confidence gates"],
        ["Commercially existing P5+", 0, "No product may be sold yet"],
        ["Staged P6", 0, "No real release staged"],
        ["Live P7", 0, "No live product"],
        ["External directories excluded", len(external_paths), "Never included in portfolio candidates"],
        ["P0 ideas", stages_present.get("P0 Idea", 0), "CAD not yet controlled"],
        ["P1 model present", stages_present.get("P1 Model present", 0), "Model exists but evidence is incomplete"],
        ["P2 digital candidates", stages_present.get("P2 Digital candidate", 0), "Digital evidence does not equal a product release"],
        ["Launch recommendation", "Germany digital-only", "At least one fixed safe-core P5 3MF release; three preferred; print/configuration gated later"],
    ]

    preflight_legend = [
        ["Field", "Meaning", "Portfolio use"],
        ["Compact form", "C# \u00b7 R# \u00b7 K# \u00b7 Lane X \u00b7 CONFIDENCE", "Exact current scorecard for product preflights; bands are allowed only for explicitly preliminary research estimates"],
        ["C0\u2013C5", "Intrinsic product/design complexity", "Never average with readiness, criticality or market potential"],
        ["R0\u2013R5", "Minimum maturity of scope, requirements, critical interfaces, process and verification", "Legacy concepts remain R0\u2013R1; SKU-201–300 reach concept-level R2; only separate SKU-301–314 named-interface children reach nominal R3"],
        ["K0\u2013K4", "Credible failure consequence and required rigor", "A research K band is a conservative proxy, not a safety qualification"],
        ["Lane A\u2013E", "Currently permitted workflow", "R<=1 or a hard-gate failure forces current Lane E"],
        ["Target lane after evidence", "Likely design workflow after readiness and hard gates are sufficient", "Planning aid only; does not override current Lane E, HOLD or CONCEPT_ONLY"],
        ["Confidence", "Qualitative workflow confidence", "No numerical success probability is inferred"],
        ["Linked current product preflight", "Research idea maps to an existing Working_SKU", "Exact current product scorecard and source path are shown; not release approval"],
        ["Structured R2 research preflight", "SKU-201–300 has a scored PC model and documented R2 basis", "K1 and C<=2 were enforced; current Lane E and CONCEPT_ONLY remain because exact process and variant evidence are open"],
        ["Specific R3 variant preflight", "SKU-301–314 is a separate named-interface child with cited E3 nominals and a pinned exact research process", "Generic parents do not inherit R3; confidence remains CONDITIONAL and a physical coupon/exact item or host is the next gate"],
        ["Preliminary idea estimate", "No mapped current product preflight", "C band uses creation/validation planning effort; K band uses the research-risk proxy; R0\u2013R1 and Lane E are fixed until evidence exists"],
        ["Market potential", "Opportunity and market-fit fields in the research register", "Keep separate from C/R/K/lane; compare side by side in Implementation Priority"],
        ["Update rule", "Regenerate after product-preflight, implementation mapping, source, variant or research-priority changes", "Run the R3 variant, priority, preflight and advancement builders, then build_product_workbook.py"],
        ["Product source", "products/*/*/preflight/preflight-result.json", "Validated project-level source of truth"],
        ["Research source", "research-idea-preflight-estimates.csv", "Version-controlled 314-row planning overlay"],
        ["Advancement source", "readiness-advancement-register.csv", f"Complete {len(combined_research_ids) + len(product_preflight_records)}-row triage: {len(combined_research_ids)} research ideas plus {len(product_preflight_records)} product directories"],
    ]

    sheets = [
        ("Summary", summary),
        ("Portfolio", unified_portfolio),
        ("Stage Definitions", stages),
        ("Research Families", legacy_family_strategy),
        ("Research Sources", research_sources),
        ("Preflight Legend", preflight_legend),
    ]

    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    for idx in range(1, len(sheets) + 1):
        content_types.append(f'<Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
    content_types.append('</Types>')

    workbook_sheets = "".join(
        f'<sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, (name, _) in enumerate(sheets, start=1)
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{workbook_sheets}</sheets><calcPr calcId="191029"/></workbook>'
    )
    workbook_rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for idx in range(1, len(sheets) + 1):
        workbook_rels.append(
            f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        )
    workbook_rels.append(
        f'<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    )
    workbook_rels.append('</Relationships>')

    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="2"><font><sz val="10"/><name val="Aptos"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="10"/><name val="Aptos"/></font></fonts>
  <fills count="6"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF17365D"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE2F0D9"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFE699"/><bgColor indexed="64"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFC00000"/><bgColor indexed="64"/></patternFill></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="7">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1" applyAlignment="1"><alignment wrapText="1" vertical="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
    <xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
    <xf numFmtId="0" fontId="0" fillId="4" borderId="0" xfId="0" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
    <xf numFmtId="0" fontId="1" fillId="5" borderId="0" xfId="0" applyFill="1" applyFont="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''

    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>MetriMade Product Portfolio</dc:title><dc:creator>MetriMade business workspace</dc:creator><dc:description>Evidence-separated product portfolio and MVP task overview</dc:description><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>MetriMade stdlib workbook builder</Application></Properties>'''

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "".join(content_types))
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("docProps/core.xml", core)
        archive.writestr("docProps/app.xml", app)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", "".join(workbook_rels))
        archive.writestr("xl/styles.xml", styles)
        for idx, (sheet_name, rows) in enumerate(sheets, start=1):
            freeze_columns = 7 if sheet_name == "Portfolio" else 0
            archive.writestr(
                f"xl/worksheets/sheet{idx}.xml",
                sheet_xml(rows, freeze_columns=freeze_columns),
            )
    OUTPUT.chmod(0o644)
    print(f"Wrote {OUTPUT} with {len(sheets)} sheets")


if __name__ == "__main__":
    main()
