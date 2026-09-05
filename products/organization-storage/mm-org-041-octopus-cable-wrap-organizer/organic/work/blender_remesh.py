import bpy, sys, json
argv = sys.argv[sys.argv.index("--")+1:]
src, dst, voxel = argv[0], argv[1], float(argv[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
try:    bpy.ops.wm.stl_import(filepath=src)
except Exception: bpy.ops.import_mesh.stl(filepath=src)
ob = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = ob
print(f"IN faces={len(ob.data.polygons)} verts={len(ob.data.vertices)}")
mod = ob.modifiers.new("Remesh", 'REMESH')
mod.mode = 'VOXEL'; mod.voxel_size = voxel; mod.adaptivity = 0.0
mod.use_smooth_shade = False
bpy.ops.object.modifier_apply(modifier=mod.name)
print(f"OUT faces={len(ob.data.polygons)} verts={len(ob.data.vertices)}")
try:    bpy.ops.wm.stl_export(filepath=dst, export_selected_objects=False, apply_modifiers=True)
except Exception: bpy.ops.export_mesh.stl(filepath=dst)
print("EXPORTED", dst)
