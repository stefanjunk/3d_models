#!/usr/bin/env python3
"""Generate an exact SVG proof of the four engraved nameplates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
from gridfont import FONT_ID, pixel_rectangles  # noqa: E402


def sha256(target: Path) -> str:
    return hashlib.sha256(target.read_bytes()).hexdigest()


def record(target: Path) -> dict:
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256(target), "size_bytes": target.stat().st_size}


def check(check_id: str, passed: bool, message: str, metrics: dict | None = None) -> dict:
    return {"id": check_id, "status": "PASS" if passed else "FAIL", "required": True, "message": message, "metrics": metrics or {}, "evidence": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=ROOT / "config/model-parameters.json")
    parser.add_argument("--batch", type=Path, default=ROOT / "config/name-batch.json")
    parser.add_argument("--svg-out", type=Path, default=ROOT / "renders/MM-ORG-029-live-batch-preview.svg")
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/live-batch-preview.json")
    args = parser.parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    plate = parameters["nameplate"]
    scale = 3.0
    width = plate["width_mm"] * scale + 48
    card_h = plate["height_mm"] * scale
    height = 70 + len(batch["names"]) * (card_h + 18)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.3f} {height:.3f}">', f'<rect width="{width:.3f}" height="{height:.3f}" fill="#f3efe6"/>', '<text x="24" y="36" font-family="sans-serif" font-size="22" font-weight="700" fill="#183e49">CraftOrbit 4 exact name proof</text>']
    for index, item in enumerate(batch["names"]):
        ox, oy = 24.0, 58.0 + index * (card_h + 18.0)
        svg.append(f'<rect x="{ox:.3f}" y="{oy:.3f}" width="{plate["width_mm"] * scale:.3f}" height="{card_h:.3f}" rx="7" fill="#e2aa3f" stroke="#183e49" stroke-width="2"/>')
        for x, y, size in pixel_rectangles(item["normalized_name"], item["layout"], plate["width_mm"] / 2.0, plate["height_mm"] / 2.0):
            sx = ox + x * scale
            sy = oy + card_h - (y + size) * scale
            svg.append(f'<rect x="{sx:.3f}" y="{sy:.3f}" width="{size * scale:.3f}" height="{size * scale:.3f}" fill="#183e49"/>')
    svg.append("</svg>")
    output = "\n".join(svg) + "\n"
    args.svg_out.write_text(output, encoding="utf-8")
    names = [item["normalized_name"] for item in batch["names"]]
    minimum_pixel = min(item["layout"]["pixel_width_mm"] for item in batch["names"])
    checks = [check("font-identity", batch["font_id"] == FONT_ID, "Preview and CAD share the normalized glyph source"), check("batch-count", len(names) == 4, "Preview contains four names"), check("minimum-pixel", minimum_pixel >= plate["minimum_pixel_width_mm"], "All glyph pixels meet the printable minimum", {"minimum_mm": minimum_pixel})]
    report = {"schema_version": "1.0", "tool": "MM-ORG-029-live-batch-preview", "tool_version": parameters["project"]["revision"], "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "profile": "draft", "inputs": [record(args.parameters), record(args.batch), record(ROOT / "cad/gridfont.py")], "checks": checks, "metrics": {"font_id": FONT_ID, "names": names, "minimum_pixel_width_mm": minimum_pixel, "svg_sha256": hashlib.sha256(output.encode()).hexdigest()}, "limitations": ["The proof confirms source identity and layout, not printed contrast or customer acceptance."], "required_capabilities": []}
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "names": names, "svg": str(args.svg_out)}, indent=2))


if __name__ == "__main__":
    main()
