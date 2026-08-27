#!/usr/bin/env python3
"""Update portfolio path fields after the self-contained product migration."""

from __future__ import annotations

import csv
import html
import os
import re
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "business/02-portfolio/product-portfolio.csv"
XLSX_PATH = ROOT / "business/02-portfolio/product-portfolio.xlsx"

PRODUCT_PATHS = {
    "MM-ORG-001": "products/organization-storage/mm-org-001-drawerfit-modular",
    "MM-PER-001": "products/organization-storage/mm-per-001-nameform-bookends",
    "MM-ORG-002": "products/organization-storage/mm-org-002-shelffit-mini-bins",
    "MM-ORG-003": "products/organization-storage/mm-org-003-modern-carbon-desk-organizer",
    "MM-BTH-001": "products/organization-storage/mm-bth-001-premium-over-toilet-shelf",
    "MM-BTH-002": "products/organization-storage/mm-bth-002-toilet-paper-fifo-system",
    "MM-BTH-003": "products/home-kitchen-garden/mm-bth-003-linear-shower-drain-hair-trap",
    "MM-MKR-001": "products/printer-workshop/mm-mkr-001-cybervault-nozzle-case",
    "MM-TOOL-001": "products/printer-workshop/mm-tool-001-kobra3max-enclosure",
    "MM-TOOL-002": "products/printer-workshop/mm-tool-002-filament-drybox-system",
    "MM-ART-001": "products/art-decor/mm-art-001-fox-mesh-collection",
    "MM-AUTO-001": "products/art-decor/mm-auto-001-opel-grandland-2018-mesh",
    "MM-ART-002": "products/art-decor/mm-art-002-plant-mesh",
    "MM-ART-003": "products/art-decor/mm-art-003-unicorn-mesh-collection",
    "MM-ACC-001": "products/wearables/mm-acc-001-honeycomb-hair-clip",
    "MM-DEC-001": "products/art-decor/mm-dec-001-marble-tile",
    "MM-DEC-002": "products/art-decor/mm-dec-002-roman-pillar",
    "MM-SHO-001": "products/wearables/mm-sho-001-barefoot-shoe-collection",
    "MM-TOY-001": "products/toys-games/mm-toy-001-rubber-ball-toy-popper",
    "MM-BOAT-001": "products/toys-games/mm-boat-001-fisher-boat",
    "MM-BOAT-002": "products/toys-games/mm-boat-002-fisher-boat-detailed",
    "MM-BOAT-003": "products/toys-games/mm-boat-003-flapping-tail-submarine",
    "MM-BOAT-004": "products/toys-games/mm-boat-004-rocket-boat",
    "MM-BOAT-005": "products/toys-games/mm-boat-005-toy-boat",
    "MM-DEC-003": "products/home-kitchen-garden/mm-dec-003-sunflower-bowl-tray",
    "MM-TOOL-003": "products/printer-workshop/mm-tool-003-kobra3max-camera-arm",
    "MM-ART-004": "products/art-decor/mm-art-004-capybara-mesh-collection",
    "MM-TOOL-004": "products/printer-workshop/mm-tool-004-claw-hammer-mesh",
    "MM-HOME-001": "products/home-kitchen-garden/mm-home-001-cup-and-measuring-spoon",
    "MM-HOB-001": "products/toys-games/mm-hob-001-polygonal-dice-tower",
    "MM-ART-005": "products/art-decor/mm-art-005-fish-mesh-collection",
    "MM-GAR-001": "products/home-kitchen-garden/mm-gar-001-rainwater-filter-well",
    "MM-ART-006": "products/art-decor/mm-art-006-mouse-mesh-collection",
    "MM-PUZ-001": "products/toys-games/mm-puz-001-parametric-labyrinth-gift-box",
    "MM-PUZ-002": "products/toys-games/mm-puz-002-mystery-puzzle-box",
    "MM-ART-007": "products/art-decor/mm-art-007-racehorse-mesh-collection",
    "MM-ART-008": "products/art-decor/mm-art-008-sports-car-mesh",
    "MM-WALL-001": "products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf",
    "MM-ART-009": "products/art-decor/mm-art-009-whale-mesh-collection",
    "MM-SYS-001": "products/furniture-systems/mm-sys-001-alex-inventory-workplace-tray",
    "MM-SYS-002": "products/furniture-systems/mm-sys-002-bror-tool-shadow-tray",
    "MM-SYS-003": "products/furniture-systems/mm-sys-003-pax-asymmetric-accessory-grid",
    "MM-SYS-004": "products/furniture-systems/mm-sys-004-billy-collection-riser",
    "MM-SYS-005": "products/furniture-systems/mm-sys-005-bror-shadow-board-workflow-cluster",
    "MM-SYS-006": "products/furniture-systems/mm-sys-006-kallax-boardgame-matrix",
    "MM-SYS-007": "products/furniture-systems/mm-sys-007-platsa-collection-cells",
    "MM-SYS-008": "products/furniture-systems/mm-sys-008-skadis-precision-tool-cluster",
    "MM-SYS-009": "products/furniture-systems/mm-sys-009-besta-passive-media-topology",
    "MM-SYS-010": "products/furniture-systems/mm-sys-010-omar-ventilated-shelf-deck",
    "MM-SYS-011": "products/furniture-systems/mm-sys-011-boaxel-cleaning-accessory-dock",
    "MM-SYS-012": "products/furniture-systems/mm-sys-012-besta-controller-and-media-tray",
    "MM-SYS-013": "products/furniture-systems/mm-sys-013-trofast-adult-workshop-insert",
    "MM-SYS-014": "products/furniture-systems/mm-sys-014-kallax-creative-material-cassette",
    "MM-SYS-015": "products/furniture-systems/mm-sys-015-boaxel-basket-microsorter",
    "MM-SYS-016": "products/furniture-systems/mm-sys-016-malm-fold-size-drawer-dividers",
    "MM-SYS-017": "products/furniture-systems/mm-sys-017-ivar-no-drill-side-inventory-rail",
    "MM-SYS-018": "products/furniture-systems/mm-sys-018-billy-collection-display-matrix",
    "MM-SYS-019": "products/furniture-systems/mm-sys-019-lagkapten-alex-reversible-cable-rail",
    "MM-SYS-020": "products/furniture-systems/mm-sys-020-lack-leg-two-pocket-mini-dock",
}

# These products retained an existing wrapper directory so that no files were
# merged or overwritten during migration.
EVIDENCE_BASES = {
    "MM-ORG-003": PRODUCT_PATHS["MM-ORG-003"] + "/modern-carbon-desk-organizer-compact-v2.0.0",
    "MM-MKR-001": PRODUCT_PATHS["MM-MKR-001"] + "/CyberVault-R4-WM1-RELEASE",
    "MM-TOOL-001": PRODUCT_PATHS["MM-TOOL-001"] + "/kobra3max_enclosure_project",
    "MM-TOOL-003": PRODUCT_PATHS["MM-TOOL-003"] + "/Kobra3Max_Slim_Camera_Arm_v6_FROM_ORIGINAL_MODEL/k3m_camera_arm_v6_from_original_model",
    "MM-TOY-001": PRODUCT_PATHS["MM-TOY-001"] + "/rubber_ball_toy_popper",
    "MM-DEC-003": PRODUCT_PATHS["MM-DEC-003"] + "/sunflower_bowl",
    "MM-HOB-001": PRODUCT_PATHS["MM-HOB-001"] + "/unicorn_tower/polygonal-dice-tower-FINAL-release-0.1.2-g1",
    "MM-WALL-001": PRODUCT_PATHS["MM-WALL-001"] + "/setzkasten/honeycomb-wood-wall-shelf",
}


def relocated_evidence(sku: str, old_source: str, evidence: str) -> str:
    if not evidence:
        return evidence
    base = EVIDENCE_BASES.get(sku, PRODUCT_PATHS[sku])
    if evidence == old_source:
        return base
    prefix = old_source.rstrip("/") + "/"
    if evidence.startswith(prefix):
        return base.rstrip("/") + "/" + evidence[len(prefix) :]
    raise ValueError(f"{sku}: evidence path is outside its old source path: {evidence}")


def update_csv() -> int:
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames
    if not fieldnames:
        raise ValueError("portfolio CSV has no header")

    changed = 0
    for row in rows:
        sku = row["Working_SKU"]
        if sku not in PRODUCT_PATHS:
            raise KeyError(f"missing product-path mapping for {sku}")
        old_source = row["Source_Path"]
        row["Model_Evidence_Path"] = relocated_evidence(
            sku, old_source, row.get("Model_Evidence_Path", "")
        )
        row["Source_Path"] = PRODUCT_PATHS[sku]
        changed += 1

    temporary = CSV_PATH.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, CSV_PATH)
    return changed


def cell_value(row_xml: str, column: str) -> str:
    match = re.search(
        rf'<c r="{column}\d+"[^>]*>.*?<t[^>]*>(.*?)</t>.*?</c>', row_xml, re.DOTALL
    )
    return html.unescape(match.group(1)) if match else ""


def replace_cell_value(row_xml: str, column: str, value: str) -> str:
    pattern = re.compile(
        rf'(<c r="{column}\d+"[^>]*>.*?<t[^>]*>)(.*?)(</t>.*?</c>)', re.DOTALL
    )
    updated, count = pattern.subn(
        lambda match: match.group(1) + escape(value) + match.group(3), row_xml, count=1
    )
    if count != 1:
        raise ValueError(f"could not update column {column} in workbook row")
    return updated


def update_xlsx() -> int:
    sheet_name = "xl/worksheets/sheet3.xml"
    with zipfile.ZipFile(XLSX_PATH, "r") as archive:
        members = [(item, archive.read(item.filename)) for item in archive.infolist()]

    changed = 0
    updated_members: list[tuple[zipfile.ZipInfo, bytes]] = []
    for item, content in members:
        if item.filename != sheet_name:
            updated_members.append((item, content))
            continue

        xml = content.decode("utf-8")

        def update_row(match: re.Match[str]) -> str:
            nonlocal changed
            row_xml = match.group(0)
            sku = cell_value(row_xml, "B")
            if sku not in PRODUCT_PATHS:
                return row_xml
            old_source = cell_value(row_xml, "E")
            evidence = cell_value(row_xml, "V")
            row_xml = replace_cell_value(row_xml, "E", PRODUCT_PATHS[sku])
            row_xml = replace_cell_value(
                row_xml, "V", relocated_evidence(sku, old_source, evidence)
            )
            changed += 1
            return row_xml

        xml = re.sub(r"<row\b.*?</row>", update_row, xml, flags=re.DOTALL)
        updated_members.append((item, xml.encode("utf-8")))

    if changed != len(PRODUCT_PATHS):
        raise ValueError(
            f"updated {changed} workbook rows; expected {len(PRODUCT_PATHS)}"
        )

    temporary_fd, temporary_name = tempfile.mkstemp(
        prefix="product-portfolio-", suffix=".xlsx", dir=XLSX_PATH.parent
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
    return changed


def main() -> int:
    csv_rows = update_csv()
    xlsx_rows = update_xlsx()
    print(f"updated {csv_rows} CSV rows and {xlsx_rows} workbook rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
