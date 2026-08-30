#!/usr/bin/env python3
"""Generate the MM-TOY-002 v2 longitudinal-pivot host coupons.

The front and rear coupons isolate only the chassis-side lower/upper wishbone
axes on a short hollow rail segment.  The unmeasured shock mount and the final
arm-neck path are deliberately excluded.  These are DRAFT interface/process
coupons, not vehicle parts.  Importing this module has no filesystem side
effects.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Literal

import cadquery as cq
import parameters as p

SCRIPT = Path(__file__).resolve()
PROJECT = SCRIPT.parent.parent
DEFAULT_EXPORT_DIR = SCRIPT.parent / "exports" / "v0.4.0-draft.3-pivot-host-coupon"
Variant = Literal["front", "rear"]


def variant_upper_eye_centers_x(variant: Variant) -> tuple[float, float]:
    if variant == "front":
        center = p.DWV2_FRONT_UPPER_OUTER_X_MM - p.AXLE_X_MM
    elif variant == "rear":
        center = p.DWV2_REAR_UPPER_OUTER_X_MM + p.AXLE_X_MM
    else:
        raise ValueError(f"unknown variant: {variant}")
    half_span = p.DWV2_UPPER_INBOARD_HALF_SPAN_X_MM
    return (center - half_span, center + half_span)


def lower_eye_centers_x() -> tuple[float, float]:
    half_span = p.DWV2_LOWER_INBOARD_HALF_SPAN_X_MM
    return (-half_span, half_span)


def upper_tower_points() -> list[tuple[float, float]]:
    """Return the local y/z outline that ties each upper lug into the rail."""
    return [
        (2.0, 21.0),
        (7.0, 21.0),
        (15.8, 29.0),
        (15.8, 35.0),
        (2.2, 35.0),
        (2.2, 28.0),
    ]


def clevis_intervals(
    center_x: float, gap: float, lug_thickness: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    half_gap = gap / 2.0
    return (
        (center_x - half_gap - lug_thickness, center_x - half_gap),
        (center_x + half_gap, center_x + half_gap + lug_thickness),
    )


def cylinder_x(
    x_start: float, length: float, y: float, z: float, radius: float
) -> cq.Shape:
    return cq.Solid.makeCylinder(
        radius,
        length,
        pnt=(x_start, y, z),
        dir=(1.0, 0.0, 0.0),
    )


def yz_prism(
    x_start: float, thickness: float, points: list[tuple[float, float]]
) -> cq.Shape:
    return (
        cq.Workplane("YZ")
        .polyline(points)
        .close()
        .extrude(thickness)
        .val()
        .translate((x_start, 0.0, 0.0))
    )


def hollow_rail() -> cq.Shape:
    length = p.DWV2_HOST_RAIL_LENGTH_MM
    width = p.RAIL_W_MM
    height = p.RAIL_H_MM
    wall = p.DWV2_HOST_RAIL_WALL_MM
    outer = cq.Solid.makeBox(
        length,
        width,
        height,
        pnt=(-length / 2.0, -width / 2.0, 0.0),
    )
    inner = cq.Solid.makeBox(
        length + 2.0,
        width - 2.0 * wall,
        height - 2.0 * wall,
        pnt=(-length / 2.0 - 1.0, -width / 2.0 + wall, wall),
    )
    return outer.cut(inner)


def add_clevis(
    positives: list[cq.Shape],
    cutters: list[cq.Shape],
    *,
    center_x: float,
    axis_y: float,
    axis_z: float,
    gap: float,
    lug_thickness: float,
    boss_diameter: float,
    bore_diameter: float,
    pocket_diameter: float,
    tower_points: list[tuple[float, float]] | None,
) -> None:
    intervals = clevis_intervals(center_x, gap, lug_thickness)
    for x_start, x_end in intervals:
        positives.append(
            cylinder_x(
                x_start,
                x_end - x_start,
                axis_y,
                axis_z,
                boss_diameter / 2.0,
            )
        )
        if tower_points is not None:
            positives.append(yz_prism(x_start, x_end - x_start, tower_points))
    cutter_start = intervals[0][0] - 0.5
    cutter_end = intervals[1][1] + 0.5
    cutters.append(
        cylinder_x(
            cutter_start,
            cutter_end - cutter_start,
            axis_y,
            axis_z,
            bore_diameter / 2.0,
        )
    )
    cutters.append(
        cylinder_x(
            center_x - gap / 2.0,
            gap,
            axis_y,
            axis_z,
            pocket_diameter / 2.0,
        )
    )


def build_pivot_host(variant: Variant) -> cq.Shape:
    positives: list[cq.Shape] = [hollow_rail()]
    cutters: list[cq.Shape] = []

    for center_x in lower_eye_centers_x():
        add_clevis(
            positives,
            cutters,
            center_x=center_x,
            axis_y=p.DWV2_LOWER_INBOARD_Y_MM - p.FRAME_RAIL_Y_MM,
            axis_z=p.DWV2_LOWER_INBOARD_Z_MM,
            gap=p.DWV2_HOST_CLEVIS_GAP_MM,
            lug_thickness=p.DWV2_HOST_LUG_THICKNESS_MM,
            boss_diameter=p.DWV2_HOST_PIVOT_BOSS_DIAMETER_MM,
            bore_diameter=p.DWV2_HOST_PIVOT_BORE_MM,
            pocket_diameter=p.DWV2_HOST_EYE_POCKET_DIAMETER_MM,
            tower_points=None,
        )

    tower_points = upper_tower_points()
    for center_x in variant_upper_eye_centers_x(variant):
        add_clevis(
            positives,
            cutters,
            center_x=center_x,
            axis_y=p.DWV2_UPPER_INBOARD_Y_MM - p.FRAME_RAIL_Y_MM,
            axis_z=p.DWV2_UPPER_INBOARD_Z_MM,
            gap=p.DWV2_HOST_CLEVIS_GAP_MM,
            lug_thickness=p.DWV2_HOST_LUG_THICKNESS_MM,
            boss_diameter=p.DWV2_HOST_PIVOT_BOSS_DIAMETER_MM,
            bore_diameter=p.DWV2_HOST_PIVOT_BORE_MM,
            pocket_diameter=p.DWV2_HOST_EYE_POCKET_DIAMETER_MM,
            tower_points=tower_points,
        )

    host = positives[0]
    for positive in positives[1:]:
        host = host.fuse(positive)
    for cutter in cutters:
        host = host.cut(cutter)
    host = host.clean()
    if not host.isValid() or len(host.Solids()) != 1:
        raise RuntimeError(f"{variant} pivot host is not one valid solid")
    return host


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    try:
        recorded_path = path.relative_to(PROJECT)
    except ValueError:
        recorded_path = path
    return {
        "path": str(recorded_path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def render_preview(mesh_paths: dict[Variant, Path], output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import trimesh
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    figure = plt.figure(figsize=(12.5, 6.2))
    for index, variant in enumerate(("front", "rear"), start=1):
        axis = figure.add_subplot(1, 2, index, projection="3d")
        mesh = trimesh.load_mesh(mesh_paths[variant], process=False)
        triangles = mesh.vertices[mesh.faces]
        collection = Poly3DCollection(
            triangles,
            facecolor="#4f89b8" if variant == "front" else "#5b9a72",
            edgecolor="#21313d",
            linewidth=0.06,
            alpha=0.92,
        )
        axis.add_collection3d(collection)
        bounds = mesh.bounds
        center = bounds.mean(axis=0)
        span = max(bounds[1] - bounds[0])
        half = span * 0.55
        axis.set_xlim(center[0] - half, center[0] + half)
        axis.set_ylim(center[1] - half, center[1] + half)
        axis.set_zlim(max(-5.0, center[2] - half), center[2] + half)
        axis.set_box_aspect((1.0, 1.0, 1.0))
        axis.view_init(elev=24, azim=-56)
        axis.set_title(f"{variant} host coupon")
        axis.set_xlabel("x longitudinal")
        axis.set_ylabel("y outward")
        axis.set_zlabel("z up")
    figure.suptitle(
        "MM-TOY-002 — longitudinal double-wishbone pivot hosts\n"
        "DRAFT interface/process coupons — not vehicle parts"
    )
    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=180,
        metadata={"Software": "MM-TOY-002 deterministic CadQuery workflow"},
    )
    plt.close(figure)


def export_coupons(output_dir: Path) -> dict[str, object]:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite output directory: {output_dir}")
    output_dir.mkdir(parents=True)
    output_paths: list[Path] = []
    mesh_paths: dict[Variant, Path] = {}
    for variant in ("front", "rear"):
        shape = build_pivot_host(variant)
        step_path = output_dir / f"DRAFT-dwv2-{variant}-pivot-host-coupon.step"
        stl_path = output_dir / f"DRAFT-dwv2-{variant}-pivot-host-coupon.stl"
        cq.exporters.export(shape, str(step_path), exportType="STEP")
        cq.exporters.export(
            shape,
            str(stl_path),
            exportType="STL",
            tolerance=0.05,
            angularTolerance=0.1,
        )
        output_paths.extend([step_path, stl_path])
        mesh_paths[variant] = stl_path
    preview_path = output_dir / "DRAFT-dwv2-pivot-host-coupons-preview.png"
    render_preview(mesh_paths, preview_path)
    output_paths.append(preview_path)

    input_paths = [
        SCRIPT,
        SCRIPT.parent / "parameters.py",
        PROJECT / "design-spec.yaml",
        PROJECT / "architecture" / "double-wishbone-v2-interface-contract-v0.4.0.json",
        PROJECT / "validation" / "double-wishbone-v2-kinematics-2026-08-30.json",
    ]
    missing = [str(path) for path in input_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing manifest inputs: " + ", ".join(missing))
    manifest = {
        "schema_version": "1.0",
        "project_id": "MM-TOY-002",
        "project_revision": "0.4.0",
        "candidate": "0.4.0-draft.3",
        "artifact_class": "chassis-pivot-host-interface-coupon",
        "vehicle_part_claim": False,
        "watermark": "DEFERRED_UNTIL_STABLE_PHYSICAL_CANDIDATE",
        "slicer": "NOT_RUN_NO_COMPLETE_PROFILE_SET",
        "inputs": [file_record(path) for path in input_paths],
        "outputs": [file_record(path) for path in output_paths],
        "notes": [
            "Coupons qualify chassis-side x-axis topology and nominal M3 process geometry only.",
            "The shock host is intentionally excluded pending arm-path and exact shock-envelope validation.",
            "Straight arm-beam routing is not claimed; only the inboard-eye pocket and clevis stack are represented.",
            "No full chassis, arm, upright, wheel, shock or drivetrain fit claim is made.",
        ],
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    for variant in ("front", "rear"):
        shape = build_pivot_host(variant)
        print(
            f"{variant}: valid={shape.isValid()} solids={len(shape.Solids())} "
            f"volume_mm3={shape.Volume():.3f}"
        )
    if args.check_only:
        return 0
    manifest = export_coupons(args.output_dir)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
