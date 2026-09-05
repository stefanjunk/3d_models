"""Blender helper invoked by generate_mesh_variants.py."""

from __future__ import annotations

import sys

import bpy


argv = sys.argv[sys.argv.index("--") + 1 :]
source, output, target_faces = argv[0], argv[1], int(argv[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.wm.stl_import(filepath=source)
except Exception:
    bpy.ops.import_mesh.stl(filepath=source)
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj
current_faces = len(obj.data.polygons)
if target_faces >= current_faces:
    raise RuntimeError("target must be below source face count")
modifier = obj.modifiers.new("Manufacturing mesh decimation", "DECIMATE")
modifier.decimate_type = "COLLAPSE"
modifier.ratio = target_faces / current_faces
modifier.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier=modifier.name)
try:
    bpy.ops.wm.stl_export(
        filepath=output, export_selected_objects=True, apply_modifiers=True
    )
except Exception:
    bpy.ops.export_mesh.stl(filepath=output, use_selection=True)
print(f"faces {current_faces} -> {len(obj.data.polygons)}")
