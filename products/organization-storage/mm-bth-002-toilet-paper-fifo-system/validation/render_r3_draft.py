#!/usr/bin/env python3
"""Render a deterministic two-view preview from the DRAFT assembly 3MF."""

from __future__ import annotations

import argparse
import os
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "zen-kintsugi-r3-matplotlib-cache"),
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402


NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
PALETTE = {
    0: "#c2b7a2",
    1: "#a66f16",
    2: "#c8b99e",
}


def read_objects(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
    objects = []
    for node in root.findall(".//m:resources/m:object", NS):
        vertices = np.asarray(
            [
                [float(vertex.attrib[axis]) for axis in ("x", "y", "z")]
                for vertex in node.findall(".//m:vertices/m:vertex", NS)
            ],
            dtype=float,
        )
        faces = np.asarray(
            [
                [int(triangle.attrib[index]) for index in ("v1", "v2", "v3")]
                for triangle in node.findall(".//m:triangles/m:triangle", NS)
            ],
            dtype=np.int64,
        )
        objects.append(
            {
                "name": node.attrib.get("name", f"object-{node.attrib['id']}"),
                "material": int(node.attrib.get("pindex", "0")),
                "vertices": vertices,
                "faces": faces,
            }
        )
    if not objects:
        raise ValueError(f"No mesh objects found in {path}")
    return objects


def render_view(ax, objects: list[dict], elevation: float, azimuth: float, label: str) -> None:
    all_vertices = np.vstack([item["vertices"] for item in objects])
    lower = all_vertices.min(axis=0)
    upper = all_vertices.max(axis=0)
    center = (lower + upper) / 2.0
    extents = upper - lower
    horizontal_span = max(extents[0], extents[1]) * 1.35
    vertical_span = extents[2] * 1.08

    for item in objects:
        triangles = item["vertices"][item["faces"]]
        normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        normal_lengths = np.linalg.norm(normals, axis=1)
        normals = normals / np.maximum(normal_lengths[:, None], 1.0e-12)
        light = np.asarray((0.45, -0.55, 0.70), dtype=float)
        light /= np.linalg.norm(light)
        intensity = 0.62 + 0.38 * np.abs(normals @ light)
        base_rgb = np.asarray(matplotlib.colors.to_rgb(PALETTE.get(item["material"], PALETTE[0])))
        facecolors = np.column_stack((intensity[:, None] * base_rgb[None, :], np.ones(len(intensity))))
        collection = Poly3DCollection(
            triangles,
            facecolors=facecolors,
            edgecolors="none",
            linewidth=0.0,
            alpha=1.0,
            shade=False,
        )
        ax.add_collection3d(collection)

    ax.set_xlim(center[0] - horizontal_span / 2.0, center[0] + horizontal_span / 2.0)
    ax.set_ylim(center[1] - horizontal_span / 2.0, center[1] + horizontal_span / 2.0)
    ax.set_zlim(center[2] - vertical_span / 2.0, center[2] + vertical_span / 2.0)
    ax.set_box_aspect((horizontal_span, horizontal_span, vertical_span))
    ax.set_proj_type("ortho")
    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_axis_off()
    ax.set_title(label, fontsize=10, color="#4d463c", pad=4)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--assembly",
        type=Path,
        default=PROJECT_ROOT
        / "exports"
        / "draft"
        / "3mf"
        / "DRAFT_ZEN_KINTSUGI_WAVE_FIFO_R3_assembly.3mf",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "validation" / "DRAFT_r3_candidate-02_preview.png",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    objects = read_objects(args.assembly.resolve())
    figure = plt.figure(figsize=(10.0, 9.0), dpi=180, facecolor="#f5f0e7")
    front = figure.add_subplot(1, 2, 1, projection="3d", facecolor="#f5f0e7")
    rear = figure.add_subplot(1, 2, 2, projection="3d", facecolor="#f5f0e7")
    render_view(front, objects, 12.0, 45.0, "FRONT / DECORATIVE SIDE")
    render_view(rear, objects, 12.0, -135.0, "REAR / MOUNTING SIDE")
    figure.suptitle(
        "DRAFT · ZEN KINTSUGI WAVE FIFO · r3.0.0-candidate-02",
        fontsize=13,
        color="#322e28",
        y=0.96,
    )
    figure.text(
        0.5,
        0.045,
        "CAD-derived preview · not slicer or physical-test evidence",
        ha="center",
        fontsize=9,
        color="#6a6257",
    )
    figure.subplots_adjust(left=0.01, right=0.99, bottom=0.07, top=0.93, wspace=0.02)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, facecolor=figure.get_facecolor())
    plt.close(figure)
    print(args.output)


if __name__ == "__main__":
    main()
