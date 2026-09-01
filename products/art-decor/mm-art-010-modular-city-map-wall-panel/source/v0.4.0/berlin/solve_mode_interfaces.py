#!/usr/bin/env python3
"""Solve and audit rear interface placements for both Berlin display modes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw
from shapely import affinity
from shapely.geometry import MultiPolygon, Polygon, box, shape
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
PARAMETERS = json.loads((HERE / "production-mode-parameters.json").read_text())
BOUNDARY_PATH = PRODUCT / "source-data" / "v0.3.0" / "berlin" / "boundary.geojson"
INTERFACE_PARAMETERS_PATH = PRODUCT / "source" / "v0.3.0" / "interface-parameters.json"
INTERFACE_PARAMETERS = json.loads(INTERFACE_PARAMETERS_PATH.read_text())
OUTPUT_DIR = HERE / "placements"
REPORT_PATH = PRODUCT / "validation" / "v0.4.0" / "berlin" / "interface-placement-report.json"
PREVIEW_PATH = PRODUCT / "validation" / "v0.4.0" / "berlin" / "renders" / "interface-placement-preview.png"

BOUNDARY_CONNECTOR_TARGET_Y = [120.0, 232.0, 344.0]
BOUNDARY_MOUNT_TARGETS = {
    "upper_hanger_left": [170.0, 320.0],
    "lower_standoff_left": [150.0, 120.0],
    "upper_hanger_right": [430.0, 320.0],
    "lower_standoff_right": [450.0, 80.0],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def polygons(geometry):
    if isinstance(geometry, Polygon):
        yield geometry
    elif isinstance(geometry, MultiPolygon):
        yield from geometry.geoms
    elif hasattr(geometry, "geoms"):
        for child in geometry.geoms:
            yield from polygons(child)


def load_boundary():
    data = json.loads(BOUNDARY_PATH.read_text())
    return unary_union([shape(feature["geometry"]) for feature in data["features"]])


def boundary_crop_geometry(boundary):
    minx, miny, maxx, maxy = boundary.bounds
    scale = min(600.0 / (maxx - minx), 400.0 / (maxy - miny))
    tx = (600.0 - (maxx - minx) * scale) / 2.0 - minx * scale
    ty = (400.0 - (maxy - miny) * scale) / 2.0 - miny * scale
    transformed = affinity.translate(
        affinity.scale(boundary, xfact=scale, yfact=scale, origin=(0.0, 0.0)), tx, ty
    )
    return transformed, {
        "source_bounds_epsg25833": list(boundary.bounds),
        "uniform_scale_mm_per_source_m": scale,
        "translate_mm": [tx, ty],
        "result_bounds_mm": list(transformed.bounds),
    }


def context_transform_record(boundary):
    bounds = PARAMETERS["modes"]["context_outline"]["frame_aspect_policy"]["default_result"]["bounds_epsg25833"]
    minx, miny, maxx, maxy = bounds
    sx = 600.0 / (maxx - minx)
    sy = 400.0 / (maxy - miny)
    if abs(sx - sy) > 1e-12:
        raise ValueError("context extent is not exactly compatible with the 3:2 frame")
    tx = -minx * sx
    ty = -miny * sx
    transformed_boundary = affinity.translate(
        affinity.scale(boundary, xfact=sx, yfact=sx, origin=(0.0, 0.0)), tx, ty
    )
    return transformed_boundary, {
        "source_bounds_epsg25833": bounds,
        "uniform_scale_mm_per_source_m": sx,
        "translate_mm": [tx, ty],
        "result_bounds_mm": [0.0, 0.0, 600.0, 400.0],
        "berlin_boundary_bounds_mm": list(transformed_boundary.bounds),
    }


def connector_protected_footprint(y: float):
    # Pocket reaches 16.25 mm into each half. Five millimetres of retained body
    # and handling ligament are included in this conservative proxy.
    return box(278.75, y - 8.0, 321.25, y + 8.0)


def connector_actual_footprint(y: float):
    clearance = INTERFACE_PARAMETERS["connector"]["selected_provisional_clearance_per_side"]
    half_width = INTERFACE_PARAMETERS["connector"]["barb_outer_width"] / 2.0 + clearance
    return box(300.0 - 16.0 - clearance, y - half_width, 300.0 + 16.0 + clearance, y + half_width)


def mount_protected_footprint(x: float, y: float):
    # Upper hanger is the larger counterpart: actual [-8,+20] x [-16,+16]
    # about the socket origin, plus five millimetres retained perimeter reserve.
    return box(x - 13.0, y - 21.0, x + 25.0, y + 21.0)


def mount_actual_footprint(x: float, y: float):
    return box(x - 8.0, y - 16.0, x + 20.0, y + 16.0)


def nearest_safe_connector(outer, target_y: float, used: list[float]) -> float:
    candidates = [float(value) for value in range(40, 361, 2)]
    candidates.sort(key=lambda value: (abs(value - target_y), value))
    for y in candidates:
        if any(abs(y - other) < 80.0 for other in used):
            continue
        if outer.covers(connector_protected_footprint(y)):
            return y
    raise ValueError(f"no safe connector station near Y={target_y}")


def nearest_safe_mount(outer, target: list[float], side: str, occupied) -> list[float]:
    x_range = range(45, 276, 5) if side == "left" else range(325, 556, 5)
    candidates = []
    for y in range(35, 366, 5):
        for x in x_range:
            protected = mount_protected_footprint(float(x), float(y))
            if not outer.covers(protected):
                continue
            if any(protected.intersects(other.buffer(8.0)) for other in occupied):
                continue
            score = abs(y - target[1]) + 0.35 * abs(x - target[0])
            candidates.append((score, float(x), float(y)))
    if not candidates:
        raise ValueError(f"no safe {side} mount near {target}")
    _, x, y = min(candidates)
    return [x, y]


def solve(mode: str, outer, transform):
    if mode == "context_outline":
        connector_y = [float(value) for value in INTERFACE_PARAMETERS["panel"]["connector_y_positions"]]
        mounts = {
            kind: [float(x), float(y)]
            for x, y, kind in INTERFACE_PARAMETERS["panel"]["socket_centers_global"]
        }
    else:
        connector_y = []
        for target in BOUNDARY_CONNECTOR_TARGET_Y:
            connector_y.append(nearest_safe_connector(outer, target, connector_y))
        occupied = [connector_protected_footprint(y) for y in connector_y]
        mounts = {}
        for kind in (
            "upper_hanger_left",
            "lower_standoff_left",
            "upper_hanger_right",
            "lower_standoff_right",
        ):
            side = "left" if kind.endswith("left") else "right"
            point = nearest_safe_mount(outer, BOUNDARY_MOUNT_TARGETS[kind], side, occupied)
            mounts[kind] = point
            occupied.append(mount_protected_footprint(*point))

    connector_checks = []
    for y in connector_y:
        actual = connector_actual_footprint(y)
        connector_checks.append({
            "y_mm": y,
            "actual_footprint_within_outer": outer.covers(actual),
            "protected_footprint_within_outer": outer.covers(connector_protected_footprint(y)),
            "minimum_outer_ligament_mm": outer.boundary.distance(actual),
        })
    mount_checks = []
    for kind, (x, y) in mounts.items():
        actual = mount_actual_footprint(x, y)
        mount_checks.append({
            "kind": kind,
            "center_mm": [x, y],
            "actual_footprint_within_outer": outer.covers(actual),
            "protected_footprint_within_outer": outer.covers(mount_protected_footprint(x, y)),
            "minimum_outer_ligament_mm": outer.boundary.distance(actual),
        })
    checks = connector_checks + mount_checks
    status = "PASS" if all(
        item["actual_footprint_within_outer"]
        and item["protected_footprint_within_outer"]
        and item["minimum_outer_ligament_mm"] >= 4.99
        for item in checks
    ) else "FAIL"
    return {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.4.0",
        "mode": mode,
        "status": status,
        "transform": transform,
        "outer_bounds_mm": list(outer.bounds),
        "outer_area_mm2": outer.area,
        "connector_y_positions_mm": connector_y,
        "socket_centers_global_mm": mounts,
        "connector_checks": connector_checks,
        "mount_checks": mount_checks,
        "rear_halo_route": {
            "construction": "boundary of retained outer body after a 14 mm inward offset; local gaps around mounts, seam and cable exits are applied by the production build",
            "nominal_led_keepout_mm": [12.0, 4.0],
            "wall_gap_mm": 18.0,
        },
        "physical_gate": "The 0.25 mm process compensation remains provisional until the exact Kobra 3 Max/filament/profile coupon passes.",
    }


def draw_preview(entries):
    scale = 2
    image = Image.new("RGB", (1200, 800), "#F3F0EA")
    draw = ImageDraw.Draw(image)
    for index, (mode, outer, manifest) in enumerate(entries):
        xoff = index * 600
        for polygon in polygons(outer):
            points = [(xoff + x * scale / 2, (400.0 - y) * scale) for x, y in polygon.exterior.coords]
            draw.polygon(points, fill="#E9E1D0", outline="#171717", width=2)
        split_x = xoff + 300
        draw.line((split_x, 0, split_x, 800), fill="#F05A24", width=2)
        for y in manifest["connector_y_positions_mm"]:
            draw.rectangle((split_x - 12, (400 - y) * scale - 5, split_x + 12, (400 - y) * scale + 5), fill="#171717")
        for kind, (x, y) in manifest["socket_centers_global_mm"].items():
            color = "#F05A24" if kind.startswith("upper") else "#73777A"
            cx = xoff + x
            cy = (400 - y) * scale
            draw.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=color, outline="#171717")
        draw.text((xoff + 12, 12), mode, fill="#171717")
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(PREVIEW_PATH)


def main():
    outputs = [
        OUTPUT_DIR / "boundary-crop-placement.json",
        OUTPUT_DIR / "context-outline-placement.json",
        REPORT_PATH,
        PREVIEW_PATH,
    ]
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        raise SystemExit("Refusing destructive overwrite of: " + ", ".join(existing))
    boundary = load_boundary()
    boundary_outer, boundary_transform = boundary_crop_geometry(boundary)
    _, context_transform = context_transform_record(boundary)
    entries = [
        ("boundary_crop", boundary_outer, solve("boundary_crop", boundary_outer, boundary_transform)),
        ("context_outline", box(0.0, 0.0, 600.0, 400.0), solve("context_outline", box(0.0, 0.0, 600.0, 400.0), context_transform)),
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for mode, _outer, manifest in entries:
        name = mode.replace("_", "-") + "-placement.json"
        (OUTPUT_DIR / name).write_text(json.dumps(manifest, indent=2) + "\n")
    draw_preview(entries)
    status = "PASS" if all(item[2]["status"] == "PASS" for item in entries) else "FAIL"
    report = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "revision": "0.4.0",
        "status": status,
        "inputs": {
            "boundary": {"path": str(BOUNDARY_PATH.relative_to(PRODUCT)), "sha256": sha256(BOUNDARY_PATH)},
            "display_parameters": {"path": str((HERE / "production-mode-parameters.json").relative_to(PRODUCT)), "sha256": sha256(HERE / "production-mode-parameters.json")},
            "interface_parameters": {"path": str(INTERFACE_PARAMETERS_PATH.relative_to(PRODUCT)), "sha256": sha256(INTERFACE_PARAMETERS_PATH)},
        },
        "modes": {mode: manifest for mode, _outer, manifest in entries},
        "preview": str(PREVIEW_PATH.relative_to(PRODUCT)),
        "limitations": [
            "This is a deterministic proxy/ligament audit, not physical connector, hanger or wall-load qualification.",
            "Wall hardware and customer lighting remain excluded purchased systems.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": status, "report": str(REPORT_PATH), "placements": [str(path) for path in outputs[:2]]}))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
