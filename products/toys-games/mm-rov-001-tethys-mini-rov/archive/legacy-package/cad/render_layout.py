#!/usr/bin/env python3
"""Render an annotated concept layout; no external assets required."""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

OUT = Path(__file__).resolve().parents[1] / "assets" / "tethys_mini_layout.png"


def dim(ax, p1, p2, text, offset=(0, 0)):
    x1, y1 = p1
    x2, y2 = p2
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="<->", color="#5f7180", lw=1.1))
    ax.text((x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1], text, ha="center", va="center", color="#354854", fontsize=8)


def top_view(ax):
    ax.set_title("Draufsicht", loc="left", weight="bold")
    # Carbon rails and cross-members.
    for y in (-95, 95):
        ax.plot([-150, 150], [y, y], color="#252b30", lw=6, solid_capstyle="round")
    for x in (-110, 110):
        ax.plot([x, x], [-105, 105], color="#343c42", lw=6, solid_capstyle="round")
    # Pressure housing.
    ax.add_patch(FancyBboxPatch((-110, -37.5), 220, 75, boxstyle="round,pad=0,rounding_size=37.5", fc="#cbeff7", ec="#24738b", lw=2))
    ax.text(0, 0, "75-mm COTS-WTE\nPi · Pico · Akku · 3× ESC", ha="center", va="center", fontsize=8)
    # Two horizontal thrusters.
    for y in (-103, 103):
        ax.add_patch(FancyBboxPatch((-145, y - 39), 58, 78, boxstyle="round,pad=0,rounding_size=8", fc="#ffb34f", ec="#9f5c00", lw=1.5))
        ax.arrow(-135, y, 32, 0, width=1.4, head_width=9, head_length=9, color="#7e4700", length_includes_head=True)
    # Vertical thruster appears as circle from above.
    ax.add_patch(Circle((-128, 0), 39, fc="#ffcc7a", ec="#9f5c00", lw=1.5))
    ax.text(-128, 0, "V", ha="center", va="center", weight="bold", color="#6d3d00")
    # Foam blocks.
    for y in (-66, 66):
        ax.add_patch(FancyBboxPatch((-65, y - 16), 145, 32, boxstyle="round,pad=0,rounding_size=6", fc="#81d6b4", ec="#227356", alpha=0.78))
    ax.annotate("Ethernet-Tether", xy=(-150, 62), xytext=(-205, 48), arrowprops=dict(arrowstyle="->", color="#6c42a4"), color="#6c42a4", fontsize=8)
    dim(ax, (-160, -145), (160, -145), "ca. 320 mm", offset=(0, -8))
    dim(ax, (185, -120), (185, 120), "ca. 240 mm", offset=(18, 0))
    ax.set_xlim(-225, 220)
    ax.set_ylim(-165, 155)
    ax.set_aspect("equal")
    ax.axis("off")


def side_view(ax):
    ax.set_title("Seitenansicht / passive Stabilität", loc="left", weight="bold")
    ax.plot([-150, 150], [0, 0], color="#252b30", lw=6, solid_capstyle="round")
    ax.add_patch(FancyBboxPatch((-110, 18), 220, 75, boxstyle="round,pad=0,rounding_size=37.5", fc="#cbeff7", ec="#24738b", lw=2))
    # Horizontal and vertical thruster silhouettes.
    ax.add_patch(FancyBboxPatch((-145, -39), 58, 78, boxstyle="round,pad=0,rounding_size=8", fc="#ffb34f", ec="#9f5c00", lw=1.5))
    ax.add_patch(FancyBboxPatch((-167, -26), 78, 52, boxstyle="round,pad=0,rounding_size=8", fc="#ffcc7a", ec="#9f5c00", lw=1.5, alpha=.72))
    # Foam above, ballast below.
    ax.add_patch(FancyBboxPatch((-65, 105), 145, 30, boxstyle="round,pad=0,rounding_size=6", fc="#81d6b4", ec="#227356"))
    ax.add_patch(Rectangle((-55, -58), 110, 8, fc="#78828a", ec="#313a40"))
    ax.annotate("geschlossenzelliger Auftrieb", xy=(5, 120), xytext=(88, 132), arrowprops=dict(arrowstyle="->", color="#227356"), color="#227356", fontsize=8)
    ax.annotate("modularer Edelstahl-Ballast", xy=(0, -54), xytext=(62, -75), arrowprops=dict(arrowstyle="->", color="#424b51"), color="#424b51", fontsize=8)
    ax.scatter([0], [92], marker="o", s=45, color="#1ba879", zorder=5)
    ax.scatter([0], [22], marker="x", s=55, color="#c73838", linewidths=2, zorder=5)
    ax.text(8, 92, "CB", va="center", fontsize=8, color="#13694e")
    ax.text(8, 22, "CG", va="center", fontsize=8, color="#8b2020")
    dim(ax, (155, -60), (155, 135), "ca. 180 mm", offset=(20, 0))
    ax.text(-205, -92, "Ziel: 20–40 g positiv · CB klar über CG · final im Wasser trimmen", fontsize=8, color="#354854")
    ax.set_xlim(-220, 220)
    ax.set_ylim(-105, 155)
    ax.set_aspect("equal")
    ax.axis("off")


def architecture(ax):
    ax.set_title("Funktionskette", loc="left", weight="bold")
    labels = [
        (0.02, "Laptop + Gamepad\nPilot.py / ffplay", "#d9e8ff"),
        (0.27, "5–10 m Cat5e\nDaten-Tether", "#eadfff"),
        (0.50, "Pi Zero 2 W\nVideo + UDP-Agent", "#cbeff7"),
        (0.72, "Pico 2\nPWM + Watchdog", "#d7f5dd"),
        (0.90, "3× ESC\n3× Thruster", "#ffe0a9"),
    ]
    widths = [0.19, 0.17, 0.17, 0.16, 0.09]
    for (x, label, colour), width in zip(labels, widths):
        ax.add_patch(FancyBboxPatch((x, .35), width, .34, boxstyle="round,pad=.01,rounding_size=.025", transform=ax.transAxes, fc=colour, ec="#3b4b57"))
        ax.text(x + width / 2, .52, label, transform=ax.transAxes, ha="center", va="center", fontsize=8)
    for x1, x2 in ((.21, .27), (.44, .50), (.67, .72), (.88, .90)):
        ax.annotate("", (x2, .52), (x1, .52), xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", lw=1.4, color="#3b4b57"))
    ax.text(.51, .18, "Failsafe: Topside 25 Hz → Pi 300 ms → Pico 300 ms → Neutral 1500 µs", transform=ax.transAxes, ha="center", fontsize=8, color="#8b2020")
    ax.axis("off")


fig = plt.figure(figsize=(13.2, 8.2), dpi=180, facecolor="#f7fafb")
grid = fig.add_gridspec(2, 2, height_ratios=(1, .46), hspace=.18, wspace=.08)
top_view(fig.add_subplot(grid[0, 0]))
side_view(fig.add_subplot(grid[0, 1]))
architecture(fig.add_subplot(grid[1, :]))
fig.suptitle("Tethys Mini ROV v0.1 — 3-Thruster-Spielzeuggröße, modular und tethered", x=.04, y=.98, ha="left", fontsize=16, weight="bold", color="#173746")
fig.text(.04, .94, "Konzeptmaß 320 × 240 × 180 mm · Frischwasser-Prototyp · COTS-Druckgrenze · druckbare Schutz-/Trimmstruktur", fontsize=9, color="#4b6471")
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, bbox_inches="tight", facecolor=fig.get_facecolor())
print(OUT)
