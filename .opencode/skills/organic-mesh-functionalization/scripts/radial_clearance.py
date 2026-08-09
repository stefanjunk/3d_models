#!/usr/bin/env python3
"""Estimate conservative radial clearance for an axial cavity from mesh cross-sections."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from common import dump_json, load_mesh


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("--axis", choices=["x", "y", "z"], default="z")
    p.add_argument("--center", type=float, nargs=2, required=True, metavar=("U", "V"), help="Center in the two radial axes")
    p.add_argument("--positions", type=float, nargs="+", required=True)
    p.add_argument("--required-wall", type=float, required=True)
    p.add_argument("--uncertainty", type=float, default=0.2)
    p.add_argument("--ignore-below-percentile", type=float, default=0.0, help="0 is conservative minimum; higher values may ignore small protrusions and require manual review")
    p.add_argument("--json-out")
    args = p.parse_args()

    mesh = load_mesh(args.mesh, process=True)
    ai = {"x": 0, "y": 1, "z": 2}[args.axis]
    radial_axes = [i for i in range(3) if i != ai]
    normal = np.zeros(3); normal[ai] = 1.0
    center = np.asarray(args.center, dtype=float)
    rows = []
    for position in args.positions:
        origin = np.zeros(3); origin[ai] = position
        section = mesh.section(plane_origin=origin, plane_normal=normal)
        if section is None:
            rows.append({"position_mm": position, "status": "no-section"})
            continue
        points = np.concatenate([np.asarray(line)[:, radial_axes] for line in section.discrete if len(line)], axis=0)
        radii = np.linalg.norm(points - center, axis=1)
        percentile = float(np.percentile(radii, args.ignore_below_percentile))
        permitted = percentile - args.required_wall - args.uncertainty
        rows.append({
            "position_mm": position,
            "samples": int(len(radii)),
            "radial_value_mm": percentile,
            "raw_min_mm": float(np.min(radii)),
            "permitted_inner_radius_mm": float(permitted),
        })
    valid = [r["permitted_inner_radius_mm"] for r in rows if "permitted_inner_radius_mm" in r]
    report = {
        "mesh": str(Path(args.mesh).resolve()),
        "axis": args.axis,
        "radial_center": args.center,
        "required_wall_mm": args.required_wall,
        "uncertainty_mm": args.uncertainty,
        "ignored_lower_percentile": args.ignore_below_percentile,
        "sections": rows,
        "global_conservative_inner_radius_mm": min(valid) if valid else None,
        "warning": "Cross-sections may include courtyard, decorations, internal shells, or unrelated components; select/segment the tower body and visually review every limiting section.",
    }
    print(dump_json(report, args.json_out))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
