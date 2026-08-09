#!/usr/bin/env python3
"""Apply an image displacement to a UV-mapped Blender mesh and export STL.

Run:
  blender object.blend --background --python displace_heightmap.py -- \
    --image heightmap.png --output result.stl --mode engrave \
    --depth-mm 0.6 --subdivision-levels 3
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import bpy

def arguments():
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser()
    p.add_argument("--image",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--object")
    p.add_argument("--mode",choices=("emboss","engrave","centered"),default="emboss")
    p.add_argument("--depth-mm",type=float,default=0.6)
    p.add_argument("--subdivision-levels",type=int,default=2)
    p.add_argument("--vertex-group")
    p.add_argument("--apply",action="store_true",default=True)
    return p.parse_args(argv)

def active_mesh(name):
    obj=bpy.data.objects.get(name) if name else bpy.context.active_object
    if obj is None or obj.type!="MESH":
        raise RuntimeError("Select a mesh object or pass --object")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True); bpy.context.view_layer.objects.active=obj
    if not obj.data.uv_layers:
        raise RuntimeError("The target mesh has no UV map")
    return obj

def apply_modifier(obj,modifier):
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)

def export_stl(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        bpy.ops.wm.stl_export(filepath=str(path),export_selected_objects=True)
    except (AttributeError,TypeError,RuntimeError):
        bpy.ops.export_mesh.stl(filepath=str(path),use_selection=True)

def main():
    args=arguments()
    if args.depth_mm<=0: raise ValueError("--depth-mm must be positive")
    obj=active_mesh(args.object)

    if args.subdivision_levels>0:
        sub=obj.modifiers.new("Heightmap_Simple_Subdivision","SUBSURF")
        sub.subdivision_type="SIMPLE"
        sub.levels=args.subdivision_levels
        sub.render_levels=args.subdivision_levels
        apply_modifier(obj,sub)

    image=bpy.data.images.load(str(args.image.resolve()),check_existing=True)
    image.colorspace_settings.name="Non-Color"
    texture=bpy.data.textures.new("Heightmap_Texture",type="IMAGE")
    texture.image=image

    disp=obj.modifiers.new("Heightmap_Displace","DISPLACE")
    disp.texture=texture
    disp.texture_coords="UV"
    disp.direction="NORMAL"
    if args.mode=="emboss":
        disp.strength=args.depth_mm; disp.mid_level=0.0
    elif args.mode=="engrave":
        disp.strength=-args.depth_mm; disp.mid_level=0.0
    else:
        disp.strength=args.depth_mm; disp.mid_level=0.5
    if args.vertex_group:
        if args.vertex_group not in obj.vertex_groups:
            raise RuntimeError("Vertex group not found: "+args.vertex_group)
        disp.vertex_group=args.vertex_group
    apply_modifier(obj,disp)
    export_stl(args.output.resolve())

if __name__=="__main__":
    main()
