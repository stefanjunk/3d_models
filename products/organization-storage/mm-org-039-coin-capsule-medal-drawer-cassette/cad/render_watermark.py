#!/usr/bin/env python3
"""Render actual finished-side recess edges for host Full and adapter Micro identities."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / "exports/master/DRAFT-MM-ORG-039-collectorgrid-six-cell-host-0.1.0-draft.1-master.stl"
ADAPTER = ROOT / "exports/master/DRAFT-MM-ORG-039-square-50-label-adapter-0.1.0-draft.1-master.stl"
TARGET = ROOT / "renders/MM-ORG-039-watermark-undersides.png"


def recess_segments(mesh, x_bounds, y_bounds):
    edges = mesh.face_adjacency_edges[mesh.face_adjacency_angles > np.deg2rad(18)]
    segments = []
    for a, b in edges:
        va, vb = mesh.vertices[a], mesh.vertices[b]
        if max(va[2], vb[2]) > 0.55: continue
        if max(va[0], vb[0]) < x_bounds[0] or min(va[0], vb[0]) > x_bounds[1]: continue
        if max(va[1], vb[1]) < y_bounds[0] or min(va[1], vb[1]) > y_bounds[1]: continue
        segments.append([[-va[0], va[1]], [-vb[0], vb[1]]])
    return segments


host = trimesh.load_mesh(HOST, force="mesh", process=True)
adapter = trimesh.load_mesh(ADAPTER, force="mesh", process=True)
fig, axes = plt.subplots(1, 2, figsize=(15, 6), facecolor="#10242e")
for ax in axes: ax.set_facecolor("#10242e")
axes[0].add_collection(LineCollection(recess_segments(host, (-45, 45), (44, 66)), colors="#58c5ae", linewidths=0.75))
axes[0].set_xlim(-47, 47); axes[0].set_ylim(43, 67); axes[0].set_aspect("equal", adjustable="box"); axes[0].set_axis_off(); axes[0].set_title("ACTUAL HOST FULL RECESS · FINISHED SIDE", color="#f5f1e8", fontsize=12, weight="bold")
axes[1].add_collection(LineCollection(recess_segments(adapter, (-24, 24), (-33, -19)), colors="#ec9d61", linewidths=0.8))
axes[1].set_xlim(-25, 25); axes[1].set_ylim(-34, -18); axes[1].set_aspect("equal", adjustable="box"); axes[1].set_axis_off(); axes[1].set_title("ACTUAL ADAPTER MICRO RECESS · FINISHED SIDE", color="#f5f1e8", fontsize=12, weight="bold")
fig.suptitle("MM-ORG-039 · v0.1.0-draft.1 · WATERMARK INTEGRATION EVIDENCE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.035, "Unscaled selected R2 tiers · exact-process Full and Micro physical coupons remain pending", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
