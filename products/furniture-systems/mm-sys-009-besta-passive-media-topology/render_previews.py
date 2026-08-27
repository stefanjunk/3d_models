#!/usr/bin/env python3
"""Render all generated STL files and build a labelled contact sheet."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
STL_DIR = ROOT / "exports" / "stl"
PREVIEW_DIR = ROOT / "previews"


def render_one(stl_path: Path, png_path: Path) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".scad",
        dir="/tmp/opencode",
        encoding="utf-8",
    ) as handle:
        escaped = str(stl_path.resolve()).replace("\\", "/").replace('"', '\\"')
        handle.write(f'color([0.16, 0.45, 0.72]) import("{escaped}");\n')
        handle.flush()
        subprocess.run(
            [
                "openscad",
                "-o",
                str(png_path),
                "--imgsize=720,540",
                "--projection=o",
                "--autocenter",
                "--viewall",
                "--colorscheme=Tomorrow",
                "--render=true",
                handle.name,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )


def contact_sheet(images: list[Path], output: Path) -> None:
    thumb_size = (360, 270)
    label_height = 34
    columns = 4
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_size[0], rows * (thumb_size[1] + label_height)), "#f4f5f7")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(images):
        image = Image.open(path).convert("RGB")
        image.thumbnail(thumb_size)
        cell_x = (index % columns) * thumb_size[0]
        cell_y = (index // columns) * (thumb_size[1] + label_height)
        x = cell_x + (thumb_size[0] - image.width) // 2
        y = cell_y + (thumb_size[1] - image.height) // 2
        sheet.paste(image, (x, y))
        draw.text((cell_x + 8, cell_y + thumb_size[1] + 8), path.stem, fill="#20242a")
    sheet.save(output)


def main() -> int:
    stl_files = sorted(STL_DIR.glob("*.stl"))
    if len(stl_files) != 20:
        raise SystemExit(f"Expected 20 STL files in {STL_DIR}, found {len(stl_files)}")
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    images: list[Path] = []
    for stl_path in stl_files:
        png_path = PREVIEW_DIR / f"{stl_path.stem}.png"
        print(f"rendering {stl_path.name}", flush=True)
        render_one(stl_path, png_path)
        images.append(png_path)
    contact_sheet(images, PREVIEW_DIR / "top20-contact-sheet.png")
    print(f"rendered {len(images)} previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
