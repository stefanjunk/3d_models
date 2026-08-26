#!/usr/bin/env python3
"""Optional CadQuery/OpenCascade loft backend for registered closed CSV sections."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from surface_geometry import align_closed_sections, mesh_metrics, read_csv_points, weld_vertices, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an OpenCascade loft solid and export STEP/STL from closed 3D CSV sections.")
    parser.add_argument("sections", type=Path)
    parser.add_argument("output_step", type=Path)
    parser.add_argument("--stl", type=Path)
    parser.add_argument("--points-per-section", type=int, default=48)
    parser.add_argument("--fit-tolerance-mm", type=float, default=0.02)
    parser.add_argument("--mesh-tolerance-mm", type=float, default=0.05)
    parser.add_argument("--angular-tolerance-rad", type=float, default=0.08)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        import cadquery as cq
    except Exception as exc:
        raise SystemExit(f"CadQuery is not available; backend status is NOT_RUN: {exc}")

    section_paths = sorted(args.sections.glob("*.csv"))
    if len(section_paths) < 2:
        raise SystemExit(f"Need at least two section CSV files in {args.sections}")
    raw_sections = [read_csv_points(path) for path in section_paths]
    if any(section.shape[1] != 3 for section in raw_sections):
        raise SystemExit("Every section must contain x,y,z coordinates")
    sections, alignment = align_closed_sections(raw_sections, point_count=args.points_per_section)
    wires = []
    for section in sections:
        edge = cq.Edge.makeSpline(
            [cq.Vector(float(x), float(y), float(z)) for x, y, z in section],
            periodic=True,
            tol=args.fit_tolerance_mm,
        )
        wires.append(cq.Wire.assembleEdges([edge]))
    solid = cq.Solid.makeLoft(wires, ruled=False)
    args.output_step.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(args.output_step), exportType="STEP", unit="MM")
    if args.stl:
        args.stl.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(
            solid,
            str(args.stl),
            exportType="STL",
            tolerance=args.mesh_tolerance_mm,
            angularTolerance=args.angular_tolerance_rad,
            unit="MM",
        )
    tess_vertices, tess_faces = solid.tessellate(args.mesh_tolerance_mm, args.angular_tolerance_rad)
    vertices = np.asarray([[v.x, v.y, v.z] for v in tess_vertices], dtype=float)
    faces = np.asarray(tess_faces, dtype=np.int64)
    welded_vertices, welded_faces = weld_vertices(
        vertices,
        faces,
        tolerance=max(args.mesh_tolerance_mm * 1e-3, 1e-8),
    )
    report = {
        "status": "PASS" if solid.isValid() else "FAIL",
        "cadquery_version": str(getattr(cq, "__version__", "unknown")),
        "sections": [str(path) for path in section_paths],
        "alignment": alignment,
        "solid_valid": bool(solid.isValid()),
        "solid_volume_mm3": float(solid.Volume()),
        "mesh_raw_patch_tessellation": mesh_metrics(vertices, faces),
        "mesh_welded": mesh_metrics(welded_vertices, welded_faces),
        "outputs": {"step": str(args.output_step), "stl": str(args.stl) if args.stl else None},
        "tolerances": {
            "spline_fit_mm": args.fit_tolerance_mm,
            "mesh_chord_mm": args.mesh_tolerance_mm,
            "mesh_angular_rad": args.angular_tolerance_rad,
        },
    }
    if args.report:
        write_json(args.report, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if solid.isValid() else 1


if __name__ == "__main__":
    raise SystemExit(main())
