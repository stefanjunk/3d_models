#!/usr/bin/env python3
"""Render front and isometric QA views from the exported assembly STL."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh


ROOT = Path(__file__).resolve().parent


def add_mesh(ax, triangles: np.ndarray, elev: float, azim: float, base_color: np.ndarray) -> None:
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.maximum(lengths, 1.0e-9)
    elev_r, azim_r = np.deg2rad([elev, azim])
    camera = np.array(
        [np.cos(elev_r) * np.cos(azim_r), np.cos(elev_r) * np.sin(azim_r), np.sin(elev_r)]
    )
    facing = normals @ camera > 0.0
    shown = triangles[facing]
    shown_normals = normals[facing]
    light = np.array([-0.25, -0.45, 0.86])
    light /= np.linalg.norm(light)
    shade = np.clip(0.30 + 0.70 * np.abs(shown_normals @ light), 0.0, 1.0)
    colors = np.clip(base_color[None, :] * (0.55 + 0.65 * shade[:, None]), 0.0, 1.0)
    ax.add_collection3d(
        Poly3DCollection(shown, facecolors=colors, edgecolors="none", linewidths=0, zsort="min")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "output" / "rev-0.2.0-draft" / "preview" / "premium_over_toilet_shelf_assembly.stl",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "rev-0.2.0-draft" / "preview" / "premium_over_toilet_shelf_preview.png",
    )
    args = parser.parse_args()
    mesh = trimesh.load(args.input, force="mesh", process=False)
    triangles = np.asarray(mesh.triangles, dtype=np.float32)
    mins = triangles.reshape(-1, 3).min(axis=0)
    maxs = triangles.reshape(-1, 3).max(axis=0)
    extents = maxs - mins
    padding = np.maximum(extents * 0.06, np.array([24.0, 24.0, 36.0]))

    fig = plt.figure(figsize=(14, 8), dpi=170)
    views = [(20.0, -58.0, "Isometric assembly"), (3.0, -90.0, "Front elevation")]
    for index, (elev, azim, title) in enumerate(views, start=1):
        ax = fig.add_subplot(1, 2, index, projection="3d")
        add_mesh(ax, triangles, elev, azim, np.array([0.43, 0.52, 0.46]))
        ax.set_xlim(mins[0] - padding[0], maxs[0] + padding[0])
        ax.set_ylim(mins[1] - padding[1], maxs[1] + padding[1])
        ax.set_zlim(max(0.0, mins[2] - padding[2]), maxs[2] + padding[2])
        ax.view_init(elev=elev, azim=azim)
        ax.set_box_aspect(
            (
                float(extents[0]),
                float(max(extents[1], extents[0] * 0.38)),
                float(extents[2]),
            )
        )
        ax.set_axis_off()
        ax.set_title(title, fontsize=13, pad=2)
        ax.set_facecolor("#f2efe8")
    fig.suptitle("Premium Over-Toilet Shelf R0.2.0 — DRAFT CAD QA Preview", fontsize=16)
    fig.patch.set_facecolor("#f2efe8")
    fig.tight_layout(pad=0.6)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
