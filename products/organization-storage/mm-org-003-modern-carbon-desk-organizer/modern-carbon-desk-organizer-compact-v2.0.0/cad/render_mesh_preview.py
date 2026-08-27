#!/usr/bin/env python3
"""Create a lightweight isometric mesh preview without claiming render validation."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "exports" / "master"
OUTPUT = ROOT / "renders" / "MM-ORG-003-compact-digital-candidate.png"
LIGHT = np.array([-0.45, -0.7, 0.8], dtype=float)
LIGHT /= np.linalg.norm(LIGHT)


def add_part(ax, path: Path, translation: tuple[float, float, float], color: str) -> None:
    mesh = trimesh.load_mesh(path, force="mesh", process=False)
    mesh.apply_translation(translation)
    triangles = mesh.vertices[mesh.faces]
    normals = mesh.face_normals
    intensity = np.clip(normals @ LIGHT, -0.4, 1.0)
    intensity = 0.66 + 0.54 * (intensity + 0.4) / 1.4
    base = np.array(to_rgb(color))
    facecolors = np.clip(base[None, :] * intensity[:, None] + 0.07, 0.0, 1.0)
    collection = Poly3DCollection(
        triangles,
        facecolors=facecolors,
        edgecolors=(0.18, 0.21, 0.26, 0.42),
        linewidths=0.22,
        antialiased=True,
    )
    ax.add_collection3d(collection)


def main() -> None:
    fig = plt.figure(figsize=(10.5, 8.2), dpi=140, facecolor="#101620")
    ax = fig.add_subplot(111, projection="3d", facecolor="#101620")
    add_part(ax, MASTER / "DRAFT-MM-ORG-003-compact-housing-2.0.0-draft.1-assembly-source.stl", (0.0, 0.0, 0.0), "#56677b")
    drawer = MASTER / "DRAFT-MM-ORG-003-compact-drawer-print-twice-2.0.0-draft.1-assembly-source.stl"
    add_part(ax, drawer, (3.45, 0.0, 3.25), "#334052")
    add_part(ax, drawer, (3.45, 0.0, 55.75), "#354356")
    add_part(ax, MASTER / "DRAFT-MM-ORG-003-compact-top-sorter-2.0.0-draft.1-assembly-source.stl", (0.0, 0.0, 108.0), "#687b91")

    ground = np.array([[[-35, -30, -2], [245, -30, -2], [245, 240, -2], [-35, 240, -2]]])
    ax.add_collection3d(Poly3DCollection(ground, facecolors="#1c2632", edgecolors="none", alpha=0.82))
    ax.set_xlim(-55, 265)
    ax.set_ylim(-50, 250)
    ax.set_zlim(-8, 225)
    ax.set_box_aspect((320, 300, 233))
    ax.view_init(elev=25, azim=-61, roll=0)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.0, right=1.0, bottom=0.04, top=0.87)
    fig.text(0.055, 0.94, "MM-ORG-003 · COMPACT 2.0", color="#eef4fb", fontsize=18, fontweight="bold")
    fig.text(0.057, 0.905, "210 × 190 × 173 mm · 2 drawers · removable 2 × 3 sorter", color="#aebed0", fontsize=10.5)
    fig.text(0.057, 0.035, "Digital engineering candidate · exact slicer and physical print pending", color="#91a2b6", fontsize=9)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, facecolor=fig.get_facecolor(), pad_inches=0.08)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
