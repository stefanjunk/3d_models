#!/usr/bin/env python3
"""Render a multi-view engineering review from the exported production STL."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BG = "#08111f"
PANEL = "#0f1b2d"
TEXT = "#f4f7fb"
MUTED = "#9fb0c6"
STONE = np.array([0.58, 0.64, 0.72])
ORANGE = "#ff9f43"
GREEN = "#58d68d"
MAGENTA = "#f04ea1"
YELLOW = "#ffca55"
CYAN = "#38d6d2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--parameters",
        type=Path,
        default=ROOT / "parameters" / "geometry-r0.1.2.json",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


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
        raise ValueError(f"Incomplete STL: {path}")
    return records["vertices"].astype(np.float64)


def read_optional(path: Path) -> np.ndarray | None:
    return read_binary_stl(path) if path.exists() else None


def shaded_colors(triangles: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    first = triangles[:, 1] - triangles[:, 0]
    second = triangles[:, 2] - triangles[:, 0]
    normals = np.cross(first, second)
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-12)
    light = np.array([-0.5, -0.65, 0.55])
    light /= np.linalg.norm(light)
    intensity = 0.35 + 0.65 * np.clip(normals @ light, 0, 1)
    rgb = np.clip(STONE[None, :] * intensity[:, None], 0, 1)
    return np.column_stack([rgb, np.full(len(rgb), alpha)])


def add_mesh(ax, triangles: np.ndarray | None, color=None, alpha=1.0, shaded=False) -> None:
    if triangles is None or len(triangles) == 0:
        return
    facecolors = shaded_colors(triangles, alpha) if shaded else color
    collection = Poly3DCollection(
        triangles,
        facecolors=facecolors,
        edgecolors="none",
        linewidths=0,
        alpha=None if shaded else alpha,
        zsort="average",
    )
    ax.add_collection3d(collection)


def setup_panel(
    ax,
    title: str,
    subtitle: str,
    elev: float,
    azim: float,
    limits: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
) -> None:
    ax.set_facecolor(PANEL)
    ax.text2D(
        0.02,
        0.98,
        title,
        transform=ax.transAxes,
        va="top",
        color=TEXT,
        fontsize=10.5,
        fontweight="bold",
    )
    ax.text2D(
        0.02,
        0.925,
        subtitle,
        transform=ax.transAxes,
        va="top",
        color=MUTED,
        fontsize=7.7,
    )
    (xmin, xmax), (ymin, ymax), (zmin, zmax) = limits
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_zlim(zmin, zmax)
    ax.set_box_aspect((xmax - xmin, ymax - ymin, zmax - zmin))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


def main() -> None:
    args = parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    revision = parameters["revision"]
    tower = parameters["tower"]
    entry = parameters["entry"]
    exit_parameters = parameters["exit"]
    baffles_parameters = parameters["baffles"]

    final = read_binary_stl(
        ROOT / "result" / f"polygonal-dice-tower-DRAFT-no-watermark-{revision}.stl"
    )
    baffles = read_binary_stl(
        ROOT / "inserts" / f"{baffles_parameters['count']}-baffle-insert-{revision}.stl"
    )
    floor = read_binary_stl(ROOT / "inserts" / f"sloped-floor-insert-{revision}.stl")
    entry_liner = read_optional(
        ROOT / "inserts" / f"rear-upper-entry-channel-liner-{revision}.stl"
    )
    exit_liner = read_optional(
        ROOT / "inserts" / f"front-exit-channel-liner-{revision}.stl"
    )
    cavity = read_optional(ROOT / "cutters" / f"interior-cylinder-cutter-{revision}.stl")

    output = args.output or ROOT / "reports" / f"production-geometry-review-{revision}.jpg"
    figure = plt.figure(figsize=(16, 10), facecolor=BG)
    grid = figure.add_gridspec(
        2,
        3,
        left=0.025,
        right=0.975,
        bottom=0.075,
        top=0.88,
        wspace=0.025,
        hspace=0.045,
    )

    full_limits = ((-78, 78), (-76, 84), (0, 223))

    ax_front = figure.add_subplot(grid[0, 0], projection="3d")
    add_mesh(ax_front, final, shaded=True)
    setup_panel(
        ax_front,
        "01  Vorderansicht",
        "Sauber gerundeter Ausgang mit kurzem Kanal",
        20,
        -118,
        full_limits,
    )

    ax_rear = figure.add_subplot(grid[0, 1], projection="3d")
    add_mesh(ax_rear, final, shaded=True)
    setup_panel(
        ax_rear,
        "02  Rückansicht",
        "Rückwand außerhalb des Einwurfs unverändert",
        25,
        72,
        full_limits,
    )

    ax_side = figure.add_subplot(grid[0, 2], projection="3d")
    add_mesh(ax_side, final, shaded=True)
    setup_panel(
        ax_side,
        "03  Dach von der Seite",
        "Horn vollständig erhalten · Einwurf 45° hinten-oben",
        13,
        -4,
        ((-55, 55), (0, 84), (120, 223)),
    )

    ax_entry = figure.add_subplot(grid[1, 0], projection="3d")
    add_mesh(ax_entry, final, shaded=True)
    setup_panel(
        ax_entry,
        "04  Einwurfkanal",
        f"Nur {entry.get('visibleProjectionMm', 0):.0f} mm sichtbar · Ø {entry['clearDiameter']:.0f} mm frei · 4 mm Wand",
        42,
        90,
        ((-50, 50), (12, 84), (128, 205)),
    )

    ax_exit = figure.add_subplot(grid[1, 1], projection="3d")
    add_mesh(ax_exit, final, shaded=True)
    setup_panel(
        ax_exit,
        "05  Auswurfkanal",
        f"Nur {exit_parameters.get('channelLengthOutsideTowerApprox', 0):.0f} mm sichtbar · {exit_parameters['clearWidth']:.0f} mm frei · 4 mm Wand",
        12,
        -92,
        ((-55, 55), (-62, 24), (0, 82)),
    )

    ax_cut = figure.add_subplot(grid[1, 2], projection="3d")
    centroids = final.mean(axis=1)
    half_shell = final[centroids[:, 0] <= tower["axisX"] - 0.35]
    add_mesh(ax_cut, half_shell, color="#8ea0b7", alpha=0.20)
    add_mesh(ax_cut, cavity, color=CYAN, alpha=0.06)
    add_mesh(ax_cut, baffles, color=ORANGE, alpha=0.98)
    add_mesh(ax_cut, floor, color=GREEN, alpha=0.95)
    add_mesh(ax_cut, entry_liner, color=MAGENTA, alpha=0.20)
    add_mesh(ax_cut, exit_liner, color=YELLOW, alpha=0.22)
    setup_panel(
        ax_cut,
        "06  Funktionsschnitt",
        f"Innenraum Ø {tower['cavityRadius'] * 2:.0f} mm · {baffles_parameters['count']} versetzte Fallstufen",
        7,
        -89,
        full_limits,
    )

    figure.text(
        0.03,
        0.945,
        "POLYGONALER WÜRFELTURM · KORREKTURPRÜFUNG",
        color=TEXT,
        fontsize=18,
        fontweight="bold",
    )
    figure.text(
        0.03,
        0.913,
        f"Geometrie {revision} · direkt aus der exportierten STL gerendert · JuSt Innovation",
        color=MUTED,
        fontsize=9,
    )
    figure.text(
        0.97,
        0.945,
        "DRAFT · OHNE WASSERZEICHEN",
        color=MAGENTA,
        fontsize=11,
        fontweight="bold",
        ha="right",
    )
    figure.text(
        0.97,
        0.913,
        "Noch keine finale Fertigungsfreigabe",
        color=MUTED,
        fontsize=8.5,
        ha="right",
    )
    figure.text(
        0.03,
        0.035,
        "Geschlossener Boden · 25-mm-Würfelpfad digital geprüft · physischer Falltest bleibt erforderlich.",
        color=TEXT,
        fontsize=8.5,
    )
    figure.text(
        0.97,
        0.035,
        "Orange: Fallstufen · Grün: geschlossener Rampenboden",
        color=MUTED,
        fontsize=8.5,
        ha="right",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output,
        dpi=160,
        facecolor=BG,
        pil_kwargs={"quality": 94, "optimize": True},
    )
    plt.close(figure)
    print(output)


if __name__ == "__main__":
    main()
