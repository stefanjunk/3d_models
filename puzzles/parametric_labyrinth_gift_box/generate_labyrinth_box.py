#!/usr/bin/env python3
"""Generate both printable parts of a parametric cylindrical labyrinth box."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Sequence

import cadquery as cq

from labyrinth_box.config import BoxConfig
from labyrinth_box.geometry import GeometryResult, build_labyrinth_box
from labyrinth_box.maze import count_simple_paths
from labyrinth_box.preflight import UnsafeParametersError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a two-piece, uniquely solvable cylindrical gift box."
    )
    parser.add_argument("--cavity-diameter", type=float, default=40.0)
    parser.add_argument("--cavity-length", type=float, default=80.0)
    parser.add_argument("--difficulty", type=int, choices=range(1, 11), default=5)
    parser.add_argument(
        "--maze-location", choices=("inner", "outer"), default="inner"
    )
    parser.add_argument("--seed", type=int, default=20260805)
    parser.add_argument("--inner-wall", type=float, default=3.2)
    parser.add_argument("--outer-wall", type=float, default=3.2)
    parser.add_argument("--bottom-thickness", type=float, default=2.4)
    parser.add_argument("--cap-thickness", type=float, default=2.4)
    parser.add_argument("--radial-clearance", type=float, default=0.35)
    parser.add_argument("--axial-clearance", type=float, default=0.5)
    parser.add_argument("--channel-width", type=float, default=2.0)
    parser.add_argument("--channel-depth", type=float, default=1.2)
    parser.add_argument("--follower-clearance", type=float, default=0.25)
    parser.add_argument("--follower-tip-clearance", type=float, default=0.2)
    parser.add_argument("--maze-margin", type=float, default=4.0)
    parser.add_argument("--minimum-wall", type=float, default=1.6)
    parser.add_argument("--minimum-web", type=float, default=1.2)
    parser.add_argument("--minimum-feature", type=float, default=0.8)
    parser.add_argument("--angular-facets", type=int, default=96)
    parser.add_argument("--stl-tolerance", type=float, default=0.08)
    parser.add_argument("--stl-angular-tolerance", type=float, default=0.15)
    parser.add_argument("--output-dir", type=Path, default=Path("exports/default"))
    return parser


def _config_from_args(args: argparse.Namespace) -> BoxConfig:
    return BoxConfig(
        cavity_diameter=args.cavity_diameter,
        cavity_length=args.cavity_length,
        difficulty=args.difficulty,
        maze_location=args.maze_location,
        seed=args.seed,
        inner_wall=args.inner_wall,
        outer_wall=args.outer_wall,
        bottom_thickness=args.bottom_thickness,
        cap_thickness=args.cap_thickness,
        radial_clearance=args.radial_clearance,
        axial_clearance=args.axial_clearance,
        channel_width=args.channel_width,
        channel_depth=args.channel_depth,
        follower_clearance=args.follower_clearance,
        follower_tip_clearance=args.follower_tip_clearance,
        maze_margin=args.maze_margin,
        minimum_wall=args.minimum_wall,
        minimum_web=args.minimum_web,
        minimum_feature=args.minimum_feature,
        angular_facets=args.angular_facets,
        stl_tolerance=args.stl_tolerance,
        stl_angular_tolerance=args.stl_angular_tolerance,
    )


def _manifest(result: GeometryResult) -> dict[str, object]:
    maze = result.maze
    return {
        "schema_version": 1,
        "units": "mm",
        "config": asdict(result.config),
        "derived": asdict(result.dimensions),
        "maze": {
            "rows": maze.rows,
            "columns": maze.columns,
            "requested_seed": result.config.seed,
            "selected_seed": maze.seed,
            "entry": maze.entry,
            "exit": maze.exit,
            "edges": sorted(maze.edges),
            "solution": maze.solution,
            "unique_solution_count": count_simple_paths(
                maze, maze.entry, maze.exit, limit=2
            ),
        },
        "difficulty_metrics": asdict(result.metrics),
        "candidate_count": result.candidate_count,
        "print_orientation": {
            "inner": "base_down",
            "outer": "cap_down",
        },
        "files": {
            "inner_stl": "inner.stl",
            "outer_stl": "outer.stl",
            "inner_step": "inner.step",
            "outer_step": "outer.step",
            "assembly_step": "assembly.step",
        },
    }


def export_box(result: GeometryResult, output_directory: Path) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    config = result.config
    dimensions = result.dimensions

    outer_print = result.outer.rotate((0, 0, 0), (1, 0, 0), 180).translate(
        (0, 0, dimensions.sleeve_height)
    )
    cq.exporters.export(
        result.inner,
        str(output_directory / "inner.stl"),
        tolerance=config.stl_tolerance,
        angularTolerance=config.stl_angular_tolerance,
    )
    cq.exporters.export(
        outer_print,
        str(output_directory / "outer.stl"),
        tolerance=config.stl_tolerance,
        angularTolerance=config.stl_angular_tolerance,
    )
    cq.exporters.export(result.inner, str(output_directory / "inner.step"))
    cq.exporters.export(outer_print, str(output_directory / "outer.step"))

    assembly = cq.Assembly(name="labyrinth_gift_box")
    assembly.add(result.inner, name="inner", color=cq.Color(0.25, 0.55, 0.85))
    assembly.add(
        result.outer.translate((2.4 * dimensions.sleeve_outer_radius, 0, 0)),
        name="outer",
        color=cq.Color(0.85, 0.45, 0.20),
    )
    assembly.export(str(output_directory / "assembly.step"))

    (output_directory / "maze.json").write_text(
        json.dumps(_manifest(result), indent=2) + "\n", encoding="utf-8"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = _config_from_args(args)
    try:
        result = build_labyrinth_box(config)
        export_box(result, args.output_dir)
    except UnsafeParametersError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(
        f"Exported {result.dimensions.rows}x{result.dimensions.columns} "
        f"{config.maze_location}-maze box to {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
