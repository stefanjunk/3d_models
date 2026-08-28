#!/usr/bin/env python3
"""Render a deterministic preview of the MM-ORG-024 digital candidate."""
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
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-024-pull-label-face-{REVISION}.stl", "#2c8290", (0.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-024-clip-thin-{REVISION}.stl", "#d58b38", (132.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-024-clip-shelffit-{REVISION}.stl", "#d46355", (154.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-024-clip-thick-{REVISION}.stl", "#8068aa", (177.0, 0.0, 0.0)),
    (ROOT / f"exports/coupons/DRAFT-MM-ORG-024-gap-gauge-{REVISION}.stl", "#72a56b", (15.0, 70.0, 0.0)),
    (ROOT / f"exports/coupons/DRAFT-MM-ORG-024-key-slot-coupon-{REVISION}.stl", "#c9a65b", (112.0, 75.0, 0.0)),
]
OUT = ROOT / "renders/MM-ORG-024-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    axis.add_collection3d(
        Poly3DCollection(
            mesh.vertices[mesh.faces],
            facecolor=color,
            edgecolor="#26343b",
            linewidth=0.045,
            alpha=0.97,
        )
    )


def main() -> None:
    figure = plt.figure(figsize=(14.0, 8.5), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    for path, color, translation in FILES:
        mesh = trimesh.load_mesh(path, force="mesh", process=True)
        mesh.apply_translation(translation)
        add_mesh(axis, mesh, color)
    axis.set_xlim(-45, 245)
    axis.set_ylim(-45, 135)
    axis.set_zlim(0, 38)
    axis.set_box_aspect((290, 180, 48))
    axis.view_init(elev=50, azim=-66)
    axis.set_axis_off()
    axis.set_title("MM-ORG-024 · BridgeKey pull face + measured U-clips + coupons", fontsize=14, pad=18)
    figure.patch.set_facecolor("#f3efe7")
    axis.set_facecolor("#f3efe7")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
