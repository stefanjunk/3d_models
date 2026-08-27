"""Helical thread cutters (trapezoidal profile) for CadQuery, axis defaults to Z."""

from __future__ import annotations

import cadquery as cq


def thread_cutter(
    pitch: float,
    r_root: float,
    r_crest: float,
    length: float,
    z_offset: float = 0.0,
) -> cq.Solid:
    """Helical trapezoidal ridge sweeping from z_offset to z_offset+length around Z.

    r_root: inner radius of the ridge, r_crest: outer radius (ridge depth = r_crest-r_root).
    """
    if r_crest <= r_root:
        raise ValueError("r_crest must exceed r_root")
    if pitch <= 0 or length <= 0:
        raise ValueError("pitch and length must be positive")
    helix = cq.Wire.makeHelix(
        radius=(r_root + r_crest) / 2.0, height=length, pitch=pitch
    )
    if z_offset:
        helix = helix.translate((0, 0, z_offset))
    prof = (
        cq.Workplane("XZ")
        .moveTo(r_root, -0.30 * pitch)
        .lineTo(r_crest, -0.15 * pitch)
        .lineTo(r_crest, 0.15 * pitch)
        .lineTo(r_root, 0.30 * pitch)
        .close()
    )
    return prof.sweep(helix).val()


def cut_internal_thread(
    solid: cq.Workplane,
    bore_r: float,
    pitch: float,
    depth: float,
    length: float,
    axis: str = "Z",
    z_offset: float = 0.0,
    cy: float = 0.0,
    cz: float = 0.0,
) -> cq.Workplane:
    """Cut an internal thread into the wall around an existing cylindrical bore."""
    cutter = thread_cutter(pitch, bore_r - 0.1, bore_r + depth, length, z_offset)
    if axis == "X":
        cutter = _to_x_axis(cutter)
    if cy or cz:
        cutter = cutter.translate((0, cy, cz))
    return solid.cut(cutter)


def cut_external_thread(
    solid: cq.Workplane,
    outer_r: float,
    pitch: float,
    depth: float,
    length: float,
    axis: str = "Z",
    z_offset: float = 0.0,
    cy: float = 0.0,
    cz: float = 0.0,
) -> cq.Workplane:
    """Carve an external thread into a cylinder of radius outer_r."""
    cutter = thread_cutter(
        pitch, outer_r - depth, outer_r + 0.1, length, z_offset
    )
    if axis == "X":
        cutter = _to_x_axis(cutter)
    if cy or cz:
        cutter = cutter.translate((0, cy, cz))
    return solid.cut(cutter)


def _to_x_axis(solid: cq.Solid) -> cq.Solid:
    import math

    return solid.rotate((0, 0, 0), (0, 1, 0), 90.0)
