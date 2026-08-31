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
RESEARCH_ADDITION_SOURCES_CSV = ROOT / "02-portfolio" / "research-idea-sources-additions.csv"
RESEARCH_PRIORITY_CSV = ROOT / "02-portfolio" / "research-idea-priority.csv"
RESEARCH_PREFLIGHT_CSV = ROOT / "02-portfolio" / "research-idea-preflight-estimates.csv"
TASKS_CSV = ROOT / "07-roadmap" / "mvp-tasks.csv"
OUTPUT = ROOT / "02-portfolio" / "product-portfolio.xlsx"
RESEARCH_WORKBOOK = ROOT.parent / "research" / "market" / "JuSt_Innovation_3D_Print_Commercial_Product_Matrix_2026.xlsx"
PRODUCTS_ROOT = ROOT.parent / "products"
PRODUCT_PREFLIGHT_AUDIT_GLOB = "PRODUCT-PREFLIGHT-AUDIT-*.json"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


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
        if scorecard != entry["scorecard"]:
            raise ValueError(f"Product preflight audit scorecard is stale for {entry['product']}")
        records.append(
            {
                "audit": entry,
                "preflight": preflight,
                "scorecard": scorecard,
                "product_root": product_root,
                "preflight_path": preflight_path,
                "purpose_path": purpose_path,
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
        "Archive_Status",
        "Archived_Entries",
    ]]
    for record in sorted(records, key=lambda item: str(item["audit"]["product"])):
        audit = record["audit"]
        preflight = record["preflight"]
        scorecard = record["scorecard"]
        rows.append(
            [
                audit["project_id"],
                f"products/{audit['product']}",
                audit["revision"],
                preflight_short(scorecard),
                scorecard["score_0_100"],
                exact_target_lane(str(scorecard["complexity"]), str(scorecard["criticality"])),
                scorecard["release"],
                preflight["assessment_id"],
                preflight["assessment_date"],
                record["preflight_path"].relative_to(ROOT.parent).as_posix(),
                record["purpose_path"].relative_to(ROOT.parent).as_posix(),
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
    if len(rows) != 200 or set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError("Research preflight overlay must contain every combined research idea exactly once")
    for row in rows:
        if row["Current_Lane"] not in {"A", "B", "C", "D", "E"}:
            raise ValueError(f"Invalid current lane for {row['SKU_ID']}")
        if "NOT RELEASE APPROVAL" not in row["Estimate_Status"]:
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


def validate_research_priority(
    rows: list[list[str]],
    expected_ids: set[str],
    research_status: dict[str, dict[str, str]],
) -> None:
    """Fail closed when the generated 200-idea implementation queue is stale or malformed."""
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
    if len(rows) != 201 or any(len(row) != len(header) for row in rows):
        raise ValueError("Research priority source must contain a 26-column header and exactly 200 complete idea rows")

    index = {name: header.index(name) for name in required}
    ids = [row[index["SKU_ID"]] for row in rows[1:]]
    if set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise ValueError("Research priority IDs do not match the combined 200-idea research register")
    orders = [int(row[index["Implementation_Order"]]) for row in rows[1:]]
    if orders != list(range(1, 201)):
        raise ValueError("Research priority implementation order must be sequential from 1 through 200")

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


def sheet_xml(rows: list[list[object]]) -> str:
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
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<dimension ref="A1:{last}"/>'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
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
    additional_sources = read_csv(RESEARCH_ADDITION_SOURCES_CSV)
    research_status = read_research_status(RESEARCH_STATUS_CSV)
    validate_research_additions(additional_research, legacy_product_matrix, portfolio, research_status)
    if additional_sources[0] != legacy_sources[0]:
        raise ValueError("Additional research-source schema does not match the retained source register")
    legacy_source_ids = {str(row[0]) for row in legacy_sources[1:]}
    additional_source_ids = [str(row[0]) for row in additional_sources[1:]]
    if len(additional_source_ids) != len(set(additional_source_ids)) or legacy_source_ids.intersection(additional_source_ids):
        raise ValueError("Additional research-source IDs are duplicate or collide with the retained source register")
    research_sources = legacy_sources + additional_sources[1:]
    valid_source_ids = {str(row[0]) for row in research_sources[1:]}
    source_index = additional_research[0].index("Source_IDs")
    used_source_ids = {
        source_id.strip()
        for row in additional_research[1:]
        for source_id in str(row[source_index]).split(";")
        if source_id.strip()
    }
    unknown_source_ids = sorted(used_source_ids.difference(valid_source_ids))
    if unknown_source_ids:
        raise ValueError(f"Research additions reference unknown source IDs: {', '.join(unknown_source_ids)}")
    research_priority = read_csv(RESEARCH_PRIORITY_CSV)
    legacy_sku_index = legacy_product_matrix[0].index("SKU ID")
    additional_sku_index = additional_research[0].index("SKU_ID")
    combined_research_ids = {
        str(row[legacy_sku_index]) for row in legacy_product_matrix[1:]
    } | {
        str(row[additional_sku_index]) for row in additional_research[1:]
    }
    validate_research_priority(research_priority, combined_research_ids, research_status)
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
    add_research_preflight(legacy_product_matrix, "SKU ID", research_preflight)
    add_research_preflight(additional_research, "SKU_ID", research_preflight)
    add_research_preflight(research_priority, "SKU_ID", research_preflight)
    for imported in (legacy_unit_economics, legacy_family_strategy):
        imported[0].append("Business_Workspace_Interpretation")
        for row in imported[1:]:
            row.extend([""] * (len(imported[0]) - 1 - len(row)))
            row.append("Research hypothesis only; not an existing, qualified, staged or live product")

    stages_present: dict[str, int] = {}
    for row in portfolio[1:]:
        stage = row[header.index("Lifecycle_Stage")]
        stages_present[stage] = stages_present.get(stage, 0) + 1
    additional_strategy_index = additional_research[0].index("Strategy_Fit")
    additional_core_count = sum(
        1 for row in additional_research[1:] if str(row[additional_strategy_index]).startswith("Core")
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
    preliminary_preflight_count = len(research_preflight) - linked_preflight_count
    summary = [
        ["Metric", "Value", "Interpretation"],
        ["Review date", "2026-08-31", "Repository-evidence snapshot"],
        ["Portfolio records", len(portfolio) - 1, "Includes planned concepts and non-external local model families"],
        ["Product directories with documented preflight", len(product_preflight_records), "Every current products/<family>/<product> directory; exact C/R/K/lane/confidence is listed in Product Preflights"],
        ["Portfolio rows with documented preflight", len(portfolio) - 1, "Exact current product scorecards are appended to the Portfolio sheet"],
        ["Product directories with explicit purpose", sum(1 for record in product_preflight_records if record["purpose_path"].is_file()), "Purpose paths are listed beside every product preflight"],
        ["Initial launch SKUs", len(initial) - 1, "Fixed target scope"],
        ["Legacy research concepts retained", len(legacy_product_matrix) - 1, "Research sheet now carries a controlled implementation overlay"],
        ["Additional research concepts", len(additional_research) - 1, "Append-only P0 hypotheses; preserved separately from the product portfolio"],
        ["Additional ideas at core/core-adjacent fit", additional_core_count, "Research allocation only; active development remains constrained by the 70% core-capacity rule"],
        ["Total research concepts", len(legacy_product_matrix) + len(additional_research) - 2, "Original 100 plus the researched 2026-08-27 addendum"],
        ["Addendum scoring", "Opportunity 0–100; risk 1–5", "Scores and price bands prioritize tests only; they are not approved demand, margin or release claims"],
        ["Research source records", len(research_sources) - 1, "Source records support direction only; per-concept demand validation is still required"],
        ["Research ideas with mapped models", sum(1 for row in research_status.values() if row.get("Implementation_Status") == "MODEL_EXISTS"), "Physical validation remains a later human gate"],
        ["Ranked research ideas", len(research_priority) - 1, "Comparable implementation planning queue; not release approval"],
        ["Research ideas linked to current product preflights", linked_preflight_count, "Exact scorecard copied from the mapped product; still not release approval"],
        ["Research ideas with preliminary preflight bands", preliminary_preflight_count, "C and K are planning bands; R0\u2013R1 and current Lane E remain until interface/process/test evidence exists"],
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
        ["R0\u2013R5", "Minimum maturity of scope, requirements, critical interfaces, process and verification", "Research-only concepts remain R0\u2013R1 until measured evidence exists"],
        ["K0\u2013K4", "Credible failure consequence and required rigor", "A research K band is a conservative proxy, not a safety qualification"],
        ["Lane A\u2013E", "Currently permitted workflow", "R<=1 or a hard-gate failure forces current Lane E"],
        ["Target lane after evidence", "Likely design workflow after readiness and hard gates are sufficient", "Planning aid only; does not override current Lane E, HOLD or CONCEPT_ONLY"],
        ["Confidence", "Qualitative workflow confidence", "No numerical success probability is inferred"],
        ["Linked current product preflight", "Research idea maps to an existing Working_SKU", "Exact current product scorecard and source path are shown; not release approval"],
        ["Preliminary idea estimate", "No mapped current product preflight", "C band uses creation/validation planning effort; K band uses the research-risk proxy; R0\u2013R1 and Lane E are fixed until evidence exists"],
        ["Market potential", "Opportunity and market-fit fields in the research register", "Keep separate from C/R/K/lane; compare side by side in Implementation Priority"],
        ["Update rule", "Regenerate after product-preflight, implementation mapping or research-priority changes", "Run build_research_preflight_estimates.py, then build_product_workbook.py"],
        ["Product source", "products/*/*/preflight/preflight-result.json", "Validated project-level source of truth"],
        ["Research source", "research-idea-preflight-estimates.csv", "Version-controlled 200-row planning overlay"],
    ]

    sheets = [
        ("Summary", summary),
        ("Initial Portfolio", initial),
        ("Portfolio", portfolio),
        ("Product Preflights", all_product_preflights),
        ("External Exclusions", exclusions),
        ("Stage Definitions", stages),
        ("MVP Tasks", tasks),
        ("Research Backlog", research),
        ("Implementation Priority", research_priority),
        ("Research Ideas 100", legacy_product_matrix),
        ("Research Ideas +100", additional_research),
        ("Research Economics", legacy_unit_economics),
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
        for idx, (_, rows) in enumerate(sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml(rows))
    OUTPUT.chmod(0o644)
    print(f"Wrote {OUTPUT} with {len(sheets)} sheets")


if __name__ == "__main__":
    main()
