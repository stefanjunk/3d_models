#!/usr/bin/env python3
"""Build the multi-sheet product portfolio workbook with Python stdlib only."""

from __future__ import annotations

import csv
import datetime as dt
import posixpath
import re
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_CSV = ROOT / "02-portfolio" / "product-portfolio.csv"
TASKS_CSV = ROOT / "07-roadmap" / "mvp-tasks.csv"
OUTPUT = ROOT / "02-portfolio" / "product-portfolio.xlsx"
RESEARCH_WORKBOOK = ROOT.parent / "market_research" / "JuSt_Innovation_3D_Print_Commercial_Product_Matrix_2026.xlsx"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


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
    if text in {"COMPLETE", "YES", "PASS", "P7 LIVE", "P6 STAGED", "P5 COMMERCIAL RELEASE"}:
        return 3
    if "BLOCK" in text or text in {"EXCLUDED", "VERY HIGH"}:
        return 5
    if text.startswith("P0 ") or text.startswith("P1 ") or text in {"HOLD", "UNKNOWN", "NOT STARTED"}:
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
        "art/external_models", "blasters/external", "boats/external", "bowls/external",
        "camera_mount/external", "clips/external", "dough_cutter/external", "fidgets/external",
        "gravity_knife/external", "music/external", "organizer/external", "puzzles/external",
        "shoes/external", "stamps/external", "walls/external",
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
    for imported in (legacy_product_matrix, legacy_unit_economics, legacy_family_strategy):
        imported[0].append("Business_Workspace_Interpretation")
        for row in imported[1:]:
            row.extend([""] * (len(imported[0]) - 1 - len(row)))
            row.append("Research hypothesis only; not an existing, qualified, staged or live product")

    stages_present: dict[str, int] = {}
    for row in portfolio[1:]:
        stage = row[header.index("Lifecycle_Stage")]
        stages_present[stage] = stages_present.get(stage, 0) + 1
    summary = [
        ["Metric", "Value", "Interpretation"],
        ["Review date", "2026-08-21", "Repository-evidence snapshot"],
        ["Portfolio records", len(portfolio) - 1, "Includes planned concepts and non-external local model families"],
        ["Initial launch SKUs", len(initial) - 1, "Fixed target scope"],
        ["Legacy research concepts retained", len(legacy_product_matrix) - 1, "Separate research sheet; no release status implied"],
        ["Commercially existing P5+", 0, "No product may be sold yet"],
        ["Staged P6", 0, "No real release staged"],
        ["Live P7", 0, "No live product"],
        ["External directories excluded", len(external_paths), "Never included in portfolio candidates"],
        ["P0 ideas", stages_present.get("P0 Idea", 0), "CAD not yet controlled"],
        ["P1 model present", stages_present.get("P1 Model present", 0), "Model exists but evidence is incomplete"],
        ["P2 digital candidates", stages_present.get("P2 Digital candidate", 0), "Digital evidence does not equal a product release"],
        ["Launch recommendation", "Germany digital-only", "Three fixed safe-core 3MF releases; print/configuration gated later"],
    ]

    sheets = [
        ("Summary", summary),
        ("Initial Portfolio", initial),
        ("Portfolio", portfolio),
        ("External Exclusions", exclusions),
        ("Stage Definitions", stages),
        ("MVP Tasks", tasks),
        ("Research Backlog", research),
        ("Research Ideas 100", legacy_product_matrix),
        ("Research Economics", legacy_unit_economics),
        ("Research Families", legacy_family_strategy),
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
    print(f"Wrote {OUTPUT} with {len(sheets)} sheets")


if __name__ == "__main__":
    main()
