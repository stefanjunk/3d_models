#!/usr/bin/env python3
"""Render a deterministic assembled preview of MM-ORG-026 SignRail."""
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
REVISION = "0.1.0-draft.1"
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())
PLATE = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-026-personalized-insert-{REVISION}.stl"
STAND = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-026-angled-end-stand-{REVISION}.stl"
GAUGE = ROOT / f"exports/coupons/DRAFT-MM-ORG-026-angled-slot-gauge-{REVISION}.stl"
KEY = ROOT / f"exports/coupons/DRAFT-MM-ORG-026-insert-fit-key-{REVISION}.stl"
OUT = ROOT / "renders/MM-ORG-026-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    axis.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor="#25333a", linewidth=0.035, alpha=0.98))


def installed_plate(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    result = mesh.copy()
    angle = np.radians(PARAMS["stand"]["slot_angle_from_horizontal_deg"])
    transform = np.eye(4)
    transform[:3, :3] = np.array([[1.0, 0.0, 0.0], [0.0, np.cos(angle), -np.sin(angle)], [0.0, np.sin(angle), np.cos(angle)]])
    result.apply_transform(transform)
    result.apply_translation((0.0, 31.0 + PARAMS["stand"]["slot_bottom_y_mm"], PARAMS["stand"]["slot_bottom_z_mm"]))
    return result


def main() -> None:
    figure = plt.figure(figsize=(14.0, 8.5), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    plate = installed_plate(trimesh.load_mesh(PLATE, force="mesh", process=True))
    add_mesh(axis, plate, "#285966")
    stand_mesh = trimesh.load_mesh(STAND, force="mesh", process=True)
    for center_x, color in zip((22.0, 178.0), ("#d7893e", "#d46656")):
        stand = stand_mesh.copy()
        stand.apply_translation((center_x - 13.0, 0.0, 0.0))
        add_mesh(axis, stand, color)
    gauge = trimesh.load_mesh(GAUGE, force="mesh", process=True)
    gauge.apply_translation((225.0, 5.0, 0.0))
    add_mesh(axis, gauge, "#8069aa")
    key = trimesh.load_mesh(KEY, force="mesh", process=True)
    key.apply_translation((252.0, 48.0, 0.0))
    add_mesh(axis, key, "#c2a04d")
    axis.set_xlim(-25, 325)
    axis.set_ylim(-25, 115)
    axis.set_zlim(0, 68)
    axis.set_box_aspect((350, 140, 72))
    axis.view_init(elev=23, azim=-61)
    axis.set_axis_off()
    axis.set_title("MM-ORG-026 · SignRail live-proofed insert + two stands + fit coupon", fontsize=14, pad=18)
    figure.patch.set_facecolor("#f3efe7")
    axis.set_facecolor("#f3efe7")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
