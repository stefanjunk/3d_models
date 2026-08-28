#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exports/manufacturing/DRAFT-MM-ORG-033-rack-0.1.0-draft.1.stl"
TARGET = ROOT / "renders/MM-ORG-033-digital-candidate.png"
mesh = trimesh.load_mesh(SOURCE, process=False)
faces = mesh.vertices[mesh.faces]
fig = plt.figure(figsize=(11, 8), facecolor="#102631")
ax = fig.add_subplot(111, projection="3d", facecolor="#102631")
poly = Poly3DCollection(faces, facecolor="#59c6b3", edgecolor="#163c45", linewidth=0.08, alpha=1)
ax.add_collection3d(poly)
mins, maxs = mesh.bounds
ax.set_xlim(mins[0], maxs[0]); ax.set_ylim(mins[1], maxs[1]); ax.set_zlim(mins[2], maxs[2])
ax.set_box_aspect([float(value) for value in mesh.extents])
ax.view_init(elev=25, azim=-48)
ax.set_axis_off()
fig.suptitle("MM-ORG-033 · GEMSTAGE 6 · DRAFT DIGITAL CANDIDATE", color="#f4f0e6", fontsize=16, weight="bold")
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
