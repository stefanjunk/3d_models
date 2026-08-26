#!/usr/bin/env python3
"""Create a deterministic mold-design plan from a JSON specification."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


def require(data: dict[str, Any], path: str) -> Any:
    value: Any = data
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            raise ValueError(f"Missing required field: {path}")
        value = value[key]
    return value


def compensated_dimensions(final: list[float], shrink: list[float]) -> tuple[list[float], list[float]]:
    if len(final) != 3 or len(shrink) != 3:
        raise ValueError("Dimensions and shrinkage must contain X/Y/Z values.")
    factors: list[float] = []
    tool: list[float] = []
    for d, s in zip(final, shrink, strict=True):
        if d <= 0 or s >= 100:
            raise ValueError("Invalid final dimension or shrinkage.")
        f = 1.0 / (1.0 - s / 100.0)
        factors.append(f)
        tool.append(d * f)
    return factors, tool


def process_guardrails(spec: dict[str, Any]) -> list[str]:
    casting = spec["casting"]
    route = casting["route"]
    final_material = casting["final_material"]
    warnings: list[str] = []
    ceramic = final_material in {"porcelain", "stoneware", "earthenware"}

    if ceramic and route == "direct_printed_negative":
        warnings.append("STOP: ordinary dense printed negatives are not the normal absorbent working mold for conventional ceramic slip casting. Route through a pottery-plaster working mold or explicitly validate an experimental porous process.")
    if ceramic and spec["shrinkage"]["status"] != "measured":
        warnings.append("Ceramic shrinkage is not measured; dimensions are provisional until exact body/process coupons are fired and measured.")
    if route == "experimental_porous_print":
        warnings.append("Experimental porous print selected: require permeability, water uptake, release, wear, contamination, and cycle testing.")
    if spec["final_object"].get("food_contact"):
        if not spec["validation"].get("migration_lab_test"):
            warnings.append("Food-contact article lacks a migration laboratory test in the validation plan.")
        if spec["detail"].get("placement") in {"interior", "both"}:
            warnings.append("Fine relief is planned on a food-contact interior; require glaze-flow and cleanability coupons and consider moving fine detail outside.")
    if spec["final_object"].get("dishwasher_target") and not spec["validation"].get("dishwasher_cycle_test"):
        warnings.append("Dishwasher target is set but no dishwasher-cycle qualification is planned.")
    if not spec["validation"].get("detail_coupon"):
        warnings.append("No detail-transfer coupon is planned.")
    if not spec["validation"].get("demolding_test"):
        warnings.append("No demolding test is planned.")
    return warnings


def tool_route(spec: dict[str, Any]) -> str:
    source = spec["source"]["type"]
    architecture = spec["mold"]["architecture"]
    if source in {"stl", "obj", "ply", "3mf", "image_heightmap"}:
        base = "Blender for organic mesh/relief preparation"
    else:
        base = "CadQuery or FreeCAD for dimensional BREP construction"
    if architecture in {"solid_block", "hollow_block"}:
        return base + "; OpenSCAD or CadQuery is sufficient for simple block/split tooling"
    if architecture in {"ribbed_shell", "printed_case", "hybrid", "modular_panels"}:
        return base + "; build ribs, flanges, keys, and channels parametrically in CadQuery/FreeCAD"
    if architecture == "flexible_skin_mother_mold":
        return "Blender for sculpted skin/parting geometry; CadQuery/FreeCAD for the mother-mold frame"
    if architecture == "precision_insert_frame":
        return "Blender or height-map tooling for the detail insert; CadQuery/OpenSCAD for the reusable frame"
    return base


def memory_summary(spec: dict[str, Any]) -> str:
    dims = spec["final_object"]["dimensions_mm"]
    pitch = spec["detail"].get("heightmap_pitch_mm")
    if not pitch:
        return "No height-map pitch specified; estimate before remesh/displacement."
    w = max(2, math.ceil(dims[0] / pitch) + 1)
    h = max(2, math.ceil(dims[1] / pitch) + 1)
    triangles = 2 * (w - 1) * (h - 1)
    return f"A full XY height field at {pitch:g} mm pitch would be about {w}×{h} samples and {triangles:,} triangles before side/back geometry. Use only the decorated region where possible."


def generate_plan(spec: dict[str, Any], source_path: Path) -> str:
    for field in (
        "project.name", "project.units", "final_object.dimensions_mm", "casting.final_material",
        "casting.route", "source.type", "printer.process", "mold.architecture",
        "mold.parting_strategy", "shrinkage.status", "shrinkage.percent_xyz",
        "detail.smallest_feature_mm", "validation.acceptance"
    ):
        require(spec, field)

    final = list(map(float, spec["final_object"]["dimensions_mm"]))
    shrink = list(map(float, spec["shrinkage"]["percent_xyz"]))
    factors, tool_dims = compensated_dimensions(final, shrink)
    warnings = process_guardrails(spec)
    m = spec["mold"]
    c = spec["casting"]
    d = spec["detail"]

    steps = [
        "Freeze the original source and run mesh/BREP preflight with verified millimetre units.",
        "Create a low-resolution proxy for parting, pull-direction, handling, and build-volume decisions.",
        f"Apply compensation scale X/Y/Z = {factors[0]:.6f}, {factors[1]:.6f}, {factors[2]:.6f}; keep the datum fixed.",
        f"Implement architecture `{m['architecture']}` with this split strategy: {m['parting_strategy']}",
        "Prove every rigid section's swept removal path; replace unresolved undercuts with more sections, loose pieces, flexible skin, or a sacrificial core.",
        "Add asymmetric keys, broad flanges, clamp load paths, labels, and controlled opening features.",
        "Design fill/reservoir/vent/drain geometry in the real gravity orientation and prove all channels are continuous and cleanable.",
        "Generate a detail coupon containing the minimum groove/ridge, curvature, seam, and selected surface finish.",
        "Export neutral design files plus print meshes; run mesh preflight and inspect slicer preview.",
        "Perform the physical prototype ladder: key strip, detail transfer, reduced assembly, leak/drain test where compatible, then full trial."
    ]

    if c["route"] in {"printed_master_to_plaster", "printed_case_to_plaster"}:
        steps.insert(7, "Make the pottery-plaster working mold using the exact product datasheet. Seal/release the printed master/case interface, but leave the ceramic slip-contact face absorbent.")

    flags = []
    for key, label in (
        ("funnel", "funnel/spout"), ("reservoir", "top-up reservoir"),
        ("vents", "air vents"), ("drain_cradle", "drain cradle")
    ):
        if m.get(key):
            flags.append(label)

    lines = [
        f"# Mold plan — {spec['project']['name']}",
        "",
        f"Source specification: `{source_path.name}`",
        f"Units: `{spec['project']['units']}`",
        "",
        "## Process classification",
        "",
        f"- Final material: **{c['final_material']}**",
        f"- Tool route: **{c['route']}**",
        f"- Fill mode: **{c.get('fill_mode', 'not specified')}**",
        f"- Planned cycles: **{c.get('target_cycles', 'not specified')}**",
        f"- Tool recommendation: {tool_route(spec)}",
        "",
        "## Dimensions and shrinkage",
        "",
        f"- Desired final XYZ: `{final[0]:.3f} × {final[1]:.3f} × {final[2]:.3f} mm`",
        f"- Shrinkage status: **{spec['shrinkage']['status']}**",
        f"- Shrinkage XYZ: `{shrink[0]:.3f}%, {shrink[1]:.3f}%, {shrink[2]:.3f}%`",
        f"- Compensation scale XYZ: `{factors[0]:.6f}, {factors[1]:.6f}, {factors[2]:.6f}`",
        f"- Compensated master/green XYZ: `{tool_dims[0]:.3f} × {tool_dims[1]:.3f} × {tool_dims[2]:.3f} mm`",
        "",
        "## Mold architecture",
        "",
        f"- Architecture: **{m['architecture']}**",
        f"- Planned parts: **{m.get('planned_parts', 'to determine')}**",
        f"- Split axis/topology: **{m.get('split_axis', 'to determine')}**",
        f"- Parting strategy: {m['parting_strategy']}",
        f"- Interfaces: {', '.join(flags) if flags else 'no special fill/drain interfaces selected'}",
        f"- Nominal shell/rib: `{m.get('shell_mm')} / {m.get('rib_mm')} mm`",
        f"- Key clearance: `{m.get('key_clearance_mm')} mm` (calibrate physically)",
        "",
        "## Detail and compute budget",
        "",
        f"- Smallest intended feature: **{d['smallest_feature_mm']} mm**",
        f"- Relief depth: **{d.get('relief_depth_mm')} mm**",
        f"- Placement: **{d.get('placement', 'not specified')}**",
        f"- Continuous mapping required: **{d.get('continuous_mapping', False)}**",
        f"- {memory_summary(spec)}",
        "",
        "## Execution sequence",
        ""
    ]
    lines.extend(f"{idx}. {step}" for idx, step in enumerate(steps, start=1))
    lines.extend(["", "## Guardrails and unresolved risks", ""])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No automatic stop condition detected; manual demolding and material validation are still required.")
    lines.extend(["", "## Acceptance criteria", ""])
    lines.extend(f"- {item}" for item in spec["validation"]["acceptance"])
    lines.extend(["", "## Required package outputs", "", "- Source and immutable original checksum", "- Mold-part CAD/mesh exports and exploded assembly", "- JSON manifest with dimensions, scale, part IDs, pull vectors, and tolerances", "- Slicer profile/critical settings", "- Coupon and trial results", "- Casting, demolding, cleaning, drying, storage, and retirement instructions", ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="JSON mold specification")
    parser.add_argument("--output", type=Path, help="Write Markdown plan; otherwise print to stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        source = args.spec.expanduser().resolve()
        data = json.loads(source.read_text(encoding="utf-8"))
        plan = generate_plan(data, source)
        if args.output:
            out = args.output.expanduser().resolve()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(plan + "\n", encoding="utf-8")
            print(out)
        else:
            print(plan)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
