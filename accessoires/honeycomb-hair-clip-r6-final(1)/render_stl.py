#!/usr/bin/env python3
"""Small orthographic binary-STL renderer for deterministic preview images."""

from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def load_stl(path: Path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + count * 50:
        raise ValueError("Only binary STL is supported")
    triangles = np.empty((count, 3, 3), dtype=np.float64)
    for index in range(count):
        values = struct.unpack_from("<12fH", data, 84 + index * 50)
        triangles[index] = np.array(values[3:12]).reshape(3, 3)
    return triangles


def rotation_matrix(ax, ay, az):
    rx = np.array([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
    ry = np.array([[math.cos(ay), 0, math.sin(ay)], [0, 1, 0], [-math.sin(ay), 0, math.cos(ay)]])
    rz = np.array([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
    return rz @ ry @ rx


def render(triangles, size, angles, output: Path):
    background = np.array([20, 21, 23], dtype=np.uint8)
    canvas = np.empty((size, size, 3), dtype=np.uint8)
    canvas[:] = background
    depth = np.full((size, size), -np.inf, dtype=np.float64)

    center = (triangles.min(axis=(0, 1)) + triangles.max(axis=(0, 1))) / 2
    rotation = rotation_matrix(*[math.radians(v) for v in angles])
    transformed = (triangles - center) @ rotation.T
    xy = transformed[:, :, :2]
    min_xy = xy.min(axis=(0, 1))
    max_xy = xy.max(axis=(0, 1))
    scale = 0.82 * size / max(max_xy - min_xy)
    projected = np.empty_like(transformed)
    projected[:, :, 0] = (transformed[:, :, 0] - (min_xy[0] + max_xy[0]) / 2) * scale + size / 2
    projected[:, :, 1] = size / 2 - (transformed[:, :, 1] - (min_xy[1] + max_xy[1]) / 2) * scale
    projected[:, :, 2] = transformed[:, :, 2]

    light = np.array([-0.35, 0.55, 0.76])
    light /= np.linalg.norm(light)
    face_normals = np.cross(transformed[:, 1] - transformed[:, 0], transformed[:, 2] - transformed[:, 0])
    normal_lengths = np.linalg.norm(face_normals, axis=1)
    valid = normal_lengths > 1e-10
    face_normals[valid] /= normal_lengths[valid, None]
    shades = np.clip(0.28 + 0.72 * np.abs(face_normals @ light), 0.22, 1.0)

    order = np.argsort(projected[:, :, 2].mean(axis=1))
    image = Image.fromarray(canvas)
    draw = ImageDraw.Draw(image, 'RGB')
    for idx in order:
        pts = [(float(projected[idx, j, 0]), float(projected[idx, j, 1])) for j in range(3)]
        shade = shades[idx]
        base = np.array([91, 96, 104]) * shade
        color = tuple(int(v) for v in np.clip(base + np.array([8, 8, 10]), 0, 255))
        draw.polygon(pts, fill=color)

    # A subtle floor shadow and vignette improve readability without changing geometry.
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((size * 0.16, size * 0.73, size * 0.84, size * 0.89), fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.025))
    bg = Image.new('RGB', (size, size), tuple(background))
    bg = Image.alpha_composite(bg.convert('RGBA'), shadow)
    bg = Image.alpha_composite(bg, image.convert('RGBA'))
    output.parent.mkdir(parents=True, exist_ok=True)
    bg.convert('RGB').save(output, quality=95)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stl', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--size', type=int, default=1200)
    parser.add_argument('--angles', default='68,0,-28', help='x,y,z degrees')
    args = parser.parse_args()
    angles = tuple(float(value) for value in args.angles.split(','))
    render(load_stl(args.stl), args.size, angles, args.output)


if __name__ == '__main__':
    main()

