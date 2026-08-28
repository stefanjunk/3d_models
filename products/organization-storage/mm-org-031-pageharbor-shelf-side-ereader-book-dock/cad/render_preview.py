#!/usr/bin/env python3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / "exports/manufacturing/DRAFT-MM-ORG-031-dock-0.1.0-draft.1.stl"
OUT = ROOT / "renders/MM-ORG-031-digital-candidate.png"


def main() -> None:
    mesh = trimesh.load_mesh(STL, force="mesh", process=True)
    triangles = mesh.vertices[mesh.faces]
    fig = plt.figure(figsize=(10, 7), dpi=180, facecolor="#f4f1ea")
    ax = fig.add_subplot(111, projection="3d", facecolor="#f4f1ea")
    poly = Poly3DCollection(triangles, facecolor="#3d7188", edgecolor="#183540", linewidth=0.12, alpha=0.98)
    ax.add_collection3d(poly)
    bounds = mesh.bounds
    center = bounds.mean(axis=0)
    span = max(mesh.extents) * 0.62
    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(0, max(bounds[1][2] * 1.08, 1))
    ax.view_init(elev=25, azim=-58)
    ax.set_box_aspect((1.4, 1.0, 0.9))
    ax.set_axis_off()
    ax.set_title("MM-ORG-031 · PageHarbor Duo 5\nParametric digital print candidate", color="#183540", fontsize=15, pad=18)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
