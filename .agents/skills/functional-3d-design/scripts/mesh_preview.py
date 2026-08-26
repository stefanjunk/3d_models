#!/usr/bin/env python3
"""Create a lightweight orthographic-style PNG preview from an STL/OBJ mesh."""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("--out", required=True)
    p.add_argument("--max-faces", type=int, default=35000)
    p.add_argument("--elev", type=float, default=28)
    p.add_argument("--azim", type=float, default=-135)
    args = p.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import trimesh

    loaded = trimesh.load(args.mesh, force="mesh", process=False)
    mesh = loaded
    faces = mesh.faces
    if len(faces) > args.max_faces:
        idx = np.linspace(0, len(faces) - 1, args.max_faces, dtype=int)
        faces = faces[idx]
    else:
        idx = np.arange(len(faces))

    vertices = mesh.vertices
    tri = vertices[faces]

    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(8, 7), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    collection = Poly3DCollection(tri, linewidths=0.02, alpha=1.0)
    light = np.array([-0.4, -0.6, 1.0], dtype=float)
    light /= np.linalg.norm(light)
    normals = mesh.face_normals[idx]
    intensity = np.clip(0.30 + 0.70 * np.maximum(0.0, normals @ light), 0.22, 1.0)
    base = np.array([0.35, 0.58, 0.78])
    colors = np.clip(intensity[:, None] * base[None, :], 0.0, 1.0)
    collection.set_facecolor(colors)
    collection.set_edgecolor("none")
    ax.add_collection3d(collection)
    bounds = mesh.bounds
    center = bounds.mean(axis=0)
    spans = bounds[1] - bounds[0]
    radius = max(spans) / 2 if max(spans) > 0 else 1
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=args.elev, azim=args.azim)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
