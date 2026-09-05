"""Render nominal bought-part visibility in the unchanged generated R3 scene.

Geometry/placement diagnostic only: cylinder vial is not supplier CAD, reed
stands on a provisional datum without a designed holder. No wet-use approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", type=Path, required=True)
    ap.add_argument("--params", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--reed-length", type=float, required=True)
    ap.add_argument("--views", default="hero,back")
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
    p = json.loads(args.params.read_text())["purchased_reference"]
    if not 0 < args.reed_length <= p["wick_length_mm"]:
        raise ValueError("Only nominal or explicitly shortened reed is supported")
    args.out.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.open_mainfile(filepath=str(args.scene.resolve()))
    refs = next(c for c in bpy.data.collections if c.name.startswith("REFERENCE ONLY"))
    reed = next(o for o in refs.objects if o.name.startswith("White fibre"))
    vial = next(o for o in refs.objects if o.name.startswith("Vial"))
    reed.dimensions = (p["wick_diameter_mm"] / 1000,) * 2 + (args.reed_length / 1000,)
    reed.location = (0, 0, (5 + args.reed_length / 2) / 1000)
    vial.dimensions = (p["vial_diameter_mm"] / 1000,) * 2 + (p["vial_height_mm"] / 1000,)
    vial.location = (0, 0, (4 + p["vial_height_mm"] / 2) / 1000)
    bpy.context.view_layer.update()
    for ob, color, roughness in [(reed, (0.82, 0.80, 0.75, 1), 0.8),
                                  (vial, (0.6, 0.65, 0.62, 1), 0.22)]:
        ob.hide_set(False)
        ob.hide_render = False
        mat = bpy.data.materials.new(ob.name + " nominal diagnostic material")
        mat.use_nodes = True
        node = mat.node_tree.nodes.get("Principled BSDF")
        node.inputs["Base Color"].default_value = color
        node.inputs["Roughness"].default_value = roughness
        ob.data.materials.clear()
        ob.data.materials.append(mat)
        # Export the exact displayed proxies in mm for the shared checker.
        ob.data.calc_loop_triangles()
        with (args.out / ("nominal-reed-mm.obj" if ob == reed else "nominal-vial-mm.obj")).open("w") as f:
            f.write("# nominal purchased envelope, NOT FOR PRINT\n")
            for v in ob.data.vertices:
                f.write("v %.7f %.7f %.7f\n" % tuple((ob.matrix_world @ v.co) * 1000))
            for t in ob.data.loop_triangles:
                f.write("f %d %d %d\n" % tuple(i + 1 for i in t.vertices))
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    camera = scene.camera
    scene.cycles.samples = 24
    views = {
        "hero": ((0.16, -0.60, 0.29), (0, 0, 0.123)),
        "back": ((-0.16, 0.60, 0.29), (0, 0, 0.123)),
        "side": ((0.65, 0, 0.15), (0, 0, 0.123)),
    }
    for view in args.views.split(","):
        camera.location, target = views[view]
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(args.out.resolve() / ("assembly-" + view + ".png"))
        bpy.ops.render.render(write_still=True)
    report = {
        "schema_version": "1.0", "status": "REVIEW_REQUIRED",
        "purpose": "nominal bought-part visibility; not a completed assembly",
        "inputs": [{"path": str(x.resolve()), "sha256": digest(x)}
                   for x in [Path(__file__), args.scene, args.params]],
        "vial": {"diameter_mm": p["vial_diameter_mm"], "height_mm": p["vial_height_mm"], "base_z_mm": 4},
        "reed": {"diameter_mm": p["wick_diameter_mm"], "purchased_length_mm": p["wick_length_mm"],
                 "shown_length_mm": args.reed_length, "base_z_mm": 5,
                 "trim_mm": p["wick_length_mm"] - args.reed_length},
        "limitations": ["Nominal cylindrical vial envelope, no neck/cap detail.",
                        "No holder or retention; provisional axial placement.",
                        "No certified self-intersection, fit, stability or diffusion evidence."]}
    (args.out / "assembly-report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
