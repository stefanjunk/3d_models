#!/usr/bin/env python3
"""Render the actual exported binary STL triangles with a small orthographic rasterizer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from validate_stl import load_binary_stl


def normalized(vector: np.ndarray) -> np.ndarray:
    length = float(np.linalg.norm(vector))
    return vector / max(length, 1.0e-12)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1100)
    parser.add_argument(
        "--view",
        choices=("overall", "hardware", "wood-coupon", "r2-driver-front", "r2-overall"),
        default="overall",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    params = json.loads((root / "config" / "model-params.json").read_text(encoding="utf-8"))
    zone = float(params["layout"]["screwdriver_zone_width"])
    split = float(params["layout"]["depth_split"])
    floor = float(params["organizer"]["floor_thickness"])
    files = [
        ("DRAFT-driver-front-textured.stl", np.array([0.0, 0.0, 0.0]), np.array([82, 88, 94])),
        ("DRAFT-driver-back-textured.stl", np.array([0.0, split, 0.0]), np.array([88, 94, 100])),
        ("DRAFT-hardware-front-textured.stl", np.array([zone, 0.0, 0.0]), np.array([91, 97, 103])),
        ("DRAFT-hardware-back-textured.stl", np.array([zone, split, 0.0]), np.array([97, 103, 109])),
        ("DRAFT-screwdriver-comb.stl", np.array([4.0, split - 5.0, floor]), np.array([115, 121, 126])),
    ]
    if args.view == "r2-overall":
        files = [
            ("DRAFT-R2-driver-front-procedural-wood-unmarked.stl", np.array([0.0, 0.0, 0.0]), np.array([142, 94, 54])),
            ("DRAFT-R2-driver-back-procedural-wood-unmarked.stl", np.array([0.0, split, 0.0]), np.array([148, 99, 57])),
            ("DRAFT-R2-hardware-front-procedural-wood-unmarked.stl", np.array([zone, 0.0, 0.0]), np.array([151, 102, 60])),
            ("DRAFT-R2-hardware-back-procedural-wood-unmarked.stl", np.array([zone, split, 0.0]), np.array([157, 107, 64])),
            ("DRAFT-R2-screwdriver-comb-procedural-wood-unmarked.stl", np.array([4.0, split - 5.0, floor]), np.array([165, 116, 72])),
        ]
        center = np.array([params["organizer"]["width_x"] / 2, params["organizer"]["depth_y"] / 2, 32.0])
        camera = center + np.array([420.0, -520.0, 390.0])
    elif args.view == "r2-driver-front":
        files = [
            (
                "DRAFT-R2-driver-front-procedural-wood-unmarked.stl",
                np.array([0.0, 0.0, 0.0]),
                np.array([142, 94, 54]),
            )
        ]
        center = np.array([50.0, 93.25, 32.0])
        camera = center + np.array([175.0, -230.0, 175.0])
    elif args.view == "wood-coupon":
        files = [
            (
                "DRAFT-R2-procedural-wood-coupon.stl",
                np.array([0.0, 0.0, 0.0]),
                np.array([142, 94, 54]),
            )
        ]
        center = np.array([61.0, 40.0, 10.3])
        camera = center + np.array([150.0, -180.0, 135.0])
    elif args.view == "hardware":
        files = files[2:4]
        center = np.array([(zone + params["organizer"]["width_x"]) / 2, split, 30.0])
        camera = center + np.array([300.0, -390.0, 250.0])
    else:
        center = np.array([params["organizer"]["width_x"] / 2, params["organizer"]["depth_y"] / 2, 32.0])
        camera = center + np.array([420.0, -520.0, 390.0])
    forward = normalized(center - camera)
    right = normalized(np.cross(forward, np.array([0.0, 0.0, 1.0])))
    up = normalized(np.cross(right, forward))
    light = normalized(np.array([-0.35, -0.45, 1.0]))

    visible: list[tuple[float, np.ndarray, tuple[int, int, int]]] = []
    all_projected = []
    for filename, translation, color in files:
        triangles = load_binary_stl(root / "output" / "DRAFT" / filename) + translation
        edges_a = triangles[:, 1] - triangles[:, 0]
        edges_b = triangles[:, 2] - triangles[:, 0]
        normals = np.cross(edges_a, edges_b)
        lengths = np.linalg.norm(normals, axis=1)
        good = lengths > 1.0e-12
        normals[good] /= lengths[good, None]
        relative = triangles - center
        projected = np.stack(
            [relative @ right, relative @ up, relative @ forward], axis=-1
        )
        all_projected.append(projected[:, :, :2].reshape(-1, 2))
        face_centers = triangles.mean(axis=1)
        view_vectors = normalized(camera - face_centers.mean(axis=0))
        facing = (normals @ forward) < 0.0
        for index in np.nonzero(facing & good)[0]:
            shade = 0.34 + 0.66 * max(0.0, float(np.dot(normals[index], light)))
            face_color = tuple(int(np.clip(channel * shade + 18, 0, 255)) for channel in color)
            depth = float(projected[index, :, 2].mean())
            visible.append((depth, projected[index, :, :2], face_color))

    projected_all = np.concatenate(all_projected, axis=0)
    minimum = projected_all.min(axis=0)
    maximum = projected_all.max(axis=0)
    margin = 70
    scale = min(
        (args.width - 2 * margin) / max(maximum[0] - minimum[0], 1.0),
        (args.height - 2 * margin) / max(maximum[1] - minimum[1], 1.0),
    )

    image = Image.new("RGB", (args.width, args.height), (238, 240, 242))
    draw = ImageDraw.Draw(image)
    visible.sort(key=lambda item: item[0], reverse=True)
    for _, points, color in visible:
        pixel_points = []
        for u, v in points:
            x = margin + (u - minimum[0]) * scale
            y = args.height - margin - (v - minimum[1]) * scale
            pixel_points.append((float(x), float(y)))
        draw.polygon(pixel_points, fill=color)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(f"rendered {len(visible)} visible triangles to {args.output}")


if __name__ == "__main__":
    main()
