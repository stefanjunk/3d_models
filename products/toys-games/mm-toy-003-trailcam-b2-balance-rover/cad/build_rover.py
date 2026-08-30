"""Build and export the MM-TOY-003 TrailCam B2 parametric DRAFT assembly.

Critical printed geometry is deterministic CadQuery B-Rep. Purchased parts are
explicitly named planning proxies. Individual STEP files preserve assembly
coordinates; validation STL files are reoriented to a documented flat printing
face and are not manufacturing-release meshes.
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
from typing import Callable

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import parameters as P

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


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Solid:
    xa, xb = sorted((x0, x1))
    ya, yb = sorted((y0, y1))
    za, zb = sorted((z0, z1))
    return cq.Solid.makeBox(xb - xa, yb - ya, zb - za, pnt=(xa, ya, za))


def cyl(p0: tuple[float, float, float], p1: tuple[float, float, float], radius: float) -> cq.Solid:
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
        [(x0 + px, z0 + pz), (x1 + px, z1 + pz),
         (x1 - px, z1 - pz), (x0 - px, z0 - pz)],
        y0,
        y1,
    )


def side_frame(side: int) -> cq.Shape:
    if side not in (-1, 1):
        raise ValueError("side must be -1 or +1")
    yc = side * P.SIDE_FRAME_Y_MM
    y0, y1 = yc - P.SIDE_FRAME_THICKNESS_MM / 2.0, yc + P.SIDE_FRAME_THICKNESS_MM / 2.0
    bars = [
        bar_xz((-72, -12), (72, -12), P.BAR_MAIN_MM, y0, y1),
        bar_xz((-72, -12), (-58, 142), P.BAR_MAIN_MM, y0, y1),
        bar_xz((72, -12), (58, 150), P.BAR_MAIN_MM, y0, y1),
        bar_xz((-58, 142), (0, 172), P.BAR_MAIN_MM, y0, y1),
        bar_xz((0, 172), (58, 150), P.BAR_MAIN_MM, y0, y1),
        bar_xz((0, -12), (0, 168), P.BAR_MAIN_MM, y0, y1),
        bar_xz((-50, 66), (50, 66), P.BAR_SECONDARY_MM, y0, y1),
        bar_xz((-50, 118), (60, 118), P.BAR_SECONDARY_MM, y0, y1),
        bar_xz((-48, 66), (0, 118), P.BAR_BRACE_MM, y0, y1),
        bar_xz((48, 66), (0, 118), P.BAR_BRACE_MM, y0, y1),
    ]
    frame = fuse(bars)
    cutters: list[cq.Shape] = []
    for x, z in ((-20, -12), (20, -12), (-40, 66), (40, 66), (-40, 118), (40, 118), (0, 172)):
        cutters.append(cyl((x, y0 - 2, z), (x, y1 + 2, z), P.M3_CLEARANCE_MM / 2.0))
    cutters.append(cyl((0, y0 - 2, 0), (0, y1 + 2, 0), P.MOTOR_SHAFT_FRAME_CLEARANCE_MM / 2.0))
    for x in (-55.0, 55.0):
        cutters.append(cyl((x, yc, -24), (x, yc, 0), P.M3_CLEARANCE_MM / 2.0))
    return cut_many(frame, cutters)


def insert_pilot_y(x: float, side: int, z: float) -> cq.Solid:
    y_end = side * P.CROSSMEMBER_END_Y_MM
    return cyl(
        (x, y_end + side * 1.0, z),
        (x, y_end - side * P.M3_INSERT_DEPTH_MM, z),
        P.M3_INSERT_PILOT_MM / 2.0,
    )


def axle_crossmember() -> cq.Shape:
    end = P.CROSSMEMBER_END_Y_MM
    deck = box(-38, 38, -end, end, -26, -20)
    end_risers = [
        box(-30, 30, side * (end - 8), side * end, -20.5, -4)
        for side in (-1, 1)
    ]
    shape = fuse([deck, *end_risers])
    cutters: list[cq.Shape] = []
    for side in (-1, 1):
        for x in (-20.0, 20.0):
            cutters.append(insert_pilot_y(x, side, -12.0))
        center = side * P.MOTOR_BRACKET_CENTER_Y_MM
        for offset in (-P.MOTOR_BRACKET_BOTTOM_PITCH_MM, 0.0, P.MOTOR_BRACKET_BOTTOM_PITCH_MM):
            y = center + side * offset
            cutters.append(cyl((0, y, -28), (0, y, -18), P.M3_CLEARANCE_MM / 2.0))
    return cut_many(shape, cutters)


def battery_crossmember() -> cq.Shape:
    end = P.CROSSMEMBER_END_Y_MM
    z0, z1 = 62.0, 68.0
    positives = [
        box(-46, -34, -end, end, z0, z1),
        box(34, 46, -end, end, z0, z1),
        box(-35, 35, -30, -22, z0, z1),
        box(-35, 35, 22, 30, z0, z1),
    ]
    shape = fuse(positives)
    cutters = [insert_pilot_y(x, side, 66.0) for side in (-1, 1) for x in (-40.0, 40.0)]
    return cut_many(shape, cutters)


def upper_crossmember() -> cq.Shape:
    end = P.CROSSMEMBER_END_Y_MM
    z0, z1 = 114.0, 120.0
    positives = [
        box(-46, -34, -end, end, z0, z1),
        box(34, 46, -end, end, z0, z1),
        box(-35, 35, -40, -32, z0, z1),
        box(-35, 35, 32, 40, z0, z1),
        box(34, 62, -30, 30, z0, z1),
    ]
    shape = fuse(positives)
    cutters = [insert_pilot_y(x, side, 118.0) for side in (-1, 1) for x in (-40.0, 40.0)]
    for x, y in ((-40, -45), (-40, 45), (40, -45), (40, 45), (56, -18), (56, 18)):
        cutters.append(cyl((x, y, 112), (x, y, 122), P.M3_CLEARANCE_MM / 2.0))
    return cut_many(shape, cutters)


def rounded_slot_z(x: float, y: float, length_x: float, width: float, z0: float, z1: float) -> cq.Shape:
    half_straight = (length_x - width) / 2.0
    if half_straight < 0:
        raise ValueError("slot length must be at least its width")
    straight = box(x - half_straight, x + half_straight, y - width / 2, y + width / 2, z0, z1)
    ends = [
        cyl((x + sign * half_straight, y, z0), (x + sign * half_straight, y, z1), width / 2)
        for sign in (-1, 1)
    ]
    return fuse([straight, *ends])


def battery_cradle() -> cq.Shape:
    positives = [
        box(-50, 50, -31, 31, 70, 74),
        box(-50, 50, 26, 31, 74, 114),
        box(-50, 50, -31, -26, 74, 114),
        box(-50, -46, -26, 26, 74, 82),
        box(46, 50, -26, 26, 74, 82),
    ]
    shape = fuse(positives)
    cutters: list[cq.Shape] = []
    for x in (-30.0, 30.0):
        for y in (-23.0, 23.0):
            cutters.append(rounded_slot_z(x, y, 28.0, 4.2, 68.0, 76.0))
    for x in (-25.0, 25.0):
        cutters.append(box(x - 6, x + 6, -34, 34, 82, 104))
    return cut_many(shape, cutters)


def control_tray() -> cq.Shape:
    plate = box(-50, 50, -54, 54, P.CONTROL_TRAY_Z_MM, P.CONTROL_TRAY_Z_MM + 3.0)
    windows = []
    for x0, x1 in ((-42, -8), (8, 42)):
        for y0, y1 in ((-46, -8), (8, 46)):
            windows.append(box(x0, x1, y0, y1, P.CONTROL_TRAY_Z_MM - 1, P.CONTROL_TRAY_Z_MM + 4))
    shape = cut_many(plate, windows)
    bosses = []
    for x, y in ((-40, -45), (-40, 45), (40, -45), (40, 45)):
        bosses.append(cyl((x, y, P.CONTROL_TRAY_Z_MM), (x, y, P.CONTROL_TRAY_Z_MM + 7), 4.5))
    bosses.append(box(-15, 15, -15, 15, P.CONTROL_TRAY_Z_MM, P.CONTROL_TRAY_Z_MM + 7))
    shape = fuse([shape, *bosses])
    cutters = [
        cyl((x, y, P.CONTROL_TRAY_Z_MM - 1), (x, y, P.CONTROL_TRAY_Z_MM + 9), P.M3_CLEARANCE_MM / 2)
        for x, y in ((-40, -45), (-40, 45), (40, -45), (40, 45))
    ]
    return cut_many(shape, cutters)


def camera_guard() -> cq.Shape:
    outer_rear = box(58, 64, -25, 25, 120, 158)
    outer_front = box(82, 88, -25, 25, 120, 158)
    inner_rear = box(56, 66, -14, 14, 128, 151)
    inner_front = box(80, 90, -14, 14, 128, 151)
    rear_hoop = outer_rear.cut(inner_rear)
    front_hoop = outer_front.cut(inner_front)
    rails = [
        box(62, 84, -25, -18, 120, 127),
        box(62, 84, 18, 25, 120, 127),
        box(62, 84, -25, -18, 151, 158),
        box(62, 84, 18, 25, 151, 158),
        box(54, 64, -24, -12, 114, 122),
        box(54, 64, 12, 24, 114, 122),
    ]
    shape = fuse([rear_hoop, front_hoop, *rails])
    cutters = [
        cyl((56, y, 112), (56, y, 124), P.M3_CLEARANCE_MM / 2)
        for y in (-18.0, 18.0)
    ]
    return cut_many(shape, cutters)


def landing_part(front: bool) -> cq.Shape:
    sign = 1.0 if front else -1.0
    x_tip0, x_tip1 = sign * 80.0, sign * P.LANDING_TIP_X_MM
    x_mount0, x_mount1 = sign * 48.0, sign * 66.0
    positives = [
        box(x_tip0, x_tip1, -65, 65, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
        box(x_mount0, x_tip0, -62, -50, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
        box(x_mount0, x_tip0, 50, 62, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
        box(x_mount0, x_mount1, -P.SIDE_FRAME_OUTER_Y_MM, -60, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
        box(x_mount0, x_mount1, 60, P.SIDE_FRAME_OUTER_Y_MM, P.LANDING_BOTTOM_Z_MM, P.LANDING_TOP_Z_MM),
    ]
    shape = fuse(positives)
    cutters = [
        cyl((sign * 55.0, side * P.SIDE_FRAME_Y_MM, P.LANDING_BOTTOM_Z_MM - 1),
            (sign * 55.0, side * P.SIDE_FRAME_Y_MM, P.LANDING_TOP_Z_MM + 1),
            P.M3_CLEARANCE_MM / 2)
        for side in (-1, 1)
    ]
    return cut_many(shape, cutters)


def antenna_mount(side: int) -> cq.Shape:
    if side not in (-1, 1):
        raise ValueError("side must be -1 or +1")
    y0 = side * P.SIDE_FRAME_OUTER_Y_MM
    y1 = side * (P.SIDE_FRAME_OUTER_Y_MM + 8.0)
    base = box(-8, 8, y0, y1, 166, 178)
    centre_y = side * (P.SIDE_FRAME_OUTER_Y_MM + 5.0)
    sleeve = cyl((0, centre_y, 174), (0, centre_y, 184), 4.0)
    hole = cyl((0, centre_y, 172), (0, centre_y, 186), 2.0)
    fastener = cyl((0, y0 - side * 2, 172), (0, y1 + side * 2, 172), P.M3_CLEARANCE_MM / 2)
    return fuse([base, sleeve]).cut(hole).cut(fastener)


def wheel_proxy(side: int) -> cq.Shape:
    centre = side * P.WHEEL_CENTER_Y_MM
    y0 = centre - P.WHEEL_WIDTH_MM / 2.0
    y1 = centre + P.WHEEL_WIDTH_MM / 2.0
    return cyl((0, y0, 0), (0, y1, 0), P.WHEEL_RADIUS_MM)


def motor_proxy(side: int) -> cq.Shape:
    y_inner = side * P.MOTOR_BODY_INNER_Y_MM
    y_outer = side * P.MOTOR_BODY_OUTER_Y_MM
    body = cyl((0, y_inner, 0), (0, y_outer, 0), P.MOTOR_BODY_RADIUS_MM)
    shaft = cyl((0, y_outer, 0), (0, side * P.MOTOR_SHAFT_OUTER_Y_MM, 0), 3.0)
    return fuse([body, shaft])


def bracket_proxy(side: int) -> cq.Shape:
    centre = side * P.MOTOR_BRACKET_CENTER_Y_MM
    y0, y1 = centre - side * 17.0, centre + side * 17.0
    base = box(-22, 22, y0, y1, -20, -17)
    cheeks = [
        box(-22, -17, y0, y1, -20, 18),
        box(17, 22, y0, y1, -20, 18),
    ]
    return fuse([base, *cheeks])


def battery_proxy() -> cq.Shape:
    lx, ly, lz = P.BATTERY_ENVELOPE_MM
    cx, cy, cz = P.BATTERY_CENTER_MM
    return box(cx - lx / 2, cx + lx / 2, cy - ly / 2, cy + ly / 2, cz - lz / 2, cz + lz / 2)


def control_stack_proxy() -> cq.Shape:
    driver = box(-42.25, 42.25, -31, 31, 128, 133)
    controller = box(-31, 31, -10, 10, 139, 143)
    imu = box(-15, 15, -15, 15, 149, 153)
    spacers = [cyl((x, y, 133), (x, y, 139), 2.0) for x in (-25, 25) for y in (-8, 8)]
    return fuse([driver, controller, imu, *spacers])


def camera_proxy() -> cq.Shape:
    lx, ly, lz = P.CAMERA_ENVELOPE_MM
    cx, cy, cz = P.CAMERA_CENTER_MM
    body = box(cx - lx / 2, cx + lx / 2, cy - ly / 2, cy + ly / 2, cz - lz / 2, cz + lz / 2)
    lens = cyl((cx + lx / 2 - 1, 0, cz), (cx + lx / 2 + 7, 0, cz), 7.0)
    return fuse([body, lens])


def antenna_proxy(side: int) -> cq.Shape:
    y = side * (P.SIDE_FRAME_OUTER_Y_MM + 5.0)
    rod = cyl((0, y, 182), (0, y, 190), 1.5)
    cap = cyl((0, y, 188), (0, y, 190), 4.0)
    return fuse([rod, cap])


def printed_parts() -> dict[str, Part]:
    anthracite = (0.24, 0.28, 0.33, 1.0)
    orange = (1.0, 0.32, 0.03, 1.0)
    return {
        "side-frame-left": Part("side-frame-left", side_frame(1), "CHASSIS_SET", P.MATERIAL, anthracite, "rotate +90° about X; outside face on bed"),
        "side-frame-right": Part("side-frame-right", side_frame(-1), "CHASSIS_SET", P.MATERIAL, anthracite, "rotate +90° about X; outside face on bed"),
        "axle-crossmember": Part("axle-crossmember", axle_crossmember(), "CHASSIS_SET", P.MATERIAL, anthracite, "native -Z deck face on bed"),
        "battery-crossmember": Part("battery-crossmember", battery_crossmember(), "CHASSIS_SET", P.MATERIAL, anthracite, "native -Z face on bed"),
        "upper-crossmember": Part("upper-crossmember", upper_crossmember(), "CHASSIS_SET", P.MATERIAL, anthracite, "native -Z face on bed"),
        "battery-cradle": Part("battery-cradle", battery_cradle(), "BATTERY_CRADLE", P.MATERIAL, anthracite, "native base on bed"),
        "control-tray": Part("control-tray", control_tray(), "CONTROL_TRAY", P.MATERIAL, anthracite, "native base on bed"),
        "camera-guard": Part("camera-guard", camera_guard(), "CAMERA_GUARD", "orange PETG candidate", orange, "rotate -90° about Y; front hoop face on bed"),
        "landing-front": Part("landing-front", landing_part(True), "LANDING_SET", "orange PETG candidate", orange, "native flat underside on bed"),
        "landing-rear": Part("landing-rear", landing_part(False), "LANDING_SET", "orange PETG candidate", orange, "native flat underside on bed"),
        "antenna-mount-left": Part("antenna-mount-left", antenna_mount(1), "ANTENNA_SET", "orange PETG/TPU candidate", orange, "rotate to place broad side on bed; coupon required"),
        "antenna-mount-right": Part("antenna-mount-right", antenna_mount(-1), "ANTENNA_SET", "orange PETG/TPU candidate", orange, "rotate to place broad side on bed; coupon required"),
    }


def cots_parts() -> dict[str, Part]:
    black = (0.06, 0.065, 0.075, 1.0)
    metal = (0.45, 0.47, 0.50, 1.0)
    battery = (0.16, 0.17, 0.19, 1.0)
    pcb = (0.02, 0.24, 0.15, 1.0)
    return {
        "wheel-left-proxy": Part("wheel-left-proxy", wheel_proxy(1), "HUB_WHEEL_SET", "COTS PROXY", black, "not printable"),
        "wheel-right-proxy": Part("wheel-right-proxy", wheel_proxy(-1), "HUB_WHEEL_SET", "COTS PROXY", black, "not printable"),
        "motor-left-proxy": Part("motor-left-proxy", motor_proxy(1), "DRIVE_SET", "COTS PROXY", metal, "not printable"),
        "motor-right-proxy": Part("motor-right-proxy", motor_proxy(-1), "DRIVE_SET", "COTS PROXY", metal, "not printable"),
        "bracket-left-proxy": Part("bracket-left-proxy", bracket_proxy(1), "MOTOR_BRACKET_SET", "COTS PROXY", metal, "not printable"),
        "bracket-right-proxy": Part("bracket-right-proxy", bracket_proxy(-1), "MOTOR_BRACKET_SET", "COTS PROXY", metal, "not printable"),
        "battery-proxy": Part("battery-proxy", battery_proxy(), "BATTERY_COTS", "COTS PROXY", battery, "not printable"),
        "control-stack-proxy": Part("control-stack-proxy", control_stack_proxy(), "CONTROL_STACK_COTS", "COTS PROXY", pcb, "not printable"),
        "camera-proxy": Part("camera-proxy", camera_proxy(), "CAMERA_COTS", "COTS PROXY", black, "not printable"),
        "antenna-left-proxy": Part("antenna-left-proxy", antenna_proxy(1), "ANTENNA_SET", "COTS PROXY", black, "not printable"),
        "antenna-right-proxy": Part("antenna-right-proxy", antenna_proxy(-1), "ANTENNA_SET", "COTS PROXY", black, "not printable"),
    }


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
    if part.name.startswith("side-frame"):
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    elif part.name == "camera-guard":
        shape = shape.rotate((0, 0, 0), (0, 1, 0), -90)
    elif part.name.startswith("antenna-mount"):
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    bb = shape.BoundingBox()
    return shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_all() -> dict[str, object]:
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    ASSEMBLY_MESH_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    printed = printed_parts()
    artifacts: list[dict[str, object]] = []
    for part in printed.values():
        step_path = STEP_DIR / f"DRAFT-{part.name}.step"
        stl_path = MESH_DIR / f"DRAFT-{part.name}.stl"
        cq.exporters.export(part.shape, str(step_path), exportType="STEP")
        cq.exporters.export(
            orient_mesh_for_print(part),
            str(stl_path),
            exportType="STL",
            tolerance=P.STL_LINEAR_TOLERANCE_MM,
            angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
        )
        artifacts.extend([
            {"path": str(step_path.relative_to(ROOT)), "kind": "step_master", "sha256": sha256(step_path), "size_bytes": step_path.stat().st_size},
            {"path": str(stl_path.relative_to(ROOT)), "kind": "validation_mesh", "sha256": sha256(stl_path), "size_bytes": stl_path.stat().st_size},
        ])

        assembly_mesh_path = ASSEMBLY_MESH_DIR / f"DRAFT-{part.name}-assembly.stl"
        cq.exporters.export(
            part.shape,
            str(assembly_mesh_path),
            exportType="STL",
            tolerance=P.STL_LINEAR_TOLERANCE_MM,
            angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
        )
        artifacts.append({"path": str(assembly_mesh_path.relative_to(ROOT)), "kind": "assembly_validation_mesh", "sha256": sha256(assembly_mesh_path), "size_bytes": assembly_mesh_path.stat().st_size})

    for part in cots_parts().values():
        assembly_mesh_path = ASSEMBLY_MESH_DIR / f"DRAFT-{part.name}-assembly.stl"
        cq.exporters.export(
            part.shape,
            str(assembly_mesh_path),
            exportType="STL",
            tolerance=P.STL_LINEAR_TOLERANCE_MM,
            angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
        )
        artifacts.append({"path": str(assembly_mesh_path.relative_to(ROOT)), "kind": "cots_proxy_mesh", "sha256": sha256(assembly_mesh_path), "size_bytes": assembly_mesh_path.stat().st_size})

    printed_compound = cq.Compound.makeCompound([part.shape for part in printed.values()])
    printed_assembly_mesh = ASSEMBLY_MESH_DIR / "DRAFT-printed-assembly.stl"
    cq.exporters.export(
        printed_compound,
        str(printed_assembly_mesh),
        exportType="STL",
        tolerance=P.STL_LINEAR_TOLERANCE_MM,
        angularTolerance=P.STL_ANGULAR_TOLERANCE_RAD,
    )
    artifacts.append({"path": str(printed_assembly_mesh.relative_to(ROOT)), "kind": "printed_assembly_validation_mesh", "sha256": sha256(printed_assembly_mesh), "size_bytes": printed_assembly_mesh.stat().st_size})

    asm = assembly()
    assembly_step = STEP_DIR / "DRAFT-trailcam-b2-assembly.step"
    assembly_glb = PREVIEW_DIR / "DRAFT-trailcam-b2-assembly.glb"
    asm.save(str(assembly_step), exportType="STEP", mode="default")
    asm.save(str(assembly_glb), exportType="GLTF", mode="default", tolerance=0.2, angularTolerance=0.2)
    artifacts.extend([
        {"path": str(assembly_step.relative_to(ROOT)), "kind": "assembly_step", "sha256": sha256(assembly_step), "size_bytes": assembly_step.stat().st_size},
        {"path": str(assembly_glb.relative_to(ROOT)), "kind": "assembly_preview", "sha256": sha256(assembly_glb), "size_bytes": assembly_glb.stat().st_size},
    ])

    report = {
        "schema_version": "1.0",
        "project_id": P.PROJECT_ID,
        "revision": P.REVISION,
        "candidate": P.CANDIDATE,
        "status": "DRAFT",
        "tool": "CadQuery",
        "tool_version": importlib.metadata.version("cadquery"),
        "coordinate_frame": {"origin": "common wheel axis at vehicle center", "x": "forward", "y": "left/axle", "z": "up"},
        "tessellation": {"linear_tolerance_mm": P.STL_LINEAR_TOLERANCE_MM, "angular_tolerance_rad": P.STL_ANGULAR_TOLERANCE_RAD},
        "printed_parts": [
            {"name": part.name, "group": part.group, "material": part.material, "print_orientation": part.print_orientation, "bounds_assembly": shape_bounds(part.shape), "volume_mm3": part.shape.Volume()}
            for part in printed.values()
        ],
        "cots_proxies": [part.name for part in cots_parts().values()],
        "artifacts": artifacts,
        "limitations": [
            "All COTS geometry and masses remain planning proxies until delivered parts are measured.",
            "Validation STLs are DRAFT geometry artifacts, not manufacturing-release meshes.",
            "No exact Anycubic profile, slice, G-code, physical fit, powered balance or safety evidence exists.",
            "M3 insert pilots require exact insert selection and process-matched coupons before manufacture."
        ]
    }
    report_path = VALIDATION_DIR / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = export_all()
    print(json.dumps({"status": result["status"], "printed_parts": len(result["printed_parts"]), "artifacts": len(result["artifacts"])}, indent=2))
