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
    return body.cut(cavity).clean()


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

    return GeometryResult(
        config=config,
        dimensions=dimensions,
        maze=maze,
        metrics=selection.metrics,
        candidate_count=selection.candidate_count,
        inner=inner,
        outer=outer,
    )
