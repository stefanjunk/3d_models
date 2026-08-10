#!/usr/bin/env python3
"""Create the seamless reference height map matching the analytic twill intent."""

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "carbon_weave_heightmap.png"


def periodic_distance(value, period):
    value = np.mod(value, period)
    return np.minimum(value, period - value)


def main():
    size = 256
    yy, xx = np.mgrid[0:size, 0:size]
    period = 32.0
    primary = np.exp(-((periodic_distance(xx + yy, period) / 4.0) ** 4))
    secondary = 0.52 * np.exp(-((periodic_distance(xx - yy + period / 2, period) / 2.8) ** 4))
    # Two-by-two checker modulation suggests strand dominance at crossings.
    checker = (((xx // (period / 2)) + (yy // (period / 2))) % 2).astype(float)
    field = np.maximum(primary * (0.82 + 0.18 * checker), secondary * (1.0 - 0.16 * checker))
    field = np.clip(field, 0, 1)
    image = (field * 65535).astype(np.uint16)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image).save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
