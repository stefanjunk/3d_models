#!/usr/bin/env python3
"""Render a deterministic preview of the three production plates and coupon."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
FILES = [
    ("Layout-5", ROOT / f"exports/manufacturing/DRAFT-MM-ORG-016-layout-5mm-{REVISION}.stl", "#39979a", (0.0, 0.0, 0.0)),
    ("Layout-4", ROOT / f"exports/manufacturing/DRAFT-MM-ORG-016-layout-4mm-{REVISION}.stl", "#dd9436", (50.0, 0.0, 0.0)),
    ("Signal-12", ROOT / f"exports/manufacturing/DRAFT-MM-ORG-016-signal-12-{REVISION}.stl", "#7762a6", (100.0, 0.0, 0.0)),
    ("Coupon", ROOT / f"exports/coupons/DRAFT-MM-ORG-016-minimum-feature-coupon-{REVISION}.stl", "#c74f59", (150.0, 0.0, 0.0)),
]
OUT = ROOT / "renders/MM-ORG-016-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    triangles = mesh.vertices[mesh.faces]
    axis.add_collection3d(Poly3DCollection(triangles, facecolor=color, edgecolor=color, linewidth=0.015, alpha=0.96))


def main() -> None:
    figure = plt.figure(figsize=(13.5, 8.2), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    for _, path, color, translation in FILES:
        mesh = trimesh.load_mesh(path, force="mesh", process=True)
        mesh.apply_translation(translation)
        add_mesh(axis, mesh, color)
    axis.set_xlim(-5, 250)
    axis.set_ylim(-8, 150)
    axis.set_zlim(0, 12)
    axis.set_box_aspect((255, 158, 28))
    axis.view_init(elev=76, azim=-90)
    axis.set_axis_off()
    axis.set_title("MM-ORG-016 · clip-free 4/5 mm stencil-ruler bookmarks + Signal-12 + feature coupon", fontsize=14, pad=18)
    figure.patch.set_facecolor("#f3efe7")
    axis.set_facecolor("#f3efe7")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
