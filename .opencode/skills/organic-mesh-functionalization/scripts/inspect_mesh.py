#!/usr/bin/env python3
"""Inspect a triangle mesh and emit a reproducible JSON baseline report."""
from __future__ import annotations

import argparse
from pathlib import Path

from common import dump_json, load_mesh, mesh_metrics, sha256_file


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh")
    p.add_argument("--json-out")
    p.add_argument("--require-watertight", action="store_true")
    p.add_argument("--expected-bodies", type=int)
    p.add_argument("--bed", type=float, nargs=3, metavar=("X", "Y", "Z"))
    p.add_argument("--no-process", action="store_true", help="Load without Trimesh standard processing")
    args = p.parse_args()

    path = Path(args.mesh)
    mesh = load_mesh(path, process=not args.no_process)
    report = {
        "file": str(path.resolve()),
        "sha256": sha256_file(path),
        "load_processing": not args.no_process,
        **mesh_metrics(mesh),
    }
    checks = {
        "nonempty": report["vertices"] > 0 and report["faces"] > 0,
        "positive_extents": all(v > 0 for v in report["extents_mm"]),
        "watertight": report["watertight"] if args.require_watertight else True,
        "expected_bodies": report["body_count"] == args.expected_bodies if args.expected_bodies is not None else True,
        "bed_fit_axis_aligned": all(report["extents_mm"][i] <= args.bed[i] for i in range(3)) if args.bed else True,
    }
    report["checks"] = checks
    report["passed"] = all(checks.values())
    report["limitations"] = [
        "Self-intersection is not exhaustively tested.",
        "Minimum wall thickness is not inferred.",
        "Loading with processing can weld coincident vertices and orient faces; compare with --no-process when provenance matters.",
    ]
    print(dump_json(report, args.json_out))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
