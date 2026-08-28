#!/usr/bin/env python3
"""Render the two functional MM-ORG-035 cassettes with reference pad cases."""
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parents[1]
SQUARE = ROOT / "exports/master/DRAFT-MM-ORG-035-square-cassette-0.1.0-draft.2-master.stl"
RECTANGULAR = ROOT / "exports/master/DRAFT-MM-ORG-035-rectangular-cassette-0.1.0-draft.2-master.stl"
TARGET = ROOT / "renders/MM-ORG-035-digital-candidate.png"


def add_mesh(ax, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0, edges: str = "#223947") -> None:
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor=edges, linewidth=0.06, alpha=alpha))


square = trimesh.load_mesh(SQUARE, force="mesh", process=False)
rectangular = trimesh.load_mesh(RECTANGULAR, force="mesh", process=False)
rectangular.apply_translation((112, 0, 0))

# Reference envelopes are visualization aids, not exported product geometry.
square_case = trimesh.creation.box((78, 78, 21))
square_case.apply_translation((43.5, 42, 13.5))
rect_case = trimesh.creation.box((100, 69, 21))
rect_case.apply_translation((112 + 54.5, 37.5, 13.5))

fig = plt.figure(figsize=(13, 8), facecolor="#112530")
ax = fig.add_subplot(111, projection="3d", facecolor="#112530")
add_mesh(ax, square, "#62c9b7")
add_mesh(ax, rectangular, "#efab58")
add_mesh(ax, square_case, "#dfe8ec", 0.24, "#93a6ae")
add_mesh(ax, rect_case, "#dfe8ec", 0.24, "#93a6ae")

combined = trimesh.util.concatenate([square, rectangular])
mins, maxs = combined.bounds
padding = 5
ax.set_xlim(mins[0] - padding, maxs[0] + padding)
ax.set_ylim(mins[1] - padding, maxs[1] + padding)
ax.set_zlim(0, maxs[2] + padding)
ax.set_box_aspect([float(v) for v in combined.extents])
ax.view_init(elev=24, azim=-58)
ax.set_axis_off()
fig.suptitle("MM-ORG-035 · INKNEST DUO · DRAFT DIGITAL CANDIDATE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.055, "3 lanes per cassette · square 78 mm and rectangular 100 × 69 mm pilot formats", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
