#!/usr/bin/env python3
"""Render a deterministic preview from the generated reference assembly."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exports/master/DRAFT-MM-ORG-007-assembly-65deg-0.1.0-draft.1.stl"
OUT = ROOT / "renders/MM-ORG-007-digital-candidate.png"
LIGHT = np.array([-0.45, -0.65, 0.85])
LIGHT /= np.linalg.norm(LIGHT)


def main():
    mesh = trimesh.load_mesh(SOURCE, force="mesh", process=False)
    triangles = mesh.vertices[mesh.faces]
    intensity = np.clip(mesh.face_normals @ LIGHT, -0.4, 1.0)
    intensity = 0.64 + 0.45 * (intensity + 0.4) / 1.4
    base = np.array(to_rgb("#5d85a8"))
    colors = np.clip(base[None, :] * intensity[:, None] + 0.05, 0, 1)

    fig = plt.figure(figsize=(10.5, 8.0), dpi=150, facecolor="#101620")
    ax = fig.add_subplot(111, projection="3d", facecolor="#101620")
    ax.add_collection3d(Poly3DCollection(
        triangles,
        facecolors=colors,
        edgecolors=(0.10, 0.15, 0.20, 0.20),
        linewidths=0.12,
    ))
    lo, hi = mesh.bounds
    center = (lo + hi) / 2
    span = np.maximum(hi - lo, 1)
    margin = 0.08 * span.max()
    ax.set_xlim(center[0] - span.max() / 2 - margin, center[0] + span.max() / 2 + margin)
    ax.set_ylim(center[1] - span.max() / 2 - margin, center[1] + span.max() / 2 + margin)
    ax.set_zlim(max(0, lo[2] - margin), hi[2] + margin)
    ax.set_box_aspect((1, 1, 0.9))
    ax.view_init(elev=25, azim=-55)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0.05, top=0.88)
    fig.text(0.055, 0.94, "MM-ORG-007 · ADJUSTABLE PASSIVE PHONE STAND",
             color="#eef4fb", fontsize=16, fontweight="bold")
    fig.text(0.057, 0.905, "95 mm base · printed-pin hinge · 55° / 65° / 75° detents",
             color="#aebed0", fontsize=10.5)
    fig.text(0.057, 0.035,
             "DRAFT digital candidate · detent profile, stability and hinge life pending physical test",
             color="#91a2b6", fontsize=9)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, facecolor=fig.get_facecolor(), pad_inches=0.08)
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
