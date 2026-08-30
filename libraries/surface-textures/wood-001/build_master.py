#!/usr/bin/env python3
"""Build the wood-001 16-bit master tile from the proven reference source.

The reference print (honeycomb wall shelf) sampled assets/holz.png through a
HeightMap loader that converts RGB to grayscale via the plain channel mean.
This builder replicates that conversion exactly so the master tile stays
bit-faithful to the proven geometry pipeline, then persists provenance,
seam metrics, and an optional periodic edge blend.

Usage:
    python3 build_master.py [--blend-px N]

Outputs (next to this script):
    master/wood-001-tile-16bit.png              master geometry input
    master/wood-001-tile-16bit.png.source.json  registration + metrics
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE.parents[2]
    / "products/organization-storage/mm-wall-001-honeycomb-wood-wall-shelf"
    / "setzkasten/honeycomb-wood-wall-shelf/assets/holz.png"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_grayscale(path: Path) -> np.ndarray:
    """Replicate the reference HeightMap loader: RGB -> channel mean, [0, 1]."""
    raw = np.asarray(Image.open(path))
    if raw.ndim == 3:
        raw = raw[..., :3].astype(np.float32).mean(axis=2)
    raw = raw.astype(np.float32)
    maximum = float(raw.max())
    if maximum > 1.0:
        raw /= 65535.0 if maximum > 255.0 else 255.0
    return np.clip(raw, 0.0, 1.0)


def seam_metrics(a: np.ndarray) -> dict:
    return {
        "seam_x_mean_abs": float(np.abs(a[:, 0] - a[:, -1]).mean()),
        "seam_y_mean_abs": float(np.abs(a[0, :] - a[-1, :]).mean()),
        "avg_abs_dx": float(np.abs(np.diff(a, axis=1)).mean()),
        "avg_abs_dy": float(np.abs(np.diff(a, axis=0)).mean()),
    }


def periodic_edge_blend(a: np.ndarray, blend_px: int) -> np.ndarray:
    """Blend a width-blend_px band on each side toward a shared seam value.

    Deterministic and local: pixels farther than blend_px from a tile edge are
    unchanged. Near-edge pixels relax toward the mean of the two opposing edge
    lines, so the periodic wrap becomes continuous while the tile interior and
    the exact edge-adjacent look of the proven print are preserved.
    """
    if blend_px <= 0:
        return a
    out = a.copy()
    h, w = a.shape
    bx = min(blend_px, w // 4)
    by = min(blend_px, h // 4)
    ref_x = 0.5 * (a[:, 0] + a[:, -1])
    ref_y = 0.5 * (a[0, :] + a[-1, :])
    for j in range(bx):
        alpha = (j + 1) / (bx + 1)  # 0 at edge -> 1 away from edge
        out[:, j] = a[:, j] * alpha + ref_x * (1.0 - alpha)
        out[:, w - 1 - j] = a[:, w - 1 - j] * alpha + ref_x * (1.0 - alpha)
    for i in range(by):
        alpha = (i + 1) / (by + 1)
        out[i, :] = out[i, :] * alpha + ref_y * (1.0 - alpha)
        out[h - 1 - i, :] = out[h - 1 - i, :] * alpha + ref_y * (1.0 - alpha)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--blend-px",
        type=int,
        default=0,
        help="periodic edge blend width in pixels (0 keeps the raw proven tile)",
    )
    args = parser.parse_args()
    if args.blend_px < 0:
        raise SystemExit("--blend-px must be >= 0")

    source_sha = sha256(SOURCE)
    image = Image.open(SOURCE)
    gray = load_grayscale(SOURCE)
    raw_metrics = seam_metrics(gray)
    blended = periodic_edge_blend(gray, args.blend_px)
    final_metrics = seam_metrics(blended)

    master_dir = HERE / "master"
    master_dir.mkdir(exist_ok=True)
    tile_path = master_dir / "wood-001-tile-16bit.png"
    tile = (np.round(blended * 65535.0)).astype(np.uint16)
    Image.fromarray(tile).save(tile_path)
    tile_sha = sha256(tile_path)

    registration = {
        "texture_id": "wood-001",
        "source_path": str(SOURCE.relative_to(HERE.parents[2])),
        "source_sha256": source_sha,
        "source_size_px": list(image.size),
        "source_mode": image.mode,
        "source_precision_bits": 8,
        "conversion": "mean of RGB channels, then linear map to uint16 (bit-faithful to reference HeightMap loader)",
        "blend_px": args.blend_px,
        "master_path": str(tile_path.relative_to(HERE)),
        "master_sha256": tile_sha,
        "master_size_px": list(image.size),
        "master_bit_depth": 16,
        "seam_metrics_source": raw_metrics,
        "seam_metrics_master": final_metrics,
        "note": "8-bit source precision is preserved honestly; the 16-bit container avoids pipeline quantization.",
    }
    (master_dir / (tile_path.name + ".source.json")).write_text(
        json.dumps(registration, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(registration, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
