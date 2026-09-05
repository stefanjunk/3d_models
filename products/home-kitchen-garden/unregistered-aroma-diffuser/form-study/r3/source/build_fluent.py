"""FLUENT: editable radial freeform study, not a manufacturing model.

Run in Blender 5.2:
  blender -b -t 12 --python source/build_fluent.py -- --out runs/001
Every output directory is new. Geometry is evaluated in mm; Blender/GLB use m.
The authoritative model is this script plus parameters.json, not an AI mesh.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.interpolate import CubicSpline


ROOT = Path(__file__).resolve().parent.parent


sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import envelope


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, content):
    path.write_text(json.dumps(content, indent=2) + "\n")


def run():
    import bpy
    import bmesh
    from mathutils import Vector

    ap = argparse.ArgumentParser()
    ap.add_argument("--params", type=Path, default=ROOT / "parameters.json")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--views", default="hero,back,side")
    ap.add_argument("--samples", type=int, default=40)
    ap.add_argument("--resolution", type=int, default=1000)
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    p = json.loads(args.params.read_text())
    for key, limits in p["allowed_ranges"].items():
        if not limits[0] <= p[key] <= limits[1]:
            raise ValueError(f"{key} outside declared form-study range")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"

    def material(name, color, roughness):
        m = bpy.data.materials.new(name)
        m.diffuse_color = (*color, 1)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = roughness
        return m

    ivory = material("Ivory | appearance target, not measured filament", (0.62, 0.54, 0.43), 0.43)
    ground = material("Warm neutral studio", (0.28, 0.24, 0.19), 0.75)
    vertices, faces = envelope(p)
    mesh = bpy.data.meshes.new("Cubic profiles + analytic 12-rib crown")
    mesh.from_pydata((vertices / 1000).tolist(), [], faces)
    mesh.update()
    shell = bpy.data.objects.new("FLUENT • parametric visual shell R3", mesh)
    scene.collection.objects.link(shell)
    shell.data.materials.append(ivory)
    for f in mesh.polygons:
        f.use_smooth = True
    shell["authority"] = "source/build_fluent.py + parameters.json"
    shell["use"] = "Form study only; no fit, wall, support or release approval"
    bevel = shell.modifiers.new("Temporary softened rim (not final tip design)", "BEVEL")
    bevel.width = 0.00055
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(48)
    bpy.context.view_layer.objects.active = shell
    shell.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)

    bpy.ops.mesh.primitive_cylinder_add(vertices=192, radius=p["foot_radius_mm"] / 1000,
                                      depth=p["foot_height_mm"] / 1000,
                                      location=(0, 0, p["foot_height_mm"] / 2000))
    foot = bpy.context.object
    foot.name = "Recessed foot • visual placeholder, no retention interface"
    foot.data.materials.append(ivory)
    b = foot.modifiers.new("Soft heel", "BEVEL")
    b.width, b.segments = 0.0007, 4
    for f in foot.data.polygons:
        f.use_smooth = True

    # Purchased references stay outside visual/manufacturing exports.
    refs = bpy.data.collections.new("REFERENCE ONLY • purchased parts • hidden")
    scene.collection.children.link(refs)
    for name, radius, depth, z in [
        ("Vial Ø50 × H64 mm", 25, 64, 36),
        ("White fibre reed Ø5 × 200 mm", 2.5, 200, 105),
    ]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius / 1000,
                                          depth=depth / 1000, location=(0, 0, z / 1000))
        ob = bpy.context.object
        ob.name = name
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        refs.objects.link(ob)
        ob.hide_render = True
        ob.hide_set(True)
        ob["status"] = "Nominal supplier reference; unmeasured; not a printed part"

    # Genuine model exports. Shell OBJ is mm; GLB is metres per format convention.
    shell.data.calc_loop_triangles()
    coords = [tuple(v.co * 1000) for v in shell.data.vertices]
    triangles = [tuple(t.vertices) for t in shell.data.loop_triangles]
    obj = out / "fluent-shell-visual-mm.obj"
    with obj.open("w") as f:
        f.write("# FLUENT R3, millimetres, VISUAL FORM STUDY — NOT FOR PRINT\n")
        for v in coords:
            f.write("v %.7f %.7f %.7f\n" % v)
        for face in triangles:
            f.write("f %d %d %d\n" % tuple(i + 1 for i in face))
    bm = bmesh.new()
    bm.from_mesh(shell.data)
    metrics = {
        "vertices": len(bm.verts), "faces_before_export_triangulation": len(bm.faces),
        "export_triangles": len(triangles),
        "boundary_edges": sum(e.is_boundary for e in bm.edges),
        "nonmanifold_edges": sum(not e.is_manifold for e in bm.edges),
        "degenerate_faces": sum(f.calc_area() < 1e-15 for f in bm.faces),
        "signed_volume_mm3": bm.calc_volume(signed=True) * 1e9,
        "bounds_mm": [np.min(coords, axis=0).tolist(), np.max(coords, axis=0).tolist()],
        "dimensions_mm": (np.max(coords, axis=0) - np.min(coords, axis=0)).tolist(),
    }
    bm.free()
    write_json(out / "parameters-used.json", p)
    write_json(out / "build-report.json", {
        "schema_version": "1.0", "tool": "FLUENT-parametric-generator",
        "status": "REVIEW_REQUIRED", "blender_version": bpy.app.version_string,
        "inputs": [{"path": str(x), "sha256": digest(x)} for x in [Path(__file__), Path(__file__).with_name("geometry.py"), args.params]],
        "outputs": [{"path": str(obj), "sha256": digest(obj)}],
        "metrics": metrics,
        "limitations": ["Appearance target, not exact reconstruction.",
                       "Mesh topology diagnostics do not certify self-intersection or wall thickness.",
                       "Radial shell value is not minimum normal wall thickness.",
                       "No holder, base retention, stability, slicer, scent or physical evidence."],
    })
    bpy.ops.object.select_all(action="DESELECT")
    shell.select_set(True)
    foot.select_set(True)
    bpy.context.view_layer.objects.active = shell
    bpy.ops.export_scene.gltf(filepath=str(out / "fluent-visual.glb"), export_format="GLB",
                              use_selection=True, export_apply=True)

    # Studio created entirely from current geometry, no imagegen overpaint.
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.0002))
    bpy.context.object.name = "Render studio floor"
    bpy.context.object.data.materials.append(ground)
    scene.world.color = (0.25, 0.25, 0.25)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.65, 0.75, 1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.20

    def aim(ob, point):
        ob.rotation_euler = (Vector(point) - ob.location).to_track_quat("-Z", "Y").to_euler()

    for name, loc, energy, size in [
        ("Large softbox left", (-0.30, -0.35, 0.42), 6, 0.22),
        ("Softbox right", (0.28, 0.10, 0.32), 4, 0.18),
        ("Quiet frontal fill", (0.0, -0.50, 0.15), 0.45, 0.35),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        ob = bpy.data.objects.new(name, data)
        scene.collection.objects.link(ob)
        ob.location = loc
        aim(ob, (0, 0, 0.12))
    camdata = bpy.data.cameras.new("Actual model studio camera")
    camera = bpy.data.objects.new("Actual model studio camera", camdata)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camdata.type, camdata.ortho_scale = "ORTHO", 0.298
    scene.render.engine = "CYCLES"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = int(args.resolution * 0.8)
    scene.render.resolution_y = args.resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    views = {
        "hero": ((0.16, -0.60, 0.29), (0, 0, 0.123)),
        "front": ((0, -0.65, 0.125), (0, 0, 0.125)),
        "back": ((-0.16, 0.60, 0.29), (0, 0, 0.123)),
        "side": ((0.65, 0, 0.15), (0, 0, 0.123)),
    }
    for view in ([] if args.views == "none" else args.views.split(",")):
        camera.location, target = views[view]
        aim(camera, target)
        scene.render.filepath = str(out / f"fluent-{view}.png")
        if view == "hero":
            bpy.ops.wm.save_as_mainfile(filepath=str(out / "fluent-parametric-study.blend"))
        bpy.ops.render.render(write_still=True)
    print("FLUENT_BUILD_REPORT", json.dumps(metrics))


if __name__ == "__main__":
    run()
