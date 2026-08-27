#!/usr/bin/env python3
"""Render the requirements-approved 0.1.2 channel-shortening concept sheet.

The sheet uses the real 0.1.1-g1 production render as exterior context and
dimensioned 2D blockouts for the two revised visible projections.  It does not
modify or export manufacturing geometry.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHEET = ROOT / "reports" / "production-geometry-review-0.1.1-g1.jpg"
OUTPUT = ROOT / "concept" / "dice-tower-channel-shortening-concept-r0.1.2.jpg"

BG = "#08111f"
PANEL = "#0f1b2d"
TEXT = "#f4f7fb"
MUTED = "#9fb0c6"
STONE = "#8ea0b7"
STONE_DARK = "#3b4c63"
CYAN = "#38d6d2"
MAGENTA = "#f04ea1"
YELLOW = "#ffca55"
GREEN = "#58d68d"


def panel_title(ax, number: str, title: str, subtitle: str) -> None:
    ax.text(
        0.025,
        0.965,
        f"{number}  {title}",
        transform=ax.transAxes,
        color=TEXT,
        fontsize=13,
        fontweight="bold",
        va="top",
    )
    ax.text(
        0.025,
        0.905,
        subtitle,
        transform=ax.transAxes,
        color=MUTED,
        fontsize=8.7,
        va="top",
    )


def setup_panel(ax) -> None:
    ax.set_facecolor(PANEL)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def outlined_text(ax, x, y, text, *, color=TEXT, size=10, ha="left", va="center"):
    label = ax.text(x, y, text, color=color, fontsize=size, ha=ha, va=va)
    label.set_path_effects([patheffects.withStroke(linewidth=3, foreground=BG)])
    return label


def draw_context(ax, source: Image.Image) -> None:
    setup_panel(ax)
    panel_title(
        ax,
        "01",
        "Revisionsumfang am realen Turm",
        "Nur die sichtbaren Kanalenden werden gekürzt; Außenornament und Innenfunktion bleiben gesperrt.",
    )
    crop = source.crop((150, 285, 2420, 820))
    image_ax = ax.inset_axes([0.02, 0.03, 0.96, 0.77])
    image_ax.imshow(crop)
    image_ax.set_xlim(0, crop.width)
    image_ax.set_ylim(crop.height, 0)
    image_ax.set_axis_off()

    # Callout positions correspond to the existing front/rear/side review panels.
    image_ax.add_patch(Circle((1740, 155), 88, fill=False, linewidth=3.0, edgecolor=CYAN))
    image_ax.add_patch(Circle((485, 420), 92, fill=False, linewidth=3.0, edgecolor=YELLOW))
    image_ax.add_patch(
        FancyArrowPatch(
            (1660, 135),
            (1420, 70),
            arrowstyle="-|>",
            mutation_scale=18,
            linewidth=2.2,
            color=CYAN,
        )
    )
    image_ax.add_patch(
        FancyArrowPatch(
            (420, 420),
            (240, 330),
            arrowstyle="-|>",
            mutation_scale=18,
            linewidth=2.2,
            color=YELLOW,
        )
    )
    outlined_text(image_ax, 1400, 55, "oben: kurze 5-mm-Lippe", color=CYAN, size=10)
    outlined_text(image_ax, 65, 310, "unten: nur 8 mm sichtbar", color=YELLOW, size=10)


def draw_upper(ax) -> None:
    setup_panel(ax)
    panel_title(
        ax,
        "02",
        "Einwurf hinten-oben",
        "Zielsilhouette im Seitenschnitt · Ø 38 mm frei · 4 mm Wand · Achse 45°",
    )
    ax.set_xlim(-42, 72)
    ax.set_ylim(-24, 90)
    ax.set_aspect("equal")

    # Dome/roof blockout and protected horn.
    roof_x = np.linspace(-40, 44, 140)
    roof_y = 8 + 22 * np.sqrt(np.clip(1 - (roof_x / 48) ** 2, 0, 1))
    roof_poly = np.column_stack(
        [np.r_[roof_x, roof_x[::-1]], np.r_[roof_y, np.full_like(roof_y, -14)[::-1]]]
    )
    ax.add_patch(Polygon(roof_poly, closed=True, facecolor=STONE_DARK, edgecolor=STONE, linewidth=1.4))
    horn = Polygon(
        [(-19, 30), (-15, 51), (-9, 64), (-4, 49), (0, 30)],
        closed=True,
        facecolor=STONE,
        edgecolor=TEXT,
        linewidth=0.8,
        alpha=0.95,
    )
    ax.add_patch(horn)

    # Tube cross-section. The visible lip is 5 mm along its 45-degree axis.
    axis = np.array([1.0, 1.0]) / np.sqrt(2)
    normal = np.array([-1.0, 1.0]) / np.sqrt(2)
    roof_center = np.array([27.0, 25.0])
    outer_radius = 23.0
    clear_radius = 19.0
    inner_depth = 28.0
    outer_projection = 5.0
    p_in = roof_center - axis * inner_depth
    p_out = roof_center + axis * outer_projection

    def tube_polygon(radius: float, color: str, alpha: float):
        points = np.array(
            [p_in + normal * radius, p_out + normal * radius, p_out - normal * radius, p_in - normal * radius]
        )
        ax.add_patch(Polygon(points, closed=True, facecolor=color, edgecolor=color, alpha=alpha, linewidth=1.5))

    tube_polygon(outer_radius, CYAN, 0.32)
    tube_polygon(clear_radius, BG, 0.96)
    ax.plot(
        [p_out[0] - normal[0] * outer_radius, p_out[0] + normal[0] * outer_radius],
        [p_out[1] - normal[1] * outer_radius, p_out[1] + normal[1] * outer_radius],
        color=CYAN,
        linewidth=4.0,
    )

    # Ghost of the former projection to make the requested shortening explicit.
    old_out = roof_center + axis * 16.0
    ghost = np.array(
        [
            p_out + normal * outer_radius,
            old_out + normal * outer_radius,
            old_out - normal * outer_radius,
            p_out - normal * outer_radius,
        ]
    )
    ax.add_patch(Polygon(ghost, closed=True, facecolor=MAGENTA, edgecolor=MAGENTA, alpha=0.23, hatch="//"))
    ax.plot(
        [old_out[0] - normal[0] * outer_radius, old_out[0] + normal[0] * outer_radius],
        [old_out[1] - normal[1] * outer_radius, old_out[1] + normal[1] * outer_radius],
        color=MAGENTA,
        linewidth=1.5,
        linestyle="--",
    )

    d0 = roof_center + normal * 29
    d1 = p_out + normal * 29
    ax.add_patch(
        FancyArrowPatch(d0, d1, arrowstyle="<->", mutation_scale=13, color=GREEN, linewidth=2.0)
    )
    ax.text(*(0.5 * (d0 + d1) + normal * 5), "5 mm", color=GREEN, fontsize=11, fontweight="bold", ha="center")
    ax.text(54, 46, "entfällt", color=MAGENTA, fontsize=9, ha="center")
    ax.text(-26, 55, "Horn geschützt", color=TEXT, fontsize=9, ha="center")
    ax.add_patch(FancyArrowPatch((-13, 53), (-9, 48), arrowstyle="-|>", mutation_scale=12, color=TEXT))
    ax.text(63, -12, "Schematische Konzeptdarstellung", color=MUTED, fontsize=7.5, ha="right")


def draw_lower(ax) -> None:
    setup_panel(ax)
    panel_title(
        ax,
        "03",
        "Auswurf zum Vorhof",
        "Zielsilhouette im Seitenschnitt · 40 × 33 mm frei · 4 mm Seiten/Krone",
    )
    ax.set_xlim(-55, 62)
    ax.set_ylim(-18, 80)
    ax.set_aspect("equal")

    # Tower wall and forecourt floor in side section.
    ax.add_patch(Rectangle((10, -6), 34, 70, facecolor=STONE_DARK, edgecolor=STONE, linewidth=1.4))
    ax.add_patch(Rectangle((-52, -6), 96, 11, facecolor=STONE_DARK, edgecolor=STONE, linewidth=1.4))
    ax.text(31, 56, "Turmwand", color=MUTED, fontsize=8, ha="center")
    ax.text(-14, -12, "Vorhof", color=MUTED, fontsize=8, ha="center")

    wall_face = 10.0
    new_tip = wall_face - 8.0
    old_tip = wall_face - 16.0
    channel_bottom = 5.0
    channel_top = 42.0

    # Remaining channel and clear route.
    ax.add_patch(
        Rectangle((new_tip, channel_bottom), wall_face - new_tip + 25, channel_top - channel_bottom,
                  facecolor=YELLOW, edgecolor=YELLOW, alpha=0.28, linewidth=1.5)
    )
    ax.add_patch(
        Rectangle((new_tip, channel_bottom + 4), wall_face - new_tip + 25, channel_top - channel_bottom - 8,
                  facecolor=BG, edgecolor=BG, alpha=0.96)
    )
    ax.plot([new_tip, new_tip], [channel_bottom, channel_top], color=YELLOW, linewidth=4)

    # Former extra 8 mm shown as removed.
    ax.add_patch(
        Rectangle((old_tip, channel_bottom), new_tip - old_tip, channel_top - channel_bottom,
                  facecolor=MAGENTA, edgecolor=MAGENTA, alpha=0.24, hatch="//")
    )
    ax.plot([old_tip, old_tip], [channel_bottom, channel_top], color=MAGENTA, linestyle="--", linewidth=1.5)

    ax.add_patch(
        FancyArrowPatch((wall_face, 49), (new_tip, 49), arrowstyle="<->", mutation_scale=13, color=GREEN, linewidth=2)
    )
    ax.text((wall_face + new_tip) / 2, 54, "8 mm", color=GREEN, fontsize=11, fontweight="bold", ha="center")
    ax.text(-2, 29, "neue kurze\nKanalkante", color=YELLOW, fontsize=9, ha="center", va="center")
    ax.text(-6, 58, "entfällt", color=MAGENTA, fontsize=9, ha="center")

    # Front-view arch inset.
    inset = ax.inset_axes([0.61, 0.12, 0.33, 0.50])
    inset.set_facecolor("#0b1626")
    inset.set_xlim(-28, 28)
    inset.set_ylim(-4, 40)
    inset.set_aspect("equal")
    inset.add_patch(Rectangle((-20, 0), 40, 13, facecolor=BG, edgecolor=YELLOW, linewidth=2.2))
    inset.add_patch(Arc((0, 13), 40, 40, theta1=0, theta2=180, color=YELLOW, linewidth=2.2))
    inset.plot([-20, -20], [0, 13], color=YELLOW, linewidth=2.2)
    inset.plot([20, 20], [0, 13], color=YELLOW, linewidth=2.2)
    inset.text(0, 35, "Frontöffnung", color=TEXT, fontsize=8, ha="center")
    inset.text(0, -2, "40 × 33 mm frei", color=MUTED, fontsize=7.5, ha="center", va="top")
    inset.set_xticks([])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_visible(False)


def draw_unchanged(ax, source: Image.Image) -> None:
    setup_panel(ax)
    panel_title(
        ax,
        "04",
        "Unveränderte Funktionskette",
        "Die Kürzung liegt vollständig außerhalb des bisherigen inneren Würfelwegs.",
    )
    crop = source.crop((1770, 930, 2415, 1480))
    image_ax = ax.inset_axes([0.43, 0.04, 0.54, 0.76])
    image_ax.imshow(crop)
    image_ax.set_axis_off()
    box = dict(boxstyle="round,pad=0.5", facecolor=BG, edgecolor=CYAN, alpha=0.94)
    ax.text(
        0.055,
        0.69,
        "Unverändert\n\n• Innenraum Ø 57 mm\n• 3 Fallstufen\n• Würfel bis 25 mm\n• Boden geschlossen\n• Horn und Rückwand geschützt",
        transform=ax.transAxes,
        color=TEXT,
        fontsize=10,
        va="top",
        bbox=box,
        linespacing=1.45,
    )


def main() -> None:
    if not SOURCE_SHEET.exists():
        raise FileNotFoundError(SOURCE_SHEET)
    source = Image.open(SOURCE_SHEET).convert("RGB")

    fig = plt.figure(figsize=(16, 9), dpi=160, facecolor=BG)
    grid = fig.add_gridspec(
        2,
        2,
        left=0.025,
        right=0.975,
        bottom=0.085,
        top=0.86,
        wspace=0.035,
        hspace=0.06,
    )
    draw_context(fig.add_subplot(grid[0, 0]), source)
    draw_upper(fig.add_subplot(grid[0, 1]))
    draw_lower(fig.add_subplot(grid[1, 0]))
    draw_unchanged(fig.add_subplot(grid[1, 1]), source)

    fig.text(
        0.03,
        0.945,
        "WÜRFELTURM · KONZEPTREVISION 0.1.2",
        color=TEXT,
        fontsize=20,
        fontweight="bold",
    )
    fig.text(
        0.03,
        0.910,
        "Kanalstutzen kompakter · basiert auf Produktionsstand 0.1.1-g1 · JuSt Innovation",
        color=MUTED,
        fontsize=9.5,
    )
    fig.text(
        0.97,
        0.945,
        "KONZEPT · KEIN FERTIGUNGSMESH",
        color=MAGENTA,
        fontsize=11,
        fontweight="bold",
        ha="right",
    )
    fig.text(
        0.03,
        0.035,
        "Maßziel: oben 5 mm sichtbarer Überstand · unten 8 mm sichtbarer Überstand · Öffnungen und Innenweg unverändert",
        color=TEXT,
        fontsize=9.5,
    )
    fig.text(
        0.97,
        0.035,
        "Magenta: entfällt · Cyan/Gelb: neue sichtbare Kante",
        color=MUTED,
        fontsize=8.5,
        ha="right",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=160, facecolor=BG, pil_kwargs={"quality": 94})
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
