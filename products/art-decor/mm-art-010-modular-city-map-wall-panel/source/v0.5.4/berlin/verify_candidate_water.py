#!/usr/bin/env python3
"""Independently verify water openings in an exported MM-ART-010 candidate.

The revision 0.5.3 build reported Tegeler See as retained because its accounting
ran on an intermediate raster.  This checker never looks at the build's own
arrays.  It sections the exported tool-1 land base of both halves, rebuilds the
solid land polygon, and measures how much of each mapped water body is still
solid material in the artefact that ships.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import shape
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
BASE_SCRIPT = PRODUCT / "source" / "v0.4.0" / "berlin" / "build_berlin_modes.py"
SEAM_GAP_MM = 0.25

MODES = {
    "boundary_crop": "boundary-crop",
    "context_outline": "context-outline",
}


def load_base(source: Path):
    spec = importlib.util.spec_from_file_location("mm_art_010_base_verify", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load base generator: {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SOURCE = source
    return module


def land_polygon(path: Path, x_offset: float):
    mesh = trimesh.load(path, process=False)
    z = (mesh.bounds[0][2] + mesh.bounds[1][2]) / 2.0
    section = mesh.section(plane_origin=[0.0, 0.0, z], plane_normal=[0.0, 0.0, 1.0])
    if section is None:
        raise ValueError(f"no cross-section at z={z} in {path}")
    planar, _ = section.to_planar(to_2D=np.eye(4))
    return affinity.translate(unary_union(list(planar.polygons_full)), x_offset, 0.0)


def transformed(geometry, transform: dict):
    scale = transform["uniform_scale_mm_per_source_m"]
    tx, ty = transform["translate_mm"]
    return affinity.translate(
        affinity.scale(geometry, xfact=scale, yfact=scale, origin=(0.0, 0.0)), tx, ty
    )


def named_official(source: Path) -> dict[str, list]:
    grouped: dict[str, list] = {}
    for feature in json.loads((source / "water-areas-berlin-official.geojson").read_text())["features"]:
        name = (feature.get("properties") or {}).get("gewname")
        geometry = feature.get("geometry")
        if not name or not geometry:
            continue
        polygon = shape(geometry)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        grouped.setdefault(name, []).append(polygon)
    return grouped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default="v0.5.4")
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--source", default=None, help="source-data directory, defaults to the revision")
    parser.add_argument("--minimum-named-open-fraction", type=float, default=0.85)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    source = Path(args.source) if args.source else PRODUCT / "source-data" / args.revision / "berlin"
    base = load_base(source)
    boundary = base.read_geojson(source / "boundary.geojson")
    production = base.read_geojson(source / "water-areas.geojson")
    official = named_official(source)
    export_root = PRODUCT / "exports" / args.revision / "berlin" / args.candidate

    result = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": args.revision,
        "candidate": args.candidate,
        "method": "cross-section of the exported tool-1 land base at mid thickness; water is 'open' where it is not inside that solid polygon",
        "source_data": str(source.relative_to(PRODUCT)),
        "minimum_named_open_fraction": args.minimum_named_open_fraction,
        "modes": {},
    }
    failures: list[str] = []
    for mode, folder in MODES.items():
        _, placement = base.load_placement(mode)
        transform = placement["transform"]
        outer = base.outer_geometry(mode, boundary, placement)
        prefix = export_root / folder / f"berlin-{folder}"
        land = unary_union([
            land_polygon(Path(f"{prefix}-left-tool1-base.stl"), 0.0),
            land_polygon(Path(f"{prefix}-right-tool1-base.stl"), 300.0 + SEAM_GAP_MM / 2.0),
        ])
        water = transformed(production, transform).intersection(outer)
        solid = water.intersection(land).area
        rows = []
        for name, parts in sorted(official.items()):
            geometry = transformed(unary_union(parts), transform).intersection(outer)
            mapped = geometry.intersection(water)
            if mapped.is_empty or mapped.area < 20.0:
                continue
            open_area = mapped.area - mapped.intersection(land).area
            rows.append({
                "name": name,
                "mapped_area_mm2": mapped.area,
                "open_area_mm2": open_area,
                "open_fraction": open_area / mapped.area,
            })
        rows.sort(key=lambda row: row["open_fraction"])
        below = [row for row in rows if row["open_fraction"] < args.minimum_named_open_fraction]
        mode_result = {
            "outer_area_mm2": outer.area,
            "land_area_mm2": land.area,
            "water_in_panel_area_mm2": water.area,
            "water_open_area_mm2": water.area - solid,
            "water_open_fraction": (water.area - solid) / water.area if water.area else 0.0,
            "named_water": rows,
            "named_water_below_threshold": below,
        }
        result["modes"][mode] = mode_result
        for row in below:
            failures.append(f"{mode}/{row['name']} open {row['open_fraction']:.3f}")
    result["status"] = "PASS" if not failures else "REVIEW_REQUIRED"
    result["below_threshold"] = failures

    output = Path(args.output) if args.output else (
        PRODUCT / "validation" / args.revision / "berlin" / args.candidate / "exported-water-verification.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    for mode, data in result["modes"].items():
        print(f"{mode}: water {data['water_in_panel_area_mm2']:.0f} mm2, open "
              f"{data['water_open_area_mm2']:.0f} mm2 = {data['water_open_fraction']*100:.1f}%")
        for row in data["named_water_below_threshold"][:12]:
            print(f"   below threshold: {row['name']:36s} {row['open_fraction']*100:5.1f}% "
                  f"({row['mapped_area_mm2']:.0f} mm2)")
    print(json.dumps({"status": result["status"], "report": str(output)}, indent=2))


if __name__ == "__main__":
    main()
