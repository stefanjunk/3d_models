#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import trimesh


def build_cylinder(segments: int = 64, radius: float = 15.0, height: float = 30.0):
    vertices = []
    uvs = []
    faces = []
    # Side with a duplicated UV seam.
    for i in range(segments + 1):
        angle = 2.0 * np.pi * i / segments
        x, y = radius * np.cos(angle), radius * np.sin(angle)
        vertices.extend([[x, y, 0.0], [x, y, height]])
        u = i / segments
        uvs.extend([[u, 0.0], [u, 1.0]])
    for i in range(segments):
        a, b = 2 * i, 2 * i + 1
        c, d = 2 * (i + 1), 2 * (i + 1) + 1
        faces.extend([[a, c, b], [b, c, d]])

    # Caps get a constant orange UV sample. Separate vertices keep the side seam clean.
    for z, reverse in [(0.0, True), (height, False)]:
        center = len(vertices)
        vertices.append([0.0, 0.0, z])
        uvs.append([0.02, 0.02])
        ring = []
        for i in range(segments):
            angle = 2.0 * np.pi * i / segments
            ring.append(len(vertices))
            vertices.append([radius * np.cos(angle), radius * np.sin(angle), z])
            uvs.append([0.02, 0.02])
        for i in range(segments):
            a, b = ring[i], ring[(i + 1) % segments]
            faces.append([center, b, a] if reverse else [center, a, b])
    return np.asarray(vertices, float), np.asarray(faces, int), np.asarray(uvs, float)


def make_texture(path: Path, width: int = 512, height: int = 256) -> None:
    colors = {"orange": "#F26A21", "white": "#F2F0E8", "black": "#181818", "blue": "#2979C7"}
    image = Image.new("RGB", (width, height), colors["orange"])
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, int(height * 0.42), width, int(height * 0.58)], fill=colors["blue"])
    draw.ellipse([int(width * 0.08), int(height * 0.12), int(width * 0.32), int(height * 0.39)], fill=colors["white"])
    draw.ellipse([int(width * 0.58), int(height * 0.62), int(width * 0.86), int(height * 0.91)], fill=colors["white"])
    draw.rectangle([int(width * 0.39), int(height * 0.10), int(width * 0.46), int(height * 0.36)], fill=colors["black"])
    draw.rectangle([int(width * 0.90), int(height * 0.64), int(width * 0.96), int(height * 0.91)], fill=colors["black"])
    image.save(path)


def write_obj(path: Path, vertices: np.ndarray, faces: np.ndarray, uvs: np.ndarray) -> None:
    mtl_name = path.with_suffix(".mtl").name
    lines = [f"mtllib {mtl_name}", "o textured_cylinder"]
    lines += [f"v {v[0]:.9g} {v[1]:.9g} {v[2]:.9g}" for v in vertices]
    lines += [f"vt {uv[0]:.9g} {uv[1]:.9g}" for uv in uvs]
    lines += ["usemtl printable_texture"]
    for face in faces:
        indices = [int(i) + 1 for i in face]
        lines.append("f " + " ".join(f"{i}/{i}" for i in indices))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.with_suffix(".mtl").write_text(
        "newmtl printable_texture\nKd 1 1 1\nmap_Kd texture.png\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    vertices, faces, uvs = build_cylinder()
    texture_path = args.output_dir / "texture.png"
    make_texture(texture_path)
    obj_path = args.output_dir / "textured-cylinder.obj"
    write_obj(obj_path, vertices, faces, uvs)

    # Also write a GLB when the installed trimesh exporter supports embedded texture data.
    try:
        visual = trimesh.visual.texture.TextureVisuals(uv=uvs, image=Image.open(texture_path))
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, visual=visual, process=False)
        (args.output_dir / "textured-cylinder.glb").write_bytes(mesh.export(file_type="glb"))
    except Exception as exc:
        (args.output_dir / "glb-export-note.txt").write_text(f"Optional GLB export unavailable: {exc}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
