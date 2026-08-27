#!/usr/bin/env python3
"""Isolated deterministic validation for one five-model implementation group."""

from __future__ import annotations

import argparse
import importlib
import json
import tempfile
from pathlib import Path

import cadquery as cq
import trimesh
from cadquery import exporters


ROOT = Path(__file__).resolve().parent
GROUPS = {
    "a": ("systemmoebel_top20.models.group_a", set(range(1, 6))),
    "b": ("systemmoebel_top20.models.group_b", set(range(6, 11))),
    "c": ("systemmoebel_top20.models.group_c", set(range(11, 16))),
    "d": ("systemmoebel_top20.models.group_d", set(range(16, 21))),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("group", choices=GROUPS)
    args = parser.parse_args()

    module_name, expected = GROUPS[args.group]
    module = importlib.import_module(module_name)
    config = json.loads((ROOT / "config" / "defaults.json").read_text(encoding="utf-8"))
    envelope = tuple(float(value) for value in config["project"]["target_build_volume"])
    specs = module.build(config)
    actual = {spec.index for spec in specs}
    if actual != expected or len(specs) != 5:
        raise AssertionError(f"Expected {sorted(expected)}, got {sorted(actual)}")

    with tempfile.TemporaryDirectory(prefix=f"systemmoebel-group-{args.group}-", dir="/tmp/opencode") as tmp:
        tmp_path = Path(tmp)
        for spec in specs:
            shape = spec.solid.val()
            bb = shape.BoundingBox()
            placed = shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))
            path = tmp_path / f"{spec.filename}.stl"
            exporters.export(
                cq.Workplane("XY").newObject([placed]),
                str(path),
                tolerance=0.1,
                angularTolerance=0.15,
            )
            mesh = trimesh.load_mesh(path, force="mesh", process=True)
            components = mesh.split(only_watertight=False)
            bounds = tuple(float(value) for value in mesh.extents)
            passed = (
                mesh.is_watertight
                and mesh.is_winding_consistent
                and mesh.is_volume
                and len(components) == 1
                and all(size <= limit + 0.01 for size, limit in zip(bounds, envelope))
            )
            if not passed:
                raise AssertionError(
                    f"{spec.filename}: watertight={mesh.is_watertight}, "
                    f"winding={mesh.is_winding_consistent}, volume={mesh.is_volume}, "
                    f"components={len(components)}, bounds={bounds}, "
                    f"declared_wall={spec.minimum_wall_mm}, support_intent={spec.support_required}"
                )
            print(f"PASS {spec.filename}: {tuple(round(v, 2) for v in bounds)} mm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
