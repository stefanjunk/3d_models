#!/usr/bin/env python3
"""Render the actual MomentPair underside and recessed identity feature edges."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exports/master/DRAFT-MM-ORG-038-momentpair-dual-slot-base-0.1.0-draft.1-master.stl"
TARGET = ROOT / "renders/MM-ORG-038-watermark-underside.png"


mesh = trimesh.load_mesh(SOURCE, force="mesh", process=True)
fig = plt.figure(figsize=(15, 7), facecolor="#10242e")
left = fig.add_subplot(121, projection="3d", facecolor="#10242e")
right = fig.add_subplot(122, facecolor="#10242e")
left.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor="#58c5ae", edgecolor="#264952", linewidth=0.04))
left.set_xlim(-75, 75); left.set_ylim(-26, 26); left.set_zlim(0, 22); left.set_box_aspect([150, 52, 22]); left.view_init(elev=-27, azim=-55); left.set_axis_off()
left.set_title("ACTUAL FINISHED BASE UNDERSIDE", color="#f5f1e8", fontsize=12, weight="bold")

edges = mesh.face_adjacency_edges[mesh.face_adjacency_angles > np.deg2rad(18)]
segments = []
for a, b in edges:
    va, vb = mesh.vertices[a], mesh.vertices[b]
    if max(va[2], vb[2]) > 0.55: continue
    if max(va[0], vb[0]) < -45 or min(va[0], vb[0]) > 45: continue
    if max(va[1], vb[1]) < 8 or min(va[1], vb[1]) > 24: continue
    segments.append([[-va[0], va[1]], [-vb[0], vb[1]]])
right.add_collection(LineCollection(segments, colors="#ec9d61", linewidths=0.8))
right.set_xlim(-46, 46); right.set_ylim(7.5, 24.5); right.set_aspect("equal", adjustable="box"); right.set_axis_off()
right.set_title("ACTUAL RECESS EDGES · FINISHED-SIDE VIEW", color="#f5f1e8", fontsize=12, weight="bold")
fig.suptitle("MM-ORG-038 · v0.1.0-draft.1 · WATERMARK INTEGRATION EVIDENCE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.035, "Unscaled priority-1 Full tier on the rear-rail underside · physical PLA coupon pending", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
