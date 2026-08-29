#!/usr/bin/env python3
"""Build the German OpenQuad CF5 research report as a polished PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "forschungsbericht.md"
OUTPUT = ROOT / "output" / "pdf" / "OpenQuad_CF5_Forschungsbericht_DE.pdf"
FIGURES = ROOT / "output" / "figures"

PAGE_W, PAGE_H = A4
MARGIN_X = 16 * mm
MARGIN_TOP = 17 * mm
MARGIN_BOTTOM = 16 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X

INK = colors.HexColor("#20252B")
MUTED = colors.HexColor("#5B646D")
ORANGE = colors.HexColor("#F07C28")
ORANGE_DARK = colors.HexColor("#A54711")
ORANGE_PALE = colors.HexColor("#FFF0E2")
CYAN = colors.HexColor("#20A7C9")
PURPLE = colors.HexColor("#7B1FA2")
GREEN = colors.HexColor("#2B8C5A")
RED = colors.HexColor("#A1262F")
GRID = colors.HexColor("#D7DADD")
PAPER = colors.HexColor("#FBFBF8")


def register_fonts() -> None:
    base = Path("/usr/share/fonts/truetype/dejavu")
    pdfmetrics.registerFont(TTFont("DVSans", str(base / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DVSans-Bold", str(base / "DejaVuSans-Bold.ttf")))
    # The minimal runtime ships no proportional DejaVu italic face. Register
    # the regular face under the italic family slot so ReportLab never falls
    # back to a non-Unicode base font.
    pdfmetrics.registerFont(TTFont("DVSans-Oblique", str(base / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DVMono", str(base / "DejaVuSansMono.ttf")))
    pdfmetrics.registerFontFamily(
        "DVSans", normal="DVSans", bold="DVSans-Bold", italic="DVSans-Oblique", boldItalic="DVSans-Bold"
    )


def build_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    styles = {
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="DVSans",
            fontSize=8.9,
            leading=12.4,
            textColor=INK,
            spaceAfter=5.2,
            allowWidows=0,
            allowOrphans=0,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=sample["BodyText"],
            fontName="DVSans",
            fontSize=7.3,
            leading=9.5,
            textColor=MUTED,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=sample["Heading1"],
            fontName="DVSans-Bold",
            fontSize=17,
            leading=21,
            textColor=INK,
            spaceBefore=11,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=sample["Heading2"],
            fontName="DVSans-Bold",
            fontSize=12.7,
            leading=16,
            textColor=ORANGE_DARK,
            spaceBefore=9,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=sample["Heading3"],
            fontName="DVSans-Bold",
            fontSize=10.4,
            leading=13.5,
            textColor=INK,
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=sample["BodyText"],
            fontName="DVSans",
            fontSize=8.7,
            leading=12.0,
            leftIndent=13,
            firstLineIndent=-8,
            bulletIndent=2,
            textColor=INK,
            spaceAfter=2.6,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=sample["BodyText"],
            fontName="DVSans",
            fontSize=8.5,
            leading=12.2,
            leftIndent=10,
            rightIndent=7,
            borderColor=ORANGE,
            borderWidth=0,
            borderPadding=(7, 9, 7, 10),
            backColor=ORANGE_PALE,
            textColor=INK,
            spaceAfter=8,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=sample["BodyText"],
            fontName="DVSans-Oblique",
            fontSize=7.4,
            leading=9.4,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceBefore=2,
            spaceAfter=7,
        ),
        "table": ParagraphStyle(
            "TableCell",
            parent=sample["BodyText"],
            fontName="DVSans",
            fontSize=6.8,
            leading=8.7,
            textColor=INK,
            spaceAfter=0,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=sample["BodyText"],
            fontName="DVSans-Bold",
            fontSize=6.8,
            leading=8.7,
            textColor=colors.white,
            spaceAfter=0,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=sample["Title"],
            fontName="DVSans-Bold",
            fontSize=29,
            leading=32,
            alignment=TA_LEFT,
            textColor=INK,
            spaceAfter=7,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=sample["BodyText"],
            fontName="DVSans",
            fontSize=12.2,
            leading=16,
            textColor=MUTED,
            spaceAfter=8,
        ),
        "cover_status": ParagraphStyle(
            "CoverStatus",
            parent=sample["BodyText"],
            fontName="DVSans-Bold",
            fontSize=8.3,
            leading=11,
            textColor=RED,
            backColor=colors.HexColor("#FCEBED"),
            borderColor=colors.HexColor("#E8B8BD"),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=7,
        ),
        "toc_title": ParagraphStyle(
            "TOCTitle",
            parent=sample["Heading1"],
            fontName="DVSans-Bold",
            fontSize=20,
            leading=24,
            textColor=INK,
            spaceAfter=14,
        ),
    }
    return styles


def inline_markup(text: str) -> str:
    result = html.escape(text.strip(), quote=True)
    result = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: f'<link href="{m.group(2)}" color="#1A6C87"><u>{m.group(1)}</u></link>',
        result,
    )
    result = re.sub(r"`([^`]+)`", r'<font name="DVMono" color="#5A355F">\1</font>', result)
    result = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", result)
    return result


def clean_heading(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("**", "").replace("`", "").strip()


def image_flowable(path: Path, max_w: float, max_h: float) -> Image:
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return Image(str(path), width=w * scale, height=h * scale)


def table_widths(rows: list[list[str]], total: float) -> list[float]:
    cols = len(rows[0])
    maxima = []
    for index in range(cols):
        maximum = max(len(re.sub(r"\[[^\]]+\]\([^)]+\)", "link", row[index])) for row in rows)
        maxima.append(min(max(maximum, 10), 58) ** 0.68)
    # Guarantee a usable minimum width, then distribute the remainder.
    minimum = 22 * mm if cols <= 4 else 18 * mm
    base = minimum * cols
    if base >= total:
        return [total / cols] * cols
    remainder = total - base
    weight_sum = sum(maxima)
    return [minimum + remainder * weight / weight_sum for weight in maxima]


def markdown_table(rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> LongTable:
    rendered = []
    for r_index, row in enumerate(rows):
        style = styles["table_header"] if r_index == 0 else styles["table"]
        rendered.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = LongTable(
        rendered,
        colWidths=table_widths(rows, CONTENT_W),
        repeatRows=1,
        splitByRow=1,
        hAlign="LEFT",
    )
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
    ]
    for r_index in range(1, len(rows)):
        if r_index % 2 == 0:
            commands.append(("BACKGROUND", (0, r_index), (-1, r_index), colors.HexColor("#F2F3F2")))
    table.setStyle(TableStyle(commands))
    return table


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        self._heading_counter = 0

    def beforeDocument(self) -> None:
        # multiBuild may lay out the document repeatedly while resolving the
        # table of contents. Stable bookmark keys are required across passes.
        self._heading_counter = 0
        super().beforeDocument()

    def afterFlowable(self, flowable) -> None:
        if not isinstance(flowable, Paragraph):
            return
        name = flowable.style.name
        if name not in {"H1", "H2", "H3"}:
            return
        level = {"H1": 0, "H2": 1, "H3": 2}[name]
        text = clean_heading(flowable.getPlainText())
        key = f"heading-{self._heading_counter}"
        self._heading_counter += 1
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)
        # Keep the printed contents page compact; subsection bookmarks remain
        # available in the PDF outline/navigation pane.
        if level == 0:
            self.notify("TOCEntry", (level, text, self.page, key))


def page_decor(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    if doc.page > 1:
        canvas.setStrokeColor(ORANGE)
        canvas.setLineWidth(1.2)
        canvas.line(MARGIN_X, PAGE_H - 11 * mm, PAGE_W - MARGIN_X, PAGE_H - 11 * mm)
        canvas.setFont("DVSans-Bold", 7.2)
        canvas.setFillColor(INK)
        canvas.drawString(MARGIN_X, PAGE_H - 8.7 * mm, "OPENQUAD CF5")
        canvas.setFont("DVSans", 7.0)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 8.7 * mm, "Forschungsentwurf - 13.08.2026")
        canvas.setStrokeColor(GRID)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_X, 10.5 * mm, PAGE_W - MARGIN_X, 10.5 * mm)
        canvas.setFont("DVSans", 6.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN_X, 7.1 * mm, "PRELIMINARY / NOT FLIGHT PROVEN")
        canvas.drawRightString(PAGE_W - MARGIN_X, 7.1 * mm, f"Seite {doc.page}")
    canvas.restoreState()


def cover_story(styles: dict[str, ParagraphStyle]) -> list:
    story = [
        Spacer(1, 3 * mm),
        HRFlowable(width="100%", thickness=5, color=ORANGE, spaceAfter=7),
        Paragraph("OpenQuad CF5", styles["cover_title"]),
        Paragraph(
            "Deep-Research-Entwurf eines modularen 5-Zoll-Quadcopters aus 3D-Druck und COTS-Komponenten",
            styles["cover_subtitle"],
        ),
        Paragraph(
            "PRELIMINARY / NOT FLIGHT PROVEN - keine Flugfreigabe, Zertifizierung oder Rechtsberatung",
            styles["cover_status"],
        ),
    ]
    story.append(image_flowable(FIGURES / "openquad_top_view.png", 116 * mm, 116 * mm))
    story.append(Spacer(1, 3 * mm))

    cards = [
        Paragraph("<b>230 mm</b><br/><font size=7>Motorabstand</font>", styles["body"]),
        Paragraph("<b>ca. 540 g</b><br/><font size=7>Startmasse, geschaetzt</font>", styles["body"]),
        Paragraph("<b>4S / 5 Zoll</b><br/><font size=7>COTS-Propulsion</font>", styles["body"]),
        Paragraph("<b>285-390 EUR</b><br/><font size=7>Fluggeraet-Budget</font>", styles["body"]),
    ]
    table = Table([cards], colWidths=[CONTENT_W / 4] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F3F2")),
                ("BOX", (0, 0), (-1, -1), 0.5, GRID),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 4 * mm),
            Paragraph(
                "Deutschland / EASA | Stand 13.08.2026 | CAD: OpenSCAD | Flugsoftware: Betaflight + ExpressLRS + EdgeTX",
                styles["caption"],
            ),
            PageBreak(),
        ]
    )
    return story


def toc_story(styles: dict[str, ParagraphStyle]) -> list:
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "TOC0", fontName="DVSans-Bold", fontSize=9.2, leading=13, leftIndent=0,
            firstLineIndent=0, textColor=INK, spaceBefore=4
        ),
        ParagraphStyle(
            "TOC1", fontName="DVSans", fontSize=8.2, leading=11, leftIndent=12,
            firstLineIndent=0, textColor=MUTED, spaceBefore=1
        ),
        ParagraphStyle(
            "TOC2", fontName="DVSans", fontSize=7.4, leading=9.5, leftIndent=24,
            firstLineIndent=0, textColor=MUTED, spaceBefore=0
        ),
    ]
    return [
        Paragraph("Inhalt", styles["toc_title"]),
        Paragraph(
            "Entwurfsentscheidung, Referenzprojekte, Mechanik, Marktkomponenten, Software, Fertigung, Validierung und EU/DE-Betrieb.",
            styles["body"],
        ),
        Spacer(1, 5 * mm),
        toc,
        PageBreak(),
    ]


def parse_markdown(styles: dict[str, ParagraphStyle]) -> list:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    # Cover already carries title and metadata. Start after the first rule.
    try:
        start = lines.index("---") + 1
    except ValueError:
        start = 0
    lines = lines[start:]
    story = []
    index = 0

    def is_special(line: str) -> bool:
        stripped = line.strip()
        return (
            not stripped
            or stripped.startswith("#")
            or stripped.startswith(">")
            or stripped.startswith("|")
            or stripped.startswith("![")
            or stripped == "---"
            or re.match(r"^\s*[-*]\s+", line) is not None
            or re.match(r"^\s*\d+\.\s+", line) is not None
        )

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            story.append(Spacer(1, 1.2 * mm))
            index += 1
            continue
        if stripped == "---":
            story.append(HRFlowable(width="100%", thickness=0.6, color=GRID, spaceBefore=5, spaceAfter=7))
            index += 1
            continue
        image_match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            caption, relative = image_match.groups()
            path = (SOURCE.parent / relative).resolve()
            max_h = 141 * mm if "top_view" in path.name else 82 * mm
            story.append(image_flowable(path, CONTENT_W, max_h))
            story.append(Paragraph(html.escape(caption), styles["caption"]))
            index += 1
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            # The Markdown document uses H1 for the cover (skipped here), H2
            # for numbered chapters and H3 for subsections. Promote the latter
            # two by one level for the report body and PDF outline.
            level = max(1, len(heading.group(1)) - 1)
            story.append(Paragraph(inline_markup(heading.group(2)), styles[f"h{level}"]))
            index += 1
            continue
        if stripped.startswith(">"):
            quote = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip()[1:].strip())
                index += 1
            story.append(Paragraph(inline_markup(" ".join(quote)), styles["quote"]))
            continue
        if stripped.startswith("|") and index + 1 < len(lines):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            parsed = [[cell.strip() for cell in line.strip("|").split("|")] for line in table_lines]
            if len(parsed) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in parsed[1]):
                parsed.pop(1)
            if parsed and all(len(row) == len(parsed[0]) for row in parsed):
                story.append(markdown_table(parsed, styles))
                story.append(Spacer(1, 2.5 * mm))
            continue
        bullet = re.match(r"^\s*([-*]|\d+\.)\s+(.+)$", raw)
        if bullet:
            marker, item = bullet.groups()
            index += 1
            continuation = []
            while index < len(lines):
                candidate = lines[index]
                if not candidate.strip() or is_special(candidate):
                    break
                continuation.append(candidate.strip())
                index += 1
            content = " ".join([item] + continuation)
            if content.startswith("[ ] "):
                content = "□ " + content[4:]
            bullet_text = "•" if marker in {"-", "*"} else marker
            story.append(Paragraph(inline_markup(content), styles["bullet"], bulletText=bullet_text))
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines) and not is_special(lines[index]):
            paragraph_lines.append(lines[index].strip())
            index += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph_lines)), styles["body"]))

    return story


def build() -> None:
    register_fonts()
    styles = build_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    frame = Frame(
        MARGIN_X,
        MARGIN_BOTTOM,
        CONTENT_W,
        PAGE_H - MARGIN_TOP - MARGIN_BOTTOM,
        id="body",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc = ReportDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="OpenQuad CF5 - Forschungsbericht",
        author="OpenAI Codex",
        subject="Modularer 5-Zoll-Quadcopter aus 3D-Druck und COTS-Komponenten",
    )
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=page_decor)])
    story = cover_story(styles) + toc_story(styles) + parse_markdown(styles)
    doc.multiBuild(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
