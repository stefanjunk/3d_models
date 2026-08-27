"""
Blender 4.x: robust two-part rigid negative mould generator.

Changes compared with the first version:
- preserves world transforms before joining GLB meshes;
- prints diagnostics for every imported mesh;
- removes tiny disconnected mesh islands that can corrupt the bounding box;
- creates ONE complete mould first, then cuts it into left/right halves;
- uses one consistent coordinate convention: 1 Blender unit = 1 mm;
- keeps temporary objects in a dedicated collection and deletes them afterwards.

Run in a NEW Blender file. The current scene is deleted.
"""

import bpy
import bmesh
import math
import os
from collections import deque
from mathutils import Vector

# -----------------------------------------------------------------------------
# USER SETTINGS
# -----------------------------------------------------------------------------

INPUT_FILE = "/home/stefan/Projekte/3d_models/roman_pillar/white_mesh.stl"
OUTPUT_DIR = "/home/stefan/Projekte/3d_models/roman_pillar/output"

# STL is normally interpreted as millimetres. GLB/glTF is normally metres, but
# this script rescales the final imported geometry to this exact height anyway.
TARGET_HEIGHT_MM = 300.0
MODEL_ROTATION_DEG = (90.0, 0.0, 0.0)

# Optional: use only one named mesh from a GLB. Leave empty to combine all meshes.
SOURCE_OBJECT_NAME = ""

# Remove tiny disconnected components such as stray triangles far from the model.
# Components are preserved when they contain at least BOTH thresholds below.
REMOVE_TINY_ISLANDS = True
MIN_ISLAND_FACES = 30
MIN_ISLAND_FACE_RATIO = 0.001  # 0.1% of the largest connected component

# Mould geometry.
WALL_MM = 15.0
BOTTOM_MM = 15.0
TOP_MM = 20.0
SPLIT_OFFSET_X_MM = 0.0

# Start with 0.0 if the source mesh is delicate or non-manifold.
# 0.15-0.30 mm may help release a rigid printed mould.
CAVITY_CLEARANCE_MM = 0.15

ADD_POUR_FUNNEL = True
POUR_BOTTOM_RADIUS_MM = 5.0
POUR_TOP_RADIUS_MM = 12.0
POUR_DEPTH_INTO_MODEL_MM = 8.0

ADD_ALIGNMENT_PINS = True
PIN_RADIUS_MM = 4.0
PIN_LENGTH_MM = 8.0
PIN_CLEARANCE_MM = 0.30
PIN_ANCHOR_MM = 2.0
PIN_SOCKET_EXTRA_DEPTH_MM = 1.0
PIN_Z_FRACTIONS = (0.25, 0.68)

EXPORT_STL = True
SAVE_BLEND = True
KEEP_SOURCE_MODEL_IN_BLEND = True

# -----------------------------------------------------------------------------
# BASIC HELPERS
# -----------------------------------------------------------------------------


def deselect_all():
    bpy.ops.object.select_all(action="DESELECT")


def activate(obj):
    deselect_all()
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj, location=False, rotation=False, scale=False):
    activate(obj)
    bpy.ops.object.transform_apply(
        location=location,
        rotation=rotation,
        scale=scale,
    )


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def world_bbox(obj):
    pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector((
        min(p.x for p in pts),
        min(p.y for p in pts),
        min(p.z for p in pts),
    ))
    maximum = Vector((
        max(p.x for p in pts),
        max(p.y for p in pts),
        max(p.z for p in pts),
    ))
    return minimum, maximum


def bbox_dims(obj):
    lo, hi = world_bbox(obj)
    return hi - lo


def duplicate_mesh(obj, name):
    dup = obj.copy()
    dup.data = obj.data.copy()
    dup.name = name
    bpy.context.collection.objects.link(dup)
    return dup


def remove_object(obj):
    if obj is not None and obj.name in bpy.context.scene.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def add_box(name, minimum, maximum):
    size = maximum - minimum
    if min(size) <= 0:
        raise ValueError(f"Invalid dimensions for {name}: {tuple(size)}")

    centre = (minimum + maximum) * 0.5
    bpy.ops.mesh.primitive_cube_add(location=centre)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    apply_transform(obj, scale=True)
    return obj


def add_cylinder_x(name, radius, x_start, x_end, y, z, vertices=48):
    depth = x_end - x_start
    if depth <= 0:
        raise ValueError("Cylinder depth must be positive")

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=((x_start + x_end) * 0.5, y, z),
        rotation=(0.0, math.radians(90.0), 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    apply_transform(obj, rotation=True, scale=True)
    return obj


def add_vertical_funnel(name, z_bottom, z_top, bottom_radius, top_radius):
    depth = z_top - z_bottom
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=bottom_radius,
        radius2=top_radius,
        depth=depth,
        location=(0.0, 0.0, (z_bottom + z_top) * 0.5),
    )
    obj = bpy.context.object
    obj.name = name
    apply_transform(obj, scale=True)
    return obj


def boolean_apply(target, cutter, operation, label):
    activate(target)
    cutter.hide_set(False)
    modifier = target.modifiers.new(name=label, type="BOOLEAN")
    modifier.operation = operation
    modifier.object = cutter
    modifier.solver = "EXACT"

    # Available in current Blender versions and useful for imperfect scan meshes.
    if hasattr(modifier, "use_self"):
        modifier.use_self = True

    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except Exception as exc:
        raise RuntimeError(
            f"Boolean '{label}' failed. The source is probably open, "
            f"self-intersecting, or contains invalid geometry."
        ) from exc


def export_stl(obj, filepath):
    activate(obj)
    try:
        bpy.ops.wm.stl_export(
            filepath=filepath,
            export_selected_objects=True,
            apply_modifiers=True,
        )
    except Exception:
        bpy.ops.export_mesh.stl(
            filepath=filepath,
            use_selection=True,
            use_mesh_modifiers=True,
        )


# -----------------------------------------------------------------------------
# IMPORT AND CLEANUP
# -----------------------------------------------------------------------------


def import_input(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Input file not found: {path}")

    before = set(bpy.context.scene.objects)
    ext = os.path.splitext(path)[1].lower()

    if ext in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".stl":
        try:
            bpy.ops.wm.stl_import(filepath=path)
        except Exception:
            bpy.ops.import_mesh.stl(filepath=path)
    else:
        raise ValueError("Supported formats: STL, GLB and glTF")

    imported = [o for o in bpy.context.scene.objects if o not in before]
    meshes = [o for o in imported if o.type == "MESH"]

    if not meshes:
        raise RuntimeError("Import succeeded, but no mesh object was found")

    print("\n--- Imported mesh diagnostics ---")
    for obj in meshes:
        dims = bbox_dims(obj)
        lo, hi = world_bbox(obj)
        centre = (lo + hi) * 0.5
        print(
            f"{obj.name!r}: faces={len(obj.data.polygons)}, "
            f"dims={tuple(round(v, 6) for v in dims)}, "
            f"centre={tuple(round(v, 6) for v in centre)}"
        )

    if SOURCE_OBJECT_NAME:
        matches = [o for o in meshes if o.name == SOURCE_OBJECT_NAME]
        if not matches:
            names = ", ".join(repr(o.name) for o in meshes)
            raise RuntimeError(
                f"SOURCE_OBJECT_NAME={SOURCE_OBJECT_NAME!r} not found. "
                f"Available: {names}"
            )
        meshes = matches

    # Preserve every object's visual/world transform before clearing parent links.
    for obj in meshes:
        world = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = world
        apply_transform(obj, location=True, rotation=True, scale=True)

    # Delete non-mesh imported objects.
    for obj in imported:
        if obj.type != "MESH":
            remove_object(obj)

    # Join selected meshes.
    deselect_all()
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    model = bpy.context.view_layer.objects.active
    model.name = "SOURCE_MODEL"

    return model


def clean_mesh(obj, merge_distance=0.01):
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    if bm.verts:
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=merge_distance)
    if bm.faces:
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def remove_tiny_face_islands(obj):
    """Delete small disconnected face components, typically scan/import debris."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    unseen = set(bm.faces)
    components = []

    while unseen:
        seed = unseen.pop()
        queue = deque([seed])
        component = {seed}

        while queue:
            face = queue.popleft()
            neighbours = set()
            for edge in face.edges:
                neighbours.update(edge.link_faces)
            for neighbour in neighbours:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    component.add(neighbour)
                    queue.append(neighbour)

        components.append(component)

    if not components:
        bm.free()
        return

    largest = max(len(c) for c in components)
    threshold = max(MIN_ISLAND_FACES, math.ceil(largest * MIN_ISLAND_FACE_RATIO))
    to_delete = [face for comp in components if len(comp) < threshold for face in comp]

    print(
        f"Connected components: {len(components)}; largest={largest} faces; "
        f"deleting {len(to_delete)} faces below threshold {threshold}."
    )

    if to_delete:
        bmesh.ops.delete(bm, geom=to_delete, context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")

    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def expand_mesh_along_normals(obj, amount):
    if amount <= 0:
        return

    activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.transform.shrink_fatten(value=amount, use_even_offset=True)
    except TypeError:
        bpy.ops.transform.shrink_fatten(value=amount)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.data.update()


# -----------------------------------------------------------------------------
# MAIN BUILD
# -----------------------------------------------------------------------------


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    clear_scene()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001  # one Blender unit is displayed as 1 mm

    model = import_input(INPUT_FILE)

    model.rotation_euler = tuple(math.radians(v) for v in MODEL_ROTATION_DEG)
    apply_transform(model, rotation=True)
    clean_mesh(model)

    if REMOVE_TINY_ISLANDS:
        remove_tiny_face_islands(model)
        clean_mesh(model)

    before_dims = bbox_dims(model)
    print(f"Combined dimensions before scaling: {tuple(round(v, 6) for v in before_dims)}")

    if before_dims.z <= 1e-9:
        raise RuntimeError("Model height is zero. Check MODEL_ROTATION_DEG")

    scale_factor = TARGET_HEIGHT_MM / before_dims.z
    model.scale = (scale_factor,) * 3
    apply_transform(model, scale=True)

    # Centre in X/Y and put the lowest point at Z=0.
    lo, hi = world_bbox(model)
    model.location += Vector((
        -(lo.x + hi.x) * 0.5,
        -(lo.y + hi.y) * 0.5,
        -lo.z,
    ))
    apply_transform(model, location=True)

    final_dims = bbox_dims(model)
    print(f"Final source dimensions: {tuple(round(v, 3) for v in final_dims)} mm")

    # Sanity check for outliers: a column should not be hundreds of times wider
    # than its height. This catches most corrupted bounding boxes early.
    if max(final_dims.x, final_dims.y) > TARGET_HEIGHT_MM * 5:
        raise RuntimeError(
            "The source bounding box is suspiciously wide. The file probably "
            "contains distant mesh debris. Set SOURCE_OBJECT_NAME or increase "
            "the island cleanup threshold."
        )

    cutter = duplicate_mesh(model, "CAVITY_CUTTER")
    expand_mesh_along_normals(cutter, CAVITY_CLEARANCE_MM)
    clean_mesh(cutter)

    cavity_min, cavity_max = world_bbox(cutter)
    split_x = SPLIT_OFFSET_X_MM

    outer_min = Vector((
        cavity_min.x - WALL_MM,
        cavity_min.y - WALL_MM,
        cavity_min.z - BOTTOM_MM,
    ))
    outer_max = Vector((
        cavity_max.x + WALL_MM,
        cavity_max.y + WALL_MM,
        cavity_max.z + TOP_MM,
    ))

    if not (outer_min.x < split_x < outer_max.x):
        raise RuntimeError("SPLIT_OFFSET_X_MM lies outside the mould")

    # Build a single complete mould first. This is more stable than subtracting
    # the same complex cutter from two separate half-blocks.
    full = add_box("MOLD_FULL", outer_min, outer_max)
    boolean_apply(full, cutter, "DIFFERENCE", "Subtract cavity")

    if ADD_POUR_FUNNEL:
        funnel = add_vertical_funnel(
            "POUR_FUNNEL_CUTTER",
            z_bottom=cavity_max.z - POUR_DEPTH_INTO_MODEL_MM,
            z_top=outer_max.z + 1.0,
            bottom_radius=POUR_BOTTOM_RADIUS_MM,
            top_radius=POUR_TOP_RADIUS_MM,
        )
        boolean_apply(full, funnel, "DIFFERENCE", "Cut pour funnel")
        remove_object(funnel)

    # Duplicate the finished complete mould and intersect each copy with a
    # half-space box. A small overlap prevents numerical gaps at the split plane.
    eps = 0.01
    left = duplicate_mesh(full, "MOLD_LEFT")
    right = duplicate_mesh(full, "MOLD_RIGHT")

    left_clip = add_box(
        "LEFT_CLIP",
        outer_min - Vector((1.0, 1.0, 1.0)),
        Vector((split_x + eps, outer_max.y + 1.0, outer_max.z + 1.0)),
    )
    right_clip = add_box(
        "RIGHT_CLIP",
        Vector((split_x - eps, outer_min.y - 1.0, outer_min.z - 1.0)),
        outer_max + Vector((1.0, 1.0, 1.0)),
    )

    boolean_apply(left, left_clip, "INTERSECT", "Create left half")
    boolean_apply(right, right_clip, "INTERSECT", "Create right half")
    remove_object(left_clip)
    remove_object(right_clip)
    remove_object(full)

    if ADD_ALIGNMENT_PINS:
        needed = 2.0 * (PIN_RADIUS_MM + PIN_CLEARANCE_MM)
        if WALL_MM < needed:
            raise RuntimeError(
                f"WALL_MM={WALL_MM} is too small for the selected pins; "
                f"use at least {needed:.1f} mm"
            )

        pin_y_positions = (
            cavity_min.y - WALL_MM * 0.5,
            cavity_max.y + WALL_MM * 0.5,
        )
        height = cavity_max.z - cavity_min.z
        pin_z_positions = [
            cavity_min.z + height * fraction for fraction in PIN_Z_FRACTIONS
        ]

        number = 0
        for z in pin_z_positions:
            for y in pin_y_positions:
                number += 1
                pin = add_cylinder_x(
                    f"PIN_{number}",
                    PIN_RADIUS_MM,
                    split_x - PIN_ANCHOR_MM,
                    split_x + PIN_LENGTH_MM,
                    y,
                    z,
                )
                boolean_apply(left, pin, "UNION", f"Add pin {number}")
                remove_object(pin)

                socket = add_cylinder_x(
                    f"SOCKET_{number}",
                    PIN_RADIUS_MM + PIN_CLEARANCE_MM,
                    split_x - 0.5,
                    split_x + PIN_LENGTH_MM + PIN_SOCKET_EXTRA_DEPTH_MM,
                    y,
                    z,
                )
                boolean_apply(right, socket, "DIFFERENCE", f"Cut socket {number}")
                remove_object(socket)

    left.color = (0.25, 0.50, 0.95, 1.0)
    right.color = (0.95, 0.45, 0.20, 1.0)

    cutter.hide_set(True)
    cutter.hide_render = True

    if KEEP_SOURCE_MODEL_IN_BLEND:
        model.hide_set(True)
        model.hide_render = True
    else:
        remove_object(model)

    if EXPORT_STL:
        left_path = os.path.join(OUTPUT_DIR, "roman_column_mold_left.stl")
        right_path = os.path.join(OUTPUT_DIR, "roman_column_mold_right.stl")
        export_stl(left, left_path)
        export_stl(right, right_path)
        print(f"Exported: {left_path}")
        print(f"Exported: {right_path}")

    if SAVE_BLEND:
        blend_path = os.path.join(OUTPUT_DIR, "roman_column_two_part_mold.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"Saved: {blend_path}")

    print("\n--- Result ---")
    print(f"Left half dimensions:  {tuple(round(v, 3) for v in bbox_dims(left))} mm")
    print(f"Right half dimensions: {tuple(round(v, 3) for v in bbox_dims(right))} mm")
    print("The two halves should touch at the X split plane; they are not moved apart.")


if __name__ == "__main__":
    main()
