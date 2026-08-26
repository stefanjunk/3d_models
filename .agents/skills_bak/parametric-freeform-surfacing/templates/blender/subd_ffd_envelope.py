"""Blender template: evaluate a SubD master, apply a lattice modifier, export OBJ.

Run inside Blender, for example:

blender --background master.blend --python subd_ffd_envelope.py -- \
  --object Envelope --lattice EnvelopeCage --levels 2 --output variant.obj

This template does not generate the artistic cage.  It makes the evaluated
handoff deterministic, applies object transforms, verifies named objects, and
writes a small JSON report beside the OBJ.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def arguments() -> argparse.Namespace:
    raw = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--object", required=True)
    parser.add_argument("--lattice", required=True)
    parser.add_argument("--levels", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(raw)


def main() -> None:
    args = arguments()
    obj = bpy.data.objects.get(args.object)
    cage = bpy.data.objects.get(args.lattice)
    if obj is None or obj.type != "MESH":
        raise RuntimeError(f"Missing mesh object: {args.object}")
    if cage is None or cage.type != "LATTICE":
        raise RuntimeError(f"Missing lattice object: {args.lattice}")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    subdivision = obj.modifiers.get("PFS_Subdivision") or obj.modifiers.new("PFS_Subdivision", "SUBSURF")
    subdivision.subdivision_type = "CATMULL_CLARK"
    subdivision.levels = args.levels
    subdivision.render_levels = args.levels
    lattice = obj.modifiers.get("PFS_Lattice") or obj.modifiers.new("PFS_Lattice", "LATTICE")
    lattice.object = cage

    args.output.parent.mkdir(parents=True, exist_ok=True)
    for candidate in bpy.context.selected_objects:
        candidate.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(filepath=str(args.output), export_selected_objects=True, apply_modifiers=True, export_materials=False)
    report = {
        "status": "PASS",
        "object": obj.name,
        "lattice": cage.name,
        "subdivision_levels": args.levels,
        "output": str(args.output),
        "note": "Run independent hardpoint, topology, wall, and slicer validation after export.",
    }
    args.output.with_suffix(".report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
