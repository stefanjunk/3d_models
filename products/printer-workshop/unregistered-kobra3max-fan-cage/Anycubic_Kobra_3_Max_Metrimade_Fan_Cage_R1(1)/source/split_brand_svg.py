#!/usr/bin/env python3
"""Create per-color SVGs for the optional OpenSCAD material-body workflow."""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "metrimade-lockup-horizontal-color.svg"
COLORS = {
    "navy": "#112431",
    "teal": "#08777D",
    "aqua": "#7FD5D3",
    "sand": "#C7AB82",
}
SVG_NS = "{http://www.w3.org/2000/svg}"


def main() -> None:
    source_root = ET.parse(SOURCE).getroot()
    for name, fill in COLORS.items():
        root = copy.deepcopy(source_root)
        for group in root.findall(f"{SVG_NS}g"):
            for path in list(group.findall(f"{SVG_NS}path")):
                if path.get("fill", "").upper() != fill.upper():
                    group.remove(path)
        output = ROOT / "assets" / f"metrimade-lockup-{name}.svg"
        ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
        print(output)

        mark_root = copy.deepcopy(source_root)
        mark_groups = mark_root.findall(f"{SVG_NS}g")
        for group_index, group in enumerate(mark_groups):
            for path in list(group.findall(f"{SVG_NS}path")):
                if group_index != 0 or path.get("fill", "").upper() != fill.upper():
                    group.remove(path)
        mark_output = ROOT / "assets" / f"metrimade-mark-{name}.svg"
        ET.ElementTree(mark_root).write(mark_output, encoding="utf-8", xml_declaration=True)
        print(mark_output)

    wordmark_root = copy.deepcopy(source_root)
    wordmark_groups = wordmark_root.findall(f"{SVG_NS}g")
    for group_index, group in enumerate(wordmark_groups):
        for path in list(group.findall(f"{SVG_NS}path")):
            if group_index != 1 or path.get("fill", "").upper() != COLORS["navy"]:
                group.remove(path)
    wordmark_output = ROOT / "assets" / "metrimade-wordmark-navy.svg"
    ET.ElementTree(wordmark_root).write(wordmark_output, encoding="utf-8", xml_declaration=True)
    print(wordmark_output)


if __name__ == "__main__":
    main()
