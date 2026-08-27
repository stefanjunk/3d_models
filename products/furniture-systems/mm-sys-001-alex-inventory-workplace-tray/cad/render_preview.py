#!/usr/bin/env python3
"""Render the current tray mesh for visual review only."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "exports" / "manufacturing" / "DRAFT-MM-SYS-001-alex-inventory-tray-0.2.0-draft.1.stl"
OUTPUT = ROOT / "renders" / "MM-SYS-001-alex-measurement-pilot.png"


def main() -> None:
    mesh = trimesh.load_mesh(MESH, force="mesh", process=False)
    triangles = mesh.vertices[mesh.faces]
    light = np.array([-0.5, -0.7, 0.75], dtype=float)
    light /= np.linalg.norm(light)
    intensity = np.clip(mesh.face_normals @ light, -0.45, 1.0)
    intensity = 0.78 + 0.56 * (intensity + 0.45) / 1.45
    base = np.array(to_rgb("#779bc2"))
    colors = np.clip(base[None, :] * intensity[:, None] + 0.08, 0.0, 1.0)

    fig = plt.figure(figsize=(10.5, 7.8), dpi=140, facecolor="#101722")
    ax = fig.add_subplot(111, projection="3d", facecolor="#101722")
    ax.add_collection3d(Poly3DCollection(triangles, facecolors=colors, edgecolors=(0.14, 0.19, 0.26, 0.46), linewidths=0.22))
    ground = np.array([[[-25, -20, -1.5], [235, -20, -1.5], [235, 190, -1.5], [-25, 190, -1.5]]])
    ax.add_collection3d(Poly3DCollection(ground, facecolors="#1c2836", edgecolors="none", alpha=0.54))
    ax.set_xlim(-30, 240)
    ax.set_ylim(-30, 200)
    ax.set_zlim(-3, 95)
    ax.set_box_aspect((270, 230, 98))
    ax.view_init(elev=29, azim=-61)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0.05, top=0.86)
    fig.text(0.055, 0.935, "MM-SYS-001 · MEASUREMENT PILOT", color="#edf4fb", fontsize=17, fontweight="bold")
    fig.text(0.057, 0.895, "210 × 160 × 32 mm · asymmetric workplace tray", color="#afc0d3", fontsize=10.5)
    fig.text(0.057, 0.035, "PROVISIONAL_UNVERIFIED furniture fit · exact slicer and physical gauge pending", color="#91a4b9", fontsize=9)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, facecolor=fig.get_facecolor(), pad_inches=0.08)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
