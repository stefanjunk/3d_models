"""Run with: blender --background --python blender_boolean_job.py -- source.stl cutter.stl result.stl"""
from __future__ import annotations

import sys
from pathlib import Path

import bpy


def args_after_double_dash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_stl(path: str, name: str):
    before = set(bpy.data.objects)
    # Blender 4.x/5.x operator. Older versions may require bpy.ops.import_mesh.stl.
    bpy.ops.wm.stl_import(filepath=str(Path(path).resolve()))
    created = list(set(bpy.data.objects) - before)
    if len(created) != 1:
        raise RuntimeError(f"Expected one imported object from {path}, got {len(created)}")
    obj = created[0]
    obj.name = name
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.select_set(False)
    return obj


def main() -> None:
    argv = args_after_double_dash()
    if len(argv) != 3:
        raise SystemExit("Expected source.stl cutter.stl result.stl")
    source_path, cutter_path, output_path = argv
    clear_scene()
    source = import_stl(source_path, "SOURCE_WORKING")
    cutter = import_stl(cutter_path, "CUTTER")
    modifier = source.modifiers.new(name="FUNCTIONAL_DIFFERENCE", type="BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = source
    source.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    cutter.hide_render = True
    cutter.hide_set(True)
    bpy.ops.object.select_all(action="DESELECT")
    source.select_set(True)
    bpy.context.view_layer.objects.active = source
    bpy.ops.wm.stl_export(filepath=str(Path(output_path).resolve()), export_selected_objects=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(output_path).with_suffix(".blend").resolve()))


if __name__ == "__main__":
    main()
