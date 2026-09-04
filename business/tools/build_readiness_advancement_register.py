#!/usr/bin/env python3
"""Build the full research-and-product readiness advancement register."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import defaultdict
from pathlib import Path

from build_product_workbook import read_xlsx_sheet


REPO_ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_DIR = REPO_ROOT / "business/02-portfolio"
PRIORITY_CSV = PORTFOLIO_DIR / "research-idea-priority.csv"
PREFLIGHT_CSV = PORTFOLIO_DIR / "research-idea-preflight-estimates.csv"
IMPLEMENTATION_CSV = PORTFOLIO_DIR / "research-ideas-implementation.csv"
PORTFOLIO_CSV = PORTFOLIO_DIR / "product-portfolio.csv"
ADDITIONS_CSV = PORTFOLIO_DIR / "research-ideas-additions.csv"
STRUCTURED_CSV = PORTFOLIO_DIR / "research-ideas-additions-2.csv"
VARIANTS_CSV = PORTFOLIO_DIR / "research-ideas-r3-variants.csv"
GENERATIVE_CSV = PORTFOLIO_DIR / "research-ideas-additions-3.csv"
LEGACY_WORKBOOK = REPO_ROOT / "research/market/JuSt_Innovation_3D_Print_Commercial_Product_Matrix_2026.xlsx"
PRODUCTS_ROOT = REPO_ROOT / "products"
OUTPUT = PORTFOLIO_DIR / "readiness-advancement-register.csv"
ASSESSMENT_DATE = "2026-08-31"
REGISTER_VERSION = "1.0"
# SKU-315..414 is reserved for the Step1X research block, so the named-interface
# R3 child identifiers are declared in explicit blocks rather than one range.
GENERIC_RESEARCH_ID_MAX = 300
R3_VARIANT_ID_BLOCKS = ((301, 314), (501, 557))
STEP1X_ID_BLOCK = (315, 414)
RESEARCH_IDS = {f"SKU-{number:03d}" for number in range(1, GENERIC_RESEARCH_ID_MAX + 1)} | {
    f"SKU-{number:03d}"
    for first, last in R3_VARIANT_ID_BLOCKS
    for number in range(first, last + 1)
} | {
    f"SKU-{number:03d}" for number in range(STEP1X_ID_BLOCK[0], STEP1X_ID_BLOCK[1] + 1)
}
RESEARCH_COUNT = len(RESEARCH_IDS)

FIELDS = [
    "Record_Key",
    "Record_Type",
    "Record_ID",
    "Parent_SKU_ID",
    "Product",
    "Product_Path",
    "Purpose_or_Intended_Use",
    "Purpose_Documented",
    "Trend_Score_0_100",
    "Priority_Score_0_100",
    "Current_Preflight_Short",
    "Complexity",
    "Readiness",
    "Criticality",
    "Current_Lane",
    "Wave",
    "Advancement_Potential",
    "Suggested_Target_R",
    "Specific_Variant_IDs",
    "Specific_Variant_Status",
    "Bottleneck",
    "Exact_Next_Evidence",
    "Evidence_Boundary",
    "Assessment_Status",
    "Assessed_On",
    "Register_Version",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def product_dirs() -> list[Path]:
    """Return every live products/<family>/<product> directory."""
    return sorted(
        product
        for family in PRODUCTS_ROOT.iterdir()
        if family.is_dir()
        for product in family.iterdir()
        if product.is_dir()
        and product.name.startswith(("mm-", "unregistered-"))
    )


def level(value: str, prefix: str, *, upper: bool = True) -> int:
    matches = [int(match) for match in re.findall(rf"{prefix}([0-5])", value)]
    if not matches:
        raise ValueError(f"Cannot parse {prefix} level from {value!r}")
    return max(matches) if upper else min(matches)


def wave_for(trend: str, complexity: str, criticality: str, readiness: str) -> str:
    trend_value = float(trend) if trend else 0.0
    c = level(complexity, "C")
    k = level(criticality, "K")
    r = level(readiness, "R")
    if r >= 3 and trend_value >= 70:
        return "W1 R3 NOMINAL — COUPON NEXT"
    if trend_value >= 85 and c <= 2 and k <= 1:
        return "W1 HIGH-TREND / LOW-COMPLEXITY"
    if c <= 2 and k <= 1:
        return "W2 LOW-COMPLEXITY"
    if c <= 3 and k <= 2:
        return "W3 CONTROLLED"
    return "W4 SPECIALIST / HOLD"


def advancement_potential(trend: str, complexity: str, criticality: str, readiness: str) -> str:
    trend_value = float(trend) if trend else 0.0
    c = level(complexity, "C")
    k = level(criticality, "K")
    r = level(readiness, "R")
    if r >= 3:
        return "R3+ ACHIEVED — PHYSICAL EVIDENCE NEXT"
    if trend_value >= 85 and c <= 2 and k <= 1:
        return "HIGH"
    if c <= 3 and k <= 2:
        return "MEDIUM"
    return "LOW / SPECIALIST"


def target_readiness(readiness: str) -> str:
    r = level(readiness, "R")
    if r < 3:
        return "R3 NOMINAL DESIGN INPUTS"
    if r == 3:
        return "R4 INDEPENDENT / PHYSICAL VALIDATION"
    if r == 4:
        return "R5 REPEATED USE / PRODUCTION EVIDENCE"
    return "R5 MAINTAINED"


def research_purposes() -> dict[str, str]:
    legacy = read_xlsx_sheet(LEGACY_WORKBOOK, "Product Matrix")
    legacy_header = legacy[0]
    legacy_sku = legacy_header.index("SKU ID")
    legacy_purpose = legacy_header.index("Customer Job")
    purposes = {str(row[legacy_sku]): str(row[legacy_purpose]).strip() for row in legacy[1:]}
    for path, field in (
        (ADDITIONS_CSV, "Customer_Job"),
        (STRUCTURED_CSV, "Purpose"),
        (VARIANTS_CSV, "Purpose"),
        (GENERATIVE_CSV, "Purpose"),
    ):
        for row in read_csv(path):
            purposes[row["SKU_ID"]] = row[field].strip()
    expected = set(RESEARCH_IDS)
    if set(purposes) != expected or any(len(purpose) < 12 for purpose in purposes.values()):
        raise ValueError("Every research idea must have an explicit purpose/customer job")
    return purposes


def research_rows() -> list[dict[str, str]]:
    priority = {row["SKU_ID"]: row for row in read_csv(PRIORITY_CSV)}
    preflight = {row["SKU_ID"]: row for row in read_csv(PREFLIGHT_CSV)}
    variants = {row["SKU_ID"]: row for row in read_csv(VARIANTS_CSV)}
    structured = {row["SKU_ID"]: row for row in read_csv(STRUCTURED_CSV)}
    generative = {row["SKU_ID"]: row for row in read_csv(GENERATIVE_CSV)}
    additions = {row["SKU_ID"]: row for row in read_csv(ADDITIONS_CSV)}
    purposes = research_purposes()
    expected = set(RESEARCH_IDS)
    if set(priority) != expected or set(preflight) != expected:
        raise ValueError("Priority and preflight sources must cover every declared research ID")

    child_ids: dict[str, list[str]] = defaultdict(list)
    for child in variants.values():
        child_ids[child["Parent_SKU_ID"]].append(child["SKU_ID"])

    output: list[dict[str, str]] = []
    for sku_id in sorted(expected, key=lambda item: int(item.split("-")[1])):
        queue = priority[sku_id]
        estimate = preflight[sku_id]
        variant = variants.get(sku_id)
        children = sorted(child_ids.get(sku_id, []))
        trend = queue["Trend_Score_0_100"]
        complexity = estimate["Complexity_Band"]
        readiness = estimate["Readiness_Band"]
        criticality = estimate["Criticality_Band"]
        current_lane = estimate["Current_Lane"]
        source = variant or structured.get(sku_id) or generative.get(sku_id) or additions.get(sku_id)
        source_next_gate = source.get("Next_Gate", "") if source else ""

        if variant:
            bottleneck = variant["Interface_Evidence_Limit"]
            next_evidence = variant["Next_Gate"]
            boundary = (
                "R3 applies only to this named variant and the cited nominal interface/process baseline. "
                "No physical fit, durability, demand, rights or commercial-release claim is inherited."
            )
            variant_status = "EVIDENCE-BACKED SPECIFIC R3 CHILD"
        elif children:
            bottleneck = (
                "The generic parameter domain remains broader than the evidence. Readiness from the named child "
                "must not be copied back to the generic parent."
            )
            next_evidence = (
                f"Keep the generic parent unchanged; use {', '.join(children)} for the named interface. "
                "Raise the parent only after multiple representative variants, explicit parameter limits, and boundary coupons pass."
            )
            boundary = "Specific-child evidence is deliberately isolated; the generic parent retains its current preflight."
            variant_status = "SPECIFIC R3 CHILD ADDED — GENERIC PARENT UNCHANGED"
        else:
            r = level(readiness, "R")
            if r <= 1:
                bottleneck = (
                    "Scope or interface remains generic and nominal interface/process/verification evidence is incomplete."
                )
                next_evidence = (
                    "Name one exact product revision, published standard, or measured interface; record E3 nominal data, "
                    "pin one exact manufacturing profile, and define a thresholded interface coupon."
                )
            elif r == 2:
                bottleneck = (
                    "Concept inputs exist, but the exact named-interface and/or exact process baseline needed for R3 is open."
                )
                next_evidence = source_next_gate or (
                    "Replace the generic/E2 interface route with E3 nominal evidence for one named variant, pin the exact process, "
                    "and define a measurable coupon."
                )
            else:
                bottleneck = "Nominal design inputs exist; independent dimensional and physical validation is still open."
                next_evidence = queue["Next_Action"]
            boundary = (
                "This is a portfolio planning assessment. Market score, C/R/K/lane and product-release evidence remain separate."
            )
            variant_status = "NO SPECIFIC CHILD ADDED IN THIS PASS"

        output.append(
            {
                "Record_Key": f"RESEARCH:{sku_id}",
                "Record_Type": "RESEARCH_IDEA",
                "Record_ID": sku_id,
                "Parent_SKU_ID": variant["Parent_SKU_ID"] if variant else "",
                "Product": queue["Product"],
                "Product_Path": "",
                "Purpose_or_Intended_Use": purposes[sku_id],
                "Purpose_Documented": "YES",
                "Trend_Score_0_100": trend,
                "Priority_Score_0_100": queue["Priority_Score_0_100"],
                "Current_Preflight_Short": estimate["Preflight_Short"],
                "Complexity": complexity,
                "Readiness": readiness,
                "Criticality": criticality,
                "Current_Lane": current_lane,
                "Wave": wave_for(trend, complexity, criticality, readiness),
                "Advancement_Potential": advancement_potential(trend, complexity, criticality, readiness),
                "Suggested_Target_R": target_readiness(readiness),
                "Specific_Variant_IDs": "; ".join(children),
                "Specific_Variant_Status": variant_status,
                "Bottleneck": bottleneck,
                "Exact_Next_Evidence": next_evidence,
                "Evidence_Boundary": boundary,
                "Assessment_Status": "COMPLETE PORTFOLIO TRIAGE — NOT RELEASE APPROVAL",
                "Assessed_On": ASSESSMENT_DATE,
                "Register_Version": REGISTER_VERSION,
            }
        )
    return output


def product_rows() -> list[dict[str, str]]:
    audit_path = sorted(PRODUCTS_ROOT.glob("PRODUCT-PREFLIGHT-AUDIT-*.json"))[-1]
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    entries = audit["products"]
    if audit.get("product_count") != len(entries):
        raise ValueError("Product preflight audit count does not match its product rows")
    expected_products = {
        product.relative_to(PRODUCTS_ROOT).as_posix() for product in product_dirs()
    }
    audited_products = {str(entry["product"]) for entry in entries}
    if audited_products != expected_products:
        raise ValueError("Product preflight audit is stale against the product-directory inventory")

    portfolio = read_csv(PORTFOLIO_CSV)
    working_by_path = {row["Source_Path"]: row["Working_SKU"] for row in portfolio}
    priority = read_csv(PRIORITY_CSV)
    priority_by_working: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in priority:
        if row["Mapped_Working_SKU"]:
            priority_by_working[row["Mapped_Working_SKU"]].append(row)

    output: list[dict[str, str]] = []
    for entry in sorted(entries, key=lambda item: item["product"]):
        relative_product = f"products/{entry['product']}"
        root = REPO_ROOT / relative_product
        preflight_path = root / entry["preflight_result"]
        purpose_path = root / entry["purpose_document"]
        preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
        scorecard = {
            "complexity": str(preflight["complexity"]["class"]),
            "readiness": str(preflight["readiness"]["level"]),
            "criticality": str(preflight["criticality"]["level"]),
            "lane": str(preflight["decision"]["lane"]),
            "confidence": str(preflight["decision"]["confidence"]),
        }
        compact = (
            f"{scorecard['complexity']} · {scorecard['readiness']} · {scorecard['criticality']} · "
            f"Lane {scorecard['lane']} · {scorecard['confidence']}"
        )
        intended_use = str(preflight.get("scope", {}).get("intended_use", "")).strip()
        purpose_documented = purpose_path.is_file() and len(intended_use) >= 12
        if not purpose_documented:
            raise ValueError(f"Product lacks an explicit purpose: {relative_product}")

        working_sku = working_by_path.get(relative_product, entry.get("project_id", ""))
        mapped = priority_by_working.get(working_sku, [])
        trend_values = [float(row["Trend_Score_0_100"]) for row in mapped if row["Trend_Score_0_100"]]
        priority_values = [float(row["Priority_Score_0_100"]) for row in mapped if row["Priority_Score_0_100"]]
        trend = f"{max(trend_values):g}" if trend_values else ""
        priority_score = f"{max(priority_values):g}" if priority_values else ""
        blockers = list(preflight["readiness"].get("blocking_unknowns", []))
        actions = [str(item.get("action", "")).strip() for item in preflight.get("next_actions", [])]
        bottleneck = "; ".join(blockers) or "No blocking readiness unknown recorded; follow the next verification gate."
        next_evidence = " ".join(action for action in actions if action) or "Record the next controlled validation result."

        if entry["product"] == "printer-workshop/unregistered-kobra3max-purge-catcher":
            bottleneck = (
                "R2 retained: the documented Kobra 3 Max context and independently measured 17 mm screw pitch improve the "
                "interface evidence, but a complete variant-confirmed clean-room envelope, screw hardware/tolerances, full "
                "motion keep-outs, and the moving-diversion versus moving-storage architecture decision remain open."
            )
            next_evidence = (
                "Approve one storage architecture; record screw head/thread/length/engagement and clean-room envelope/tolerances "
                "from the user's machine; build the independent 17 mm hole-pattern plus outline coupon; sweep powered-off full "
                "XYZ and service removal; then observe supervised low/mid/high-Z purge before any R4 claim."
            )
        elif entry["product"] == "furniture-systems/mm-sys-001-alex-inventory-workplace-tray":
            bottleneck = (
                "R1 retained: exact ALEX article/revision and real drawer interface are not identified; the 209.3/210/210.7 mm "
                "gauges are digital artifacts without a recorded physical result or exact process."
            )
            next_evidence = (
                "Record the exact ALEX article/revision; measure the real drawer datums and uncertainty; pin the exact process; "
                "print the three width gauges; record the selected fit before changing the tray."
            )

        output.append(
            {
                "Record_Key": f"PRODUCT:{entry['product']}",
                "Record_Type": "PRODUCT_DIRECTORY",
                "Record_ID": str(entry.get("project_id", working_sku)),
                "Parent_SKU_ID": "",
                "Product": str(preflight.get("product", entry["product"])),
                "Product_Path": relative_product,
                "Purpose_or_Intended_Use": intended_use,
                "Purpose_Documented": "YES",
                "Trend_Score_0_100": trend,
                "Priority_Score_0_100": priority_score,
                "Current_Preflight_Short": compact,
                "Complexity": scorecard["complexity"],
                "Readiness": scorecard["readiness"],
                "Criticality": scorecard["criticality"],
                "Current_Lane": scorecard["lane"],
                "Wave": wave_for(trend, scorecard["complexity"], scorecard["criticality"], scorecard["readiness"]),
                "Advancement_Potential": advancement_potential(
                    trend, scorecard["complexity"], scorecard["criticality"], scorecard["readiness"]
                ),
                "Suggested_Target_R": target_readiness(scorecard["readiness"]),
                "Specific_Variant_IDs": "",
                "Specific_Variant_Status": "CURRENT PRODUCT — CREATE A SEPARATE NAMED VARIANT IF SCOPE NARROWS",
                "Bottleneck": bottleneck,
                "Exact_Next_Evidence": next_evidence,
                "Evidence_Boundary": (
                    "Uses the live product preflight and purpose document. No R increase is assigned without the stated "
                    "interface, process, dimensional or physical evidence."
                ),
                "Assessment_Status": "COMPLETE PORTFOLIO TRIAGE — NOT RELEASE APPROVAL",
                "Assessed_On": ASSESSMENT_DATE,
                "Register_Version": REGISTER_VERSION,
            }
        )
    return output


def build_rows() -> list[dict[str, str]]:
    research = research_rows()
    products = product_rows()
    rows = research + products
    keys = [row["Record_Key"] for row in rows]
    if len(research) != RESEARCH_COUNT or len(products) != len(product_dirs()) or len(keys) != len(set(keys)):
        raise ValueError("Readiness advancement register coverage or key uniqueness failed")
    if any(row["Purpose_Documented"] != "YES" for row in rows):
        raise ValueError("Every register record must have an explicit purpose")
    return rows


def render(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the checked-in register is stale")
    args = parser.parse_args()
    content = render(build_rows())
    product_count = len(product_dirs())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != content:
            raise SystemExit(f"stale or missing readiness advancement register: {OUTPUT}")
        print(f"PASS: {OUTPUT} is current with {RESEARCH_COUNT + product_count} records")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT} with {RESEARCH_COUNT} research and {product_count} product records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
