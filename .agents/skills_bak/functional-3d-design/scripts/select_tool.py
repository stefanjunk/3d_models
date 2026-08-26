#!/usr/bin/env python3
"""Score OpenSCAD, CadQuery, FreeCAD, and Blender for a design task."""
from __future__ import annotations

import argparse
import json

TOOLS = ["cadquery", "openscad", "freecad", "blender"]


def score_tools(args: argparse.Namespace) -> dict:
    score = {tool: 0.0 for tool in TOOLS}
    reasons = {tool: [] for tool in TOOLS}

    def add(tool: str, points: float, reason: str) -> None:
        score[tool] += points
        reasons[tool].append(reason)

    if args.input_kind in {"mesh", "scan", "glb", "obj", "stl"}:
        add("blender", 7, "mesh/scan input")
        add("freecad", -2, "dense mesh is not a natural B-Rep edit")
        add("cadquery", -3, "dense mesh is not a natural B-Rep edit")
    elif args.input_kind in {"step", "brep"}:
        add("cadquery", 5, "precise B-Rep input")
        add("freecad", 6, "interactive B-Rep editing")
    elif args.input_kind in {"svg", "dxf", "2d-profile"}:
        add("openscad", 5, "2D import/extrusion/relief")
        add("cadquery", 3, "precise profile-based solid")

    if args.geometry == "prismatic":
        add("cadquery", 5, "functional prismatic geometry")
        add("openscad", 4, "simple CSG and extrusions")
    elif args.geometry == "mixed":
        add("cadquery", 4, "mixed functional geometry")
        add("freecad", 3, "interactive mixed CAD")
        add("blender", 2, "organic details")
    elif args.geometry == "organic":
        add("blender", 8, "organic/sculpted geometry")
        add("freecad", 1, "possible surface workflow")
        add("openscad", -3, "organic offsets and local edits are difficult")

    if args.precision == "high":
        add("cadquery", 6, "high dimensional precision")
        add("freecad", 5, "high dimensional precision")
        add("blender", -2, "mesh workflow needs extra dimensional checks")
    elif args.precision == "medium":
        add("cadquery", 3, "moderate dimensional precision")
        add("openscad", 2, "parameterized dimensions")
        add("freecad", 2, "interactive dimensions")

    if args.needs_step:
        add("cadquery", 7, "STEP master required")
        add("freecad", 7, "STEP master required")
        add("openscad", -5, "no native precise STEP master")
        add("blender", -5, "mesh-first, not a precise STEP master")
    if args.needs_fem:
        add("freecad", 9, "FEM workbench/solver workflow")
        add("cadquery", 2, "good STEP source for FEM")
    if args.heavy_texture:
        add("blender", 6, "dense relief/texture")
        add("openscad", 2, "2D relief can be simple")
        add("cadquery", -2, "dense texture booleans can be expensive")
    if args.large_pattern:
        add("openscad", 4, "compact arrays/patterns")
        add("blender", 3, "geometry nodes/mesh repetition")
        add("cadquery", -1, "very high feature counts can burden B-Rep")
    if args.gui:
        add("freecad", 4, "interactive CAD GUI requested")
        add("blender", 4, "interactive mesh GUI requested")
    if args.language == "python":
        add("cadquery", 3, "Python-native")
        add("blender", 2, "Python automation")
        add("freecad", 2, "Python console/API")
    elif args.language == "scad":
        add("openscad", 6, "SCAD preference")

    ranked = sorted(TOOLS, key=lambda t: score[t], reverse=True)
    primary, secondary = ranked[:2]
    hybrid = None
    if primary == "blender" and (args.needs_step or args.precision == "high"):
        hybrid = "Use CadQuery/FreeCAD for precise interfaces and Blender for organic mesh operations."
    elif primary in {"cadquery", "freecad"} and args.heavy_texture:
        hybrid = "Keep precise CAD as master; apply dense noncritical relief in Blender or an implicit mesh stage."
    elif args.needs_fem and primary != "freecad":
        hybrid = "Export STEP and use FreeCAD FEM for analysis."

    return {
        "primary": primary,
        "secondary": secondary,
        "scores": score,
        "reasons": reasons,
        "hybrid_advice": hybrid,
        "warning": "Tool score is a routing aid; output formats, model condition, and team skills can override it.",
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-kind", default="none", choices=["none", "step", "brep", "mesh", "scan", "stl", "obj", "glb", "svg", "dxf", "2d-profile"])
    p.add_argument("--geometry", default="mixed", choices=["prismatic", "mixed", "organic"])
    p.add_argument("--precision", default="medium", choices=["low", "medium", "high"])
    p.add_argument("--needs-step", action="store_true")
    p.add_argument("--needs-fem", action="store_true")
    p.add_argument("--heavy-texture", action="store_true")
    p.add_argument("--large-pattern", action="store_true")
    p.add_argument("--gui", action="store_true")
    p.add_argument("--language", default="any", choices=["any", "python", "scad", "gui"])
    p.add_argument("--json", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    result = score_tools(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Primary:   {result['primary']}")
        print(f"Secondary: {result['secondary']}")
        if result["hybrid_advice"]:
            print(f"Hybrid:    {result['hybrid_advice']}")
        print("Scores:")
        for tool, value in sorted(result["scores"].items(), key=lambda item: item[1], reverse=True):
            print(f"  {tool:10s} {value:5.1f}  - " + "; ".join(result["reasons"][tool]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
