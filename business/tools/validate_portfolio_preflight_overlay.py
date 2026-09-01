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
    portfolio_header, portfolio = rows_by_key("Product Register", "Record_ID")
    if len(portfolio) != 99:
        raise ValueError(f"Expected 99 Product Register rows, found {len(portfolio)}")
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


def indexed_sheet(
    sheet_name: str, key: str
) -> tuple[list[object], dict[str, tuple[int, list[object]]]]:
    rows = workbook.read_xlsx_sheet(workbook.OUTPUT, sheet_name)
    if not rows or key not in rows[0]:
        raise ValueError(f"Workbook sheet/key is missing: {sheet_name}/{key}")
    header = rows[0]
    key_index = header.index(key)
    result: dict[str, tuple[int, list[object]]] = {}
    for row_number, source_row in enumerate(rows[1:], start=2):
        row = list(source_row) + [""] * (len(header) - len(source_row))
        value = str(row[key_index])
        if not value or value in result:
            raise ValueError(f"Duplicate or blank {key} in {sheet_name}: {value}")
        result[value] = (row_number, row)
    return header, result


def compare_raw_block(
    master_header: list[object],
    master_row: list[object],
    source_header: list[object],
    source_row: list[object] | None,
    prefix: str,
    record_key: str,
) -> None:
    """Verify every namespaced raw cell against the source sheet cell-for-cell."""
    source_values: dict[str, object] = {}
    if source_row is not None:
        padded = list(source_row) + [""] * (len(source_header) - len(source_row))
        source_values = dict(zip(workbook.namespaced_headers(source_header, prefix), padded))
    for column_index, column in enumerate(master_header):
        column_name = str(column)
        if not column_name.startswith(prefix):
            continue
        expected = source_values.get(column_name, "")
        actual = master_row[column_index] if column_index < len(master_row) else ""
        if str(actual or "") != str(expected or ""):
            raise ValueError(
                f"Raw-source mismatch for {record_key} at {column_name}: "
                f"master={actual!r}, source={expected!r}"
            )


def validate_unified_portfolio() -> tuple[int, int, int]:
    master_header, master = rows_by_key("Portfolio", "Unified_Record_Key")
    if len(master) != 422 or len(master_header) != len(set(master_header)):
        raise ValueError(
            f"Unified Portfolio must contain 422 records and unique columns; "
            f"found {len(master)} records/{len(master_header)} columns"
        )

    product_header, product_rows = indexed_sheet("Product Register", "Source_Path")
    preflight_header, preflight_rows = indexed_sheet("Product Preflights", "Product_Path")
    priority_header, priority_rows = indexed_sheet("Implementation Priority", "SKU_ID")
    economics_header, economics_rows = indexed_sheet("Research Economics", "SKU ID")
    advancement_header, advancement_rows = indexed_sheet("R Advancement", "Record_Key")
    idea_sources: dict[str, tuple[str, int, list[object], list[object]]] = {}
    for sheet_name, key in (
        ("Research Ideas 100", "SKU ID"),
        ("Research Ideas +100", "SKU_ID"),
        ("Research Ideas +200", "SKU_ID"),
        ("Research Variants R3", "SKU_ID"),
    ):
        source_header, source_rows = indexed_sheet(sheet_name, key)
        for sku_id, (row_number, row) in source_rows.items():
            if sku_id in idea_sources:
                raise ValueError(f"Research idea exists in multiple source sheets: {sku_id}")
            idea_sources[sku_id] = (sheet_name, row_number, source_header, row)

    required_master_columns = {
        "Portfolio_Status", "Primary_Source_Sheet", "Primary_Source_Row", "Record_ID", "Product",
        "Purpose_or_Customer_Job", "Preflight_Short", "Complexity", "Readiness", "Criticality",
        "Current_Lane", "Suggested_Target_R", "Bottleneck", "Exact_Next_Evidence", "Evidence_Boundary",
        "Max_L_mm", "Max_W_mm", "Max_H_mm", "Priority_Score_0_100", "Trend_Score_0_100",
    }
    missing_columns = sorted(required_master_columns.difference(master_header))
    if missing_columns:
        raise ValueError(f"Unified Portfolio lacks comparison columns: {', '.join(missing_columns)}")

    product_count = 0
    research_count = 0
    detailed_economics_count = 0
    numeric_trend_count = 0
    used_product_paths: set[str] = set()
    used_preflight_paths: set[str] = set()
    used_research_ids: set[str] = set()
    for record_key, master_row in master.items():
        record_type = str(cell(master_header, master_row, "Record_Type"))
        record_id = str(cell(master_header, master_row, "Record_ID"))
        product_path = str(cell(master_header, master_row, "Product_Path"))
        primary_sheet = str(cell(master_header, master_row, "Primary_Source_Sheet"))
        primary_row = int(cell(master_header, master_row, "Primary_Source_Row"))
        for required in (
            "Portfolio_Status", "Record_ID", "Product", "Purpose_or_Customer_Job", "Preflight_Short",
            "Complexity", "Readiness", "Criticality", "Current_Lane", "Suggested_Target_R",
            "Bottleneck", "Exact_Next_Evidence", "Evidence_Boundary",
        ):
            if not str(cell(master_header, master_row, required)).strip():
                raise ValueError(f"Unified Portfolio field {required} is blank for {record_key}")

        advancement_entry = advancement_rows.get(record_key)
        if advancement_entry is None:
            raise ValueError(f"Unified Portfolio row has no advancement source: {record_key}")
        compare_raw_block(
            master_header, master_row, advancement_header, advancement_entry[1], "Advancement__", record_key
        )

        if record_type == "PRODUCT_DIRECTORY":
            product_count += 1
            preflight_entry = preflight_rows.get(product_path)
            if not product_path or preflight_entry is None:
                raise ValueError(f"Product row lacks its path-based preflight: {record_key}")
            product_entry = product_rows.get(product_path)
            expected_sheet = "Product Register" if product_entry is not None else "Product Preflights"
            expected_row = product_entry[0] if product_entry is not None else preflight_entry[0]
            if (primary_sheet, primary_row) != (expected_sheet, expected_row):
                raise ValueError(f"Product source-row pointer shifted for {record_key}")
            compare_raw_block(
                master_header,
                master_row,
                product_header,
                product_entry[1] if product_entry else None,
                "Product__",
                record_key,
            )
            compare_raw_block(
                master_header, master_row, preflight_header, preflight_entry[1], "Preflight__", record_key
            )
            compare_raw_block(master_header, master_row, [], None, "Idea__", record_key)
            compare_raw_block(master_header, master_row, [], None, "Priority__", record_key)
            compare_raw_block(master_header, master_row, [], None, "Economics__", record_key)
            used_preflight_paths.add(product_path)
            if product_entry:
                used_product_paths.add(product_path)
        elif record_type == "RESEARCH_IDEA":
            research_count += 1
            idea_entry = idea_sources.get(record_id)
            priority_entry = priority_rows.get(record_id)
            if idea_entry is None or priority_entry is None:
                raise ValueError(f"Research row lacks an idea or priority source: {record_key}")
            idea_sheet, idea_row_number, idea_header, idea_row = idea_entry
            if (primary_sheet, primary_row) != (idea_sheet, idea_row_number):
                raise ValueError(f"Research source-row pointer shifted for {record_key}")
            for numeric_column in (
                "Max_L_mm", "Max_W_mm", "Max_H_mm", "Priority_Score_0_100", "Opportunity_Score_0_100"
            ):
                if not isinstance(cell(master_header, master_row, numeric_column), (int, float)):
                    raise ValueError(f"Unified numeric comparison field is not numeric: {record_key}/{numeric_column}")
            trend_score = cell(master_header, master_row, "Trend_Score_0_100")
            if trend_score not in (None, ""):
                if not isinstance(trend_score, (int, float)):
                    raise ValueError(f"Unified trend score is populated but nonnumeric: {record_key}")
                numeric_trend_count += 1
            economics_entry = economics_rows.get(record_id)
            if economics_entry:
                detailed_economics_count += 1
            compare_raw_block(master_header, master_row, [], None, "Product__", record_key)
            compare_raw_block(master_header, master_row, [], None, "Preflight__", record_key)
            compare_raw_block(master_header, master_row, idea_header, idea_row, "Idea__", record_key)
            compare_raw_block(
                master_header, master_row, priority_header, priority_entry[1], "Priority__", record_key
            )
            compare_raw_block(
                master_header,
                master_row,
                economics_header,
                economics_entry[1] if economics_entry else None,
                "Economics__",
                record_key,
            )
            used_research_ids.add(record_id)
        else:
            raise ValueError(f"Unexpected unified record type for {record_key}: {record_type}")

    if (research_count, product_count, detailed_economics_count) != (314, 108, 100):
        raise ValueError(
            "Unexpected unified split/economics coverage: "
            f"{research_count}/{product_count}/{detailed_economics_count}"
        )
    if numeric_trend_count != 214:
        raise ValueError(f"Unexpected populated trend-score coverage: {numeric_trend_count}/314")
    if used_product_paths != set(product_rows) or used_preflight_paths != set(preflight_rows):
        raise ValueError("Product source rows were duplicated or omitted from Unified Portfolio")
    if used_research_ids != set(idea_sources) or used_research_ids != set(priority_rows):
        raise ValueError("Research source rows were duplicated or omitted from Unified Portfolio")
    return research_count, product_count, detailed_economics_count


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


def build_expected_unified_portfolio() -> list[list[object]]:
    """Rebuild the master rows directly from version-controlled source data."""
    portfolio = workbook.read_csv(workbook.PORTFOLIO_CSV)
    product_records = workbook.load_product_preflight_records()
    workbook.add_portfolio_preflight(portfolio, product_records)
    product_preflights = workbook.product_preflight_sheet(product_records)

    legacy = workbook.read_xlsx_sheet(workbook.RESEARCH_WORKBOOK, "Product Matrix")
    additions = workbook.read_csv(workbook.RESEARCH_ADDITIONS_CSV)
    structured = workbook.read_csv(workbook.RESEARCH_ADDITIONS_2_CSV)
    variants = workbook.read_csv(workbook.RESEARCH_R3_VARIANTS_CSV)
    priority = workbook.read_csv(workbook.RESEARCH_PRIORITY_CSV)
    advancement = workbook.read_csv(workbook.READINESS_ADVANCEMENT_CSV)
    economics = workbook.read_xlsx_sheet(workbook.RESEARCH_WORKBOOK, "Unit Economics")
    research_status = workbook.read_research_status(workbook.RESEARCH_STATUS_CSV)

    workbook.validate_research_additions(additions, legacy, portfolio, research_status)
    workbook.validate_structured_research_additions(structured, legacy, additions, portfolio)
    legacy_ids = {str(row[legacy[0].index("SKU ID")]) for row in legacy[1:]}
    addition_ids = {str(row[additions[0].index("SKU_ID")]) for row in additions[1:]}
    structured_ids = {str(row[structured[0].index("SKU_ID")]) for row in structured[1:]}
    prior_ids = legacy_ids | addition_ids | structured_ids
    occupied_names = {
        workbook.normalize_name(row[legacy[0].index("Product")]) for row in legacy[1:]
    } | {
        workbook.normalize_name(row[additions[0].index("Product")]) for row in additions[1:]
    } | {
        workbook.normalize_name(row[structured[0].index("Product")]) for row in structured[1:]
    } | {
        workbook.normalize_name(row[portfolio[0].index("Product_or_Model")]) for row in portfolio[1:]
    }
    workbook.validate_specific_r3_variants(variants, prior_ids, occupied_names)
    variant_ids = {str(row[variants[0].index("SKU_ID")]) for row in variants[1:]}
    research_ids = prior_ids | variant_ids
    workbook.validate_research_priority(priority, research_ids, research_status)
    workbook.validate_readiness_advancement(advancement, research_ids, len(product_records))
    preflight = workbook.read_research_preflight(workbook.RESEARCH_PREFLIGHT_CSV, research_ids)

    source_tables = [
        ("Research Ideas 100", legacy, "SKU ID", "Research hypothesis; implementation fields are controlled by research-ideas-implementation.csv"),
        ("Research Ideas +100", additions, "SKU_ID", "New research hypothesis checked 2026-08-27; not a selected, qualified or released product"),
        ("Research Ideas +200", structured, "SKU_ID", "Trend-screened research hypothesis checked 2026-08-31; structured R2 concept preflight, not a selected, qualified or released product"),
        ("Research Variants R3", variants, "SKU_ID", "Named-interface child checked 2026-08-31; R3 nominal design inputs only, not physical qualification, demand proof or release"),
    ]
    for _, rows, key_column, interpretation in source_tables:
        workbook.add_research_overlay(rows, key_column, research_status, interpretation)
        workbook.add_research_preflight(rows, key_column, preflight)
    workbook.add_research_preflight(priority, "SKU_ID", preflight)
    economics[0].append("Business_Workspace_Interpretation")
    for row in economics[1:]:
        row.extend([""] * (len(economics[0]) - 1 - len(row)))
        row.append("Research hypothesis only; not an existing, qualified, staged or live product")

    return workbook.build_unified_portfolio(
        portfolio,
        product_preflights,
        [(sheet_name, rows, key_column) for sheet_name, rows, key_column, _ in source_tables],
        priority,
        economics,
        advancement,
    )


def values_equal(left: object, right: object) -> bool:
    if left in (None, "") and right in (None, ""):
        return True
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= 1e-12
    return str(left) == str(right)


def validate_slim_workbook(expected: list[list[object]]) -> tuple[int, int, int]:
    """Validate the six-sheet user workbook and its single Working_SKU identity."""
    with zipfile.ZipFile(workbook.OUTPUT) as archive:
        workbook_xml = archive.read("xl/workbook.xml").decode("utf-8")
    expected_sheets = [
        "Summary", "Portfolio", "Stage Definitions", "Research Families", "Research Sources", "Preflight Legend"
    ]
    actual_sheet_names = re.findall(r'<sheet name="([^"]+)"', workbook_xml)
    if actual_sheet_names != expected_sheets:
        raise ValueError(f"Unexpected workbook sheets: {actual_sheet_names}")

    actual = workbook.read_xlsx_sheet(workbook.OUTPUT, "Portfolio")
    if len(actual) != len(expected) or actual[0] != expected[0]:
        raise ValueError(
            f"Portfolio shape/header mismatch: actual={len(actual)}x{len(actual[0])}, "
            f"expected={len(expected)}x{len(expected[0])}"
        )
    for row_number, (actual_row, expected_row) in enumerate(zip(actual, expected), start=1):
        for column_number in range(len(expected[0])):
            left = actual_row[column_number] if column_number < len(actual_row) else ""
            right = expected_row[column_number] if column_number < len(expected_row) else ""
            if not values_equal(left, right):
                raise ValueError(
                    f"Portfolio source mismatch at row {row_number}, column {column_number + 1}: "
                    f"actual={left!r}, expected={right!r}"
                )

    header = actual[0]
    forbidden = {
        "Record_ID", "Mapped_Working_SKU", "Product__Record_ID", "Product__Working_SKU",
        "Idea__Mapped_Working_SKU", "Priority__Mapped_Working_SKU", "Advancement__Record_ID",
    }
    present_forbidden = sorted(forbidden.intersection(str(value) for value in header))
    if present_forbidden:
        raise ValueError(f"Redundant portfolio identifiers remain: {', '.join(present_forbidden)}")
    sku_index = header.index("Working_SKU")
    type_index = header.index("Record_Type")
    key_index = header.index("Unified_Record_Key")
    skus = [str(row[sku_index]) for row in actual[1:]]
    expected_total = len(expected) - 1
    if any(not sku for sku in skus) or len(skus) != len(set(skus)) or len(skus) != expected_total:
        raise ValueError(
            f"Portfolio must contain exactly {expected_total} populated, unique Working_SKU values"
        )
    research_count = 0
    product_count = 0
    for row in actual[1:]:
        record_type = str(row[type_index])
        if record_type == "RESEARCH_IDEA":
            research_count += 1
            expected_sku = str(row[key_index]).removeprefix("RESEARCH:")
            if str(row[sku_index]) != expected_sku:
                raise ValueError(f"Research Working_SKU mismatch: {row[key_index]}")
        elif record_type == "PRODUCT_DIRECTORY":
            product_count += 1
        else:
            raise ValueError(f"Unknown portfolio record type: {record_type}")
    expected_research_count = sum(
        str(row[type_index]) == "RESEARCH_IDEA" for row in expected[1:]
    )
    expected_product_count = sum(
        str(row[type_index]) == "PRODUCT_DIRECTORY" for row in expected[1:]
    )
    if (research_count, product_count) != (expected_research_count, expected_product_count):
        raise ValueError(f"Unexpected portfolio split: {research_count}/{product_count}")
    return len(skus), research_count, product_count


def main() -> int:
    expected_estimate_csv = estimates_builder.render(estimates_builder.build_rows())
    if workbook.RESEARCH_PREFLIGHT_CSV.read_text(encoding="utf-8") != expected_estimate_csv:
        raise ValueError("Research preflight estimate CSV is stale")
    with zipfile.ZipFile(workbook.OUTPUT) as archive:
        bad_member = archive.testzip()
    if bad_member:
        raise ValueError(f"Corrupt workbook member: {bad_member}")
    expected = build_expected_unified_portfolio()
    sku_count, research_count, product_count = validate_slim_workbook(expected)
    print(
        "PASS: slim unified portfolio; "
        f"working_skus={sku_count}, research={research_count}, products={product_count}, "
        f"columns={len(expected[0])}, sheets=6"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
