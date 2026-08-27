#!/usr/bin/env python3
"""Render a deterministic digital-candidate preview for MM-ORG-014."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())
DOCK = ROOT / "exports/manufacturing/DRAFT-MM-ORG-014-palette-dock-0.1.0-draft.1.stl"
OUT = ROOT / "renders/MM-ORG-014-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0) -> None:
    triangles = mesh.vertices[mesh.faces]
    collection = Poly3DCollection(triangles, facecolor=color, edgecolor="#203238", linewidth=0.08, alpha=alpha)
    axis.add_collection3d(collection)


def box_mesh(width: float, depth: float, height: float, translation: tuple[float, float, float]) -> trimesh.Trimesh:
    mesh = trimesh.creation.box((width, depth, height))
    mesh.apply_translation((translation[0] + width / 2, translation[1] + depth / 2, translation[2] + height / 2))
    return mesh


def seat_z(thickness: float) -> float:
    slot = PARAMS["slot"]
    target = thickness if thickness <= slot["throat_width_mm"] else thickness + 0.2
    if target <= slot["throat_width_mm"]:
        return slot["bottom_z_mm"]
    return slot["bottom_z_mm"] + (target - slot["throat_width_mm"]) * (slot["shoulder_z_mm"] - slot["bottom_z_mm"]) / (slot["mid_width_mm"] - slot["throat_width_mm"])


def main() -> None:
    dock = trimesh.load_mesh(DOCK, force="mesh", process=True)
    figure = plt.figure(figsize=(13.5, 8.2), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    add_mesh(axis, dock, "#286873")
    palette = ["#b73a53", "#de8b35", "#d4b044", "#5b9a68", "#3d82a8", "#765a9e"]
    d = PARAMS["dock"]
    positions = [d["first_position_y_mm"] + i * d["slot_pitch_mm"] for i in range(d["positions_per_lane"])]
    standards = PARAMS["card_standards"]
    color_index = 0
    for lane_index, center_x in enumerate(d["lane_centers_x_mm"]):
        for position_index, center_y in enumerate(positions):
            card = standards[(lane_index + position_index) % len(standards)]
            z = seat_z(card["thickness_mm"])
            mesh = box_mesh(card["width_mm"], card["thickness_mm"], card["height_mm"], (center_x - card["width_mm"] / 2, center_y - card["thickness_mm"] / 2, z))
            add_mesh(axis, mesh, palette[color_index % len(palette)], 0.92)
            color_index += 1
    axis.set_xlim(-5, 225)
    axis.set_ylim(-8, 125)
    axis.set_zlim(0, 70)
    axis.set_box_aspect((230, 133, 85))
    axis.view_init(elev=28, azim=-57)
    axis.set_axis_off()
    axis.set_title("MM-ORG-014 · 30-colour embroidery-floss project palette dock\nvirtual card envelopes; manufacturing dock is teal", fontsize=15, pad=18)
    figure.patch.set_facecolor("#f4f0e8")
    axis.set_facecolor("#f4f0e8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
