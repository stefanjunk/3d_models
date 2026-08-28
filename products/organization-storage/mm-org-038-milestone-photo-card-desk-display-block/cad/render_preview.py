#!/usr/bin/env python3
"""Render the actual MomentPair base and gauge with illustrative card planes."""
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
BASE = ROOT / f"exports/master/DRAFT-MM-ORG-038-momentpair-dual-slot-base-{REVISION}-master.stl"
GAUGE = ROOT / f"exports/coupons/DRAFT-MM-ORG-038-two-depth-card-slot-gauge-{REVISION}.stl"
TARGET = ROOT / "renders/MM-ORG-038-digital-candidate.png"


def add_mesh(ax, mesh, color, alpha=1.0, edge="#233f4a"):
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor=edge, linewidth=0.06, alpha=alpha))


def card_mesh(width, height, thickness, center_x, top_slot_y, bottom_z, tilt_deg):
    plate = trimesh.creation.box(extents=[width, thickness, height])
    plate.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(tilt_deg), [1, 0, 0]))
    plate.apply_translation([center_x, top_slot_y, bottom_z + height / 2])
    return plate


base = trimesh.load_mesh(BASE, force="mesh", process=False)
gauge = trimesh.load_mesh(GAUGE, force="mesh", process=False)
gauge.apply_translation((105, -5, 0))
rear_card = card_mesh(118, 78, 0.7, 0, 16, 14, 8)
front_card = card_mesh(48, 50, 0.7, 28, -16, 12, 8)

fig = plt.figure(figsize=(14, 8), facecolor="#10242e")
ax = fig.add_subplot(111, projection="3d", facecolor="#10242e")
add_mesh(ax, base, "#58c5ae")
add_mesh(ax, gauge, "#d8bb70")
add_mesh(ax, rear_card, "#e8e2d4", 0.94, "#bcae94")
add_mesh(ax, front_card, "#ec9d61", 0.96, "#a85c38")
combined = trimesh.util.concatenate([base, gauge, rear_card, front_card])
mins, maxs = combined.bounds
ax.set_xlim(mins[0] - 8, maxs[0] + 8); ax.set_ylim(mins[1] - 10, maxs[1] + 10); ax.set_zlim(0, maxs[2] + 8)
ax.set_box_aspect([float(v) for v in combined.extents])
ax.view_init(elev=25, azim=-58)
ax.set_axis_off()
fig.suptitle("MM-ORG-038 · MOMENTPAIR 2 · DRAFT DIGITAL CANDIDATE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.045, "Actual 150 × 52 × 22 mm base and two-depth gauge · card planes are illustrative, not included", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
