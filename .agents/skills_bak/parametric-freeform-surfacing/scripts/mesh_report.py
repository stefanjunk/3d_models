#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from surface_geometry import mesh_metrics, read_obj, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Report deterministic edge-incidence and volume metrics for an OBJ mesh.")
    parser.add_argument("input_obj", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    vertices, faces = read_obj(args.input_obj)
    report = {"input": str(args.input_obj), "mesh": mesh_metrics(vertices, faces)}
    if args.report:
        write_json(args.report, report)
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
