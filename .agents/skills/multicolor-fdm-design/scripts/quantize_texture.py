#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.color import deltaE_ciede2000, rgb2lab

from common import hex_to_rgb8, load_palette, save_json, sha256_file


def map_rgb_to_palette(rgb01: np.ndarray, palette_rgb01: np.ndarray, chunk_size: int = 250_000) -> tuple[np.ndarray, np.ndarray]:
    flat = np.asarray(rgb01, dtype=np.float64).reshape(-1, 3)
    palette_lab = rgb2lab(palette_rgb01.reshape(1, -1, 3)).reshape(-1, 3)
    labels = np.empty(len(flat), dtype=np.int16)
    errors = np.empty(len(flat), dtype=np.float32)
    for start in range(0, len(flat), chunk_size):
        stop = min(start + chunk_size, len(flat))
        sample_lab = rgb2lab(flat[start:stop].reshape(-1, 1, 3)).reshape(-1, 3)
        distance = np.stack(
            [deltaE_ciede2000(sample_lab, color_lab[None, :]) for color_lab in palette_lab],
            axis=1,
        )
        labels[start:stop] = np.argmin(distance, axis=1)
        errors[start:stop] = np.min(distance, axis=1)
    return labels.reshape(rgb01.shape[:2]), errors.reshape(rgb01.shape[:2])


def cleanup_small_islands(labels: np.ndarray, minimum_pixels: int, base_label: int = 0) -> tuple[np.ndarray, dict[str, Any]]:
    if minimum_pixels <= 1:
        return labels.copy(), {"minimum_pixels": minimum_pixels, "components_removed": 0, "pixels_reassigned": 0}
    output = labels.copy()
    removed = 0
    reassigned = 0
    structure = ndimage.generate_binary_structure(2, 2)
    for color in np.unique(labels):
        cc, count = ndimage.label(labels == color, structure=structure)
        if count == 0:
            continue
        sizes = np.bincount(cc.ravel())
        for component in range(1, count + 1):
            size = int(sizes[component])
            if size >= minimum_pixels:
                continue
            mask = cc == component
            ring = ndimage.binary_dilation(mask, structure=structure, iterations=2) & ~mask
            neighbors = output[ring]
            neighbors = neighbors[neighbors != color]
            target = int(np.bincount(neighbors).argmax()) if neighbors.size else int(base_label)
            output[mask] = target
            removed += 1
            reassigned += size
    return output, {"minimum_pixels": minimum_pixels, "components_removed": removed, "pixels_reassigned": reassigned}


def save_heatmap(path: Path, errors: np.ndarray) -> None:
    cap = max(float(np.percentile(errors, 99)), 1e-6)
    normalized = np.clip(errors / cap, 0.0, 1.0)
    # Blue -> cyan -> yellow -> red, implemented without an external plotting dependency.
    r = np.clip(2.0 * normalized, 0, 1)
    g = np.clip(2.0 - np.abs(4.0 * normalized - 2.0), 0, 1)
    b = np.clip(2.0 * (1.0 - normalized), 0, 1)
    rgb = (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)
    Image.fromarray(rgb, mode="RGB").save(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantize an image to an actual fixed filament palette using CIEDE2000.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--palette", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--labels-out", type=Path, help="Optional compressed NumPy label map (.npz).")
    parser.add_argument("--heatmap", type=Path)
    parser.add_argument("--minimum-island-pixels", type=int, default=0)
    parser.add_argument("--base-color", help="Palette id used when an isolated component has no neighbor.")
    parser.add_argument("--alpha-background", default=None, help="Hex color used behind transparency; defaults to first palette color.")
    args = parser.parse_args()

    palette = load_palette(args.palette)
    palette_rgb8 = np.array([hex_to_rgb8(item["display_hex"]) for item in palette], dtype=np.uint8)
    palette_rgb01 = palette_rgb8.astype(np.float64) / 255.0
    id_to_index = {item["id"]: index for index, item in enumerate(palette)}
    base_index = id_to_index.get(args.base_color, 0)

    rgba = np.asarray(Image.open(args.image).convert("RGBA"), dtype=np.float64) / 255.0
    bg_rgb8 = np.array(hex_to_rgb8(args.alpha_background or palette[base_index]["display_hex"]), dtype=np.float64) / 255.0
    alpha = rgba[..., 3:4]
    rgb = rgba[..., :3] * alpha + bg_rgb8.reshape(1, 1, 3) * (1.0 - alpha)

    raw_labels, raw_errors = map_rgb_to_palette(rgb, palette_rgb01)
    labels, cleanup = cleanup_small_islands(raw_labels, args.minimum_island_pixels, base_index)
    quantized = palette_rgb8[labels]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(quantized.astype(np.uint8), mode="RGB").save(args.output)
    if args.labels_out:
        args.labels_out.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.labels_out, labels=labels, palette_ids=np.array([p["id"] for p in palette]))
    if args.heatmap:
        args.heatmap.parent.mkdir(parents=True, exist_ok=True)
        save_heatmap(args.heatmap, raw_errors)

    counts = np.bincount(labels.ravel(), minlength=len(palette))
    fractions = counts / max(int(counts.sum()), 1)
    report = {
        "source": str(args.image.resolve()),
        "source_sha256": sha256_file(args.image),
        "palette": str(args.palette.resolve()),
        "palette_sha256": sha256_file(args.palette),
        "method": "fixed-palette CIE Lab / CIEDE2000; no dithering",
        "width_px": int(labels.shape[1]),
        "height_px": int(labels.shape[0]),
        "palette_entries": [
            {
                "index": index,
                "id": item["id"],
                "name": item["name"],
                "display_hex": item["display_hex"],
                "pixel_count": int(counts[index]),
                "fraction": float(fractions[index]),
            }
            for index, item in enumerate(palette)
        ],
        "delta_e": {
            "mean": float(np.mean(raw_errors)),
            "median": float(np.median(raw_errors)),
            "p95": float(np.percentile(raw_errors, 95)),
            "maximum": float(np.max(raw_errors)),
        },
        "cleanup": cleanup,
        "output": str(args.output.resolve()),
    }
    if args.report:
        save_json(args.report, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
