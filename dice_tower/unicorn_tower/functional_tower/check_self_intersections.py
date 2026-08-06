#!/usr/bin/env python3
"""Blender BVH self-overlap indicator for the final STL."""
import json
from pathlib import Path

import bmesh
import bpy
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
source = ROOT / "exports" / "functional_unicorn_dice_tower.stl"
report_path = ROOT / "reports" / "functional_unicorn_dice_tower.self_intersection.json"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=str(source))
obj = bpy.context.selected_objects[0]
mesh = obj.data
bm = bmesh.new()
bm.from_mesh(mesh)
original_vertices = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
bmesh.ops.triangulate(bm, faces=list(bm.faces))
bm.to_mesh(mesh)
bm.free()
mesh.update()
mesh.calc_loop_triangles()
vertices = [tuple(v.co) for v in mesh.vertices]
triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=1e-7)
pairs = tree.overlap(tree)
nonadjacent = []
for a, b in pairs:
    if a >= b:
        continue
    if set(triangles[a]).intersection(triangles[b]):
        continue
    nonadjacent.append((int(a), int(b)))
report = {
    "mesh": str(source),
    "method": "Blender 4.3 BVHTree self-overlap indicator after 1e-5 mm vertex welding; triangle pairs sharing any vertex are excluded as normal adjacency.",
    "original_import_vertices": original_vertices,
    "welded_vertices": len(vertices),
    "triangles": len(triangles),
    "raw_bvh_pairs": len(pairs),
    "nonadjacent_overlap_pairs": len(nonadjacent),
    "first_nonadjacent_pairs": nonadjacent[:20],
    "scope": "Indicator for nonadjacent triangle overlaps; complements, but does not replace, OpenSCAD Simple and watertight/manifold checks.",
    "passed": len(nonadjacent) == 0,
}
report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] else 2)
