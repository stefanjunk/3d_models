#!/usr/bin/env python3
"""Render a deterministic preview of the connected module family and fit coupon."""
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
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-017-soft-arc-coin-slope-module-{REVISION}.stl", "#39979a", (0.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-017-clean-facet-coin-slope-module-{REVISION}.stl", "#dd9436", (56.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-017-utility-rib-coin-slope-module-{REVISION}.stl", "#7762a6", (112.0, 0.0, 0.0)),
    (ROOT / f"exports/coupons/DRAFT-MM-ORG-017-connector-clearance-gauge-{REVISION}.stl", "#c74f59", (25.0, 95.0, 0.0)),
    (ROOT / f"exports/coupons/DRAFT-MM-ORG-017-connector-test-key-{REVISION}.stl", "#485963", (104.0, 108.0, 0.0)),
]
OUT = ROOT / "renders/MM-ORG-017-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    triangles = mesh.vertices[mesh.faces]
    axis.add_collection3d(Poly3DCollection(triangles, facecolor=color, edgecolor="#26343b", linewidth=0.06, alpha=0.96))


def main() -> None:
    figure = plt.figure(figsize=(13.5, 8.2), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    for path, color, translation in FILES:
        mesh = trimesh.load_mesh(path, force="mesh", process=True)
        mesh.apply_translation(translation)
        add_mesh(axis, mesh, color)
    axis.set_xlim(-8, 182)
    axis.set_ylim(-8, 148)
    axis.set_zlim(0, 50)
    axis.set_box_aspect((190, 156, 65))
    axis.view_init(elev=38, azim=-62)
    axis.set_axis_off()
    axis.set_title("MM-ORG-017 · connected coin-slope modules + connector clearance coupon", fontsize=14, pad=18)
    figure.patch.set_facecolor("#f3efe7")
    axis.set_facecolor("#f3efe7")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
