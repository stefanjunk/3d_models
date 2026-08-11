#!/usr/bin/env python3
"""Write a binary STL in bounded-memory chunks from raw Manifold mesh arrays."""

from __future__ import annotations

import argparse
import os
import struct
from pathlib import Path

import numpy as np

RECORD = np.dtype(
    [("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")],
    align=False,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertices", required=True, type=Path)
    parser.add_argument("--indices", required=True, type=Path)
    parser.add_argument("--num-prop", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    vertices = np.memmap(args.vertices, dtype="<f4", mode="r").reshape(-1, args.num_prop)
    indices = np.memmap(args.indices, dtype="<u4", mode="r")
    if len(indices) % 3:
        raise ValueError("Triangle index array length is not divisible by three")
    triangle_count = len(indices) // 3
    if triangle_count > 0xFFFFFFFF:
        raise ValueError("Binary STL triangle count exceeds uint32")

    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    header = bytearray(84)
    label = b"MANIFOLD-3D DESK ORGANIZER R1.1.2"
    header[: len(label)] = label
    struct.pack_into("<I", header, 80, triangle_count)
    with tmp.open("wb") as stream:
        stream.write(header)
        stream.truncate(84 + triangle_count * RECORD.itemsize)

    records = np.memmap(tmp, dtype=RECORD, mode="r+", offset=84, shape=(triangle_count,))
    chunk = 200_000
    for start in range(0, triangle_count, chunk):
        end = min(start + chunk, triangle_count)
        ids = np.asarray(indices[3 * start : 3 * end]).reshape(-1, 3)
        tri = np.asarray(vertices[ids, :3], dtype=np.float32)
        normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        lengths = np.linalg.norm(normal, axis=1)
        normal /= np.maximum(lengths[:, None], np.float32(1e-20))
        records["normal"][start:end] = normal
        records["vertices"][start:end] = tri
        records["attribute"][start:end] = 0
    records.flush()
    del records, indices, vertices
    os.replace(tmp, args.output)
    args.vertices.unlink()
    args.indices.unlink()


if __name__ == "__main__":
    main()
