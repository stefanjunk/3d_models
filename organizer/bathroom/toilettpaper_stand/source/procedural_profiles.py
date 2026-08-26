"""Low-dimensional deterministic profiles for ZEN KINTSUGI WAVE R3.

All coordinates are millimetres. These functions define sparse curves and
buffered vector ribbons; no image, raster height field, or imported mesh is
used anywhere in the production geometry.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np
from scipy.interpolate import splprep, splev
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union


def rounded_rectangle(x0: float, y0: float, x1: float, y1: float, radius: float) -> Polygon:
    """Return a valid rounded rectangle with a bounded corner radius."""
    if x1 <= x0 or y1 <= y0:
        raise ValueError("Rounded rectangle requires positive dimensions")
    radius = min(radius, (x1 - x0) / 2.0, (y1 - y0) / 2.0)
    if radius <= 0:
        return box(x0, y0, x1, y1)
    return box(x0 + radius, y0 + radius, x1 - radius, y1 - radius).buffer(
        radius, resolution=12, join_style=1
    )


def sample_spline(
    controls: Sequence[tuple[float, float]],
    samples: int = 48,
    smoothing: float = 0.0,
) -> list[tuple[float, float]]:
    """Sample a cubic approximating B-spline through semantic controls."""
    if len(controls) < 2:
        raise ValueError("At least two spline controls are required")
    points = np.asarray(controls, dtype=float)
    degree = min(3, len(points) - 1)
    tck, _ = splprep([points[:, 0], points[:, 1]], s=smoothing, k=degree)
    u = np.linspace(0.0, 1.0, max(samples, len(points) * 8))
    x_values, y_values = splev(u, tck)
    return list(zip(np.asarray(x_values), np.asarray(y_values), strict=True))


def spline_ribbon(
    controls: Sequence[tuple[float, float]],
    width: float,
    samples: int = 48,
    smoothing: float = 0.0,
) -> Polygon:
    if width <= 0:
        raise ValueError("Ribbon width must be positive")
    return LineString(sample_spline(controls, samples, smoothing)).buffer(
        width / 2.0,
        cap_style=1,
        join_style=1,
        resolution=4,
    )


def side_frame_profile(depth: float, height: float, phase: float = 0.0) -> Polygon:
    """Open side frame in local (depth, height) coordinates."""
    outer = rounded_rectangle(0.0, 0.0, depth, height, 5.0)
    margin_y = 11.0
    margin_z = 7.0
    inner = rounded_rectangle(
        margin_y,
        margin_z,
        depth - margin_y,
        height - margin_z,
        8.0,
    )
    frame = outer.difference(inner)

    # One continuous S-rib replaces the dense legacy lattice. The rib remains
    # outside the roll swept volume because the complete profile is extruded
    # only in the external side-frame plane.
    controls = [
        (margin_y + 2.0, margin_z + 7.0),
        (depth * (0.36 + 0.03 * np.sin(phase)), height * 0.32),
        (depth * (0.63 + 0.03 * np.cos(phase)), height * 0.66),
        (depth - margin_y - 2.0, height - margin_z - 7.0),
    ]
    rib = spline_ribbon(controls, 6.0, samples=40)
    return unary_union([frame, rib]).intersection(outer).buffer(0)


def front_rail_profile(
    outer_half_width: float,
    height: float,
    opening_half_width: float,
    output_module: bool,
) -> Polygon:
    """Paired front rails in local (width, height) coordinates."""
    rail_outer = outer_half_width
    normal_inner = opening_half_width
    if output_module:
        # Widen only the lower output region, then transition smoothly to the
        # retaining opening above it.
        transition_z = min(138.0, height * 0.58)
        output_inner = min(outer_half_width - 2.0, opening_half_width + 3.0)
        left_controls = [
            (-rail_outer, 0.0),
            (-output_inner, 0.0),
            (-output_inner, transition_z * 0.72),
            (-normal_inner, transition_z),
            (-normal_inner, height),
            (-rail_outer, height),
        ]
        left = Polygon(left_controls).buffer(1.2, join_style=1).intersection(
            box(-rail_outer, 0.0, -normal_inner + 1.2, height)
        )
    else:
        left = rounded_rectangle(-rail_outer, 0.0, -normal_inner, height, 3.0)
    right = Polygon([(-x, z) for x, z in reversed(list(left.exterior.coords))]).buffer(0)
    return unary_union([left, right]).buffer(0)


def skin_outline(depth: float, height: float, margin: float) -> Polygon:
    return rounded_rectangle(margin, margin, depth - margin, height - margin, 6.0)


def skin_wave_grooves(
    depth: float,
    height: float,
    margin: float,
    width: float,
    phase: float,
) -> Polygon:
    """Three fair nested spline grooves clipped to a safe skin inset."""
    safe = skin_outline(depth, height, margin + 5.0)
    ribbons = []
    for index, offset in enumerate((-0.08, 0.0, 0.08)):
        controls = [
            (margin + 7.0, height * (0.10 + offset)),
            (depth * (0.30 + 0.02 * np.sin(phase + index)), height * (0.27 + offset)),
            (depth * (0.58 + 0.02 * np.cos(phase + index)), height * (0.52 + offset)),
            (depth - margin - 7.0, height * (0.82 + offset)),
        ]
        ribbons.append(spline_ribbon(controls, width, samples=44))
    return unary_union(ribbons).intersection(safe).buffer(0)


def skin_kintsugi_network(
    depth: float,
    height: float,
    margin: float,
    width: float,
    phase: float,
    keepout_centers: Iterable[tuple[float, float]] = (),
    keepout_radius: float = 7.0,
) -> Polygon:
    """Sparse trunk plus two branches, clipped away from fastener keep-outs."""
    safe = skin_outline(depth, height, margin + 4.0)
    drift = 0.035 * np.sin(phase)
    trunk_controls = [
        (depth * (0.24 + drift), height - margin - 6.0),
        (depth * (0.47 - drift), height * 0.72),
        (depth * (0.37 + drift), height * 0.43),
        (depth * (0.63 - drift), margin + 7.0),
    ]
    trunk = spline_ribbon(trunk_controls, width, samples=48)
    branch_1 = spline_ribbon(
        [
            (depth * 0.43, height * 0.70),
            (depth * 0.66, height * 0.63),
            (depth * 0.82, height * 0.55),
        ],
        width * 0.78,
        samples=32,
    )
    branch_2 = spline_ribbon(
        [
            (depth * 0.40, height * 0.42),
            (depth * 0.24, height * 0.34),
            (depth * 0.16, height * 0.25),
        ],
        width * 0.72,
        samples=32,
    )
    network = unary_union([trunk, branch_1, branch_2]).intersection(safe)
    if keepout_centers:
        keepouts = unary_union([Point(y, z).buffer(keepout_radius) for y, z in keepout_centers])
        network = network.difference(keepouts)
    return network.buffer(0)


def crown_ribbons(width: float, height: float, ribbon_width: float = 8.0) -> Polygon:
    """Three sparse wave sweeps in local (width, height) coordinates."""
    ribbons = []
    families = [
        [(-0.46, 0.06), (-0.26, 0.60), (0.02, 0.28), (0.23, 0.72), (0.46, 0.16)],
        [(-0.42, 0.05), (-0.18, 0.92), (0.08, 0.54), (0.38, 0.82)],
        [(-0.35, 0.08), (-0.08, 0.48), (0.12, 0.94), (0.42, 0.42)],
    ]
    for family in families:
        controls = [(x * width, z * height) for x, z in family]
        ribbons.append(spline_ribbon(controls, ribbon_width, samples=44))
    base = rounded_rectangle(-width / 2.0, 0.0, width / 2.0, 8.0, 3.0)
    # Spline interpolation and ribbon buffering can overshoot the semantic
    # controls. Clip to the declared crown envelope so crown_height remains an
    # authoritative production parameter rather than an approximate input.
    envelope = box(-width / 2.0, 0.0, width / 2.0, height)
    return unary_union([base, *ribbons]).intersection(envelope).buffer(0)
