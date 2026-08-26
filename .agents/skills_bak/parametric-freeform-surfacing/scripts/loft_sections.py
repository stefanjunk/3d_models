#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from surface_geometry import (
    loft_closed_sections,
    mesh_metrics,
    read_csv_points,
    write_ascii_stl,
    write_json,
    write_obj,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Loft closed 3D CSV sections into a deterministic triangle mesh.")
    parser.add_argument("sections", type=Path, help="Directory containing lexically ordered *.csv sections")
    parser.add_argument("output_obj", type=Path)
    parser.add_argument("--stl", type=Path)
    parser.add_argument("--points-per-section", type=int, default=96)
    parser.add_argument("--no-cap-start", action="store_true")
    parser.add_argument("--no-cap-end", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    paths = sorted(args.sections.glob("*.csv"))
    if len(paths) < 2:
        raise SystemExit(f"Need at least two *.csv sections in {args.sections}")
    sections = []
    for path in paths:
        points = read_csv_points(path)
        if points.shape[1] != 3:
            raise SystemExit(f"Section must be 3D: {path}")
        sections.append(points)
    vertices, faces, alignment = loft_closed_sections(
        sections,
        cap_start=not args.no_cap_start,
        cap_end=not args.no_cap_end,
        point_count=args.points_per_section,
    )
    write_obj(args.output_obj, vertices, faces, object_name="lofted_envelope")
    if args.stl:
        write_ascii_stl(args.stl, vertices, faces, solid_name="lofted_envelope")
    report = {
        "section_files": [str(path) for path in paths],
        "points_per_section": args.points_per_section,
        "alignment": alignment,
        "mesh": mesh_metrics(vertices, faces),
        "outputs": {"obj": str(args.output_obj), "stl": str(args.stl) if args.stl else None},
    }
    if args.report:
        write_json(args.report, report)
    print(f"Wrote {args.output_obj} ({len(vertices)} vertices, {len(faces)} faces)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
