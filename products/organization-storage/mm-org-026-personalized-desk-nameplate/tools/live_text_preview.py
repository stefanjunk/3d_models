#!/usr/bin/env python3
"""Generate a browser-safe SVG proof from the exact CAD glyph source."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
from gridfont import FONT_ID, layout, normalize_text, pixel_rectangles  # noqa: E402


def file_record(path: Path) -> dict:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size_bytes": path.stat().st_size,
    }


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {
        "id": check_id,
        "status": "PASS" if passed else "FAIL",
        "required": True,
        "message": message,
        "metrics": metrics or {},
        "evidence": [],
    }


def svg_preview(parameters: dict, name_value: str, title_value: str) -> tuple[str, dict]:
    plate = parameters["plate"]
    personal = parameters["personalization"]
    name = normalize_text(name_value, personal["allowed_characters"], personal["name_maximum_characters_after_transliteration"])
    title = normalize_text(title_value, personal["allowed_characters"], personal["title_maximum_characters_after_transliteration"])
    available = plate["width_mm"] - 2.0 * plate["text_margin_x_mm"]
    name_layout = layout(name, available, plate["name_height_mm"], plate["maximum_pixel_pitch_mm"], plate["minimum_pixel_width_mm"])
    title_layout = layout(title, available, plate["title_height_mm"], plate["maximum_pixel_pitch_mm"], plate["minimum_pixel_width_mm"])
    scale = 4.0
    width = plate["width_mm"] * scale
    height = plate["height_mm"] * scale
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="{-plate["width_mm"]/2:.3f} {-plate["height_mm"]/2:.3f} {plate["width_mm"]:.3f} {plate["height_mm"]:.3f}">', f'<rect x="{-plate["width_mm"]/2:.3f}" y="{-plate["height_mm"]/2:.3f}" width="{plate["width_mm"]:.3f}" height="{plate["height_mm"]:.3f}" rx="{plate["corner_radius_mm"]:.3f}" fill="#254e5a"/>']
    for text, data, center_y in ((name, name_layout, plate["name_center_y_mm"]), (title, title_layout, plate["title_center_y_mm"])):
        for x, y, size in pixel_rectangles(text, data, 0.0, center_y):
            elements.append(f'<rect x="{x:.4f}" y="{-y-size:.4f}" width="{size:.4f}" height="{size:.4f}" fill="#f2c14e"/>')
    elements.append(f'<rect x="{-plate["width_mm"]/2+plate["border_inset_mm"]:.3f}" y="{-plate["height_mm"]/2+plate["border_inset_mm"]:.3f}" width="{plate["width_mm"]-2*plate["border_inset_mm"]:.3f}" height="{plate["height_mm"]-2*plate["border_inset_mm"]:.3f}" rx="2" fill="none" stroke="#f2c14e" stroke-width="{plate["border_width_mm"]:.3f}"/>')
    elements.append('</svg>')
    svg = "\n".join(elements) + "\n"
    minimum_pixel = plate["minimum_pixel_width_mm"]
    checks = [
        check("font-identity", FONT_ID == parameters["personalization"]["font_id"], "Preview uses the configured repository-owned glyph source"),
        check("name-present", bool(name), "Normalized name is non-empty"),
        check("title-present", bool(title), "Normalized title is non-empty"),
        check("name-pixel-width", name_layout["pixel_width_mm"] >= minimum_pixel, "Name pixels meet the printable minimum", {"pixel_width_mm": name_layout["pixel_width_mm"]}),
        check("title-pixel-width", title_layout["pixel_width_mm"] >= minimum_pixel, "Title pixels meet the printable minimum", {"pixel_width_mm": title_layout["pixel_width_mm"]}),
    ]
    proof = {
        "schema_version": "1.0",
        "tool": "MM-ORG-026-live-text-preview",
        "tool_version": "0.1.0-draft.1",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "draft",
        "inputs": [file_record(ROOT / "config/model-parameters.json"), file_record(ROOT / "cad/gridfont.py")],
        "checks": checks,
        "metrics": {
            "font_id": FONT_ID,
            "normalized_name": name,
            "normalized_title": title,
            "name_layout": name_layout,
            "title_layout": title_layout,
            "svg_sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
            "privacy": parameters["workflow_contract"]["privacy"],
        },
        "limitations": [
            "The SVG is an exact digital text proof, not evidence of engraved contrast after printing.",
            "Customer-specific names must not be retained outside the order and proof records.",
        ],
        "required_capabilities": [],
        # Stable convenience fields consumed by the CAD generator and tests.
        "font_id": FONT_ID,
        "normalized_name": name,
        "normalized_title": title,
        "name_layout": name_layout,
        "title_layout": title_layout,
        "svg_sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
        "privacy": parameters["workflow_contract"]["privacy"],
    }
    return svg, proof


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=ROOT / "config/model-parameters.json")
    parser.add_argument("--name")
    parser.add_argument("--title")
    parser.add_argument("--svg-out", type=Path, default=ROOT / "renders/MM-ORG-026-live-text-preview.svg")
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/live-text-preview.json")
    args = parser.parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    name = args.name if args.name is not None else parameters["personalization"]["name"]
    title = args.title if args.title is not None else parameters["personalization"]["title"]
    svg, proof = svg_preview(parameters, name, title)
    args.svg_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.svg_out.write_text(svg, encoding="utf-8")
    args.json_out.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metrics = proof["metrics"]
    print(json.dumps({"status": proof["status"], "svg": str(args.svg_out), "proof": str(args.json_out), "normalized_name": metrics["normalized_name"], "normalized_title": metrics["normalized_title"], "font_id": metrics["font_id"]}, indent=2))


if __name__ == "__main__":
    main()
