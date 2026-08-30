#!/usr/bin/env python3
"""MM-TOY-002 double-wishbone v2 kinematic skeleton.

This module intentionally produces a non-manufacturing assembly: joint points,
axes and conservative purchased-part envelopes only.  It is the fail-closed
step between the rejected trailing-arm experiment and printable suspension
geometry.  Importing the module has no filesystem side effects.

Coordinate system: x forward, y left, z up; millimetres and degrees.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import parameters as p

SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
DEFAULT_EXPORT_DIR = SCRIPT.parent / "exports" / "v0.4.0-draft.2-double-wishbone"
Vec3 = tuple[float, float, float]


def v_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_scale(a: Vec3, scalar: float) -> Vec3:
    return (a[0] * scalar, a[1] * scalar, a[2] * scalar)


def v_dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def v_length(a: Vec3) -> float:
    return math.sqrt(v_dot(a, a))


def v_unit(a: Vec3) -> Vec3:
    length = v_length(a)
    if length <= 1e-12:
        raise ValueError("zero-length vector")
    return v_scale(a, 1.0 / length)


def distance(a: Vec3, b: Vec3) -> float:
    return v_length(v_sub(a, b))


def rotate_vector(vector: Vec3, axis: Vec3, angle_rad: float) -> Vec3:
    """Rodrigues rotation of a vector around an axis through the origin."""
    k = v_unit(axis)
    cosine = math.cos(angle_rad)
    sine = math.sin(angle_rad)
    return v_add(
        v_add(v_scale(vector, cosine), v_scale(v_cross(k, vector), sine)),
        v_scale(k, v_dot(k, vector) * (1.0 - cosine)),
    )


def rotate_point(point: Vec3, origin: Vec3, axis: Vec3, angle_deg: float) -> Vec3:
    return v_add(
        origin,
        rotate_vector(v_sub(point, origin), axis, math.radians(angle_deg)),
    )


def align_vector(vector: Vec3, source_axis: Vec3, target_axis: Vec3) -> Vec3:
    """Apply the smallest rotation that maps source_axis onto target_axis."""
    source = v_unit(source_axis)
    target = v_unit(target_axis)
    cosine = max(-1.0, min(1.0, v_dot(source, target)))
    if cosine > 1.0 - 1e-12:
        return vector
    if cosine < -1.0 + 1e-12:
        helper = (1.0, 0.0, 0.0) if abs(source[0]) < 0.9 else (0.0, 1.0, 0.0)
        return rotate_vector(vector, v_cross(source, helper), math.pi)
    axis = v_cross(source, target)
    return rotate_vector(vector, axis, math.acos(cosine))


def axis_range(start: float, stop: float, step: float) -> list[float]:
    count = round((stop - start) / step)
    return [round(start + index * step, 9) for index in range(count + 1)]


def circle_intersections(
    center_a: tuple[float, float],
    radius_a: float,
    center_b: tuple[float, float],
    radius_b: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return both intersections in the local outward-y/z plane."""
    dx = center_b[0] - center_a[0]
    dz = center_b[1] - center_a[1]
    separation = math.hypot(dx, dz)
    if separation <= 1e-12:
        raise ValueError("concentric linkage circles")
    if separation > radius_a + radius_b + 1e-9:
        raise ValueError("linkage circles do not intersect")
    along = (radius_a * radius_a - radius_b * radius_b + separation * separation) / (
        2.0 * separation
    )
    height_sq = radius_a * radius_a - along * along
    if height_sq < -1e-8:
        raise ValueError("negative linkage circle height")
    height = math.sqrt(max(0.0, height_sq))
    base_y = center_a[0] + along * dx / separation
    base_z = center_a[1] + along * dz / separation
    offset_y = -dz * height / separation
    offset_z = dx * height / separation
    return (
        (base_y + offset_y, base_z + offset_z),
        (base_y - offset_y, base_z - offset_z),
    )


@dataclass(frozen=True)
class CornerPose:
    axle: str
    side: int
    travel_mm: float
    steer_deg: float
    rear_toe_deg: float
    lower_inboard_a: Vec3
    lower_inboard_b: Vec3
    upper_inboard_a: Vec3
    upper_inboard_b: Vec3
    lower_outer: Vec3
    upper_outer: Vec3
    wheel_center: Vec3
    wheel_axis: Vec3
    shock_lower: Vec3
    shock_upper: Vec3
    tie_outer: Vec3
    tie_inner: Vec3
    halfshaft_inner: Vec3
    halfshaft_outer: Vec3
    lower_arm_delta_deg: float
    upright_delta_deg: float
    shock_length_mm: float
    halfshaft_length_mm: float
    halfshaft_angle_deg: float


def axle_x(axle: str) -> float:
    if axle == "front":
        return p.AXLE_X_MM
    if axle == "rear":
        return -p.AXLE_X_MM
    raise ValueError(f"unknown axle: {axle}")


def upper_outer_x(axle: str) -> float:
    return (
        p.DWV2_FRONT_UPPER_OUTER_X_MM
        if axle == "front"
        else p.DWV2_REAR_UPPER_OUTER_X_MM
    )


def nominal_points(axle: str, side: int) -> dict[str, Vec3]:
    x_axle = axle_x(axle)
    x_upper = upper_outer_x(axle)
    sign = float(side)
    return {
        "lower_outer": (
            x_axle,
            sign * p.DWV2_LOWER_OUTER_Y_MM,
            p.DWV2_LOWER_OUTER_Z_MM,
        ),
        "upper_outer": (
            x_upper,
            sign * p.DWV2_UPPER_OUTER_Y_MM,
            p.DWV2_UPPER_OUTER_Z_MM,
        ),
        "wheel_center": (
            x_axle,
            sign * p.WHEEL_Y_MM,
            p.DWV2_WHEEL_CENTER_Z_MM,
        ),
        "halfshaft_outer": (
            x_axle,
            sign * p.DWV2_OUTER_HALFSHAFT_Y_MM,
            p.DWV2_OUTER_HALFSHAFT_Z_MM,
        ),
        "tie_outer": (
            (
                p.DWV2_FRONT_TIE_OUTER_MM
                if axle == "front"
                else p.DWV2_REAR_TOE_OUTER_MM
            )[0],
            sign
            * (
                p.DWV2_FRONT_TIE_OUTER_MM
                if axle == "front"
                else p.DWV2_REAR_TOE_OUTER_MM
            )[1],
            (
                p.DWV2_FRONT_TIE_OUTER_MM
                if axle == "front"
                else p.DWV2_REAR_TOE_OUTER_MM
            )[2],
        ),
    }


def outer_joints(
    axle: str, side: int, travel_mm: float
) -> tuple[Vec3, Vec3, float, float]:
    """Solve the rigid four-bar branch for the requested lower-joint z travel."""
    sign = float(side)
    x_axle = axle_x(axle)
    x_upper = upper_outer_x(axle)
    lower_inner = (p.DWV2_LOWER_INBOARD_Y_MM, p.DWV2_LOWER_INBOARD_Z_MM)
    upper_inner = (p.DWV2_UPPER_INBOARD_Y_MM, p.DWV2_UPPER_INBOARD_Z_MM)
    lower_nominal = (p.DWV2_LOWER_OUTER_Y_MM, p.DWV2_LOWER_OUTER_Z_MM)
    upper_nominal = (p.DWV2_UPPER_OUTER_Y_MM, p.DWV2_UPPER_OUTER_Z_MM)
    lower_radius = math.dist(lower_inner, lower_nominal)
    upper_radius = math.dist(upper_inner, upper_nominal)
    upright_yz_length = math.dist(lower_nominal, upper_nominal)

    lower_z = p.DWV2_LOWER_OUTER_Z_MM + travel_mm
    radial_z = lower_z - lower_inner[1]
    radial_y_sq = lower_radius * lower_radius - radial_z * radial_z
    if radial_y_sq <= 0.0:
        raise ValueError(f"lower arm singular at travel {travel_mm}")
    lower_y = lower_inner[0] + math.sqrt(radial_y_sq)
    lower_local = (lower_y, lower_z)

    choices = circle_intersections(
        upper_inner,
        upper_radius,
        lower_local,
        upright_yz_length,
    )
    upper_local = min(choices, key=lambda point: math.dist(point, upper_nominal))

    lower_angle_0 = math.atan2(
        lower_nominal[1] - lower_inner[1],
        lower_nominal[0] - lower_inner[0],
    )
    lower_angle = math.atan2(
        lower_local[1] - lower_inner[1],
        lower_local[0] - lower_inner[0],
    )
    upright_angle_0 = math.atan2(
        upper_nominal[1] - lower_nominal[1],
        upper_nominal[0] - lower_nominal[0],
    )
    upright_angle = math.atan2(
        upper_local[1] - lower_local[1],
        upper_local[0] - lower_local[0],
    )
    lower = (x_axle, sign * lower_local[0], lower_local[1])
    upper = (x_upper, sign * upper_local[0], upper_local[1])
    return (
        lower,
        upper,
        math.degrees(lower_angle - lower_angle_0),
        math.degrees(upright_angle - upright_angle_0),
    )


def map_upright_point(
    axle: str,
    side: int,
    travel_mm: float,
    point: Vec3,
    steer_deg: float = 0.0,
) -> Vec3:
    nominal = nominal_points(axle, side)
    lower, upper, _, _ = outer_joints(axle, side, travel_mm)
    nominal_axis = v_sub(nominal["upper_outer"], nominal["lower_outer"])
    current_axis = v_sub(upper, lower)
    aligned = v_add(
        lower,
        align_vector(
            v_sub(point, nominal["lower_outer"]),
            nominal_axis,
            current_axis,
        ),
    )
    if abs(steer_deg) <= 1e-12:
        return aligned
    return rotate_point(aligned, lower, current_axis, steer_deg * float(side))


def map_upright_direction(
    axle: str,
    side: int,
    travel_mm: float,
    direction: Vec3,
    steer_deg: float = 0.0,
) -> Vec3:
    nominal = nominal_points(axle, side)
    lower, upper, _, _ = outer_joints(axle, side, travel_mm)
    nominal_axis = v_sub(nominal["upper_outer"], nominal["lower_outer"])
    current_axis = v_sub(upper, lower)
    aligned = align_vector(direction, nominal_axis, current_axis)
    if abs(steer_deg) > 1e-12:
        aligned = rotate_vector(
            aligned,
            current_axis,
            math.radians(steer_deg * float(side)),
        )
    return v_unit(aligned)


def lower_shock_point(axle: str, side: int, lower_delta_deg: float) -> Vec3:
    x_axle = axle_x(axle)
    pivot = (
        x_axle,
        float(side) * p.DWV2_LOWER_INBOARD_Y_MM,
        p.DWV2_LOWER_INBOARD_Z_MM,
    )
    nominal = (
        x_axle,
        float(side) * p.DWV2_LOWER_SHOCK_Y_MM,
        p.DWV2_LOWER_SHOCK_Z_MM,
    )
    return v_add(
        pivot,
        rotate_vector(
            v_sub(nominal, pivot),
            (1.0, 0.0, 0.0),
            math.radians(lower_delta_deg * float(side)),
        ),
    )


def rear_toe_angle(side: int, travel_mm: float) -> float:
    nominal = nominal_points("rear", side)
    outer_nominal = nominal["tie_outer"]
    inner_values = p.DWV2_REAR_TOE_INNER_MM
    inner = (inner_values[0], float(side) * inner_values[1], inner_values[2])
    target_sq = distance(outer_nominal, inner) ** 2
    lower, upper, _, _ = outer_joints("rear", side, travel_mm)
    base_outer = map_upright_point("rear", side, travel_mm, outer_nominal)
    axis = v_sub(upper, lower)

    def residual(angle_deg: float) -> float:
        moved = rotate_point(base_outer, lower, axis, angle_deg * float(side))
        return distance(moved, inner) ** 2 - target_sq

    samples = axis_range(-6.0, 6.0, 0.05)
    roots: list[float] = []
    previous_angle = samples[0]
    previous_value = residual(previous_angle)
    if abs(previous_value) < 1e-12:
        roots.append(previous_angle)
    for angle in samples[1:]:
        value = residual(angle)
        if abs(value) < 1e-12:
            roots.append(angle)
        elif value * previous_value < 0.0:
            low, high = previous_angle, angle
            low_value = previous_value
            for _ in range(70):
                middle = (low + high) / 2.0
                middle_value = residual(middle)
                if abs(middle_value) < 1e-14:
                    low = high = middle
                    break
                if low_value * middle_value <= 0.0:
                    high = middle
                else:
                    low = middle
                    low_value = middle_value
            roots.append((low + high) / 2.0)
        previous_angle, previous_value = angle, value
    if not roots:
        best = min(samples, key=lambda angle: abs(residual(angle)))
        if abs(residual(best)) > 1e-6:
            raise ValueError(f"rear toe link cannot close at travel {travel_mm}")
        return best
    return min(roots, key=abs)


def front_rack_inner(side: int, outer: Vec3) -> Vec3:
    outer_values = p.DWV2_FRONT_TIE_OUTER_MM
    inner_values = p.DWV2_FRONT_TIE_INNER_MM
    outer_nominal = (outer_values[0], float(side) * outer_values[1], outer_values[2])
    inner_nominal = (inner_values[0], float(side) * inner_values[1], inner_values[2])
    target_length = distance(outer_nominal, inner_nominal)
    fixed_x = inner_values[0]
    fixed_z = inner_values[2]
    remaining_sq = target_length * target_length - (
        (fixed_x - outer[0]) ** 2 + (fixed_z - outer[2]) ** 2
    )
    if remaining_sq < -1e-8:
        raise ValueError("front tie rod cannot reach the fixed rack x/z corridor")
    inward = math.sqrt(max(0.0, remaining_sq))
    return (fixed_x, outer[1] - float(side) * inward, fixed_z)


def corner_pose(
    axle: str, side: int, travel_mm: float, steer_deg: float = 0.0
) -> CornerPose:
    if side not in (-1, 1):
        raise ValueError("side must be -1 (right) or +1 (left)")
    if axle == "rear" and abs(steer_deg) > 1e-12:
        raise ValueError("rear steer is closed by the toe link")
    x_axle = axle_x(axle)
    x_upper = upper_outer_x(axle)
    sign = float(side)
    lower, upper, lower_delta, upright_delta = outer_joints(axle, side, travel_mm)
    nominal = nominal_points(axle, side)
    rear_toe = rear_toe_angle(side, travel_mm) if axle == "rear" else 0.0
    actual_steer = rear_toe if axle == "rear" else steer_deg

    wheel = map_upright_point(
        axle, side, travel_mm, nominal["wheel_center"], actual_steer
    )
    wheel_axis = map_upright_direction(
        axle, side, travel_mm, (0.0, sign, 0.0), actual_steer
    )
    shock_lower = lower_shock_point(axle, side, lower_delta)
    shock_upper = (
        x_axle,
        sign * p.DWV2_UPPER_SHOCK_Y_MM,
        p.DWV2_UPPER_SHOCK_Z_MM,
    )
    tie_outer = map_upright_point(
        axle, side, travel_mm, nominal["tie_outer"], actual_steer
    )
    if axle == "front":
        tie_inner = front_rack_inner(side, tie_outer)
    else:
        values = p.DWV2_REAR_TOE_INNER_MM
        tie_inner = (values[0], sign * values[1], values[2])
    halfshaft_inner = (
        x_axle,
        sign * p.DWV2_INNER_HALFSHAFT_Y_MM,
        p.DWV2_INNER_HALFSHAFT_Z_MM,
    )
    halfshaft_outer = map_upright_point(
        axle, side, travel_mm, nominal["halfshaft_outer"], actual_steer
    )
    shaft_vector = v_sub(halfshaft_outer, halfshaft_inner)
    shaft_length = v_length(shaft_vector)
    shaft_angle = math.degrees(math.asin(min(1.0, abs(shaft_vector[2]) / shaft_length)))

    return CornerPose(
        axle=axle,
        side=side,
        travel_mm=travel_mm,
        steer_deg=steer_deg,
        rear_toe_deg=rear_toe,
        lower_inboard_a=(
            x_axle - p.DWV2_LOWER_INBOARD_HALF_SPAN_X_MM,
            sign * p.DWV2_LOWER_INBOARD_Y_MM,
            p.DWV2_LOWER_INBOARD_Z_MM,
        ),
        lower_inboard_b=(
            x_axle + p.DWV2_LOWER_INBOARD_HALF_SPAN_X_MM,
            sign * p.DWV2_LOWER_INBOARD_Y_MM,
            p.DWV2_LOWER_INBOARD_Z_MM,
        ),
        upper_inboard_a=(
            x_upper - p.DWV2_UPPER_INBOARD_HALF_SPAN_X_MM,
            sign * p.DWV2_UPPER_INBOARD_Y_MM,
            p.DWV2_UPPER_INBOARD_Z_MM,
        ),
        upper_inboard_b=(
            x_upper + p.DWV2_UPPER_INBOARD_HALF_SPAN_X_MM,
            sign * p.DWV2_UPPER_INBOARD_Y_MM,
            p.DWV2_UPPER_INBOARD_Z_MM,
        ),
        lower_outer=lower,
        upper_outer=upper,
        wheel_center=wheel,
        wheel_axis=wheel_axis,
        shock_lower=shock_lower,
        shock_upper=shock_upper,
        tie_outer=tie_outer,
        tie_inner=tie_inner,
        halfshaft_inner=halfshaft_inner,
        halfshaft_outer=halfshaft_outer,
        lower_arm_delta_deg=lower_delta,
        upright_delta_deg=upright_delta,
        shock_length_mm=distance(shock_lower, shock_upper),
        halfshaft_length_mm=shaft_length,
        halfshaft_angle_deg=shaft_angle,
    )


def cylinder_between(start: Vec3, end: Vec3, radius: float) -> cq.Shape:
    direction = v_sub(end, start)
    return cq.Solid.makeCylinder(
        radius, v_length(direction), pnt=start, dir=v_unit(direction)
    )


def sphere(center: Vec3, radius: float = 1.8) -> cq.Shape:
    return cq.Solid.makeSphere(radius, center)


def arm_skeleton(pose: CornerPose, upper: bool) -> cq.Shape:
    if upper:
        inner_a, inner_b, outer = (
            pose.upper_inboard_a,
            pose.upper_inboard_b,
            pose.upper_outer,
        )
    else:
        inner_a, inner_b, outer = (
            pose.lower_inboard_a,
            pose.lower_inboard_b,
            pose.lower_outer,
        )
    bodies = [
        cylinder_between(inner_a, inner_b, 0.8),
        cylinder_between(inner_a, outer, 1.2),
        cylinder_between(inner_b, outer, 1.2),
        sphere(inner_a),
        sphere(inner_b),
        sphere(outer),
    ]
    return cq.Compound.makeCompound(bodies)


def tire_shell(pose: CornerPose, radius: float, shell: float = 1.0) -> cq.Shape:
    half_width = p.TIRE_WIDTH_MM / 2.0
    start = v_add(pose.wheel_center, v_scale(pose.wheel_axis, -half_width))
    outer = cq.Solid.makeCylinder(
        radius, p.TIRE_WIDTH_MM, pnt=start, dir=pose.wheel_axis
    )
    inner = cq.Solid.makeCylinder(
        radius - shell,
        p.TIRE_WIDTH_MM + 0.4,
        pnt=v_add(start, v_scale(pose.wheel_axis, -0.2)),
        dir=pose.wheel_axis,
    )
    return outer.cut(inner)


def drivetrain_proxy(axle: str) -> tuple[cq.Shape, cq.Shape]:
    x_axle = axle_x(axle)
    direction = 1.0 if axle == "front" else -1.0
    motor_start = (
        x_axle - direction * p.POLOLU_4743_AXIAL_ENVELOPE_WITH_SHAFT_MM,
        0.0,
        p.DWV2_INNER_HALFSHAFT_Z_MM,
    )
    motor = cq.Solid.makeCylinder(
        p.POLOLU_4743_FLANGE_DIAMETER_MM / 2.0,
        p.POLOLU_4743_AXIAL_ENVELOPE_WITH_SHAFT_MM,
        pnt=motor_start,
        dir=(direction, 0.0, 0.0),
    )
    spool = cq.Solid.makeCylinder(
        5.0,
        50.0,
        pnt=(x_axle, -25.0, p.DWV2_INNER_HALFSHAFT_Z_MM),
        dir=(0.0, 1.0, 0.0),
    )
    return motor, spool


def neutral_assembly(include_chassis: bool = True) -> cq.Assembly:
    assembly = cq.Assembly(name="MM-TOY-002-double-wishbone-v2-skeleton")
    chassis_path = SCRIPT.parent / "exports" / "DRAFT-chassis-printed.step"
    if include_chassis and chassis_path.is_file():
        chassis = cq.importers.importStep(str(chassis_path)).val()
        assembly.add(
            chassis, name="reference-chassis-v1", color=cq.Color(0.28, 0.28, 0.30, 0.35)
        )
    for axle in ("front", "rear"):
        motor, spool = drivetrain_proxy(axle)
        assembly.add(
            motor, name=f"{axle}-motor-envelope", color=cq.Color(0.45, 0.45, 0.48, 0.5)
        )
        assembly.add(
            spool, name=f"{axle}-spool-envelope", color=cq.Color(0.75, 0.55, 0.12, 0.8)
        )
        for side in (-1, 1):
            side_name = "left" if side > 0 else "right"
            pose = corner_pose(axle, side, 0.0, 0.0)
            prefix = f"{axle}-{side_name}"
            assembly.add(
                arm_skeleton(pose, upper=False),
                name=f"{prefix}-lower-wishbone-axis",
                color=cq.Color(0.15, 0.45, 0.90),
            )
            assembly.add(
                arm_skeleton(pose, upper=True),
                name=f"{prefix}-upper-wishbone-axis",
                color=cq.Color(0.15, 0.70, 0.95),
            )
            assembly.add(
                cylinder_between(pose.lower_outer, pose.upper_outer, 1.1),
                name=f"{prefix}-upright-axis",
                color=cq.Color(0.25, 0.85, 0.35),
            )
            assembly.add(
                cylinder_between(pose.shock_lower, pose.shock_upper, 1.8),
                name=f"{prefix}-shock-envelope",
                color=cq.Color(1.0, 0.40, 0.08),
            )
            assembly.add(
                cylinder_between(pose.halfshaft_inner, pose.halfshaft_outer, 1.8),
                name=f"{prefix}-halfshaft-envelope",
                color=cq.Color(0.85, 0.18, 0.20),
            )
            assembly.add(
                cylinder_between(pose.tie_inner, pose.tie_outer, 1.1),
                name=f"{prefix}-tie-link",
                color=cq.Color(0.75, 0.25, 0.85),
            )
            assembly.add(
                tire_shell(pose, p.TIRE_DIAMETER_MM / 2.0),
                name=f"{prefix}-tire-r45",
                color=cq.Color(0.10, 0.10, 0.10, 0.65),
            )
            assembly.add(
                tire_shell(pose, p.TIRE_DIAMETER_MAX_MM / 2.0),
                name=f"{prefix}-tire-r57p5",
                color=cq.Color(0.55, 0.55, 0.55, 0.20),
            )
    return assembly


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    try:
        recorded_path = path.relative_to(PROJECT)
    except ValueError:
        recorded_path = path
    return {
        "path": str(recorded_path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def render_preview(path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure = plt.figure(figsize=(13.5, 7.5))
    axis = figure.add_subplot(111, projection="3d")
    axis.set_proj_type("ortho")

    def line(
        points: Sequence[Vec3], color: str, width: float = 1.8, alpha: float = 1.0
    ) -> None:
        axis.plot(
            [point[0] for point in points],
            [point[1] for point in points],
            [point[2] for point in points],
            color=color,
            linewidth=width,
            alpha=alpha,
        )

    # Current chassis v1 envelope is shown only as a reference box.
    for side in (-1, 1):
        line(
            [(-198.0, side * 80.0, 0.0), (198.0, side * 80.0, 0.0)],
            "#55595f",
            4.0,
            0.55,
        )
        line(
            [(-198.0, side * 80.0, 52.0), (198.0, side * 80.0, 52.0)],
            "#777b80",
            1.0,
            0.35,
        )
    for axle in ("front", "rear"):
        for side in (-1, 1):
            pose = corner_pose(axle, side, 0.0, 0.0)
            line(
                [pose.lower_inboard_a, pose.lower_outer, pose.lower_inboard_b],
                "#2878d0",
                2.2,
            )
            line(
                [pose.upper_inboard_a, pose.upper_outer, pose.upper_inboard_b],
                "#31a9d8",
                2.2,
            )
            line([pose.lower_outer, pose.upper_outer], "#45b85a", 2.5)
            line([pose.shock_lower, pose.shock_upper], "#f26b1d", 2.5)
            line([pose.halfshaft_inner, pose.halfshaft_outer], "#d8343a", 2.0)
            line([pose.tie_inner, pose.tie_outer], "#a54dcc", 1.6)
            for radius, color, alpha in (
                (45.0, "#1f2022", 0.75),
                (57.5, "#96999d", 0.35),
            ):
                points: list[Vec3] = []
                for degree in range(0, 361, 6):
                    angle = math.radians(degree)
                    points.append(
                        (
                            pose.wheel_center[0] + radius * math.cos(angle),
                            pose.wheel_center[1],
                            pose.wheel_center[2] + radius * math.sin(angle),
                        )
                    )
                line(points, color, 1.2, alpha)
    axis.set_xlim(-215, 215)
    axis.set_ylim(-125, 125)
    axis.set_zlim(-60, 85)
    axis.set_box_aspect((430, 250, 145))
    axis.view_init(elev=24, azim=-58)
    axis.set_xlabel("x / mm (forward)")
    axis.set_ylabel("y / mm (left)")
    axis.set_zlabel("z / mm (up)")
    axis.set_title(
        "MM-TOY-002 — Double-wishbone v2 kinematic skeleton\nDRAFT / envelopes only / not manufacturable"
    )
    legend_items = (
        ("#2878d0", "lower wishbone axes"),
        ("#31a9d8", "upper wishbone axes"),
        ("#45b85a", "upright/steering axis"),
        ("#f26b1d", "shock envelope"),
        ("#d8343a", "halfshaft envelope"),
        ("#a54dcc", "tie/toe link"),
    )
    for color, label in legend_items:
        axis.plot([], [], [], color=color, linewidth=2.3, label=label)
    axis.legend(loc="upper left", fontsize=8, framealpha=0.9)
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=180,
        metadata={"Software": "MM-TOY-002 deterministic CadQuery workflow"},
    )
    plt.close(figure)


def export_skeleton(
    output_dir: Path, include_chassis: bool = True
) -> dict[str, object]:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite output directory: {output_dir}")
    output_dir.mkdir(parents=True)
    step_path = output_dir / "DRAFT-double-wishbone-v2-kinematic-skeleton.step"
    preview_path = output_dir / "DRAFT-double-wishbone-v2-neutral-preview.png"
    assembly = neutral_assembly(include_chassis=include_chassis)
    cq.exporters.export(assembly.toCompound(), str(step_path), exportType="STEP")
    render_preview(preview_path)

    source_inputs = [
        SCRIPT,
        SCRIPT.parent / "parameters.py",
        PROJECT / "design-spec.yaml",
        PROJECT / "architecture" / "double-wishbone-v2-interface-contract-v0.4.0.json",
        PROJECT / "reports" / "cots-drivetrain-study-v0.4.0.md",
    ]
    if include_chassis:
        source_inputs.append(SCRIPT.parent / "exports" / "DRAFT-chassis-printed.step")
    missing = [str(path) for path in source_inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing manifest inputs: " + ", ".join(missing))
    manifest = {
        "schema_version": "1.0",
        "project_id": "MM-TOY-002",
        "project_revision": "0.4.0",
        "candidate": "0.4.0-draft.2",
        "artifact_class": "non-manufacturing-kinematic-skeleton",
        "manufacturing_exports": [],
        "stl_export": "INTENTIONALLY_NOT_GENERATED",
        "watermark": "DEFERRED_UNTIL_STABLE_PHYSICAL_CANDIDATE",
        "inputs": [file_record(path) for path in source_inputs],
        "outputs": [file_record(step_path), file_record(preview_path)],
        "notes": [
            "STEP contains reference/skeleton/envelope solids, not printable part geometry.",
            "Current chassis v1 is an unchanged reference and is not integration-compatible.",
            "No supplier CAD is redistributed; purchased parts are conservative analytic proxies only.",
        ],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--without-chassis", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    # A neutral solve exercises both front/rear and both mirrored sides.
    for axle in ("front", "rear"):
        for side in (-1, 1):
            corner_pose(axle, side, 0.0, 0.0)
    if args.check_only:
        print("PASS: neutral double-wishbone v2 kinematic solve")
        return 0
    manifest = export_skeleton(
        args.output_dir, include_chassis=not args.without_chassis
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
