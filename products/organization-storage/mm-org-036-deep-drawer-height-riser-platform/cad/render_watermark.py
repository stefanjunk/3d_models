#!/usr/bin/env python3
"""Render actual candidate underside and watermark-land close-up."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exports/master/DRAFT-MM-ORG-036-liftdeck-platform-0.1.0-draft.2-master.stl"
TARGET = ROOT / "renders/MM-ORG-036-watermark-underside.png"


def add_mesh(ax, mesh: trimesh.Trimesh, color: str, edge: str, width: float) -> None:
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor=edge, linewidth=width))


mesh = trimesh.load_mesh(SOURCE, force="mesh", process=True)
fig = plt.figure(figsize=(15, 7), facecolor="#112530")
left = fig.add_subplot(121, projection="3d", facecolor="#112530")
right = fig.add_subplot(122, facecolor="#112530")

add_mesh(left, mesh, "#5fc8b4", "#264952", 0.045)
left.set_xlim(0, 180)
left.set_ylim(0, 140)
left.set_zlim(0, 50)
left.set_box_aspect([180, 140, 50])
left.view_init(elev=-24, azim=-58)
left.set_axis_off()
left.set_title("ACTUAL FINISHED UNDERSIDE", color="#f5f1e8", fontsize=12, weight="bold")

# Draw only sharp feature edges from the actual mesh. Coplanar tessellation is
# omitted, leaving the recess strokes and land boundary legible. A finished
# underside view looks toward +Z, so screen X is the negative model-X axis.
angles = mesh.face_adjacency_angles
edges = mesh.face_adjacency_edges[angles > np.deg2rad(18)]
segments = []
for a, b in edges:
    va, vb = mesh.vertices[a], mesh.vertices[b]
    if max(va[2], vb[2]) < 43.75 or min(va[2], vb[2]) > 44.5:
        continue
    if max(va[0], vb[0]) < 39.5 or min(va[0], vb[0]) > 140.5:
        continue
    if max(va[1], vb[1]) < 89.5 or min(va[1], vb[1]) > 110.5:
        continue
    segments.append([[-va[0], va[1]], [-vb[0], vb[1]]])
right.add_collection(LineCollection(segments, colors="#efab58", linewidths=0.75))
right.set_xlim(-141, -39)
right.set_ylim(88.5, 111.5)
right.set_aspect("equal", adjustable="box")
right.set_axis_off()
right.set_title("ACTUAL RECESS FEATURE EDGES · FINISHED-SIDE VIEW", color="#f5f1e8", fontsize=12, weight="bold")

fig.suptitle("MM-ORG-036 · v0.1.0-draft.2 · WATERMARK INTEGRATION EVIDENCE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.035, "Finished-side reading direction · unscaled priority-1 Full tier · physical PLA coupon still pending", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
