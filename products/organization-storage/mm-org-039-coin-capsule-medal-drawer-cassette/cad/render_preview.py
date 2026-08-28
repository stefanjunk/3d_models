#!/usr/bin/env python3
"""Render the actual host/adapters with illustrative protective capsules."""
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
HOST = ROOT / f"exports/master/DRAFT-MM-ORG-039-collectorgrid-six-cell-host-{REVISION}-master.stl"
SQUARE = ROOT / f"exports/master/DRAFT-MM-ORG-039-square-50-label-adapter-{REVISION}-master.stl"
ROUND = ROOT / f"exports/master/DRAFT-MM-ORG-039-round-46-label-adapter-{REVISION}-master.stl"
TARGET = ROOT / "renders/MM-ORG-039-digital-candidate.png"


def add_mesh(ax, mesh, color, alpha=1.0, edge="#233f4a"):
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor=color, linewidth=0.0, alpha=alpha))


host = trimesh.load_mesh(HOST, force="mesh", process=False)
square_source = trimesh.load_mesh(SQUARE, force="mesh", process=False)
round_source = trimesh.load_mesh(ROUND, force="mesh", process=False)
x_centers = [-70.5333333333, 0.0, 70.5333333333]
y_front, y_rear = -35.4, 35.4
parts = [host]
adapters = []
capsules = []
for x in x_centers:
    square = square_source.copy(); square.apply_translation((x, y_rear, 7.5)); adapters.append(square); parts.append(square)
    round_adapter = round_source.copy(); round_adapter.apply_translation((x, y_front, 7.5)); adapters.append(round_adapter); parts.append(round_adapter)
    square_capsule = trimesh.creation.box(extents=[50.0, 50.0, 6.25]); square_capsule.apply_translation((x, y_rear + 5.5, 10.625)); capsules.append(square_capsule); parts.append(square_capsule)
    round_capsule = trimesh.creation.cylinder(radius=23.0, height=5.0, sections=80); round_capsule.apply_translation((x, y_front + 5.5, 10.0)); capsules.append(round_capsule); parts.append(round_capsule)

fig = plt.figure(figsize=(14, 8), facecolor="#10242e")
ax = fig.add_subplot(111, projection="3d", facecolor="#10242e")
add_mesh(ax, host, "#58c5ae", 0.88)
for adapter in adapters: add_mesh(ax, adapter, "#d8bb70")
for capsule in capsules: add_mesh(ax, capsule, "#e8e2d4", 0.94, "#bcae94")
combined = trimesh.util.concatenate(parts)
mins, maxs = combined.bounds
ax.set_xlim(mins[0] - 8, maxs[0] + 8); ax.set_ylim(mins[1] - 8, maxs[1] + 8); ax.set_zlim(0, maxs[2] + 8)
ax.set_box_aspect([214, 144, 48]); ax.view_init(elev=48, azim=-56); ax.set_axis_off()
fig.suptitle("MM-ORG-039 · COLLECTORGRID 6 · DRAFT DIGITAL CANDIDATE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.045, "Actual marked host and adapters · transparent square/round protective capsules are illustrative and not included", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
