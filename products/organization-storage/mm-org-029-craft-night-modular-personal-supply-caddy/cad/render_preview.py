#!/usr/bin/env python3
"""Render the docked four-caddy system from manufacturing STLs."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
REVISION = "0.1.0-draft.1"


def add_mesh(axis, mesh: trimesh.Trimesh, color: str) -> None:
    collection = Poly3DCollection(mesh.vertices[mesh.faces], facecolor=color, edgecolor="#243b42", linewidth=0.06)
    axis.add_collection3d(collection)


def transform(mesh: trimesh.Trimesh, rotation_deg: float, translation: tuple[float, float, float]) -> trimesh.Trimesh:
    result = mesh.copy()
    if rotation_deg:
        result.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(rotation_deg), [0, 0, 1]))
    result.apply_translation(translation)
    return result


def main() -> None:
    caddy_path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-029-personal-caddy-{REVISION}.stl"
    hub_path = ROOT / f"exports/manufacturing/DRAFT-MM-ORG-029-shared-center-hub-{REVISION}.stl"
    caddy = trimesh.load_mesh(caddy_path, force="mesh", process=False)
    hub = trimesh.load_mesh(hub_path, force="mesh", process=False)
    assemblies = [(hub, "#e0a83d")]
    poses = [(0, (72, -11.5, 0)), (180, (0, 83.5, 0)), (90, (83.5, 72, 0)), (-90, (-11.5, 0, 0))]
    colors = ["#3d9997", "#4ba7a0", "#357f86", "#5caf9f"]
    for pose, color in zip(poses, colors):
        assemblies.append((transform(caddy, *pose), color))
    figure = plt.figure(figsize=(12, 8), dpi=160)
    axis = figure.add_subplot(111, projection="3d")
    for mesh, color in assemblies:
        add_mesh(axis, mesh, color)
    axis.set_xlim(-155, 230)
    axis.set_ylim(-155, 230)
    axis.set_zlim(0, 150)
    axis.set_box_aspect((385, 385, 150))
    axis.view_init(elev=31, azim=-47)
    axis.set_xlabel("table X (mm)")
    axis.set_ylabel("table Y (mm)")
    axis.set_zlabel("height (mm)")
    axis.set_title("MM-ORG-029 · CraftOrbit 4 digital candidate", pad=18)
    axis.grid(False)
    figure.patch.set_facecolor("#f3efe6")
    axis.set_facecolor("#f3efe6")
    figure.tight_layout()
    output = ROOT / "renders/MM-ORG-029-digital-candidate.png"
    figure.savefig(output, bbox_inches="tight")
    print(output)


if __name__ == "__main__":
    main()
