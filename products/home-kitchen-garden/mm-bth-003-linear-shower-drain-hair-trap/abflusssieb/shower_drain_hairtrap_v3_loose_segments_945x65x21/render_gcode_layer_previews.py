#!/usr/bin/env python3
"""Render selected Anycubic G-code layers without executing the G-code."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
GCODE = ROOT / "build" / "slice-anycubic-next-double-3.1.0-draft.1-r1" / "plate_1.gcode"
OUTPUT_DIR = ROOT / "validation" / "previews"
TARGETS = {
    0.24: OUTPUT_DIR / "DRAFT-MM-BTH-003-3.1.0-draft.1-anycubic-first-layer.png",
    52.44: OUTPUT_DIR / "DRAFT-MM-BTH-003-3.1.0-draft.1-anycubic-watermark-mid-layer.png",
}
WORD = re.compile(r"([A-Z])(-?(?:\d+(?:\.\d*)?|\.\d+))")


def layer_segments() -> dict[float, list[tuple[float, float, float, float]]]:
    result: dict[float, list[tuple[float, float, float, float]]] = {value: [] for value in TARGETS}
    x = y = z = e_absolute = 0.0
    relative_extrusion = True
    active_target: float | None = None
    pending_layer = False
    for raw in GCODE.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split(";", 1)[0].strip()
        if raw.startswith(";LAYER_CHANGE"):
            pending_layer = True
            active_target = None
            continue
        if pending_layer and raw.startswith(";Z:"):
            z = float(raw[3:])
            active_target = next((target for target in TARGETS if abs(target - z) < 1e-6), None)
            pending_layer = False
            continue
        if line == "M82":
            relative_extrusion = False
            continue
        if line == "M83":
            relative_extrusion = True
            continue
        if line.startswith("G92"):
            words = {key: float(value) for key, value in WORD.findall(line)}
            if "E" in words:
                e_absolute = words["E"]
            continue
        if not (line.startswith("G0 ") or line.startswith("G1 ")):
            continue
        words = {key: float(value) for key, value in WORD.findall(line)}
        new_x, new_y = words.get("X", x), words.get("Y", y)
        extrusion = 0.0
        if "E" in words:
            if relative_extrusion:
                extrusion = words["E"]
            else:
                extrusion = words["E"] - e_absolute
                e_absolute = words["E"]
        if active_target is not None and extrusion > 0 and (new_x != x or new_y != y):
            result[active_target].append((x, y, new_x, new_y))
        x, y = new_x, new_y
        z = words.get("Z", z)
    return result


def render(target_z: float, segments: list[tuple[float, float, float, float]], output: Path) -> None:
    assert segments, f"no extrusion segments at Z={target_z}"
    xs = [value for segment in segments for value in (segment[0], segment[2])]
    ys = [value for segment in segments for value in (segment[1], segment[3])]
    fig, axis = plt.subplots(figsize=(9, 5.5), dpi=200)
    for x0, y0, x1, y1 in segments:
        axis.plot((x0, x1), (y0, y1), color="#176B87", linewidth=0.55)
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlim(min(xs) - 3, max(xs) + 3)
    axis.set_ylim(min(ys) - 3, max(ys) + 3)
    axis.set_title(f"MM-BTH-003 · Anycubic Slicer Next · extrusion paths at Z={target_z:.2f} mm")
    axis.set_xlabel("machine X (mm)")
    axis.set_ylabel("machine Y (mm)")
    axis.grid(True, linewidth=0.25, alpha=0.35)
    axis.text(0.01, 0.01, f"Source: exact retained plate_1.gcode · {len(segments)} positive-extrusion moves", transform=axis.transAxes, fontsize=7)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, facecolor="white")
    plt.close(fig)


def main() -> None:
    grouped = layer_segments()
    for target, output in TARGETS.items():
        render(target, grouped[target], output)


if __name__ == "__main__":
    main()
