"""Shared 2D footprint contract for DrawerFit CAD and exact paper templates."""
from __future__ import annotations

import math
from shapely.geometry import Polygon


def footprint_points(preset: dict, clearance_mm: float) -> list[tuple[float, float]]:
    length, width = preset["length_mm"], preset["width_mm"]
    if preset["id"] == "round-corner":
        radius = preset["obstruction_radius_mm"] + clearance_mm
        points = [(radius, 0.0), (length, 0.0), (length, width), (0.0, width), (0.0, radius)]
        for index in range(1, preset["arc_segments"]):
            angle = math.pi / 2 * (1 - index / preset["arc_segments"])
            points.append((radius * math.cos(angle), radius * math.sin(angle)))
        return points
    if preset["id"] == "rectangular-notch":
        notch_w = preset["notch_width_mm"] + clearance_mm
        notch_h = preset["notch_height_mm"] + clearance_mm
        return [(notch_w, 0.0), (length, 0.0), (length, width), (0.0, width), (0.0, notch_h), (notch_w, notch_h)]
    if preset["id"] == "skewed-corner":
        cut_x = preset["corner_cut_x_mm"] + clearance_mm
        cut_y = preset["corner_cut_y_mm"] + clearance_mm
        return [(cut_x, 0.0), (length, 0.0), (length, width), (0.0, width), (0.0, cut_y)]
    raise ValueError(f"unsupported preset {preset['id']}")


def footprint_polygon(preset: dict, clearance_mm: float) -> Polygon:
    polygon = Polygon(footprint_points(preset, clearance_mm))
    if not polygon.is_valid or polygon.area <= 0:
        raise ValueError(f"invalid footprint for {preset['id']}")
    return polygon


def inner_polygon(preset: dict, clearance_mm: float, wall_mm: float) -> Polygon:
    inner = footprint_polygon(preset, clearance_mm).buffer(-wall_mm, join_style=2)
    if inner.geom_type != "Polygon" or not inner.is_valid or inner.area <= 0:
        raise ValueError(f"wall offset collapses {preset['id']}")
    return inner
