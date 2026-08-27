#!/usr/bin/env python3
"""Render a deterministic assembly preview from manufacturing meshes."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
OUTPUT = ROOT / "renders/MM-ORG-010-digital-candidate.png"
PLATE_OUTPUT = ROOT / "renders/MM-ORG-010-nameplate-detail.png"
LIGHT = np.array([-0.55, -0.75, 0.9])
LIGHT /= np.linalg.norm(LIGHT)


def add_mesh(axis, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0) -> None:
    triangles = mesh.vertices[mesh.faces]
    intensity = 0.60 + 0.44 * (np.clip(mesh.face_normals @ LIGHT, -0.4, 1.0) + 0.4) / 1.4
    base = np.array(to_rgb(color))
    face_colors = np.clip(base[None, :] * intensity[:, None] + 0.04, 0.0, 1.0)
    rgba = np.column_stack((face_colors, np.full(len(face_colors), alpha)))
    axis.add_collection3d(
        Poly3DCollection(
            triangles,
            facecolors=rgba,
            edgecolors=(0.07, 0.10, 0.14, 0.18),
            linewidths=0.08,
        )
    )


def main() -> None:
    body_path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-010-caddy-chassis-{REVISION}.stl"
    plate_path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-010-personalized-nameplate-{REVISION}.stl"
    body = trimesh.load_mesh(body_path, force="mesh", process=False)
    plate_print = trimesh.load_mesh(plate_path, force="mesh", process=False)
    plate_assembly = plate_print.copy()
    plate_assembly.apply_transform(
        np.array(
            [
                [1.0, 0.0, 0.0, 7.0],
                [0.0, 0.0, -1.0, -3.0],
                [0.0, 1.0, 0.0, 8.2],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
    )

    figure = plt.figure(figsize=(12.8, 8.2), dpi=160, facecolor="#101721")
    axis = figure.add_subplot(111, projection="3d", facecolor="#101721")
    add_mesh(axis, body, "#65a79d")
    add_mesh(axis, plate_assembly, "#e6a15b")
    axis.set_xlim(-8.0, 160.0)
    axis.set_ylim(-8.0, 132.0)
    axis.set_zlim(0.0, 135.0)
    axis.set_box_aspect((168.0, 140.0, 135.0))
    axis.view_init(elev=25.0, azim=-61.0)
    axis.set_axis_off()
    figure.subplots_adjust(left=0.0, right=1.0, bottom=0.055, top=0.88)
    figure.text(
        0.055,
        0.94,
        "MM-ORG-010 · PERSONALIZED STATIONERY CADDY",
        color="#eef4fa",
        fontsize=17,
        fontweight="bold",
    )
    figure.text(
        0.057,
        0.905,
        "three tall wells · small-item tray · passive phone cradle · slide plate shown exploded",
        color="#aebed0",
        fontsize=10.5,
    )
    figure.text(
        0.057,
        0.035,
        "DRAFT digital model · plate fit, phone stability, tall-item tipping and exact slicing pending",
        color="#91a2b6",
        fontsize=9,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, facecolor=figure.get_facecolor(), pad_inches=0.08)
    plt.close(figure)

    detail, detail_axis = plt.subplots(figsize=(13.6, 3.8), dpi=160, facecolor="#101721")
    detail_axis.set_facecolor("#101721")
    upward_faces = plate_print.face_normals[:, 2] > 0.9
    top_faces = upward_faces & (plate_print.triangles_center[:, 2] > 1.95)
    recess_faces = upward_faces & (plate_print.triangles_center[:, 2] < 1.8)
    top_triangles = plate_print.vertices[plate_print.faces[top_faces]][:, :, :2]
    recess_triangles = plate_print.vertices[plate_print.faces[recess_faces]][:, :, :2]
    detail_axis.add_collection(
        PolyCollection(
            top_triangles,
            facecolors="#e6a15b",
            edgecolors="none",
        )
    )
    detail_axis.add_collection(
        PolyCollection(
            recess_triangles,
            facecolors="#553a2d",
            edgecolors="none",
        )
    )
    detail_axis.set_xlim(-2.0, 138.0)
    detail_axis.set_ylim(-2.0, 29.0)
    detail_axis.set_aspect("equal")
    detail_axis.set_axis_off()
    detail.subplots_adjust(left=0.01, right=0.99, bottom=0.03, top=0.82)
    detail.text(
        0.02,
        0.90,
        "PRINT-FACE DETAIL · EMBEDDED 5×7 GLYPHS · 0.6 mm RECESSED",
        color="#eef4fa",
        fontsize=13,
        fontweight="bold",
    )
    detail.savefig(PLATE_OUTPUT, facecolor=detail.get_facecolor(), pad_inches=0.04)
    plt.close(detail)
    print(OUTPUT)
    print(PLATE_OUTPUT)


if __name__ == "__main__":
    main()
