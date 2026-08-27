#!/usr/bin/env python3
"""Generate both printable parts of a parametric cylindrical labyrinth box."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import tempfile
from typing import Sequence

import cadquery as cq

from labyrinth_box.config import BoxConfig
from labyrinth_box.errors import ImageReliefError
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
    parser.add_argument(
        "--grip-length",
        type=float,
        default=15.0,
        help="solid grip collar length below the cup in mm; 0 disables it",
    )
    parser.add_argument("--channel-width", type=float, default=2.0)
    parser.add_argument("--channel-depth", type=float, default=1.2)
    parser.add_argument("--follower-clearance", type=float, default=0.25)
    parser.add_argument("--follower-tip-clearance", type=float, default=0.2)
    parser.add_argument("--maze-margin", type=float, default=4.0)
    parser.add_argument(
        "--ornament-type",
        choices=("none", "flutes", "diamonds", "rings"),
        default="none",
        help="optional exact B-Rep ornament on the sleeve and enabled grip",
    )
    parser.add_argument(
        "--decoration-mode",
        choices=("engrave", "emboss"),
        default="engrave",
        help="cut decorations inward or raise them outward",
    )
    parser.add_argument(
        "--decoration-depth",
        type=float,
        default=0.6,
        help="ornament and image-relief depth in mm (0.2 to 2.0)",
    )
    parser.add_argument(
        "--decoration-count",
        type=int,
        default=16,
        help="repeat count for built-in ornaments (3 to 128)",
    )
    parser.add_argument(
        "--decoration-margin",
        type=float,
        default=3.0,
        help="blank margin in mm at bottoms, tops, and both sides of the seam",
    )
    parser.add_argument(
        "--image-relief",
        dest="image_relief_path",
        type=Path,
        help="optional grayscale image for detailed STL-only 360-degree relief",
    )
    parser.add_argument(
        "--image-relief-resolution",
        type=int,
        default=256,
        help="circumferential image samples (32 to 1024)",
    )
    parser.add_argument(
        "--image-relief-invert",
        action="store_true",
        help="make light pixels stronger instead of dark pixels",
    )
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
        grip_length=args.grip_length,
        channel_width=args.channel_width,
        channel_depth=args.channel_depth,
        follower_clearance=args.follower_clearance,
        follower_tip_clearance=args.follower_tip_clearance,
        maze_margin=args.maze_margin,
        ornament_type=args.ornament_type,
        decoration_mode=args.decoration_mode,
        decoration_depth=args.decoration_depth,
        decoration_count=args.decoration_count,
        decoration_margin=args.decoration_margin,
        image_relief_path=(
            str(args.image_relief_path) if args.image_relief_path is not None else None
        ),
        image_relief_resolution=args.image_relief_resolution,
        image_relief_invert=args.image_relief_invert,
        minimum_wall=args.minimum_wall,
        minimum_web=args.minimum_web,
        minimum_feature=args.minimum_feature,
        angular_facets=args.angular_facets,
        stl_tolerance=args.stl_tolerance,
        stl_angular_tolerance=args.stl_angular_tolerance,
    )


def _manifest(
    result: GeometryResult,
    image_relief_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    maze = result.maze
    requested = result.config.image_relief_path is not None
    source_image_name = (
        Path(result.config.image_relief_path).name if requested else None
    )
    relief = {
        "requested": requested,
        "source_image": source_image_name,
        "resolution": result.config.image_relief_resolution,
        "invert": result.config.image_relief_invert,
        "dark_pixels_are_stronger": not result.config.image_relief_invert,
        "stl_includes_raster_relief": requested,
        "step_includes_raster_relief": False,
    }
    if image_relief_metadata:
        relief.update(image_relief_metadata)
    config_record = asdict(result.config)
    if requested:
        config_record["image_relief_path"] = source_image_name
    return {
        "schema_version": 2,
        "units": "mm",
        "config": config_record,
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
            "inner": "grip_down" if result.config.grip_length > 0 else "base_down",
            "outer": "cap_down",
            "inner_note": "translated from assembly coordinates so exported zmin is 0",
            "outer_note": "rotated 180 degrees from assembly coordinates",
        },
        "exact_brep": {
            "includes_grip": result.config.grip_length > 0,
            "includes_built_in_ornaments": result.config.ornament_type != "none",
            "includes_raster_image_relief": False,
        },
        "image_relief": relief,
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

def _write_print_files(
    result: GeometryResult,
    inner_print: cq.Workplane,
    outer_print: cq.Workplane,
    target: Path,
) -> None:
    config = result.config
    dimensions = result.dimensions

    cq.exporters.export(
        inner_print,
        str(target / "inner.stl"),
        tolerance=config.stl_tolerance,
        angularTolerance=config.stl_angular_tolerance,
    )
    cq.exporters.export(
        outer_print,
        str(target / "outer.stl"),
        tolerance=config.stl_tolerance,
        angularTolerance=config.stl_angular_tolerance,
    )
    cq.exporters.export(inner_print, str(target / "inner.step"))
    cq.exporters.export(outer_print, str(target / "outer.step"))

    assembly = cq.Assembly(name="labyrinth_gift_box")
    assembly.add(result.inner, name="inner", color=cq.Color(0.25, 0.55, 0.85))
    assembly.add(
        result.outer.translate((2.4 * dimensions.sleeve_outer_radius, 0, 0)),
        name="outer",
        color=cq.Color(0.85, 0.45, 0.20),
    )
    assembly.export(str(target / "assembly.step"))


def export_box(result: GeometryResult, output_directory: Path) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    config = result.config
    dimensions = result.dimensions

    inner_print = result.inner.translate((0.0, 0.0, config.grip_length))
    outer_print = result.outer.rotate((0, 0, 0), (1, 0, 0), 180).translate(
        (0, 0, dimensions.sleeve_height)
    )

    image_relief_metadata: dict[str, object] | None = None
    if config.image_relief_path is not None:
        from labyrinth_box.image_relief import apply_image_relief_to_exports

        with tempfile.TemporaryDirectory(dir=output_directory) as staging_name:
            staging = Path(staging_name)
            _write_print_files(result, inner_print, outer_print, staging)
            image_relief_metadata = apply_image_relief_to_exports(
                config, dimensions, staging
            )
            for staged in sorted(staging.iterdir()):
                staged.rename(output_directory / staged.name)
    else:
        _write_print_files(result, inner_print, outer_print, output_directory)

    (output_directory / "maze.json").write_text(
        json.dumps(_manifest(result, image_relief_metadata), indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = _config_from_args(args)
    try:
        result = build_labyrinth_box(config)
        export_box(result, args.output_dir)
    except (UnsafeParametersError, ImageReliefError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(
        f"Exported {result.dimensions.rows}x{result.dimensions.columns} "
        f"{config.maze_location}-maze box to {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
