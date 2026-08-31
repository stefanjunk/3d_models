#!/usr/bin/env python3
"""Rebuild the portfolio workbook from all canonical CSV and preflight sources."""

from __future__ import annotations

import argparse
import csv
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "business/02-portfolio/product-portfolio.csv"
BUILD_SCRIPT = ROOT / "business/tools/build_product_workbook.py"


def validate_record_ids(record_ids: set[str]) -> None:
    if not record_ids:
        return
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        existing = {row["Record_ID"] for row in csv.DictReader(handle)}
    unknown = sorted(record_ids.difference(existing))
    if unknown:
        raise ValueError(f"Unknown portfolio record ID(s): {', '.join(unknown)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--record-id",
        action="append",
        default=[],
        help="Compatibility option: validate this record ID before the canonical full rebuild.",
    )
    args = parser.parse_args()
    validate_record_ids(set(args.record_id))
    namespace = runpy.run_path(str(BUILD_SCRIPT), run_name="portfolio_workbook_builder")
    namespace["main"]()
    print("Rebuilt the complete workbook so preflight and research overlays remain intact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
