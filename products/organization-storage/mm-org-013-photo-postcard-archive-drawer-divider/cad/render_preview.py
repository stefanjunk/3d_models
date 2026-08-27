#!/usr/bin/env python3
"""Render deterministic installed and gauge previews from manufacturing meshes."""
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
OUTPUT = ROOT / "renders/MM-ORG-013-digital-candidate.png"
LIGHT = np.array([-0.55, -0.72, 0.95])
LIGHT /= np.linalg.norm(LIGHT)


def add_mesh(axis, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0) -> None:
    triangles = mesh.vertices[mesh.faces]
    intensity = 0.60 + 0.44 * (np.clip(mesh.face_normals @ LIGHT, -0.4, 1.0) + 0.4) / 1.4
    base = np.array(to_rgb(color))
    face_colors = np.clip(base[None, :] * intensity[:, None] + 0.04, 0.0, 1.0)
    axis.add_collection3d(
        Poly3DCollection(
            triangles,
            facecolors=np.column_stack((face_colors, np.full(len(face_colors), alpha))),
            edgecolors="none",
            linewidths=0.0,
            antialiaseds=False,
        )
    )


def divider_installed(mesh: trimesh.Trimesh, slot_y: float, thickness: float = 2.0) -> trimesh.Trimesh:
    result = mesh.copy()
    transform = np.array(
        [
            [1.0, 0.0, 0.0, 0.4],
            [0.0, 0.0, -1.0, slot_y + thickness / 2.0],
            [0.0, 1.0, 0.0, 2.05],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    result.apply_transform(transform)
    return result


def main() -> None:
    frame = trimesh.load_mesh(
        ROOT / f"exports/manufacturing/DRAFT-MM-ORG-013-archive-frame-{REVISION}.stl",
        force="mesh",
        process=False,
    )
    labels = ["1900", "1980", "2000", "2010", "2020", "2025"]
    positions = [15.0, 45.0, 75.0, 105.0, 135.0, 150.0]
    dividers = []
    for label, position in zip(labels, positions):
        mesh = trimesh.load_mesh(
            ROOT / f"exports/manufacturing/DRAFT-MM-ORG-013-divider-{label}-{REVISION}.stl",
            force="mesh",
            process=False,
        )
        dividers.append(divider_installed(mesh, position))

    figure = plt.figure(figsize=(12.8, 8.4), dpi=160, facecolor="#101721")
    axis = figure.add_subplot(111, projection="3d", facecolor="#101721")
    add_mesh(axis, frame, "#5ca5a0")
    for divider in dividers:
        add_mesh(axis, divider, "#dfa45e")
    axis.set_xlim(-10.0, 220.0)
    axis.set_ylim(-12.0, 180.0)
    axis.set_zlim(0.0, 95.0)
    axis.set_box_aspect((230.0, 192.0, 95.0))
    axis.view_init(elev=29.0, azim=-58.0)
    axis.set_axis_off()
    figure.subplots_adjust(left=0.0, right=1.0, bottom=0.055, top=0.88)
    figure.text(0.055, 0.94, "MM-ORG-013 · PHOTO / POSTCARD DRAWER INDEX", color="#eef4fa", fontsize=17, fontweight="bold")
    figure.text(0.057, 0.905, "ten receiver positions · six flat-print labels · lateral index gutter beyond 180 mm media", color="#aebed0", fontsize=10.5)
    figure.text(0.057, 0.035, "DRAFT digital candidate · three format gauges included · physical paper and drawer tests pending", color="#91a2b6", fontsize=9)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, facecolor=figure.get_facecolor(), pad_inches=0.08)
    plt.close(figure)
    print(OUTPUT)


if __name__ == "__main__":
    main()
