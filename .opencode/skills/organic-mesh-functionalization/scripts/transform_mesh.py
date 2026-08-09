#!/usr/bin/env python3
"""Apply a recorded homogeneous transform to a mesh and export a new file."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from common import dump_json, load_mesh


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("output")
    p.add_argument("--matrix-json", help="JSON file containing matrix or {'matrix': [[...]]}")
    p.add_argument("--translate", type=float, nargs=3, default=[0, 0, 0])
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--json-out")
    args = p.parse_args()

    matrix = np.eye(4)
    matrix[:3, :3] *= args.scale
    matrix[:3, 3] = args.translate
    if args.matrix_json:
        raw = json.loads(Path(args.matrix_json).read_text(encoding="utf-8"))
        matrix = np.asarray(raw.get("matrix", raw), dtype=float)
        if matrix.shape != (4, 4):
            raise SystemExit("Transform matrix must be 4x4")
    mesh = load_mesh(args.mesh, process=False)
    mesh.apply_transform(matrix)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(out)
    print(dump_json({"output": str(out.resolve()), "matrix": matrix.tolist(), "extents_mm": mesh.extents.tolist()}, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
