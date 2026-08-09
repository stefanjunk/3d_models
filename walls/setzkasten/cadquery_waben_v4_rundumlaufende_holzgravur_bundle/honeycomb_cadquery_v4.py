#!/usr/bin/env python3
"""
Parametrischer modularer Waben-Setzkasten in CadQuery.

Features
--------
- Regelmäßige sechseckige Einzelwabe mit offenen Vorder-/Rückseiten
- Leicht gerundete Wabenecken
- Parametrische Seitenkantenlänge und Tiefe
- Zwei innenliegende Aufhängeösen nahe den oberen Innenwänden
- Verdeckte rückseitige Doppelschwalbenschwanz-Verbinder auf allen 6 Seiten
- Separater Steckverbinder, der zwei benachbarte Waben koppelt
- Optionale Bild-/Heightmap-Gravur auf:
    * Außenflächen
    * Innenflächen
    * vorderer Kopfseite/Stirnfläche
    * optional rückwärtiger Kopfseite
- Automatische Erzeugung einer kupferstichartigen Höhenkarte aus einem Bild
- STEP bleibt als sauberes parametrisches CAD/B-Rep erhalten
- Die Bildgravur wird beim STL-Export als fein unterteilte Mesh-Gravur eingebracht
- Einheitliche Holzfaserrichtung: Bild-V läuft auf allen Seiten in Tiefenrichtung
- U läuft ohne Spiegelung kontinuierlich um den gesamten Wabenumfang

Warum Mesh für die Bildgravur?
------------------------------
Eine echte Graustufen-Höhenkarte besteht aus sehr vielen kleinen Höhenwerten.
Tausende B-Rep-Booleans in CadQuery/OpenCascade würden STEP-Datei und Renderzeit
unnötig groß machen. Deshalb bleibt die präzise Konstruktionsgeometrie CAD-basiert,
während die dekorative Gravur erst im STL-Mesh aufgebracht wird. Verbinder,
Aufhänger, Maße und Rundungen bleiben dadurch exakt.

Koordinaten:
- XY = Ebene der Wand
- +Z = von der Vorderseite in Richtung Wand
- z=0 Vorderkante, z=DEPTH Rückseite/Wandseite
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from PIL import Image, ImageFilter, ImageOps

# ============================================================
# HAUPTPARAMETER
# ============================================================

# Länge EINER Außenkante des regelmäßigen Sechsecks.
# 115.47 mm => ca. 200 mm Seite-zu-Seite (flat-to-flat).
SIDE_LENGTH = 115.47

# Tiefe von vorne bis zur Wand.
DEPTH = 55.0

WALL_THICKNESS = 4.5
CORNER_RADIUS = 4.0

# ============================================================
# AUFHÄNGUNG
# ============================================================

ENABLE_HANGERS = True
HANGER_THICKNESS = 5.0           # nur die letzten mm nahe der Wand
HANGER_BOSS_DIAMETER = 18.0
HANGER_HOLE_DIAMETER = 5.0
HANGER_COUNTERBORE_DIAMETER = 9.5
HANGER_COUNTERBORE_DEPTH = 2.2
HANGER_INSET = 1.8               # Bossmitte nur leicht von der Innenwand abgesetzt; hält die Ösen wandnah
HANGER_TANGENT_FRACTION = 0.17   # Position entlang der oberen Schrägwand

# ============================================================
# MODULARE VERBINDER
# ============================================================

ENABLE_CONNECTOR_SLOTS = True

# Pro Kontaktfläche werden zwei rückseitig eingeschobene Verbinder verwendet.
CONNECTORS_PER_FACE = 2
CONNECTOR_TANGENT_FRACTION = 0.22
CONNECTOR_INSERT_LENGTH = 20.0   # Länge des Schlüssels in Z-Richtung
CONNECTOR_RECESS = 1.55          # Eindringtiefe je Wabe; < Wandstärke
CONNECTOR_WAIST_WIDTH = 6.0      # schmale Breite direkt zwischen den beiden Waben
CONNECTOR_LOBE_WIDTH = 10.0      # breitere Verankerung im Material
CONNECTOR_CLEARANCE = 0.25       # Druckspiel pro Seite
CONNECTOR_LEADIN = 0.8           # Fase am Einsteckende des separaten Schlüssels

# ============================================================
# BILD-/HEIGHTMAP-TEXTUR
# ============================================================

ENABLE_TEXTURE = True

# Bilddatei mit der gewünschten Oberflächenstruktur.
# Im Bundle liegt bereits eine gerade fotografierte/generierte Holzwand.
TEXTURE_IMAGE = "wood_wall_source.png"

# Die daraus automatisch erzeugte Graustufenkarte.
TEXTURE_HEIGHTMAP = "wood_wall_engraving_heightmap.png"

# Welche Flächen graviert werden sollen.
TEXTURE_OUTER_SURFACES = True
TEXTURE_INNER_SURFACES = True
TEXTURE_FRONT_FACE = True       # sichtbare vordere Kopf-/Stirnseite
TEXTURE_BACK_FACE = False       # normalerweise an der Wand -> standardmäßig aus

# Maximale Tiefe der Gravur. Es wird NUR Material entfernt/eingedrückt.
TEXTURE_SIDE_DEPTH = 0.65       # mm
TEXTURE_FACE_DEPTH = 0.50       # mm

# "engraving" = lokale dunkle Linien/Kanten werden betont (Kupferstich-Look)
# "height"    = normale Graustufe des Bildes als Höhenkarte
TEXTURE_HEIGHTMAP_MODE = "engraving"
TEXTURE_INVERT = False

# Auflösung der erzeugten Heightmap. Diese kostet kaum Mesh-Speicher; die
# tatsächliche 3D-Auflösung wird primär durch TEXTURE_SUBDIVISIONS bestimmt.
TEXTURE_HEIGHTMAP_PIXELS = 1024

# 4 = guter Standard für ca. 20-cm-Waben, relativ speicherschonend.
# 5 = deutlich feiner, aber ungefähr 4x so viele Dreiecke / Datei deutlich größer.
# 3 = schnelle Vorschau.
TEXTURE_SUBDIVISIONS = 6

# Die Bildtextur wird physikalisch gekachelt. Kleinere Werte = feinere Maserung.
TEXTURE_TILE_SIZE_MM = 180.0

# Richtungsabbildung der Holzmaserung:
# Die V-Achse der Heightmap (im Quellbild die bevorzugte vertikale Faserrichtung)
# läuft auf ALLEN sechs Innen- und Außenflächen in +Z, also von der Front zur Wand.
# Die U-Achse läuft kontinuierlich gegen den Uhrzeigersinn um den Wabenumfang.
# Dadurch gibt es weder 60°-Wechsel noch gespiegelte Nachbarflächen.
TEXTURE_SIDE_GRAIN_ALONG_DEPTH = True
TEXTURE_CONTINUOUS_PERIMETER = True

# Keine zufälligen Phasenverschiebungen zwischen den Flächen.
TEXTURE_VARY_FACE_PHASE = False

# Kopfseite: Heightmap-V zeigt global nach +Y (= 90° zur +X-Achse).
TEXTURE_FRONT_GRAIN_ANGLE_DEG = 90.0

# Nur exakt planare Grundflächen werden graviert. Rundungen, Verbinder-Nuten,
# Aufhängeösen und deren Übergänge bleiben konstruktiv sauber.
TEXTURE_PLANE_TOLERANCE = 0.20   # mm
TEXTURE_NORMAL_TOLERANCE = 0.94

# ============================================================
# EXPORT / BEISPIEL-LAYOUT
# ============================================================

EXPORT_DIR = Path(__file__).resolve().parent
EXPORT_STL_TOLERANCE = 0.08
EXPORT_ANGULAR_TOLERANCE = 0.12

# Axialkoordinaten für eine kompakte 7-Waben-Vorschau.
PREVIEW_LAYOUT = [
    (0, 0),
    (1, 0), (-1, 0),
    (0, 1), (0, -1),
    (1, -1), (-1, 1),
]

# Nur diese Vorschau-Module besitzen Aufhängeösen.
PREVIEW_ANCHOR_CELLS = {(0, 1), (0, -1)}

EPS = 0.05


# ============================================================
# ABGELEITETE MASSE
# ============================================================

SQRT3 = math.sqrt(3.0)
OUTER_R = SIDE_LENGTH
OUTER_APOTHEM = SQRT3 * SIDE_LENGTH / 2.0
FLAT_TO_FLAT = 2.0 * OUTER_APOTHEM
POINT_TO_POINT = 2.0 * SIDE_LENGTH
INNER_APOTHEM = OUTER_APOTHEM - WALL_THICKNESS
INNER_R = INNER_APOTHEM / (SQRT3 / 2.0)
INNER_SIDE_LENGTH = INNER_R
INNER_CORNER_RADIUS = max(0.8, CORNER_RADIUS - WALL_THICKNESS * 0.35)
FACE_ANGLES = [0, 60, 120, 180, 240, 300]


def validate_parameters() -> None:
    if SIDE_LENGTH <= 20:
        raise ValueError("SIDE_LENGTH ist zu klein für dieses Design.")
    if DEPTH <= 10:
        raise ValueError("DEPTH muss > 10 mm sein.")
    if WALL_THICKNESS <= 2.0:
        raise ValueError("WALL_THICKNESS sollte für Regal/Verbinder > 2 mm sein.")
    if CONNECTOR_RECESS >= WALL_THICKNESS - 1.2:
        raise ValueError("CONNECTOR_RECESS lässt zu wenig Restwand stehen.")
    if CONNECTOR_INSERT_LENGTH >= DEPTH - 2.0:
        raise ValueError("CONNECTOR_INSERT_LENGTH muss deutlich kleiner als DEPTH sein.")
    if HANGER_THICKNESS >= DEPTH:
        raise ValueError("HANGER_THICKNESS muss kleiner als DEPTH sein.")
    if TEXTURE_SIDE_DEPTH < 0 or TEXTURE_FACE_DEPTH < 0:
        raise ValueError("Gravurtiefe darf nicht negativ sein.")
    if TEXTURE_SIDE_DEPTH >= WALL_THICKNESS * 0.45:
        raise ValueError("TEXTURE_SIDE_DEPTH ist für die Wandstärke zu groß.")
    if TEXTURE_SUBDIVISIONS < 0 or TEXTURE_SUBDIVISIONS > 6:
        raise ValueError("TEXTURE_SUBDIVISIONS sollte zwischen 0 und 6 liegen.")


def hex_points(radius: float) -> list[tuple[float, float]]:
    """Pointy-top Hexagon, identisch zur bisherigen OpenSCAD-Orientierung."""
    return [
        (0.0, radius),
        (SQRT3 / 2.0 * radius, radius / 2.0),
        (SQRT3 / 2.0 * radius, -radius / 2.0),
        (0.0, -radius),
        (-SQRT3 / 2.0 * radius, -radius / 2.0),
        (-SQRT3 / 2.0 * radius, radius / 2.0),
    ]


def prism_from_polygon(points: list[tuple[float, float]], height: float, z0: float = 0.0) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(0, 0, z0))
        .polyline(points)
        .close()
        .extrude(height)
    )


def rounded_hex_prism(radius: float, height: float, corner_radius: float, z0: float = 0.0) -> cq.Workplane:
    solid = prism_from_polygon(hex_points(radius), height, z0)
    if corner_radius > 0:
        solid = solid.edges("|Z").fillet(corner_radius)
    return solid


def base_hex_ring() -> cq.Workplane:
    outer = rounded_hex_prism(OUTER_R, DEPTH, CORNER_RADIUS)
    inner = rounded_hex_prism(
        INNER_R,
        DEPTH + 2 * EPS,
        INNER_CORNER_RADIUS,
        z0=-EPS,
    )
    return outer.cut(inner).clean()


def rotate_vec(angle_deg: float) -> tuple[tuple[float, float], tuple[float, float]]:
    a = math.radians(angle_deg)
    outward = (math.cos(a), math.sin(a))
    tangent = (-math.sin(a), math.cos(a))
    return outward, tangent


def local_point(
    face_center: tuple[float, float],
    outward: tuple[float, float],
    tangent: tuple[float, float],
    u: float,
    v_inward: float,
) -> tuple[float, float]:
    return (
        face_center[0] + tangent[0] * u - outward[0] * v_inward,
        face_center[1] + tangent[1] * u - outward[1] * v_inward,
    )


def connector_groove_for_face(angle_deg: float, tangent_offset: float) -> cq.Workplane:
    """Eine rückseitig offene halbe Schwalbenschwanznut in einer Außenfläche."""
    outward, tangent = rotate_vec(angle_deg)
    face_center = (OUTER_APOTHEM * outward[0], OUTER_APOTHEM * outward[1])

    p1 = local_point(face_center, outward, tangent, tangent_offset - CONNECTOR_WAIST_WIDTH / 2, -EPS)
    p2 = local_point(face_center, outward, tangent, tangent_offset + CONNECTOR_WAIST_WIDTH / 2, -EPS)
    p3 = local_point(face_center, outward, tangent, tangent_offset + CONNECTOR_LOBE_WIDTH / 2, CONNECTOR_RECESS)
    p4 = local_point(face_center, outward, tangent, tangent_offset - CONNECTOR_LOBE_WIDTH / 2, CONNECTOR_RECESS)

    z0 = DEPTH - CONNECTOR_INSERT_LENGTH
    return prism_from_polygon([p1, p2, p3, p4], CONNECTOR_INSERT_LENGTH + 2 * EPS, z0=z0)


def add_connector_slots(part: cq.Workplane) -> cq.Workplane:
    if not ENABLE_CONNECTOR_SLOTS:
        return part

    if CONNECTORS_PER_FACE == 1:
        offsets = [0.0]
    elif CONNECTORS_PER_FACE == 2:
        off = SIDE_LENGTH * CONNECTOR_TANGENT_FRACTION
        offsets = [-off, off]
    else:
        raise ValueError("CONNECTORS_PER_FACE unterstützt aktuell 1 oder 2.")

    result = part
    for angle in FACE_ANGLES:
        for tangential in offsets:
            result = result.cut(connector_groove_for_face(angle, tangential))
    return result.clean()


def hanger_boss_center(angle_deg: float, tangent_offset: float) -> tuple[float, float]:
    outward, tangent = rotate_vec(angle_deg)
    wall_point = (
        INNER_APOTHEM * outward[0] + tangent[0] * tangent_offset,
        INNER_APOTHEM * outward[1] + tangent[1] * tangent_offset,
    )
    boss_r = HANGER_BOSS_DIAMETER / 2.0
    inward = boss_r - HANGER_INSET
    return (
        wall_point[0] - outward[0] * inward,
        wall_point[1] - outward[1] * inward,
    )


def add_internal_hangers(part: cq.Workplane) -> cq.Workplane:
    if not ENABLE_HANGERS:
        return part

    # Frühere Versionen nutzten zusätzlich kleine rechteckige Brücken.
    # Diese führten optisch zu zwei "funktionslosen Blöcken" am Rand.
    # Jetzt bleiben nur noch die eigentlichen runden Schraubösen,
    # direkt wandnah an den beiden oberen Innenwänden.
    z0 = DEPTH - HANGER_THICKNESS
    boss_r = HANGER_BOSS_DIAMETER / 2.0
    tangent_amount = INNER_SIDE_LENGTH * HANGER_TANGENT_FRACTION

    hanger_specs = [
        (60.0, +tangent_amount),
        (120.0, -tangent_amount),
    ]

    result = part

    for angle, tangential in hanger_specs:
        cx, cy = hanger_boss_center(angle, tangential)

        boss = (
            cq.Workplane("XY", origin=(0, 0, z0))
            .center(cx, cy)
            .circle(boss_r)
            .extrude(HANGER_THICKNESS)
        )
        result = result.union(boss)

        through = (
            cq.Workplane("XY", origin=(0, 0, z0 - EPS))
            .center(cx, cy)
            .circle(HANGER_HOLE_DIAMETER / 2.0)
            .extrude(HANGER_THICKNESS + 2 * EPS)
        )
        result = result.cut(through)

        counterbore = (
            cq.Workplane("XY", origin=(0, 0, z0 - EPS))
            .center(cx, cy)
            .circle(HANGER_COUNTERBORE_DIAMETER / 2.0)
            .extrude(HANGER_COUNTERBORE_DEPTH + EPS)
        )
        result = result.cut(counterbore)

    return result.clean()

def make_hex_module(enable_hangers: bool = True) -> cq.Workplane:
    global ENABLE_HANGERS
    old = ENABLE_HANGERS
    try:
        ENABLE_HANGERS = enable_hangers
        part = base_hex_ring()
        part = add_connector_slots(part)
        part = add_internal_hangers(part)
        return part.clean()
    finally:
        ENABLE_HANGERS = old


def make_connector_key() -> cq.Workplane:
    """Separater Doppelschwalbenschwanz-Schlüssel für eine Verbindung."""
    recess = max(0.2, CONNECTOR_RECESS - CONNECTOR_CLEARANCE)
    waist = max(1.0, CONNECTOR_WAIST_WIDTH - 2 * CONNECTOR_CLEARANCE)
    groove_width_at_key_depth = CONNECTOR_WAIST_WIDTH + (
        (CONNECTOR_LOBE_WIDTH - CONNECTOR_WAIST_WIDTH)
        * (recess / CONNECTOR_RECESS)
    )
    lobe = max(waist + 0.8, groove_width_at_key_depth - 2 * CONNECTOR_CLEARANCE)
    length = CONNECTOR_INSERT_LENGTH - CONNECTOR_CLEARANCE

    pts = [
        (-lobe / 2, -recess),
        ( lobe / 2, -recess),
        ( waist / 2, 0.0),
        ( lobe / 2, recess),
        (-lobe / 2, recess),
        (-waist / 2, 0.0),
    ]
    key = prism_from_polygon(pts, length)

    if CONNECTOR_LEADIN > 0:
        try:
            key = key.faces("<Z").edges().chamfer(CONNECTOR_LEADIN)
        except Exception:
            pass
    return key.clean()


def axial_to_xy(q: int, r: int) -> tuple[float, float]:
    x = SQRT3 * SIDE_LENGTH * (q + r / 2.0)
    y = 1.5 * SIDE_LENGTH * r
    return x, y


def make_preview_compound() -> cq.Compound:
    shapes = []
    for cell in PREVIEW_LAYOUT:
        x, y = axial_to_xy(*cell)
        mod = make_hex_module(enable_hangers=(cell in PREVIEW_ANCHOR_CELLS))
        shapes.append(mod.val().moved(cq.Location(cq.Vector(x, y, 0))))
    return cq.Compound.makeCompound(shapes)


def export_model(obj, path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix == ".stl":
        cq.exporters.export(
            obj,
            str(path),
            tolerance=EXPORT_STL_TOLERANCE,
            angularTolerance=EXPORT_ANGULAR_TOLERANCE,
        )
    else:
        cq.exporters.export(obj, str(path))


# ============================================================
# HEIGHTMAP-ERZEUGUNG
# ============================================================

def resolve_asset(name: str) -> Path:
    p = Path(name)
    if not p.is_absolute():
        p = EXPORT_DIR / p
    return p


def build_heightmap() -> tuple[np.ndarray, Path]:
    """Erzeugt/aktualisiert die Heightmap aus TEXTURE_IMAGE und gibt 0..1 zurück."""
    src = resolve_asset(TEXTURE_IMAGE)
    out = resolve_asset(TEXTURE_HEIGHTMAP)

    if not src.exists():
        raise FileNotFoundError(
            f"Texturbild fehlt: {src}\n"
            "Lege ein Bild dort ab oder ändere TEXTURE_IMAGE."
        )

    px = max(32, int(TEXTURE_HEIGHTMAP_PIXELS))
    img = Image.open(src).convert("L")
    img = ImageOps.fit(img, (px, px), method=Image.Resampling.LANCZOS)

    if TEXTURE_HEIGHTMAP_MODE.lower() == "height":
        arr = np.asarray(img, dtype=np.float32) / 255.0
        arr = 1.0 - arr  # dunkle Bildstellen = tiefere Gravur
    elif TEXTURE_HEIGHTMAP_MODE.lower() == "engraving":
        g = np.asarray(img, dtype=np.float32) / 255.0
        local = np.asarray(
            img.filter(ImageFilter.GaussianBlur(radius=max(1.0, px / 64.0))),
            dtype=np.float32,
        ) / 255.0
        fine = np.asarray(
            img.filter(ImageFilter.GaussianBlur(radius=max(0.45, px / 230.0))),
            dtype=np.float32,
        ) / 255.0

        # Dunkle Maserung/Risse gegenüber lokaler Umgebung.
        dark_detail = np.clip((local - g) * 4.2, 0.0, 1.0)
        # Feine lokale Unterschiede unabhängig von absoluter Holzhelligkeit.
        detail = np.clip(np.abs(fine - g) * 5.2, 0.0, 1.0)
        # Breiter Grundverlauf des Holzes, damit Planken und Astlöcher lesbar bleiben.
        base_wood = np.clip((1.0 - g - 0.18) / 0.82, 0.0, 1.0)
        # Kanten geben den kupferstichartigen Liniencharakter.
        edge_img = img.filter(ImageFilter.FIND_EDGES).filter(
            ImageFilter.GaussianBlur(radius=max(0.2, px / 640.0))
        )
        edges = np.asarray(edge_img, dtype=np.float32) / 255.0
        edges = np.clip((edges - 0.05) * 2.4, 0.0, 1.0)

        arr = 0.38 * base_wood + 0.42 * dark_detail + 0.28 * detail + 0.18 * edges
        arr = np.clip(arr, 0.0, 1.0)
        arr = np.asarray(ImageOps.autocontrast(Image.fromarray(np.uint8(arr * 255), mode="L")), dtype=np.float32) / 255.0
        p99 = float(np.percentile(arr, 99.4))
        if p99 > 1e-6:
            arr = np.clip(arr / p99, 0.0, 1.0)
        arr = arr ** 1.05
    else:
        raise ValueError('TEXTURE_HEIGHTMAP_MODE muss "engraving" oder "height" sein.')

    if TEXTURE_INVERT:
        arr = 1.0 - arr

    Image.fromarray(np.uint8(np.clip(arr, 0, 1) * 255), mode="L").save(out)
    return arr.astype(np.float32), out


# ============================================================
# MESH-GRAVUR
# ============================================================

def _face_basis(angle_deg: float) -> tuple[np.ndarray, np.ndarray]:
    a = math.radians(angle_deg)
    outward = np.array([math.cos(a), math.sin(a), 0.0], dtype=np.float64)
    tangent = np.array([-math.sin(a), math.cos(a), 0.0], dtype=np.float64)
    return outward, tangent


def _perimeter_u_mm(points: np.ndarray, face_index: int, side_len: float, tangent: np.ndarray) -> np.ndarray:
    """Kontinuierliche U-Koordinate um den kompletten Hexagonumfang.

    FACE_ANGLES sind gegen den Uhrzeigersinn sortiert und _face_basis liefert
    dazu ebenfalls eine gegen den Uhrzeigersinn laufende Tangente. Deshalb
    steigt U an einer gemeinsamen Ecke ohne Spiegelung in der nächsten Fläche
    weiter. Das verhindert wechselnde Textur-/Maserungsrichtungen.
    """
    local_t = points @ tangent
    return face_index * side_len + local_t + side_len / 2.0


def _hex_radial_mm(points_xy: np.ndarray) -> np.ndarray:
    """Hexagonaler radialer Abstand anhand der sechs Flächennormalen."""
    radial = np.full(len(points_xy), -1e18, dtype=np.float64)
    for angle in FACE_ANGLES:
        outward, _ = _face_basis(angle)
        radial = np.maximum(radial, points_xy @ outward[:2])
    return radial


def _side_wrap_u_mm(points_xy: np.ndarray, perimeter_mm: float, angle_offset_deg: float = 0.0) -> np.ndarray:
    """Kontinuierliche U-Koordinate einmal rund um die komplette Wabe.

    Anders als die frühere flächenweise Zuordnung funktioniert diese Abbildung
    auch auf den Eckrundungen ohne Richtungswechsel.
    """
    ang = np.arctan2(points_xy[:, 1], points_xy[:, 0]) - math.radians(angle_offset_deg)
    ang = np.mod(ang, 2.0 * math.pi)
    return ang / (2.0 * math.pi) * perimeter_mm


def side_vertex_masks(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray]:
    """Ermittelt Außen- und Innen-Seitenbereiche inklusive Eckrundungen."""
    v = mesh.vertices
    vn = mesh.vertex_normals
    xy = v[:, :2]
    radial = _hex_radial_mm(xy)
    horiz = np.abs(vn[:, 2]) < 0.42

    outer_band = (radial >= OUTER_APOTHEM - CORNER_RADIUS - 0.8) & (radial <= OUTER_APOTHEM + 0.8)
    inner_band = (radial >= INNER_APOTHEM - 0.8) & (radial <= INNER_APOTHEM + INNER_CORNER_RADIUS + 0.8)

    not_front_back = (v[:, 2] > TEXTURE_PLANE_TOLERANCE * 1.5) & (v[:, 2] < DEPTH - TEXTURE_PLANE_TOLERANCE * 1.5)

    outer_mask = horiz & outer_band & not_front_back
    inner_mask = horiz & inner_band & not_front_back & (~outer_mask)
    return outer_mask, inner_mask

def classify_texture_faces(mesh: trimesh.Trimesh) -> np.ndarray:
    """
    Labelt nur die großen, planaren Originalflächen.

    0      = nicht texturieren
    1..6   = Außenflächen
    7..12  = Innenflächen
    13     = vordere Kopfseite z=0
    14     = rückwärtige Kopfseite z=DEPTH
    """
    c = mesh.triangles_center
    n = mesh.face_normals
    labels = np.zeros(len(mesh.faces), dtype=np.int16)

    # Kopfseiten: nur Bereich des Hex-Rings, damit interne Hanger nicht erwischt werden.
    radial = np.zeros(len(c), dtype=np.float64)
    for angle in FACE_ANGLES:
        outward, _ = _face_basis(angle)
        radial = np.maximum(radial, c @ outward)
    ring_mask = (
        (radial >= INNER_APOTHEM - TEXTURE_PLANE_TOLERANCE * 2)
        & (radial <= OUTER_APOTHEM + TEXTURE_PLANE_TOLERANCE * 2)
    )

    if TEXTURE_FRONT_FACE:
        labels[
            (np.abs(c[:, 2]) <= TEXTURE_PLANE_TOLERANCE)
            & (n[:, 2] < -TEXTURE_NORMAL_TOLERANCE)
            & ring_mask
        ] = 13

    if TEXTURE_BACK_FACE:
        labels[
            (np.abs(c[:, 2] - DEPTH) <= TEXTURE_PLANE_TOLERANCE)
            & (n[:, 2] > TEXTURE_NORMAL_TOLERANCE)
            & ring_mask
        ] = 14

    # Planare Innen-/Außenflächen.
    horizontal_normal = np.abs(n[:, 2]) < 0.08
    for i, angle in enumerate(FACE_ANGLES):
        outward, _ = _face_basis(angle)
        plane_d = c @ outward
        normal_d = n @ outward

        if TEXTURE_OUTER_SURFACES:
            mask = (
                horizontal_normal
                & (np.abs(plane_d - OUTER_APOTHEM) <= TEXTURE_PLANE_TOLERANCE)
                & (normal_d > TEXTURE_NORMAL_TOLERANCE)
            )
            labels[mask] = 1 + i

        if TEXTURE_INNER_SURFACES:
            mask = (
                horizontal_normal
                & (np.abs(plane_d - INNER_APOTHEM) <= TEXTURE_PLANE_TOLERANCE)
                & (normal_d < -TEXTURE_NORMAL_TOLERANCE)
            )
            labels[mask] = 7 + i

    return labels


def subdivide_with_labels(
    mesh: trimesh.Trimesh,
    labels: np.ndarray,
    iterations: int,
) -> tuple[trimesh.Trimesh, np.ndarray]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    face_labels = labels.copy()

    # Globale Unterteilung hält das Mesh wasserdicht. Selektive Unterteilung würde
    # an den Grenzen T-Junctions erzeugen.
    for _ in range(iterations):
        vertices, faces = trimesh.remesh.subdivide(vertices, faces)
        face_labels = np.repeat(face_labels, 4)

    result = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    return result, face_labels


def vertex_surface_labels(mesh: trimesh.Trimesh, face_labels: np.ndarray) -> np.ndarray:
    """Nur Vertices, deren ALLE Nachbarflächen zur selben Zielfläche gehören, werden bewegt."""
    vf = mesh.vertex_faces
    result = np.zeros(len(mesh.vertices), dtype=np.int16)

    # Dieser konservative Ansatz lässt Kanten/Rundungen/Bohrungen unangetastet.
    for vi in range(len(mesh.vertices)):
        fi = vf[vi]
        fi = fi[fi >= 0]
        if len(fi) == 0:
            continue
        local = face_labels[fi]
        first = local[0]
        if first > 0 and np.all(local == first):
            result[vi] = first
    return result


def sample_heightmap(heightmap: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Bilineare, nahtlos gekachelte Abtastung."""
    h, w = heightmap.shape
    u = np.mod(u, 1.0) * (w - 1)
    v = np.mod(v, 1.0) * (h - 1)

    x0 = np.floor(u).astype(np.int64)
    y0 = np.floor(v).astype(np.int64)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    fx = u - x0
    fy = v - y0

    a = heightmap[y0, x0]
    b = heightmap[y0, x1]
    c = heightmap[y1, x0]
    d = heightmap[y1, x1]
    return (
        a * (1 - fx) * (1 - fy)
        + b * fx * (1 - fy)
        + c * (1 - fx) * fy
        + d * fx * fy
    )


def apply_heightmap_engraving(
    mesh: trimesh.Trimesh,
    heightmap: np.ndarray,
) -> trimesh.Trimesh:
    original_labels = classify_texture_faces(mesh)
    textured, face_labels = subdivide_with_labels(mesh, original_labels, TEXTURE_SUBDIVISIONS)
    vlabels = vertex_surface_labels(textured, face_labels)

    verts = textured.vertices.copy()
    tile = max(5.0, float(TEXTURE_TILE_SIZE_MM))

    # --------------------------------------------------------
    # Seitenflächen: echte rundumlaufende Gravur
    # --------------------------------------------------------
    # Die Holzmaserung verläuft auf allen Seiten in Tiefenrichtung (Z).
    # Die zweite Texturachse läuft kontinuierlich rund um den gesamten
    # Umfang der Wabe. Dadurch bleiben Faserrichtung und Holzbild auch
    # auf den Eckrundungen durchgängig.
    outer_side_mask, inner_side_mask = side_vertex_masks(textured)
    vnormals = textured.vertex_normals.copy()

    if TEXTURE_OUTER_SURFACES and np.any(outer_side_mask):
        pts = verts[outer_side_mask]
        u_mm = _side_wrap_u_mm(pts[:, :2], perimeter_mm=6.0 * SIDE_LENGTH, angle_offset_deg=0.0)
        v_mm = pts[:, 2] if TEXTURE_SIDE_GRAIN_ALONG_DEPTH else u_mm
        u = u_mm / tile
        v = v_mm / tile
        amount = sample_heightmap(heightmap, u, v) * TEXTURE_SIDE_DEPTH
        verts[outer_side_mask] += (-vnormals[outer_side_mask]) * amount[:, None]

    if TEXTURE_INNER_SURFACES and np.any(inner_side_mask):
        pts = verts[inner_side_mask]
        u_mm = _side_wrap_u_mm(pts[:, :2], perimeter_mm=6.0 * INNER_SIDE_LENGTH, angle_offset_deg=0.0)
        v_mm = pts[:, 2] if TEXTURE_SIDE_GRAIN_ALONG_DEPTH else u_mm
        u = u_mm / tile
        v = v_mm / tile
        amount = sample_heightmap(heightmap, u, v) * TEXTURE_SIDE_DEPTH
        verts[inner_side_mask] += (-vnormals[inner_side_mask]) * amount[:, None]

    # Kopfseiten
    idx = np.flatnonzero(vlabels == 13)
    if len(idx):
        pts = verts[idx]
        ga = math.radians(TEXTURE_FRONT_GRAIN_ANGLE_DEG)
        grain = np.array([math.cos(ga), math.sin(ga)], dtype=np.float64)
        cross = np.array([-grain[1], grain[0]], dtype=np.float64)
        u = (pts[:, :2] @ cross) / tile
        v = (pts[:, :2] @ grain) / tile
        amount = sample_heightmap(heightmap, u, v) * TEXTURE_FACE_DEPTH
        verts[idx] += (-vnormals[idx]) * amount[:, None]

    idx = np.flatnonzero(vlabels == 14)
    if len(idx):
        pts = verts[idx]
        ga = math.radians(TEXTURE_FRONT_GRAIN_ANGLE_DEG)
        grain = np.array([math.cos(ga), math.sin(ga)], dtype=np.float64)
        cross = np.array([-grain[1], grain[0]], dtype=np.float64)
        u = (pts[:, :2] @ cross) / tile
        v = (pts[:, :2] @ grain) / tile
        amount = sample_heightmap(heightmap, u, v) * TEXTURE_FACE_DEPTH
        verts[idx] += (-vnormals[idx]) * amount[:, None]

    textured.vertices = verts
    textured.remove_unreferenced_vertices()
    return textured

def export_textured_stl(part: cq.Workplane, out_path: Path, heightmap: np.ndarray) -> dict[str, object]:
    temp = EXPORT_DIR / f".__texture_tmp_{out_path.stem}.stl"
    try:
        export_model(part, temp)
        mesh = trimesh.load_mesh(temp, force="mesh", process=True)
        if not isinstance(mesh, trimesh.Trimesh):
            raise RuntimeError("STL konnte nicht als einzelnes Mesh geladen werden.")
        before_faces = len(mesh.faces)
        result = apply_heightmap_engraving(mesh, heightmap)
        result.export(out_path, file_type="stl")
        return {
            "watertight": bool(result.is_watertight),
            "winding_consistent": bool(result.is_winding_consistent),
            "faces_before": int(before_faces),
            "faces_after": int(len(result.faces)),
            "vertices_after": int(len(result.vertices)),
        }
    finally:
        if temp.exists():
            temp.unlink()


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    validate_parameters()

    print(f"CadQuery {cq.__version__}")
    print(f"Seitenkantenlänge: {SIDE_LENGTH:.2f} mm")
    print(f"Breite Seite-zu-Seite: {FLAT_TO_FLAT:.2f} mm")
    print(f"Höhe Spitze-zu-Spitze: {POINT_TO_POINT:.2f} mm")
    print(f"Tiefe: {DEPTH:.2f} mm")
    print(f"Wandstärke: {WALL_THICKNESS:.2f} mm")
    print(f"Textur: {'AN' if ENABLE_TEXTURE else 'AUS'}")

    module_anchor = make_hex_module(enable_hangers=True)
    module_plain = make_hex_module(enable_hangers=False)
    key = make_connector_key()

    # STEP bleibt bewusst sauberes CAD/B-Rep.
    step_exports = {
        "wabe_mit_aufhaengung.step": module_anchor,
        "wabe_ohne_aufhaengung.step": module_plain,
        "waben_verbinder.step": key,
    }
    for filename, obj in step_exports.items():
        path = EXPORT_DIR / filename
        export_model(obj, path)
        print("Exportiert:", path.name)

    # Glatte Referenz-STLs sind immer praktisch zum Vergleichen und schnellen Slicen.
    smooth_exports = {
        "wabe_mit_aufhaengung_glatt.stl": module_anchor,
        "wabe_ohne_aufhaengung_glatt.stl": module_plain,
        "waben_verbinder.stl": key,
    }
    for filename, obj in smooth_exports.items():
        path = EXPORT_DIR / filename
        export_model(obj, path)
        print("Exportiert:", path.name)

    if ENABLE_TEXTURE:
        heightmap, heightmap_path = build_heightmap()
        print("Heightmap erzeugt:", heightmap_path.name)

        textured_specs = [
            (module_anchor, "wabe_mit_aufhaengung_texturiert.stl", "wabe_mit_aufhaengung.stl"),
            (module_plain, "wabe_ohne_aufhaengung_texturiert.stl", "wabe_ohne_aufhaengung.stl"),
        ]
        for obj, textured_name, convenient_name in textured_specs:
            out = EXPORT_DIR / textured_name
            stats = export_textured_stl(obj, out, heightmap)
            shutil.copyfile(out, EXPORT_DIR / convenient_name)
            print(
                f"Texturiert: {textured_name} | watertight={stats['watertight']} | "
                f"Faces {stats['faces_before']} -> {stats['faces_after']}"
            )
    else:
        shutil.copyfile(EXPORT_DIR / "wabe_mit_aufhaengung_glatt.stl", EXPORT_DIR / "wabe_mit_aufhaengung.stl")
        shutil.copyfile(EXPORT_DIR / "wabe_ohne_aufhaengung_glatt.stl", EXPORT_DIR / "wabe_ohne_aufhaengung.stl")

    preview = make_preview_compound()
    export_model(preview, EXPORT_DIR / "setzkasten_7_waben_preview.step")
    print("Exportiert: setzkasten_7_waben_preview.step")


if __name__ == "__main__":
    main()
