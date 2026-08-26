#!/usr/bin/env python3
"""Config-driven Blender mesh Boolean pipeline.

Run:
  blender --background --python blender_functionalize.py -- config.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy


def cli_config() -> Path:
    if "--" not in sys.argv:
        raise SystemExit("Expected config path after --")
    values = sys.argv[sys.argv.index("--") + 1:]
    if len(values) != 1:
        raise SystemExit("Usage: blender --background --python script.py -- config.json")
    return Path(values[0]).resolve()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_mesh(path: Path):
    ext = path.suffix.lower()
    before = set(bpy.data.objects)
    if ext == ".stl":
        try:
            bpy.ops.wm.stl_import(filepath=str(path))
        except Exception:
            bpy.ops.import_mesh.stl(filepath=str(path))
    elif ext == ".obj":
        try:
            bpy.ops.wm.obj_import(filepath=str(path))
        except Exception:
            bpy.ops.import_scene.obj(filepath=str(path))
    elif ext in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif ext == ".ply":
        try:
            bpy.ops.wm.ply_import(filepath=str(path))
        except Exception:
            bpy.ops.import_mesh.ply(filepath=str(path))
    else:
        raise ValueError(f"Unsupported input format: {ext}")
    created = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    if not created:
        raise RuntimeError(f"No mesh imported from {path}")
    if len(created) == 1:
        return created[0]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in created:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = created[0]
    bpy.ops.object.join()
    return bpy.context.object


def set_active(obj) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj) -> None:
    set_active(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def make_cutter(spec: dict, base: Path):
    kind = spec["type"].lower()
    location = spec.get("location", [0, 0, 0])
    rotation = [math.radians(float(v)) for v in spec.get("rotation_deg", [0, 0, 0])]
    if kind == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=int(spec.get("vertices", 96)),
            radius=float(spec["radius"]),
            depth=float(spec["depth"]),
            location=location,
            rotation=rotation,
        )
        obj = bpy.context.object
    elif kind == "box":
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
        obj = bpy.context.object
        obj.dimensions = tuple(map(float, spec["size"]))
        apply_transform(obj)
    elif kind == "sphere":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=int(spec.get("subdivisions", 4)),
            radius=float(spec["radius"]),
            location=location,
            rotation=rotation,
        )
        obj = bpy.context.object
    elif kind == "import":
        obj = import_mesh((base / spec["path"]).resolve())
        obj.location = location
        obj.rotation_euler = rotation
        apply_transform(obj)
    else:
        raise ValueError(f"Unsupported cutter type: {kind}")
    obj.name = spec.get("name", f"cutter-{kind}")
    return obj


def apply_decimate(obj, ratio: float) -> None:
    mod = obj.modifiers.new("working-decimate", "DECIMATE")
    mod.ratio = float(ratio)
    set_active(obj)
    bpy.ops.object.modifier_apply(modifier=mod.name)


def boolean_stage(target, cutter, operation: str, solver: str) -> None:
    mod = target.modifiers.new(name=f"bool-{operation.lower()}", type="BOOLEAN")
    mod.operation = operation.upper()
    mod.object = cutter
    try:
        mod.solver = solver.upper()
    except Exception:
        if solver.upper() != "EXACT":
            print(f"Warning: solver {solver} unavailable; using Blender default", file=sys.stderr)
    set_active(target)
    bpy.ops.object.modifier_apply(modifier=mod.name)


def export_mesh(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    set_active(obj)
    ext = path.suffix.lower()
    if ext == ".stl":
        try:
            bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True)
        except Exception:
            bpy.ops.export_mesh.stl(filepath=str(path), use_selection=True)
    elif ext in {".glb", ".gltf"}:
        bpy.ops.export_scene.gltf(filepath=str(path), use_selection=True)
    elif ext == ".ply":
        try:
            bpy.ops.wm.ply_export(filepath=str(path), export_selected_objects=True)
        except Exception:
            bpy.ops.export_mesh.ply(filepath=str(path), use_selection=True)
    else:
        raise ValueError(f"Unsupported output format: {ext}")


def main() -> int:
    cfg_path = cli_config()
    cfg = json.loads(cfg_path.read_text())
    base = cfg_path.parent
    clear_scene()
    target = import_mesh((base / cfg["input"]).resolve())
    target.name = cfg.get("target_object") or "organic-target"
    if cfg.get("apply_transform", True):
        apply_transform(target)
    if cfg.get("decimate_ratio") is not None:
        apply_decimate(target, float(cfg["decimate_ratio"]))

    for stage in cfg.get("operations", []):
        cutter_spec = dict(stage["cutter"])
        cutter_spec.setdefault("name", stage.get("name", "cutter"))
        cutter = make_cutter(cutter_spec, base)
        if cfg.get("apply_transform", True):
            apply_transform(cutter)
        boolean_stage(target, cutter, stage["operation"], stage.get("solver", "EXACT"))
        if not stage.get("keep_cutter", False):
            bpy.data.objects.remove(cutter, do_unlink=True)
        checkpoint = stage.get("checkpoint")
        if checkpoint:
            export_mesh(target, (base / checkpoint).resolve())

    if cfg.get("save_blend"):
        blend_path = (base / cfg["save_blend"]).resolve()
        blend_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    export_mesh(target, (base / cfg["output"]).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
