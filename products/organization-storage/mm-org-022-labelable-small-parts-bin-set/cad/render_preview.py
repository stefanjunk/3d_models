#!/usr/bin/env python3
"""Render a deterministic preview of the MM-ORG-022 digital candidate."""
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
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-022-matrix-frame-{REVISION}.stl", "#8068aa", (0.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-022-narrow-bin-{REVISION}.stl", "#2c8290", (205.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-022-medium-bin-{REVISION}.stl", "#d58b38", (260.0, 0.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-022-wide-bin-{REVISION}.stl", "#d46355", (340.0, 0.0, 0.0)),
    (ROOT / f"exports/coupons/DRAFT-MM-ORG-022-label-slot-gauge-{REVISION}.stl", "#6b8e5d", (205.0, 100.0, 0.0)),
]
OUT = ROOT / "renders/MM-ORG-022-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    axis.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor="#26343b", linewidth=0.05, alpha=0.96))


def main() -> None:
    figure = plt.figure(figsize=(14.0, 8.5), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    for path, color, translation in FILES:
        mesh = trimesh.load_mesh(path, force="mesh", process=True)
        mesh.apply_translation(translation)
        add_mesh(axis, mesh, color)
    axis.set_xlim(-10, 450)
    axis.set_ylim(-20, 190)
    axis.set_zlim(0, 55)
    axis.set_box_aspect((460, 210, 80))
    axis.view_init(elev=43, azim=-67)
    axis.set_axis_off()
    axis.set_title("MM-ORG-022 · 45 / 67.5 / 90 mm ScoopLabel bins + open matrix frame", fontsize=14, pad=18)
    figure.patch.set_facecolor("#f3efe7")
    axis.set_facecolor("#f3efe7")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
