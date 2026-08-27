#!/usr/bin/env python3
"""Compose the revision 3.0.0 concept sheet from a style render and exact schematics.

This is presentation-only artwork. It does not generate production geometry.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
STYLE_RENDER = ROOT / "zen_kintsugi_wave_fifo_r3.0.0_concept-v2.png"
OUTPUT = ROOT / "zen_kintsugi_wave_fifo_r3.0.0_concept.png"

CANVAS = (1800, 1200)
BG = "#eee9df"
PANEL = "#f8f5ef"
INK = "#302c27"
MUTED = "#746b60"
IVORY = "#e6ddcd"
IVORY_LIGHT = "#f5f0e7"
IVORY_DARK = "#a79c8b"
GOLD = "#bc8a22"
SHAFT = "#625a50"
ARROW = "#956f27"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    paths = [
        Path("/usr/share/fonts/truetype/dejavu") / name,
        Path("/usr/share/fonts") / name,
    ]
    for path in paths:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


TITLE = font(34, True)
SUBTITLE = font(20)
HEADING = font(22, True)
LABEL = font(18)
SMALL = font(15)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=20, fill=PANEL, outline="#d5cec2", width=2)


def roll(draw: ImageDraw.ImageDraw, center: tuple[int, int], size: tuple[int, int]) -> None:
    cx, cy = center
    width, height = size
    box = (cx - width // 2, cy - height // 2, cx + width // 2, cy + height // 2)
    draw.rounded_rectangle(box, radius=height // 2, fill=IVORY_LIGHT, outline=IVORY_DARK, width=2)
    draw.arc((box[0] + 8, box[1] + 8, box[2] - 8, box[3] - 8), 205, 515, fill="#d6ccbb", width=2)
    hole_w = max(16, height // 4)
    draw.ellipse(
        (box[2] - hole_w - 10, cy - hole_w // 2, box[2] - 10, cy + hole_w // 2),
        fill=SHAFT,
    )


def arrow(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]]) -> None:
    draw.line(points, fill=ARROW, width=5, joint="curve")
    x0, y0 = points[-2]
    x1, y1 = points[-1]
    if abs(x1 - x0) > abs(y1 - y0):
        sign = 1 if x1 > x0 else -1
        tip = [(x1, y1), (x1 - sign * 18, y1 - 10), (x1 - sign * 18, y1 + 10)]
    else:
        sign = 1 if y1 > y0 else -1
        tip = [(x1, y1), (x1 - 10, y1 - sign * 18), (x1 + 10, y1 - sign * 18)]
    draw.polygon(tip, fill=ARROW)


def draw_fifo_section(draw: ImageDraw.ImageDraw, origin: tuple[int, int]) -> None:
    ox, oy = origin
    body = (ox + 95, oy + 55, ox + 375, oy + 855)
    draw.rounded_rectangle(body, radius=28, fill=IVORY, outline=IVORY_DARK, width=3)
    draw.rounded_rectangle((ox + 130, oy + 85, ox + 340, oy + 785), radius=18, fill="#7b7369")
    # Exactly two structural seams: after one roll, then after the next two rolls.
    seam_1 = oy + 275
    seam_2 = oy + 555
    for seam in (seam_1, seam_2):
        draw.line((body[0] + 4, seam, body[2] - 4, seam), fill="#857968", width=4)
        draw.line((body[0] + 12, seam + 4, body[2] - 12, seam + 4), fill=GOLD, width=2)
    for cy in (oy + 205, oy + 345, oy + 485, oy + 625, oy + 765):
        roll(draw, (ox + 235, cy), (180, 96))
    # Unobstructed loading mouth and lower output bay.
    draw.rounded_rectangle((ox + 145, oy + 60, ox + 325, oy + 130), radius=24, fill=BG)
    draw.rounded_rectangle((ox + 140, oy + 790, ox + 330, oy + 850), radius=24, fill=BG)
    arrow(draw, [(ox + 235, oy + 5), (ox + 235, oy + 95)])
    arrow(draw, [(ox + 210, oy + 825), (ox + 45, oy + 825)])
    draw.text((ox + 15, oy + 22), "TOP LOAD", font=SMALL, fill=MUTED)
    draw.text((ox + 5, oy + 850), "ONE-ROLL OUTPUT", font=SMALL, fill=MUTED)
    draw.text((ox + 390, oy + 145), "TOP · 1 roll", font=SMALL, fill=MUTED)
    draw.text((ox + 390, oy + 375), "MIDDLE · 2 rolls", font=SMALL, fill=MUTED)
    draw.text((ox + 390, oy + 655), "BOTTOM · 2 rolls + output", font=SMALL, fill=MUTED)


def draw_module(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], rolls: int, output: bool) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=18, fill=IVORY, outline=IVORY_DARK, width=3)
    inner = (x0 + 22, y0 + 18, x1 - 22, y1 - (60 if output else 18))
    draw.rounded_rectangle(inner, radius=15, fill="#7b7369")
    available = inner[3] - inner[1]
    step = available / rolls
    for index in range(rolls):
        cy = int(inner[1] + step * (index + 0.5))
        roll(draw, ((x0 + x1) // 2, cy), (125, min(72, int(step * 0.72))))
    if output:
        draw.rounded_rectangle((x0 + 30, y1 - 68, x1 - 30, y1 - 10), radius=18, fill=BG)


def draw_exploded_modules(draw: ImageDraw.ImageDraw, origin: tuple[int, int]) -> None:
    ox, oy = origin
    top = (ox, oy, ox + 205, oy + 145)
    middle = (ox, oy + 175, ox + 205, oy + 405)
    bottom = (ox, oy + 435, ox + 205, oy + 745)
    draw_module(draw, top, 1, False)
    draw_module(draw, middle, 2, False)
    draw_module(draw, bottom, 2, True)
    # One flat procedural skin and gold path per structural module.
    for index, module in enumerate((top, middle, bottom)):
        _, y0, _, y1 = module
        skin = (ox + 260, y0, ox + 350, y1)
        draw.rounded_rectangle(skin, radius=10, fill=IVORY_LIGHT, outline=IVORY_DARK, width=2)
        for offset in (22, 38, 54):
            draw.arc((skin[0] - 30, y0 + offset, skin[2] + 20, y1 + 40), 190, 305, fill="#b6aa98", width=3)
        path = [
            (skin[0] + 25, y0 + 15),
            (skin[0] + 45, y0 + (y1 - y0) // 3),
            (skin[0] + 30, y0 + 2 * (y1 - y0) // 3),
            (skin[0] + 62, y1 - 12),
        ]
        draw.line(path, fill=GOLD, width=5, joint="curve")
        draw.ellipse((path[1][0] - 3, path[1][1] - 3, path[1][0] + 3, path[1][1] + 3), fill=GOLD)
        draw.text((skin[0], y1 + 4), f"skin {index + 1}", font=SMALL, fill=MUTED)


def draw_rear_mount(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    back = (x0 + 45, y0 + 45, x1 - 45, y1 - 35)
    draw.rounded_rectangle(back, radius=20, fill=IVORY, outline=IVORY_DARK, width=3)
    draw.rounded_rectangle((back[0] + 35, back[1] + 20, back[2] - 35, back[3] - 20), radius=12, outline="#8f8578", width=5)
    holes = [
        (back[0] + 60, back[1] + 65),
        (back[2] - 60, back[1] + 65),
        (back[0] + 60, back[3] - 65),
        (back[2] - 60, back[3] - 65),
    ]
    for x, y in holes:
        draw.ellipse((x - 13, y - 13, x + 13, y + 13), fill="#847765", outline=GOLD, width=3)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="#3f3931")
    draw.text((x0 + 18, y1 - 28), "4 substrate-specific mounting zones", font=SMALL, fill=MUTED)


def draw_accessory(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    tray = (x0 + 35, y0 + 78, x1 - 35, y1 - 50)
    draw.rounded_rectangle(tray, radius=35, fill=IVORY, outline=IVORY_DARK, width=3)
    draw.rounded_rectangle((tray[0] + 18, tray[1] + 15, tray[2] - 18, tray[3] - 18), radius=25, fill="#ddd1be")
    draw.ellipse((tray[0] + 70, tray[1] + 20, tray[2] - 55, tray[3] - 12), fill="#c5b596", outline="#9d8d74", width=2)
    draw.polygon(
        [(tray[0] + 18, tray[3]), (tray[0] + 55, tray[3]), (tray[0] + 45, tray[3] + 22), (tray[0] + 28, tray[3] + 22)],
        fill=IVORY_DARK,
    )
    draw.text((x0 + 28, y1 - 32), "removable · dry scent stone only", font=SMALL, fill=MUTED)


def main() -> None:
    canvas = Image.new("RGB", CANVAS, BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((45, 28), "ZEN KINTSUGI WAVE FIFO · CONCEPT R3.0.0", font=TITLE, fill=INK)
    draw.text((48, 72), "three-module parametric redesign · five-roll gravity FIFO · no image-to-3D production geometry", font=SUBTITLE, fill=MUTED)

    overview_box = (35, 115, 855, 1160)
    panel(draw, overview_box)
    draw.text((60, 135), "OVERVIEW", font=HEADING, fill=INK)
    style = Image.open(STYLE_RENDER).convert("RGB")
    # The left area of the generated style sheet contains the consistent five-roll overview.
    crop = style.crop((0, 0, 470, 1080))
    fitted = ImageOps.contain(crop, (775, 960), method=Image.Resampling.LANCZOS)
    mask = Image.new("L", fitted.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, fitted.width, fitted.height), radius=16, fill=255)
    paste_x = 58 + (775 - fitted.width) // 2
    paste_y = 178 + (960 - fitted.height) // 2
    canvas.paste(fitted, (paste_x, paste_y), mask)

    section_box = (880, 115, 1765, 650)
    panel(draw, section_box)
    draw.text((905, 135), "FIFO SECTION · DIAGRAMMATIC", font=HEADING, fill=INK)
    section_layer = Image.new("RGBA", (850, 900), (0, 0, 0, 0))
    section_draw = ImageDraw.Draw(section_layer)
    draw_fifo_section(section_draw, (20, 0))
    section_layer = section_layer.resize((520, 500), Image.Resampling.LANCZOS)
    canvas.paste(section_layer, (900, 165), section_layer)
    draw_rear_mount(draw, (1430, 180, 1740, 620))
    draw.text((1490, 145), "REAR MOUNT", font=LABEL, fill=INK)

    modules_box = (880, 675, 1395, 1160)
    panel(draw, modules_box)
    draw.text((905, 695), "THREE STRUCTURAL MODULES", font=HEADING, fill=INK)
    module_layer = Image.new("RGBA", (420, 780), (0, 0, 0, 0))
    module_draw = ImageDraw.Draw(module_layer)
    draw_exploded_modules(module_draw, (20, 0))
    module_layer = module_layer.resize((400, 430), Image.Resampling.LANCZOS)
    canvas.paste(module_layer, (935, 730), module_layer)

    accessory_box = (1420, 675, 1765, 1160)
    panel(draw, accessory_box)
    draw.text((1445, 695), "OPTIONAL ACCESSORY", font=HEADING, fill=INK)
    draw_accessory(draw, (1435, 735, 1750, 1115))

    canvas.save(OUTPUT, quality=95)


if __name__ == "__main__":
    main()
