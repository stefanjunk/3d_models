#!/usr/bin/env python3
"""Render a deterministic preview from the audited manufacturing meshes."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
OUTPUT = ROOT / "renders/MM-ORG-012-digital-candidate.png"
LIGHT = np.array([-0.55, -0.72, 0.95])
LIGHT /= np.linalg.norm(LIGHT)


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    triangles = mesh.vertices[mesh.faces]
    intensity = 0.60 + 0.44 * (np.clip(mesh.face_normals @ LIGHT, -0.4, 1.0) + 0.4) / 1.4
    base = np.array(to_rgb(color))
    face_colors = np.clip(base[None, :] * intensity[:, None] + 0.04, 0.0, 1.0)
    axis.add_collection3d(
        Poly3DCollection(
            triangles,
            facecolors=np.column_stack((face_colors, np.ones(len(face_colors)))),
            edgecolors="none",
            linewidths=0.0,
            antialiaseds=False,
        )
    )


def main() -> None:
    tray = trimesh.load_mesh(
        ROOT / f"exports/manufacturing/DRAFT-MM-ORG-012-inventory-tray-{REVISION}.stl",
        force="mesh",
        process=False,
    )
    coupon = trimesh.load_mesh(
        ROOT / f"exports/coupons/DRAFT-MM-ORG-012-retrieval-coupon-{REVISION}.stl",
        force="mesh",
        process=False,
    )
    coupon.apply_translation((37.0, -78.0, 0.0))

    figure = plt.figure(figsize=(12.8, 8.4), dpi=160, facecolor="#101721")
    axis = figure.add_subplot(111, projection="3d", facecolor="#101721")
    add_mesh(axis, tray, "#5ca5a0")
    add_mesh(axis, coupon, "#dfa45e")
    axis.set_xlim(-8.0, 188.0)
    axis.set_ylim(-86.0, 148.0)
    axis.set_zlim(0.0, 70.0)
    axis.set_box_aspect((196.0, 234.0, 70.0))
    axis.view_init(elev=34.0, azim=-58.0)
    axis.set_axis_off()
    figure.subplots_adjust(left=0.0, right=1.0, bottom=0.055, top=0.88)
    figure.text(
        0.055,
        0.94,
        "MM-ORG-012 · STATIONERY-REFILL INVENTORY TRAY",
        color="#eef4fa",
        fontsize=17,
        fontweight="bold",
    )
    figure.text(
        0.057,
        0.905,
        "five labeled refill lanes · three scoop pockets · production-derived retrieval coupon",
        color="#aebed0",
        fontsize=10.5,
    )
    figure.text(
        0.057,
        0.035,
        "DRAFT digital candidate · exact Kobra 3 Max / PLA slice passed · physical package retrieval pending",
        color="#91a2b6",
        fontsize=9,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, facecolor=figure.get_facecolor(), pad_inches=0.08)
    plt.close(figure)
    print(OUTPUT)


if __name__ == "__main__":
    main()
