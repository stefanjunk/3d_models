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
- Export als STEP und STL
- Optionale 7-Waben-Vorschau als STEP

Koordinaten:
- XY = Ebene der Wand
- +Z = von der Vorderseite in Richtung Wand
- z=0 Vorderkante, z=DEPTH Rückseite/Wandseite
"""

from __future__ import annotations

import math
from pathlib import Path
import cadquery as cq

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
HANGER_INSET = 5.0               # Bossmitte vom Innenwandkontakt in den Innenraum
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
# Dadurch zeigt die Preview das Prinzip "wenige Wandlöcher, viele verbundene Waben".
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
    # v_inward > 0 bewegt vom Außenrand in das Material / Richtung Hexzentrum.
    return (
        face_center[0] + tangent[0] * u - outward[0] * v_inward,
        face_center[1] + tangent[1] * u - outward[1] * v_inward,
    )


def connector_groove_for_face(angle_deg: float, tangent_offset: float) -> cq.Workplane:
    """Eine rückseitig offene halbe Schwalbenschwanznut in einer Außenfläche."""
    outward, tangent = rotate_vec(angle_deg)
    face_center = (OUTER_APOTHEM * outward[0], OUTER_APOTHEM * outward[1])

    # V=0 liegt auf der Außenfläche; leicht nach außen erweitern für sauberen Cut.
    p1 = local_point(face_center, outward, tangent, tangent_offset - CONNECTOR_WAIST_WIDTH / 2, -EPS)
    p2 = local_point(face_center, outward, tangent, tangent_offset + CONNECTOR_WAIST_WIDTH / 2, -EPS)
    p3 = local_point(face_center, outward, tangent, tangent_offset + CONNECTOR_LOBE_WIDTH / 2, CONNECTOR_RECESS)
    p4 = local_point(face_center, outward, tangent, tangent_offset - CONNECTOR_LOBE_WIDTH / 2, CONNECTOR_RECESS)

    z0 = DEPTH - CONNECTOR_INSERT_LENGTH
    return prism_from_polygon([p1, p2, p3, p4], CONNECTOR_INSERT_LENGTH + 2 * EPS, z0=z0)


def add_connector_slots(part: cq.Workplane) -> cq.Workplane:
    if not ENABLE_CONNECTOR_SLOTS:
        return part

    # Außenflächennormalen einer pointy-top Wabe.
    face_angles = [0, 60, 120, 180, 240, 300]

    if CONNECTORS_PER_FACE == 1:
        offsets = [0.0]
    elif CONNECTORS_PER_FACE == 2:
        off = SIDE_LENGTH * CONNECTOR_TANGENT_FRACTION
        offsets = [-off, off]
    else:
        raise ValueError("CONNECTORS_PER_FACE unterstützt aktuell 1 oder 2.")

    result = part
    for angle in face_angles:
        for tangential in offsets:
            result = result.cut(connector_groove_for_face(angle, tangential))
    return result.clean()


def hanger_boss_center(angle_deg: float, tangent_offset: float) -> tuple[float, float]:
    """Bosszentrum knapp innerhalb einer Innenwand."""
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

    z0 = DEPTH - HANGER_THICKNESS
    boss_r = HANGER_BOSS_DIAMETER / 2.0
    tangent_amount = INNER_SIDE_LENGTH * HANGER_TANGENT_FRACTION

    # Obere rechte und obere linke Schrägwand.
    hanger_specs = [
        (60.0, +tangent_amount),
        (120.0, -tangent_amount),
    ]

    result = part

    for angle, tangential in hanger_specs:
        outward, tangent = rotate_vec(angle)
        cx, cy = hanger_boss_center(angle, tangential)

        # Runder Boss nahe der Wand.
        boss = (
            cq.Workplane("XY", origin=(0, 0, z0))
            .center(cx, cy)
            .circle(boss_r)
            .extrude(HANGER_THICKNESS)
        )

        # Kleine Brücke zur Innenwand, damit die Öse auch bei Parameterschwankungen sicher verbunden ist.
        wall_point = (
            INNER_APOTHEM * outward[0] + tangent[0] * tangential,
            INNER_APOTHEM * outward[1] + tangent[1] * tangential,
        )
        bridge_len = math.dist((cx, cy), wall_point) + WALL_THICKNESS * 0.8
        bridge_w = HANGER_BOSS_DIAMETER * 0.72
        bridge_center = ((cx + wall_point[0]) / 2.0, (cy + wall_point[1]) / 2.0)
        bridge_angle = math.degrees(math.atan2(wall_point[1] - cy, wall_point[0] - cx))
        bridge = (
            cq.Workplane("XY", origin=(0, 0, z0))
            .center(*bridge_center)
            .rect(bridge_len, bridge_w)
            .extrude(HANGER_THICKNESS)
            .rotate((0, 0, z0), (0, 0, z0 + 1), bridge_angle)
        )

        result = result.union(boss).union(bridge)

        # Durchgangsloch für Schraubenschaft.
        through = (
            cq.Workplane("XY", origin=(0, 0, z0 - EPS))
            .center(cx, cy)
            .circle(HANGER_HOLE_DIAMETER / 2.0)
            .extrude(HANGER_THICKNESS + 2 * EPS)
        )
        result = result.cut(through)

        # Flache Senkung auf der von vorne zugänglichen Seite des Bosses.
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
    # Die Nut wird mit zunehmender Tiefe breiter. Der Schlüssel endet wegen des
    # Druckspiels vor dem Nutgrund; seine Lobenbreite muss daher zur Breite der
    # Nut an genau dieser Tiefe passen (nicht zur Maximalbreite am Nutgrund).
    groove_width_at_key_depth = CONNECTOR_WAIST_WIDTH + (
        (CONNECTOR_LOBE_WIDTH - CONNECTOR_WAIST_WIDTH)
        * (recess / CONNECTOR_RECESS)
    )
    lobe = max(waist + 0.8, groove_width_at_key_depth - 2 * CONNECTOR_CLEARANCE)
    length = CONNECTOR_INSERT_LENGTH - CONNECTOR_CLEARANCE

    # X = Tangente/Schlüsselbreite, Y = quer durch beide Waben, Z = Einschubrichtung.
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
        # Nur Einsteckende leicht anfasen; wenn der Selector scheitert, bleibt der Schlüssel funktional.
        try:
            key = key.faces("<Z").edges().chamfer(CONNECTOR_LEADIN)
        except Exception:
            pass
    return key.clean()


def axial_to_xy(q: int, r: int) -> tuple[float, float]:
    """Axialkoordinaten für pointy-top Hexagons."""
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


def main() -> None:
    validate_parameters()

    print(f"CadQuery {cq.__version__}")
    print(f"Seitenkantenlänge: {SIDE_LENGTH:.2f} mm")
    print(f"Breite Seite-zu-Seite: {FLAT_TO_FLAT:.2f} mm")
    print(f"Höhe Spitze-zu-Spitze: {POINT_TO_POINT:.2f} mm")
    print(f"Tiefe: {DEPTH:.2f} mm")
    print(f"Wandstärke: {WALL_THICKNESS:.2f} mm")

    module_anchor = make_hex_module(enable_hangers=True)
    module_plain = make_hex_module(enable_hangers=False)
    key = make_connector_key()

    exports = {
        "wabe_mit_aufhaengung.step": module_anchor,
        "wabe_mit_aufhaengung.stl": module_anchor,
        "wabe_ohne_aufhaengung.step": module_plain,
        "wabe_ohne_aufhaengung.stl": module_plain,
        "waben_verbinder.step": key,
        "waben_verbinder.stl": key,
    }

    for filename, obj in exports.items():
        path = EXPORT_DIR / filename
        export_model(obj, path)
        print("Exportiert:", path.name)

    preview = make_preview_compound()
    export_model(preview, EXPORT_DIR / "setzkasten_7_waben_preview.step")
    print("Exportiert: setzkasten_7_waben_preview.step")


if __name__ == "__main__":
    main()
