#!/usr/bin/env python3
"""Render a lightweight isometric QA preview from the assembled STL."""

from __future__ import annotations

import struct
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "output" / "assembly" / "desk_organizer_assembly_preview.stl"
OUTPUT = ROOT / "output" / "assembly" / "desk_organizer_preview.png"


def read_binary(path: Path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    triangles = np.empty((count, 3, 3), dtype=np.float32)
    offset = 84
    for i in range(count):
        values = struct.unpack_from("<12fH", data, offset)
        triangles[i, 0] = values[3:6]
        triangles[i, 1] = values[6:9]
        triangles[i, 2] = values[9:12]
        offset += 50
    return triangles


def main():
    tris = read_binary(INPUT)
    # Uniform downsampling keeps the preview responsive while retaining all major forms.
    stride = max(1, len(tris) // 45000)
    shown = tris[::stride]
    normals = np.cross(shown[:, 1] - shown[:, 0], shown[:, 2] - shown[:, 0])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.maximum(lengths, 1e-9)
    light = np.array([-0.35, -0.55, 0.75], dtype=np.float32)
    light /= np.linalg.norm(light)
    shade = np.clip(0.28 + 0.72 * np.abs(normals @ light), 0, 1)
    base = np.array([0.10, 0.12, 0.15])
    colors = np.clip(base[None, :] + shade[:, None] * np.array([0.34, 0.38, 0.43]), 0, 1)

    fig = plt.figure(figsize=(11, 8), dpi=180)
    ax = fig.add_subplot(111, projection="3d")
    collection = Poly3DCollection(shown, facecolors=colors, edgecolors="none", linewidths=0)
    ax.add_collection3d(collection)

    mins = shown.reshape(-1, 3).min(axis=0)
    maxs = shown.reshape(-1, 3).max(axis=0)
    centers = (mins + maxs) / 2
    span = float((maxs - mins).max()) * 0.57
    ax.set_xlim(centers[0] - span, centers[0] + span)
    ax.set_ylim(centers[1] - span, centers[1] + span)
    ax.set_zlim(max(0, centers[2] - span), centers[2] + span)
    ax.view_init(elev=24, azim=-63)
    ax.set_box_aspect((1, 0.82, 0.78))
    ax.set_axis_off()
    fig.patch.set_facecolor("#f4f5f7")
    ax.set_facecolor("#f4f5f7")
    ax.set_title("Modern Carbon Desk Organizer — assembly preview", fontsize=15, pad=4)
    fig.tight_layout(pad=0.2)
    fig.savefig(OUTPUT, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
