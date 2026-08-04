"""
Blender 4.x: Viertelsymmetrie + Negativform fuer Gips
=====================================================

Vorbereitung in Blender:
1. Das importierte Fliesenmodell so ausrichten, dass seine Kanten entlang X/Y liegen.
2. Die flache Rueckseite soll unten liegen und das Relief nach +Z zeigen.
3. Das Modell als einziges aktives Objekt auswaehlen.
4. Dieses Skript im Scripting-Workspace oeffnen und mit "Run Script" ausfuehren.

Das Skript veraendert das Quellobjekt nicht. Es erzeugt:
- Tile_Symmetric: aus einem gewaehlten Viertel ueber X und Y gespiegelt
- Tile_Cutter: gedrehter Schneidkoerper fuer die Form
- Mold_Negative: massiver Block mit ausgeschnittener Negativform

Hinweis:
Tiefe Hinterschneidungen werden durch dieses Skript nicht entfernt. Eine starre
PLA/PETG-Form kann sich deshalb eventuell nicht entformen lassen. Fuer komplexe
Ornamente ist eine Silikonform meist sicherer.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# -----------------------------------------------------------------------------
# KONFIGURATION
# -----------------------------------------------------------------------------

# Mittelpunkt fuer die Spiegelung:
# "BOUNDS" = Mittelpunkt der lokalen Bounding Box (meist passend fuer Fliesen)
# "CURSOR" = X/Y des 3D-Cursors; Z bleibt der Bounding-Box-Mittelpunkt
CENTER_MODE = "BOUNDS"

# Welches Originalviertel soll erhalten und auf die anderen Seiten gespiegelt
# werden? Erlaubte Werte: "POSITIVE" oder "NEGATIVE".
KEEP_X_SIDE = "POSITIVE"
KEEP_Y_SIDE = "POSITIVE"

# Das Skript nimmt standardmaessig an, dass das Relief nach +Z zeigt und die
# flache Rueckseite bei -Z liegt. Dann wird der Cutter um 180 Grad gedreht,
# sodass die Form nach oben offen ist.
RELIEF_POINTS_TO_POSITIVE_Z = True

# Physische Abmessungen der Negativform in Millimetern.
SIDE_WALL_MM = 8.0
BOTTOM_MM = 6.0

# Der Cutter ragt geringfuegig aus der Oberseite des Blocks heraus. Dadurch
# entstehen keine exakt koplanaren Flaechen an der Eingussoeffnung.
OPENING_OVERLAP_MM = 0.5

# Schwellwert zum Verschmelzen der Spiegelnaht.
MIRROR_MERGE_MM = 0.02

# Boolean-Einstellungen.
APPLY_BOOLEAN = True
BOOLEAN_HOLE_TOLERANT = False
BOOLEAN_SELF_INTERSECTION = True

# Sichtbarkeit nach erfolgreichem Durchlauf.
HIDE_SOURCE_AFTER_RUN = True
HIDE_SYMMETRIC_AFTER_MOLD = True
HIDE_CUTTER_AFTER_RUN = True

GENERATED_COLLECTION_NAME = "Generated_Plaster_Mold"


# -----------------------------------------------------------------------------
# HILFSFUNKTIONEN
# -----------------------------------------------------------------------------

def mm_to_blender_units(value_mm: float) -> float:
    """Konvertiert Millimeter anhand von scene.unit_settings.scale_length."""
    scale_length = bpy.context.scene.unit_settings.scale_length
    if not scale_length or scale_length <= 0.0:
        scale_length = 1.0
    return (value_mm / 1000.0) / scale_length


def ensure_object_mode() -> None:
    obj = bpy.context.object
    if obj is not None and obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def activate_only(obj: bpy.types.Object) -> None:
    ensure_object_mode()
    for candidate in bpy.context.view_layer.objects:
        candidate.select_set(False)
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def get_or_create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def evaluated_mesh_copy(
    source: bpy.types.Object,
    name: str,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    """Erzeugt eine unabhaengige Mesh-Kopie mit ausgewertetem Modifier-Stack."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    source_eval = source.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        source_eval,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    obj = bpy.data.objects.new(name, mesh)
    obj.matrix_world = source.matrix_world.copy()
    collection.objects.link(obj)
    return obj


def ordinary_mesh_copy(
    source: bpy.types.Object,
    name: str,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = name
    collection.objects.link(obj)
    return obj


def apply_rotation_and_scale(obj: bpy.types.Object) -> None:
    activate_only(obj)
    result = bpy.ops.object.transform_apply(
        location=False,
        rotation=True,
        scale=True,
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"Rotation/Scale konnten bei {obj.name} nicht angewendet werden.")


def apply_modifier(obj: bpy.types.Object, modifier_name: str) -> None:
    activate_only(obj)
    result = bpy.ops.object.modifier_apply(modifier=modifier_name)
    if "FINISHED" not in result:
        raise RuntimeError(
            f"Modifier '{modifier_name}' konnte bei {obj.name} nicht angewendet werden."
        )


def local_bounds(obj: bpy.types.Object):
    points = [Vector(corner) for corner in obj.bound_box]
    minimum = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    maximum = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))
    return minimum, maximum


def world_bounds(obj: bpy.types.Object):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    maximum = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))
    return minimum, maximum


def move_origin_to_local_point(obj: bpy.types.Object, local_point: Vector) -> None:
    """Verschiebt den Ursprung, ohne die Weltposition der Geometrie zu aendern."""
    world_point = obj.matrix_world @ local_point
    obj.data.transform(Matrix.Translation(-local_point))
    obj.data.update()

    matrix = obj.matrix_world.copy()
    matrix.translation = world_point
    obj.matrix_world = matrix


def symmetry_center_local(obj: bpy.types.Object) -> Vector:
    minimum, maximum = local_bounds(obj)
    bounds_center = (minimum + maximum) * 0.5

    mode = CENTER_MODE.upper()
    if mode == "BOUNDS":
        return bounds_center
    if mode == "CURSOR":
        cursor_local = obj.matrix_world.inverted() @ bpy.context.scene.cursor.location
        return Vector((cursor_local.x, cursor_local.y, bounds_center.z))

    raise ValueError("CENTER_MODE muss 'BOUNDS' oder 'CURSOR' sein.")


def recalculate_and_weld(obj: bpy.types.Object, weld_distance: float) -> None:
    mesh = obj.data
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        if weld_distance > 0.0 and bm.verts:
            bmesh.ops.remove_doubles(
                bm,
                verts=list(bm.verts),
                dist=weld_distance,
            )
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        mesh.validate(verbose=False)
        mesh.update()
    finally:
        bm.free()


def non_manifold_edge_count(obj: bpy.types.Object) -> int:
    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        return sum(1 for edge in bm.edges if not edge.is_manifold)
    finally:
        bm.free()


def add_xy_mirror(obj: bpy.types.Object, merge_distance: float) -> None:
    keep_x = KEEP_X_SIDE.upper()
    keep_y = KEEP_Y_SIDE.upper()
    if keep_x not in {"POSITIVE", "NEGATIVE"}:
        raise ValueError("KEEP_X_SIDE muss 'POSITIVE' oder 'NEGATIVE' sein.")
    if keep_y not in {"POSITIVE", "NEGATIVE"}:
        raise ValueError("KEEP_Y_SIDE muss 'POSITIVE' oder 'NEGATIVE' sein.")

    modifier = obj.modifiers.new(name="Quarter_Symmetry_XY", type="MIRROR")

    modifier.use_axis[0] = True
    modifier.use_axis[1] = True
    modifier.use_axis[2] = False

    modifier.use_bisect_axis[0] = True
    modifier.use_bisect_axis[1] = True
    modifier.use_bisect_axis[2] = False

    # Ohne Flip behaelt der aktuelle Mirror Modifier die positive Seite.
    modifier.use_bisect_flip_axis[0] = keep_x == "NEGATIVE"
    modifier.use_bisect_flip_axis[1] = keep_y == "NEGATIVE"
    modifier.use_bisect_flip_axis[2] = False

    modifier.use_mirror_merge = True
    modifier.use_clip = True
    modifier.merge_threshold = merge_distance

    if hasattr(modifier, "bisect_threshold"):
        modifier.bisect_threshold = merge_distance

    apply_modifier(obj, modifier.name)


def create_axis_aligned_cube(
    name: str,
    minimum: Vector,
    maximum: Vector,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    size = maximum - minimum
    if min(size) <= 0.0:
        raise ValueError("Der Formblock haette eine ungueltige Groesse.")

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)

    half = size * 0.5
    vertices = [
        (-half.x, -half.y, -half.z),
        ( half.x, -half.y, -half.z),
        ( half.x,  half.y, -half.z),
        (-half.x,  half.y, -half.z),
        (-half.x, -half.y,  half.z),
        ( half.x, -half.y,  half.z),
        ( half.x,  half.y,  half.z),
        (-half.x,  half.y,  half.z),
    ]
    faces = [
        (0, 3, 2, 1),  # unten
        (4, 5, 6, 7),  # oben
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj.location = (minimum + maximum) * 0.5
    return obj


# -----------------------------------------------------------------------------
# HAUPTABLAUF
# -----------------------------------------------------------------------------

def main() -> None:
    ensure_object_mode()

    source = bpy.context.active_object
    if source is None or source.type != "MESH":
        raise RuntimeError("Bitte genau ein Mesh-Objekt als aktives Objekt auswaehlen.")

    generated_collection = get_or_create_collection(GENERATED_COLLECTION_NAME)

    wall = mm_to_blender_units(SIDE_WALL_MM)
    bottom = mm_to_blender_units(BOTTOM_MM)
    overlap = mm_to_blender_units(OPENING_OVERLAP_MM)
    merge = mm_to_blender_units(MIRROR_MERGE_MM)

    print("\n--- Viertelsymmetrie und Negativform ---")
    print(f"Quelle: {source.name}")
    print(f"Blender-Version: {bpy.app.version_string}")

    # 1. Arbeitskopie mit ausgewertetem Modifier-Stack erstellen.
    symmetric = evaluated_mesh_copy(source, "Tile_Symmetric", generated_collection)
    apply_rotation_and_scale(symmetric)

    # 2. Ursprung exakt auf den Spiegelmittelpunkt setzen.
    center_local = symmetry_center_local(symmetric)
    move_origin_to_local_point(symmetric, center_local)

    # 3. Aus dem gewaehlten Viertel eine X/Y-symmetrische Fliese erzeugen.
    add_xy_mirror(symmetric, merge)
    recalculate_and_weld(symmetric, merge)
    symmetric.name = "Tile_Symmetric"

    non_manifold = non_manifold_edge_count(symmetric)
    print(f"Nicht-manifold Kanten nach Spiegelung: {non_manifold}")
    if non_manifold:
        print(
            "WARNUNG: Das positive Modell ist nicht vollstaendig manifold. "
            "Der Boolean kann deshalb fehlschlagen oder Artefakte erzeugen."
        )

    # 4. Cutter kopieren und fuer eine nach oben offene Form ausrichten.
    cutter = ordinary_mesh_copy(symmetric, "Tile_Cutter", generated_collection)
    if RELIEF_POINTS_TO_POSITIVE_Z:
        cutter.rotation_euler.rotate_axis("X", math.pi)
        apply_rotation_and_scale(cutter)

    cutter.display_type = "WIRE"
    cutter.show_in_front = True
    cutter.hide_render = True

    cutter_min, cutter_max = world_bounds(cutter)

    # Die Oberseite des Blocks liegt knapp unterhalb der flachen Cutter-Rueckseite.
    # Dadurch ragt der Cutter um OPENING_OVERLAP_MM aus dem Block heraus.
    block_min = Vector((
        cutter_min.x - wall,
        cutter_min.y - wall,
        cutter_min.z - bottom,
    ))
    block_max = Vector((
        cutter_max.x + wall,
        cutter_max.y + wall,
        cutter_max.z - overlap,
    ))

    if block_max.z <= cutter_min.z:
        raise RuntimeError(
            "OPENING_OVERLAP_MM ist zu gross oder das Modell ist extrem flach."
        )

    # 5. Massiven Formblock erzeugen.
    mold = create_axis_aligned_cube(
        "Mold_Negative",
        block_min,
        block_max,
        generated_collection,
    )

    # 6. Positivvolumen aus dem Block ausschneiden.
    boolean = mold.modifiers.new(name="Cut_Tile_Cavity", type="BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = cutter

    if hasattr(boolean, "use_hole_tolerant"):
        boolean.use_hole_tolerant = BOOLEAN_HOLE_TOLERANT
    if hasattr(boolean, "use_self"):
        boolean.use_self = BOOLEAN_SELF_INTERSECTION

    if APPLY_BOOLEAN:
        print("Boolean wird angewendet. Bei sehr dichten Hunyuan-Meshes kann das dauern ...")
        apply_modifier(mold, boolean.name)
        recalculate_and_weld(mold, 0.0)

        mold_non_manifold = non_manifold_edge_count(mold)
        print(f"Nicht-manifold Kanten der Negativform: {mold_non_manifold}")
        if mold_non_manifold:
            print(
                "WARNUNG: Die Negativform ist nicht vollstaendig manifold. "
                "Vor dem STL-Export bitte mit der 3D Print Toolbox pruefen."
            )
    else:
        print("Boolean bleibt als nicht angewendeter Modifier erhalten.")

    # 7. Sichtbarkeit ordnen.
    source.hide_set(HIDE_SOURCE_AFTER_RUN)
    symmetric.hide_set(HIDE_SYMMETRIC_AFTER_MOLD)
    cutter.hide_set(HIDE_CUTTER_AFTER_RUN)
    mold.hide_set(False)
    activate_only(mold)

    print("--- Fertig ---")
    print(f"Symmetrisches Positiv: {symmetric.name}")
    print(f"Boolean-Cutter:        {cutter.name}")
    print(f"Negativform:           {mold.name}")
    print(
        "Pruefe die Form vor dem Druck auf Hinterschneidungen und "
        "nicht-manifold Geometrie."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nFEHLER:", error)
        raise
