#!/usr/bin/env python3
"""Validate CyberVault meshes, build a two-object 3MF, and render QA views."""

from __future__ import annotations

import argparse
import json
import math
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


@dataclass
class Mesh:
    vertices: np.ndarray
    triangles: np.ndarray
    source_triangles: int


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = np.arange(size, dtype=np.int64)
        self.rank = np.zeros(size, dtype=np.uint8)

    def find(self, value: int) -> int:
        parent = self.parent
        root = value
        while parent[root] != root:
            root = int(parent[root])
        while parent[value] != value:
            nxt = int(parent[value])
            parent[value] = root
            value = nxt
        return root

    def union(self, left: int, right: int) -> None:
        a = self.find(left)
        b = self.find(right)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1


def read_binary_stl(target: Path, weld_tolerance: float = 1e-5) -> Mesh:
    data = target.read_bytes()
    if len(data) < 84:
        raise ValueError(f"{target}: not a binary STL")
    triangle_count = struct.unpack_from("<I", data, 80)[0]
    expected_size = 84 + triangle_count * 50
    if len(data) != expected_size:
        raise ValueError(
            f"{target}: binary STL size mismatch ({len(data)} != {expected_size})"
        )
    record = np.dtype(
        [
            ("normal", "<f4", (3,)),
            ("vertices", "<f4", (3, 3)),
            ("attribute", "<u2"),
        ]
    )
    raw = np.frombuffer(data, dtype=record, count=triangle_count, offset=84)
    corners = raw["vertices"].astype(np.float64).reshape(-1, 3)
    quantized = np.rint(corners / weld_tolerance).astype(np.int64)
    _, first, inverse = np.unique(
        quantized, axis=0, return_index=True, return_inverse=True
    )
    vertices = corners[first]
    triangles = inverse.reshape(-1, 3).astype(np.int64)
    return Mesh(vertices, triangles, triangle_count)


def write_binary_stl(target: Path, mesh: Mesh, header: str) -> None:
    points = mesh.vertices[mesh.triangles].astype("<f4")
    normals = np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    valid = lengths > 0
    normals[valid] /= lengths[valid, None]
    record = np.zeros(
        len(mesh.triangles),
        dtype=[("normal", "<f4", (3,)), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")],
    )
    record["normal"] = normals
    record["vertices"] = points
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        handle.write(header.encode("ascii", "replace")[:80].ljust(80, b"\0"))
        handle.write(struct.pack("<I", len(mesh.triangles)))
        handle.write(record.tobytes())


def analyze_mesh(mesh: Mesh, name: str) -> dict:
    vertices = mesh.vertices
    triangles = mesh.triangles
    tri_vertices = vertices[triangles]
    cross = np.cross(
        tri_vertices[:, 1] - tri_vertices[:, 0],
        tri_vertices[:, 2] - tri_vertices[:, 0],
    )
    twice_area = np.linalg.norm(cross, axis=1)
    degenerate = int(np.count_nonzero(twice_area <= 1e-10))
    signed_volume = float(
        np.einsum(
            "ij,ij->i",
            tri_vertices[:, 0],
            np.cross(tri_vertices[:, 1], tri_vertices[:, 2]),
        ).sum()
        / 6.0
    )

    directed_edges = np.concatenate(
        [
            triangles[:, [0, 1]],
            triangles[:, [1, 2]],
            triangles[:, [2, 0]],
        ],
        axis=0,
    )
    undirected = np.sort(directed_edges, axis=1)
    unique_edges, counts = np.unique(undirected, axis=0, return_counts=True)
    boundary_edges = int(np.count_nonzero(counts == 1))
    nonmanifold_edges = int(np.count_nonzero(counts > 2))

    directed_unique, directed_counts = np.unique(
        directed_edges, axis=0, return_counts=True
    )
    direction_map = {
        (int(edge[0]), int(edge[1])): int(count)
        for edge, count in zip(directed_unique, directed_counts, strict=True)
    }
    inconsistent_pairs = 0
    for a, b in unique_edges[counts == 2]:
        if direction_map.get((int(a), int(b)), 0) != 1 or direction_map.get(
            (int(b), int(a)), 0
        ) != 1:
            inconsistent_pairs += 1

    union_find = UnionFind(len(vertices))
    for a, b, c in triangles:
        union_find.union(int(a), int(b))
        union_find.union(int(b), int(c))
    used = np.unique(triangles)
    components = len({union_find.find(int(index)) for index in used})

    bounds_min = vertices.min(axis=0)
    bounds_max = vertices.max(axis=0)
    watertight = boundary_edges == 0 and nonmanifold_edges == 0
    consistently_oriented = inconsistent_pairs == 0
    return {
        "source": name,
        "vertices_welded": int(len(vertices)),
        "triangles": int(len(triangles)),
        "source_triangles": mesh.source_triangles,
        "connected_components": components,
        "watertight": watertight,
        "consistently_oriented": consistently_oriented,
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "inconsistent_edge_pairs": inconsistent_pairs,
        "degenerate_triangles": degenerate,
        "signed_volume_mm3": round(signed_volume, 6),
        "absolute_volume_mm3": round(abs(signed_volume), 6),
        "surface_area_mm2": round(float(twice_area.sum() / 2.0), 6),
        "bounds_mm": [
            [round(float(value), 6) for value in bounds_min],
            [round(float(value), 6) for value in bounds_max],
        ],
        "size_mm": [
            round(float(value), 6) for value in (bounds_max - bounds_min)
        ],
    }


def transform_closed_lid(mesh: Mesh) -> Mesh:
    vertices = mesh.vertices.copy()
    vertices[:, 1] *= -1.0
    vertices[:, 2] = 18.0 - vertices[:, 2]
    triangles = mesh.triangles[:, [0, 2, 1]].copy()
    return Mesh(vertices, triangles, mesh.source_triangles)


def combine_meshes(meshes: list[Mesh]) -> Mesh:
    vertices = []
    triangles = []
    offset = 0
    source_triangles = 0
    for mesh in meshes:
        vertices.append(mesh.vertices)
        triangles.append(mesh.triangles + offset)
        offset += len(mesh.vertices)
        source_triangles += mesh.source_triangles
    return Mesh(np.vstack(vertices), np.vstack(triangles), source_triangles)


def object_xml(object_id: int, name: str, mesh: Mesh) -> str:
    vertices = "\n".join(
        f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>'
        for x, y, z in mesh.vertices
    )
    triangles = "\n".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}"/>'
        for a, b, c in mesh.triangles
    )
    return (
        f'<object id="{object_id}" type="model" name="{escape(name)}"><mesh>'
        f"<vertices>{vertices}</vertices><triangles>{triangles}</triangles>"
        "</mesh></object>"
    )


def write_3mf(target: Path, base: Mesh, lid: Mesh) -> None:
    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="de-DE" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<metadata name="Title">CyberVault Düsen-Schatulle R4 DRAFT</metadata>'
        '<metadata name="Designer">JuSt Innovation</metadata>'
        '<metadata name="Description">Zwei Objekte: Unterkasten und unverlierbar gekoppelter Deckel; offene Print-in-place-Ausrichtung.</metadata>'
        f"<resources>{object_xml(1, 'CyberVault Unterkasten', base)}"
        f"{object_xml(2, 'CyberVault Deckel', lid)}</resources>"
        '<build><item objectid="1"/><item objectid="2"/></build></model>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        "</Types>"
    )
    relationships = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        "</Relationships>"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", relationships)
        archive.writestr("3D/3dmodel.model", model_xml)


def verify_3mf(target: Path) -> dict:
    with zipfile.ZipFile(target, "r") as archive:
        members = sorted(archive.namelist())
        model = archive.read("3D/3dmodel.model").decode("utf-8")
        bad_member = archive.testzip()
    return {
        "source": target.name,
        "zip_integrity": bad_member is None,
        "members": members,
        "object_count": model.count("<object "),
        "build_item_count": model.count("<item "),
        "units": "millimeter" if 'unit="millimeter"' in model else "unknown",
    }


def sample_triangle_indexes(mesh: Mesh, maximum: int = 90000) -> np.ndarray:
    if len(mesh.triangles) <= maximum:
        return np.arange(len(mesh.triangles))
    else:
        return np.linspace(0, len(mesh.triangles) - 1, maximum, dtype=int)


def set_equal_axes(axis, vertices: np.ndarray, pad: float = 0.03) -> None:
    lower = vertices.min(axis=0)
    upper = vertices.max(axis=0)
    span = np.maximum(upper - lower, 1.0)
    margin = span * pad
    axis.set_xlim(lower[0] - margin[0], upper[0] + margin[0])
    axis.set_ylim(lower[1] - margin[1], upper[1] + margin[1])
    axis.set_zlim(max(0, lower[2] - margin[2]), upper[2] + margin[2])
    display_span = span + 2 * margin
    display_span[2] = max(display_span[2], 0.12 * max(display_span[0], display_span[1]))
    axis.set_box_aspect(display_span)


def add_mesh(axis, mesh: Mesh, color: str, alpha: float = 1.0) -> None:
    indexes = sample_triangle_indexes(mesh)
    triangles = mesh.vertices[mesh.triangles[indexes]]
    normals = np.cross(
        triangles[:, 1] - triangles[:, 0],
        triangles[:, 2] - triangles[:, 0],
    )
    lengths = np.maximum(np.linalg.norm(normals, axis=1), 1e-12)
    normals /= lengths[:, None]
    light_direction = np.array([0.35, -0.45, 0.82])
    diffuse = np.clip(0.42 + 0.58 * np.abs(normals @ light_direction), 0.25, 1.0)
    base_rgb = np.asarray(matplotlib.colors.to_rgb(color))
    facecolors = np.column_stack((diffuse[:, None] * base_rgb[None, :], np.full(len(diffuse), alpha)))
    collection = Poly3DCollection(
        triangles,
        facecolors=facecolors,
        edgecolors="none",
        linewidth=0,
    )
    axis.add_collection3d(collection)


def style_axis(axis, title: str) -> None:
    axis.set_title(title, color="#dffaff", pad=12, fontsize=13, weight="bold")
    axis.set_facecolor("#071219")
    axis.grid(False)
    for pane in [axis.xaxis.pane, axis.yaxis.pane, axis.zaxis.pane]:
        pane.set_facecolor((0.03, 0.09, 0.12, 1.0))
        pane.set_edgecolor((0.15, 0.45, 0.52, 0.25))
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_zticks([])


def render_qa(
    open_target: Path,
    closed_target: Path,
    base: Mesh,
    lid: Mesh,
    status_label: str = "DRAFT",
) -> None:
    cyan = "#38d8e8"
    graphite = "#26424a"

    fig = plt.figure(figsize=(9, 12), facecolor="#050b10")
    axis = fig.add_subplot(111, projection="3d")
    add_mesh(axis, base, graphite)
    add_mesh(axis, lid, cyan, 0.86)
    all_vertices = np.vstack([base.vertices, lid.vertices])
    set_equal_axes(axis, all_vertices, pad=0.01)
    axis.view_init(elev=61, azim=-45)
    style_axis(axis, f"CyberVault R4 · offen / Drucklage · {status_label}")
    fig.text(
        0.5,
        0.035,
        "12 Aufnahmen · 4 beschriftete Dreiergruppen · 0,35 mm Passspiel je Seite",
        ha="center",
        color="#8cb7bd",
        fontsize=10,
    )
    fig.savefig(open_target, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    closed_lid = transform_closed_lid(lid)
    fig = plt.figure(figsize=(10, 7), facecolor="#050b10")
    axis = fig.add_subplot(111, projection="3d")
    add_mesh(axis, base, graphite)
    add_mesh(axis, closed_lid, cyan, 0.9)
    closed_vertices = np.vstack([base.vertices, closed_lid.vertices])
    set_equal_axes(axis, closed_vertices, pad=0.12)
    axis.view_init(elev=28, azim=-48)
    style_axis(axis, f"CyberVault R4 · geschlossen · {status_label}")
    fig.text(
        0.5,
        0.035,
        "Starre Nominalstellung kollisionsfrei; Scharnier und Rastverschluss physisch bestätigt",
        ha="center",
        color="#8cb7bd",
        fontsize=10,
    )
    fig.savefig(closed_target, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def render_lid_relief_top(
    target: Path, lid: Mesh, status_label: str = "DRAFT"
) -> None:
    closed_lid = transform_closed_lid(lid)
    points = closed_lid.vertices[closed_lid.triangles]
    centroids = points.mean(axis=1)
    selected = centroids[:, 2] >= 17.30
    polygons = points[selected, :, :2]
    heights = centroids[selected, 2]
    order = np.argsort(heights)
    polygons = polygons[order]
    heights = heights[order]
    depth = np.clip((18.0 - heights) / 0.64, 0.0, 1.0)
    colors = np.zeros((len(depth), 4), dtype=float)
    colors[:, 0] = 0.06 + 0.05 * (1 - depth)
    colors[:, 1] = 0.22 + 0.58 * (1 - depth)
    colors[:, 2] = 0.27 + 0.63 * (1 - depth)
    colors[:, 3] = 1.0

    fig, axis = plt.subplots(figsize=(6.5, 14), facecolor="#050b10")
    axis.set_facecolor("#071219")
    axis.add_collection(PolyCollection(polygons, facecolors=colors, edgecolors="none"))
    lower = polygons.reshape(-1, 2).min(axis=0)
    upper = polygons.reshape(-1, 2).max(axis=0)
    axis.set_xlim(lower[0] - 3, upper[0] + 3)
    axis.set_ylim(lower[1] - 3, upper[1] + 3)
    axis.set_aspect("equal")
    axis.set_title(
        f"CyberVault R4 · fertige Deckelaußenseite · {status_label}",
        color="#dffaff",
        fontsize=14,
        weight="bold",
        pad=14,
    )
    axis.axis("off")
    fig.text(
        0.5,
        0.025,
        f"Tatsächliches {status_label}-STL · 0,64 / 0,32 mm Gravur · geschlossene Leserichtung",
        ha="center",
        color="#8cb7bd",
        fontsize=9,
    )
    fig.savefig(target, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

def assert_mesh(report: dict, expected_components: int) -> None:
    failures = []
    if not report["watertight"]:
        failures.append("not watertight")
    if not report["consistently_oriented"]:
        failures.append("inconsistent orientation")
    if report["connected_components"] != expected_components:
        failures.append(
            f"{report['connected_components']} components, expected {expected_components}"
        )
    if report["degenerate_triangles"]:
        failures.append(f"{report['degenerate_triangles']} degenerate triangles")
    if failures:
        raise RuntimeError(f"{report['source']}: " + "; ".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-dir", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()
    export_dir = project_dir / "exports" / "draft"
    report_dir = project_dir / "reports"
    render_dir = project_dir / "renders"
    report_dir.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    prefix = "cyber_nozzle_case_R4_DRAFT"

    targets = {
        "base": export_dir / f"{prefix}_base_manifold.stl",
        "lid": export_dir / f"{prefix}_lid_relief_manifold.stl",
        "assembly": export_dir / f"{prefix}_print_in_place.stl",
        "hinge_coupon": export_dir / "hinge_coupon_R4_DRAFT.stl",
    }
    base_mesh = read_binary_stl(targets["base"])
    lid_mesh = read_binary_stl(targets["lid"])
    write_binary_stl(
        targets["assembly"],
        combine_meshes([base_mesh, lid_mesh]),
        "CyberVault R4 print-in-place assembly",
    )
    meshes = {name: read_binary_stl(target) for name, target in targets.items()}
    reports = {
        name: analyze_mesh(mesh, targets[name].name) for name, mesh in meshes.items()
    }
    assert_mesh(reports["base"], 1)
    assert_mesh(reports["lid"], 1)
    assert_mesh(reports["assembly"], 2)
    assert_mesh(reports["hinge_coupon"], 2)

    envelope = reports["assembly"]["size_mm"]
    bed = [420.0, 420.0, 500.0]
    bed_fit = all(size <= limit for size, limit in zip(envelope, bed, strict=True))
    if not bed_fit:
        raise RuntimeError(f"Print envelope {envelope} exceeds Kobra 3 Max bed {bed}")

    brep_report = json.loads(
        (report_dir / "production-cad-candidate.json").read_text(encoding="utf-8")
    )
    relief_report = json.loads(
        (report_dir / "cyber-lid-relief-boolean.json").read_text(encoding="utf-8")
    )
    expected_volume = {
        "base": brep_report["base"]["volume_mm3"],
        "lid": relief_report["output_lid_volume_mm3"],
    }
    volume_delta = {
        name: round(
            abs(reports[name]["absolute_volume_mm3"] - expected_volume[name])
            / expected_volume[name]
            * 100.0,
            6,
        )
        for name in ["base", "lid"]
    }
    if any(delta > 0.5 for delta in volume_delta.values()):
        raise RuntimeError(f"STL/B-Rep volume delta too high: {volume_delta}")

    three_mf = export_dir / f"{prefix}.3mf"
    write_3mf(three_mf, meshes["base"], meshes["lid"])
    three_mf_report = verify_3mf(three_mf)
    if not (
        three_mf_report["zip_integrity"]
        and three_mf_report["object_count"] == 2
        and three_mf_report["build_item_count"] == 2
    ):
        raise RuntimeError(f"3MF verification failed: {three_mf_report}")

    open_render = render_dir / "cyber-nozzle-case-R4-DRAFT-candidate-open.png"
    closed_render = render_dir / "cyber-nozzle-case-R4-DRAFT-candidate-closed.png"
    relief_render = render_dir / "cyber-nozzle-case-R4-DRAFT-relief-top.png"
    render_qa(open_render, closed_render, meshes["base"], meshes["lid"])
    render_lid_relief_top(relief_render, meshes["lid"])

    manifold_report = json.loads(
        (report_dir / "manifold-collision-candidate.json").read_text(
            encoding="utf-8"
        )
    )
    collision = manifold_report["collision_volume_mm3"]
    collision_pass = (
        abs(collision["open"]) <= 1e-6
        and abs(collision["closed_rigid_nominal"]) <= 1e-6
    )
    if not collision_pass:
        raise RuntimeError(f"Collision validation failed: {collision}")

    report = {
        "geometry_revision": brep_report["geometry_revision"],
        "release_status": "DRAFT — REVISION 4 COMPLETE RELEASE APPROVAL PENDING",
        "validator": "independent binary-STL topology analysis plus manifold-3d collision analysis",
        "meshes": reports,
        "stl_to_brep_volume_delta_percent": volume_delta,
        "print_bed": {
            "printer": "Anycubic Kobra 3 Max",
            "available_mm": bed,
            "assembly_envelope_mm": envelope,
            "fits": bed_fit,
        },
        "body_count": {
            "required": 2,
            "observed_in_print_in_place_stl": reports["assembly"][
                "connected_components"
            ],
            "pass": reports["assembly"]["connected_components"] == 2,
        },
        "collision_volume_mm3": collision,
        "collision_pass": collision_pass,
        "three_mf": three_mf_report,
        "qa_renders": [open_render.name, closed_render.name, relief_render.name],
        "digital_result": "PASS",
        "physical_test_evidence": {
            "hinge": "PASS BASIC FUNCTION — user confirmed fit on 2026-08-11",
            "latch": "PASS BASIC FUNCTION — user confirmed fit on 2026-08-11",
        },
        "physical_tests_pending": [
            "optional documented 100-cycle pretest and 1000-cycle lifetime target",
            "full-case loaded inversion and 40 cm label-readability check",
        ],
    }
    output = report_dir / "mesh-validation-candidate.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
