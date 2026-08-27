#!/usr/bin/env python3
"""Synchronize canonical CSV rows into the Portfolio worksheet."""

from __future__ import annotations

import argparse
import csv
import html
import os
import re
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "business/02-portfolio/product-portfolio.csv"
XLSX_PATH = ROOT / "business/02-portfolio/product-portfolio.xlsx"
SHEET_NAME = "xl/worksheets/sheet3.xml"


def column_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def inline_cell(column: str, row_number: int, value: str) -> str:
    escaped = html.escape(value, quote=False)
    return (
        f'<c r="{column}{row_number}" s="6" t="inlineStr">'
        f'<is><t xml:space="preserve">{escaped}</t></is></c>'
    )


def row_xml(record: dict[str, str], fieldnames: list[str], row_number: int) -> str:
    cells = "".join(
        inline_cell(column_name(index), row_number, record.get(field, ""))
        for index, field in enumerate(fieldnames, start=1)
    )
    return f'<row r="{row_number}">{cells}</row>'


def sync_workbook(update_record_ids: set[str] | None = None) -> tuple[int, int]:
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames
    if not fieldnames:
        raise ValueError("portfolio CSV has no header")

    with zipfile.ZipFile(XLSX_PATH, "r") as archive:
        members = [(item, archive.read(item.filename)) for item in archive.infolist()]

    updated_members: list[tuple[zipfile.ZipInfo, bytes]] = []
    added = 0
    updated = 0
    for item, content in members:
        if item.filename != SHEET_NAME:
            updated_members.append((item, content))
            continue

        xml = content.decode("utf-8")
        existing_rows = {
            html.unescape(record_id): int(row_number)
            for row_number, record_id in re.findall(
                r'<row r="(\d+)"[^>]*>.*?<c r="A\d+"[^>]*>.*?'
                r'<t[^>]*>(.*?)</t>.*?</c>.*?</row>',
                xml,
                flags=re.DOTALL,
            )
        }
        row_numbers = [int(value) for value in re.findall(r'<row r="(\d+)"', xml)]
        next_row = max(row_numbers) + 1
        new_rows: list[str] = []
        for record in rows:
            record_id = record["Record_ID"]
            if record_id in existing_rows:
                if update_record_ids and record_id in update_record_ids:
                    row_number = existing_rows[record_id]
                    replacement = row_xml(record, fieldnames, row_number)
                    pattern = rf'<row r="{row_number}"[^>]*>.*?</row>'
                    xml, count = re.subn(pattern, replacement, xml, count=1, flags=re.DOTALL)
                    if count != 1:
                        raise ValueError(f"could not replace workbook row for {record_id}")
                    updated += 1
                continue
            new_rows.append(row_xml(record, fieldnames, next_row))
            next_row += 1
            added += 1

        if new_rows:
            last_row = next_row - 1
            xml = xml.replace("</sheetData>", "".join(new_rows) + "</sheetData>", 1)
            xml = re.sub(
                r'(<dimension ref="A1:[A-Z]+)\d+("/>)',
                rf"\g<1>{last_row}\2",
                xml,
                count=1,
            )
            xml = re.sub(
                r'(<autoFilter ref="A1:[A-Z]+)\d+("/>)',
                rf"\g<1>{last_row}\2",
                xml,
                count=1,
            )
        updated_members.append((item, xml.encode("utf-8")))

    temporary_fd, temporary_name = tempfile.mkstemp(
        prefix="product-portfolio-sync-", suffix=".xlsx", dir=XLSX_PATH.parent
    )
    os.close(temporary_fd)
    try:
        with zipfile.ZipFile(temporary_name, "w") as archive:
            for item, content in updated_members:
                archive.writestr(item, content)
        os.replace(temporary_name, XLSX_PATH)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
    return added, updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--record-id",
        action="append",
        default=[],
        help="Replace this existing workbook record from the CSV; may be repeated.",
    )
    args = parser.parse_args()
    added, updated = sync_workbook(set(args.record_id))
    print(f"appended {added} missing row(s); updated {updated} selected row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
