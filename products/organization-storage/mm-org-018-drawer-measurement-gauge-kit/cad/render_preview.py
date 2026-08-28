#!/usr/bin/env python3
"""Render a deterministic preview of the drawer measurement kit."""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
FILES = []
for index, radius in enumerate((2, 4, 6, 8, 10, 12)):
    FILES.append((ROOT / f"exports/manufacturing/DRAFT-MM-ORG-018-radius-r{radius:02d}-{REVISION}.stl", "#39979a", (index * 38.0, 0.0, 0.0)))
FILES.extend([
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-018-height-card-{REVISION}.stl", "#dd9436", (0.0, 45.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-018-height-card-{REVISION}.stl", "#dd9436", (38.0, 45.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-018-clearance-comb-{REVISION}.stl", "#7762a6", (80.0, 45.0, 0.0)),
    (ROOT / f"exports/manufacturing/DRAFT-MM-ORG-018-calibration-frame-{REVISION}.stl", "#c74f59", (0.0, 120.0, 0.0)),
])
OUT = ROOT / "renders/MM-ORG-018-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    axis.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor="#26343b", linewidth=0.035, alpha=0.96))


def main() -> None:
    figure = plt.figure(figsize=(13.5, 8.2), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    for path, color, translation in FILES:
        mesh = trimesh.load_mesh(path, force="mesh", process=True)
        mesh.apply_translation(translation)
        add_mesh(axis, mesh, color)
    axis.set_xlim(-8, 240)
    axis.set_ylim(-8, 175)
    axis.set_zlim(0, 22)
    axis.set_box_aspect((248, 183, 36))
    axis.view_init(elev=62, azim=-88)
    axis.set_axis_off()
    axis.set_title("MM-ORG-018 · radius tiles + paired height cards + clearance comb + calibration frame", fontsize=14, pad=18)
    figure.patch.set_facecolor("#f3efe7")
    axis.set_facecolor("#f3efe7")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
