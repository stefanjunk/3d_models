#!/usr/bin/env python3
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

ROOT = Path(__file__).resolve().parents[1]
PETG = ROOT / "exports/master/DRAFT-MM-ORG-034-petg-clip-m-0.1.0-draft.2-master.stl"
TPU = ROOT / "exports/master/DRAFT-MM-ORG-034-tpu-rail-loop-0.1.0-draft.2-master.stl"
TARGET = ROOT / "renders/MM-ORG-034-digital-candidate.png"

petg = trimesh.load_mesh(PETG, process=False)
tpu = trimesh.load_mesh(TPU, process=False)
gap = 2.6
total_height = 2.2 + gap + 1.8
tpu.apply_translation((0, 0, total_height / 2))

fig = plt.figure(figsize=(11, 8), facecolor="#102631")
ax = fig.add_subplot(111, projection="3d", facecolor="#102631")
for mesh, color in [(petg, "#59c6b3"), (tpu, "#f3a64a")]:
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor="#163c45", linewidth=0.08, alpha=1))
combined = trimesh.util.concatenate([petg, tpu])
mins, maxs = combined.bounds
ax.set_xlim(mins[0], maxs[0]); ax.set_ylim(mins[1], maxs[1]); ax.set_zlim(mins[2], maxs[2])
ax.set_box_aspect([float(v) for v in combined.extents])
ax.view_init(elev=24, azim=-52)
ax.set_axis_off()
fig.suptitle("MM-ORG-034 · FLEXDOCK · DRAFT DIGITAL CANDIDATE", color="#f4f0e6", fontsize=16, weight="bold")
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
