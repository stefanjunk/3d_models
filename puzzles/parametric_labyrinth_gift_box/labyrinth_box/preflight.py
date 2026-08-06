"""Dimension derivation and fail-fast FDM checks."""

from __future__ import annotations

from dataclasses import dataclass
import math
import warnings

from .config import BoxConfig


NOZZLE_DIAMETER = 0.4
ROBUST_TWO_LINE_WIDTH = 2.0 * NOZZLE_DIAMETER
MAX_CHANNEL_CHORD_SAG = 0.02
BOOLEAN_RADIAL_OVERLAP = 0.05


class PrintabilityWarning(UserWarning):
    """A requested parameter combination violates the declared FDM limits."""


class UnsafeParametersError(ValueError):
    """Raised after a printability warning to prevent unsafe export."""


@dataclass(frozen=True, slots=True)
class DerivedDimensions:
    rows: int
    columns: int
    row_capacity: int
    column_capacity: int
    row_pitch: float
    column_pitch: float
    minimum_pitch: float
    maze_span: float
    maze_start_z: float
    maze_end_z: float
    maze_radius: float
    maze_spacing_radius: float
    inner_outer_radius: float
    inner_height: float
    sleeve_inner_radius: float
    sleeve_outer_radius: float
    sleeve_inner_depth: float
    sleeve_height: float
    follower_width: float
    follower_projection: float
    angular_facets: int


def requested_grid(difficulty: int) -> tuple[int, int]:
    """Map difficulty 1..10 to axial rows and circumferential columns."""
    if not 1 <= difficulty <= 10:
        raise ValueError("difficulty must be between 1 and 10")
    return 4 + difficulty, 8 + 2 * difficulty


def _reject(message: str) -> None:
    warnings.warn(message, PrintabilityWarning, stacklevel=3)
    raise UnsafeParametersError(message)


def validate_and_derive(config: BoxConfig) -> DerivedDimensions:
    """Validate dimensions and derive the printable cylindrical grid."""
    dimensions = {
        "cavity_diameter": config.cavity_diameter,
        "cavity_length": config.cavity_length,
        "inner_wall": config.inner_wall,
        "outer_wall": config.outer_wall,
        "bottom_thickness": config.bottom_thickness,
        "cap_thickness": config.cap_thickness,
        "radial_clearance": config.radial_clearance,
        "axial_clearance": config.axial_clearance,
        "channel_width": config.channel_width,
        "channel_depth": config.channel_depth,
        "follower_clearance": config.follower_clearance,
        "follower_tip_clearance": config.follower_tip_clearance,
        "maze_margin": config.maze_margin,
        "minimum_wall": config.minimum_wall,
        "minimum_web": config.minimum_web,
        "minimum_feature": config.minimum_feature,
        "stl_tolerance": config.stl_tolerance,
        "stl_angular_tolerance": config.stl_angular_tolerance,
    }
    non_finite = [name for name, value in dimensions.items() if not math.isfinite(value)]
    if non_finite:
        _reject(f"dimensions must be finite: {', '.join(non_finite)}")
    non_positive = [name for name, value in dimensions.items() if value <= 0]
    if non_positive:
        _reject(f"dimensions must be positive: {', '.join(non_positive)}")
    if config.maze_location not in {"inner", "outer"}:
        _reject("maze_location must be 'inner' or 'outer'")
    if not 1 <= config.difficulty <= 10:
        _reject("difficulty must be between 1 and 10")
    if config.angular_facets < 48:
        _reject("angular_facets must be at least 48 for a printable round surface")
    safety_floors = {
        "minimum_wall": (config.minimum_wall, ROBUST_TWO_LINE_WIDTH),
        "minimum_web": (config.minimum_web, ROBUST_TWO_LINE_WIDTH),
        "minimum_feature": (config.minimum_feature, NOZZLE_DIAMETER),
    }
    for name, (value, floor) in safety_floors.items():
        if value < floor:
            _reject(
                f"{name} {value:.2f} mm is below the fixed PLA/0.4 mm nozzle "
                f"safety floor of {floor:.2f} mm"
            )
    if config.channel_width < config.minimum_feature:
        _reject("channel_width is below the declared minimum feature")
    if config.channel_depth < config.minimum_feature:
        _reject("channel_depth is below the declared minimum feature")
    if config.stl_tolerance > config.minimum_feature / 2.0:
        _reject("stl_tolerance is too large for the declared minimum feature")
    if config.stl_angular_tolerance > 0.5:
        _reject("stl_angular_tolerance must not exceed 0.5 radians")
    if config.bottom_thickness < config.minimum_wall:
        _reject("bottom_thickness is below the declared minimum wall")
    if config.cap_thickness < config.minimum_wall:
        _reject("cap_thickness is below the declared minimum wall")
    required_margin = config.channel_width / 2.0 + config.minimum_web
    if config.maze_margin < required_margin:
        _reject(
            f"maze_margin {config.maze_margin:.2f} mm is too small; at least "
            f"{required_margin:.2f} mm is required to keep non-exit channels "
            "away from the open rim"
        )

    follower_width = config.channel_width - config.follower_clearance
    if follower_width < config.minimum_feature:
        _reject(
            f"follower width {follower_width:.2f} mm is below the declared "
            f"minimum feature {config.minimum_feature:.2f} mm"
        )
    follower_projection = (
        config.radial_clearance + config.channel_depth - config.follower_tip_clearance
    )
    if config.follower_tip_clearance <= 0 or follower_projection <= config.radial_clearance:
        _reject("follower tip clearance leaves no positive engagement in the maze")

    inner_residual = config.inner_wall - (
        config.channel_depth if config.maze_location == "inner" else 0.0
    )
    if inner_residual < config.minimum_wall:
        _reject(
            f"inner wall leaves only {inner_residual:.2f} mm after the maze cut; "
            f"at least {config.minimum_wall:.2f} mm is required"
        )
    outer_residual = config.outer_wall - (
        config.channel_depth if config.maze_location == "outer" else 0.0
    )
    if outer_residual < config.minimum_wall:
        _reject(
            f"outer wall leaves only {outer_residual:.2f} mm after the maze cut; "
            f"at least {config.minimum_wall:.2f} mm is required"
        )

    rows, columns = requested_grid(config.difficulty)
    minimum_pitch = config.channel_width + config.minimum_web
    maze_span = config.cavity_length - 2.0 * config.maze_margin
    if maze_span <= 0:
        _reject("cavity length is too short after applying maze end margins")

    inner_outer_radius = config.cavity_diameter / 2.0 + config.inner_wall
    inner_height = config.bottom_thickness + config.cavity_length
    sleeve_inner_radius = inner_outer_radius + config.radial_clearance
    sleeve_outer_radius = sleeve_inner_radius + config.outer_wall
    sleeve_inner_depth = inner_height + config.axial_clearance
    sleeve_height = sleeve_inner_depth + config.cap_thickness
    maze_radius = (
        inner_outer_radius if config.maze_location == "inner" else sleeve_inner_radius
    )
    maze_spacing_radius = (
        inner_outer_radius - config.channel_depth
        if config.maze_location == "inner"
        else sleeve_inner_radius
    )
    if maze_spacing_radius <= 0:
        _reject("channel depth consumes the cylindrical maze spacing radius")
    chord_sag_limit = min(
        MAX_CHANNEL_CHORD_SAG,
        config.follower_clearance / 8.0,
        config.stl_tolerance / 2.0,
    )
    largest_channel_radius = max(
        inner_outer_radius + BOOLEAN_RADIAL_OVERLAP,
        sleeve_inner_radius + config.channel_depth,
    )
    cosine = max(-1.0, min(1.0, 1.0 - chord_sag_limit / largest_channel_radius))
    required_facets = math.ceil(math.pi / math.acos(cosine))
    angular_facets = max(config.angular_facets, required_facets)

    row_capacity = math.floor(maze_span / minimum_pitch) + 1
    spacing_ratio = minimum_pitch / (2.0 * maze_spacing_radius)
    column_capacity = (
        2 if spacing_ratio >= 1.0 else math.floor(math.pi / math.asin(spacing_ratio))
    )
    if rows > row_capacity or columns > column_capacity:
        _reject(
            f"difficulty {config.difficulty} requests a {rows}x{columns} maze, but "
            f"length {config.cavity_length:.2f} mm and cavity diameter "
            f"{config.cavity_diameter:.2f} mm safely fit at most "
            f"{row_capacity}x{column_capacity} cells for a 0.4 mm nozzle"
        )

    row_pitch = maze_span / (rows - 1)
    column_pitch = 2.0 * maze_spacing_radius * math.sin(math.pi / columns)
    maze_start_z = config.bottom_thickness + config.maze_margin
    maze_end_z = maze_start_z + maze_span

    return DerivedDimensions(
        rows=rows,
        columns=columns,
        row_capacity=row_capacity,
        column_capacity=column_capacity,
        row_pitch=row_pitch,
        column_pitch=column_pitch,
        minimum_pitch=minimum_pitch,
        maze_span=maze_span,
        maze_start_z=maze_start_z,
        maze_end_z=maze_end_z,
        maze_radius=maze_radius,
        maze_spacing_radius=maze_spacing_radius,
        inner_outer_radius=inner_outer_radius,
        inner_height=inner_height,
        sleeve_inner_radius=sleeve_inner_radius,
        sleeve_outer_radius=sleeve_outer_radius,
        sleeve_inner_depth=sleeve_inner_depth,
        sleeve_height=sleeve_height,
        follower_width=follower_width,
        follower_projection=follower_projection,
        angular_facets=angular_facets,
    )
