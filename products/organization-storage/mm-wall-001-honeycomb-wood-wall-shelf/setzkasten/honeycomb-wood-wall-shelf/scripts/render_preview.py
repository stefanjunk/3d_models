#!/usr/bin/env python3
"""Render a dimension-driven module and assembly preview."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon


PROJECT_DIR = Path(__file__).resolve().parents[1]


def hex_points(radius: float, center: np.ndarray) -> np.ndarray:
    angles = np.arange(6) * np.pi / 3.0
    return center + np.column_stack((radius * np.cos(angles), radius * np.sin(angles)))


def ear_points(
    center: np.ndarray,
    radius: float,
    neck_width: float,
    inner_top_y: float,
) -> np.ndarray:
    half_neck = neck_width / 2.0
    external = np.asarray([half_neck, inner_top_y - center[1]], dtype=np.float64)
    distance_squared = float(np.dot(external, external))
    base = (radius * radius / distance_squared) * external
    tangent_scale = radius * np.sqrt(distance_squared - radius * radius) / distance_squared
    right_tangent = base - tangent_scale * np.asarray([-external[1], external[0]])
    right_angle = np.arctan2(right_tangent[1], right_tangent[0])
    angles = np.linspace(np.pi - right_angle, 2.0 * np.pi + right_angle, 49)
    arc = center + radius * np.column_stack((np.cos(angles), np.sin(angles)))
    return np.vstack(
        (
            [center + [-half_neck, inner_top_y - center[1]]],
            arc,
            [center + [half_neck, inner_top_y - center[1]]],
        )
    )


def render() -> None:
    params = json.loads((PROJECT_DIR / "parameters.json").read_text(encoding="utf-8"))
    fig = plt.figure(figsize=(14, 7.5), dpi=180, facecolor="#f6f2ea")
    outer_radius = float(params["module"]["outer_radius"])
    wall = float(params["module"]["wall_thickness"])
    back_panel_enabled = bool(params["module"].get("back_panel_enabled", True))
    mounting = params["mounting"]
    inner_radius = outer_radius - wall / np.cos(np.pi / 6)
    ax_single = fig.add_subplot(1, 2, 1)
    back_center = np.array([-13.0, 12.0])
    front_center = np.array([12.0, -8.0])
    outer_back = hex_points(outer_radius, back_center)
    outer_front = hex_points(outer_radius, front_center)
    inner_back = hex_points(inner_radius, back_center)
    inner_front = hex_points(inner_radius, front_center)

    ax_single.add_patch(
        Polygon(outer_back, closed=True, facecolor="#6f3517", edgecolor="#3f2414", linewidth=1.2)
    )
    for index in range(6):
        nxt = (index + 1) % 6
        ax_single.add_patch(
            Polygon(
                [outer_back[index], outer_back[nxt], outer_front[nxt], outer_front[index]],
                closed=True,
                facecolor="#844319" if index % 2 else "#915020",
                edgecolor="#4b2a16",
                linewidth=0.8,
            )
        )
    ax_single.add_patch(
        Polygon(
            inner_back,
            closed=True,
            facecolor="#9c5725" if back_panel_enabled else "#f6f2ea",
            edgecolor="#4b2a16",
            linewidth=0.8,
        )
    )
    if not back_panel_enabled:
        inner_top_y = float(inner_back[1, 1])
        for raw_center in mounting["hole_centers"]:
            center = back_center + np.asarray(raw_center, dtype=np.float64)
            ax_single.add_patch(
                Polygon(
                    ear_points(
                        center,
                        float(mounting["ear_outer_radius"]),
                        float(mounting["ear_neck_width"]),
                        inner_top_y,
                    ),
                    closed=True,
                    facecolor="#9c5725",
                    edgecolor="#4b2a16",
                    linewidth=0.8,
                    zorder=4,
                )
            )
            ax_single.add_patch(
                plt.Circle(
                    center,
                    float(mounting["shank_clearance_diameter"]) / 2,
                    color="#2f241d",
                    zorder=5,
                )
            )
    else:
        for raw_center in mounting["hole_centers"]:
            center = back_center + np.asarray(raw_center, dtype=np.float64)
            ax_single.add_patch(
                plt.Circle(
                    center,
                    float(mounting["shank_clearance_diameter"]) / 2,
                    color="#2f241d",
                    zorder=5,
                )
            )
    for index in range(6):
        nxt = (index + 1) % 6
        ax_single.add_patch(
            Polygon(
                [inner_back[index], inner_back[nxt], inner_front[nxt], inner_front[index]],
                closed=True,
                facecolor="#b96c2e" if index % 2 else "#a95e27",
                edgecolor="#4b2a16",
                linewidth=0.7,
            )
        )
    for index in range(6):
        nxt = (index + 1) % 6
        ax_single.add_patch(
            Polygon(
                [outer_front[index], outer_front[nxt], inner_front[nxt], inner_front[index]],
                closed=True,
                facecolor="#c47734",
                edgecolor="#4b2a16",
                linewidth=1.0,
                zorder=6,
            )
        )
    ax_single.set_xlim(-105, 115)
    ax_single.set_ylim(-92, 95)
    ax_single.set_aspect("equal")
    ax_single.axis("off")
    back_label = "offene Rückseite" if not back_panel_enabled else "geschlossene Rückwand"
    ax_single.set_title(
        f"Formvorschau des Einzelmoduls ({back_label})\n168 × 145,5 × 72 mm",
        fontsize=14,
        pad=12,
    )

    ax = fig.add_subplot(1, 2, 2)
    center_distance = 2 * outer_radius * np.cos(np.pi / 6)
    centers = [
        np.array([0.0, 0.0]),
        center_distance * np.array([np.cos(np.pi / 6), np.sin(np.pi / 6)]),
        center_distance * np.array([0.0, 1.0]),
    ]
    outer_patches = [Polygon(hex_points(outer_radius, c), closed=True) for c in centers]
    inner_patches = [Polygon(hex_points(inner_radius, c), closed=True) for c in centers]
    ax.add_collection(
        PatchCollection(outer_patches, facecolor="#a96028", edgecolor="#4b2a16", linewidth=1.5)
    )
    ax.add_collection(
        PatchCollection(inner_patches, facecolor="#f6f2ea", edgecolor="#4b2a16", linewidth=1.1)
    )
    for center_point in centers:
        for raw_center in mounting["hole_centers"]:
            ear_center = center_point + np.asarray(raw_center, dtype=np.float64)
            ax.add_patch(
                Polygon(
                    ear_points(
                        ear_center,
                        float(mounting["ear_outer_radius"]),
                        float(mounting["ear_neck_width"]),
                        center_point[1] + inner_radius * np.sin(np.pi / 3),
                    ),
                    closed=True,
                    facecolor="#a96028",
                    edgecolor="#4b2a16",
                    linewidth=0.7,
                    zorder=5,
                )
            )
            ax.scatter([ear_center[0]], [ear_center[1]], s=16, c="#2f241d", zorder=6)
    ax.text(
        np.mean([c[0] for c in centers]),
        min(c[1] for c in centers) - 92,
        "Je gemeinsame Kante: 2 U-Brücken von hinten; vor Wandmontage einsetzen",
        ha="center",
        va="top",
        fontsize=11,
        color="#4b2a16",
    )
    all_points = np.vstack([hex_points(outer_radius, c) for c in centers])
    margin = 24
    ax.set_xlim(all_points[:, 0].min() - margin, all_points[:, 0].max() + margin)
    ax.set_ylim(all_points[:, 1].min() - 115, all_points[:, 1].max() + margin)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Beispielanordnung aus 3 Modulen", fontsize=14, pad=12)
    fig.suptitle("Modulares Honeycomb-Wandregal mit Holzgravur", fontsize=18, y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    output = PROJECT_DIR / "generated" / "honeycomb-wall-shelf-preview.png"
    fig.savefig(output, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    render()
