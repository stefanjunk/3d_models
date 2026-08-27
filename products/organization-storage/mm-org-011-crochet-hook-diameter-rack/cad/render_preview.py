#!/usr/bin/env python3
"""Render deterministic rack and gauge-card previews from manufacturing meshes."""
from pathlib import Path
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"
LIGHT = np.array([-0.55, -0.75, 0.9])
LIGHT /= np.linalg.norm(LIGHT)


def add_mesh(axis, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0, edges: bool = True) -> None:
    triangles = mesh.vertices[mesh.faces]
    intensity = 0.60 + 0.44 * (np.clip(mesh.face_normals @ LIGHT, -0.4, 1.0) + 0.4) / 1.4
    base = np.array(to_rgb(color))
    face_colors = np.clip(base[None, :] * intensity[:, None] + 0.04, 0.0, 1.0)
    rgba = np.column_stack((face_colors, np.full(len(face_colors), alpha)))
    axis.add_collection3d(Poly3DCollection(
        triangles,
        facecolors=rgba,
        edgecolors=(0.07, 0.10, 0.14, 0.14) if edges else "none",
        linewidths=0.07,
    ))


def main() -> None:
    parameters = json.loads((ROOT / "config/model-parameters.json").read_text(encoding="utf-8"))
    rack_p = parameters["rack"]
    profiles = parameters["hook_profiles"]
    rack = trimesh.load_mesh(
        ROOT / f"exports/manufacturing/DRAFT-MM-ORG-011-crochet-hook-rack-{REVISION}.stl",
        force="mesh",
        process=False,
    )
    card = trimesh.load_mesh(
        ROOT / f"exports/manufacturing/DRAFT-MM-ORG-011-handle-profile-card-{REVISION}.stl",
        force="mesh",
        process=False,
    )

    figure = plt.figure(figsize=(13.2, 8.5), dpi=160, facecolor="#101721")
    axis = figure.add_subplot(111, projection="3d", facecolor="#101721")
    add_mesh(axis, rack, "#5d8fa6")
    hook_colors = ["#ee9b54", "#e56b6f", "#d8c45d", "#8cc084", "#b58bd4"]
    for index, profile in enumerate(profiles):
        row = index // rack_p["columns"]
        column = index % rack_p["columns"]
        x_coord = rack_p["side_margin"] + (column + 0.5) * rack_p["column_pitch"]
        front = rack_p["front_margin"] + row * rack_p["row_pitch"]
        y_coord = front + rack_p["shelf_depth"] - rack_p["slot_end_from_back"]
        z_level = rack_p["shelf_levels"][row] + rack_p["shelf_thickness"]
        shaft = trimesh.creation.cylinder(radius=profile["shaft_diameter"] / 2.0, height=58.0, sections=18)
        shaft.apply_translation((x_coord, y_coord, z_level - 20.0))
        handle = trimesh.creation.cylinder(radius=profile["handle_major"] / 2.0, height=34.0, sections=22)
        handle.apply_translation((x_coord, y_coord, z_level + 17.0))
        add_mesh(axis, shaft, hook_colors[column], alpha=0.72, edges=False)
        add_mesh(axis, handle, hook_colors[column], alpha=0.83, edges=False)
    axis.set_xlim(-10, 215)
    axis.set_ylim(-8, 122)
    axis.set_zlim(0, 160)
    axis.set_box_aspect((225, 130, 160))
    axis.view_init(elev=24, azim=-63)
    axis.set_axis_off()
    figure.subplots_adjust(left=0, right=1, bottom=0.05, top=0.88)
    figure.text(0.05, 0.94, "MM-ORG-011 · CROCHET-HOOK DIAMETER RACK", color="#eef4fa", fontsize=17, fontweight="bold")
    figure.text(0.052, 0.905, "15 measured side-entry slots · 3 stepped tiers · simulated hook envelopes", color="#aebed0", fontsize=10.5)
    figure.text(0.052, 0.032, "DRAFT digital candidate · physical hook fit, abrasion and loaded stability deferred", color="#91a2b6", fontsize=9)
    output = ROOT / "renders/MM-ORG-011-digital-candidate.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, facecolor=figure.get_facecolor(), pad_inches=0.08)
    plt.close(figure)

    card_figure = plt.figure(figsize=(13.2, 5.4), dpi=160, facecolor="#101721")
    card_axis = card_figure.add_subplot(111, projection="3d", facecolor="#101721")
    add_mesh(card_axis, card, "#d8b46c")
    card_axis.set_xlim(-5, 215)
    card_axis.set_ylim(-5, 77)
    card_axis.set_zlim(0, 18)
    card_axis.set_box_aspect((220, 82, 25))
    card_axis.view_init(elev=58, azim=-84)
    card_axis.set_axis_off()
    card_figure.subplots_adjust(left=0, right=1, bottom=0.03, top=0.82)
    card_figure.text(0.04, 0.91, "FIRST-PRINT PROFILE CARD", color="#eef4fa", fontsize=16, fontweight="bold")
    card_figure.text(0.042, 0.86, "top edge: 15 shaft notches · bottom edge: 9 handle-envelope notches", color="#aebed0", fontsize=10)
    card_output = ROOT / "renders/MM-ORG-011-measurement-card.png"
    card_figure.savefig(card_output, facecolor=card_figure.get_facecolor(), pad_inches=0.06)
    plt.close(card_figure)
    print(output)
    print(card_output)


if __name__ == "__main__":
    main()
