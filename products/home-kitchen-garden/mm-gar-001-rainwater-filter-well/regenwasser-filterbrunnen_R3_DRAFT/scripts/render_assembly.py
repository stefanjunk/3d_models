#!/usr/bin/env python3
"""Render overview, cutaway and exploded PNGs from actual assembly STL components."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


STL_DTYPE = np.dtype(
    [
        ("normal", "<f4", (3,)),
        ("vertices", "<f4", (3, 3)),
        ("attribute", "<u2"),
    ]
)


def read_binary_stl(path: Path) -> np.ndarray:
    data = path.read_bytes()
    count = struct.unpack("<I", data[80:84])[0]
    expected = 84 + 50 * count
    if len(data) != expected:
        raise ValueError(f"Invalid binary STL size for {path}")
    return np.frombuffer(data, dtype=STL_DTYPE, count=count, offset=84)["vertices"].astype(float)


def configure_axes(ax, title: str) -> None:
    ax.set_title(title, fontsize=16, pad=18, color="#0f172a", weight="bold")
    ax.set_facecolor("#f8fafc")
    ax.grid(False)
    ax.set_axis_off()
    ax.set_proj_type("persp", focal_length=0.9)


def equalize_axes(ax, bounds: tuple[np.ndarray, np.ndarray], margin: float = 0.06) -> None:
    minimum, maximum = bounds
    center = (minimum + maximum) / 2
    span = float(np.max(maximum - minimum)) * (1 + 2 * margin)
    half = span / 2
    ax.set_xlim(center[0] - half, center[0] + half)
    ax.set_ylim(center[1] - half, center[1] + half)
    ax.set_zlim(max(0, center[2] - half), center[2] + half)
    ax.set_box_aspect((1, 1, 1))


def transformed_bounds(components: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    all_vertices = np.concatenate([item["triangles"].reshape(-1, 3) for item in components])
    return all_vertices.min(axis=0), all_vertices.max(axis=0)


def add_mesh(ax, triangles: np.ndarray, color: str, alpha: float = 1.0, edge: bool = False) -> None:
    collection = Poly3DCollection(
        triangles,
        facecolor=color,
        edgecolor="#334155" if edge else color,
        linewidth=0.08 if edge else 0.0,
        alpha=alpha,
        antialiased=True,
    )
    collection.set_rasterized(True)
    ax.add_collection3d(collection)


def is_body(name: str) -> bool:
    return "Gehaeuse" in name


def render_overview(components: list[dict], output: Path) -> None:
    fig = plt.figure(figsize=(8.2, 10.2), dpi=220, facecolor="#f8fafc")
    ax = fig.add_subplot(111, projection="3d")
    configure_axes(ax, "Regenwasser-Filterbrunnen · Revision 3")
    order = sorted(components, key=lambda item: not is_body(item["name"]))
    for item in order:
        add_mesh(ax, item["triangles"], item["color"], 1.0, edge=False)
    equalize_axes(ax, transformed_bounds(components), margin=0.04)
    ax.view_init(elev=18, azim=-58)
    fig.text(
        0.5,
        0.025,
        "DRAFT CAD rendering · 851 mm total height · open air-gap inlet",
        ha="center",
        fontsize=9,
        color="#475569",
    )
    fig.savefig(output, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def render_cutaway(components: list[dict], output: Path) -> None:
    fig = plt.figure(figsize=(8.5, 10.5), dpi=220, facecolor="#f8fafc")
    ax = fig.add_subplot(111, projection="3d")
    configure_axes(ax, "Schnittansicht · tatsächliche CAD-Geometrie")
    for item in components:
        triangles = item["triangles"]
        if is_body(item["name"]):
            # Camera looks along +Y; remove the front half of housing triangles.
            triangles = triangles[triangles.mean(axis=1)[:, 1] >= 0]
            add_mesh(ax, triangles, item["color"], 0.32, edge=True)
        else:
            add_mesh(ax, triangles, item["color"], 0.96, edge=True)
    equalize_axes(ax, transformed_bounds(components), margin=0.04)
    ax.view_init(elev=13, azim=-90)
    fig.text(
        0.5,
        0.025,
        "Front half of the three housings hidden; inserts and water-transfer parts remain complete.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    fig.savefig(output, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def exploded_shift(name: str) -> np.ndarray:
    if name == "Stufe 1 Gehaeuse":
        return np.array([0.0, 0.0, 165.0])
    if name == "Schlammtrichter":
        return np.array([245.0, 0.0, 165.0])
    if name in {"Einlaufbecher", "Tangential-Fallrohr"}:
        return np.array([-215.0, 0.0, 165.0])
    if name == "Stufe 2 Gehaeuse":
        return np.array([0.0, 0.0, 82.0])
    if name == "Lamellenkassette":
        return np.array([240.0, 0.0, 82.0])
    if name in {"Fallrohr", "Diffusor"}:
        return np.array([-210.0, 0.0, 82.0])
    if name.startswith("Medienkorb"):
        return np.array([245.0, 0.0, 0.0])
    if name == "Verteilerplatte":
        return np.array([-210.0, 0.0, 0.0])
    return np.zeros(3)


def render_exploded(components: list[dict], output: Path) -> None:
    exploded = []
    for item in components:
        shifted = dict(item)
        shifted["triangles"] = item["triangles"] + exploded_shift(item["name"])
        exploded.append(shifted)

    fig = plt.figure(figsize=(11.5, 9.2), dpi=220, facecolor="#f8fafc")
    ax = fig.add_subplot(111, projection="3d")
    configure_axes(ax, "Explosionsansicht · Wartungsbaugruppen")
    for item in exploded:
        add_mesh(ax, item["triangles"], item["color"], 0.98, edge=True)
        if not is_body(item["name"]) and item["name"] != "Kaskadenauslauf":
            center = item["triangles"].reshape(-1, 3).mean(axis=0)
            ax.text(
                center[0],
                center[1],
                center[2],
                item["name"],
                fontsize=6.2,
                color="#0f172a",
                ha="center",
                va="center",
                bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "#cbd5e1", "alpha": 0.86},
            )
    equalize_axes(ax, transformed_bounds(exploded), margin=0.02)
    ax.view_init(elev=14, azim=-67)
    fig.text(
        0.5,
        0.025,
        "Printed modules separate vertically; removable inserts are pulled sideways only for illustration.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    fig.savefig(output, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    project_root = args.metadata.parents[3]
    components = []
    for item in metadata["assembly"]["components"]:
        component = dict(item)
        component["triangles"] = read_binary_stl(project_root / item["path"])
        components.append(component)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    render_overview(components, args.output_dir / "DRAFT_R3_assembly_overview.png")
    render_cutaway(components, args.output_dir / "DRAFT_R3_assembly_cutaway.png")
    render_exploded(components, args.output_dir / "DRAFT_R3_assembly_exploded.png")
    print(json.dumps({"rendered": 3, "output": str(args.output_dir)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
