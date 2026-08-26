#!/usr/bin/env python3
"""Inventory and render immutable image-to-3D GLB source meshes.

The script is diagnostic only: it never modifies the source GLBs.  It writes
an auditable JSON inventory and orthographic contact sheets used to establish
scale, orientation, repair strategy, and interface ownership.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection


def glb_manifest(path: Path) -> dict:
    data = path.read_bytes()
    magic, version, declared_length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or declared_length != len(data):
        raise ValueError(f"Invalid GLB header: {path}")
    offset = 12
    document: dict = {}
    while offset + 8 <= len(data):
        chunk_length, chunk_type = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunk = data[offset : offset + chunk_length]
        offset += chunk_length
        if chunk_type == b"JSON":
            document = json.loads(chunk.decode("utf-8").rstrip("\x00 "))
            break
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "asset": document.get("asset", {}),
        "declared": {
            key: len(document.get(key, []))
            for key in ("nodes", "meshes", "materials", "textures", "images", "animations")
        },
    }


def load_single_mesh(path: Path) -> trimesh.Trimesh:
    scene = trimesh.load(path, force="scene", process=False)
    meshes = []
    for node_name in scene.graph.nodes_geometry:
        transform, geometry_name = scene.graph[node_name]
        mesh = scene.geometry[geometry_name].copy()
        mesh.apply_transform(transform)
        meshes.append(mesh)
    if not meshes:
        raise ValueError(f"No triangle geometry in {path}")
    return meshes[0] if len(meshes) == 1 else trimesh.util.concatenate(meshes)


def topology(mesh: trimesh.Trimesh) -> dict:
    edge_counts = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    components = trimesh.graph.connected_components(
        mesh.face_adjacency,
        nodes=np.arange(len(mesh.faces)),
        min_len=1,
    )
    component_sizes = sorted((len(item) for item in components), reverse=True)
    return {
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "connected_face_components": int(len(component_sizes)),
        "largest_component_fraction": float(component_sizes[0] / len(mesh.faces)),
        "boundary_edges": int(np.count_nonzero(edge_counts == 1)),
        "nonmanifold_edges": int(np.count_nonzero(edge_counts > 2)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "euler_number": int(mesh.euler_number),
        "signed_volume_source_units3": float(mesh.volume),
    }


def textured_face_colors(mesh: trimesh.Trimesh) -> np.ndarray:
    try:
        vertex = mesh.visual.to_color().vertex_colors[:, :3].astype(float) / 255.0
        color = vertex[mesh.faces].mean(axis=1)
    except Exception:
        color = np.full((len(mesh.faces), 3), [0.78, 0.74, 0.67])
    normals = mesh.face_normals
    light = np.array([-0.25, -0.40, 0.88])
    light /= np.linalg.norm(light)
    shade = np.clip(0.48 + 0.52 * np.maximum(0.0, normals @ light), 0.35, 1.0)
    return np.clip(color * shade[:, None] + 0.04, 0.0, 1.0)


def rotation_matrix(elevation_deg: float, azimuth_deg: float) -> np.ndarray:
    elevation = math.radians(elevation_deg)
    azimuth = math.radians(azimuth_deg)
    rz = np.array(
        [
            [math.cos(azimuth), -math.sin(azimuth), 0.0],
            [math.sin(azimuth), math.cos(azimuth), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    rx = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(elevation), -math.sin(elevation)],
            [0.0, math.sin(elevation), math.cos(elevation)],
        ]
    )
    return rx @ rz


def draw_view(
    ax,
    mesh: trimesh.Trimesh,
    colors: np.ndarray,
    rotation: np.ndarray,
    title: str,
) -> None:
    verts = mesh.vertices @ rotation.T
    projected = verts[:, :2]
    faces = mesh.faces
    polygons = projected[faces]
    depths = verts[faces, 2].mean(axis=1)
    order = np.argsort(depths)
    collection = PolyCollection(
        polygons[order],
        facecolors=colors[order],
        edgecolors="none",
        linewidths=0,
        rasterized=True,
    )
    ax.add_collection(collection)
    minimum = projected.min(axis=0)
    maximum = projected.max(axis=0)
    span = np.maximum(maximum - minimum, 1e-9)
    margin = span * 0.06
    ax.set_xlim(minimum[0] - margin[0], maximum[0] + margin[0])
    ax.set_ylim(minimum[1] - margin[1], maximum[1] + margin[1])
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=8, color="#433b32", pad=3)
    ax.axis("off")


def render_one(path: Path, mesh: trimesh.Trimesh, output: Path) -> None:
    colors = textured_face_colors(mesh)
    views = [
        (np.eye(3), "XY / Reliefvorderseite"),
        (rotation_matrix(25.0, -28.0), "Schrägansicht"),
        (rotation_matrix(90.0, 0.0), "XZ / Seitenprofil"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.0), dpi=180)
    fig.patch.set_facecolor("#f2eee7")
    for ax, (rotation, title) in zip(axes, views):
        ax.set_facecolor("#f2eee7")
        draw_view(ax, mesh, colors, rotation, title)
    fig.suptitle(path.name, fontsize=13, weight="bold", color="#2e2923")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(output, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    report = {"unit_policy": "Raw coordinates are preserved; declared metre units are not trusted for product scale.", "files": {}}
    for path in sorted(args.input.glob("*.glb")):
        mesh = load_single_mesh(path)
        bounds = mesh.bounds
        entry = glb_manifest(path)
        entry.update(
            {
                "bounds_source_units": np.round(bounds, 8).tolist(),
                "extents_source_units": np.round(mesh.extents, 8).tolist(),
                "centroid_source_units": np.round(mesh.centroid, 8).tolist(),
                "visual_kind": mesh.visual.kind,
                "has_uv": bool(getattr(mesh.visual, "uv", None) is not None),
                "topology": topology(mesh),
            }
        )
        material = getattr(mesh.visual, "material", None)
        image = getattr(material, "baseColorTexture", None) if material is not None else None
        entry["base_color_texture_px"] = list(image.size) if image is not None else None
        report["files"][path.name] = entry
        render_one(path, mesh, args.output / f"{path.stem}_inspection.png")

    (args.output / "raw_glb_inventory.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
