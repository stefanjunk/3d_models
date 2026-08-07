"""CadQuery geometry for the two-piece cylindrical labyrinth box."""

from __future__ import annotations

from dataclasses import dataclass
import math

import cadquery as cq

from .config import BoxConfig
from .maze import Maze, MazeMetrics, count_simple_paths, generate_maze_for_difficulty
from .preflight import DerivedDimensions, validate_and_derive


BOOLEAN_OVERLAP = 0.05
FOLLOWER_ATTACHMENT = 0.4


@dataclass(frozen=True)
class GeometryResult:
    config: BoxConfig
    dimensions: DerivedDimensions
    maze: Maze
    metrics: MazeMetrics
    candidate_count: int
    inner: cq.Workplane
    outer: cq.Workplane


def _radial_prism(
    angle_degrees: float,
    radial_min: float,
    radial_max: float,
    tangential_width: float,
    z_min: float,
    z_max: float,
) -> cq.Workplane:
    radial_length = radial_max - radial_min
    axial_length = z_max - z_min
    if radial_length <= 0 or axial_length <= 0:
        raise ValueError("radial prism dimensions must be positive")
    prism = (
        cq.Workplane("XY")
        .box(
            radial_length,
            tangential_width,
            axial_length,
            centered=(True, True, False),
        )
        .translate(((radial_min + radial_max) / 2.0, 0.0, z_min))
    )
    return prism.rotate((0, 0, 0), (0, 0, 1), angle_degrees)


def _annular_sector(
    radial_min: float,
    radial_max: float,
    start_angle: float,
    sweep_angle: float,
    z_min: float,
    height: float,
    angular_facets: int,
) -> cq.Workplane:
    segment_count = max(2, math.ceil(abs(sweep_angle) / 360.0 * angular_facets))
    angles = [
        math.radians(start_angle + sweep_angle * index / segment_count)
        for index in range(segment_count + 1)
    ]
    outer = [(radial_max * math.cos(a), radial_max * math.sin(a)) for a in angles]
    inner = [
        (radial_min * math.cos(a), radial_min * math.sin(a))
        for a in reversed(angles)
    ]
    return (
        cq.Workplane("XY")
        .polyline(outer + inner)
        .close()
        .extrude(height)
        .translate((0.0, 0.0, z_min))
    )


def _shortest_column_delta(first: int, second: int, columns: int) -> int:
    forward = (second - first) % columns
    return forward if forward <= columns // 2 else forward - columns


def _cell_z(row: int, config: BoxConfig, dimensions: DerivedDimensions) -> float:
    offset = row * dimensions.row_pitch
    if config.maze_location == "inner":
        return dimensions.maze_start_z + offset
    return dimensions.maze_end_z - offset


def _channel_radial_bounds(
    config: BoxConfig, dimensions: DerivedDimensions
) -> tuple[float, float]:
    if config.maze_location == "inner":
        return (
            dimensions.inner_outer_radius - config.channel_depth,
            dimensions.inner_outer_radius + BOOLEAN_OVERLAP,
        )
    return (
        dimensions.sleeve_inner_radius - BOOLEAN_OVERLAP,
        dimensions.sleeve_inner_radius + config.channel_depth,
    )


def _maze_cutters(
    maze: Maze, config: BoxConfig, dimensions: DerivedDimensions
) -> list[cq.Workplane]:
    radial_min, radial_max = _channel_radial_bounds(config, dimensions)
    angle_step = 360.0 / maze.columns
    half_width = config.channel_width / 2.0
    half_angle = math.degrees(half_width / dimensions.maze_radius)
    cutters: list[cq.Workplane] = []

    for first, second in sorted(maze.edges):
        first_z = _cell_z(first[0], config, dimensions)
        second_z = _cell_z(second[0], config, dimensions)
        first_angle = first[1] * angle_step

        if first[1] == second[1]:
            cutters.append(
                _radial_prism(
                    first_angle,
                    radial_min,
                    radial_max,
                    config.channel_width,
                    min(first_z, second_z) - half_width,
                    max(first_z, second_z) + half_width,
                )
            )
            continue

        column_delta = _shortest_column_delta(first[1], second[1], maze.columns)
        sweep = column_delta * angle_step
        direction = 1.0 if sweep > 0 else -1.0
        cutters.append(
            _annular_sector(
                radial_min,
                radial_max,
                first_angle - direction * half_angle,
                sweep + direction * 2.0 * half_angle,
                first_z - half_width,
                config.channel_width,
                dimensions.angular_facets,
            )
        )

    exit_angle = maze.exit[1] * angle_step
    exit_z = _cell_z(maze.exit[0], config, dimensions)
    if config.maze_location == "inner":
        lead_min = exit_z - half_width
        lead_max = dimensions.inner_height + BOOLEAN_OVERLAP
    else:
        lead_min = -BOOLEAN_OVERLAP
        lead_max = exit_z + half_width
    cutters.append(
        _radial_prism(
            exit_angle,
            radial_min,
            radial_max,
            config.channel_width,
            lead_min,
            lead_max,
        )
    )
    return cutters


def _cut_all(base: cq.Workplane, cutters: list[cq.Workplane]) -> cq.Workplane:
    shapes = [cutter.val() for cutter in cutters]
    result = base.val().cut(*shapes)
    return cq.Workplane("XY").newObject([result]).clean()


def _inner_cup(config: BoxConfig, dimensions: DerivedDimensions) -> cq.Workplane:
    body = (
        cq.Workplane("XY")
        .circle(dimensions.inner_outer_radius)
        .extrude(dimensions.inner_height)
    )
    cavity = (
        cq.Workplane("XY")
        .circle(config.cavity_diameter / 2.0)
        .extrude(config.cavity_length + BOOLEAN_OVERLAP)
        .translate((0.0, 0.0, config.bottom_thickness))
    )
    cup = body.cut(cavity)
    if config.grip_length > 0:
        grip = (
            cq.Workplane("XY")
            .circle(dimensions.grip_radius)
            .extrude(config.grip_length)
            .translate((0.0, 0.0, -config.grip_length))
        )
        cup = cup.union(grip)
    return cup.clean()


def _outer_sleeve(config: BoxConfig, dimensions: DerivedDimensions) -> cq.Workplane:
    body = (
        cq.Workplane("XY")
        .circle(dimensions.sleeve_outer_radius)
        .extrude(dimensions.sleeve_height)
    )
    bore = (
        cq.Workplane("XY")
        .circle(dimensions.sleeve_inner_radius)
        .extrude(dimensions.sleeve_inner_depth + BOOLEAN_OVERLAP)
        .translate((0.0, 0.0, -BOOLEAN_OVERLAP))
    )
    return body.cut(bore).clean()


def _decoration_radial_bounds(
    radius: float, config: BoxConfig
) -> tuple[float, float]:
    if config.decoration_mode == "emboss":
        return radius - BOOLEAN_OVERLAP, radius + config.decoration_depth
    return radius - config.decoration_depth, radius + BOOLEAN_OVERLAP


def _ring_tools(
    radius: float,
    z_min: float,
    z_max: float,
    allocated_count: int,
    config: BoxConfig,
) -> list[cq.Workplane]:
    radial_min, radial_max = _decoration_radial_bounds(radius, config)
    band_height = z_max - z_min
    pitch = band_height / allocated_count
    width = max(config.minimum_feature, min(0.45 * pitch, 2.4))
    return [
        (
            cq.Workplane("XY")
            .circle(radial_max)
            .circle(radial_min)
            .extrude(width)
            .translate((0.0, 0.0, z_min + (index + 0.5) * pitch - width / 2.0))
        )
        for index in range(allocated_count)
    ]


def _flute_tools(
    radius: float,
    z_min: float,
    z_max: float,
    config: BoxConfig,
) -> list[cq.Workplane]:
    radial_min, radial_max = _decoration_radial_bounds(radius, config)
    sweep = 0.45 * 360.0 / config.decoration_count
    return [
        _annular_sector(
            radial_min,
            radial_max,
            index * 360.0 / config.decoration_count - sweep / 2.0,
            sweep,
            z_min,
            z_max - z_min,
            max(config.angular_facets, config.decoration_count * 8),
        )
        for index in range(config.decoration_count)
    ]


def _diamond_tools(
    radius: float,
    z_min: float,
    z_max: float,
    config: BoxConfig,
) -> list[cq.Workplane]:
    radial_min, radial_max = _decoration_radial_bounds(radius, config)
    band_height = z_max - z_min
    circumference_pitch = 2.0 * math.pi * radius / config.decoration_count
    width = 0.55 * circumference_pitch
    target_height = min(1.25 * width, band_height)
    rows = max(1, min(8, math.floor(band_height / max(1.3 * target_height, 1e-9))))
    row_pitch = band_height / rows
    height = min(target_height, 0.70 * row_pitch)
    tools: list[cq.Workplane] = []
    for row in range(rows):
        center_z = z_min + (row + 0.5) * row_pitch
        for column in range(config.decoration_count):
            angle = column * 360.0 / config.decoration_count
            plane = cq.Plane(
                origin=(radial_min, 0.0, center_z),
                xDir=(0.0, 1.0, 0.0),
                normal=(1.0, 0.0, 0.0),
            )
            diamond = (
                cq.Workplane(plane)
                .polyline(
                    [
                        (-width / 2.0, 0.0),
                        (0.0, height / 2.0),
                        (width / 2.0, 0.0),
                        (0.0, -height / 2.0),
                    ]
                )
                .close()
                .extrude(radial_max - radial_min)
                .rotate((0, 0, 0), (0, 0, 1), angle)
            )
            tools.append(diamond)
    return tools


def _apply_ornament_band(
    base: cq.Workplane,
    radius: float,
    z_min: float,
    z_max: float,
    allocated_ring_count: int,
    config: BoxConfig,
) -> cq.Workplane:
    if z_max <= z_min:
        raise ValueError("ornament band must have positive height")
    if config.ornament_type == "rings":
        tools = _ring_tools(radius, z_min, z_max, allocated_ring_count, config)
    elif config.ornament_type == "flutes":
        tools = _flute_tools(radius, z_min, z_max, config)
    elif config.ornament_type == "diamonds":
        tools = _diamond_tools(radius, z_min, z_max, config)
    else:
        return base

    shapes = [tool.val() for tool in tools]
    if config.decoration_mode == "emboss":
        decorated = base.val().fuse(*shapes)
    else:
        decorated = base.val().cut(*shapes)
    result = cq.Workplane("XY").newObject([decorated]).clean()
    if not result.val().isValid() or len(result.solids().vals()) != 1:
        raise RuntimeError(
            f"{config.ornament_type} {config.decoration_mode} ornament did not "
            "produce one valid solid"
        )
    return result


def _apply_built_in_ornaments(
    inner: cq.Workplane,
    outer: cq.Workplane,
    config: BoxConfig,
    dimensions: DerivedDimensions,
) -> tuple[cq.Workplane, cq.Workplane]:
    if config.ornament_type == "none":
        return inner, outer

    margin = config.decoration_margin
    sleeve_height = dimensions.sleeve_height - 2.0 * margin
    grip_height = max(0.0, config.grip_length - 2.0 * margin)
    total_height = sleeve_height + grip_height
    sleeve_rings = max(
        1, round(config.decoration_count * sleeve_height / total_height)
    )
    outer = _apply_ornament_band(
        outer,
        dimensions.sleeve_outer_radius,
        margin,
        dimensions.sleeve_height - margin,
        sleeve_rings,
        config,
    )
    if config.grip_length > 0:
        grip_rings = max(1, config.decoration_count - sleeve_rings)
        inner = _apply_ornament_band(
            inner,
            dimensions.grip_radius,
            -config.grip_length + margin,
            -margin,
            grip_rings,
            config,
        )
    return inner, outer


def _follower_at(
    config: BoxConfig,
    dimensions: DerivedDimensions,
    angle_degrees: float,
    center_z: float,
) -> cq.Workplane:
    if config.maze_location == "inner":
        radial_min = dimensions.sleeve_inner_radius - dimensions.follower_projection
        radial_max = dimensions.sleeve_inner_radius + FOLLOWER_ATTACHMENT
    else:
        radial_min = dimensions.inner_outer_radius - FOLLOWER_ATTACHMENT
        radial_max = dimensions.inner_outer_radius + dimensions.follower_projection
    pin_plane = cq.Plane(
        origin=(radial_min, 0.0, center_z),
        xDir=(0.0, 1.0, 0.0),
        normal=(1.0, 0.0, 0.0),
    )
    pin = (
        cq.Workplane(pin_plane)
        .circle(dimensions.follower_width / 2.0)
        .extrude(radial_max - radial_min)
    )
    return pin.rotate((0, 0, 0), (0, 0, 1), angle_degrees)


def _follower(config: BoxConfig, dimensions: DerivedDimensions) -> cq.Workplane:
    center_z = (
        dimensions.maze_start_z
        if config.maze_location == "inner"
        else dimensions.maze_end_z
    )
    return _follower_at(config, dimensions, angle_degrees=0.0, center_z=center_z)


def build_labyrinth_box(config: BoxConfig) -> GeometryResult:
    """Build both parts after preflight and independent maze verification."""
    dimensions = validate_and_derive(config)
    selection = generate_maze_for_difficulty(
        rows=dimensions.rows,
        columns=dimensions.columns,
        seed=config.seed,
        difficulty=config.difficulty,
    )
    maze = selection.maze
    if len(maze.edges) != dimensions.rows * dimensions.columns - 1:
        raise RuntimeError("maze is not a spanning tree")
    if count_simple_paths(maze, maze.entry, maze.exit, limit=2) != 1:
        raise RuntimeError("maze does not have exactly one solution")

    inner = _inner_cup(config, dimensions)
    outer = _outer_sleeve(config, dimensions)
    cutters = _maze_cutters(maze, config, dimensions)
    follower = _follower(config, dimensions)

    if config.maze_location == "inner":
        inner = _cut_all(inner, cutters)
        outer = outer.union(follower).clean()
    else:
        outer = _cut_all(outer, cutters)
        inner = inner.union(follower).clean()

    inner, outer = _apply_built_in_ornaments(
        inner, outer, config, dimensions
    )

    return GeometryResult(
        config=config,
        dimensions=dimensions,
        maze=maze,
        metrics=selection.metrics,
        candidate_count=selection.candidate_count,
        inner=inner,
        outer=outer,
    )
