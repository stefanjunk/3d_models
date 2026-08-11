#!/usr/bin/env python3
"""Generate a conservative starting print profile from material, nozzle, and use."""
from __future__ import annotations

import argparse
import json
import math

from common import clamp, load_data


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--material", default="petg")
    p.add_argument("--nozzle", type=float, choices=[0.4, 0.6, 0.8], default=0.6)
    p.add_argument("--intent", choices=["detail", "balanced", "fast"], default="balanced")
    p.add_argument("--load", choices=["cosmetic", "light", "functional", "structural"], default="functional")
    p.add_argument("--part-size", choices=["small", "medium", "large"], default="medium")
    p.add_argument("--layer", type=float)
    p.add_argument("--speed", type=float, default=45.0, help="Requested print speed mm/s for flow estimate")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    mats = load_data("materials.yaml")["materials"]
    if args.material not in mats:
        raise SystemExit(f"Unknown material '{args.material}'. See data/materials.yaml")
    m = mats[args.material]
    nozzle_data = load_data("nozzles.yaml")["nozzles"][f"{args.nozzle:.1f}"]

    fraction = {"detail": 0.35, "balanced": 0.50, "fast": 0.66}[args.intent]
    layer = args.layer if args.layer is not None else args.nozzle * fraction
    layer = round(clamp(layer, nozzle_data["layer_min_mm"], min(nozzle_data["layer_max_normal_mm"], args.nozzle * 0.75)), 3)
    line_width = float(nozzle_data["line_width_default_mm"])

    perimeters = {"cosmetic": 2, "light": 3, "functional": 4, "structural": 5}[args.load]
    if args.nozzle == 0.8 and args.load in {"functional", "structural"}:
        perimeters = max(3, perimeters - 1)
    shell_mm = round(perimeters * line_width, 2)

    top_bottom_mm = {"cosmetic": 0.8, "light": 1.0, "functional": 1.2, "structural": 1.6}[args.load]
    top_bottom_layers = max(3, math.ceil(top_bottom_mm / layer))
    infill = {"cosmetic": 10, "light": 15, "functional": 25, "structural": 35}[args.load]
    if args.part_size == "large":
        infill = max(10, infill - 5)

    flow = round(line_width * layer * args.speed, 2)
    notes = [
        "Orient primary loads to avoid interlayer peel.",
        "Use local solid modifiers/ribs around fasteners rather than globally extreme infill.",
        "Inspect every layer in the slicer and retain the 3MF project/profile identity.",
    ]
    if m.get("abrasive"):
        notes.append("Use an abrasion-resistant nozzle; verify supplier minimum nozzle diameter.")
    if args.nozzle < float(m.get("min_nozzle_mm", 0.4)):
        notes.append(f"Selected nozzle is below the material dataset starting minimum ({m.get('min_nozzle_mm')} mm).")
    if m.get("drying") == "required":
        notes.append("Dry and print from a controlled dry path to supplier guidance.")
    if m.get("enclosure") in {"required", "industrial-heated"}:
        notes.append(f"Enclosure requirement: {m.get('enclosure')}.")
    if args.material.startswith("tpu") or args.material == "tpu-soft":
        notes.append("Reduce acceleration/retraction and print substantially slower than the generic flow estimate.")

    result = {
        "material": args.material,
        "nozzle_mm": args.nozzle,
        "layer_height_mm": layer,
        "line_width_mm": line_width,
        "perimeters": perimeters,
        "nominal_shell_thickness_mm": shell_mm,
        "top_layers": top_bottom_layers,
        "bottom_layers": top_bottom_layers,
        "infill_percent_start": infill,
        "infill_pattern_start": "gyroid-or-cubic",
        "requested_speed_mm_s": args.speed,
        "estimated_requested_flow_mm3_s": flow,
        "temperature_source": "Use exact supplier/printer profile; broad dataset range is not a final setting.",
        "broad_process_range": {"nozzle_c": m.get("typical_nozzle_c"), "bed_c": m.get("typical_bed_c")},
        "notes": notes,
        "warning": "Starting profile only. Calibrate flow, dimensions, bridges, cooling, and maximum volumetric speed on the exact machine/material/nozzle.",
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            if key != "notes":
                print(f"{key}: {value}")
        print("notes:")
        for note in notes:
            print(f"  - {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
