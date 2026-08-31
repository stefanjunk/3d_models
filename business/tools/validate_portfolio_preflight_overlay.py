#!/usr/bin/env python3
"""Validate product and research preflight coverage in the portfolio workbook."""

from __future__ import annotations

import csv
import re
import zipfile
from pathlib import Path

import build_product_workbook as workbook
import build_research_preflight_estimates as estimates_builder


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPACT_RE = re.compile(
    r"^C[0-5](?:\u2013C[0-5])? \u00b7 R[0-5](?:\u2013R[0-5])? \u00b7 "
    r"K[0-4](?:\u2013K[0-4])? \u00b7 Lane [A-E] \u00b7 "
    r"(?:HIGH|MEDIUM_HIGH|CONDITIONAL|LOW_UNKNOWN|NOT_AUTONOMOUSLY_RELEASABLE)$"
)
EXACT_COMPACT_RE = re.compile(
    r"^C[0-5] \u00b7 R[0-5] \u00b7 K[0-4] \u00b7 Lane [A-E] \u00b7 "
    r"(?:HIGH|MEDIUM_HIGH|CONDITIONAL|LOW_UNKNOWN|NOT_AUTONOMOUSLY_RELEASABLE)$"
)


def rows_by_key(sheet_name: str, key: str) -> tuple[list[object], dict[str, list[object]]]:
    rows = workbook.read_xlsx_sheet(workbook.OUTPUT, sheet_name)
    if not rows:
        raise ValueError(f"Workbook sheet is empty: {sheet_name}")
    header = rows[0]
    key_index = header.index(key)
    keyed = {str(row[key_index]): row for row in rows[1:]}
    if len(keyed) != len(rows) - 1:
        raise ValueError(f"Duplicate or blank {key} in {sheet_name}")
    return header, keyed


def cell(header: list[object], row: list[object], column: str) -> object:
    return row[header.index(column)]


def validate_product_sheets() -> tuple[int, int]:
    portfolio_header, portfolio = rows_by_key("Portfolio", "Record_ID")
    if len(portfolio) != 99:
        raise ValueError(f"Expected 99 Portfolio rows, found {len(portfolio)}")
    for record_id, row in portfolio.items():
        compact = str(cell(portfolio_header, row, "Preflight_Short"))
        if not EXACT_COMPACT_RE.fullmatch(compact):
            raise ValueError(f"Invalid exact preflight compact form for {record_id}: {compact}")
        for column in ("Preflight_Result_Path", "Purpose_Document_Path"):
            path = REPO_ROOT / str(cell(portfolio_header, row, column))
            if not path.is_file():
                raise ValueError(f"Missing {column} for {record_id}: {path}")

    product_header, products = rows_by_key("Product Preflights", "Product_Path")
    if len(products) != 108:
        raise ValueError(f"Expected 108 Product Preflights rows, found {len(products)}")
    live_product_roots = {
        product.relative_to(REPO_ROOT).as_posix()
        for family in (REPO_ROOT / "products").iterdir()
        if family.is_dir()
        for product in family.iterdir()
        if product.is_dir()
    }
    if set(products) != live_product_roots:
        raise ValueError("Product Preflights sheet does not match the current product-directory inventory")
    for product_path, row in products.items():
        compact = str(cell(product_header, row, "Preflight_Short"))
        if not EXACT_COMPACT_RE.fullmatch(compact):
            raise ValueError(f"Invalid product preflight compact form for {product_path}: {compact}")
        for column in ("Preflight_Result", "Purpose_Document"):
            path = REPO_ROOT / str(cell(product_header, row, column))
            if not path.is_file():
                raise ValueError(f"Missing {column} for {product_path}: {path}")
    return len(portfolio), len(products)


def validate_research_sheets() -> tuple[int, int, int, int]:
    with workbook.RESEARCH_PREFLIGHT_CSV.open(newline="", encoding="utf-8") as handle:
        estimates = {row["SKU_ID"]: row for row in csv.DictReader(handle)}
    if len(estimates) != 314:
        raise ValueError(f"Expected 314 research preflight estimates, found {len(estimates)}")

    workbook_columns = {
        "Preflight_Short": "Preflight_Short",
        "Preflight_Complexity_Band": "Complexity_Band",
        "Preflight_Readiness_Band": "Readiness_Band",
        "Preflight_Criticality_Band": "Criticality_Band",
        "Preflight_Current_Lane": "Current_Lane",
        "Preflight_Target_Lane_After_Evidence": "Target_Lane_After_Evidence",
        "Preflight_Estimate_Status": "Estimate_Status",
        "Preflight_Basis": "Basis",
        "Preflight_Source": "Source_Or_Linked_Preflight",
    }
    combined: set[str] = set()
    research_sheets = (
        ("Research Ideas 100", "SKU ID", 100),
        ("Research Ideas +100", "SKU_ID", 100),
        ("Research Ideas +200", "SKU_ID", 100),
        ("Research Variants R3", "SKU_ID", 14),
    )
    for sheet_name, key, expected_count in research_sheets:
        header, rows = rows_by_key(sheet_name, key)
        if len(rows) != expected_count:
            raise ValueError(f"Expected {expected_count} ideas in {sheet_name}, found {len(rows)}")
        combined.update(rows)
        for sku_id, row in rows.items():
            estimate = estimates.get(sku_id)
            if estimate is None:
                raise ValueError(f"No research preflight estimate for {sku_id}")
            compact = str(cell(header, row, "Preflight_Short"))
            if not COMPACT_RE.fullmatch(compact):
                raise ValueError(f"Invalid research preflight compact form for {sku_id}: {compact}")
            for workbook_column, source_column in workbook_columns.items():
                if str(cell(header, row, workbook_column)) != estimate[source_column]:
                    raise ValueError(f"Stale {workbook_column} for {sku_id} in {sheet_name}")
            if estimate["Estimate_Status"].startswith("PRELIMINARY"):
                if estimate["Readiness_Band"] != "R0\u2013R1" or estimate["Current_Lane"] != "E":
                    raise ValueError(f"Preliminary idea bypasses R0\u2013R1/Lane E for {sku_id}")
            elif estimate["Estimate_Status"].startswith("STRUCTURED RESEARCH PREFLIGHT R2"):
                if (
                    estimate["Readiness_Band"] != "R2"
                    or estimate["Criticality_Band"] != "K1"
                    or estimate["Complexity_Band"] not in {"C0", "C1", "C2"}
                    or estimate["Current_Lane"] != "E"
                    or estimate["Target_Lane_After_Evidence"] != "B"
                    or estimate["Design_Release"] != "CONCEPT_ONLY"
                ):
                    raise ValueError(f"Structured concept preflight violates the C/R/K/lane gate for {sku_id}")
            elif estimate["Estimate_Status"].startswith("STRUCTURED SPECIFIC-VARIANT PREFLIGHT R3"):
                expected_lane = "C" if estimate["Complexity_Band"] == "C3" else "B"
                if (
                    estimate["Readiness_Band"] != "R3"
                    or estimate["Criticality_Band"] != "K1"
                    or estimate["Complexity_Band"] not in {"C1", "C2", "C3"}
                    or estimate["Current_Lane"] != expected_lane
                    or estimate["Target_Lane_After_Evidence"] != expected_lane
                    or estimate["Confidence"] != "CONDITIONAL"
                    or estimate["Design_Release"] != "GO_WITH_CONTROLS"
                ):
                    raise ValueError(f"Specific R3 variant violates the C/R/K/lane gate for {sku_id}")
            elif not (REPO_ROOT / estimate["Source_Or_Linked_Preflight"]).is_file():
                raise ValueError(f"Linked product preflight is missing for {sku_id}")
    if combined != set(estimates):
        raise ValueError("The four research sheets do not cover the same 314 IDs as the estimate source")

    structured_header, structured = rows_by_key("Research Ideas +200", "SKU_ID")
    for sku_id, row in structured.items():
        if not str(cell(structured_header, row, "Purpose")).strip():
            raise ValueError(f"Explicit purpose is missing for {sku_id}")
        if float(cell(structured_header, row, "Trend_Score_0_100")) <= 70:
            raise ValueError(f"Trend score does not exceed 70 for {sku_id}")
        if str(cell(structured_header, row, "Trend_Score_Status")) != "DIRECTIONAL PLANNING SCORE — NOT VALIDATED DEMAND":
            raise ValueError(f"Trend-score disclaimer is missing for {sku_id}")
        if "G3 FAIL" not in str(cell(structured_header, row, "Hard_Gates")):
            raise ValueError(f"Fail-closed process gate is missing for {sku_id}")

    variant_header, variants = rows_by_key("Research Variants R3", "SKU_ID")
    for sku_id, row in variants.items():
        if not str(cell(variant_header, row, "Purpose")).strip():
            raise ValueError(f"Explicit purpose is missing for {sku_id}")
        if float(cell(variant_header, row, "Trend_Score_0_100")) <= 70:
            raise ValueError(f"Trend score does not exceed 70 for {sku_id}")
        if str(cell(variant_header, row, "Trend_Score_Status")) != "INHERITED DIRECTIONAL PLANNING SCORE — NOT VALIDATED VARIANT DEMAND":
            raise ValueError(f"Variant-demand disclaimer is missing for {sku_id}")
        if any(f"G{number} PASS" not in str(cell(variant_header, row, "Hard_Gates")) for number in range(7)):
            raise ValueError(f"R3 hard-gate evidence is incomplete for {sku_id}")

    priority_header, priority = rows_by_key("Implementation Priority", "SKU_ID")
    if len(priority) != 314:
        raise ValueError(f"Expected 314 Implementation Priority rows, found {len(priority)}")
    for required in ("Priority_Score_0_100", "Trend_Score_0_100", "Estimated_Market_Fit_1_5", *workbook_columns):
        if required not in priority_header:
            raise ValueError(f"Implementation Priority is missing comparison column {required}")
    for sku_id, row in priority.items():
        estimate = estimates[sku_id]
        for workbook_column, source_column in workbook_columns.items():
            if str(cell(priority_header, row, workbook_column)) != estimate[source_column]:
                raise ValueError(f"Stale {workbook_column} for {sku_id} in Implementation Priority")

    linked = sum(1 for row in estimates.values() if row["Estimate_Status"].startswith("LINKED"))
    structured_count = sum(1 for row in estimates.values() if row["Estimate_Status"].startswith("STRUCTURED"))
    specific_r3 = sum(
        1 for row in estimates.values() if row["Estimate_Status"].startswith("STRUCTURED SPECIFIC-VARIANT")
    )
    structured_r2 = structured_count - specific_r3
    preliminary = len(estimates) - linked - structured_r2 - specific_r3
    if (linked, preliminary, structured_r2, specific_r3) != (37, 163, 100, 14):
        raise ValueError(
            f"Unexpected linked/preliminary/structured-R2/specific-R3 split: "
            f"{linked}/{preliminary}/{structured_r2}/{specific_r3}"
        )
    return linked, preliminary, structured_r2, specific_r3


def validate_advancement_sheet() -> tuple[int, int]:
    header, rows = rows_by_key("R Advancement", "Record_Key")
    if len(rows) != 422:
        raise ValueError(f"Expected 422 readiness advancement rows, found {len(rows)}")
    record_type_index = header.index("Record_Type")
    purpose_index = header.index("Purpose_or_Intended_Use")
    purpose_documented_index = header.index("Purpose_Documented")
    research_count = 0
    product_count = 0
    for key, row in rows.items():
        record_type = str(row[record_type_index])
        research_count += record_type == "RESEARCH_IDEA"
        product_count += record_type == "PRODUCT_DIRECTORY"
        if str(row[purpose_documented_index]) != "YES" or len(str(row[purpose_index]).strip()) < 12:
            raise ValueError(f"Advancement record lacks an explicit purpose: {key}")
    if (research_count, product_count) != (314, 108):
        raise ValueError(f"Unexpected advancement split: {research_count}/{product_count}")
    return research_count, product_count


def main() -> int:
    expected_estimate_csv = estimates_builder.render(estimates_builder.build_rows())
    if workbook.RESEARCH_PREFLIGHT_CSV.read_text(encoding="utf-8") != expected_estimate_csv:
        raise ValueError("Research preflight estimate CSV is stale")
    with zipfile.ZipFile(workbook.OUTPUT) as archive:
        bad_member = archive.testzip()
    if bad_member:
        raise ValueError(f"Corrupt workbook member: {bad_member}")
    portfolio_count, product_count = validate_product_sheets()
    linked, preliminary, structured_count, specific_r3 = validate_research_sheets()
    advancement_research, advancement_products = validate_advancement_sheet()
    print(
        "PASS: portfolio preflight overlay; "
        f"portfolio={portfolio_count}, products={product_count}, "
        f"research_linked={linked}, research_preliminary={preliminary}, "
        f"research_structured_r2={structured_count}, research_specific_r3={specific_r3}, "
        f"advancement={advancement_research}+{advancement_products}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
