#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from surface_geometry import ffd_deform_vertices, mesh_metrics, read_obj, write_json, write_obj


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply regular Bernstein-lattice FFD to an OBJ mesh.")
    parser.add_argument("input_obj", type=Path)
    parser.add_argument("config_json", type=Path)
    parser.add_argument("output_obj", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    vertices, faces = read_obj(args.input_obj)
    config = json.loads(args.config_json.read_text(encoding="utf-8"))
    deformed, deformation_report = ffd_deform_vertices(vertices, config)
    write_obj(args.output_obj, deformed, faces, object_name="ffd_variant")
    report = {
        "input": str(args.input_obj),
        "config": str(args.config_json),
        "output": str(args.output_obj),
        "deformation": deformation_report,
        "mesh_before": mesh_metrics(vertices, faces),
        "mesh_after": mesh_metrics(deformed, faces),
    }
    if args.report:
        write_json(args.report, report)
    print(f"Wrote {args.output_obj}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
