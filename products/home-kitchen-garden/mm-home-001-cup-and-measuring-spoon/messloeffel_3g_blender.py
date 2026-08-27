# Kompakter Messlöffel für ungefähr 3 g Flohsamenschalen
# In Blender: Scripting > New > einfügen > Run Script
#
# Das Volumen ist auf 6 ml bis zum Rand eingestellt.
# Da Flohsamenschalen je nach Produkt unterschiedlich viel wiegen,
# sollte der erste Druck mit einer Küchenwaage geprüft werden.
#
# Maße in Millimetern.

import bpy
import math
from pathlib import Path

# ============================================================
# EINSTELLUNGEN
# ============================================================

TARGET_VOLUME_ML = 6.0
INNER_RADIUS = 10.0
WALL = 1.6
BOTTOM = 1.8

HANDLE_EXTENSION = 8.0
HANDLE_WIDTH = 8.0
HANDLE_THICKNESS = 3.4

CYLINDER_SEGMENTS = 128
EXPORT_DIRECTORY = ""

# ============================================================
# ABGELEITETE MASSE
# ============================================================

INNER_DEPTH = TARGET_VOLUME_ML * 1000.0 / (math.pi * INNER_RADIUS ** 2)
OUTER_RADIUS = INNER_RADIUS + WALL
TOTAL_HEIGHT = BOTTOM + INNER_DEPTH

# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def apply_modifier(obj, modifier):
    activate(obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)

def boolean_apply(target, cutter, operation):
    modifier = target.modifiers.new(name="Boolean_" + operation, type="BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = cutter
    apply_modifier(target, modifier)
    bpy.data.objects.remove(cutter, do_unlink=True)

def export_stl(obj, filepath):
    activate(obj)
    try:
        bpy.ops.wm.stl_export(
            filepath=str(filepath),
            export_selected_objects=True,
            ascii_format=False,
        )
        return
    except Exception:
        pass
    bpy.ops.export_mesh.stl(
        filepath=str(filepath),
        use_selection=True,
        ascii=False,
        global_scale=1.0,
    )

def export_directory():
    if EXPORT_DIRECTORY.strip():
        return Path(EXPORT_DIRECTORY).expanduser()
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop / "Messloeffel_3g_STL"
    return Path.home() / "Messloeffel_3g_STL"

# ============================================================
# SZENE LEEREN
# ============================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "MILLIMETERS"
scene.unit_settings.scale_length = 0.001

# ============================================================
# GRUNDKÖRPER
# ============================================================

bpy.ops.mesh.primitive_cylinder_add(
    vertices=CYLINDER_SEGMENTS,
    radius=OUTER_RADIUS,
    depth=TOTAL_HEIGHT,
    location=(0.0, 0.0, TOTAL_HEIGHT / 2.0),
)
spoon = bpy.context.object
spoon.name = "Messloeffel_3g_6ml"

bpy.ops.mesh.primitive_cylinder_add(
    vertices=CYLINDER_SEGMENTS,
    radius=INNER_RADIUS,
    depth=INNER_DEPTH + 1.0,
    location=(0.0, 0.0, BOTTOM + (INNER_DEPTH + 1.0) / 2.0),
)
cavity = bpy.context.object
boolean_apply(spoon, cavity, "DIFFERENCE")

# ============================================================
# KURZER GRIFF
# ============================================================

handle_start = OUTER_RADIUS - 1.0
handle_end = OUTER_RADIUS + HANDLE_EXTENSION
handle_length = handle_end - handle_start

bpy.ops.mesh.primitive_cube_add(
    location=(
        (handle_start + handle_end) / 2.0,
        0.0,
        HANDLE_THICKNESS / 2.0,
    )
)
handle = bpy.context.object
handle.name = "Kurzer_Griff"
handle.dimensions = (
    handle_length,
    HANDLE_WIDTH,
    HANDLE_THICKNESS,
)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

bevel = handle.modifiers.new(name="Griff_Abrundung", type="BEVEL")
bevel.width = 1.4
bevel.segments = 5
bevel.limit_method = "ANGLE"
apply_modifier(handle, bevel)

boolean_apply(spoon, handle, "UNION")

# Kleine Abrundung außen
bevel = spoon.modifiers.new(name="Kanten_Abrundung", type="BEVEL")
bevel.width = 0.25
bevel.segments = 3
bevel.limit_method = "ANGLE"
apply_modifier(spoon, bevel)

activate(spoon)
bpy.ops.object.shade_smooth_by_angle()

# ============================================================
# EXPORT
# ============================================================

folder = export_directory()
folder.mkdir(parents=True, exist_ok=True)

stl_path = folder / "messloeffel_3g_6ml.stl"
export_stl(spoon, stl_path)

blend_path = folder / "messloeffel_3g_6ml.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

print("")
print("Messlöffel fertig.")
print("Nominales Volumen: %.2f ml" % TARGET_VOLUME_ML)
print("Innen-Ø: %.2f mm" % (INNER_RADIUS * 2.0))
print("Gesamthöhe: %.2f mm" % TOTAL_HEIGHT)
print("Gesamtlänge: ca. %.2f mm" % (OUTER_RADIUS * 2.0 + HANDLE_EXTENSION))
print("Export:", folder)
