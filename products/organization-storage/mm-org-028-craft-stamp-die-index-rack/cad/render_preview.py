#!/usr/bin/env python3
"""Render the selected rack with four installed index frames from manufacturing STLs."""
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


def add_mesh(axis, mesh: trimesh.Trimesh, color: str, alpha: float = 1.0) -> None:
    faces = mesh.vertices[mesh.faces]
    collection = Poly3DCollection(faces, facecolor=color, edgecolor="#243b42", linewidth=0.08, alpha=alpha)
    axis.add_collection3d(collection)


def main() -> None:
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())
    rack_info = interface["metrics"]["interfaces"]["rack"]
    rack_path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-028-rack-{REVISION}.stl"
    rack = trimesh.load_mesh(rack_path, force="mesh", process=False)
    meshes = [(rack, "#43a5a3")]
    labels = ["stamps", "dies", "alpha", "floral"]
    lanes = [1, 5, 9, 13]
    rotation = trimesh.transformations.rotation_matrix(np.deg2rad(120), [1, 1, 1])
    for index, (label, lane) in enumerate(zip(labels, lanes), 1):
        path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-028-index-divider-{index:02d}-{label}-{REVISION}.stl"
        mesh = trimesh.load_mesh(path, force="mesh", process=False)
        mesh.apply_transform(rotation)
        slot = rack_info["slots"][lane]
        mesh.apply_translation([slot["x0_mm"] + 0.2, 4.0, 3.0])
        meshes.append((mesh, "#e0a83d" if index % 2 else "#d88948"))
    figure = plt.figure(figsize=(12, 8), dpi=160)
    axis = figure.add_subplot(111, projection="3d")
    for mesh, color in meshes:
        add_mesh(axis, mesh, color)
    axis.set_xlim(0, 220)
    axis.set_ylim(0, 160)
    axis.set_zlim(0, 205)
    axis.set_box_aspect((220, 160, 205))
    axis.view_init(elev=25, azim=-55)
    axis.set_xlabel("rack lanes / X (mm)")
    axis.set_ylabel("envelope width / Y (mm)")
    axis.set_zlabel("index height / Z (mm)")
    axis.set_title("MM-ORG-028 · IndexDock 15 digital candidate", pad=18)
    axis.grid(False)
    figure.patch.set_facecolor("#f2eee5")
    axis.set_facecolor("#f2eee5")
    figure.tight_layout()
    output = ROOT / "renders/MM-ORG-028-digital-candidate.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, bbox_inches="tight")
    print(output)


if __name__ == "__main__":
    main()
