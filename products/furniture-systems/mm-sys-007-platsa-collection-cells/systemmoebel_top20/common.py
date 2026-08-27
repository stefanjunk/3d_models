"""Shared geometry and metadata helpers for the twenty concept models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cadquery as cq


@dataclass(frozen=True)
class ModelSpec:
    index: int
    slug: str
    title: str
    solid: cq.Workplane
    material: str
    print_orientation: str
    support_required: bool
    minimum_wall_mm: float
    interface_note: str
    protected_features: tuple[str, ...]

    @property
    def filename(self) -> str:
        return f"{self.index:02d}_{self.slug}"


def rounded_prism(
    width: float,
    depth: float,
    height: float,
    radius: float = 3.0,
    z0: float = 0.0,
) -> cq.Workplane:
    """Create a robust rounded rectangle prism without edge-selection fillets."""
    radius = min(radius, width / 2.0, depth / 2.0)
    if radius <= 0:
        return (
            cq.Workplane("XY")
            .box(width, depth, height, centered=(True, True, False))
            .translate((0, 0, z0))
        )

    parts: list[cq.Workplane] = []
    if width - 2 * radius > 1e-6:
        parts.append(cq.Workplane("XY").rect(width - 2 * radius, depth).extrude(height))
    if depth - 2 * radius > 1e-6:
        parts.append(cq.Workplane("XY").rect(width, depth - 2 * radius).extrude(height))
    x = width / 2.0 - radius
    y = depth / 2.0 - radius
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner = (
                cq.Workplane("XY")
                .center(sx * x, sy * y)
                .circle(radius)
                .extrude(height)
            )
            parts.append(corner)
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result.translate((0, 0, z0)).clean()


def open_tray(
    width: float,
    depth: float,
    height: float,
    wall: float = 2.4,
    floor: float = 2.4,
    radius: float = 5.0,
) -> cq.Workplane:
    """Open-top tray with a continuous floor and perimeter load path."""
    outer = rounded_prism(width, depth, height, radius)
    inner_radius = max(0.8, radius - wall)
    inner = rounded_prism(
        width - 2 * wall,
        depth - 2 * wall,
        height - floor + 1.0,
        inner_radius,
        z0=floor,
    )
    return outer.cut(inner).clean()


def plate(
    width: float,
    depth: float,
    height: float,
    center: tuple[float, float] = (0.0, 0.0),
    z0: float = 0.0,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(True, True, False))
        .translate((center[0], center[1], z0))
    )


def cylinder(
    diameter: float,
    height: float,
    center: tuple[float, float] = (0.0, 0.0),
    z0: float = 0.0,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .center(center[0], center[1])
        .circle(diameter / 2.0)
        .extrude(height)
        .translate((0, 0, z0))
    )


def ring(
    outer_diameter: float,
    inner_diameter: float,
    height: float,
    center: tuple[float, float] = (0.0, 0.0),
    z0: float = 0.0,
) -> cq.Workplane:
    return cylinder(outer_diameter, height, center, z0).cut(
        cylinder(inner_diameter, height + 1.0, center, z0)
    )


def horizontal_tube(
    outer_diameter: float,
    inner_diameter: float,
    length: float,
    axis: str = "X",
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> cq.Workplane:
    """Create a tube along X or Y, useful for open docking rings."""
    plane = "YZ" if axis == "X" else "XZ"
    tube = (
        cq.Workplane(plane)
        .circle(outer_diameter / 2.0)
        .circle(inner_diameter / 2.0)
        .extrude(length / 2.0, both=True)
    )
    return tube.translate(center)


def rectangular_c_clip(
    inner_width: float,
    inner_depth: float,
    height: float,
    wall: float,
    opening: float,
    z0: float = 0.0,
) -> cq.Workplane:
    """Rectangular C-clip around a furniture post, open on +Y."""
    outer = rounded_prism(inner_width + 2 * wall, inner_depth + 2 * wall, height, 2.5, z0)
    inner = rounded_prism(inner_width, inner_depth, height + 1.0, 1.2, z0)
    clip = outer.cut(inner)
    slot = (
        cq.Workplane("XY")
        .box(opening, inner_depth / 2.0 + 2 * wall + 2.0, height + 2.0, centered=(True, True, False))
        .translate((0, inner_depth / 4.0 + wall, z0 - 1.0))
    )
    return clip.cut(slot).clean()


def config_number(config: dict[str, Any], key: str) -> float:
    value = config[key]
    if not isinstance(value, (int, float)):
        raise TypeError(f"Expected numeric config value for {key}, got {value!r}")
    return float(value)
