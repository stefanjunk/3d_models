#!/usr/bin/env python3
"""Generate an exact SVG proof for every normalized CSV label cap."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
from gridfont import FONT_ID, pixel_rectangles  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def build_svg(parameters: dict, batch: dict) -> str:
    cap = parameters["label_cap"]
    scale = 3.2
    card_w = cap["width_mm"] * scale
    card_h = cap["height_mm"] * scale
    gutter = 28.0
    width = 3 * card_w + 4 * gutter
    height = 2 * card_h + 3 * gutter + 65.0
    rows = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.3f} {height:.3f}">', f'<rect width="{width:.3f}" height="{height:.3f}" fill="#f2eee5"/>', '<text x="28" y="40" font-family="sans-serif" font-size="24" font-weight="700" fill="#173e48">ShelfCue exact label proof</text>']
    for index, item in enumerate(batch["labels"]):
        column, row = index % 3, index // 3
        ox = gutter + column * (card_w + gutter)
        oy = 65.0 + gutter + row * (card_h + gutter)
        rows.append(f'<rect x="{ox:.3f}" y="{oy:.3f}" width="{card_w:.3f}" height="{card_h:.3f}" rx="10" fill="#e0a83d" stroke="#173e48" stroke-width="3"/>')
        text_center_y = -cap["height_mm"] / 2.0 + cap["text_center_y_mm"]
        for x, y, size in pixel_rectangles(item["normalized_label"], item["layout"], 0.0, text_center_y):
            sx = ox + (x + cap["width_mm"] / 2.0) * scale
            sy = oy + (cap["height_mm"] - (y + cap["height_mm"] / 2.0) - size) * scale
            rows.append(f'<rect x="{sx:.3f}" y="{sy:.3f}" width="{size * scale:.3f}" height="{size * scale:.3f}" fill="#173e48"/>')
        slot_x = ox + (item["slot_center_x_mm"] + cap["width_mm"] / 2.0 - cap["nominal_slot_width_mm"] / 2.0) * scale
        rows.append(f'<rect x="{slot_x:.3f}" y="{oy + (cap["height_mm"] - cap["slot_insertion_depth_mm"]) * scale:.3f}" width="{cap["nominal_slot_width_mm"] * scale:.3f}" height="{cap["slot_insertion_depth_mm"] * scale:.3f}" fill="#f2eee5"/>')
        rows.append(f'<text x="{ox:.3f}" y="{oy + card_h + 19:.3f}" font-family="sans-serif" font-size="13" fill="#48636a">{item["tab_position"]} · pixel {item["layout"]["pixel_width_mm"]:.2f} mm</text>')
    rows.append('</svg>')
    return "\n".join(rows) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=ROOT / "config/model-parameters.json")
    parser.add_argument("--batch", type=Path, default=ROOT / "config/label-batch.json")
    parser.add_argument("--svg-out", type=Path, default=ROOT / "renders/MM-ORG-027-live-batch-preview.svg")
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/live-batch-preview.json")
    args = parser.parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    svg = build_svg(parameters, batch)
    args.svg_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.svg_out.write_text(svg, encoding="utf-8")
    labels = [item["normalized_label"] for item in batch["labels"]]
    minimum_pixel = min(item["layout"]["pixel_width_mm"] for item in batch["labels"])
    checks = [
        check("font-identity", batch["font_id"] == FONT_ID, "Preview uses the normalized batch glyph source"),
        check("batch-count", len(labels) == parameters["batch"]["maximum_labels"], "Preview contains the complete default batch"),
        check("label-identity", len(set(labels)) == len(labels), "Preview labels are unique"),
        check("minimum-pixel", minimum_pixel >= parameters["label_cap"]["minimum_pixel_width_mm"], "Every preview label meets the printable pixel minimum", {"minimum_mm": minimum_pixel}),
    ]
    proof = {"schema_version": "1.0", "tool": "MM-ORG-027-live-batch-preview", "tool_version": parameters["project"]["revision"], "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [record(args.parameters), record(args.batch), record(ROOT / "cad/gridfont.py")], "checks": checks, "metrics": {"font_id": FONT_ID, "labels": labels, "tab_positions": [item["tab_position"] for item in batch["labels"]], "minimum_pixel_width_mm": minimum_pixel, "svg_sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest()}, "limitations": ["The SVG proves source identity and layout, not printed contrast or customer acceptance."], "required_capabilities": []}
    args.json_out.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": proof["status"], "labels": labels, "svg": str(args.svg_out), "report": str(args.json_out)}, indent=2))


if __name__ == "__main__":
    main()
