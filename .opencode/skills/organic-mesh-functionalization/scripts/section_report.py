#!/usr/bin/env python3
"""Measure mesh cross-section loops, approximate areas, and 2D bounds at selected positions."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import dump_json, load_mesh


def polygon_area(points2: np.ndarray) -> float:
    if len(points2) < 3:
        return 0.0
    x = points2[:, 0]
    y = points2[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("--axis", choices=["x", "y", "z"], default="z")
    p.add_argument("--positions", type=float, nargs="+", required=True)
    p.add_argument("--json-out")
    args = p.parse_args()

    mesh = load_mesh(args.mesh, process=True)
    ai = {"x": 0, "y": 1, "z": 2}[args.axis]
    proj = [i for i in range(3) if i != ai]
    normal = np.zeros(3)
    normal[ai] = 1.0
    rows = []
    for pos in args.positions:
        origin = np.zeros(3)
        origin[ai] = pos
        section = mesh.section(plane_origin=origin, plane_normal=normal)
        if section is None:
            rows.append({"position_mm": pos, "loops": 0, "approx_area_mm2": 0.0, "bounds_2d_mm": None})
            continue
        loops = [np.asarray(x) for x in section.discrete if len(x) >= 3]
        allp = np.concatenate([x[:, proj] for x in loops], axis=0) if loops else np.empty((0, 2))
        area = sum(polygon_area(x[:, proj]) for x in loops)
        bounds = [allp.min(axis=0).tolist(), allp.max(axis=0).tolist()] if len(allp) else None
        rows.append({"position_mm": pos, "loops": len(loops), "approx_area_mm2": area, "bounds_2d_mm": bounds, "polyline_points": int(sum(len(x) for x in loops))})
    report = {"mesh": str(Path(args.mesh).resolve()), "axis": args.axis, "sections": rows, "warning": "Area is the sum of absolute loop areas and does not classify nested holes; use visual review for complex multi-loop sections."}
    print(dump_json(report, args.json_out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
