# Parametrischer Flohsamen-Becher mit Außenbecher und Schraubdeckel
# Getestetes Konstruktionsprinzip: geschlossene, manifold Meshes ohne Boolean-Operationen.
# In Blender: Scripting > New > Inhalt einfügen > Run Script
#
# Das Skript erstellt:
#   1. Innerer Becher, ca. 100 ml, mit grobem Außengewinde
#   2. Passender Außenbecher
#   3. Deckel mit Innengewinde
# und exportiert alle drei Teile automatisch als STL.
#
# Maße sind in Millimetern.

import bpy
import bmesh
import math
import os
from pathlib import Path

# ============================================================
# EINSTELLUNGEN
# ============================================================

TARGET_VOLUME_ML = 100.0
INNER_RADIUS = 25.0          # 50 mm Innendurchmesser
WALL = 2.4                   # 3 Linien mit 0,8-mm-Düse
BOTTOM = 2.4
PITCH = 4.0                  # grobes Gewinde
THREAD_HEIGHT = 1.6
THREAD_TURNS = 3.1
THREAD_TOP_MARGIN = 1.2
NECK_STEP = 1.0

RADIAL_THREAD_CLEARANCE = 0.7
OUTER_CUP_CLEARANCE = 0.6

LID_TOP = 2.4
LID_SIDE = 3.3

THETA_SEGMENTS = 160
Z_STEP = 0.25

# Leer lassen = Exportordner auf dem Desktop bzw. im Benutzerordner.
EXPORT_DIRECTORY = ""

# ============================================================
# ABGELEITETE MASSE
# ============================================================

INNER_HEIGHT = TARGET_VOLUME_ML * 1000.0 / (math.pi * INNER_RADIUS ** 2)
INNER_CUP_HEIGHT = BOTTOM + INNER_HEIGHT

BODY_RADIUS = INNER_RADIUS + WALL
THREAD_CORE_RADIUS = BODY_RADIUS + NECK_STEP
THREAD_MAJOR_RADIUS = THREAD_CORE_RADIUS + THREAD_HEIGHT

THREAD_END = INNER_CUP_HEIGHT - THREAD_TOP_MARGIN
THREAD_START = THREAD_END - THREAD_TURNS * PITCH
TRANSITION_START = THREAD_START - 1.0

OUTER_CUP_INNER_RADIUS = BODY_RADIUS + OUTER_CUP_CLEARANCE
OUTER_CUP_INNER_DEPTH = TRANSITION_START
OUTER_CUP_HEIGHT = BOTTOM + OUTER_CUP_INNER_DEPTH
OUTER_CUP_OUTER_RADIUS = OUTER_CUP_INNER_RADIUS + WALL

FEMALE_ROOT_RADIUS = THREAD_MAJOR_RADIUS + RADIAL_THREAD_CLEARANCE
FEMALE_THREAD_DEPTH = THREAD_HEIGHT - 0.25

LID_CAVITY_HEIGHT = (INNER_CUP_HEIGHT - TRANSITION_START) + 1.6
LID_HEIGHT = LID_CAVITY_HEIGHT + LID_TOP
LID_OUTER_RADIUS = FEMALE_ROOT_RADIUS + LID_SIDE

# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def clamp01(value):
    return max(0.0, min(1.0, value))

def smoothstep01(value):
    value = clamp01(value)
    return value * value * (3.0 - 2.0 * value)

def thread_profile(phase, flat=0.18, slope=0.12):
    phase %= 1.0
    distance = min(phase, 1.0 - phase)
    half_flat = flat / 2.0
    half_total = half_flat + slope

    if distance <= half_flat:
        return 1.0
    if distance < half_total:
        return 1.0 - (distance - half_flat) / slope
    return 0.0

def thread_window(z, start, end, ramp=1.3):
    return (
        smoothstep01((z - start) / ramp)
        * smoothstep01((end - z) / ramp)
    )

def evenly_spaced(start, end, step):
    count = max(1, math.ceil((end - start) / step))
    return [start + (end - start) * i / count for i in range(count + 1)]

def triangulate(face):
    if len(face) == 3:
        return [face]
    return [
        (face[0], face[1], face[2]),
        (face[0], face[2], face[3]),
    ]

def create_mesh_object(name, vertices, faces):
    triangles = []
    for face in faces:
        triangles.extend(triangulate(face))

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], triangles)
    mesh.validate(verbose=False)
    mesh.update()

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def create_open_cup(name, outer_radius_fn, inner_radius_fn, height, bottom):
    ntheta = THETA_SEGMENTS
    theta_values = [2.0 * math.pi * i / ntheta for i in range(ntheta)]
    z_outer = evenly_spaced(0.0, height, Z_STEP)
    z_inner = evenly_spaced(bottom, height, Z_STEP)

    vertices = []
    faces = []

    outer_idx = []
    for z in z_outer:
        ring = []
        for theta in theta_values:
            radius = outer_radius_fn(theta, z)
            ring.append(len(vertices))
            vertices.append((
                radius * math.cos(theta),
                radius * math.sin(theta),
                z,
            ))
        outer_idx.append(ring)

    inner_idx = []
    for z in z_inner:
        ring = []
        for theta in theta_values:
            radius = inner_radius_fn(theta, z)
            ring.append(len(vertices))
            vertices.append((
                radius * math.cos(theta),
                radius * math.sin(theta),
                z,
            ))
        inner_idx.append(ring)

    # Außenwand
    for z_index in range(len(z_outer) - 1):
        for i in range(ntheta):
            j = (i + 1) % ntheta
            faces.append((
                outer_idx[z_index][i],
                outer_idx[z_index][j],
                outer_idx[z_index + 1][j],
                outer_idx[z_index + 1][i],
            ))

    # Innenwand
    for z_index in range(len(z_inner) - 1):
        for i in range(ntheta):
            j = (i + 1) % ntheta
            faces.append((
                inner_idx[z_index][i],
                inner_idx[z_index + 1][i],
                inner_idx[z_index + 1][j],
                inner_idx[z_index][j],
            ))

    # Oberer Rand
    for i in range(ntheta):
        j = (i + 1) % ntheta
        faces.append((
            outer_idx[-1][i],
            outer_idx[-1][j],
            inner_idx[-1][j],
            inner_idx[-1][i],
        ))

    # Unterseite
    bottom_center = len(vertices)
    vertices.append((0.0, 0.0, 0.0))
    for i in range(ntheta):
        j = (i + 1) % ntheta
        faces.append((
            bottom_center,
            outer_idx[0][j],
            outer_idx[0][i],
        ))

    # Innenboden
    floor_center = len(vertices)
    vertices.append((0.0, 0.0, bottom))
    for i in range(ntheta):
        j = (i + 1) % ntheta
        faces.append((
            floor_center,
            inner_idx[0][i],
            inner_idx[0][j],
        ))

    return create_mesh_object(name, vertices, faces)

def create_lid(name, outer_radius_fn, inner_radius_fn, height, cavity_height):
    ntheta = THETA_SEGMENTS
    theta_values = [2.0 * math.pi * i / ntheta for i in range(ntheta)]
    z_outer = evenly_spaced(0.0, height, Z_STEP)
    z_inner = evenly_spaced(0.0, cavity_height, Z_STEP)

    vertices = []
    faces = []

    outer_idx = []
    for z in z_outer:
        ring = []
        for theta in theta_values:
            radius = outer_radius_fn(theta, z)
            ring.append(len(vertices))
            vertices.append((
                radius * math.cos(theta),
                radius * math.sin(theta),
                z,
            ))
        outer_idx.append(ring)

    inner_idx = []
    for z in z_inner:
        ring = []
        for theta in theta_values:
            radius = inner_radius_fn(theta, z)
            ring.append(len(vertices))
            vertices.append((
                radius * math.cos(theta),
                radius * math.sin(theta),
                z,
            ))
        inner_idx.append(ring)

    # Außenwand
    for z_index in range(len(z_outer) - 1):
        for i in range(ntheta):
            j = (i + 1) % ntheta
            faces.append((
                outer_idx[z_index][i],
                outer_idx[z_index][j],
                outer_idx[z_index + 1][j],
                outer_idx[z_index + 1][i],
            ))

    # Innenwand mit Gewinde
    for z_index in range(len(z_inner) - 1):
        for i in range(ntheta):
            j = (i + 1) % ntheta
            faces.append((
                inner_idx[z_index][i],
                inner_idx[z_index + 1][i],
                inner_idx[z_index + 1][j],
                inner_idx[z_index][j],
            ))

    # Offener Rand
    for i in range(ntheta):
        j = (i + 1) % ntheta
        faces.append((
            outer_idx[0][i],
            inner_idx[0][i],
            inner_idx[0][j],
            outer_idx[0][j],
        ))

    # Deckelaußenseite
    top_center = len(vertices)
    vertices.append((0.0, 0.0, height))
    for i in range(ntheta):
        j = (i + 1) % ntheta
        faces.append((
            top_center,
            outer_idx[-1][i],
            outer_idx[-1][j],
        ))

    # Innere Decke
    ceiling_center = len(vertices)
    vertices.append((0.0, 0.0, cavity_height))
    for i in range(ntheta):
        j = (i + 1) % ntheta
        faces.append((
            ceiling_center,
            inner_idx[-1][j],
            inner_idx[-1][i],
        ))

    # 180° um X drehen und so verschieben, dass die geschlossene Seite
    # für einen supportfreien Druck auf dem Druckbett liegt.
    rotated = []
    for x, y, z in vertices:
        rotated.append((x, -y, height - z))

    return create_mesh_object(name, rotated, faces)

def inner_cup_outer(theta, z):
    transition = smoothstep01(
        (z - TRANSITION_START) / (THREAD_START - TRANSITION_START)
    )
    core_radius = BODY_RADIUS + (
        THREAD_CORE_RADIUS - BODY_RADIUS
    ) * transition

    amplitude = thread_window(z, THREAD_START, THREAD_END, 1.3)
    phase = z / PITCH - theta / (2.0 * math.pi)

    return (
        core_radius
        + THREAD_HEIGHT
        * amplitude
        * thread_profile(phase, flat=0.18, slope=0.12)
    )

def inner_cup_inner(theta, z):
    return INNER_RADIUS

def outer_cup_outer(theta, z):
    return OUTER_CUP_OUTER_RADIUS

def outer_cup_inner(theta, z):
    return OUTER_CUP_INNER_RADIUS

def lid_outer(theta, z):
    # Flache senkrechte Griffrippen.
    grip = 0.35 * (0.5 + 0.5 * math.cos(24.0 * theta)) ** 3
    return LID_OUTER_RADIUS + grip

def lid_inner(theta, z):
    amplitude = thread_window(
        z,
        1.0,
        LID_CAVITY_HEIGHT - 0.8,
        1.3,
    )
    phase = z / PITCH - theta / (2.0 * math.pi) + 0.5

    return (
        FEMALE_ROOT_RADIUS
        - FEMALE_THREAD_DEPTH
        * amplitude
        * thread_profile(phase, flat=0.12, slope=0.11)
    )

def choose_export_directory():
    if EXPORT_DIRECTORY.strip():
        return Path(EXPORT_DIRECTORY).expanduser()

    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop / "Flohsamen_Becher_STL"

    return Path.home() / "Flohsamen_Becher_STL"

def export_stl(obj, filepath):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()

    # Blender 4.x
    try:
        bpy.ops.wm.stl_export(
            filepath=str(filepath),
            export_selected_objects=True,
            ascii_format=False,
        )
        return
    except Exception:
        pass

    # Blender 3.x
    bpy.ops.export_mesh.stl(
        filepath=str(filepath),
        use_selection=True,
        ascii=False,
        global_scale=1.0,
    )

# ============================================================
# SZENE ERZEUGEN
# ============================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "MILLIMETERS"
scene.unit_settings.scale_length = 0.001

inner_cup = create_open_cup(
    "Innerer_Becher_100ml",
    inner_cup_outer,
    inner_cup_inner,
    INNER_CUP_HEIGHT,
    BOTTOM,
)

outer_cup = create_open_cup(
    "Aussenbecher",
    outer_cup_outer,
    outer_cup_inner,
    OUTER_CUP_HEIGHT,
    BOTTOM,
)

lid = create_lid(
    "Deckel_Innengewinde",
    lid_outer,
    lid_inner,
    LID_HEIGHT,
    LID_CAVITY_HEIGHT,
)

# Export zunächst am Ursprung.
export_dir = choose_export_directory()
export_dir.mkdir(parents=True, exist_ok=True)

export_stl(inner_cup, export_dir / "innerer_becher_100ml.stl")
export_stl(outer_cup, export_dir / "aussenbecher.stl")
export_stl(lid, export_dir / "deckel_innengewinde.stl")

# Danach übersichtlich nebeneinander in Blender anordnen.
inner_cup.location.x = -70.0
outer_cup.location.x = 0.0
lid.location.x = 75.0

# Blender-Datei speichern.
blend_path = export_dir / "flohsamen_becher_set.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

print("")
print("Fertig.")
print("Geometrisches Innenvolumen: %.2f ml" % TARGET_VOLUME_ML)
print("Innerer Becher: Ø innen %.1f mm, Höhe %.1f mm" % (
    INNER_RADIUS * 2.0,
    INNER_CUP_HEIGHT,
))
print("Gewinde: Steigung %.1f mm, radiales Spiel %.2f mm" % (
    PITCH,
    RADIAL_THREAD_CLEARANCE,
))
print("Exportordner:", export_dir)
