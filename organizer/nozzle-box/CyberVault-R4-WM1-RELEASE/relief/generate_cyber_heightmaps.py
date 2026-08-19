#!/usr/bin/env python3
"""Generate the printable two-level CyberVault R4 relief maps.

The 16-bit maps are manufacturing references, not raw luminance conversions:
black is untouched material, mid-gray is the 0.32 mm secondary engraving and
white is the 0.64 mm primary engraving. Side emboss remains a separate binary
mask because it is fused outward instead of subtracted inward.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def mm_to_px(value: float, pitch: float) -> int:
    return max(1, int(round(value / pitch)))


def xy_to_pixel(
    x: float,
    y: float,
    width_px: int,
    height_px: int,
    pitch: float,
) -> tuple[int, int]:
    return (
        int(round((width_px - 1) / 2 + x / pitch)),
        int(round((height_px - 1) / 2 - y / pitch)),
    )


def z_to_row(z: float, height_mm: float, pitch: float) -> int:
    return int(round((height_mm - z) / pitch))


def level_for(pattern: dict, depth_class: str) -> int:
    engraving = pattern["engraving"]
    if depth_class == "major":
        return 65535
    ratio = engraving["secondary_depth_mm"] / engraving["major_depth_mm"]
    return int(round(65535 * ratio))


def regular_hex(
    center: tuple[float, float],
    radius: float,
    rotation_deg: float,
) -> list[tuple[float, float]]:
    cx, cy = center
    return [
        (
            cx + radius * math.cos(math.radians(rotation_deg + 60 * i)),
            cy + radius * math.sin(math.radians(rotation_deg + 60 * i)),
        )
        for i in range(6)
    ]


def chamfered_rectangle(
    center: tuple[float, float],
    width: float,
    height: float,
    chamfer: float,
) -> list[tuple[float, float]]:
    cx, cy = center
    x0, x1 = cx - width / 2, cx + width / 2
    y0, y1 = cy - height / 2, cy + height / 2
    c = min(chamfer, width / 2, height / 2)
    return [
        (x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
        (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c),
    ]


def draw_hex_ring(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    outer_radius: float,
    inner_radius: float,
    rotation_deg: float,
    value: int,
    width_px: int,
    height_px: int,
    pitch: float,
) -> None:
    outer = [
        xy_to_pixel(x, y, width_px, height_px, pitch)
        for x, y in regular_hex(center, outer_radius, rotation_deg)
    ]
    inner = [
        xy_to_pixel(x, y, width_px, height_px, pitch)
        for x, y in regular_hex(center, inner_radius, rotation_deg)
    ]
    draw.polygon(outer, fill=value)
    draw.polygon(inner, fill=0)


def draw_polyline_mm(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    value: int,
    line_width_mm: float,
    width_px: int,
    height_px: int,
    pitch: float,
) -> None:
    draw.line(
        [xy_to_pixel(x, y, width_px, height_px, pitch) for x, y in points],
        fill=value,
        width=mm_to_px(line_width_mm, pitch),
        joint="curve",
    )


def draw_panel_frame(
    draw: ImageDraw.ImageDraw,
    panel: dict,
    value: int,
    width_px: int,
    height_px: int,
    pitch: float,
) -> None:
    outer = chamfered_rectangle(
        tuple(panel["center"]),
        float(panel["width_mm"]),
        float(panel["height_mm"]),
        float(panel["chamfer_mm"]),
    )
    line_width = float(panel["line_width_mm"])
    inner = chamfered_rectangle(
        tuple(panel["center"]),
        float(panel["width_mm"]) - 2 * line_width,
        float(panel["height_mm"]) - 2 * line_width,
        max(0.5, float(panel["chamfer_mm"]) - line_width),
    )
    draw.polygon(
        [xy_to_pixel(*p, width_px, height_px, pitch) for p in outer],
        fill=value,
    )
    draw.polygon(
        [xy_to_pixel(*p, width_px, height_px, pitch) for p in inner],
        fill=0,
    )


def rounded_rectangle_mask(
    size: tuple[int, int],
    width_mm: float,
    height_mm: float,
    radius_mm: float,
    pitch: float,
) -> Image.Image:
    width_px, height_px = size
    image = Image.new("1", size, 0)
    draw = ImageDraw.Draw(image)
    inset_x = ((width_px - 1) - width_mm / pitch) / 2
    inset_y = ((height_px - 1) - height_mm / pitch) / 2
    draw.rounded_rectangle(
        [inset_x, inset_y, width_px - 1 - inset_x, height_px - 1 - inset_y],
        radius=radius_mm / pitch,
        fill=1,
    )
    return image


def draw_perimeter_frames(
    image: Image.Image,
    pattern: dict,
    pitch: float,
) -> None:
    width_px, height_px = image.size
    for frame in pattern["perimeter_frames"]:
        value = level_for(pattern, frame["depth_class"])
        outer = rounded_rectangle_mask(
            image.size,
            frame["width_mm"],
            frame["height_mm"],
            frame["radius_mm"],
            pitch,
        )
        inner = rounded_rectangle_mask(
            image.size,
            frame["width_mm"] - 2 * frame["line_width_mm"],
            frame["height_mm"] - 2 * frame["line_width_mm"],
            max(0.5, frame["radius_mm"] - frame["line_width_mm"]),
            pitch,
        )
        ring = np.asarray(outer, dtype=bool) & ~np.asarray(inner, dtype=bool)
        arr = np.asarray(image, dtype=np.uint16).copy()
        arr[ring] = np.maximum(arr[ring], value)
        image.paste(Image.fromarray(arr, mode="I;16"))


def expand_bus_lane(lane: dict) -> list[tuple[float, float]]:
    side = float(lane["side"])
    y = float(lane["y_mm"])
    return [
        (side * float(lane["x_start_mm"]), y),
        (side * float(lane["x_elbow_mm"]), y),
        (side * float(lane["x_end_mm"]), y + float(lane["rise_mm"])),
    ]


def draw_ticks(
    draw: ImageDraw.ImageDraw,
    bank: dict,
    value: int,
    width_px: int,
    height_px: int,
    pitch: float,
) -> None:
    cx, cy = bank["center"]
    angle = math.radians(bank["angle_deg"])
    dx = math.cos(angle) * bank["length_mm"] / 2
    dy = math.sin(angle) * bank["length_mm"] / 2
    for i in range(bank["count"]):
        x = cx + (i - (bank["count"] - 1) / 2) * bank["spacing_mm"]
        draw_polyline_mm(
            draw,
            [(x - dx, cy - dy), (x + dx, cy + dy)],
            value,
            0.8,
            width_px,
            height_px,
            pitch,
        )


def draw_chevrons(
    draw: ImageDraw.ImageDraw,
    bank: dict,
    value: int,
    width_px: int,
    height_px: int,
    pitch: float,
) -> None:
    cx, cy = bank["center"]
    size = bank["size_mm"]
    direction = bank["direction"]
    for i in range(bank["count"]):
        x = cx + direction * i * size * 0.8
        points = [
            (x - direction * size / 2, cy - size / 2),
            (x + direction * size / 2, cy),
            (x - direction * size / 2, cy + size / 2),
        ]
        draw_polyline_mm(
            draw, points, value, 0.9, width_px, height_px, pitch
        )


def draw_text_marks(
    image: Image.Image,
    pattern: dict,
    pitch: float,
) -> None:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(FONT_PATH)
    draw = ImageDraw.Draw(image)
    width_px, height_px = image.size
    for mark in pattern["text_marks"]:
        font = ImageFont.truetype(str(FONT_PATH), mm_to_px(mark["font_size_mm"], pitch))
        center = xy_to_pixel(*mark["center"], width_px, height_px, pitch)
        draw.text(
            center,
            mark["text"],
            font=font,
            fill=level_for(pattern, mark["depth_class"]),
            anchor="mm",
            stroke_width=0,
        )


def decorative_cell_coverage(
    arr: np.ndarray,
    pattern: dict,
    pitch: float,
) -> dict:
    surface = pattern["surface"]
    grid_mm = float(surface["decorative_grid_mm"])
    cell_px = max(1, mm_to_px(grid_mm, pitch))
    margin_px = mm_to_px(surface["margin_mm"], pitch)
    active = arr > 0
    covered = 0
    total = 0
    for y0 in range(margin_px, arr.shape[0] - margin_px, cell_px):
        for x0 in range(margin_px, arr.shape[1] - margin_px, cell_px):
            cell = active[y0:min(y0 + cell_px, arr.shape[0] - margin_px), x0:min(x0 + cell_px, arr.shape[1] - margin_px)]
            if not cell.size:
                continue
            total += 1
            if np.any(cell):
                covered += 1
    return {
        "grid_mm": grid_mm,
        "covered_cells": covered,
        "total_cells": total,
        "fraction": covered / total if total else 0.0,
    }


def build_lid_heightmap(pattern: dict, pitch: float) -> tuple[np.ndarray, dict]:
    surface = pattern["surface"]
    width_mm = float(surface["width_mm"])
    height_mm = float(surface["height_mm"])
    width_px = mm_to_px(width_mm, pitch) + 1
    height_px = mm_to_px(height_mm, pitch) + 1
    image = Image.new("I;16", (width_px, height_px), 0)
    draw_perimeter_frames(image, pattern, pitch)
    draw = ImageDraw.Draw(image)

    for ring in pattern["reactor_rings"]:
        draw_hex_ring(
            draw,
            tuple(ring["center"]),
            ring["outer_radius_mm"],
            ring["inner_radius_mm"],
            ring["rotation_deg"],
            level_for(pattern, ring["depth_class"]),
            width_px,
            height_px,
            pitch,
        )

    for panel in pattern["panel_frames"]:
        draw_panel_frame(
            draw,
            panel,
            level_for(pattern, panel["depth_class"]),
            width_px,
            height_px,
            pitch,
        )

    for lane in pattern["bus_lanes"]:
        depth_class = lane["depth_class"]
        draw_polyline_mm(
            draw,
            expand_bus_lane(lane),
            level_for(pattern, depth_class),
            pattern["engraving"][f"{depth_class}_line_width_mm"],
            width_px,
            height_px,
            pitch,
        )

    for bus in pattern["vertical_buses"]:
        depth_class = bus["depth_class"]
        draw_polyline_mm(
            draw,
            [(bus["x_mm"], bus["y0_mm"]), (bus["x_mm"], bus["y1_mm"])],
            level_for(pattern, depth_class),
            pattern["engraving"][f"{depth_class}_line_width_mm"],
            width_px,
            height_px,
            pitch,
        )

    for field in pattern["microhex_fields"]:
        ox, oy = field["origin"]
        for row in range(field["rows"]):
            for column in range(field["columns"]):
                center = (
                    ox + column * field["pitch_x_mm"] + (row % 2) * field["pitch_x_mm"] / 2,
                    oy + row * field["pitch_y_mm"],
                )
                draw_hex_ring(
                    draw,
                    center,
                    pattern["microhex_outer_radius_mm"],
                    pattern["microhex_inner_radius_mm"],
                    30.0,
                    level_for(pattern, "secondary"),
                    width_px,
                    height_px,
                    pitch,
                )

    for node in pattern["node_rings"]:
        draw_hex_ring(
            draw,
            tuple(node["center"]),
            node["outer_radius_mm"],
            node["inner_radius_mm"],
            0.0,
            level_for(pattern, node["depth_class"]),
            width_px,
            height_px,
            pitch,
        )

    for bank in pattern["tick_banks"]:
        draw_ticks(
            draw, bank, level_for(pattern, "secondary"), width_px, height_px, pitch
        )
    for bank in pattern["chevron_banks"]:
        draw_chevrons(
            draw, bank, level_for(pattern, "major"), width_px, height_px, pitch
        )

    draw_text_marks(image, pattern, pitch)
    arr = np.asarray(image, dtype=np.uint16)
    coverage = decorative_cell_coverage(arr, pattern, pitch)
    report = {
        "type": "authored-two-level-cyber-line-art-heightmap",
        "operation": "engrave",
        "white_is_deepest": True,
        "physical_size_mm": [width_mm, height_mm],
        "pixel_size": [width_px, height_px],
        "actual_pitch_mm": [
            width_mm / (width_px - 1),
            height_mm / (height_px - 1),
        ],
        "source_geometry": "pattern_geometry.json",
        "major_depth_mm": pattern["engraving"]["major_depth_mm"],
        "secondary_depth_mm": pattern["engraving"]["secondary_depth_mm"],
        "minimum_feature_mm": min(
            pattern["engraving"]["major_line_width_mm"],
            pattern["engraving"]["secondary_line_width_mm"],
        ),
        "nonzero_fraction": float(np.count_nonzero(arr) / arr.size),
        "major_fraction": float(np.count_nonzero(arr == 65535) / arr.size),
        "secondary_fraction": float(np.count_nonzero((arr > 0) & (arr < 65535)) / arr.size),
        "decorative_cell_coverage": coverage,
        "exact_text": [mark["text"] for mark in pattern["text_marks"]],
    }
    return arr, report


def draw_side_capsule(
    draw: ImageDraw.ImageDraw,
    p0: tuple[float, float],
    p1: tuple[float, float],
    width_mm: float,
    value: int,
    width_px: int,
    height_px: int,
    tile_height_mm: float,
    pitch: float,
) -> None:
    def point(value_pair: tuple[float, float]) -> tuple[int, int]:
        x, z = value_pair
        return int(round(x / pitch)), z_to_row(z, tile_height_mm, pitch)

    draw.line(
        [point(p0), point(p1)],
        fill=value,
        width=mm_to_px(width_mm, pitch),
    )


def build_side_maps(pattern: dict, pitch: float) -> tuple[np.ndarray, np.ndarray, dict]:
    width_mm = 48.0
    height_mm = 12.0
    width_px = mm_to_px(width_mm, pitch)
    height_px = mm_to_px(height_mm, pitch) + 1
    engraving = Image.new("I;16", (width_px, height_px), 0)
    draw = ImageDraw.Draw(engraving)
    major = 65535
    secondary = int(round(65535 * 2 / 3))

    # Full-width rails are exactly periodic and carry the motif over every
    # rounded corner. Local nodes remain away from the tile boundary.
    for z_mm, value, line_mm in ((2.0, secondary, 0.8), (10.0, major, 0.8)):
        row = z_to_row(z_mm, height_mm, pitch)
        draw.line([(0, row), (width_px - 1, row)], fill=value, width=mm_to_px(line_mm, pitch))

    side_paths = [
        [(1.0, 4.0), (10.0, 4.0), (14.0, 6.0), (22.0, 6.0)],
        [(26.0, 6.0), (34.0, 6.0), (38.0, 8.0), (47.0, 8.0)],
        [(2.0, 8.0), (9.0, 8.0), (13.0, 6.0)],
        [(35.0, 6.0), (39.0, 4.0), (46.5, 4.0)],
    ]
    for index, path in enumerate(side_paths):
        for p0, p1 in zip(path, path[1:]):
            draw_side_capsule(
                draw,
                p0,
                p1,
                0.8 if index % 2 else 1.0,
                major if index % 2 == 0 else secondary,
                width_px,
                height_px,
                height_mm,
                pitch,
            )

    for x_mm, z_mm in ((7.5, 4.0), (22.0, 6.0), (34.0, 6.0), (41.0, 8.0)):
        cx = int(round(x_mm / pitch))
        cy = z_to_row(z_mm, height_mm, pitch)
        radius = mm_to_px(1.45, pitch)
        yy, xx = np.ogrid[:height_px, :width_px]
        outer = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
        inner = (xx - cx) ** 2 + (yy - cy) ** 2 < max(1, radius - mm_to_px(0.8, pitch)) ** 2
        arr = np.asarray(engraving, dtype=np.uint16).copy()
        arr[outer & ~inner] = major
        engraving = Image.fromarray(arr, mode="I;16")
        draw = ImageDraw.Draw(engraving)

    emboss = Image.new("I;16", (width_px, height_px), 0)
    emboss_draw = ImageDraw.Draw(emboss)
    row = z_to_row(6.0, height_mm, pitch)
    emboss_draw.line(
        [(0, row), (width_px - 1, row)],
        fill=65535,
        width=mm_to_px(1.12, pitch),
    )
    engraving_arr = np.asarray(engraving, dtype=np.uint16)
    emboss_arr = np.asarray(emboss, dtype=np.uint16)
    report = {
        "type": "periodic-two-level-side-tech-band",
        "operation": "engrave-plus-analytic-emboss",
        "white_is_deepest": True,
        "physical_tile_size_mm": [width_mm, height_mm],
        "pixel_size": [width_px, height_px],
        "repeat_axis": "perimeter-u",
        "seam": "exactly periodic full-width rails; seam placed at hinge side",
        "engraving_depth_mm": pattern["side_band"]["engraving_depth_mm"],
        "emboss_depth_mm": pattern["side_band"]["emboss_depth_mm"],
        "engraving_nonzero_fraction": float(np.count_nonzero(engraving_arr) / engraving_arr.size),
        "emboss_nonzero_fraction": float(np.count_nonzero(emboss_arr) / emboss_arr.size),
    }
    return engraving_arr, emboss_arr, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--pitch-mm", type=float, default=0.20)
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    relief_dir = project_dir / "relief"
    report_dir = project_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    pattern = json.loads(
        (relief_dir / "pattern_geometry.json").read_text(encoding="utf-8")
    )

    lid, lid_report = build_lid_heightmap(pattern, args.pitch_mm)
    side, side_emboss, side_report = build_side_maps(pattern, args.pitch_mm)
    Image.fromarray(lid, mode="I;16").save(relief_dir / "cyber_lid_heightmap_16bit.png")
    Image.fromarray(side, mode="I;16").save(relief_dir / "cyber_side_tile_16bit.png")
    Image.fromarray(side_emboss, mode="I;16").save(relief_dir / "cyber_side_emboss_mask_16bit.png")
    (report_dir / "cyber-heightmap-generation.json").write_text(
        json.dumps({"lid": lid_report, "side": side_report}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"lid": lid_report, "side": side_report}, indent=2))


if __name__ == "__main__":
    main()
