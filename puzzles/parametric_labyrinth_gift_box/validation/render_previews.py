#!/usr/bin/env python3
"""Render multi-angle previews from the actual exported STL meshes."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


ROOT = Path(__file__).resolve().parent.parent
PREVIEWS = ROOT / "previews"
VIEWS = {
    "iso": (24, -55),
    "front": (0, -90),
    "back": (0, 90),
    "left": (0, 180),
    "right": (0, 0),
    "top": (90, -90),
}


def _load(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"{path} did not load as one mesh")
    return mesh


def _translated(mesh: trimesh.Trimesh, x: float) -> trimesh.Trimesh:
    result = mesh.copy()
    result.apply_translation((x, 0, 0))
    return result


def _set_equal_limits(axis, meshes: list[trimesh.Trimesh]) -> None:
    bounds = np.vstack([mesh.bounds for mesh in meshes])
    minimum = bounds.min(axis=0)
    maximum = bounds.max(axis=0)
    center = (minimum + maximum) / 2.0
    radius = max(maximum - minimum) / 2.0 * 1.08
    axis.set_xlim(center[0] - radius, center[0] + radius)
    axis.set_ylim(center[1] - radius, center[1] + radius)
    axis.set_zlim(max(0.0, center[2] - radius), center[2] + radius)
    axis.set_box_aspect((1, 1, 1))


def _render(
    meshes: list[trimesh.Trimesh],
    colors: list[str],
    output: Path,
    view: tuple[float, float],
    alphas: list[float] | None = None,
) -> None:
    figure = plt.figure(figsize=(8, 8), dpi=150)
    axis = figure.add_subplot(111, projection="3d")
    alphas = alphas or [1.0] * len(meshes)
    for mesh, color, alpha in zip(meshes, colors, alphas):
        collection = Poly3DCollection(
            mesh.triangles,
            facecolor=color,
            edgecolor=(0.08, 0.10, 0.12, 0.12),
            linewidth=0.08,
            alpha=alpha,
        )
        axis.add_collection3d(collection)
    _set_equal_limits(axis, meshes)
    axis.view_init(elev=view[0], azim=view[1])
    axis.set_axis_off()
    figure.patch.set_facecolor("#f3f1eb")
    axis.set_facecolor("#f3f1eb")
    figure.tight_layout(pad=0)
    figure.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(figure)


def _front_cutaway(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    clipped_triangles: list[np.ndarray] = []
    for triangle in mesh.triangles:
        polygon = [vertex for vertex in triangle]
        output: list[np.ndarray] = []
        for index, current in enumerate(polygon):
            previous = polygon[index - 1]
            current_inside = current[1] >= 0.0
            previous_inside = previous[1] >= 0.0
            if current_inside != previous_inside:
                ratio = -previous[1] / (current[1] - previous[1])
                output.append(previous + ratio * (current - previous))
            if current_inside:
                output.append(current)
        if len(output) >= 3:
            for index in range(1, len(output) - 1):
                triangle = np.asarray([output[0], output[index], output[index + 1]])
                area_vector = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
                if np.linalg.norm(area_vector) > 1e-10:
                    clipped_triangles.append(triangle)

    vertices = np.asarray(clipped_triangles).reshape((-1, 3))
    faces = np.arange(len(vertices)).reshape((-1, 3))
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def render_variant(name: str) -> None:
    inner = _translated(_load(ROOT / "exports" / name / "inner.stl"), -34.0)
    outer = _translated(_load(ROOT / "exports" / name / "outer.stl"), 34.0)
    for view_name, view in VIEWS.items():
        _render(
            [inner, outer],
            ["#377eb8", "#e97938"],
            PREVIEWS / f"{name}_{view_name}.png",
            view,
        )

    if name == "outer_maze":
        cutaway = _translated(
            _front_cutaway(_load(ROOT / "exports" / name / "outer.stl")), 34.0
        )
        _render(
            [inner, cutaway],
            ["#377eb8", "#e97938"],
            PREVIEWS / f"{name}_cutaway.png",
            VIEWS["iso"],
        )


def main() -> None:
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    render_variant("inner_maze")
    render_variant("outer_maze")


if __name__ == "__main__":
    main()
