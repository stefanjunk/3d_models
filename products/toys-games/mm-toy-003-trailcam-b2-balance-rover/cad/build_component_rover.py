"""Build MM-TOY-003 component-driven DRAFT candidate 0.1.0-parametric.3.

Critical printed geometry is deterministic CadQuery B-Rep.  Purchased parts
are named, dimensioned registration proxies for BOM 0.1.0-bom.1.  STEP files
retain assembly coordinates; DRAFT STL files are separately print-oriented.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import sys
from dataclasses import dataclass
from functools import reduce
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import component_parameters as P

ARTIFACT_REVISION = f"v{P.CANDIDATE}"
EXPORT_ROOT = HERE / "exports" / ARTIFACT_REVISION
STEP_DIR = EXPORT_ROOT / "master-step"
MESH_DIR = EXPORT_ROOT / "validation-mesh"
ASSEMBLY_MESH_DIR = EXPORT_ROOT / "assembly-mesh"
PREVIEW_DIR = ROOT / "previews"
VALIDATION_DIR = ROOT / "validation" / ARTIFACT_REVISION


@dataclass(frozen=True)
class Part:
    name: str
    shape: cq.Shape
    group: str
    material: str
    color: tuple[float, float, float, float]
    print_orientation: str
    interface_authority: str


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Solid:
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    za, zb = sorted((z0, z1))
    return cq.Solid.makeBox(xb - xa, yb - ya, zb - za, pnt=(xa, ya, za))


def cyl(
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    radius: float,
) -> cq.Solid:
    delta = cq.Vector(p1) - cq.Vector(p0)
    return cq.Solid.makeCylinder(radius, delta.Length, pnt=p0, dir=delta.normalized())


def fuse(shapes: list[cq.Shape]) -> cq.Shape:
    if not shapes:
        raise ValueError("cannot fuse an empty shape list")
    return reduce(lambda left, right: left.fuse(right), shapes)


def cut_many(shape: cq.Shape, cutters: list[cq.Shape]) -> cq.Shape:
    return reduce(lambda result, cutter: result.cut(cutter), cutters, shape)


def prism_xz(points: list[tuple[float, float]], y0: float, y1: float) -> cq.Solid:
    ya, yb = sorted((y0, y1))
    workplane = cq.Workplane("XZ", origin=(0.0, yb, 0.0)).moveTo(*points[0])
    for point in points[1:]:
        workplane = workplane.lineTo(*point)
    return workplane.close().extrude(yb - ya).val()


def bar_xz(
    p0: tuple[float, float],
    p1: tuple[float, float],
    width: float,
    y0: float,
    y1: float,
) -> cq.Solid:
    x0, z0 = p0
    x1, z1 = p1
    dx, dz = x1 - x0, z1 - z0
    length = math.hypot(dx, dz)
    if length <= 0:
        raise ValueError("bar endpoints must differ")
    px, pz = -dz / length * width / 2.0, dx / length * width / 2.0
    return prism_xz(
        [
            (x0 + px, z0 + pz),
            (x1 + px, z1 + pz),
            (x1 - px, z1 - pz),
            (x0 - px, z0 - pz),
        ],
        y0,
        y1,
    )


def slot_xy(
    x: float,
    y: float,
    length: float,
    width: float,
    axis: str,
    z0: float,
    z1: float,
) -> cq.Shape:
    """Vertical-axis rounded slot whose long axis is X or Y."""
    half = (length - width) / 2.0
    if half < 0:
        raise ValueError("slot length must be at least its width")
    if axis == "x":
        core = box(x - half, x + half, y - width / 2.0, y + width / 2.0, z0, z1)
        ends = [
            cyl((x + sign * half, y, z0), (x + sign * half, y, z1), width / 2.0)
            for sign in (-1, 1)
        ]
    elif axis == "y":
        core = box(x - width / 2.0, x + width / 2.0, y - half, y + half, z0, z1)
        ends = [
            cyl((x, y + sign * half, z0), (x, y + sign * half, z1), width / 2.0)
            for sign in (-1, 1)
        ]
    else:
        raise ValueError("axis must be 'x' or 'y'")
    return fuse([core, *ends])


def slot_xz_through_y(
    x: float,
    z: float,
    length_x: float,
    width_z: float,
    y0: float,
    y1: float,
) -> cq.Shape:
    half = (length_x - width_z) / 2.0
    core = box(x - half, x + half, y0, y1, z - width_z / 2.0, z + width_z / 2.0)
    ends = [
        cyl((x + sign * half, y0, z), (x + sign * half, y1, z), width_z / 2.0)
        for sign in (-1, 1)
    ]
    return fuse([core, *ends])


def side_frame(side: int) -> cq.Shape:
    if side not in (-1, 1):
        raise ValueError("side must be -1 or +1")
    yc = side * P.SIDE_FRAME_Y_MM
    y0 = yc - P.SIDE_FRAME_THICKNESS_MM / 2.0
    y1 = yc + P.SIDE_FRAME_THICKNESS_MM / 2.0
    bars = [
        bar_xz((-72, -24), (72, -24), P.BAR_MAIN_MM, y0, y1),
        bar_xz((-72, -24), (-64, 170), P.BAR_MAIN_MM, y0, y1),
        bar_xz((72, -24), (64, 170), P.BAR_MAIN_MM, y0, y1),
        bar_xz((-64, 170), (0, 184), P.BAR_MAIN_MM, y0, y1),
        bar_xz((0, 184), (64, 170), P.BAR_MAIN_MM, y0, y1),
        # Start inside the motor ring so tessellation cannot retain a tangent,
        # four-face edge at the ring crown.
        bar_xz((0, 18), (0, 181), P.BAR_MAIN_MM, y0, y1),
        bar_xz((-69, 108), (69, 108), P.BAR_SECONDARY_MM, y0, y1),
        bar_xz((-68, 150), (68, 150), P.BAR_SECONDARY_MM, y0, y1),
        bar_xz((-55, 171), (55, 171), P.BAR_SECONDARY_MM, y0, y1),
        bar_xz((-66, 108), (0, 150), P.BAR_BRACE_MM, y0, y1),
        bar_xz((66, 108), (0, 150), P.BAR_BRACE_MM, y0, y1),
        bar_xz((-62, 150), (0, 180), P.BAR_BRACE_MM, y0, y1),
        bar_xz((62, 150), (0, 180), P.BAR_BRACE_MM, y0, y1),
    ]
    motor_ring = cyl((0, y0, 0), (0, y1, 0), 29.0).cut(
        cyl((0, y0 - 1, 0), (0, y1 + 1, 0), P.MOTOR_BODY_RADIUS_MM + 2.1)
    )
    shape = fuse([motor_ring, *bars])
    through_holes = [
        (-22.0, -28.0),
        (22.0, -28.0),
        (-22.0, -12.0),
        (22.0, -12.0),
        (-64.0, 108.0),
        (64.0, 108.0),
        (-62.0, 150.0),
        (62.0, 150.0),
        (-50.0, 171.0),
        (50.0, 171.0),
        (-58.0, -25.0),
        (58.0, -25.0),
    ]
    cutters = [
        cyl((x, y0 - 1.0, z), (x, y1 + 1.0, z), P.M3_CLEARANCE_MM / 2.0)
        for x, z in through_holes
    ]
    return cut_many(shape, cutters)


def axle_crossmember() -> cq.Shape:
    end = P.CROSSMEMBER_END_Y_MM
    shape = fuse(
        [
            box(-36, -28, -end, end, -31, -25),
            box(-5, 5, -end, end, -31, -25),
            box(28, 36, -end, end, -31, -25),
            box(-36, 36, -end, -end + 9, -31, -25),
            box(-36, 36, end - 9, end, -31, -25),
            box(-36, -29, -end, end, -25, -19),
            box(-4, 4, -end, end, -25, -19),
            box(29, 36, -end, end, -25, -19),
        ]
    )
    cutters = []
    for side in (-1, 1):
        y_end = side * end
        for x in (-22.0, 22.0):
            cutters.append(
                cyl(
                    (x, y_end + side * 1.0, -28.0),
                    (x, y_end - side * P.M3_INSERT_DEPTH_MM_PROVISIONAL, -28.0),
                    P.M3_INSERT_PILOT_MM_PROVISIONAL / 2.0,
                )
            )
    return cut_many(shape, cutters)


def motor_pod(side: int) -> cq.Shape:
    if side not in (-1, 1):
        raise ValueError("side must be -1 or +1")
    inner = side * P.SIDE_FRAME_OUTER_Y_MM
    outer = side * P.MOTOR_POD_OUTER_Y_MM
    flange_outer = side * (P.SIDE_FRAME_OUTER_Y_MM + 4.0)
    shape = fuse(
        [
            box(-24, 24, inner, outer, -25, -18),
            box(-24, 24, inner, flange_outer, -22, 5),
            box(-24, -18, inner, outer, -18, -7),
            box(18, 24, inner, outer, -18, -7),
        ]
    )
    cutters = [
        cyl(
            (x, inner - side * 1.0, z),
            (x, flange_outer + side * 1.0, z),
            P.M3_CLEARANCE_MM / 2.0,
        )
        for x, z in ((-22.0, -12.0), (22.0, -12.0))
    ]
    for x in (-P.MOTOR_BRACKET_BASE_PITCH_MM, 0.0, P.MOTOR_BRACKET_BASE_PITCH_MM):
        cutters.append(
            slot_xy(
                x,
                side * P.MOTOR_BRACKET_CENTER_Y_MM,
                P.MOTOR_BRACKET_AXIAL_SLOT_MM,
                P.M3_SLOT_WIDTH_MM,
                "y",
                -27,
                -16,
            )
        )
    return cut_many(shape, cutters)


def frame_crossmember(z0: float, z1: float, role: str) -> cq.Shape:
    end = P.CROSSMEMBER_END_Y_MM
    if role == "battery":
        x_outer, x_inner, y_band = 74.0, 62.0, 8.0
        mount_x, mount_z = 64.0, 108.0
    elif role == "electronics":
        x_outer, x_inner, y_band = 72.0, 60.0, 8.0
        mount_x, mount_z = 62.0, 150.0
    elif role == "upper":
        x_outer, x_inner, y_band = 58.0, 48.0, 8.0
        mount_x, mount_z = 50.0, 171.0
    else:
        raise ValueError(role)
    shape = fuse(
        [
            box(-x_outer, -x_inner, -end, end, z0, z1),
            box(x_inner, x_outer, -end, end, z0, z1),
            box(-x_inner, x_inner, -32, -32 + y_band, z0, z1),
            box(-x_inner, x_inner, 32 - y_band, 32, z0, z1),
            box(-6, 6, -32, 32, z0, z1),
        ]
    )
    cutters = []
    for side in (-1, 1):
        y_end = side * end
        for x in (-mount_x, mount_x):
            cutters.append(
                cyl(
                    (x, y_end + side * 1.0, mount_z),
                    (x, y_end - side * P.M3_INSERT_DEPTH_MM_PROVISIONAL, mount_z),
                    P.M3_INSERT_PILOT_MM_PROVISIONAL / 2.0,
                )
            )
    if role == "battery":
        for x in (-55.0, 55.0):
            for y in (-29.0, 29.0):
                cutters.append(cyl((x, y, z0 - 1), (x, y, z1 + 1), P.M3_CLEARANCE_MM / 2.0))
    elif role == "electronics":
        for x in (-68.0, 68.0):
            for y in (-48.0, 48.0):
                cutters.append(cyl((x, y, z0 - 1), (x, y, z1 + 1), P.M3_CLEARANCE_MM / 2.0))
    elif role == "upper":
        for x in (-33.0, 33.0):
            for y in (-17.0, 17.0):
                cutters.append(cyl((x, y, z0 - 1), (x, y, z1 + 1), P.M3_CLEARANCE_MM / 2.0))
    return cut_many(shape, cutters)


def battery_cradle() -> cq.Shape:
    half_x = P.BATTERY_INNER_MM[0] / 2.0 + P.BATTERY_WALL_MM
    half_y = P.BATTERY_INNER_MM[1] / 2.0 + P.BATTERY_WALL_MM
    base = P.BATTERY_BASE_Z_MM
    floor_top = base + P.BATTERY_FLOOR_MM
    positives = [
        box(-half_x, half_x, -half_y, -20, base, floor_top),
        box(-half_x, half_x, 20, half_y, base, floor_top),
        box(-half_x, -half_x + 6, -20, 20, base, floor_top),
        box(half_x - 6, half_x, -20, 20, base, floor_top),
        box(-60, -50, -half_y, half_y, base, floor_top),
        box(-5, 5, -half_y, half_y, base, floor_top),
        box(50, 60, -half_y, half_y, base, floor_top),
        box(-half_x, half_x, 23, half_y, floor_top, P.BATTERY_CRADLE_TOP_Z_MM),
        box(-half_x, half_x, -half_y, -23, floor_top, P.BATTERY_CRADLE_TOP_Z_MM),
        box(-half_x, -half_x + 3, -23, 23, floor_top, floor_top + 12),
        box(half_x - 3, half_x, -23, 23, floor_top, floor_top + 12),
        box(-half_x, half_x, half_y, half_y + 6, base, floor_top),
        box(-half_x, half_x, -half_y - 6, -half_y, base, floor_top),
    ]
    shape = fuse(positives)
    cutters: list[cq.Shape] = []
    for x0, x1 in ((-68, -24), (-18, 18), (24, 68)):
        cutters.append(box(x0, x1, 22, half_y + 1, floor_top + 6, P.BATTERY_CRADLE_TOP_Z_MM - 6))
        cutters.append(box(x0, x1, -half_y - 1, -22, floor_top + 6, P.BATTERY_CRADLE_TOP_Z_MM - 6))
    for x in (-55.0, 55.0):
        for y in (-half_y - 3.0, half_y + 3.0):
            cutters.append(
                slot_xy(
                    x,
                    y,
                    P.BATTERY_MOUNT_SLOT_LENGTH_MM,
                    P.M3_SLOT_WIDTH_MM,
                    "x",
                    base - 1,
                    floor_top + 1,
                )
            )
    for x in (-45.0, 45.0):
        for y in (-23.0, 23.0):
            cutters.append(
                slot_xy(
                    x,
                    y,
                    P.BATTERY_STRAP_SLOT_LENGTH_MM,
                    P.BATTERY_STRAP_SLOT_WIDTH_MM,
                    "x",
                    base - 1,
                    floor_top + 1,
                )
            )
    cutters.append(box(-half_x - 1, -half_x + 4, -12, 12, floor_top + 2, floor_top + 13))
    return cut_many(shape, cutters)


def electronics_deck() -> cq.Shape:
    z0, z1 = P.ELECTRONICS_DECK_Z_MM
    outer = box(-76, 76, -60, 60, z0, z1)
    inner = box(-68, 68, -52, 52, z0 - 1, z1 + 1)
    perimeter = outer.cut(inner)
    rails = [
        box(-68, 68, -3, 3, z0, z1),
        box(-62, -46, -52, 52, z0, z1),
        box(-2, 4, -52, 52, z0, z1),
        box(62, 68, -52, 52, z0, z1),
        box(9, 72, 15, 20, z0, z1 + 2),
        box(9, 72, 34, 39, z0, z1 + 2),
        box(18, 52, -42, -24, z0, z1),
        box(52, 68, -36, -30, z0, z1),
        box(-61, -33, 30, 58, z0, z1),
        box(-17, 8, 34, 58, z0, z1),
        box(15, 42, 39, 58, z0, z1),
    ]
    shape = fuse([perimeter, *rails])
    cutters: list[cq.Shape] = []
    # Pololu 2507 diagonal mounting-hole relation, with X slots for board-revision tolerance.
    for x, y in ((-57.5, -21.59), (-49.88, 21.59)):
        cutters.append(slot_xy(x, y, 8.0, P.M3_SLOT_WIDTH_MM, "x", z0 - 1, z1 + 3))
    # TX800 exact 20 x 20 mm M3 pattern.
    tx, ty, _ = P.TX800_CENTER_MM
    for dx in (-10.0, 10.0):
        for dy in (-10.0, 10.0):
            cutters.append(cyl((tx + dx, ty + dy, z0 - 1), (tx + dx, ty + dy, z1 + 2), P.M3_CLEARANCE_MM / 2.0))
    # Deck-to-crossmember mounts.
    for x in (-68.0, 68.0):
        for y in (-48.0, 48.0):
            cutters.append(cyl((x, y, z0 - 1), (x, y, z1 + 3), P.M3_CLEARANCE_MM / 2.0))
    # Teensy, BEC and RP3 restraint slots; purchased straps/soft ties own preload.
    for x in (24.0, 57.0):
        cutters.append(slot_xy(x, 17.5, 12.0, 3.2, "x", z0 - 1, z1 + 3))
        cutters.append(slot_xy(x, 36.5, 12.0, 3.2, "x", z0 - 1, z1 + 3))
    for x in (-12.0, 2.0, 20.0, 36.0):
        cutters.append(slot_xy(x, 47.0, 8.0, 3.2, "x", z0 - 1, z1 + 3))
    return cut_many(shape, cutters)


def imu_datum() -> cq.Shape:
    cx, cy, _ = P.IMU_CENTER_MM
    z0, z1 = 158.0, 161.0
    plate = box(cx - 17, cx + 17, cy - 14, cy + 14, z0, z1)
    shape = plate
    cutters: list[cq.Shape] = []
    for dx in (-10.0, 10.0):
        for dy in (-7.0, 7.0):
            cutters.append(slot_xy(cx + dx, cy + dy, 5.0, 2.8, "x", z0 - 1, z1 + 1))
    for dx in (-14.0, 14.0):
        cutters.append(cyl((cx + dx, cy, z0 - 1), (cx + dx, cy, z1 + 1), P.M3_CLEARANCE_MM / 2.0))
    return cut_many(shape, cutters)


def power_service_panel() -> cq.Shape:
    y0, y1 = P.POWER_PANEL_Y_MM - 2.0, P.POWER_PANEL_Y_MM + 2.0
    panel = box(-73, 43, y0, y1, 113, 147)
    shape = panel
    cutters: list[cq.Shape] = []
    # Large lightening/service window between the protected end zones.
    cutters.append(box(-18, 4, y0 - 1, y1 + 1, 119, 141))
    # XT60E-M provisional panel opening and screw pitch.
    cut_x, cut_z = P.XT60_PANEL_CUTOUT_MM_PROVISIONAL
    xt_x, _, xt_z = P.XT60_CENTER_MM
    cutters.append(box(xt_x - cut_x / 2, xt_x + cut_x / 2, y0 - 1, y1 + 1, xt_z - cut_z / 2, xt_z + cut_z / 2))
    for dx in (-P.XT60_MOUNT_PITCH_MM_PROVISIONAL / 2.0, P.XT60_MOUNT_PITCH_MM_PROVISIONAL / 2.0):
        cutters.append(cyl((xt_x + dx, y0 - 1, xt_z), (xt_x + dx, y1 + 1, xt_z), 1.4))
    # Fuse-holder strap slots.
    for x in (-62.0, -24.0):
        cutters.append(slot_xz_through_y(x, 121.0, 9.0, 3.2, y0 - 1, y1 + 1))
        cutters.append(slot_xz_through_y(x, 139.0, 9.0, 3.2, y0 - 1, y1 + 1))
    # Panel-to-frame fasteners.
    for x in (-68.0, 38.0):
        for z in (117.0, 143.0):
            cutters.append(cyl((x, y0 - 1, z), (x, y1 + 1, z), P.M3_CLEARANCE_MM / 2.0))
    return cut_many(shape, cutters)


def camera_guard() -> cq.Shape:
    # Side cheeks define 21 mm clear width around the 19 mm camera body.
    cheeks = [
        box(58, 91, -13.5, -10.5, 124, 155),
        box(58, 91, 10.5, 13.5, 124, 155),
    ]
    rear = box(58, 63, -18, 18, 120, 158).cut(box(56, 65, -9.5, 9.5, 129, 149))
    front = box(91, 95, -18, 18, 120, 158).cut(box(90, 96, -9.5, 9.5, 129, 149))
    rails = [
        box(61, 93, -18, -11, 120, 126),
        box(61, 93, 11, 18, 120, 126),
        box(61, 93, -18, -11, 152, 158),
        box(61, 93, 11, 18, 152, 158),
        box(54, 64, -24, -12, 114, 122),
        box(54, 64, 12, 24, 114, 122),
    ]
    shape = fuse([*cheeks, rear, front, *rails])
    cutters = [
        slot_xz_through_y(
            P.CAMERA_CENTER_MM[0],
            P.CAMERA_CENTER_MM[2],
            P.CAMERA_MOUNT_SLOT_LENGTH_MM,
            P.CAMERA_MOUNT_HOLE_MM_PROVISIONAL,
            -15,
            15,
        )
    ]
    for y in (-18.0, 18.0):
        cutters.append(cyl((56, y, 112), (56, y, 124), P.M3_CLEARANCE_MM / 2.0))
    return cut_many(shape, cutters)


def landing_part(front: bool) -> cq.Shape:
    sign = 1.0 if front else -1.0
    x_tip0, x_tip1 = sign * 80.0, sign * P.LANDING_TIP_X_MM
    x_mount0, x_mount1 = sign * 48.0, sign * 66.0
    shape = fuse(
        [
            box(x_tip0, x_tip1, -63, 63, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
            box(x_mount0, x_tip0, -60, -50, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
            box(x_mount0, x_tip0, 50, 60, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
            box(x_mount0, x_mount1, -P.SIDE_FRAME_OUTER_Y_MM, -58, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
            box(x_mount0, x_mount1, 58, P.SIDE_FRAME_OUTER_Y_MM, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
        ]
    )
    cutters = [
        cyl(
            (sign * 58.0, side * P.SIDE_FRAME_Y_MM, P.LANDING_BOTTOM_Z_MM - 1),
            (sign * 58.0, side * P.SIDE_FRAME_Y_MM, P.LANDING_TOP_Z_MM + 1),
            P.M3_CLEARANCE_MM / 2.0,
        )
        for side in (-1, 1)
    ]
    return cut_many(shape, cutters)


def antenna_guide(side: int) -> cq.Shape:
    if side not in (-1, 1):
        raise ValueError("side must be -1 or +1")
    y0 = side * P.SIDE_FRAME_OUTER_Y_MM
    y1 = side * 81.0
    base = box(-9, 9, y0, y1, 174, 184)
    cy = side * 78.0
    sleeve = cyl((0, cy, 180), (0, cy, 188), 4.0)
    bore = cyl((0, cy, 179), (0, cy, 189), 2.0)
    fastener = cyl((0, y0 - side, 179), (0, y1 + side, 179), P.M3_CLEARANCE_MM / 2.0)
    return fuse([base, sleeve]).cut(bore).cut(fastener)


def ballast_cassette() -> cq.Shape:
    hx = P.BALLAST_OUTER_MM[0] / 2.0
    hy = P.BALLAST_OUTER_MM[1] / 2.0
    z0, z1 = P.BALLAST_BODY_Z0_MM, P.BALLAST_BODY_Z1_MM
    outer = box(-hx, hx, -hy, hy, z0, z1)
    inner = box(
        -hx + P.BALLAST_WALL_MM,
        hx - P.BALLAST_WALL_MM,
        -hy + P.BALLAST_WALL_MM,
        hy - P.BALLAST_WALL_MM,
        z0 + P.BALLAST_WALL_MM,
        z1 + 1,
    )
    shape = outer.cut(inner)
    bosses = [
        cyl((x, y, z0), (x, y, z1), 4.5)
        for x in (-P.BALLAST_FASTENER_X_MM, P.BALLAST_FASTENER_X_MM)
        for y in (-P.BALLAST_FASTENER_Y_MM, P.BALLAST_FASTENER_Y_MM)
    ]
    shape = fuse([shape, *bosses])
    cutters = [
        cyl((x, y, z0 - 1), (x, y, z1 + 1), P.M3_CLEARANCE_MM / 2.0)
        for x in (-P.BALLAST_FASTENER_X_MM, P.BALLAST_FASTENER_X_MM)
        for y in (-P.BALLAST_FASTENER_Y_MM, P.BALLAST_FASTENER_Y_MM)
    ]
    return cut_many(shape, cutters)


def ballast_lid() -> cq.Shape:
    hx = P.BALLAST_OUTER_MM[0] / 2.0
    hy = P.BALLAST_OUTER_MM[1] / 2.0
    shape = box(-hx, hx, -hy, hy, P.BALLAST_BODY_Z1_MM, P.BALLAST_LID_Z1_MM)
    cutters = [
        cyl((x, y, P.BALLAST_BODY_Z1_MM - 1), (x, y, P.BALLAST_LID_Z1_MM + 1), P.M3_CLEARANCE_MM / 2.0)
        for x in (-P.BALLAST_FASTENER_X_MM, P.BALLAST_FASTENER_X_MM)
        for y in (-P.BALLAST_FASTENER_Y_MM, P.BALLAST_FASTENER_Y_MM)
    ]
    return cut_many(shape, cutters)


def wheel_proxy(side: int) -> cq.Shape:
    centre = side * P.WHEEL_CENTER_Y_MM
    return cyl(
        (0, centre - P.WHEEL_WIDTH_MM / 2.0, 0),
        (0, centre + P.WHEEL_WIDTH_MM / 2.0, 0),
        P.WHEEL_RADIUS_MM,
    )


def motor_proxy(side: int) -> cq.Shape:
    face = side * P.MOTOR_OUTPUT_FACE_Y_MM_PROVISIONAL
    inner = side * P.MOTOR_BODY_INNER_Y_MM_PROVISIONAL
    body = cyl((0, inner, 0), (0, face, 0), P.MOTOR_BODY_RADIUS_MM)
    shaft_end = side * (P.MOTOR_OUTPUT_FACE_Y_MM_PROVISIONAL + P.MOTOR_SHAFT_LENGTH_MM)
    shaft = cyl((0, face, 0), (0, shaft_end, 0), P.MOTOR_SHAFT_RADIUS_MM)
    adapter_end = side * (P.MOTOR_OUTPUT_FACE_Y_MM_PROVISIONAL + P.WHEEL_ADAPTER_LENGTH_MM)
    adapter = cyl((0, face, 0), (0, adapter_end, 0), P.WHEEL_ADAPTER_RADIUS_PROXY_MM)
    return fuse([body, shaft, adapter])


def bracket_proxy(side: int) -> cq.Shape:
    centre = side * P.MOTOR_BRACKET_CENTER_Y_MM
    y0 = centre - side * 6.25
    y1 = centre + side * 6.25
    plate = box(-18.4, 18.4, y0, y1, -18.0, 18.8)
    opening = cyl((0, min(y0, y1) - 1, 0), (0, max(y0, y1) + 1, 0), P.MOTOR_BODY_RADIUS_MM + 0.4)
    base = box(-18.4, 18.4, y0, y1, -18.8, -14.0)
    return fuse([plate.cut(opening), base])


def centered_box(center: tuple[float, float, float], size: tuple[float, float, float]) -> cq.Solid:
    cx, cy, cz = center
    sx, sy, sz = size
    return box(cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2, cz - sz / 2, cz + sz / 2)


def battery_proxy() -> cq.Shape:
    return centered_box((0.0, 0.0, P.BATTERY_CENTER_Z_MM), P.BATTERY_SIZE_MM_PROVISIONAL)


def camera_proxy() -> cq.Shape:
    body = centered_box(P.CAMERA_CENTER_MM, P.CAMERA_SIZE_MM)
    cx, cy, cz = P.CAMERA_CENTER_MM
    lens = cyl(
        (cx + P.CAMERA_SIZE_MM[0] / 2.0 - 1.0, cy, cz),
        (cx + P.CAMERA_SIZE_MM[0] / 2.0 + P.CAMERA_LENS_PROTRUSION_MM_PROVISIONAL, cy, cz),
        P.CAMERA_LENS_RADIUS_MM_PROVISIONAL,
    )
    return fuse([body, lens])


def printed_parts() -> dict[str, Part]:
    structural = (0.22, 0.27, 0.34, 1.0)
    accent = (1.0, 0.31, 0.03, 1.0)
    service = (0.18, 0.34, 0.42, 1.0)
    return {
        "side-frame-left": Part("side-frame-left", side_frame(1), "CHASSIS", P.MATERIAL, structural, "rotate +90 deg about X; outer face on bed", "frame datum; Pololu 4755 body clearance is provisional"),
        "side-frame-right": Part("side-frame-right", side_frame(-1), "CHASSIS", P.MATERIAL, structural, "rotate +90 deg about X; outer face on bed", "frame datum; Pololu 4755 body clearance is provisional"),
        "axle-crossmember": Part("axle-crossmember", axle_crossmember(), "CHASSIS", P.MATERIAL, structural, "native -Z face on bed", "common axle structural datum"),
        "motor-pod-left": Part("motor-pod-left", motor_pod(1), "MOTOR_POD", P.MATERIAL, structural, "native -Z face on bed", "Pololu 1995 bracket base; slots remain sample-owned"),
        "motor-pod-right": Part("motor-pod-right", motor_pod(-1), "MOTOR_POD", P.MATERIAL, structural, "native -Z face on bed", "Pololu 1995 bracket base; slots remain sample-owned"),
        "battery-crossmember": Part("battery-crossmember", frame_crossmember(*P.BATTERY_CROSSMEMBER_Z_MM, "battery"), "CHASSIS", P.MATERIAL, structural, "native -Z face on bed", "sliding cradle datum"),
        "electronics-crossmember": Part("electronics-crossmember", frame_crossmember(*P.ELECTRONICS_CROSSMEMBER_Z_MM, "electronics"), "CHASSIS", P.MATERIAL, structural, "native -Z face on bed", "electronics deck datum"),
        "upper-crossmember": Part("upper-crossmember", frame_crossmember(*P.UPPER_CROSSMEMBER_Z_MM, "upper"), "CHASSIS", P.MATERIAL, structural, "native -Z face on bed", "ballast cassette through-bolt datum"),
        "battery-cradle": Part("battery-cradle", battery_cradle(), "BATTERY", P.MATERIAL, structural, "native base on bed", "Gens ace GEA503S60X6GT retailer envelope plus straps"),
        "electronics-deck": Part("electronics-deck", electronics_deck(), "ELECTRONICS", P.MATERIAL, service, "native -Z face on bed", "Pololu 2507, Teensy 4.1, TX800, RP3 and BEC footprints"),
        "imu-datum": Part("imu-datum", imu_datum(), "IMU", P.MATERIAL, accent, "native -Z face on bed", "Adafruit 4502 adjustable rigid datum; exact carrier holes pending"),
        "power-service-panel": Part("power-service-panel", power_service_panel(), "POWER", P.MATERIAL, service, "rotate +90 deg about X; broad face on bed", "XT60E-M and ATO-FKH fit coupon required"),
        "camera-guard": Part("camera-guard", camera_guard(), "CAMERA", "orange PETG candidate", accent, "rotate -90 deg about Y; front hoop on bed", "RunCam Phoenix 2 SE V2 19 mm body; side screw slot pending sample"),
        "landing-front": Part("landing-front", landing_part(True), "LANDING", "orange PETG candidate", accent, "native flat underside on bed", "non-rolling sacrificial landing load path"),
        "landing-rear": Part("landing-rear", landing_part(False), "LANDING", "orange PETG candidate", accent, "native flat underside on bed", "non-rolling sacrificial landing load path"),
        "antenna-guide-left": Part("antenna-guide-left", antenna_guide(1), "RADIO", "orange PETG/TPU candidate", accent, "rotate +90 deg about X; broad face on bed", "RP3 antenna active element keep-out pending sample"),
        "antenna-guide-right": Part("antenna-guide-right", antenna_guide(-1), "RADIO", "orange PETG/TPU candidate", accent, "rotate +90 deg about X; broad face on bed", "RP3 antenna active element keep-out pending sample"),
        "ballast-cassette": Part("ballast-cassette", ballast_cassette(), "TRIM", P.MATERIAL, structural, "native -Z face on bed", "closed steel-segment cassette; exact mass measurement-owned"),
        "ballast-lid": Part("ballast-lid", ballast_lid(), "TRIM", P.MATERIAL, accent, "native top face inverted onto bed", "four M3 through-bolts; adhesive is non-structural"),
    }


def cots_parts() -> dict[str, Part]:
    black = (0.04, 0.045, 0.055, 1.0)
    metal = (0.48, 0.50, 0.54, 1.0)
    battery = (0.14, 0.15, 0.18, 1.0)
    pcb = (0.02, 0.24, 0.13, 1.0)
    orange = (0.85, 0.20, 0.02, 1.0)
    result = {
        "wheel-left-proxy": Part("wheel-left-proxy", wheel_proxy(1), "WHEEL", "COTS PROXY", black, "not printable", "INJORA 120 x 42 rotating envelope"),
        "wheel-right-proxy": Part("wheel-right-proxy", wheel_proxy(-1), "WHEEL", "COTS PROXY", black, "not printable", "INJORA 120 x 42 rotating envelope"),
        "motor-left-proxy": Part("motor-left-proxy", motor_proxy(1), "DRIVE", "COTS PROXY", metal, "not printable", "Pololu 4755/2686 declared envelope"),
        "motor-right-proxy": Part("motor-right-proxy", motor_proxy(-1), "DRIVE", "COTS PROXY", metal, "not printable", "Pololu 4755/2686 declared envelope"),
        "bracket-left-proxy": Part("bracket-left-proxy", bracket_proxy(1), "DRIVE", "COTS PROXY", metal, "not printable", "Pololu 1995 simplified reference"),
        "bracket-right-proxy": Part("bracket-right-proxy", bracket_proxy(-1), "DRIVE", "COTS PROXY", metal, "not printable", "Pololu 1995 simplified reference"),
        "battery-proxy": Part("battery-proxy", battery_proxy(), "POWER", "COTS PROXY", battery, "not printable", "Gens ace retailer envelope"),
        "driver-proxy": Part("driver-proxy", centered_box(P.DRIVER_CENTER_MM, P.DRIVER_SIZE_MM), "CONTROL", "COTS PROXY", pcb, "not printable", "Pololu 2507 board envelope"),
        "teensy-proxy": Part("teensy-proxy", centered_box(P.TEENSY_CENTER_MM, P.TEENSY_SIZE_MM), "CONTROL", "COTS PROXY", pcb, "not printable", "PJRC Teensy 4.1 envelope"),
        "imu-proxy": Part("imu-proxy", centered_box(P.IMU_CENTER_MM, P.IMU_SIZE_MM_PROVISIONAL), "CONTROL", "COTS PROXY", pcb, "not printable", "Adafruit 4502 provisional carrier envelope"),
        "tx800-proxy": Part("tx800-proxy", centered_box(P.TX800_CENTER_MM, P.TX800_SIZE_MM), "FPV", "COTS PROXY", pcb, "not printable", "SpeedyBee TX800 envelope"),
        "rp3-proxy": Part("rp3-proxy", centered_box(P.RP3_CENTER_MM, P.RP3_SIZE_MM), "RADIO", "COTS PROXY", pcb, "not printable", "RadioMaster RP3 V2 envelope"),
        "bec-proxy": Part("bec-proxy", centered_box(P.BEC_CENTER_MM, P.BEC_SIZE_MM), "POWER", "COTS PROXY", pcb, "not printable", "Pololu D24V50F5 envelope"),
        "camera-proxy": Part("camera-proxy", camera_proxy(), "FPV", "COTS PROXY", black, "not printable", "RunCam Phoenix 2 SE V2 envelope"),
        "fuse-holder-proxy": Part("fuse-holder-proxy", centered_box(P.FUSE_HOLDER_CENTER_MM, P.FUSE_HOLDER_ENVELOPE_MM_PROVISIONAL), "POWER", "COTS PROXY", black, "not printable", "Littelfuse ATO-FKH provisional body envelope"),
        "xt60-proxy": Part("xt60-proxy", centered_box(P.XT60_CENTER_MM, P.XT60_ENVELOPE_MM_PROVISIONAL), "POWER", "COTS PROXY", orange, "not printable", "AMASS XT60E-M provisional envelope"),
    }
    for side in (-1, 1):
        y = side * 78.0
        antenna = cyl((0, y, 181), (0, y, 188), 1.5)
        name = "antenna-left-proxy" if side == 1 else "antenna-right-proxy"
        result[name] = Part(name, antenna, "RADIO", "COTS PROXY", black, "not printable", "RP3 V2 antenna routing proxy")
    return result


def assembly() -> cq.Assembly:
    result = cq.Assembly(name=f"{P.PROJECT_ID}-{P.CANDIDATE}")
    for part in [*printed_parts().values(), *cots_parts().values()]:
        result.add(part.shape, name=part.name, color=cq.Color(*part.color))
    return result


def shape_bounds(shape: cq.Shape) -> dict[str, list[float]]:
    bb = shape.BoundingBox()
    return {
        "min_mm": [bb.xmin, bb.ymin, bb.zmin],
        "max_mm": [bb.xmax, bb.ymax, bb.zmax],
        "size_mm": [bb.xlen, bb.ylen, bb.zlen],
    }


def orient_mesh_for_print(part: Part) -> cq.Shape:
    shape = part.shape
    if part.name.startswith("side-frame") or part.name.startswith("antenna-guide") or part.name == "power-service-panel":
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    elif part.name == "camera-guard":
        shape = shape.rotate((0, 0, 0), (0, 1, 0), -90)
    elif part.name == "ballast-lid":
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = shape.BoundingBox()
    return shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_all() -> dict[str, object]:
    for directory in (STEP_DIR, MESH_DIR, ASSEMBLY_MESH_DIR, PREVIEW_DIR, VALIDATION_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    printed = printed_parts()
    cots = cots_parts()
    artifacts: list[dict[str, object]] = []
    for part in printed.values():
        step_path = STEP_DIR / f"DRAFT-{part.name}.step"
        stl_path = MESH_DIR / f"DRAFT-{part.name}.stl"
        assembly_mesh_path = ASSEMBLY_MESH_DIR / f"DRAFT-{part.name}-assembly.stl"
        cq.exporters.export(part.shape, str(step_path), exportType="STEP")
        cq.exporters.export(
            orient_mesh_for_print(part),
            str(stl_path),
            exportType="STL",
            tolerance=P.STL_LINEAR_TOLERANCE_MM,
            angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
        )
        cq.exporters.export(
            part.shape,
            str(assembly_mesh_path),
            exportType="STL",
            tolerance=P.STL_LINEAR_TOLERANCE_MM,
            angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
        )
        for path, kind in (
            (step_path, "step_master"),
            (stl_path, "draft_manufacturing_mesh"),
            (assembly_mesh_path, "assembly_validation_mesh"),
        ):
            artifacts.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "kind": kind,
                    "sha256": sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    for part in cots.values():
        path = ASSEMBLY_MESH_DIR / f"DRAFT-{part.name}-assembly.stl"
        cq.exporters.export(
            part.shape,
            str(path),
            exportType="STL",
            tolerance=P.STL_LINEAR_TOLERANCE_MM,
            angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
        )
        artifacts.append(
            {
                "path": str(path.relative_to(ROOT)),
                "kind": "cots_registration_proxy",
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )

    printed_compound = cq.Compound.makeCompound([part.shape for part in printed.values()])
    printed_mesh = ASSEMBLY_MESH_DIR / "DRAFT-printed-assembly.stl"
    cq.exporters.export(
        printed_compound,
        str(printed_mesh),
        exportType="STL",
        tolerance=P.STL_LINEAR_TOLERANCE_MM,
        angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
    )
    artifacts.append(
        {
            "path": str(printed_mesh.relative_to(ROOT)),
            "kind": "printed_assembly_validation_mesh",
            "sha256": sha256(printed_mesh),
            "size_bytes": printed_mesh.stat().st_size,
        }
    )

    asm = assembly()
    assembly_step = STEP_DIR / "DRAFT-trailcam-b2-component-assembly.step"
    assembly_glb = PREVIEW_DIR / f"DRAFT-trailcam-b2-assembly-v{P.CANDIDATE}.glb"
    asm.save(str(assembly_step), exportType="STEP", mode="default")
    asm.save(str(assembly_glb), exportType="GLTF", mode="default", tolerance=0.2, angularTolerance=0.2)
    for path, kind in ((assembly_step, "assembly_step"), (assembly_glb, "assembly_preview")):
        artifacts.append(
            {
                "path": str(path.relative_to(ROOT)),
                "kind": kind,
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )

    report = {
        "schema_version": "1.0",
        "project_id": P.PROJECT_ID,
        "revision": P.REVISION,
        "candidate": P.CANDIDATE,
        "bom_candidate": P.BOM_CANDIDATE,
        "status": "DRAFT",
        "tool": "CadQuery",
        "tool_version": importlib.metadata.version("cadquery"),
        "coordinate_frame": {
            "origin": "common wheel axis at vehicle centre",
            "x": "forward",
            "y": "left / axle",
            "z": "up",
        },
        "tessellation": {
            "linear_tolerance_mm": P.STL_LINEAR_TOLERANCE_MM,
            "angular_tolerance_rad": P.STL_ANGULAR_TOLERANCE_RAD,
            "mesh_simplification": "not applied; direct analytic B-Rep tessellation",
        },
        "printed_parts": [
            {
                "name": part.name,
                "group": part.group,
                "material": part.material,
                "print_orientation": part.print_orientation,
                "interface_authority": part.interface_authority,
                "bounds_assembly": shape_bounds(part.shape),
                "volume_mm3": part.shape.Volume(),
                "solid_petg_mass_estimate_g": part.shape.Volume() * P.PETG_DENSITY_G_PER_MM3,
            }
            for part in printed.values()
        ],
        "cots_registration_proxies": [
            {"name": part.name, "authority": part.interface_authority, "bounds": shape_bounds(part.shape)}
            for part in cots.values()
        ],
        "artifacts": artifacts,
        "limitations": [
            "COTS registration geometry is derived from manufacturer or named-retailer declarations and is not delivered-part inspection evidence.",
            "All STL files are DRAFT manufacturing candidates; no final release or watermark approval is implied.",
            "No complete Anycubic machine/process/filament profile set exists, so no 3MF or G-code is generated.",
            "Motor-pod, wheel-stack, IMU, XT60, fuse-holder and camera screw interfaces require process-matched coupons and delivered-part measurements.",
            "Printed solid-density mass is a conservative CAD comparison, not a slicer material estimate.",
        ],
    }
    report_path = VALIDATION_DIR / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = export_all()
    print(
        json.dumps(
            {
                "status": result["status"],
                "candidate": result["candidate"],
                "printed_parts": len(result["printed_parts"]),
                "artifacts": len(result["artifacts"]),
            },
            indent=2,
        )
    )
