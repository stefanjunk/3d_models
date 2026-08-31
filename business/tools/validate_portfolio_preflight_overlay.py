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


def validate_research_sheets() -> tuple[int, int]:
    with workbook.RESEARCH_PREFLIGHT_CSV.open(newline="", encoding="utf-8") as handle:
        estimates = {row["SKU_ID"]: row for row in csv.DictReader(handle)}
    if len(estimates) != 200:
        raise ValueError(f"Expected 200 research preflight estimates, found {len(estimates)}")

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
    for sheet_name, key in (("Research Ideas 100", "SKU ID"), ("Research Ideas +100", "SKU_ID")):
        header, rows = rows_by_key(sheet_name, key)
        if len(rows) != 100:
            raise ValueError(f"Expected 100 ideas in {sheet_name}, found {len(rows)}")
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
            elif not (REPO_ROOT / estimate["Source_Or_Linked_Preflight"]).is_file():
                raise ValueError(f"Linked product preflight is missing for {sku_id}")
    if combined != set(estimates):
        raise ValueError("The two research sheets do not cover the same 200 IDs as the estimate source")

    priority_header, priority = rows_by_key("Implementation Priority", "SKU_ID")
    if len(priority) != 200:
        raise ValueError(f"Expected 200 Implementation Priority rows, found {len(priority)}")
    for required in ("Priority_Score_0_100", "Estimated_Market_Fit_1_5", *workbook_columns):
        if required not in priority_header:
            raise ValueError(f"Implementation Priority is missing comparison column {required}")
    for sku_id, row in priority.items():
        estimate = estimates[sku_id]
        for workbook_column, source_column in workbook_columns.items():
            if str(cell(priority_header, row, workbook_column)) != estimate[source_column]:
                raise ValueError(f"Stale {workbook_column} for {sku_id} in Implementation Priority")

    linked = sum(1 for row in estimates.values() if row["Estimate_Status"].startswith("LINKED"))
    preliminary = len(estimates) - linked
    if (linked, preliminary) != (37, 163):
        raise ValueError(f"Unexpected linked/preliminary split: {linked}/{preliminary}")
    return linked, preliminary


def main() -> int:
    expected_estimate_csv = estimates_builder.render(estimates_builder.build_rows())
    if workbook.RESEARCH_PREFLIGHT_CSV.read_text(encoding="utf-8") != expected_estimate_csv:
        raise ValueError("Research preflight estimate CSV is stale")
    with zipfile.ZipFile(workbook.OUTPUT) as archive:
        bad_member = archive.testzip()
    if bad_member:
        raise ValueError(f"Corrupt workbook member: {bad_member}")
    portfolio_count, product_count = validate_product_sheets()
    linked, preliminary = validate_research_sheets()
    print(
        "PASS: portfolio preflight overlay; "
        f"portfolio={portfolio_count}, products={product_count}, "
        f"research_linked={linked}, research_preliminary={preliminary}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
