import bpy, sys, math, mathutils
a=sys.argv[sys.argv.index("--")+1:]
src,out=a[0],a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
try: bpy.ops.wm.stl_import(filepath=src)
except Exception: bpy.ops.import_mesh.stl(filepath=src)
ob=bpy.context.selected_objects[0]
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=900; sc.render.resolution_y=700
sc.render.film_transparent=False
cam_data=bpy.data.cameras.new("C"); cam=bpy.data.objects.new("C",cam_data); sc.collection.objects.link(cam); sc.camera=cam
cam_data.type='ORTHO'; cam_data.ortho_scale=150
views={"iso":(60,0,45),"top":(0,0,0),"front":(90,0,0)}
for name,(rx,ry,rz) in views.items():
    d=260
    e=mathutils.Euler((math.radians(rx),math.radians(ry),math.radians(rz)),'XYZ')
    v=mathutils.Vector((0,0,d)); v.rotate(e)
    cam.location=v+mathutils.Vector((0,0,30)); cam.rotation_euler=e
    sc.render.filepath=out.replace(".png",f"-{name}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered",name)
