#!/usr/bin/env python3
"""Audit whether every portfolio row has a local 3D model artifact.

The portfolio CSV remains the product source of truth. This script adds or
refreshes three explicit model-status columns and emits detailed CSV/Markdown
evidence. It ignores concepts, reports, validation files, coupons, copied
watermark assets and every path under an ``external`` directory.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


BUSINESS = Path(__file__).resolve().parents[1]
WORKSPACE = BUSINESS.parent
PORTFOLIO = BUSINESS / "02-portfolio" / "product-portfolio.csv"
AUDIT_CSV = BUSINESS / "02-portfolio" / "model-artifact-audit.csv"
AUDIT_MD = BUSINESS / "02-portfolio" / "model-artifact-audit.md"

MODEL_EXTENSIONS = {".3mf", ".stl", ".step", ".stp", ".obj", ".glb", ".gltf", ".fcstd", ".blend"}
SOURCE_EXTENSIONS = {".py", ".scad", ".fcstd", ".blend"}
IGNORE_PARTS = {
    ".git", "__pycache__", "external", "archive", "assets", "concept",
    "previews", "reports", "validation", "coupons",
}
IGNORE_NAME_TOKENS = {"coupon", "calibration", "test-piece", "test_piece"}
PREFERENCE = {ext: rank for rank, ext in enumerate((
    ".3mf", ".stl", ".step", ".stp", ".fcstd", ".blend", ".obj", ".glb", ".gltf", ".scad", ".py"
))}


def ignored(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & IGNORE_PARTS:
        return True
    name = path.name.lower()
    return any(token in name for token in IGNORE_NAME_TOKENS)


def candidates_for(row: dict[str, str]) -> tuple[Path, list[Path]]:
    source = WORKSPACE / row["Source_Path"]
    if not source.exists():
        return source, []
    if source.is_file():
        return source, [source]
    files = [path for path in source.rglob("*") if path.is_file() and not ignored(path.relative_to(source))]
    return source, sorted(set(files))


def audit_row(row: dict[str, str], audit_date: str) -> dict[str, str]:
    source, files = candidates_for(row)
    model_files = [path for path in files if path.suffix.lower() in MODEL_EXTENSIONS]
    source_files = [path for path in files if path.suffix.lower() in SOURCE_EXTENSIONS]
    three_mf = [path for path in model_files if path.suffix.lower() == ".3mf"]
    # A source file is useful supporting evidence, but portfolio coverage is
    # fail-closed on an actual neutral/manufacturing model artifact.
    model_present = bool(model_files)
    controlled = bool(source_files and model_files)
    if controlled:
        status = "YES — controlled CAD/source + model artifact"
    elif model_files:
        status = "YES — model artifact present"
    elif source_files:
        status = "NO — source found, no local 3D model artifact"
    else:
        status = "NO — no local 3D model found"
    evidence_pool = model_files or source_files
    evidence_pool = sorted(
        evidence_pool,
        key=lambda path: (PREFERENCE.get(path.suffix.lower(), 99), str(path).lower()),
    )
    evidence = str(evidence_pool[0].relative_to(WORKSPACE)) if evidence_pool else ""
    lifecycle = row["Lifecycle_Stage"]
    contradiction = ""
    if lifecycle.startswith("P0") and model_present:
        contradiction = "P0 stage but model exists"
    elif (lifecycle.startswith("P1") or lifecycle.startswith("P2")) and not model_present:
        contradiction = f"{lifecycle} but no model found"
    return {
        "Record_ID": row["Record_ID"],
        "Working_SKU": row["Working_SKU"],
        "Product_or_Model": row["Product_or_Model"],
        "Lifecycle_Stage": lifecycle,
        "Portfolio_Source_Path": row["Source_Path"],
        "Source_Path_Exists": "YES" if source.exists() else "NO",
        "Model_Status": status,
        "Parametric_Source_Present": "YES" if source_files else "NO",
        "Manufacturing_or_Neutral_Model_Present": "YES" if model_files else "NO",
        "3MF_Present": "YES" if three_mf else "NO",
        "Representative_Model_Evidence": evidence,
        "Model_File_Count": str(len(model_files)),
        "Source_File_Count": str(len(source_files)),
        "Portfolio_Contradiction": contradiction,
        "Audit_Date": audit_date,
    }


def write_audit(rows: list[dict[str, str]]) -> None:
    AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter("YES" if row["Model_Status"].startswith("YES") else "NO" for row in rows)
    source_count = sum(row["Parametric_Source_Present"] == "YES" for row in rows)
    artifact_count = sum(row["Manufacturing_or_Neutral_Model_Present"] == "YES" for row in rows)
    three_mf_count = sum(row["3MF_Present"] == "YES" for row in rows)
    contradictions = [row for row in rows if row["Portfolio_Contradiction"]]
    lines = [
        "# Portfolio 3D-model artifact audit",
        "",
        f"Audit date: {rows[0]['Audit_Date']}",
        "",
        f"- Portfolio records: **{len(rows)}**",
        f"- Records with a local neutral/manufacturing 3D artifact: **{artifact_count}**",
        f"- Records without a local 3D artifact: **{counts['NO']}**",
        f"- Records with detected parametric source: **{source_count}**",
        f"- Records with at least one 3MF: **{three_mf_count}**",
        f"- Lifecycle/model contradictions: **{len(contradictions)}**",
        "",
        "A `YES` requires a local neutral/manufacturing 3D artifact. Parametric source is reported separately. Neither proves rights, slicability, fit, strength, physical qualification or commercial release.",
        "",
        "| Record | SKU | Product | Lifecycle | Model status | Representative evidence |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['Record_ID']} | {row['Working_SKU']} | {row['Product_or_Model']} | "
            f"{row['Lifecycle_Stage']} | {row['Model_Status']} | `{row['Representative_Model_Evidence']}` |"
        )
    if contradictions:
        lines.extend(["", "## Contradictions", ""])
        for row in contradictions:
            lines.append(f"- {row['Record_ID']}: {row['Portfolio_Contradiction']}")
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_portfolio(rows: list[dict[str, str]], audited: list[dict[str, str]]) -> None:
    by_id = {row["Record_ID"]: row for row in audited}
    fields = list(rows[0])
    for field in ("Model_Status", "Model_Evidence_Path", "Model_Audit_Date"):
        if field not in fields:
            fields.append(field)
    for row in rows:
        audit = by_id[row["Record_ID"]]
        row["Model_Status"] = audit["Model_Status"]
        row["Model_Evidence_Path"] = audit["Representative_Model_Evidence"]
        row["Model_Audit_Date"] = audit["Audit_Date"]
    with PORTFOLIO.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-date", default="2026-08-26")
    parser.add_argument("--update-portfolio", action="store_true")
    args = parser.parse_args()
    with PORTFOLIO.open(newline="", encoding="utf-8") as handle:
        portfolio_rows = list(csv.DictReader(handle))
    audited = [audit_row(row, args.audit_date) for row in portfolio_rows]
    write_audit(audited)
    if args.update_portfolio:
        update_portfolio(portfolio_rows, audited)
    missing = [row for row in audited if row["Model_Status"].startswith("NO")]
    contradictions = [row for row in audited if row["Portfolio_Contradiction"]]
    print(f"records={len(audited)} models={len(audited)-len(missing)} missing={len(missing)} contradictions={len(contradictions)}")
    for row in missing:
        print(f"MISSING {row['Record_ID']} {row['Working_SKU']} {row['Product_or_Model']}")
    for row in contradictions:
        print(f"CONTRADICTION {row['Record_ID']} {row['Portfolio_Contradiction']}")
    raise SystemExit(1 if missing or contradictions else 0)


if __name__ == "__main__":
    main()
