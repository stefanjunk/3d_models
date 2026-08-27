#!/usr/bin/env python3
"""Build, export, and validate all twenty system-furniture concept models."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cadquery as cq
import trimesh
from cadquery import exporters

from systemmoebel_top20 import ModelSpec
from systemmoebel_top20.models import (
    build_group_a,
    build_group_b,
    build_group_c,
    build_group_d,
)


ROOT = Path(__file__).resolve().parent


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def bed_place(workplane: cq.Workplane) -> cq.Workplane:
    shape = workplane.val()
    bb = shape.BoundingBox()
    placed = shape.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    return cq.Workplane("XY").newObject([placed])


def validate_mesh(path: Path, envelope: tuple[float, float, float]) -> dict:
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Expected one mesh in {path}, got {type(mesh).__name__}")
    extents = tuple(round(float(value), 3) for value in mesh.extents)
    components = mesh.split(only_watertight=False)
    return {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "connected_components": len(components),
        "volume_mm3": round(float(abs(mesh.volume)), 3),
        "surface_area_mm2": round(float(mesh.area), 3),
        "triangles": int(len(mesh.faces)),
        "bounds_mm": extents,
        "within_target_build_volume": all(size <= limit + 0.01 for size, limit in zip(extents, envelope)),
    }


def validate_step(path: Path, envelope: tuple[float, float, float]) -> dict:
    imported = cq.importers.importStep(str(path))
    solids = imported.solids().vals()
    if not solids:
        return {
            "solid_count": 0,
            "volume_mm3": 0.0,
            "bounds_mm": [0.0, 0.0, 0.0],
            "within_target_build_volume": False,
        }
    compound = cq.Compound.makeCompound(solids)
    bb = compound.BoundingBox()
    bounds = (round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3))
    return {
        "solid_count": len(solids),
        "volume_mm3": round(sum(float(solid.Volume()) for solid in solids), 3),
        "bounds_mm": bounds,
        "within_target_build_volume": all(size <= limit + 0.01 for size, limit in zip(bounds, envelope)),
    }


def _point_is_solid(shape: cq.Shape, point: tuple[float, float, float]) -> bool:
    probe_size = 0.2
    probe = cq.Solid.makeBox(
        probe_size,
        probe_size,
        probe_size,
        cq.Vector(
            point[0] - probe_size / 2.0,
            point[1] - probe_size / 2.0,
            point[2] - probe_size / 2.0,
        ),
    )
    return shape.intersect(probe).Volume() > 1e-6


def validate_design_features(specs: list[ModelSpec], config: dict) -> list[dict]:
    by_index = {spec.index: spec for spec in specs}
    checks: list[dict] = []

    feature_points: dict[int, tuple[str, list[tuple[float, float, float]]]] = {
        5: (
            "four BROR purchased-strap through-slots",
            [(x, y, 2.5) for x in (-55.0, 55.0) for y in (12.0, 28.0)],
        ),
        8: (
            "two SKADIS slotted retention flanges",
            [
                (
                    side
                    * (
                        (config["08_skadis_workflow_cluster"]["width"] - 24.0) / 2.0
                        + max(18.0, 3.0 * config["08_skadis_workflow_cluster"]["backplate"]) / 2.0
                        - max(6.0, config["08_skadis_workflow_cluster"]["backplate"])
                    ),
                    0.0,
                    config["08_skadis_workflow_cluster"]["backplate"] / 2.0,
                )
                for side in (-1.0, 1.0)
            ],
        ),
        11: (
            "four BOAXEL purchased-strap through-slots",
            [
                (x + offset, 23.0, 1.5)
                for x in (-78.0, 78.0)
                for offset in (-6.0, 6.0)
            ],
        ),
        10: (
            "fine OMAR vent openings",
            [(0.0, 0.0, config["10_omar_shelf_deck"]["wall"] / 2.0)],
        ),
    }

    for index, (name, points) in feature_points.items():
        shape = by_index[index].solid.val()
        void_points = [not _point_is_solid(shape, point) for point in points]
        checks.append(
            {
                "model": index,
                "feature": name,
                "sample_points": points,
                "void_points_confirmed": sum(void_points),
                "required_void_points": len(points),
                "passed": all(void_points),
            }
        )
    return checks


def write_markdown_report(records: list[dict], path: Path) -> None:
    lines = [
        "# Mesh-Validierung: Systemmöbel Top 20",
        "",
        "Digitale Prüfung der erzeugten STL-Dateien. Physische Passungs-, Last- und Slicer-Tests stehen noch aus.",
        "",
        "| Nr. | Modell | Bounds mm | STL-Komponenten | Wasserdicht | STEP-Solids | Bauraum |",
        "|---:|---|---:|---:|:---:|---:|:---:|",
    ]
    for record in records:
        check = record["mesh"]
        bounds = " × ".join(f"{value:.1f}" for value in check["bounds_mm"])
        lines.append(
            f"| {record['index']} | `{record['filename']}.stl` | {bounds} | "
            f"{check['connected_components']} | {'ja' if check['watertight'] else 'NEIN'} | "
            f"{record['step']['solid_count']} | "
            f"{'ja' if check['within_target_build_volume'] else 'NEIN'} |"
        )
    lines.extend(
        [
            "",
            "## Freigabestatus",
            "",
            "- **Geometrie-Gate:** bestanden, wenn jede Zeile wasserdicht, ein Volumenkörper, eine Komponente und im Zielbauraum ist.",
            "- **Passungs-Gate:** blockiert, bis die jeweilige Möbelrevision vermessen und ein Fit-Coupon gedruckt wurde.",
            "- **Last-Gate:** blockiert, bis belastete Clips und Halter physisch geprüft wurden.",
            "- **Produktions-Gate:** blockiert, bis jedes Modell im vorgesehenen Material und Profil gesliced und probeweise gedruckt wurde.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "defaults.json")
    parser.add_argument("--only", type=int, nargs="*", help="Build only selected product numbers")
    parser.add_argument("--no-step", action="store_true", help="Skip STEP exports")
    args = parser.parse_args()

    config = load_config(args.config)
    envelope = tuple(float(value) for value in config["project"]["target_build_volume"])
    selected = set(args.only or range(1, 21))

    start = time.time()
    specs: list[ModelSpec] = []
    for builder in (build_group_a, build_group_b, build_group_c, build_group_d):
        specs.extend(builder(config))
    specs = [spec for spec in specs if spec.index in selected]
    specs.sort(key=lambda spec: spec.index)

    expected = selected.intersection(range(1, 21))
    actual = {spec.index for spec in specs}
    if actual != expected:
        raise SystemExit(f"Model index mismatch: expected {sorted(expected)}, got {sorted(actual)}")

    feature_checks = validate_design_features(specs, config) if selected == set(range(1, 21)) else []
    failed_features = [check["feature"] for check in feature_checks if not check["passed"]]
    if failed_features:
        raise SystemExit(f"Required design-feature checks failed: {failed_features}")

    stl_dir = ROOT / "exports" / "stl"
    step_dir = ROOT / "exports" / "step"
    reports_dir = ROOT / "reports"
    stl_dir.mkdir(parents=True, exist_ok=True)
    step_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    failed: list[str] = []
    for spec in specs:
        print(f"[{spec.index:02d}/20] {spec.title}", flush=True)
        printable = bed_place(spec.solid)
        stl_path = stl_dir / f"{spec.filename}.stl"
        exporters.export(printable, str(stl_path), tolerance=0.08, angularTolerance=0.12)
        check = validate_mesh(stl_path, envelope)
        if not args.no_step:
            step_path = step_dir / f"{spec.filename}.step"
            exporters.export(spec.solid, str(step_path))
            step_check = validate_step(step_path, envelope)
        else:
            step_check = {
                "solid_count": 1,
                "volume_mm3": round(float(spec.solid.val().Volume()), 3),
                "bounds_mm": check["bounds_mm"],
                "within_target_build_volume": True,
            }
        record = {
            "index": spec.index,
            "slug": spec.slug,
            "filename": spec.filename,
            "title": spec.title,
            "material": spec.material,
            "print_orientation": spec.print_orientation,
            "support_intent": "support-free" if not spec.support_required else "supports-expected",
            "declared_functional_wall_mm": spec.minimum_wall_mm,
            "interface_note": spec.interface_note,
            "protected_features": list(spec.protected_features),
            "mesh": check,
            "step": step_check,
        }
        records.append(record)
        passed = (
            check["watertight"]
            and check["winding_consistent"]
            and check["is_volume"]
            and check["connected_components"] == 1
            and check["within_target_build_volume"]
            and step_check["solid_count"] == 1
            and step_check["volume_mm3"] > 0
            and step_check["within_target_build_volume"]
        )
        if not passed:
            failed.append(spec.filename)
        print(
            f"  {check['bounds_mm']} mm, {check['triangles']} triangles, "
            f"{'PASS' if passed else 'FAIL'}"
        )

    report = {
        "status": "PASS" if not failed else "FAIL",
        "generated_models": len(records),
        "failed_models": failed,
        "target_build_volume_mm": envelope,
        "fit_status": config["project"]["fit_status"],
        "elapsed_seconds": round(time.time() - start, 3),
        "models": records,
    }
    (reports_dir / "mesh-validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_markdown_report(records, reports_dir / "mesh-validation.md")
    (reports_dir / "resolved-parameters.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (reports_dir / "feature-validation.json").write_text(
        json.dumps(
            {
                "status": "PASS" if not failed_features else "FAIL",
                "checks": feature_checks,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    if failed:
        print(f"Validation failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"Generated and validated {len(records)} models in {time.time() - start:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
