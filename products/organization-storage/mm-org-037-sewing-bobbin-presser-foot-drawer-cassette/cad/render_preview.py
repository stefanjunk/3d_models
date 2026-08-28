#!/usr/bin/env python3
"""Render the StitchCell cassette, installed insert, alternate insert and gauges."""
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
CASS = ROOT / f"exports/master/DRAFT-MM-ORG-037-stitchcell-cassette-{REVISION}-master.stl"
CB = ROOT / f"exports/master/DRAFT-MM-ORG-037-bobbin-insert-cb-20p5-{REVISION}-master.stl"
HOR = ROOT / f"exports/master/DRAFT-MM-ORG-037-bobbin-insert-horizontal-21p6-{REVISION}-master.stl"
BOBBIN_GAUGE = ROOT / f"exports/coupons/DRAFT-MM-ORG-037-two-standard-bobbin-fit-gauge-{REVISION}.stl"
FOOT_GAUGE = ROOT / f"exports/coupons/DRAFT-MM-ORG-037-presser-foot-cell-width-gauge-{REVISION}.stl"
TARGET = ROOT / "renders/MM-ORG-037-digital-candidate.png"


def add_mesh(ax, mesh, color, alpha=1.0, edge="#223947"):
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor=edge, linewidth=0.055, alpha=alpha))


cassette = trimesh.load_mesh(CASS, force="mesh", process=False)
cb = trimesh.load_mesh(CB, force="mesh", process=False)
horizontal = trimesh.load_mesh(HOR, force="mesh", process=False)
bobbin_gauge = trimesh.load_mesh(BOBBIN_GAUGE, force="mesh", process=False)
foot_gauge = trimesh.load_mesh(FOOT_GAUGE, force="mesh", process=False)

cb.apply_translation(((210 - 204.4) / 2, 2.4 + (46 - 45.2) / 2, 2.4))
horizontal.apply_translation((0, 168, 0))
bobbin_gauge.apply_translation((224, 0, 0))
foot_gauge.apply_translation((224, 48, 0))

fig = plt.figure(figsize=(14, 8), facecolor="#112530")
ax = fig.add_subplot(111, projection="3d", facecolor="#112530")
add_mesh(ax, cassette, "#5fc8b4")
add_mesh(ax, cb, "#efab58")
add_mesh(ax, horizontal, "#d98069")
add_mesh(ax, bobbin_gauge, "#d9c27e")
add_mesh(ax, foot_gauge, "#b7a6df")

combined = trimesh.util.concatenate([cassette, cb, horizontal, bobbin_gauge, foot_gauge])
mins, maxs = combined.bounds
ax.set_xlim(mins[0] - 8, maxs[0] + 8)
ax.set_ylim(mins[1] - 8, maxs[1] + 8)
ax.set_zlim(0, 48)
ax.set_box_aspect([float(v) for v in combined.extents])
ax.view_init(elev=31, azim=-55)
ax.set_axis_off()
fig.suptitle("MM-ORG-037 · STITCHCELL 7+10 · DRAFT DIGITAL CANDIDATE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.05, "210 × 150 × 28 mm cassette · ten open foot cells · interchangeable seven-bobbin inserts · fit gauges", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
