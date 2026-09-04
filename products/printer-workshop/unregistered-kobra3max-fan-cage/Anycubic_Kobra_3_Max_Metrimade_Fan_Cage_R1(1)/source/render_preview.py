#!/usr/bin/env python3
"""Create a lightweight, deterministic preview from the generated voxel bodies."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from generate_fan_cage import PITCH, make_occupancy


COLORS = {
    "body_navy": (17, 36, 49, 255),
    "brand_teal": (8, 119, 125, 255),
    "brand_aqua": (127, 213, 211, 255),
    "brand_sand": (199, 171, 130, 255),
}


def resized_mask(mask: np.ndarray, scale: int) -> Image.Image:
    return Image.fromarray((mask.astype(np.uint8) * 255), mode="L").resize(
        (mask.shape[1] * scale, mask.shape[0] * scale), Image.Resampling.NEAREST
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "preview_metrimade_D52.png"
    occs, meta = make_occupancy(52.0)
    cage = occs["single"]
    scale = 2
    model_w = cage.shape[2] * scale
    model_h = cage.shape[1] * scale
    canvas = Image.new("RGB", (1500, 1080), (238, 241, 245))
    draw = ImageDraw.Draw(canvas)

    front_origin = (55, 115)
    # Back geometry is offset up-right to make the wraparound shell depth readable.
    for k in range(cage.shape[0] - 1, -1, -1):
        mask = resized_mask(cage[k], scale)
        alpha = mask.point(lambda value: 125 if value else 0)
        shade = int(70 + 45 * (1.0 - k / max(cage.shape[0] - 1, 1)))
        layer = Image.new("RGBA", mask.size, (shade, shade + 2, shade + 7, 0))
        layer.putalpha(alpha)
        dx = int(round(k * PITCH * scale * 0.65))
        dy = -int(round(k * PITCH * scale * 0.35))
        canvas.paste(layer, (front_origin[0] + dx, front_origin[1] + dy), layer)

    for name in ("body_navy", "brand_teal", "brand_aqua", "brand_sand"):
        mask = resized_mask(occs[name][0], scale)
        layer = Image.new("RGBA", mask.size, COLORS[name])
        layer.putalpha(mask)
        canvas.paste(layer, front_origin, layer)

    # Side profile is an exact union projection, enlarged for legibility.
    side = cage.any(axis=1)  # z,x
    side_scale = 1
    side_img = resized_mask(side, side_scale)
    side_rgba = Image.new("RGBA", side_img.size, (35, 39, 46, 255))
    side_rgba.putalpha(side_img)
    side_x = 860
    side_y = 340
    canvas.paste(side_rgba, (side_x, side_y), side_rgba)

    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    draw.text((55, 20), "Metrimade · Kobra 3 Max Printhead Cover", fill=(25, 28, 33), font=title_font)
    draw.text((860, 270), "Side profile", fill=(25, 28, 33), font=body_font)
    draw.text((860, 445), "10.8 mm wraparound depth", fill=(60, 65, 74), font=small_font)
    draw.text((860, 477), "1.6 mm honeycomb carrier", fill=(60, 65, 74), font=small_font)
    draw.text((860, 509), "2.4 mm fan badge", fill=(60, 65, 74), font=small_font)
    draw.text((860, 541), "6 fan clips + 4 side stabilizers", fill=(60, 65, 74), font=small_font)
    draw.text((860, 620), "D52 candidate", fill=(25, 28, 33), font=body_font)
    draw.text((860, 660), "72 × 88 mm full front face", fill=(60, 65, 74), font=small_font)
    draw.text((860, 692), "7.2 mm honeycomb pitch", fill=(60, 65, 74), font=small_font)
    draw.text((860, 724), "0.6 mm color inlay", fill=(60, 65, 74), font=small_font)
    draw.text((860, 772), f"Fan-zone open area: {meta['airflow_projection']['estimated_D40_open_area_percent']:.1f}%", fill=(60, 65, 74), font=small_font)
    draw.text((860, 804), f"Surround open area: {meta['brand']['cover']['projected_surround_open_area_percent']:.1f}%", fill=(60, 65, 74), font=small_font)
    draw.text((55, 1035), "Original mechanical design · supplied vector lockup · PETG recommended", fill=(82, 88, 98), font=small_font)
    canvas.save(output, optimize=True)
    print(output)


if __name__ == "__main__":
    main()
