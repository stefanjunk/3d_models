#!/usr/bin/env python3
"""Render the mandatory review views from the actual watermarked STL."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Rectangle
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARAMETERS = ROOT / "parameters" / "geometry-r0.1.2.json"

BG = "#08111f"
PANEL = "#0f1b2d"
TEXT = "#f4f7fb"
MUTED = "#9fb0c6"
GRID = "#31445e"
BODY = "#8290a3"
MARK = "#34d5cf"
ACCENT = "#ffca55"
MAGENTA = "#f04ea1"


def read_binary_stl(path: Path) -> np.ndarray:
    with path.open("rb") as handle:
        handle.read(80)
        count = struct.unpack("<I", handle.read(4))[0]
        records = np.fromfile(
            handle,
            dtype=np.dtype(
                [("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")]
            ),
            count=count,
        )
    if len(records) != count:
        raise ValueError("Incomplete STL")
    return records["vertices"].astype(np.float64)


def normals(triangles: np.ndarray) -> np.ndarray:
    values = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    return values / np.maximum(np.linalg.norm(values, axis=1)[:, None], 1e-12)


def underside_polygons(triangles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    face_normals = normals(triangles)
    centroids = triangles.mean(axis=1)
    keep = (face_normals[:, 2] < -0.35) & (centroids[:, 2] < 0.65)
    return triangles[keep], centroids[keep]


def project_bottom(triangles: np.ndarray) -> np.ndarray:
    projected = triangles[..., :2].copy()
    projected[..., 0] *= -1
    return projected


def section_segments(triangles: np.ndarray, plane_x: float) -> np.ndarray:
    segments = []
    for triangle in triangles:
        distances = triangle[:, 0] - plane_x
        points = []
        for first, second in ((0, 1), (1, 2), (2, 0)):
            a = triangle[first]
            b = triangle[second]
            da = distances[first]
            db = distances[second]
            if abs(da) < 1e-9:
                points.append(a[1:])
            if da * db < 0:
                fraction = da / (da - db)
                points.append((a + fraction * (b - a))[1:])
        unique = []
        for point in points:
            if not any(np.linalg.norm(point - existing) < 1e-7 for existing in unique):
                unique.append(point)
        if len(unique) >= 2:
            segments.append([unique[0], unique[1]])
    return np.asarray(segments)


def horizontal_segments(triangles: np.ndarray, height: float, bounds: tuple[float, float, float, float]) -> np.ndarray:
    segments = []
    x0, x1, y0, y1 = bounds
    for triangle in triangles:
        if triangle[:, 2].min() > height or triangle[:, 2].max() < height:
            continue
        points = []
        for first, second in ((0, 1), (1, 2), (2, 0)):
            a = triangle[first]
            b = triangle[second]
            da = a[2] - height
            db = b[2] - height
            if abs(da) < 1e-9:
                points.append(a[:2])
            if da * db < 0:
                fraction = da / (da - db)
                points.append((a + fraction * (b - a))[:2])
        unique = []
        for point in points:
            if not any(np.linalg.norm(point - existing) < 1e-7 for existing in unique):
                unique.append(point)
        if len(unique) >= 2:
            midpoint = (unique[0] + unique[1]) / 2
            if x0 <= midpoint[0] <= x1 and y0 <= midpoint[1] <= y1:
                segment = np.asarray([unique[0], unique[1]])
                segment[:, 0] *= -1
                segments.append(segment)
    return np.asarray(segments)


def panel_header(ax, title: str, subtitle: str) -> None:
    ax.set_facecolor(PANEL)
    ax.text(0.02, 0.98, title, transform=ax.transAxes, va="top", color=TEXT, fontsize=11, fontweight="bold", zorder=20)
    ax.text(0.02, 0.915, subtitle, transform=ax.transAxes, va="top", color=MUTED, fontsize=8, zorder=20)


def add_underside(ax, bottom: np.ndarray, centroids: np.ndarray, closeup: bool) -> None:
    projected = project_bottom(bottom)
    mark_floor = centroids[:, 2] > 0.20
    body_collection = PolyCollection(projected[~mark_floor], facecolors=BODY, edgecolors="none", alpha=0.92)
    mark_collection = PolyCollection(projected[mark_floor], facecolors=MARK, edgecolors="none", alpha=1.0)
    ax.add_collection(body_collection)
    ax.add_collection(mark_collection)
    ax.set_aspect("equal")
    ax.grid(False)
    if closeup:
        ax.set_xlim(-10, 10)
        ax.set_ylim(-61, -43)
    else:
        ax.set_xlim(-78, 78)
        ax.set_ylim(-76, 78)
    ax.set_xticks([])
    ax.set_yticks([])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=DEFAULT_PARAMETERS)
    parser.add_argument("--stl", type=Path)
    parser.add_argument("--validation", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parameters_path = args.parameters.resolve()
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))
    revision = parameters["revision"]
    stl_path = (args.stl or (
        ROOT / "result" / f"polygonal-dice-tower-DRAFT-watermarked-{revision}.stl"
    )).resolve()
    validation_path = (args.validation or (
        ROOT / "reports" / f"watermark-validation-{revision}.json"
    )).resolve()
    output_path = (args.output or (
        ROOT / "reports" / f"watermark-release-review-{revision}.jpg"
    )).resolve()
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    triangles = read_binary_stl(stl_path)
    bottom, bottom_centroids = underside_polygons(triangles)
    watermark = parameters["watermark"]
    center_screen_x = -watermark["centerX"]
    center_y = watermark["centerY"]
    width, height = watermark["actualEnvelope"]

    figure = plt.figure(figsize=(16, 10), facecolor=BG)
    grid = figure.add_gridspec(2, 2, left=0.035, right=0.975, bottom=0.075, top=0.875, wspace=0.06, hspace=0.08)

    ax_full = figure.add_subplot(grid[0, 0])
    panel_header(ax_full, "01  Finished underside · orthographic", "Direct outside view · front is down · reading direction verified")
    add_underside(ax_full, bottom, bottom_centroids, closeup=False)
    ax_full.add_patch(Rectangle((center_screen_x - 12, center_y - 10), 24, 20, fill=False, edgecolor=ACCENT, linewidth=1.2))
    ax_full.annotate("watermark ROI", xy=(center_screen_x, center_y), xytext=(25, -58), color=ACCENT, fontsize=8,
                     arrowprops={"arrowstyle": "->", "color": ACCENT, "lw": 1.1})

    ax_close = figure.add_subplot(grid[0, 1])
    panel_header(ax_close, "02  Dimensioned underside detail", "Actual JSI-WM-001-R1 compact cutter · selector scale 1.20")
    add_underside(ax_close, bottom, bottom_centroids, closeup=True)
    safe_w, safe_h = watermark["safeRectangle"]
    ax_close.add_patch(Rectangle((center_screen_x - safe_w / 2, center_y - safe_h / 2), safe_w, safe_h,
                                 fill=False, edgecolor=GRID, linestyle="--", linewidth=1.0))
    x_left = center_screen_x - width / 2
    x_right = center_screen_x + width / 2
    y_bottom = center_y - height / 2
    y_top = center_y + height / 2
    ax_close.annotate("", xy=(x_left, y_bottom - 1.2), xytext=(x_right, y_bottom - 1.2),
                      arrowprops={"arrowstyle": "<->", "color": ACCENT, "lw": 1.1})
    ax_close.text(center_screen_x, y_bottom - 1.8, f"{width:.3f} mm", color=ACCENT, fontsize=8, ha="center", va="top")
    ax_close.annotate("", xy=(x_right + 1.2, y_bottom), xytext=(x_right + 1.2, y_top),
                      arrowprops={"arrowstyle": "<->", "color": ACCENT, "lw": 1.1})
    ax_close.text(x_right + 1.65, center_y, f"{height:.1f} mm", color=ACCENT, fontsize=8, rotation=90, va="center")
    ax_close.text(0.02, 0.08, (
        f"product edge ≥ {watermark['minimumProductEdgeClearance']:.1f} mm\n"
        f"exit feature ≥ {watermark['minimumFeatureClearance']:.1f} mm\n"
        f"safe region {safe_w:.0f} × {safe_h:.0f} mm"
    ),
                  transform=ax_close.transAxes, color=MUTED, fontsize=8, linespacing=1.4)

    ax_section = figure.add_subplot(grid[1, 0])
    panel_header(ax_section, "03  Actual local section", "Plane through mark centre · cutter removes upward only; original bed datum is unchanged")
    section = section_segments(triangles, watermark["centerX"])
    local = section[
        (section[:, :, 0].mean(axis=1) >= -61)
        & (section[:, :, 0].mean(axis=1) <= -43)
        & (section[:, :, 1].max(axis=1) <= 1.2)
    ]
    ax_section.add_collection(LineCollection(local, colors=MARK, linewidths=1.4))
    ax_section.set_xlim(-61, -43)
    ax_section.set_ylim(-0.12, 1.05)
    ax_section.set_xlabel("working Y (mm)", color=MUTED, fontsize=8)
    ax_section.set_ylabel("Z above bed datum (mm)", color=MUTED, fontsize=8)
    ax_section.tick_params(colors=MUTED, labelsize=7)
    ax_section.grid(color=GRID, linewidth=0.45, alpha=0.6)
    ax_section.axhline(0, color=ACCENT, linewidth=0.8, linestyle="--")
    depth = validation["depth"]
    host_wall = validation["hostWall"]
    ax_section.annotate(
        f"{depth['actualMinimumMm']:.3f}–{depth['actualMaximumMm']:.3f} mm actual recess",
        xy=(-52, 0.45), xytext=(-59.5, 0.78), color=ACCENT, fontsize=8,
                        arrowprops={"arrowstyle": "->", "color": ACCENT, "lw": 1.0})
    ax_section.text(0.02, 0.08, (
        f"nominal depth {watermark['depth']:.2f} mm\n"
        f"minimum residual wall {host_wall['minimumAfterMm']:.3f} mm\n"
        "no geometry below original bed datum"
    ),
                    transform=ax_section.transAxes, color=MUTED, fontsize=8, linespacing=1.4)

    ax_layers = figure.add_subplot(grid[1, 1])
    panel_header(ax_layers, "04  First watermark-bearing layers", "Geometric 0.20 mm layer sections from the exported STL · verify final G-code in the chosen slicer")
    ax_layers.set_axis_off()
    bounds = (-9, 9, -61, -43)
    layer_specs = [(0.10, "Layer 1 centre"), (0.30, "Layer 2 centre"), (0.50, "Layer 3 centre")]
    for index, (height_z, label) in enumerate(layer_specs):
        inset = ax_layers.inset_axes([0.03 + index * 0.325, 0.15, 0.30, 0.62])
        inset.set_facecolor("#0b1627")
        segments = horizontal_segments(triangles, height_z, bounds)
        if len(segments):
            inset.add_collection(LineCollection(segments, colors=MARK, linewidths=1.0))
        inset.set_xlim(9, -9)
        inset.set_ylim(-61, -43)
        inset.set_aspect("equal")
        inset.set_xticks([])
        inset.set_yticks([])
        inset.set_title(f"{label}\nZ = {height_z:.2f} mm", color=TEXT, fontsize=8, pad=7)
        for spine in inset.spines.values():
            spine.set_color(GRID)
    process = validation["processFeatures"]
    ax_layers.text(0.03, 0.06, (
        f"{process['scaledMinimumStrokeMm']:.2f} mm scaled minimum stroke · "
        f"{process['scaledMinimumGapMm']:.2f} mm scaled minimum gap · "
        f"{process['nozzleMm']:.1f} mm nozzle / {process['layerHeightMm']:.1f} mm layers"
    ),
                   transform=ax_layers.transAxes, color=MUTED, fontsize=8)

    figure.text(0.035, 0.945, "JuSt INNOVATION WATERMARK · RELEASE GATE", color=TEXT, fontsize=18, fontweight="bold")
    figure.text(0.035, 0.912, f"Actual production candidate {revision} · asset JSI-WM-001-R1 · recessed compact profile", color=MUTED, fontsize=9)
    figure.text(0.975, 0.945, "FINAL APPROVAL REQUIRED", color=MAGENTA, fontsize=11, fontweight="bold", ha="right")
    figure.text(0.975, 0.912, "Candidate remains DRAFT until approval", color=MUTED, fontsize=8.5, ha="right")
    figure.text(0.035, 0.035, "Finished underside reading direction is verified directly, not inferred from a top-view CAD screenshot.", color=TEXT, fontsize=8.5)
    figure.text(0.975, 0.035, "Rendered from watermarked STL", color=MUTED, fontsize=8.5, ha="right")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160, facecolor=BG, pil_kwargs={"quality": 95, "optimize": True})
    plt.close(figure)
    print(output_path)


if __name__ == "__main__":
    main()
