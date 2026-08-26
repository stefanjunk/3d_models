#!/usr/bin/env python3
"""Create a deterministic 16-bit botanical-wave demo heightmap."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--width", type=int, default=1800)
    parser.add_argument("--height", type=int, default=700)
    args = parser.parse_args()
    x = np.linspace(-1.0, 1.0, args.width)
    y = np.linspace(-1.0, 1.0, args.height)
    xx, yy = np.meshgrid(x, y)
    wave = 0.20 * (np.sin(8.0 * xx + 2.2 * np.sin(3.0 * yy)) + 1.0)
    petals = np.zeros_like(wave)
    for center_x in (-0.62, 0.0, 0.62):
        radius = np.sqrt((xx - center_x) ** 2 + (1.25 * yy) ** 2)
        angle = np.arctan2(1.25 * yy, xx - center_x)
        petals += np.exp(-7.0 * radius**2) * (0.45 + 0.45 * np.cos(6.0 * angle) ** 2)
    field = np.clip(0.10 + wave + petals, 0.0, 1.0)
    image = np.round(field * 65535.0).astype(np.uint16)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
