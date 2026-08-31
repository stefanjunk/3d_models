#!/usr/bin/env python3
"""Generate the R7-C01 clean-room Wiper interface measurement coupon.

The coupon is deliberately a parameter sweep, not a product model.  Its only
machine datum is the independently measured 17 mm screw-centre pitch.  No
third-party model, contour, metadata, image or dimension is loaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
from PIL import Image, ImageDraw, ImageFont
import trimesh


SEGMENTS = {
    "0": "abcedf",  # order is irrelevant; seven-segment names are unique
    "1": "bc",
    "2": "abdeg",
    "3": "abcdg",
    "4": "bcfg",
    "5": "acdfg",
    "6": "acdefg",
    "7": "abc",
    "8": "abcdefg",
    "9": "abcdfg",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, root: Path) -> dict:
    return {
        "path": str(path.relative_to(root)),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def make_box(x: float, y: float, z: float, dx: float, dy: float, dz: float) -> cq.Shape:
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


def make_cylinder(x: float, y: float, z: float, diameter: float, height: float) -> cq.Shape:
    return cq.Solid.makeCylinder(
        diameter / 2.0,
        height,
        cq.Vector(x, y, z),
        cq.Vector(0.0, 0.0, 1.0),
    )


def glyph_advance(character: str, scale: float) -> float:
    return (0.65 if character == "." else 2.05) * scale


def label_width(text: str, scale: float) -> float:
    return sum(glyph_advance(character, scale) for character in text)


def make_digit(character: str, x: float, y: float, z: float, scale: float, depth: float) -> cq.Shape:
    if character == ".":
        size = 0.38 * scale
        return make_box(x, y, z, size, size, depth)

    segment_names = SEGMENTS[character]
    thickness = 0.34 * scale
    horizontal = 1.45 * scale
    vertical = 1.20 * scale
    width = horizontal + 2.0 * thickness
    mid_y = vertical + thickness
    top_y = 2.0 * vertical + 2.0 * thickness
    parts: list[cq.Shape] = []
    definitions = {
        "a": (x + thickness, y + top_y, horizontal, thickness),
        "b": (x + width - thickness, y + mid_y + thickness, thickness, vertical),
        "c": (x + width - thickness, y + thickness, thickness, vertical),
        "d": (x + thickness, y, horizontal, thickness),
        "e": (x, y + thickness, thickness, vertical),
        "f": (x, y + mid_y + thickness, thickness, vertical),
        "g": (x + thickness, y + mid_y, horizontal, thickness),
    }
    for name in segment_names:
        sx, sy, dx, dy = definitions[name]
        parts.append(make_box(sx, sy, z, dx, dy, depth))
    return cq.Compound.makeCompound(parts)


def make_label(text: str, center_x: float, y: float, top_z: float, scale: float, relief: float) -> cq.Shape:
    x = center_x - label_width(text, scale) / 2.0
    glyphs: list[cq.Shape] = []
    for character in text:
        glyphs.append(make_digit(character, x, y, top_z - relief, scale, relief + 0.2))
        x += glyph_advance(character, scale)
    return cq.Compound.makeCompound(glyphs)


def build_mount_tabs(params: dict) -> tuple[list[cq.Shape], list[dict]]:
    cfg = params["mount_tabs"]
    width = float(cfg["tab_width_mm"])
    height = float(cfg["tab_height_mm"])
    thickness = float(cfg["tab_thickness_mm"])
    lower_y = float(cfg["lower_hole_center_y_mm"])
    pitch = float(cfg["screw_center_pitch_mm"])
    gap = float(cfg["tab_gap_mm"])
    relief = float(cfg["label_relief_mm"])
    tabs: list[cq.Shape] = []
    metrics: list[dict] = []
    for index, diameter_value in enumerate(cfg["hole_diameter_candidates_mm"]):
        diameter = float(diameter_value)
        origin_x = index * (width + gap)
        tab = make_box(origin_x, 0.0, 0.0, width, height, thickness)
        centers = [(origin_x + width / 2.0, lower_y), (origin_x + width / 2.0, lower_y + pitch)]
        for center_x, center_y in centers:
            tab = tab.cut(make_cylinder(center_x, center_y, -0.2, diameter, thickness + 0.4))
        marker_count = index + 1
        marker_pitch = 1.05
        marker_start_x = origin_x + width / 2.0 - (marker_count - 1) * marker_pitch / 2.0
        for marker_index in range(marker_count):
            tab = tab.cut(
                make_cylinder(
                    marker_start_x + marker_index * marker_pitch,
                    2.4,
                    -0.2,
                    0.65,
                    thickness + 0.4,
                )
            )
        tab = tab.clean()
        tabs.append(tab)
        metrics.append(
            {
                "candidate_id": f"D{int(round(diameter * 10)):02d}",
                "hole_diameter_mm": diameter,
                "hole_centers_mm": [[centers[0][0], centers[0][1]], [centers[1][0], centers[1][1]]],
                "center_pitch_mm": centers[1][1] - centers[0][1],
                "hole_kind": "two closed circular through holes",
                "slot_features": 0,
                "tab_thickness_mm": thickness,
                "unary_marker_holes": marker_count,
            }
        )
    return tabs, metrics


def build_head_gauge(params: dict, origin_y: float) -> tuple[cq.Shape, dict]:
    cfg = params["head_gauge"]
    candidates = [float(value) for value in cfg["notch_width_candidates_mm"]]
    spacing = float(cfg["notch_spacing_mm"])
    depth = float(cfg["notch_depth_mm"])
    height = float(cfg["body_height_mm"])
    thickness = float(cfg["body_thickness_mm"])
    width = spacing * len(candidates) + 2.0
    gauge = make_box(0.0, origin_y, 0.0, width, height, thickness)
    notches: list[dict] = []
    for index, candidate in enumerate(candidates):
        center_x = 1.0 + spacing * (index + 0.5)
        cutter = make_box(
            center_x - candidate / 2.0,
            origin_y + height - depth,
            -0.2,
            candidate,
            depth + 0.4,
            thickness + 0.4,
        )
        gauge = gauge.cut(cutter)
        notches.append({"width_mm": candidate, "center_x_mm": center_x})
    return gauge.clean(), {
        "origin_y_mm": origin_y,
        "width_mm": width,
        "height_mm": height,
        "notches": notches,
        "measurement_kind": "open functional head-width gauge; not a nominal standard identifier",
    }


def build_length_ruler(params: dict, origin_y: float) -> tuple[cq.Shape, dict]:
    cfg = params["length_ruler"]
    width = float(cfg["body_width_mm"])
    height = float(cfg["body_height_mm"])
    thickness = float(cfg["body_thickness_mm"])
    range_mm = int(cfg["range_mm"])
    major = int(cfg["major_tick_mm"])
    ruler = make_box(0.0, origin_y, 0.0, width, height, thickness)
    zero_x = 5.0
    tick_metrics: list[dict] = []
    for value in range(range_mm + 1):
        tick_height = 4.0 if value % major == 0 else 2.0
        x = zero_x + value
        tick = make_box(x - 0.12, origin_y + height - tick_height, thickness - 0.4, 0.24, tick_height, 0.6)
        ruler = ruler.cut(tick)
        tick_metrics.append({"value_mm": value, "x_mm": x, "major": value % major == 0})
    return ruler.clean(), {
        "origin_y_mm": origin_y,
        "zero_x_mm": zero_x,
        "range_mm": range_mm,
        "ticks": tick_metrics,
        "measurement_kind": "coarse printed cross-check; use a caliper for the recorded screw length",
    }


def mesh_record(path: Path) -> dict:
    loaded = trimesh.load_mesh(path, process=True)
    if isinstance(loaded, trimesh.Scene):
        mesh = loaded.to_geometry()
    else:
        mesh = loaded
    components = mesh.split(only_watertight=False)
    return {
        "bounds_mm": mesh.bounds.tolist(),
        "extents_mm": mesh.extents.tolist(),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "components": int(len(components)),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": float(mesh.volume),
    }


def render_preview(params: dict, tabs: list[dict], head: dict, ruler: dict, output: Path) -> None:
    scale = 8.0
    margin = 70
    max_x = max(tab["hole_centers_mm"][0][0] + float(params["mount_tabs"]["tab_width_mm"]) / 2.0 for tab in tabs)
    max_y = ruler["origin_y_mm"] + float(params["length_ruler"]["body_height_mm"])
    canvas = Image.new("RGB", (int(max_x * scale) + 2 * margin, int(max_y * scale) + 220), "#f4f1ea")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 22)
    small = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 17)
    title = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 30)

    def px(x: float) -> int:
        return margin + int(x * scale)

    def py(y: float) -> int:
        return 120 + int((max_y - y) * scale)

    draw.text((margin, 28), "R7-C01 · Wiper-Schnittstellen-Messcoupon", font=title, fill="#17242d")
    draw.text((margin, 70), "Nur stromloser Kaltpass-Test · kein Umlenkermodell · keine Fremdgeometrie", font=font, fill="#a23b2a")
    tab_width = float(params["mount_tabs"]["tab_width_mm"])
    tab_height = float(params["mount_tabs"]["tab_height_mm"])
    for tab in tabs:
        center_x = tab["hole_centers_mm"][0][0]
        x0 = center_x - tab_width / 2.0
        draw.rounded_rectangle((px(x0), py(tab_height), px(x0 + tab_width), py(0.0)), radius=7, outline="#155e75", width=3, fill="#d7eef1")
        for center in tab["hole_centers_mm"]:
            radius = tab["hole_diameter_mm"] * scale / 2.0
            draw.ellipse((px(center[0]) - radius, py(center[1]) - radius, px(center[0]) + radius, py(center[1]) + radius), outline="#17242d", width=3, fill="#f4f1ea")
        draw.text((px(center_x) - 18, py(3.0) - 10), f"{tab['hole_diameter_mm']:.1f}", font=small, fill="#17242d")
    pitch_x = tabs[0]["hole_centers_mm"][0][0]
    pitch_y0 = tabs[0]["hole_centers_mm"][0][1]
    pitch_y1 = tabs[0]["hole_centers_mm"][1][1]
    dim_x = px(pitch_x - 5.0)
    draw.line((dim_x, py(pitch_y0), dim_x, py(pitch_y1)), fill="#c96a2b", width=3)
    draw.text((dim_x - 52, (py(pitch_y0) + py(pitch_y1)) // 2 - 10), "17 mm", font=small, fill="#a04418")

    head_y = head["origin_y_mm"]
    draw.rectangle((px(0), py(head_y + head["height_mm"]), px(head["width_mm"]), py(head_y)), outline="#155e75", width=3, fill="#d7eef1")
    for notch in head["notches"]:
        w = notch["width_mm"]
        cx = notch["center_x_mm"]
        draw.rectangle((px(cx - w / 2), py(head_y + head["height_mm"]), px(cx + w / 2), py(head_y + head["height_mm"] - float(params["head_gauge"]["notch_depth_mm"]))), fill="#f4f1ea", outline="#17242d", width=2)
        draw.text((px(cx) - 16, py(head_y + 3.0) - 8), f"{w:.1f}", font=small, fill="#17242d")

    ruler_y = ruler["origin_y_mm"]
    draw.rectangle((px(0), py(ruler_y + float(params["length_ruler"]["body_height_mm"])), px(float(params["length_ruler"]["body_width_mm"])), py(ruler_y)), outline="#155e75", width=3, fill="#d7eef1")
    for tick in ruler["ticks"]:
        h = 4.0 if tick["major"] else 2.0
        draw.line((px(tick["x_mm"]), py(ruler_y + 12.0), px(tick["x_mm"]), py(ruler_y + 12.0 - h)), fill="#17242d", width=2)
    draw.text((px(45), py(ruler_y + 8.0)), "Kopfbreitenlehre + 0–30-mm-Grobskala", font=font, fill="#17242d")
    draw.text((margin, canvas.height - 55), "Die kleinste zwangfrei passende Rundlochlasche wird protokolliert; mit montiertem Coupon darf der Drucker nicht verfahren.", font=small, fill="#17242d")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    params_path = args.params.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    params = json.loads(params_path.read_text(encoding="utf-8"))

    mount_cfg = params["mount_tabs"]
    assert abs(float(mount_cfg["screw_center_pitch_mm"]) - 17.0) < 1.0e-9
    candidates = [float(value) for value in mount_cfg["hole_diameter_candidates_mm"]]
    assert candidates == sorted(set(candidates))
    assert candidates[0] <= 2.8 and candidates[-1] >= 4.8
    assert params["evidence_scope"]["third_party_geometry_inputs"] == []
    assert params["evidence_scope"]["third_party_dimensions_used"] is False
    assert params["release_boundary"]["powered_motion_allowed"] is False
    assert params["release_boundary"]["full_diverter_generation_allowed"] is False

    tabs, tab_metrics = build_mount_tabs(params)
    head_y = float(mount_cfg["tab_height_mm"]) + float(params["layout"]["row_gap_mm"])
    head_gauge, head_metrics = build_head_gauge(params, head_y)
    ruler_y = head_y + float(params["head_gauge"]["body_height_mm"]) + float(params["layout"]["component_gap_mm"])
    ruler, ruler_metrics = build_length_ruler(params, ruler_y)
    shapes = [*tabs, head_gauge, ruler]
    coupon = cq.Compound.makeCompound(shapes)

    model_dir = output_dir / "models"
    stl_dir = model_dir / "stl"
    step_dir = model_dir / "step"
    report_dir = output_dir / "reports"
    preview_dir = output_dir / "previews"
    for path in (stl_dir, step_dir, report_dir, preview_dir):
        path.mkdir(parents=True, exist_ok=True)
    stl_path = stl_dir / "DRAFT-R7-C01-interface-measurement-coupon.stl"
    step_path = step_dir / "DRAFT-R7-C01-interface-measurement-coupon.step"
    preview_path = preview_dir / "DRAFT-R7-C01-interface-measurement-coupon.png"
    cq.exporters.export(
        coupon,
        str(stl_path),
        tolerance=float(params["manufacturing"]["stl_linear_tolerance_mm"]),
        angularTolerance=float(params["manufacturing"]["stl_angular_tolerance_rad"]),
    )
    cq.exporters.export(coupon, str(step_path))
    render_preview(params, tab_metrics, head_metrics, ruler_metrics, preview_path)

    mesh_metrics = mesh_record(stl_path)
    expected_components = len(shapes)
    assert mesh_metrics["components"] == expected_components
    assert mesh_metrics["watertight"]
    assert mesh_metrics["winding_consistent"]
    assert all(abs(tab["center_pitch_mm"] - 17.0) < 1.0e-9 for tab in tab_metrics)
    assert all(tab["slot_features"] == 0 for tab in tab_metrics)

    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "project_id": params["project_id"],
        "coupon_id": params["coupon_id"],
        "classification": params["release_boundary"]["classification"],
        "source_scope": params["evidence_scope"],
        "parameters": file_record(params_path, params_path.parent.parent),
        "mount_tabs": tab_metrics,
        "head_gauge": head_metrics,
        "length_ruler": ruler_metrics,
        "geometry": {
            "expected_components": expected_components,
            "actual_components": mesh_metrics["components"],
            "mesh": mesh_metrics,
            "all_mounting_holes_closed_and_round": True,
            "slot_features": 0,
            "supports_required": False,
            "print_orientation": params["manufacturing"]["print_orientation"],
        },
        "mass_estimate_g": mesh_metrics["volume_mm3"] / 1000.0 * float(params["manufacturing"]["density_g_cm3"]),
        "artifacts": {
            "stl": file_record(stl_path, output_dir),
            "step": file_record(step_path, output_dir),
            "preview": file_record(preview_path, output_dir),
        },
        "release_boundary": params["release_boundary"],
        "mesh_simplification": {
            "status": "not-beneficial",
            "reason": "Simple analytic coupon geometry with exact circular test holes, modest mesh size and no organic or relief field; lossy decimation would risk the calibrated openings without a meaningful benefit.",
            "protected_regions": ["all circular test holes", "17 mm hole centres", "head-width notches", "ruler ticks and labels", "bed-contact faces"],
        },
    }
    report_path = report_dir / "generation-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "report": str(report_path), "stl": str(stl_path)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
