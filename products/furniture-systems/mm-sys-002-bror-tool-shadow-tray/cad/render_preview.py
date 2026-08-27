#!/usr/bin/env python3
"""Render the current BROR/tool measurement-pilot mesh for visual review."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "exports" / "manufacturing" / "DRAFT-MM-SYS-002-bror-tool-shadow-tray-0.2.0-draft.1.stl"
OUTPUT = ROOT / "renders" / "MM-SYS-002-bror-measurement-pilot.png"


def main() -> None:
    mesh = trimesh.load_mesh(MESH, force="mesh", process=False)
    light = np.array([-0.5, -0.7, 0.75], dtype=float)
    light /= np.linalg.norm(light)
    intensity = np.clip(mesh.face_normals @ light, -0.45, 1.0)
    intensity = 0.78 + 0.56 * (intensity + 0.45) / 1.45
    base = np.array(to_rgb("#c58a4b"))
    colors = np.clip(base[None, :] * intensity[:, None] + 0.07, 0.0, 1.0)
    fig = plt.figure(figsize=(10.5, 7.8), dpi=140, facecolor="#111720")
    ax = fig.add_subplot(111, projection="3d", facecolor="#111720")
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolors=colors, edgecolors=(0.22, 0.15, 0.09, 0.46), linewidths=0.18))
    ground = np.array([[[-25, -20, -1.5], [241, -20, -1.5], [241, 210, -1.5], [-25, 210, -1.5]]])
    ax.add_collection3d(Poly3DCollection(ground, facecolors="#202a35", edgecolors="none", alpha=0.52))
    ax.set_xlim(-30, 246)
    ax.set_ylim(-30, 215)
    ax.set_zlim(-3, 90)
    ax.set_box_aspect((276, 245, 93))
    ax.view_init(elev=30, azim=-60)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0.05, top=0.86)
    fig.text(0.055, 0.935, "MM-SYS-002 · TOOL-TRAY PILOT", color="#f3f5f8", fontsize=17, fontweight="bold")
    fig.text(0.057, 0.895, "216 × 180 × 28 mm · 2 mm nominal bed margin per X side", color="#c3cbd5", fontsize=10.5)
    fig.text(0.057, 0.035, "PROVISIONAL_UNVERIFIED drawer and tool fit · exact slicer and print pending", color="#98a7ba", fontsize=9)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, facecolor=fig.get_facecolor(), pad_inches=0.08)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
