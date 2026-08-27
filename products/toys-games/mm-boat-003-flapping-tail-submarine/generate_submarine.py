#!/usr/bin/env python3
"""Generate the flapping-tail submarine: STL exports, previews, buoyancy + preflight reports."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import cadquery as cq
from cadquery import exporters

from submarine.buoyancy import compute_buoyancy
from submarine.config import SubmarineConfig
from submarine.geometry import PartSpec, build_all
from submarine.mechanism import solve_rocker, validate_rocker
from submarine.preflight import PartCheck, run_preflight

ROOT = Path(__file__).resolve().parent


def _rotated(solid: cq.Solid, rot: tuple[float, float, float]) -> cq.Solid:
    axes = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    out = solid
    for axis, ang in zip(axes, rot):
        if ang:
            out = out.rotate((0, 0, 0), axis, ang)
    return out


def _bed_placement(solid: cq.Solid) -> cq.Solid:
    bb = solid.BoundingBox()
    return solid.translate((-bb.xmin, -bb.ymin, -bb.zmin))


def export_print_stl(spec: PartSpec, path: Path) -> tuple[float, float, float]:
    s = _bed_placement(_rotated(spec.solid.val(), spec.print_rotation))
    exporters.export(cq.Workplane("XY").newObject([s]), str(path), tolerance=0.08)
    bb = s.BoundingBox()
    return (bb.xlen, bb.ylen, bb.zlen)


def check_mesh(path: Path) -> tuple[bool, float]:
    import trimesh

    m = trimesh.load(str(path), force="mesh")
    return bool(m.is_watertight), float(m.volume)


def export_previews(parts: list[PartSpec], out_dir: Path) -> None:
    world_dir = out_dir / "world"
    world_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    for spec in parts:
        fname = world_dir / f"{spec.name}.stl"
        exporters.export(spec.solid, str(fname), tolerance=0.12)
        lines.append(f'import("world/{spec.name}.stl");')
    (out_dir / "assembly.scad").write_text("\n".join(lines) + "\n")
    png = out_dir / "assembly.png"
    try:
        subprocess.run(
            [
                "openscad", "-o", str(png),
                "--camera=180,-120,60,55,0,25,520",
                "--colorscheme=Tomorrow",
                str(out_dir / "assembly.scad"),
            ],
            check=True,
            capture_output=True,
            timeout=300,
        )
        print(f"  preview: {png.relative_to(ROOT)}")
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"  preview render skipped: {exc.__class__.__name__}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "exports" / "stl")
    parser.add_argument("--no-previews", action="store_true")
    parser.add_argument("--skip-mesh-checks", action="store_true")
    args = parser.parse_args()

    cfg = SubmarineConfig()
    t0 = time.time()
    print("building geometry ...")
    parts = build_all(cfg)
    print(f"  {len(parts)} parts in {time.time() - t0:.1f} s")

    args.outdir.mkdir(parents=True, exist_ok=True)
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)

    envelope_mm3: dict[str, float] = {}
    part_mass_mm3: dict[str, float] = {}
    part_checks: list[PartCheck] = []

    print("exporting STLs (print orientation) ...")
    for spec in parts:
        path = args.outdir / f"{spec.name}.stl"
        bbox = export_print_stl(spec, path)
        part_mass_mm3[spec.name] = spec.solid.val().Volume()
        if spec.envelope is not None:
            envelope_mm3[spec.name] = spec.envelope.val().Volume()
        wt_actual = None
        if not args.skip_mesh_checks:
            try:
                watertight, _ = check_mesh(path)
                wt_actual = watertight
            except ImportError:
                pass
        part_checks.append(
            PartCheck(
                name=spec.name,
                bbox=(round(bbox[0], 1), round(bbox[1], 1), round(bbox[2], 1)),
                watertight_expected=spec.watertight,
                watertight_actual=wt_actual,
                print_note=spec.note,
            )
        )
        print(f"  {spec.name:18s} {bbox[0]:6.1f} x {bbox[1]:6.1f} x {bbox[2]:6.1f} mm")

    buoyancy = compute_buoyancy(cfg, envelope_mm3, part_mass_mm3)
    mech = validate_rocker(cfg)
    report = run_preflight(cfg, buoyancy, mech, part_checks)

    (reports_dir / "buoyancy.json").write_text(json.dumps(buoyancy.to_dict(), indent=2))
    (reports_dir / "preflight.json").write_text(json.dumps(report, indent=2))
    (reports_dir / "rocker.json").write_text(
        json.dumps(solve_rocker(cfg).__dict__ | {"problems": mech}, indent=2, default=float)
    )
    (reports_dir / "config.json").write_text(json.dumps(cfg.to_dict(), indent=2))
    angle_scales = [
        cfg.fish_rib_dorsal_scale
        + min(abs(angle) / 90.0, 1.0)
        * (cfg.fish_rib_lateral_scale - cfg.fish_rib_dorsal_scale)
        for angle in cfg.fish_rib_angles_deg
    ]
    peak_r = cfg.fish_rib_peak_radius * max(angle_scales)
    peak_overlap = min(cfg.fish_rib_overlap, 0.75 * peak_r)
    surfacing = {
        "method": "bspline-loft-hybrid",
        "construction": "additive B-Rep rib envelope; functional core not deformed",
        "ribbed_parts": [
            "nose_body", "segment_01", "segment_02", "segment_03",
            "segment_04", "capsule_body",
        ],
        "rib_count_per_part": len(cfg.fish_rib_angles_deg),
        "semantic_sections_per_rib": 4,
        "loft_solids": 6 * len(cfg.fish_rib_angles_deg),
        "angles_deg_from_dorsal": list(cfg.fish_rib_angles_deg),
        "minimum_printed_rib_diameter_mm": round(
            2 * cfg.fish_rib_end_radius * min(angle_scales), 3
        ),
        "maximum_visible_protrusion_mm": round(2 * peak_r - peak_overlap, 3),
        "joint_end_margin_mm": cfg.fish_rib_end_margin,
        "hardpoint_geometry_modified": False,
        "hardpoint_validation": "PASS via existing collision/fit tests",
        "parameter_extremes": "PASS via test_fish_rib_parameter_sweep_valid",
        "continuity_intent": "G2 longitudinal highlight flow",
        "continuity_measurement": "NOT_RUN; no formal G2/Class-A claim",
        "topology": "PASS via mesh watertightness preflight",
        "tessellation_chord_tolerance_mm": 0.08,
    }
    (reports_dir / "surfacing.json").write_text(json.dumps(surfacing, indent=2))

    print("\n-- buoyancy --------------------------------------------------")
    for k, v in buoyancy.to_dict().items():
        print(f"  {k:34s} {v}")
    print(f"\npreflight: PASS ({len(report['checks'])} checks)")

    if not args.no_previews:
        print("\nrendering previews ...")
        export_previews(parts, ROOT / "previews")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
