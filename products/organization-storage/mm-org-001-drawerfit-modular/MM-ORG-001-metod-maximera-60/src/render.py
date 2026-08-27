#!/usr/bin/env python3
"""Render deterministic DRAFT assembly views in the approved metriMade palette."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


ROOT = Path(__file__).resolve().parent.parent
PALETTE = {
    "navy": "#112431",
    "teal": "#08777D",
    "aqua": "#7FD5D3",
    "sand": "#C7AB82",
    "canvas": "#FBFAF7",
}


def add_mesh(ax, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0) -> None:
    collection = Poly3DCollection(mesh.triangles, linewidths=0, edgecolors="none", alpha=alpha)
    collection.set_facecolor(color)
    ax.add_collection3d(collection)


def configured_mesh(path: Path, translation: list[float]) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(path, process=False)
    mesh.apply_translation(translation)
    return mesh


def style_axis(ax, elevation: float, azimuth: float) -> None:
    ax.set_xlim(0, 512)
    ax.set_ylim(0, 491)
    ax.set_zlim(0, 120)
    ax.set_box_aspect((512, 491, 150))
    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_axis_off()
    ax.set_facecolor(PALETTE["canvas"])


def main() -> None:
    build = json.loads((ROOT / "reports" / "build-report.json").read_text(encoding="utf-8"))
    fig = plt.figure(figsize=(16, 9), facecolor=PALETTE["canvas"])
    ax_iso = fig.add_subplot(1, 2, 1, projection="3d")
    ax_top = fig.add_subplot(1, 2, 2, projection="3d")
    module_colors = [PALETTE["sand"], PALETTE["teal"], PALETTE["navy"]]
    for item in build["modules"]:
        mesh = configured_mesh(ROOT / item["manufacturing_file"], item["assembly_translation_mm"])
        color = module_colors[item["column"]]
        add_mesh(ax_iso, mesh, color)
        add_mesh(ax_top, mesh, color)
    comb = build["accessories"]["screwdriver_comb"]
    comb_mesh = configured_mesh(ROOT / comb["manufacturing_file"], comb["assembly_translation_mm"])
    add_mesh(ax_iso, comb_mesh, PALETTE["aqua"])
    add_mesh(ax_top, comb_mesh, PALETTE["aqua"])
    style_axis(ax_iso, 28, -58)
    style_axis(ax_top, 89.8, -90)
    ax_iso.set_title("DRAFT 0.1.0 · neun Module + Kamm", color=PALETTE["navy"], fontsize=17, pad=12, fontweight="bold")
    ax_top.set_title("512 × 491 mm · Werkzeugspur + 18 Fächer", color=PALETTE["navy"], fontsize=17, pad=12, fontweight="bold")
    fig.text(0.03, 0.035, "MM-ORG-001 · digitale DRAFT-Ansicht · Connector-Fit und Schubladenpassung noch nicht physisch freigegeben", color=PALETTE["teal"], fontsize=11)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    destination = ROOT / "reports" / "DRAFT-MM-ORG-001-v0.1.0-draft.1-assembly.png"
    fig.savefig(destination, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(destination)


if __name__ == "__main__":
    main()
