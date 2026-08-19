#!/usr/bin/env python3
"""Render watermark evidence from the actual primary-body binary STL files."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Rectangle


STL_DTYPE = np.dtype(
    [
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ]
)


def read_binary_stl(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open("rb") as handle:
        handle.seek(80)
        triangle_count = struct.unpack("<I", handle.read(4))[0]
    triangles = np.fromfile(path, dtype=STL_DTYPE, count=triangle_count, offset=84)
    return triangles["vertices"].astype(float), triangles["normal"].astype(float)


def underside_polygons(vertices: np.ndarray, normals: np.ndarray, maximum_z: float = 0.405):
    horizontal = (normals[:, 2] < -0.8) & (vertices[:, :, 2].max(axis=1) <= maximum_z + 1e-5)
    selected = vertices[horizontal]
    z_mean = selected[:, :, 2].mean(axis=1)
    order = np.argsort(z_mean)
    polygons = [np.column_stack((-selected[index, :, 0], selected[index, :, 1])) for index in order]
    colors = ["#dbe3e8" if z_mean[index] < 0.05 else "#1f6f8b" for index in order]
    return polygons, colors


def draw_underside(ax, vertices: np.ndarray, normals: np.ndarray):
    polygons, colors = underside_polygons(vertices, normals)
    ax.add_collection(PolyCollection(polygons, facecolors=colors, edgecolors="none"))
    flat = vertices.reshape(-1, 3)
    ax.set_xlim(-flat[:, 0].max() - 5, -flat[:, 0].min() + 5)
    ax.set_ylim(flat[:, 1].min() - 5, flat[:, 1].max() + 5)
    ax.set_aspect("equal")
    ax.axis("off")


def slice_segments(vertices: np.ndarray, z_plane: float):
    segments = []
    for triangle in vertices:
        points = []
        for first, second in ((0, 1), (1, 2), (2, 0)):
            a, b = triangle[first], triangle[second]
            da, db = a[2] - z_plane, b[2] - z_plane
            if abs(da) < 1e-8 and abs(db) < 1e-8:
                continue
            if da * db > 0 or abs(a[2] - b[2]) < 1e-12:
                continue
            t = (z_plane - a[2]) / (b[2] - a[2])
            if -1e-8 <= t <= 1 + 1e-8:
                point = a + t * (b - a)
                points.append([-point[0], point[1]])
        unique = []
        for point in points:
            if not any(np.linalg.norm(np.asarray(point) - np.asarray(other)) < 1e-5 for other in unique):
                unique.append(point)
        if len(unique) == 2:
            segments.append(unique)
    return segments


def add_dimension(ax, start, end, text, offset=(0, 0), color="#b23a48"):
    p0 = np.asarray(start, dtype=float) + np.asarray(offset, dtype=float)
    p1 = np.asarray(end, dtype=float) + np.asarray(offset, dtype=float)
    ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="<->", color=color, lw=1.4))
    midpoint = (p0 + p1) / 2
    ax.text(midpoint[0], midpoint[1], text, color=color, fontsize=9, ha="center", va="bottom")


def render(metadata_path: Path, output_dir: Path) -> list[Path]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    project_root = metadata_path.parents[3]
    wm = metadata["watermark"]
    primary = [part for part in metadata["parts"] if part["primary"]]
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = []

    loaded = []
    for part in primary:
        stl_path = project_root / part["stl"]
        loaded.append((part, *read_binary_stl(stl_path)))

    fig, axes = plt.subplots(1, len(loaded), figsize=(15, 5.3), constrained_layout=True)
    for ax, (part, vertices, normals) in zip(axes, loaded):
        draw_underside(ax, vertices, normals)
        ax.set_title(part["name"], fontsize=11, pad=8)
        ax.text(
            0.5,
            0.02,
            "Ansicht von außen auf die fertige Unterseite",
            transform=ax.transAxes,
            ha="center",
            fontsize=8,
            color="#455a64",
        )
    fig.suptitle("DRAFT R3 · Kennzeichnung auf allen drei Primärgehäusen", fontsize=15, fontweight="bold")
    overview_path = output_dir / "DRAFT_R3_watermark_underside.png"
    fig.savefig(overview_path, dpi=220, facecolor="white")
    plt.close(fig)
    rendered.append(overview_path)

    part, vertices, normals = loaded[-1]
    polygons, colors = underside_polygons(vertices, normals)
    fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
    ax.add_collection(PolyCollection(polygons, facecolors=colors, edgecolors="none"))
    design_min_x, design_min_y = part["designBoundsMm"][0][:2]
    x0 = wm["boundsMm"][0][0] - design_min_x
    y0 = wm["boundsMm"][0][1] - design_min_y
    x1 = wm["boundsMm"][1][0] - design_min_x
    y1 = wm["boundsMm"][1][1] - design_min_y
    screen_x0, screen_x1 = -x1, -x0
    center_screen_x = -(x0 + x1) / 2
    center_y = (y0 + y1) / 2
    safe_width, safe_height = wm["safeRectangle"]
    safe_x = center_screen_x - safe_width / 2
    safe_y = center_y - safe_height / 2
    ax.add_patch(Rectangle((safe_x, safe_y), safe_width, safe_height, fill=False, ec="#2a9d8f", lw=1.8, ls="--"))
    ax.add_patch(Rectangle((screen_x0, y0), screen_x1 - screen_x0, y1 - y0, fill=False, ec="#b23a48", lw=1.6))
    add_dimension(ax, (screen_x0, y1), (screen_x1, y1), f"{x1 - x0:.2f} mm", offset=(0, 2.3))
    add_dimension(ax, (screen_x1, y0), (screen_x1, y1), f"{y1 - y0:.2f} mm", offset=(2.3, 0))
    vertical_clearance = (safe_height - (y1 - y0)) / 2
    ax.text(
        safe_x,
        safe_y - 1.3,
        f"konservativ freie CAD-Fläche: {safe_width:.0f} × {safe_height:.0f} mm · kleinster Rand {vertical_clearance:.1f} mm",
        ha="left",
        va="top",
        fontsize=9,
        color="#2a9d8f",
    )
    ax.set_xlim(safe_x - 4, safe_x + safe_width + 4)
    ax.set_ylim(safe_y - 7, safe_y + safe_height + 7)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Bemaßte Nahansicht · tatsächliche STL-Unterseite Stufe 3", fontsize=14, fontweight="bold")
    closeup_path = output_dir / "DRAFT_R3_watermark_closeup.png"
    fig.savefig(closeup_path, dpi=240, facecolor="white")
    plt.close(fig)
    rendered.append(closeup_path)

    base = float(wm["hostWallBefore"])
    depth = float(wm["depth"])
    residual = float(wm["hostWallAfter"])
    fig, ax = plt.subplots(figsize=(10, 4.8), constrained_layout=True)
    ax.add_patch(Rectangle((-30, 0), 60, base, facecolor="#dbe3e8", edgecolor="#263238", lw=1.4))
    ax.add_patch(Rectangle((-8.57, 0), 17.14, depth, facecolor="white", edgecolor="#1f6f8b", lw=1.8))
    ax.axhline(0, color="#b23a48", lw=1.5)
    ax.text(31, -0.35, "unveränderter Bett-Datum Z=0", va="top", fontsize=10, color="#b23a48")
    ax.annotate("", xy=(12, depth), xytext=(12, 0), arrowprops=dict(arrowstyle="<->", color="#b23a48", lw=1.4))
    ax.text(13.2, depth + 0.12, "0,40 mm", color="#b23a48", fontsize=9, ha="left", va="bottom")
    ax.annotate("", xy=(21, base), xytext=(21, depth), arrowprops=dict(arrowstyle="<->", color="#b23a48", lw=1.4))
    ax.text(19.7, (base + depth) / 2, "5,60 mm\nRestwand", color="#b23a48", fontsize=9, ha="right", va="center")
    ax.annotate("", xy=(31, base), xytext=(31, 0), arrowprops=dict(arrowstyle="<->", color="#b23a48", lw=1.4))
    ax.text(32.2, base / 2, "6,00 mm\nBasis", color="#b23a48", fontsize=9, ha="left", va="center")
    ax.text(0, depth + 0.22, "Vertiefung", ha="center", va="bottom", fontsize=9, color="#1f6f8b")
    ax.set_xlim(-36, 42)
    ax.set_ylim(-0.8, 7.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Parametrischer Schnitt durch die Bett-Unterseite", fontsize=14, fontweight="bold")
    section_path = output_dir / "DRAFT_R3_watermark_section.png"
    fig.savefig(section_path, dpi=240, facecolor="white")
    plt.close(fig)
    rendered.append(section_path)

    x_margin, y_margin = 5, 4
    levels = [0.14, 0.28, 0.42]
    fig, axes = plt.subplots(1, len(levels), figsize=(13, 4.7), constrained_layout=True)
    for ax, z_plane in zip(axes, levels):
        ax.set_facecolor("#eef2f4")
        segments = slice_segments(vertices, z_plane)
        ax.add_collection(LineCollection(segments, colors="#1f6f8b", linewidths=1.0))
        ax.set_xlim(screen_x0 - x_margin, screen_x1 + x_margin)
        ax.set_ylim(y0 - y_margin, y1 + y_margin)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"Z = {z_plane:.2f} mm", fontsize=11)
    fig.suptitle(
        "Geometrische Schichtkonturen aus der tatsächlichen STL · kein Slicer-Toolpath",
        fontsize=14,
        fontweight="bold",
    )
    layer_path = output_dir / "DRAFT_R3_watermark_geometric_layers.png"
    fig.savefig(layer_path, dpi=240, facecolor="white")
    plt.close(fig)
    rendered.append(layer_path)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    rendered = render(args.metadata, args.output_dir)
    print(json.dumps({"rendered": len(rendered), "files": [str(path) for path in rendered]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
