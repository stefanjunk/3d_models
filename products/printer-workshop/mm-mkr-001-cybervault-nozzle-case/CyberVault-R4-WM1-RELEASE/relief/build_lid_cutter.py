#!/usr/bin/env python3
"""Build a closed binary-STL engraving cutter from the R4 lid height map.

This small project-local generator avoids a runtime dependency on trimesh while
preserving the relief skill's closed two-skin patch architecture.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import struct

import numpy as np
from PIL import Image


def write_binary_stl(target: Path, vertices: np.ndarray, triangles: np.ndarray) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    header = b"CyberVault R4 closed lid engraving cutter".ljust(80, b"\0")
    with target.open("wb") as handle:
        handle.write(header)
        handle.write(struct.pack("<I", len(triangles)))
        for tri in triangles:
            points = vertices[tri].astype(np.float32)
            normal = np.cross(points[1] - points[0], points[2] - points[0])
            length = float(np.linalg.norm(normal))
            if length > 0:
                normal /= length
            handle.write(struct.pack("<3f", *normal))
            handle.write(points.astype("<f4", copy=False).tobytes(order="C"))
            handle.write(struct.pack("<H", 0))


def make_faces(nu: int, nv: int) -> np.ndarray:
    top_faces: list[tuple[int, int, int]] = []
    bottom_faces: list[tuple[int, int, int]] = []
    offset = nu * nv
    for j in range(nv - 1):
        row = j * nu
        next_row = (j + 1) * nu
        for i in range(nu - 1):
            a = row + i
            b = a + 1
            d = next_row + i
            c = d + 1
            top_faces.extend([(a, b, c), (a, c, d)])
            bottom_faces.extend(
                [(offset + a, offset + c, offset + b), (offset + a, offset + d, offset + c)]
            )

    boundary: list[int] = []
    boundary.extend(range(0, nu))
    boundary.extend(j * nu + (nu - 1) for j in range(1, nv))
    boundary.extend((nv - 1) * nu + i for i in range(nu - 2, -1, -1))
    boundary.extend(j * nu for j in range(nv - 2, 0, -1))
    side_faces: list[tuple[int, int, int]] = []
    for index, a in enumerate(boundary):
        b = boundary[(index + 1) % len(boundary)]
        side_faces.extend([(a, offset + a, offset + b), (a, offset + b, b)])

    return np.asarray(top_faces + bottom_faces + side_faces, dtype=np.uint32)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--heightmap", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--width-mm", type=float, default=73.5)
    parser.add_argument("--height-mm", type=float, default=189.5)
    parser.add_argument("--mesh-pitch-mm", type=float, default=0.28)
    parser.add_argument("--depth-mm", type=float, default=0.64)
    parser.add_argument("--overlap-mm", type=float, default=0.08)
    args = parser.parse_args()

    source = Image.open(args.heightmap)
    source_mode = source.mode
    nu = math.ceil(args.width_mm / args.mesh_pitch_mm) + 1
    nv = math.ceil(args.height_mm / args.mesh_pitch_mm) + 1
    sampled = source.resize((nu, nv), Image.Resampling.BILINEAR)
    # Image row zero maps to the print-layout Y minimum. Closing the lid rotates
    # it 180 degrees about the X hinge axis, restoring the artwork's normal
    # top-to-bottom reading direction on the finished exterior.
    field = np.asarray(sampled, dtype=np.float32) / 65535.0
    x = np.linspace(-args.width_mm / 2, args.width_mm / 2, nu, dtype=np.float64)
    y = np.linspace(1.45, 1.45 + args.height_mm, nv, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)
    top = np.column_stack((xx.ravel(), yy.ravel(), (field * args.depth_mm).ravel()))
    bottom = np.column_stack(
        (xx.ravel(), yy.ravel(), np.full(nu * nv, -args.overlap_mm, dtype=np.float64))
    )
    vertices = np.vstack((top, bottom))
    triangles = make_faces(nu, nv)

    tri_points = vertices[triangles]
    signed_volume = float(
        np.einsum(
            "ij,ij->i",
            tri_points[:, 0],
            np.cross(tri_points[:, 1], tri_points[:, 2]),
        ).sum()
        / 6.0
    )
    if signed_volume < 0:
        triangles = triangles[:, [0, 2, 1]]
        signed_volume = -signed_volume

    write_binary_stl(args.output, vertices, triangles)
    report = {
        "status": "PASS",
        "type": "closed-two-skin-engraving-cutter",
        "heightmap": str(args.heightmap),
        "heightmap_mode": source_mode,
        "physical_size_mm": [args.width_mm, args.height_mm],
        "mesh_pitch_requested_mm": args.mesh_pitch_mm,
        "mesh_pitch_actual_mm": [args.width_mm / (nu - 1), args.height_mm / (nv - 1)],
        "grid": [nu, nv],
        "vertices": int(len(vertices)),
        "triangles": int(len(triangles)),
        "depth_mm": args.depth_mm,
        "overlap_mm": args.overlap_mm,
        "bounds_mm": [
            [float(vertices[:, 0].min()), float(vertices[:, 1].min()), float(vertices[:, 2].min())],
            [float(vertices[:, 0].max()), float(vertices[:, 1].max()), float(vertices[:, 2].max())],
        ],
        "signed_volume_mm3": signed_volume,
        "expected_boundary_edges": 0,
        "expected_connected_components": 1,
        "operation": "subtract from lid exterior at z=0; white is deepest",
        "orientation": "source-row-zero-to-object-y-min; upright after 180-degree closure about X",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
