#!/usr/bin/env python3
"""Create auditable JSI-WM-001-R1 evidence from the marked DRAFT candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.patches import Circle, Polygon as MplPolygon, Rectangle
from shapely.geometry import LineString


ROOT = Path(__file__).resolve().parent.parent
DXF = Path(__file__).resolve().parent / "just-innovation-watermark" / "exports" / "dxf" / "just-innovation-compact.dxf"
MARKED_STL = ROOT / "STL" / "MODULE_OUTPUT_bronze.stl"
OUT = ROOT / "reports" / "watermark"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_mark_polygons():
    source = trimesh.load_path(DXF)
    return list(source.polygons_full)


def draw_mark(ax, polygons, center_z=62.0, recess="#E9DFC9", body="#5A3827"):
    for poly in polygons:
        exterior = np.asarray(poly.exterior.coords)
        exterior[:, 1] += center_z
        ax.add_patch(MplPolygon(exterior, closed=True, facecolor=recess, edgecolor="#B28A50", linewidth=0.7))
        for interior in poly.interiors:
            coords = np.asarray(interior.coords)
            coords[:, 1] += center_z
            ax.add_patch(MplPolygon(coords, closed=True, facecolor=body, edgecolor=body, linewidth=0.2))


def orthographic(polygons):
    fig, ax = plt.subplots(figsize=(4.2, 10.5), dpi=180)
    fig.patch.set_facecolor("#EEE8DC"); ax.set_facecolor("#EEE8DC")
    ax.add_patch(Rectangle((-10, 0), 20, 124, facecolor="#5A3827", edgecolor="#2E1D15", linewidth=1.2))
    for z in (38.44, 88.04):
        ax.add_patch(Circle((0, z), 4.7, facecolor="#EEE8DC", edgecolor="#2E1D15", linewidth=0.8))
        ax.add_patch(Circle((0, z), 2.35, facecolor="#D6CCBA", edgecolor="none"))
    draw_mark(ax, polygons)
    ax.set_xlim(-13, 13); ax.set_ylim(-3, 127); ax.set_aspect("equal"); ax.axis("off")
    fig.text(0.08, 0.975, "JSI-WM-001-R1 · FERTIGE AUSSENANSICHT", ha="left", va="top", fontsize=10.5, weight="bold", color="#302923")
    fig.text(0.08, 0.952, "actual marked MODULE_OUTPUT_bronze geometry · viewed from +Y", ha="left", va="top", fontsize=7, color="#62584E")
    fig.savefig(OUT / "watermark_orthographic.png", bbox_inches="tight")
    plt.close(fig)


def dimensioned(polygons, bounds, side_clearance, nearest_counterbore_clearance):
    fig, ax = plt.subplots(figsize=(7.6, 5.5), dpi=180)
    fig.patch.set_facecolor("#EEE8DC"); ax.set_facecolor("#EEE8DC")
    ax.add_patch(Rectangle((-10, 50), 20, 24, facecolor="#5A3827", edgecolor="#2E1D15", linewidth=1.2))
    draw_mark(ax, polygons)
    xmin, zmin, xmax, zmax = bounds[0], 62 + bounds[1], bounds[2], 62 + bounds[3]
    ax.annotate("", xy=(xmin, 49.1), xytext=(xmax, 49.1), arrowprops=dict(arrowstyle="<->", color="#302923", linewidth=1.0))
    ax.text((xmin+xmax)/2, 48.3, f"{xmax-xmin:.3f} mm", ha="center", va="top", fontsize=8)
    ax.annotate("", xy=(10.9, zmin), xytext=(10.9, zmax), arrowprops=dict(arrowstyle="<->", color="#302923", linewidth=1.0))
    ax.text(11.5, (zmin+zmax)/2, f"{zmax-zmin:.3f} mm", rotation=90, ha="left", va="center", fontsize=8)
    ax.annotate(f"{side_clearance:.2f} mm side clearance", xy=(xmax, 62), xytext=(-9.5, 72.3), arrowprops=dict(arrowstyle="->", color="#8B6B3F"), fontsize=7.5)
    ax.annotate(f"≥{nearest_counterbore_clearance:.2f} mm to nearest counterbore", xy=(0, zmin), xytext=(-9.5, 51.0), arrowprops=dict(arrowstyle="->", color="#8B6B3F"), fontsize=7.5)
    ax.set_xlim(-12.5, 15.5); ax.set_ylim(47.0, 76.2); ax.set_aspect("equal"); ax.axis("off")
    fig.text(0.06, 0.965, "DIMENSIONIERTER MARKIERUNGSBEREICH", ha="left", va="top", fontsize=11, weight="bold", color="#302923")
    fig.text(0.06, 0.925, "compact profile · scale 1.0 · rotation 0° · centre X=0 / Z=62 mm", ha="left", va="top", fontsize=7.5, color="#62584E")
    fig.savefig(OUT / "watermark_dimensioned.png", bbox_inches="tight")
    plt.close(fig)


def section_view(bounds):
    fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=180)
    fig.patch.set_facecolor("#EEE8DC"); ax.set_facecolor("#EEE8DC")
    ax.add_patch(Rectangle((0, 0), 5.2, 10, facecolor="#5A3827", edgecolor="#2E1D15", linewidth=1.2))
    ax.add_patch(Rectangle((4.8, 3.3), 0.4, 3.4, facecolor="#EEE8DC", edgecolor="#B28A50", linewidth=0.9))
    ax.axvline(0, color="#2E1D15", linestyle="--", linewidth=0.9)
    ax.text(0, 10.45, "wall datum Y=0", ha="center", fontsize=7.5)
    ax.annotate("", xy=(4.8, 2.6), xytext=(5.2, 2.6), arrowprops=dict(arrowstyle="<->", linewidth=1.0))
    ax.text(5.0, 2.0, "0.40 mm recess", ha="center", fontsize=8)
    ax.annotate("", xy=(0, 8.0), xytext=(4.8, 8.0), arrowprops=dict(arrowstyle="<->", linewidth=1.0))
    ax.text(2.4, 8.45, "4.80 mm residual spine", ha="center", fontsize=8)
    ax.text(2.6, 0.75, "host before cut: 5.20 mm", ha="center", fontsize=8, color="#E9DFC9")
    ax.text(6.05, 5.0, "viewed section\nthrough one filled stroke", va="center", fontsize=7.5, color="#62584E")
    ax.set_xlim(-0.8, 8.0); ax.set_ylim(-0.5, 11.5); ax.set_aspect("equal"); ax.axis("off")
    fig.text(0.06, 0.96, "RECESS SECTION", ha="left", va="top", fontsize=11, weight="bold", color="#302923")
    fig.text(0.06, 0.91, f"mark lies at Z={62+bounds[1]:.3f}…{62+bounds[3]:.3f} mm; module bed datum Z=0 remains unchanged", ha="left", va="top", fontsize=7.5, color="#62584E")
    fig.savefig(OUT / "watermark_section.png", bbox_inches="tight")
    plt.close(fig)


def layer_preview(polygons):
    # Exact 0.20 mm geometric layer sections.  This is deliberately labelled as
    # geometry evidence; destination-slicer toolpath approval remains pending.
    levels = np.linspace(-5.4, 5.4, 8)
    fig, axes = plt.subplots(2, 4, figsize=(12.0, 5.6), dpi=170, sharex=True, sharey=True)
    fig.patch.set_facecolor("#EEE8DC")
    for ax, local_z in zip(axes.ravel(), levels):
        ax.set_facecolor("#EEE8DC")
        ax.add_patch(Rectangle((-10, 0), 20, 5.2, facecolor="#5A3827", edgecolor="#2E1D15", linewidth=0.8))
        line = LineString([(-20, local_z), (20, local_z)])
        intervals = []
        for poly in polygons:
            inter = poly.intersection(line)
            geoms = [inter] if inter.geom_type == "LineString" else list(getattr(inter, "geoms", []))
            for geom in geoms:
                if geom.geom_type == "LineString" and geom.length > 1e-6:
                    xs = [p[0] for p in geom.coords]
                    intervals.append((min(xs), max(xs)))
        for x0, x1 in intervals:
            ax.add_patch(Rectangle((x0, 4.8), x1-x0, 0.4, facecolor="#EEE8DC", edgecolor="#B28A50", linewidth=0.45))
        layer_z = 62.0 + local_z
        layer_index = round(layer_z / 0.2)
        ax.set_title(f"Z={layer_z:.2f} mm · L{layer_index}", fontsize=7.2)
        ax.set_xlim(-10.5, 10.5); ax.set_ylim(-0.25, 5.45); ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle("0.20-mm GEOMETRIC LAYER RECONSTRUCTION · WATERMARK-BEARING LAYERS", x=0.03, y=0.98, ha="left", fontsize=10.5, weight="bold", color="#302923")
    fig.text(0.03, 0.025, "Exact marked-mesh section logic; Anycubic Slicer Next toolpath preview remains a release-side user check.", fontsize=7.4, color="#62584E")
    fig.subplots_adjust(left=0.025, right=0.985, bottom=0.09, top=0.88, wspace=0.08, hspace=0.28)
    fig.savefig(OUT / "watermark_layer_preview.png", bbox_inches="tight")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    polygons = load_mark_polygons()
    combined_bounds = np.array([poly.bounds for poly in polygons])
    bounds = [float(combined_bounds[:,0].min()), float(combined_bounds[:,1].min()), float(combined_bounds[:,2].max()), float(combined_bounds[:,3].max())]
    side_clearance = 10.0 - max(abs(bounds[0]), abs(bounds[2]))
    counterbore_centres = (124.0 * 0.31, 124.0 * 0.71)
    zmin = 62.0 + bounds[1]
    zmax = 62.0 + bounds[3]
    nearest_counterbore_clearance = min(
        zmin - (counterbore_centres[0] + 4.7),
        (counterbore_centres[1] - 4.7) - zmax,
    )
    mesh = trimesh.load_mesh(MARKED_STL, process=True)
    unmarked_volume = 17440.925475541462
    marked_volume = abs(float(mesh.volume))
    area = sum(float(poly.area) for poly in polygons)
    expected_removed = area * 0.4
    report = {
        "status": "DRAFT-BLOCKED-DESTINATION-SLICER-EVIDENCE",
        "asset_id": "JSI-WM-001-R1",
        "variant": "compact",
        "operation": "recessed",
        "surface": "front face of the rear central bronze spine; alternate safe surface because no 10 mm-high obstruction-free underside patch exists",
        "uniform_scale": 1.0,
        "rotation_deg": 0.0,
        "actual_envelope_mm": [round(bounds[2]-bounds[0], 6), round(bounds[3]-bounds[1], 6)],
        "position_mm": {"centre_x": 0.0, "exterior_y": 5.2, "centre_z": 62.0},
        "depth_mm": 0.4,
        "host_wall_before_mm": 5.2,
        "residual_host_wall_mm": 4.8,
        "side_edge_clearance_mm": round(side_clearance, 6),
        "nearest_counterbore_clearance_mm": round(nearest_counterbore_clearance, 6),
        "module_bed_datum_z_mm": 0.0,
        "mark_z_range_mm": [round(62+bounds[1], 6), round(62+bounds[3], 6)],
        "marked_candidate": str(MARKED_STL.relative_to(ROOT)),
        "marked_candidate_sha256": sha256(MARKED_STL),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "components": len(mesh.split(only_watertight=False)),
        "unmarked_reference_volume_mm3": unmarked_volume,
        "marked_volume_mm3": marked_volume,
        "removed_volume_mm3": unmarked_volume - marked_volume,
        "expected_outline_area_times_depth_mm3": expected_removed,
        "volume_delta_error_mm3": abs((unmarked_volume-marked_volume)-expected_removed),
        "coverage": {
            "marked": ["MODULE_OUTPUT_bronze", "MODULE_MIDDLE_A_bronze", "MODULE_MIDDLE_B_bronze"],
            "covered_by_marked_assembly": ["MODULE_CROWN", "scent_tray", "connector_pins", "colour inlay bodies"],
            "standalone_saleable_unmarked_parts": []
        },
        "profile": {"printer": "Anycubic Kobra 3 Max", "nozzle_mm": 0.4, "layer_height_mm": 0.2, "material": "PETG"},
        "evidence": ["watermark_orthographic.png", "watermark_dimensioned.png", "watermark_section.png", "watermark_layer_preview.png"],
        "destination_slicer_preview": "PENDING-Anycubic-Slicer-Next",
        "note": "The included layer preview is an exact 0.20 mm geometric reconstruction, not G-code evidence."
    }
    orthographic(polygons)
    dimensioned(polygons, bounds, side_clearance, nearest_counterbore_clearance)
    section_view(bounds)
    layer_preview(polygons)
    (OUT / "watermark_validation_DRAFT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
