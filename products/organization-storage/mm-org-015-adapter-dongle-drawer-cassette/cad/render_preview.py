#!/usr/bin/env python3
"""Render a deterministic digital-candidate preview for MM-ORG-015."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())
CASSETTE = ROOT / "exports/manufacturing/DRAFT-MM-ORG-015-adapter-dongle-cassette-0.1.0-draft.1.stl"
OUT = ROOT / "renders/MM-ORG-015-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0) -> None:
    triangles = mesh.vertices[mesh.faces]
    collection = Poly3DCollection(triangles, facecolor=color, edgecolor="#203238", linewidth=0.08, alpha=alpha)
    axis.add_collection3d(collection)


def box_mesh(width: float, depth: float, height: float, translation: tuple[float, float, float]) -> trimesh.Trimesh:
    mesh = trimesh.creation.box((width, depth, height))
    mesh.apply_translation((translation[0] + width / 2, translation[1] + depth / 2, translation[2] + height / 2))
    return mesh


def placement(index: int, item: dict) -> dict:
    c = PARAMS["cassette"]
    row, column = divmod(index, c["columns"])
    left = c["margin_mm"] + column * c["cell_pitch_x_mm"]
    bottom = c["margin_mm"] + row * c["cell_pitch_y_mm"]
    right = left + c["cell_pitch_x_mm"]
    center_y = bottom + c["cell_pitch_y_mm"] / 2
    back_inner = right - c["back_inset_mm"]
    rear = back_inner - c["rear_body_clearance_mm"]
    front = rear - item["body_length_mm"]
    return {"front": front, "rear": rear, "center_y": center_y}


def main() -> None:
    cassette = trimesh.load_mesh(CASSETTE, force="mesh", process=True)
    figure = plt.figure(figsize=(13.5, 8.2), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    add_mesh(axis, cassette, "#2f7f86", 0.28)
    palette = ["#b94e5f", "#d98a36", "#d3b044", "#69a46f", "#4b8bb5", "#7b62a4"]
    base_z = PARAMS["cassette"]["base_height_mm"]
    for index, item in enumerate(PARAMS["item_classes"]):
        place = placement(index, item)
        body = box_mesh(
            item["body_length_mm"],
            item["body_width_mm"],
            item["body_height_mm"],
            (place["front"], place["center_y"] - item["body_width_mm"] / 2, base_z),
        )
        add_mesh(axis, body, palette[index % len(palette)], 0.94)
        connector_h = min(4.0, item["body_height_mm"])
        connector = box_mesh(
            item["connector_reach_mm"],
            item["connector_width_mm"],
            connector_h,
            (
                place["front"] - item["connector_reach_mm"],
                place["center_y"] - item["connector_width_mm"] / 2,
                base_z + (item["body_height_mm"] - connector_h) / 2,
            ),
        )
        add_mesh(axis, connector, "#9aa3a6", 0.98)
    axis.set_xlim(-5, 225)
    axis.set_ylim(-8, 170)
    axis.set_zlim(0, 34)
    axis.set_box_aspect((230, 178, 62))
    axis.view_init(elev=31, azim=-58)
    axis.set_axis_off()
    axis.set_title(
        "MM-ORG-015 · 20-position adapter-and-dongle drawer cassette\nvirtual generic envelopes; manufacturing cassette is teal",
        fontsize=15,
        pad=18,
    )
    figure.patch.set_facecolor("#f4f0e8")
    axis.set_facecolor("#f4f0e8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
