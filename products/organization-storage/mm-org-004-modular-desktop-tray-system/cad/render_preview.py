#!/usr/bin/env python3
"""Render a lightweight isometric preview from the generated assembly mesh."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exports" / "master" / "DRAFT-MM-ORG-004-assembly-preview-0.1.0-draft.1.stl"
OUTPUT = ROOT / "renders" / "MM-ORG-004-digital-candidate.png"
LIGHT = np.array([-0.45, -0.70, 0.85], dtype=float)
LIGHT /= np.linalg.norm(LIGHT)


def main() -> None:
    mesh = trimesh.load_mesh(SOURCE, force="mesh", process=False)
    triangles = mesh.vertices[mesh.faces]
    intensity = np.clip(mesh.face_normals @ LIGHT, -0.4, 1.0)
    intensity = 0.62 + 0.55 * (intensity + 0.4) / 1.4
    base = np.array(to_rgb("#6f879d"))
    facecolors = np.clip(base[None, :] * intensity[:, None] + 0.06, 0.0, 1.0)

    fig = plt.figure(figsize=(11.0, 8.0), dpi=150, facecolor="#101620")
    ax = fig.add_subplot(111, projection="3d", facecolor="#101620")
    ax.add_collection3d(Poly3DCollection(triangles, facecolors=facecolors, edgecolors=(0.15, 0.2, 0.25, 0.30), linewidths=0.18))
    bounds = mesh.bounds
    ext = mesh.extents
    margin = 18.0
    ax.set_xlim(bounds[0, 0] - margin, bounds[1, 0] + margin)
    ax.set_ylim(bounds[0, 1] - margin, bounds[1, 1] + margin)
    ax.set_zlim(-4.0, max(75.0, bounds[1, 2] + 15.0))
    ax.set_box_aspect((ext[0] + 2 * margin, ext[1] + 2 * margin, 82.0))
    ax.view_init(elev=29, azim=-58, roll=0)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0.05, top=0.88)
    fig.text(0.055, 0.94, "MM-ORG-004 · MODULAR DESKTOP TRAYS", color="#eef4fb", fontsize=18, fontweight="bold")
    fig.text(0.057, 0.905, "Precision · Soft · Lounge · common underside bow-tie link", color="#aebed0", fontsize=10.5)
    fig.text(0.057, 0.035, "DRAFT digital engineering candidate · exact slicer and physical fit pending", color="#91a2b6", fontsize=9)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, facecolor=fig.get_facecolor(), pad_inches=0.08)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
