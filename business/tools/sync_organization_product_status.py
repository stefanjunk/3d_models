#!/usr/bin/env python3
"""Synchronize implemented MM-ORG research products into business control CSVs."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from build_product_workbook import read_xlsx_sheet

ROOT = Path(__file__).resolve().parents[2]
BUSINESS = ROOT / "business"
PRODUCTS = ROOT / "products" / "organization-storage"
ADDITIONS = BUSINESS / "02-portfolio" / "research-ideas-additions.csv"
LEGACY = ROOT / "research" / "market" / "JuSt_Innovation_3D_Print_Commercial_Product_Matrix_2026.xlsx"
IMPLEMENTATION = BUSINESS / "02-portfolio" / "research-ideas-implementation.csv"
PORTFOLIO = BUSINESS / "02-portfolio" / "product-portfolio.csv"
AUDIT_DATE = "2026-08-28"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def source_records() -> dict[str, dict[str, str]]:
    records = {row["SKU_ID"]: row for row in read_csv(ADDITIONS)}
    rows = read_xlsx_sheet(LEGACY, "Product Matrix")
    for values in rows[1:]:
        raw = dict(zip(rows[0], values))
        sku = str(raw["SKU ID"])
        records[sku] = {
            "SKU_ID": sku,
            "Product": str(raw["Product"]),
            "Product_Family": str(raw["Product Family"]),
            "Strategy_Fit": "Core" if "organizer" in str(raw["Product Family"]).lower() else "Core adjacent",
            "Risk_Score": str(raw["Risk Score"]),
        }
    return records


def product_sku(folder: Path) -> str | None:
    for name in ["design-spec.yaml", "requirements-review.md", "learning-trace.yaml", "README.md"]:
        path = folder / name
        if not path.exists():
            continue
        match = re.search(r"SKU[-_/](\d{3})|SKU-(\d{3})", path.read_text(encoding="utf-8"))
        if match:
            return f"SKU-{match.group(1) or match.group(2)}"
    return None


def candidate_passes(folder: Path) -> bool:
    path = folder / "validation" / "print-candidate-report.json"
    if not path.exists():
        return False
    try:
        return json.loads(path.read_text())["status"] == "PASS"
    except (KeyError, json.JSONDecodeError):
        return False


def implemented_products() -> list[dict[str, object]]:
    sources = source_records()
    found = []
    for folder in sorted(PRODUCTS.glob("mm-org-[0-9][0-9][0-9]-*")):
        match = re.match(r"mm-org-(\d{3})-", folder.name)
        if not match or int(match.group(1)) < 9:
            continue
        sku = product_sku(folder)
        if not sku or sku not in sources:
            continue
        three_mf = sorted((folder / "exports" / "3mf").glob("*.3mf"))
        if not three_mf:
            continue
        found.append({
            "working_sku": f"MM-ORG-{match.group(1)}",
            "sku": sku,
            "folder": folder,
            "evidence": three_mf[0],
            "candidate": candidate_passes(folder),
            "source": sources[sku],
        })
    return found


def implementation_rows(products: list[dict[str, object]]) -> list[dict[str, str]]:
    existing = {row["SKU_ID"]: row for row in read_csv(IMPLEMENTATION)}
    for item in products:
        source = item["source"]
        stage = "P2-digital-print-candidate" if item["candidate"] else "P2-digital-candidate"
        existing[item["sku"]] = {
            "SKU_ID": item["sku"],
            "Implementation_Status": "MODEL_EXISTS",
            "Mapped_Working_SKU": item["working_sku"],
            "Product_Package": str(item["folder"].relative_to(ROOT)),
            "Model_Evidence": str(item["evidence"].relative_to(ROOT)),
            "Workflow_Stage": stage,
            "Implementation_Updated": AUDIT_DATE,
            "Implementation_Notes": (
                f"Controlled parametric DRAFT package for {source['Product']}; "
                + ("digital print-candidate validation passes; " if item["candidate"] else "geometry/interface validation exists; ")
                + "physical qualification and commercial release remain open."
            ),
        }
    return sorted(existing.values(), key=lambda row: int(row["SKU_ID"].split("-")[1]))


def portfolio_rows(products: list[dict[str, object]]) -> list[dict[str, str]]:
    rows = read_csv(PORTFOLIO)
    fields = list(rows[0])
    by_working = {row["Working_SKU"]: row for row in rows}
    next_id = max(int(row["Record_ID"].split("-")[1]) for row in rows) + 1
    for item in products:
        if item["working_sku"] in by_working:
            continue
        source = item["source"]
        exact = bool(item["candidate"])
        risk = source.get("Risk_Score", "2")
        row = {field: "" for field in fields}
        row.update({
            "Record_ID": f"PORT-{next_id:03d}",
            "Working_SKU": item["working_sku"],
            "Product_or_Model": source["Product"],
            "Category": source.get("Product_Family", "Organization and storage"),
            "Source_Path": str(item["folder"].relative_to(ROOT)),
            "Origin_Class": "Local controlled project",
            "Strategy_Fit": source.get("Strategy_Fit", "Core"),
            "Lifecycle_Stage": "P2 Digital print candidate" if exact else "P2 Digital candidate",
            "Commercial_Existing": "No",
            "Digital_Evidence": "Parametric source, neutral/manufacturing exports, DRAFT 3MF and machine-readable validation package" + (" including exact Anycubic slicer evidence" if exact else ""),
            "Physical_Evidence": "No repository physical print or measured fit/use evidence; human physical gates remain open",
            "Rights_Provenance": "Local parametric source; broader commercial source/component register remains open",
            "Safety_Risk": f"Portfolio risk {risk}/5; product-specific physical fit/use and edge review required",
            "Digital_Offer": "Hold until physical qualification",
            "Printed_Offer": "Hold until physical qualification",
            "Website_Status": "No catalog item",
            "Initial_Portfolio_Role": "Ranked research-idea implementation",
            "Priority": "P1 NEXT",
            "Next_Gate": "Print the first-fit coupon where supplied, then the unchanged candidate; complete product-specific physical tests, safety, watermark and commercial review",
            "Notes": "DRAFT only; no physical-performance, compatibility or sale claim",
            "Model_Status": "YES — controlled CAD/source + model artifact",
            "Model_Evidence_Path": str(item["evidence"].relative_to(ROOT)),
            "Model_Audit_Date": AUDIT_DATE,
        })
        rows.append(row)
        by_working[item["working_sku"]] = row
        next_id += 1
    return rows


def csv_text(rows: list[dict[str, str]], fields: list[str], quote_all: bool) -> str:
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    products = implemented_products()
    implementation = implementation_rows(products)
    portfolio = portfolio_rows(products)
    implementation_fields = list(read_csv(IMPLEMENTATION)[0])
    portfolio_fields = list(read_csv(PORTFOLIO)[0])
    outputs = {
        IMPLEMENTATION: csv_text(implementation, implementation_fields, False),
        PORTFOLIO: csv_text(portfolio, portfolio_fields, True),
    }
    changed = [path for path, content in outputs.items() if path.read_text(encoding="utf-8") != content]
    if args.check:
        if changed:
            for path in changed:
                print(f"OUTDATED {path.relative_to(ROOT)}")
            raise SystemExit(1)
        print(f"Synchronized {len(products)} implemented organization products")
        return
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    print(f"Updated {len(products)} implemented products; portfolio rows={len(portfolio)}")


if __name__ == "__main__":
    main()
