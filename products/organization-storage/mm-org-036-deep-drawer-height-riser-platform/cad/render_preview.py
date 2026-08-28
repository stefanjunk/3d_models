#!/usr/bin/env python3
"""Render the LiftDeck use orientation and both physical-test coupons."""
from pathlib import Path

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "exports/master/DRAFT-MM-ORG-036-liftdeck-platform-0.1.0-draft.2-master.stl"
CORNER = ROOT / "exports/coupons/DRAFT-MM-ORG-036-corner-post-creep-coupon-0.1.0-draft.2.stl"
RIB = ROOT / "exports/coupons/DRAFT-MM-ORG-036-rib-support-creep-coupon-0.1.0-draft.2.stl"
TARGET = ROOT / "renders/MM-ORG-036-digital-candidate.png"


def add_mesh(ax, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0, edges: str = "#223947") -> None:
    ax.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor=edges, linewidth=0.06, alpha=alpha))


platform = trimesh.load_mesh(PLATFORM, force="mesh", process=False)
corner = trimesh.load_mesh(CORNER, force="mesh", process=False)
rib = trimesh.load_mesh(RIB, force="mesh", process=False)

# Coupons are exported top-face-down; reorient them to their use/test position for this preview.
for coupon in [corner, rib]:
    rotation = trimesh.transformations.rotation_matrix(angle=3.141592653589793, direction=[0, 1, 0])
    coupon.apply_transform(rotation)
    coupon.apply_translation((-coupon.bounds[0][0], -coupon.bounds[0][1], -coupon.bounds[0][2]))
corner.apply_translation((198, 0, 0))
rib.apply_translation((198, 86, 0))

# The translucent envelope represents a compatible third-party upper organizer tray.
tray = trimesh.creation.box((130, 95, 12))
tray.apply_translation((90, 70, 57))

fig = plt.figure(figsize=(13, 8), facecolor="#112530")
ax = fig.add_subplot(111, projection="3d", facecolor="#112530")
add_mesh(ax, platform, "#5fc8b4")
add_mesh(ax, corner, "#efab58")
add_mesh(ax, rib, "#d98069")
add_mesh(ax, tray, "#dfe8ec", 0.22, "#93a6ae")

combined = trimesh.util.concatenate([platform, corner, rib])
mins, maxs = combined.bounds
padding = 8
ax.set_xlim(mins[0] - padding, maxs[0] + padding)
ax.set_ylim(mins[1] - padding, maxs[1] + padding)
ax.set_zlim(0, max(maxs[2], tray.bounds[1][2]) + padding)
ax.set_box_aspect([float(v) for v in combined.extents])
ax.view_init(elev=25, azim=-58)
ax.set_axis_off()
fig.suptitle("MM-ORG-036 · LIFTDECK 50 · DRAFT DIGITAL CANDIDATE", color="#f5f1e8", fontsize=16, weight="bold")
fig.text(0.5, 0.055, "180 × 140 × 50 mm platform · corner-post and side-rib 2 kg / 30 day comparison coupons", ha="center", color="#c9d7db", fontsize=10)
TARGET.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(TARGET, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
print(TARGET)
