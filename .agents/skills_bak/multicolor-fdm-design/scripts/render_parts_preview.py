#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh

from common import hex_to_rgb01, resolve_manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a simple colored preview of a parts manifest.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-faces-per-part", type=int, default=12000)
    parser.add_argument("--elev", type=float, default=28)
    parser.add_argument("--azim", type=float, default=-55)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    fig = plt.figure(figsize=(8, 6), dpi=130)
    ax = fig.add_subplot(111, projection="3d")
    all_vertices = []
    all_triangles = []
    all_colors = []
    for part in manifest.get("parts", []):
        path = resolve_manifest_path(args.manifest.resolve(), str(part["path"]))
        loaded = trimesh.load(path, force="scene", process=True)
        scene = loaded if isinstance(loaded, trimesh.Scene) else trimesh.Scene(loaded)
        mesh = trimesh.util.concatenate([g for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)])
        faces = np.asarray(mesh.faces)
        if len(faces) > args.max_faces_per_part:
            step = int(np.ceil(len(faces) / args.max_faces_per_part))
            faces = faces[::step]
        triangles = np.asarray(mesh.vertices)[faces]
        color = hex_to_rgb01(str(part.get("display_hex", "#808080")))
        all_triangles.append(triangles)
        all_colors.extend([color] * len(triangles))
        all_vertices.append(np.asarray(mesh.vertices))
    if all_triangles:
        collection = Poly3DCollection(np.concatenate(all_triangles, axis=0), facecolors=all_colors, edgecolor="none", linewidth=0.0, alpha=1.0)
        ax.add_collection3d(collection)
    if not all_vertices:
        raise SystemExit("No parts found")
    vertices = np.vstack(all_vertices)
    low = vertices.min(axis=0)
    high = vertices.max(axis=0)
    center = (low + high) / 2.0
    radius = max((high - low).max() / 2.0, 1.0)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=args.elev, azim=args.azim)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, transparent=False, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
