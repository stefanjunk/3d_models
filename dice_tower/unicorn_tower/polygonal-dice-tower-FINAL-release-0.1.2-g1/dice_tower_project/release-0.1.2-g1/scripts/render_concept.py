#!/usr/bin/env python3
"""Render the requirements-approved dice-tower concept sheet.

This script deliberately creates a visualization blockout only.  It does not
modify the source STL or export manufacturing geometry.
"""

from __future__ import annotations

import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Wedge
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "upload" / "polygonal(1).stl"
OUTPUT = ROOT / "concept" / "dice-tower-concept-r0.1.0.jpg"

SCALE = 110.445300740
SOURCE_MIN_Y = -1.000030279
AXIS_SOURCE_XZ = np.array([0.003, -0.258])

HEIGHT = 220.0
AXIS_X = AXIS_SOURCE_XZ[0] * SCALE
AXIS_Y = -AXIS_SOURCE_XZ[1] * SCALE
INNER_R = 61.849 / 2.0
OUTER_R_MIN = INNER_R + 3.540
FLOOR_Z = 3.2
CAVITY_Z0 = 18.0
CAVITY_Z1 = 183.0

COLORS = {
    "background": "#08111f",
    "panel": "#0f1b2d",
    "grid": "#27364d",
    "text": "#f4f7fb",
    "muted": "#9fb0c6",
    "stone": np.array([0.55, 0.62, 0.70]),
    "cavity": "#38d6d2",
    "baffle": "#ff9f43",
    "entry": "#f04ea1",
    "exit": "#ffca55",
    "floor": "#58d68d",
    "die": "#f9e65c",
}


def read_binary_stl(path: Path) -> np.ndarray:
    """Return binary-STL triangles as an (n, 3, 3) float64 array."""

    with path.open("rb") as handle:
        header = handle.read(80)
        if len(header) != 80:
            raise ValueError("STL header is incomplete")
        raw_count = handle.read(4)
        if len(raw_count) != 4:
            raise ValueError("STL triangle count is missing")
        count = struct.unpack("<I", raw_count)[0]
        records = np.fromfile(
            handle,
            dtype=np.dtype(
                [
                    ("normal", "<f4", (3,)),
                    ("vertices", "<f4", (3, 3)),
                    ("attribute", "<u2"),
                ]
            ),
            count=count,
        )
    if len(records) != count:
        raise ValueError(f"Expected {count} STL facets, read {len(records)}")
    return records["vertices"].astype(np.float64)


def source_to_working(triangles: np.ndarray) -> np.ndarray:
    """Map source +Y up/+Z front into working +Z up/-Y front, in millimetres."""

    out = np.empty_like(triangles)
    out[..., 0] = triangles[..., 0] * SCALE
    out[..., 1] = -triangles[..., 2] * SCALE
    out[..., 2] = (triangles[..., 1] - SOURCE_MIN_Y) * SCALE
    return out


def shade_faces(triangles: np.ndarray, alpha: float) -> np.ndarray:
    edges_a = triangles[:, 1] - triangles[:, 0]
    edges_b = triangles[:, 2] - triangles[:, 0]
    normals = np.cross(edges_a, edges_b)
    lengths = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(lengths[:, None], 1e-12)
    light = np.array([-0.45, -0.70, 0.55])
    light /= np.linalg.norm(light)
    intensity = 0.38 + 0.62 * np.clip(normals @ light, 0.0, 1.0)
    rgb = np.clip(COLORS["stone"][None, :] * intensity[:, None], 0.0, 1.0)
    return np.column_stack((rgb, np.full(len(rgb), alpha)))


def panel_title(ax, index: str, title: str, subtitle: str) -> None:
    ax.text2D(
        0.02,
        0.98,
        f"{index}  {title}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        color=COLORS["text"],
        fontsize=12,
        fontweight="bold",
    )
    ax.text2D(
        0.02,
        0.935,
        subtitle,
        transform=ax.transAxes,
        va="top",
        ha="left",
        color=COLORS["muted"],
        fontsize=8.5,
    )


def add_cylinder_wire(ax, radius: float, z0: float, z1: float) -> None:
    theta = np.linspace(0.0, 2.0 * np.pi, 96)
    for z in (z0, z1):
        ax.plot(
            AXIS_X + radius * np.cos(theta),
            AXIS_Y + radius * np.sin(theta),
            np.full_like(theta, z),
            color=COLORS["cavity"],
            linewidth=1.6,
            alpha=0.8,
        )
    for t in np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False):
        ax.plot(
            [AXIS_X + radius * np.cos(t)] * 2,
            [AXIS_Y + radius * np.sin(t)] * 2,
            [z0, z1],
            color=COLORS["cavity"],
            linewidth=0.65,
            alpha=0.32,
        )


def baffle_grid(angle_deg: float, z_level: float, resolution: int = 34):
    edge_u = INNER_R - 32.0
    u = np.linspace(-INNER_R, edge_u, resolution)
    v = np.linspace(-INNER_R, INNER_R, resolution)
    uu, vv = np.meshgrid(u, v)
    valid = uu * uu + vv * vv <= INNER_R * INNER_R
    slope = np.tan(np.deg2rad(6.0))
    zz = z_level - slope * (uu + INNER_R)
    theta = np.deg2rad(angle_deg)
    xx = AXIS_X + uu * np.cos(theta) - vv * np.sin(theta)
    yy = AXIS_Y + uu * np.sin(theta) + vv * np.cos(theta)
    xx = np.where(valid, xx, np.nan)
    yy = np.where(valid, yy, np.nan)
    zz = np.where(valid, zz, np.nan)
    return xx, yy, zz


def draw_overview(ax, triangles: np.ndarray) -> None:
    panel_title(
        ax,
        "01",
        "Ghosted overview",
        "Original exterior preserved; functional path shown inside",
    )

    shell = Poly3DCollection(
        triangles,
        facecolors=shade_faces(triangles, 0.17),
        edgecolors="none",
        linewidths=0.0,
        zsort="average",
    )
    ax.add_collection3d(shell)

    add_cylinder_wire(ax, INNER_R, CAVITY_Z0, CAVITY_Z1)

    baffle_levels = [165.0, 135.0, 105.0, 75.0, 45.0]
    baffle_angles = [20.0 + 100.0 * i for i in range(5)]
    for angle, level in zip(baffle_angles, baffle_levels):
        xx, yy, zz = baffle_grid(angle, level)
        ax.plot_surface(
            xx,
            yy,
            zz,
            color=COLORS["baffle"],
            alpha=0.96,
            linewidth=0,
            antialiased=True,
            shade=True,
        )

    path_z = np.linspace(180.0, 38.0, 240)
    revolutions = (180.0 - path_z) / 30.0 * np.deg2rad(100.0)
    path_x = AXIS_X + 12.0 * np.cos(revolutions + np.deg2rad(20.0))
    path_y = AXIS_Y + 12.0 * np.sin(revolutions + np.deg2rad(20.0))
    ax.plot(path_x, path_y, path_z, color=COLORS["die"], linewidth=2.3, alpha=0.95)

    # Rear roof insertion marker: concept ring on the rear roof plane.
    entry_y = AXIS_Y + 27.0
    entry_x = np.array([-17, 17, 17, -17, -17], dtype=float) + AXIS_X
    entry_z = np.array([174, 174, 208, 208, 174], dtype=float)
    ax.plot(
        entry_x,
        np.full_like(entry_x, entry_y),
        entry_z,
        color=COLORS["entry"],
        linewidth=3.2,
    )

    # Lower front portal marker: rounded arch on the front tower wall.
    front_y = AXIS_Y - OUTER_R_MIN
    left_x = AXIS_X - 18.0
    right_x = AXIS_X + 18.0
    base_z = 6.5
    shoulder_z = 22.0
    arch_t = np.linspace(np.pi, 0.0, 48)
    arch_x = AXIS_X + 18.0 * np.cos(arch_t)
    arch_z = shoulder_z + 16.0 * np.sin(arch_t)
    portal_x = np.concatenate(([left_x, left_x], arch_x, [right_x, right_x]))
    portal_z = np.concatenate(([base_z, shoulder_z], arch_z, [shoulder_z, base_z]))
    ax.plot(
        portal_x,
        np.full_like(portal_x, front_y),
        portal_z,
        color=COLORS["exit"],
        linewidth=3.2,
    )

    ax.scatter(
        [path_x[0], path_x[-1]],
        [path_y[0], path_y[-1]],
        [path_z[0], path_z[-1]],
        s=[38, 38],
        color=[COLORS["entry"], COLORS["exit"]],
        depthshade=False,
    )

    ax.set_xlim(-79, 80)
    ax.set_ylim(-78, 84)
    ax.set_zlim(0, 224)
    ax.set_box_aspect((159, 162, 224))
    ax.view_init(elev=22, azim=-128)
    ax.set_axis_off()

    ax.text2D(
        0.04,
        0.075,
        "magenta  Einwurf hinten oben\norange     5 Wendel-Baffles\ngelb       Würfelweg\ntürkis     Innenzylinder\nhellgelb   Auslauf zum Vorhof",
        transform=ax.transAxes,
        color=COLORS["muted"],
        fontsize=8.1,
        linespacing=1.45,
        family="DejaVu Sans Mono",
        bbox=dict(boxstyle="round,pad=0.55", facecolor="#0a1424", edgecolor=COLORS["grid"], alpha=0.92),
    )


def section_segments(triangles: np.ndarray, plane_x: float) -> np.ndarray:
    """Intersect triangles with X=plane_x and return line segments in Y/Z."""

    segments = []
    for tri in triangles:
        distances = tri[:, 0] - plane_x
        points = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            di, dj = distances[i], distances[j]
            pi, pj = tri[i], tri[j]
            if abs(di) < 1e-9 and abs(dj) < 1e-9:
                points.extend((pi[1:], pj[1:]))
            elif abs(di) < 1e-9:
                points.append(pi[1:])
            elif abs(dj) < 1e-9:
                points.append(pj[1:])
            elif di * dj < 0.0:
                t = di / (di - dj)
                point = pi + t * (pj - pi)
                points.append(point[1:])
        unique = []
        for point in points:
            if not any(np.linalg.norm(point - other) < 1e-6 for other in unique):
                unique.append(point)
        if len(unique) >= 2:
            segments.append([unique[0], unique[1]])
    return np.asarray(segments)


def draw_section(ax, triangles: np.ndarray) -> None:
    ax.set_facecolor(COLORS["panel"])
    ax.set_title(
        "02  Longitudinal cutaway",
        loc="left",
        color=COLORS["text"],
        fontsize=12,
        fontweight="bold",
        pad=14,
    )
    ax.text(
        0.0,
        1.005,
        "Front / forecourt at left · rear entry at right",
        transform=ax.transAxes,
        color=COLORS["muted"],
        fontsize=8.5,
        va="bottom",
    )

    segments = section_segments(triangles, AXIS_X)
    if len(segments):
        ax.add_collection(
            LineCollection(
                segments,
                colors="#91a0b3",
                linewidths=0.72,
                alpha=0.66,
                zorder=2,
            )
        )

    cavity = Rectangle(
        (AXIS_Y - INNER_R, CAVITY_Z0),
        2.0 * INNER_R,
        CAVITY_Z1 - CAVITY_Z0,
        facecolor="#38d6d21a",
        edgecolor=COLORS["cavity"],
        linewidth=1.5,
        linestyle=(0, (5, 3)),
        zorder=1,
    )
    ax.add_patch(cavity)

    baffle_levels = [165.0, 135.0, 105.0, 75.0, 45.0]
    baffle_angles = [20.0 + 100.0 * i for i in range(5)]
    edge_u = INNER_R - 32.0
    for angle_deg, level in zip(baffle_angles, baffle_levels):
        theta = np.deg2rad(angle_deg)
        ys = np.linspace(-INNER_R, INNER_R, 260)
        u = np.sin(theta) * ys
        valid = u <= edge_u
        if not np.any(valid):
            continue
        y_valid = AXIS_Y + ys[valid]
        z_valid = level - np.tan(np.deg2rad(6.0)) * (u[valid] + INNER_R)
        ax.plot(
            y_valid,
            z_valid,
            color=COLORS["baffle"],
            linewidth=5.2,
            solid_capstyle="round",
            zorder=5,
        )
        # A symbolic 45-degree printable underside at the wall attachment.
        attach_idx = 0 if abs(ys[valid][0]) > abs(ys[valid][-1]) else -1
        attach_y = y_valid[attach_idx]
        attach_z = z_valid[attach_idx]
        brace_direction = 1.0 if attach_y < AXIS_Y else -1.0
        ax.plot(
            [attach_y, attach_y + brace_direction * 7.0],
            [attach_z - 0.5, attach_z - 7.5],
            color=COLORS["baffle"],
            linewidth=2.1,
            alpha=0.95,
            zorder=4,
        )

    # Entry chute, shown as a broad magenta guide from the rear roof to cavity.
    entry_path = np.array(
        [
            [AXIS_Y + 34.0, 202.0],
            [AXIS_Y + 26.0, 191.0],
            [AXIS_Y + 13.0, 181.0],
            [AXIS_Y + 8.0, 174.0],
        ]
    )
    ax.plot(
        entry_path[:, 0],
        entry_path[:, 1],
        color=COLORS["entry"],
        linewidth=6.0,
        solid_capstyle="round",
        zorder=6,
    )
    ax.add_patch(
        FancyArrowPatch(
            entry_path[-2],
            entry_path[-1],
            arrowstyle="-|>",
            mutation_scale=14,
            color=COLORS["entry"],
            linewidth=1.5,
            zorder=7,
        )
    )

    # Closed floor and the lower discharge opening toward the forecourt.
    ax.plot(
        [AXIS_Y - INNER_R, AXIS_Y + INNER_R],
        [FLOOR_Z, FLOOR_Z],
        color=COLORS["floor"],
        linewidth=4.5,
        solid_capstyle="round",
        zorder=5,
    )
    exit_poly = np.array(
        [
            [AXIS_Y - 48.0, 7.0],
            [AXIS_Y - INNER_R + 1.0, 7.0],
            [AXIS_Y - INNER_R + 1.0, 38.0],
            [AXIS_Y - 36.0, 33.0],
            [AXIS_Y - 48.0, 23.0],
        ]
    )
    ax.add_patch(
        Polygon(
            exit_poly,
            closed=True,
            facecolor="#ffca5533",
            edgecolor=COLORS["exit"],
            linewidth=2.2,
            zorder=4,
        )
    )

    # Conceptual dice route through the alternating openings.
    route = np.array(
        [
            [AXIS_Y + 8.0, 174.0],
            [AXIS_Y - 12.0, 154.0],
            [AXIS_Y + 10.0, 124.0],
            [AXIS_Y - 11.0, 94.0],
            [AXIS_Y + 9.0, 64.0],
            [AXIS_Y - 9.0, 36.0],
            [AXIS_Y - 45.0, 21.0],
        ]
    )
    ax.plot(
        route[:, 0],
        route[:, 1],
        color=COLORS["die"],
        linewidth=1.9,
        linestyle=(0, (3.5, 2.5)),
        zorder=7,
    )
    ax.add_patch(
        FancyArrowPatch(
            route[-2],
            route[-1],
            arrowstyle="-|>",
            mutation_scale=14,
            color=COLORS["die"],
            linewidth=1.5,
            zorder=8,
        )
    )

    ax.annotate(
        "rear roof entry",
        xy=entry_path[0],
        xytext=(AXIS_Y + 43, 216),
        color=COLORS["entry"],
        fontsize=8.5,
        ha="right",
        arrowprops=dict(arrowstyle="-", color=COLORS["entry"], lw=1.0),
    )
    ax.annotate(
        "closed print-bed floor",
        xy=(AXIS_Y + 7, FLOOR_Z),
        xytext=(AXIS_Y + 43, 18),
        color=COLORS["floor"],
        fontsize=8.3,
        ha="right",
        arrowprops=dict(arrowstyle="-", color=COLORS["floor"], lw=1.0),
    )
    ax.annotate(
        "front discharge",
        xy=(AXIS_Y - 44, 24),
        xytext=(-74, 50),
        color=COLORS["exit"],
        fontsize=8.3,
        ha="left",
        arrowprops=dict(arrowstyle="-", color=COLORS["exit"], lw=1.0),
    )
    ax.text(
        AXIS_Y - 29,
        111,
        "5 levels\nrotated 100°",
        color=COLORS["baffle"],
        fontsize=8.4,
        ha="left",
        va="center",
        path_effects=[patheffects.withStroke(linewidth=3, foreground=COLORS["panel"])],
        zorder=9,
    )

    ax.set_xlim(-80, 85)
    ax.set_ylim(-2, 224)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(COLORS["grid"])
        spine.set_linewidth(1.0)
    ax.text(
        0.02,
        0.02,
        "CONCEPT CUT · not manufacturing geometry",
        transform=ax.transAxes,
        color=COLORS["muted"],
        fontsize=7.2,
        va="bottom",
    )


def circular_segment_polygon(radius: float, edge_u: float, angle_deg: float) -> np.ndarray:
    phi_a = np.arccos(np.clip(edge_u / radius, -1.0, 1.0))
    arc = np.linspace(phi_a, 2.0 * np.pi - phi_a, 160)
    local = np.column_stack((radius * np.cos(arc), radius * np.sin(arc)))
    theta = np.deg2rad(angle_deg)
    rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    return local @ rotation.T + np.array([AXIS_X, AXIS_Y])


def draw_plan(ax) -> None:
    ax.set_facecolor(COLORS["panel"])
    ax.set_title(
        "03  One baffle level",
        loc="left",
        color=COLORS["text"],
        fontsize=12,
        fontweight="bold",
        pad=14,
    )
    ax.text(
        0.0,
        1.005,
        "Plan view · the next level turns around the tower axis",
        transform=ax.transAxes,
        color=COLORS["muted"],
        fontsize=8.5,
        va="bottom",
    )

    # Protected minimum wall reserve and clear cylinder.
    ax.add_patch(
        Wedge(
            (AXIS_X, AXIS_Y),
            OUTER_R_MIN,
            0,
            360,
            width=OUTER_R_MIN - INNER_R,
            facecolor="#aeb8c666",
            edgecolor="#cbd3df",
            linewidth=1.0,
            zorder=2,
        )
    )
    ax.add_patch(
        Circle(
            (AXIS_X, AXIS_Y),
            INNER_R,
            facecolor="#38d6d212",
            edgecolor=COLORS["cavity"],
            linewidth=1.4,
            zorder=1,
        )
    )

    angle = 20.0
    edge_u = INNER_R - 32.0
    baffle_poly = circular_segment_polygon(INNER_R, edge_u, angle)
    ax.add_patch(
        Polygon(
            baffle_poly,
            closed=True,
            facecolor=COLORS["baffle"],
            edgecolor="#ffd0a0",
            linewidth=1.0,
            alpha=0.92,
            zorder=4,
        )
    )

    # Subsequent baffle edge orientations, as thin dashed intent lines.
    for subsequent in (120.0, 220.0, 320.0, 420.0):
        theta = np.deg2rad(subsequent)
        tangent = np.array([-np.sin(theta), np.cos(theta)])
        normal = np.array([np.cos(theta), np.sin(theta)])
        half_chord = np.sqrt(max(INNER_R * INNER_R - edge_u * edge_u, 0.0))
        center = np.array([AXIS_X, AXIS_Y]) + edge_u * normal
        endpoints = np.array([center - half_chord * tangent, center + half_chord * tangent])
        ax.plot(
            endpoints[:, 0],
            endpoints[:, 1],
            color=COLORS["baffle"],
            linewidth=1.0,
            linestyle=(0, (3, 3)),
            alpha=0.48,
            zorder=3,
        )

    theta = np.deg2rad(angle)
    normal = np.array([np.cos(theta), np.sin(theta)])
    tangent = np.array([-np.sin(theta), np.cos(theta)])

    # 25 mm clearance-body footprint positioned in the open side.
    die_center_u = 0.5 * (edge_u + INNER_R)
    die_center = np.array([AXIS_X, AXIS_Y]) + die_center_u * normal
    half = 12.5
    die_local = np.array([[-half, -half], [half, -half], [half, half], [-half, half]])
    basis = np.column_stack((normal, tangent))
    die_xy = die_local @ basis.T + die_center
    ax.add_patch(
        Polygon(
            die_xy,
            closed=True,
            facecolor="#f9e65c42",
            edgecolor=COLORS["die"],
            linewidth=1.5,
            zorder=5,
        )
    )

    gap_start = np.array([AXIS_X, AXIS_Y]) + edge_u * normal
    gap_end = np.array([AXIS_X, AXIS_Y]) + (INNER_R - 0.7) * normal
    ax.add_patch(
        FancyArrowPatch(
            gap_start,
            gap_end,
            arrowstyle="<->",
            mutation_scale=10,
            color=COLORS["die"],
            linewidth=1.3,
            zorder=6,
        )
    )
    gap_label = 0.5 * (gap_start + gap_end) + 5.3 * tangent
    ax.text(
        gap_label[0],
        gap_label[1],
        "free passage",
        color=COLORS["die"],
        fontsize=8.0,
        ha="center",
        va="center",
        rotation=angle,
        zorder=7,
        path_effects=[patheffects.withStroke(linewidth=3, foreground=COLORS["panel"])],
    )

    ax.annotate(
        "protected wall reserve",
        xy=(AXIS_X - OUTER_R_MIN * 0.72, AXIS_Y + OUTER_R_MIN * 0.72),
        xytext=(AXIS_X - 51, AXIS_Y + 49),
        color="#d3dae5",
        fontsize=8.2,
        ha="left",
        arrowprops=dict(arrowstyle="-", color="#d3dae5", lw=0.9),
    )
    ax.annotate(
        "largest die envelope",
        xy=die_center,
        xytext=(AXIS_X + 50, AXIS_Y - 49),
        color=COLORS["die"],
        fontsize=8.2,
        ha="right",
        arrowprops=dict(arrowstyle="-", color=COLORS["die"], lw=0.9),
    )

    rotation_arc = Wedge(
        (AXIS_X, AXIS_Y),
        INNER_R * 0.55,
        35,
        122,
        width=0.0,
        fill=False,
        edgecolor=COLORS["baffle"],
        linewidth=1.4,
        linestyle=(0, (3, 2)),
        zorder=6,
    )
    ax.add_patch(rotation_arc)
    ax.text(
        AXIS_X - 2,
        AXIS_Y + 19,
        "+100° next level",
        color=COLORS["baffle"],
        fontsize=8.0,
        ha="center",
        va="bottom",
        path_effects=[patheffects.withStroke(linewidth=3, foreground=COLORS["panel"])],
    )

    ax.scatter([AXIS_X], [AXIS_Y], s=18, color=COLORS["cavity"], zorder=8)
    ax.set_xlim(AXIS_X - 58, AXIS_X + 58)
    ax.set_ylim(AXIS_Y - 58, AXIS_Y + 58)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(COLORS["grid"])
        spine.set_linewidth(1.0)

    ax.text(
        0.04,
        0.035,
        "solid orange  active shelf\ndashed orange  next four orientations",
        transform=ax.transAxes,
        color=COLORS["muted"],
        fontsize=7.7,
        linespacing=1.45,
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#0a1424", edgecolor=COLORS["grid"], alpha=0.92),
    )


def main() -> None:
    source_triangles = read_binary_stl(SOURCE)
    triangles = source_to_working(source_triangles)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": COLORS["panel"],
            "figure.facecolor": COLORS["background"],
            "savefig.facecolor": COLORS["background"],
        }
    )
    fig = plt.figure(figsize=(16, 9), dpi=160, facecolor=COLORS["background"])
    grid = fig.add_gridspec(
        1,
        3,
        left=0.025,
        right=0.985,
        bottom=0.105,
        top=0.865,
        wspace=0.075,
        width_ratios=(1.27, 0.98, 0.88),
    )

    overview = fig.add_subplot(grid[0, 0], projection="3d", facecolor=COLORS["panel"])
    section = fig.add_subplot(grid[0, 1], facecolor=COLORS["panel"])
    plan = fig.add_subplot(grid[0, 2], facecolor=COLORS["panel"])

    draw_overview(overview, triangles)
    draw_section(section, triangles)
    draw_plan(plan)

    fig.text(
        0.03,
        0.945,
        "POLYGONAL DICE TOWER · FUNCTIONALIZATION CONCEPT",
        color=COLORS["text"],
        fontsize=18,
        fontweight="bold",
        ha="left",
        va="center",
    )
    fig.text(
        0.03,
        0.908,
        "Requirements-approved blockout · specification 0.1.0 · JuSt Innovation",
        color=COLORS["muted"],
        fontsize=9.3,
        ha="left",
        va="center",
    )
    fig.text(
        0.97,
        0.938,
        "CONCEPT ONLY",
        color=COLORS["entry"],
        fontsize=11,
        fontweight="bold",
        ha="right",
        va="center",
    )
    fig.text(
        0.97,
        0.908,
        "Not dimensional proof · not ready to print",
        color=COLORS["muted"],
        fontsize=8.4,
        ha="right",
        va="center",
    )

    fig.add_artist(
        plt.Line2D(
            [0.03, 0.97],
            [0.885, 0.885],
            transform=fig.transFigure,
            color=COLORS["grid"],
            linewidth=1.0,
        )
    )
    fig.add_artist(
        plt.Line2D(
            [0.03, 0.97],
            [0.082, 0.082],
            transform=fig.transFigure,
            color=COLORS["grid"],
            linewidth=1.0,
        )
    )
    fig.text(
        0.03,
        0.045,
        "Intent: rear roof insertion → five self-supporting rotated baffles → lower front arch → existing forecourt",
        color=COLORS["text"],
        fontsize=8.8,
        ha="left",
        va="center",
    )
    fig.text(
        0.97,
        0.045,
        "Source STL remains unchanged",
        color=COLORS["muted"],
        fontsize=8.5,
        ha="right",
        va="center",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        OUTPUT,
        dpi=160,
        format="jpeg",
        facecolor=COLORS["background"],
        edgecolor="none",
        pil_kwargs={"quality": 94, "optimize": True, "progressive": True},
    )
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
