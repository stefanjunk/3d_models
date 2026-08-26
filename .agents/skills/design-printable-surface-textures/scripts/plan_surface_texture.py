#!/usr/bin/env python3
"""Plan a compact, printable FDM surface-texture representation.

The script does not certify printability. It turns physical process inputs into a
repeatable first-pass method choice, uniform-heightfield worst-case estimate,
and coupon checklist using only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


PATTERNS = {
    "carbon-twill": {
        "primary": "vector-or-toolpath",
        "secondary": "material-or-finish",
        "avoid": "full-resolution photographic displacement over the whole patch",
        "repeating": True,
    },
    "wood-grain": {
        "primary": "vector-plus-localized-relief",
        "secondary": "material-or-fuzzy-wall",
        "avoid": "unfiltered photo heightmap over every visible face",
        "repeating": False,
    },
    "stone": {
        "primary": "procedural-low-frequency-relief",
        "secondary": "fuzzy-wall-or-material",
        "avoid": "uniformly triangulated high-frequency noise",
        "repeating": False,
    },
    "leather": {
        "primary": "procedural-cell-network-or-adaptive-relief",
        "secondary": "material-or-fuzzy-wall",
        "avoid": "micro-pore geometry below the extrusion scale",
        "repeating": False,
    },
    "hammered-metal": {
        "primary": "sparse-parametric-dimples",
        "secondary": "material-and-finish",
        "avoid": "dense grayscale displacement",
        "repeating": False,
    },
    "brushed-metal": {
        "primary": "directed-top-toolpaths",
        "secondary": "metallic-material-or-finish",
        "avoid": "modeled microscopic scratches",
        "repeating": True,
    },
    "fabric-weave": {
        "primary": "vector-or-toolpath",
        "secondary": "material-and-color",
        "avoid": "one mesh vertex per source-image pixel",
        "repeating": True,
    },
    "knurl": {
        "primary": "parametric-macro-geometry",
        "secondary": "toolpath-compatible-ribs",
        "avoid": "image engraving for a functional grip",
        "repeating": True,
    },
    "lotus": {
        "primary": "vector-relief-or-separate-lattice",
        "secondary": "multi-material-texture-skin",
        "avoid": "dense image displacement when petal boundaries are vectorizable",
        "repeating": False,
    },
    "custom-image": {
        "primary": "localized-adaptive-heightmap",
        "secondary": "vectorization-where-possible",
        "avoid": "unmasked uniform heightfield over the full object",
        "repeating": False,
    },
}

SURFACES = (
    "plane",
    "horizontal-top",
    "vertical-wall",
    "cylinder",
    "rounded-perimeter",
    "freeform",
)


def positive(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("value must be finite and greater than zero")
    return number


def size_mm(value: str) -> tuple[float, float]:
    try:
        left, right = value.lower().replace("×", "x").split("x", 1)
        width, height = positive(left), positive(right)
    except (ValueError, argparse.ArgumentTypeError) as exc:
        raise argparse.ArgumentTypeError("size must be WIDTHxHEIGHT in millimetres") from exc
    return width, height


def resolution_band(feature_mm: float | None, line_width_mm: float) -> dict[str, object]:
    if feature_mm is None:
        return {
            "band": "unspecified",
            "feature_to_line_width": None,
            "guidance": "Set the smallest required physical feature before detailed generation.",
        }
    ratio = feature_mm / line_width_mm
    if ratio < 0.75:
        band = "sub-path-optical"
        guidance = "Use material, color, gloss, coating, film, or bed imprint; do not model it as reliable geometry."
    elif ratio < 3.0:
        band = "path-scale"
        guidance = "Prefer slicer or authored extrusion paths and prove continuity on a coupon."
    else:
        band = "macro-geometry"
        guidance = "Use vector/procedural CAD; reserve heightmaps for irregular continuous local height."
    return {
        "band": band,
        "feature_to_line_width": round(ratio, 4),
        "guidance": guidance,
    }


def method_notes(pattern: str, surface: str, source: str) -> tuple[list[str], list[str]]:
    profile = PATTERNS[pattern]
    methods = [str(profile["primary"]), str(profile["secondary"])]
    warnings: list[str] = [f"Avoid: {profile['avoid']}."]

    if source in {"image", "concept-image"} and profile["repeating"]:
        warnings.append(
            "The source is a repeating image: derive a seamless vector/procedural tile before using continuous displacement."
        )
    if surface == "horizontal-top":
        methods.append("slicer-top-surface-pattern")
    elif surface == "vertical-wall":
        methods.append("localized-fuzzy-skin-candidate")
    elif surface in {"cylinder", "rounded-perimeter", "freeform"}:
        methods.append("surface-distance-mapped-vector-or-skin")
        warnings.append(
            "Ordinary slicer infill/top paths do not automatically follow a curved exterior; map in physical surface distance."
        )
    return list(dict.fromkeys(methods)), warnings


def build_plan(args: argparse.Namespace) -> dict[str, object]:
    width_mm, height_mm = args.patch_mm
    area_mm2 = width_mm * height_mm
    line_width_mm = args.line_width_mm or 1.1 * args.nozzle_mm
    pitch_mm = args.sample_pitch_mm or 0.5 * args.nozzle_mm
    estimated_triangles = math.ceil(2.0 * area_mm2 / (pitch_mm * pitch_mm))
    stop_limit = max(5_000_000, 5 * args.triangle_budget)
    if estimated_triangles <= args.triangle_budget:
        mesh_gate = "PASS"
    elif estimated_triangles <= stop_limit:
        mesh_gate = "REVIEW"
    else:
        mesh_gate = "STOP"

    band = resolution_band(args.smallest_feature_mm, line_width_mm)
    methods, warnings = method_notes(args.pattern, args.surface, args.source)
    relief_layers = None
    if args.relief_mm is not None:
        relief_layers = args.relief_mm / args.layer_height_mm
        if relief_layers < 0.5:
            warnings.append("Relief is below half a nominal layer; it may quantize away or become process noise.")
        if relief_layers > 5.0:
            warnings.append("Relief exceeds five nominal layers; review snagging, cleanability, wall reserve, and support behavior.")
    if mesh_gate != "PASS":
        warnings.append(
            "Uniform raster tessellation exceeds the portable target; crop/mask, vectorize, mesh adaptively, or simplify by physical error."
        )

    return {
        "schema_version": "1.0",
        "inputs": {
            "pattern": args.pattern,
            "source": args.source,
            "surface": args.surface,
            "patch_mm": [width_mm, height_mm],
            "nozzle_mm": args.nozzle_mm,
            "line_width_mm": round(line_width_mm, 5),
            "layer_height_mm": args.layer_height_mm,
            "smallest_feature_mm": args.smallest_feature_mm,
            "relief_mm": args.relief_mm,
        },
        "representation": {
            "resolution_band": band,
            "recommended_methods": methods,
            "motif_pitch_start_mm": [round(3 * line_width_mm, 4), round(8 * line_width_mm, 4)],
            "shallow_relief_start_mm": [
                round(0.5 * args.layer_height_mm, 4),
                round(2.0 * args.layer_height_mm, 4),
            ],
            "relief_in_nominal_layers": None if relief_layers is None else round(relief_layers, 4),
        },
        "uniform_heightfield_worst_case": {
            "displaced_area_mm2": round(area_mm2, 4),
            "sample_pitch_mm": round(pitch_mm, 5),
            "estimated_relief_triangles": estimated_triangles,
            "portable_pass_limit": args.triangle_budget,
            "portable_stop_limit": stop_limit,
            "gate": mesh_gate,
            "note": "This is a planning lower bound for a uniform grid, not a recommendation to build one.",
        },
        "integration": {
            "named_parts": ["CORE", "TEXTURE_SKIN"],
            "preserve_part_identity_until_slicing": True,
            "one_piece_print_rule": "Use a slicer-verified capture/overlap band when separate parts must fuse in place.",
            "project_rule": "Preserve common origin, transforms, part assignments, slicer version, and exact 3MF/project.",
        },
        "coupon": {
            "candidates": ["material-or-process", "vector-or-procedural", "localized-adaptive-heightmap", "custom-path-if-needed"],
            "hold_constant": ["printer", "nozzle", "material", "orientation", "profile", "lighting", "viewing-distance"],
            "inspect": ["toolpath-continuity", "short-segments", "bond-to-core", "appearance", "touch", "wear", "cleanability"],
        },
        "warnings": warnings,
    }


def as_markdown(plan: dict[str, object]) -> str:
    inputs = plan["inputs"]
    representation = plan["representation"]
    budget = plan["uniform_heightfield_worst_case"]
    lines = [
        "# Surface texture plan",
        "",
        f"- Pattern: `{inputs['pattern']}`",
        f"- Source: `{inputs['source']}`",
        f"- Surface: `{inputs['surface']}`",
        f"- Patch: `{inputs['patch_mm'][0]} × {inputs['patch_mm'][1]} mm`",
        f"- Resolution band: `{representation['resolution_band']['band']}` "
        f"({representation['resolution_band']['guidance']})",
        f"- Recommended methods: {', '.join(f'`{value}`' for value in representation['recommended_methods'])}",
        f"- Motif-pitch starting sweep: `{representation['motif_pitch_start_mm'][0]}–{representation['motif_pitch_start_mm'][1]} mm`",
        "",
        "## Uniform-heightfield worst case",
        "",
        f"- Sample pitch: `{budget['sample_pitch_mm']} mm`",
        f"- Estimated relief triangles: `{budget['estimated_relief_triangles']:,}`",
        f"- Gate: `{budget['gate']}`",
        f"- Note: {budget['note']}",
        "",
        "## Warnings",
        "",
    ]
    lines.extend(f"- {warning}" for warning in plan["warnings"])
    return "\n".join(lines) + "\n"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--pattern", choices=sorted(PATTERNS), required=True)
    result.add_argument(
        "--source",
        choices=("concept-image", "design-description", "image", "vector", "procedural", "authored-depth", "material"),
        required=True,
    )
    result.add_argument("--surface", choices=SURFACES, required=True)
    result.add_argument("--patch-mm", type=size_mm, required=True, metavar="WIDTHxHEIGHT")
    result.add_argument("--nozzle-mm", type=positive, required=True)
    result.add_argument("--line-width-mm", type=positive)
    result.add_argument("--layer-height-mm", type=positive, required=True)
    result.add_argument("--smallest-feature-mm", type=positive)
    result.add_argument("--relief-mm", type=positive)
    result.add_argument("--sample-pitch-mm", type=positive)
    result.add_argument("--triangle-budget", type=int, default=1_000_000)
    result.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    result.add_argument("--output", type=Path, help="Write the report to this path")
    return result


def main() -> int:
    args = parser().parse_args()
    if args.triangle_budget <= 0:
        print("error: --triangle-budget must be greater than zero", file=sys.stderr)
        return 2
    plan = build_plan(args)
    payload = json.dumps(plan, indent=2, sort_keys=True) + "\n" if args.json else as_markdown(plan)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
