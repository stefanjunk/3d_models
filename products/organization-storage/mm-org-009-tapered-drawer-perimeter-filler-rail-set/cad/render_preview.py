#!/usr/bin/env python3
"""Render a deterministic model-centred preview from the manufacturing meshes."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
OUTPUT = ROOT / "renders/MM-ORG-009-digital-candidate.png"
LIGHT = np.array([-0.55, -0.65, 0.8])
LIGHT /= np.linalg.norm(LIGHT)


def add_mesh(axis, path: Path, translation, color: str) -> None:
    mesh = trimesh.load_mesh(path, force="mesh", process=False)
    mesh.apply_translation(translation)
    triangles = mesh.vertices[mesh.faces]
    intensity = 0.62 + 0.42 * (np.clip(mesh.face_normals @ LIGHT, -0.4, 1.0) + 0.4) / 1.4
    base = np.array(to_rgb(color))
    face_colors = np.clip(base[None, :] * intensity[:, None] + 0.04, 0.0, 1.0)
    axis.add_collection3d(
        Poly3DCollection(
            triangles,
            facecolors=face_colors,
            edgecolors=(0.08, 0.12, 0.16, 0.17),
            linewidths=0.08,
        )
    )


def main() -> None:
    left = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-009-left-rail-{REVISION}.stl"
    right = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-009-right-rail-{REVISION}.stl"
    gauge = ROOT / f"exports/coupons/DRAFT-MM-ORG-009-taper-gauge-{REVISION}.stl"

    figure = plt.figure(figsize=(12, 7.8), dpi=150, facecolor="#101721")
    axis = figure.add_subplot(111, projection="3d", facecolor="#101721")
    add_mesh(axis, left, (0.0, 0.0, 0.0), "#d98a4a")
    add_mesh(axis, right, (0.0, 36.0, 0.0), "#4fa5a1")
    add_mesh(axis, gauge, (40.0, 79.0, 0.0), "#d4bf73")

    axis.set_xlim(-5.0, 220.0)
    axis.set_ylim(-5.0, 120.0)
    axis.set_zlim(0.0, 65.0)
    axis.set_box_aspect((225.0, 125.0, 65.0))
    axis.view_init(elev=28.0, azim=-58.0)
    axis.set_axis_off()
    figure.subplots_adjust(left=0.0, right=1.0, bottom=0.05, top=0.88)
    figure.text(
        0.055,
        0.94,
        "MM-ORG-009 · TAPERED DRAWER FILLER RAIL SET",
        color="#eef4fa",
        fontsize=17,
        fontweight="bold",
    )
    figure.text(
        0.057,
        0.905,
        "independent left/right tapers · ribbed underside · 2–26 mm measurement gauge",
        color="#aebed0",
        fontsize=10.5,
    )
    figure.text(
        0.057,
        0.035,
        "DRAFT digital model · drawer fit, finish contact and removal cycles pending",
        color="#91a2b6",
        fontsize=9,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, facecolor=figure.get_facecolor(), pad_inches=0.08)
    plt.close(figure)
    print(OUTPUT)


if __name__ == "__main__":
    main()
