#!/usr/bin/env python3
"""Render a deterministic assembled preview of MM-ORG-025."""
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
BASE = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-025-palette-grid-base-{REVISION}.stl"
DIVIDER = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-025-removable-divider-{REVISION}.stl"
GAUGE = ROOT / f"exports/coupons/DRAFT-MM-ORG-025-slot-gauge-{REVISION}.stl"
KEY = ROOT / f"exports/coupons/DRAFT-MM-ORG-025-divider-fit-key-{REVISION}.stl"
OUT = ROOT / "renders/MM-ORG-025-digital-candidate.png"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str, alpha: float = 0.97) -> None:
    axis.add_collection3d(Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor="#25333a", linewidth=0.035, alpha=alpha))


def installed_divider(mesh: trimesh.Trimesh, slot_x: float) -> trimesh.Trimesh:
    result = mesh.copy()
    transform = np.eye(4)
    transform[:3, :3] = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    result.apply_transform(transform)
    bounds = result.bounds
    result.apply_translation((95.0 + slot_x - (bounds[0, 0] + bounds[1, 0]) / 2.0, 53.0 - (bounds[0, 1] + bounds[1, 1]) / 2.0, 2.0 - bounds[0, 2]))
    return result


def main() -> None:
    figure = plt.figure(figsize=(14.0, 8.5), dpi=180)
    axis = figure.add_subplot(111, projection="3d")
    base = trimesh.load_mesh(BASE, force="mesh", process=True)
    divider = trimesh.load_mesh(DIVIDER, force="mesh", process=True)
    add_mesh(axis, base, "#2a8790")
    positions = [(index - (PARAMS["base"]["slot_count"] - 1) / 2.0) * PARAMS["base"]["slot_pitch_mm"] for index in PARAMS["divider"]["default_slot_indices"]]
    for index, slot_x in enumerate(positions):
        add_mesh(axis, installed_divider(divider, slot_x), "#d8893d" if index % 2 == 0 else "#d56755")
    gauge = trimesh.load_mesh(GAUGE, force="mesh", process=True)
    gauge.apply_translation((225.0, 15.0, 0.0))
    add_mesh(axis, gauge, "#8069aa")
    key = trimesh.load_mesh(KEY, force="mesh", process=True)
    key.apply_translation((240.0, 48.0, 0.0))
    add_mesh(axis, key, "#c3a14c")
    axis.set_xlim(-20, 310)
    axis.set_ylim(-25, 150)
    axis.set_zlim(0, 92)
    axis.set_box_aspect((330, 175, 100))
    axis.view_init(elev=31, azim=-58)
    axis.set_axis_off()
    axis.set_title("MM-ORG-025 · PaletteGrid assembled layout + fit-first coupon", fontsize=14, pad=18)
    figure.patch.set_facecolor("#f3efe7")
    axis.set_facecolor("#f3efe7")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    figure.savefig(OUT, bbox_inches="tight", facecolor=figure.get_facecolor())
    print(OUT)


if __name__ == "__main__":
    main()
