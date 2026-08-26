#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def yes(value: str) -> bool:
    return value.lower() == "yes"


def route(args: argparse.Namespace) -> dict[str, Any]:
    reasons: list[str] = []
    companions = ["parametric-freeform-surfacing"]
    steps: list[str] = ["capture semantic parameters, hardpoints, continuity targets, and FDM acceptance"]

    if yes(args.protected_source) or args.input == "dense-ai-mesh":
        companions.append("organic-mesh-functionalization")
        reasons.append("The authoritative input is a dense/protected mesh, so source preservation and ROI controls are required.")

    if args.hardpoints == "exact" or args.step_required == "yes":
        companions.append("functional-3d-design")
        reasons.append("Exact hardpoints or STEP delivery require a B-Rep/functional-core responsibility.")

    if args.input in {"new-parametric", "cad-brep", "sketch-image", "scan-points"} and args.step_required == "yes":
        primary = "nurbs-brep-hybrid"
        steps += ["construct fair B-spline/NURBS guides and registered sections", "loft/network the aesthetic envelope in a B-Rep backend"]
        reasons.append("Editable freeform surfaces and neutral CAD exchange are both required.")
    elif args.input in {"clean-master-mesh", "dense-ai-mesh"} and yes(args.style_variants):
        primary = "subd-ffd-morph-hybrid"
        steps += ["retopologize or verify stable topology", "author a sparse SubD/FFD cage or morph targets", "protect/rebuild exact interfaces"]
        reasons.append("A good mesh master plus style variants is best served by cage/morph parameterization.")
    elif args.editability == "high":
        primary = "bspline-loft-hybrid"
        steps += ["build low-dimensional fair curves and semantic sections", "construct the envelope and expose controlled parameters"]
        reasons.append("High editability favors sparse curves/sections over opaque mesh smoothing.")
    else:
        primary = "subd-envelope"
        steps += ["shape a sparse quad control cage", "evaluate and validate the SubD surface"]
        reasons.append("Visual form dominates and exact B-Rep exchange was not requested.")

    if yes(args.local_blends):
        steps.append("apply local SDF/implicit blends only in declared transition regions")
        reasons.append("Local complex junctions can be blended implicitly without remeshing the full product.")
    if args.hardpoints == "exact":
        steps.append("regenerate and remeasure holes, axes, planes, seats, and clearances after freeform operations")
    steps += ["validate fairness/continuity and parameter extremes", "export with explicit tessellation controls and inspect slicer layers"]

    return {
        "primary_method": primary,
        "companions": sorted(set(companions)),
        "reasons": reasons,
        "workflow": steps,
        "warnings": [
            "Do not treat smooth shading as geometric evidence.",
            "Do not convert a dense mesh to a face-per-triangle B-Rep.",
            "Mark unavailable backend checks NOT_RUN rather than claiming success.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a freeform surface task to an appropriate representation strategy.")
    parser.add_argument("--input", choices=("new-parametric", "cad-brep", "clean-master-mesh", "dense-ai-mesh", "scan-points", "sketch-image"), required=True)
    parser.add_argument("--hardpoints", choices=("exact", "tolerant", "none"), default="exact")
    parser.add_argument("--editability", choices=("high", "medium", "low"), default="high")
    parser.add_argument("--style-variants", choices=("yes", "no"), default="yes")
    parser.add_argument("--local-blends", choices=("yes", "no"), default="no")
    parser.add_argument("--step-required", choices=("yes", "no"), default="no")
    parser.add_argument("--protected-source", choices=("yes", "no"), default="no")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    result = route(args)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
