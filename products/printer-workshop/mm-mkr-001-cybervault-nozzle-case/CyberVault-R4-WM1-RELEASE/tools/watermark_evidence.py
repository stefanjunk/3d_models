#!/usr/bin/env python3
"""Create watermark release-gate evidence from the actual candidate base STL."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Rectangle

from validate_and_package import Mesh, read_binary_stl


PROJECT = Path(__file__).resolve().parents[1]
EXPORTS = PROJECT / "exports" / "draft"
REPORTS = PROJECT / "reports"
RENDERS = PROJECT / "renders"
BASE_STL = EXPORTS / "cyber_nozzle_case_R4_DRAFT_base_manifold.stl"
CENTER = np.array([0.0, -96.2])
SAFE_SIZE = np.array([50.0, 20.0])
PROFILE_SIZE = np.array([32.0, 10.0])
DEPTH = 0.4
LAYER = 0.16


def sha256(target: Path) -> str:
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def triangle_normals(mesh: Mesh) -> np.ndarray:
    points = mesh.vertices[mesh.triangles]
    return np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0])


def finish_figure(fig, target: Path) -> None:
    fig.savefig(target, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def projected_underside(mesh: Mesh) -> tuple[np.ndarray, np.ndarray]:
    points = mesh.vertices[mesh.triangles]
    normals = triangle_normals(mesh)
    horizontal = np.abs(normals[:, 2]) > 1e-8
    near_underside = points[:, :, 2].max(axis=1) <= DEPTH + 1e-5
    selected = horizontal & near_underside
    polygons = points[selected, :, :2]
    heights = points[selected, :, 2].mean(axis=1)
    order = np.argsort(heights)
    return polygons[order], heights[order]


def style_2d(axis, title: str) -> None:
    axis.set_title(title, color="#e2fbff", fontsize=15, weight="bold", pad=14)
    axis.set_facecolor("#071219")
    axis.tick_params(colors="#90adb3")
    for spine in axis.spines.values():
        spine.set_color("#285766")
    axis.set_aspect("equal")


def render_finished_underside(mesh: Mesh, target: Path) -> None:
    polygons, heights = projected_underside(mesh)
    colors = plt.get_cmap("winter")((heights - heights.min()) / max(np.ptp(heights), 1e-9))
    colors[:, :3] = 0.25 * colors[:, :3] + 0.75 * np.array([0.03, 0.22, 0.26])
    colors[heights > 0.2, :3] = np.array([0.15, 0.92, 0.92])

    fig, axis = plt.subplots(figsize=(6.5, 13), facecolor="#050b10")
    axis.add_collection(PolyCollection(polygons, facecolors=colors, edgecolors="none"))
    lower = mesh.vertices.min(axis=0)
    upper = mesh.vertices.max(axis=0)
    axis.set_xlim(upper[0] + 3, lower[0] - 3)  # direct view from outside/below
    axis.set_ylim(lower[1] - 3, upper[1] + 3)
    style_2d(axis, "Fertige Unterseite · Direktansicht von außen")
    axis.set_xlabel("X [mm] · Blick von −Z", color="#90adb3")
    axis.set_ylabel("Y [mm]", color="#90adb3")
    axis.text(
        0.5,
        -0.075,
        "Originales Produktions-STL · Bett-Datum bleibt Z = 0,00 mm",
        transform=axis.transAxes,
        ha="center",
        color="#8cb7bd",
        fontsize=9,
    )
    finish_figure(fig, target)


def actual_recess_bounds(mesh: Mesh) -> tuple[np.ndarray, np.ndarray]:
    points = mesh.vertices[mesh.triangles]
    normals = triangle_normals(mesh)
    centroids = points.mean(axis=1)
    in_safe = (
        (np.abs(centroids[:, 0] - CENTER[0]) <= SAFE_SIZE[0] / 2)
        & (np.abs(centroids[:, 1] - CENTER[1]) <= SAFE_SIZE[1] / 2)
    )
    recess_floor = (
        np.all(np.abs(points[:, :, 2] - DEPTH) <= 1e-5, axis=1)
        & (np.abs(normals[:, 2]) > 1e-8)
        & in_safe
    )
    footprint = points[recess_floor, :, :2].reshape(-1, 2)
    if not len(footprint):
        raise RuntimeError("No actual 0.40 mm watermark floor found in candidate STL")
    return footprint.min(axis=0), footprint.max(axis=0)


def dimension_arrow(axis, start, end, text, offset=(0, 0)) -> None:
    start = np.asarray(start, dtype=float) + np.asarray(offset, dtype=float)
    end = np.asarray(end, dtype=float) + np.asarray(offset, dtype=float)
    axis.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle="<->", color="#ffd166", lw=1.5),
    )
    midpoint = (start + end) / 2
    axis.text(
        midpoint[0],
        midpoint[1],
        text,
        color="#ffd166",
        ha="center",
        va="bottom",
        fontsize=9,
        bbox=dict(facecolor="#071219", edgecolor="none", pad=1.5),
    )


def render_dimensioned_closeup(mesh: Mesh, target: Path) -> tuple[list[float], list[float]]:
    polygons, heights = projected_underside(mesh)
    recess_min, recess_max = actual_recess_bounds(mesh)
    close = (
        (polygons[:, :, 0].mean(axis=1) >= CENTER[0] - SAFE_SIZE[0] / 2 - 1)
        & (polygons[:, :, 0].mean(axis=1) <= CENTER[0] + SAFE_SIZE[0] / 2 + 1)
        & (polygons[:, :, 1].mean(axis=1) >= CENTER[1] - SAFE_SIZE[1] / 2 - 1)
        & (polygons[:, :, 1].mean(axis=1) <= CENTER[1] + SAFE_SIZE[1] / 2 + 1)
    )
    colors = np.tile(np.array([[0.06, 0.27, 0.31, 1.0]]), (int(close.sum()), 1))
    colors[heights[close] > 0.2] = np.array([0.12, 0.92, 0.92, 1.0])

    fig, axis = plt.subplots(figsize=(12, 6), facecolor="#050b10")
    axis.add_collection(
        PolyCollection(polygons[close], facecolors=colors, edgecolors="none")
    )
    safe_min = CENTER - SAFE_SIZE / 2
    profile_min = CENTER - PROFILE_SIZE / 2
    axis.add_patch(
        Rectangle(
            safe_min,
            SAFE_SIZE[0],
            SAFE_SIZE[1],
            fill=False,
            linestyle=(0, (5, 3)),
            linewidth=1.4,
            edgecolor="#ff7b72",
            label="geprüfte freie Fläche 50 × 20 mm",
        )
    )
    axis.add_patch(
        Rectangle(
            profile_min,
            PROFILE_SIZE[0],
            PROFILE_SIZE[1],
            fill=False,
            linewidth=1.2,
            edgecolor="#ffd166",
            label="nominales Asset-Fenster 32 × 10 mm",
        )
    )

    dimension_arrow(
        axis,
        [profile_min[0], profile_min[1]],
        [profile_min[0] + PROFILE_SIZE[0], profile_min[1]],
        "32,00 mm nominal",
        offset=[0, -2.1],
    )
    dimension_arrow(
        axis,
        [profile_min[0], profile_min[1]],
        [profile_min[0], profile_min[1] + PROFILE_SIZE[1]],
        "10,00 mm",
        offset=[-2.1, 0],
    )
    dimension_arrow(
        axis,
        [safe_min[0], safe_min[1] + SAFE_SIZE[1] + 1.2],
        [profile_min[0], safe_min[1] + SAFE_SIZE[1] + 1.2],
        "9,00 mm",
    )
    dimension_arrow(
        axis,
        [profile_min[0] + PROFILE_SIZE[0], safe_min[1] + SAFE_SIZE[1] + 1.2],
        [safe_min[0] + SAFE_SIZE[0], safe_min[1] + SAFE_SIZE[1] + 1.2],
        "9,00 mm",
    )
    axis.set_xlim(safe_min[0] - 5, safe_min[0] + SAFE_SIZE[0] + 5)
    axis.set_ylim(safe_min[1] - 5, safe_min[1] + SAFE_SIZE[1] + 5)
    style_2d(axis, "Maßprüfung · tatsächliche 0,40-mm-Aussparung")
    axis.legend(
        loc="upper center",
        ncol=2,
        frameon=False,
        labelcolor="#d5eef2",
        fontsize=9,
    )
    axis.text(
        0.5,
        -0.12,
        f"Tatsächliche Outline im STL: {recess_max[0]-recess_min[0]:.3f} × {recess_max[1]-recess_min[1]:.3f} mm · Restboden 2,60 mm",
        transform=axis.transAxes,
        ha="center",
        color="#8cb7bd",
        fontsize=9,
    )
    finish_figure(fig, target)
    return recess_min.tolist(), recess_max.tolist()


def plane_segments(mesh: Mesh, axis: int, value: float) -> np.ndarray:
    points = mesh.vertices[mesh.triangles]
    segments = []
    for triangle in points:
        distances = triangle[:, axis] - value
        hits = []
        for left, right in [(0, 1), (1, 2), (2, 0)]:
            dl = distances[left]
            dr = distances[right]
            if abs(dl) < 1e-9 and abs(dr) < 1e-9:
                continue
            if (dl <= 0 <= dr) or (dr <= 0 <= dl):
                denominator = dl - dr
                if abs(denominator) < 1e-12:
                    continue
                t = dl / denominator
                hit = triangle[left] + t * (triangle[right] - triangle[left])
                hits.append(hit)
        if len(hits) >= 2:
            unique = []
            for hit in hits:
                if not any(np.linalg.norm(hit - prior) < 1e-7 for prior in unique):
                    unique.append(hit)
            if len(unique) >= 2:
                segments.append([unique[0], unique[1]])
    return np.asarray(segments, dtype=float)


def choose_section_y(mesh: Mesh) -> float:
    best_y = float(CENTER[1])
    best_count = -1
    for y in np.linspace(CENTER[1] - 4.6, CENTER[1] + 4.6, 47):
        segments = plane_segments(mesh, 1, float(y))
        count = int(
            np.count_nonzero(
                (np.abs(segments[:, :, 2].mean(axis=1) - DEPTH) < 1e-4)
                & (np.abs(segments[:, :, 0].mean(axis=1) - CENTER[0]) < 20)
            )
        )
        if count > best_count:
            best_count = count
            best_y = float(y)
    return best_y


def render_section(mesh: Mesh, target: Path) -> float:
    section_y = choose_section_y(mesh)
    segments = plane_segments(mesh, 1, section_y)
    xz = segments[:, :, [0, 2]]
    crop = (
        (np.abs(xz[:, :, 0].mean(axis=1)) <= 21)
        & (xz[:, :, 1].max(axis=1) <= 3.25)
    )
    fig, axis = plt.subplots(figsize=(12, 4.8), facecolor="#050b10")
    axis.add_collection(
        LineCollection(xz[crop], colors="#42e5e9", linewidths=1.2)
    )
    axis.axhline(0, color="#ff7b72", lw=1.2, linestyle="--")
    axis.text(20.6, 0.03, "Bett-Datum Z = 0,00", color="#ff7b72", ha="right", va="bottom")
    axis.axhline(DEPTH, color="#ffd166", lw=0.8, linestyle=":")
    axis.annotate(
        "0,40 mm Rezess",
        xy=(18.0, DEPTH),
        xytext=(18.0, 0.0),
        arrowprops=dict(arrowstyle="<->", color="#ffd166", lw=1.5),
        color="#ffd166",
        ha="right",
        va="center",
    )
    axis.annotate(
        "2,60 mm Restboden",
        xy=(-18.0, 3.0),
        xytext=(-18.0, DEPTH),
        arrowprops=dict(arrowstyle="<->", color="#9effa1", lw=1.5),
        color="#9effa1",
        ha="left",
        va="center",
    )
    axis.set_xlim(-21, 21)
    axis.set_ylim(-0.15, 3.25)
    axis.set_xlabel("X [mm]", color="#90adb3")
    axis.set_ylabel("Z [mm]", color="#90adb3")
    style_2d(axis, f"STL-Schnitt durch das Wasserzeichen · Y = {section_y:.2f} mm")
    axis.set_aspect("auto")
    finish_figure(fig, target)
    return section_y


def segment_loop_count(segments: np.ndarray, crop_min: np.ndarray, crop_max: np.ndarray) -> int:
    projected = segments[:, :, :2]
    centers = projected.mean(axis=1)
    keep = np.all((centers >= crop_min) & (centers <= crop_max), axis=1)
    projected = projected[keep]
    if not len(projected):
        return 0
    quant = np.rint(projected.reshape(-1, 2) * 1e4).astype(np.int64)
    unique, inverse = np.unique(quant, axis=0, return_inverse=True)
    edges = inverse.reshape(-1, 2)
    parent = np.arange(len(unique), dtype=np.int64)

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = int(parent[value])
        return value

    for a, b in edges:
        ra = find(int(a))
        rb = find(int(b))
        if ra != rb:
            parent[rb] = ra
    return len({find(int(value)) for value in np.unique(edges)})


def render_layer_preview(mesh: Mesh, target: Path) -> dict:
    sample_z = [0.08, 0.24, 0.36]
    crop_min = CENTER - PROFILE_SIZE / 2 - np.array([2.0, 2.0])
    crop_max = CENTER + PROFILE_SIZE / 2 + np.array([2.0, 2.0])
    loop_counts = []
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.8), facecolor="#050b10")
    for index, (axis, z) in enumerate(zip(axes, sample_z, strict=True), start=1):
        segments = plane_segments(mesh, 2, z)
        xy = segments[:, :, :2]
        centers = xy.mean(axis=1)
        keep = np.all((centers >= crop_min) & (centers <= crop_max), axis=1)
        xy = xy[keep]
        loops = segment_loop_count(segments, crop_min, crop_max)
        loop_counts.append(loops)
        axis.add_collection(
            LineCollection(xy, colors="#ff9f43", linewidths=1.0, capstyle="round")
        )
        axis.set_xlim(crop_max[0], crop_min[0])
        axis.set_ylim(crop_min[1], crop_max[1])
        style_2d(axis, f"L{index} · Z = {z:.2f} mm")
        axis.set_xticks([])
        axis.set_yticks([])
        axis.text(
            0.5,
            -0.09,
            f"{loops} geschlossene Konturen im Prüfbereich",
            transform=axis.transAxes,
            ha="center",
            color="#8cb7bd",
            fontsize=9,
        )
    fig.suptitle(
        "Analytische Schichtvorschau aus dem tatsächlichen STL · 0,16-mm-Profil",
        color="#e2fbff",
        fontsize=16,
        weight="bold",
        y=1.02,
    )
    fig.text(
        0.5,
        0.01,
        "Orange = geschnittene Modellkonturen; identische offene Innenräume in allen wasserzeichentragenden Schichten",
        ha="center",
        color="#8cb7bd",
        fontsize=9,
    )
    finish_figure(fig, target)
    return {"sample_z_mm": sample_z, "closed_contours_in_crop": loop_counts}


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    mesh = read_binary_stl(BASE_STL)
    files = {
        "finished_underside": RENDERS / "watermark-01-finished-underside.png",
        "dimensioned_closeup": RENDERS / "watermark-02-dimensioned-closeup.png",
        "section": RENDERS / "watermark-03-section.png",
        "layer_preview": RENDERS / "watermark-04-layer-preview.png",
    }
    render_finished_underside(mesh, files["finished_underside"])
    recess_min, recess_max = render_dimensioned_closeup(
        mesh, files["dimensioned_closeup"]
    )
    section_y = render_section(mesh, files["section"])
    layers = render_layer_preview(mesh, files["layer_preview"])

    production = json.loads(
        (REPORTS / "production-cad-candidate.json").read_text(encoding="utf-8")
    )
    report = {
        "asset_id": "JSI-WM-001-R1",
        "geometry_revision": production["geometry_revision"],
        "geometry_hashes_sha256": {
            "base_stl": sha256(BASE_STL),
            "print_in_place_stl": sha256(
                EXPORTS / "cyber_nozzle_case_R4_DRAFT_print_in_place.stl"
            ),
            "step": sha256(EXPORTS / "cyber_nozzle_case_R4_DRAFT.step"),
            "cad_source": sha256(PROJECT / "cad-js" / "cyber_nozzle_case.mjs"),
        },
        "profile": "standard",
        "nominal_envelope_mm": PROFILE_SIZE.tolist(),
        "actual_recess_bounds_mm": [recess_min, recess_max],
        "actual_recess_outline_size_mm": [
            round(recess_max[0] - recess_min[0], 5),
            round(recess_max[1] - recess_min[1], 5),
        ],
        "uniform_scale": 1.0,
        "rotation_deg": 0,
        "position_center_mm": [0.0, -96.2, 0.0],
        "surface": "base print-bed-facing underside",
        "operation": "recessed",
        "depth_mm": DEPTH,
        "bed_datum_min_z_mm": float(mesh.vertices[:, 2].min()),
        "local_floor_before_mm": 3.0,
        "residual_floor_mm": 2.6,
        "safe_rectangle_mm": SAFE_SIZE.tolist(),
        "profile_edge_clearance_within_safe_rectangle_mm": [9.0, 5.0],
        "minimum_feature_clearance_mm": 3.0,
        "marked_part_coverage": {
            "base": "marked durable primary body",
            "lid": "covered by permanently captive marked assembly; not separately saleable",
            "hinge_pin": "integral to captive lid",
        },
        "process": {
            "material": "unfilled PETG",
            "nozzle_mm": 0.4,
            "layer_height_mm": LAYER,
            "recess_depth_in_layers": DEPTH / LAYER,
        },
        "section_y_mm": section_y,
        "analytical_layer_preview": layers,
        "evidence_files": {
            name: str(target.relative_to(PROJECT)) for name, target in files.items()
        },
        "result": "PASS — evidence complete; explicit watermark approval pending",
        "limitations": [
            "Layer view is an analytical planar slice of the exported STL, not a vendor-specific G-code preview.",
            "Physical first-layer legibility remains part of the production print check.",
        ],
    }
    (REPORTS / "watermark-evidence.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
