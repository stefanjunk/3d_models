#!/usr/bin/env python3
"""Filter and score broad filament families from the skill data set."""
from __future__ import annotations

import argparse
import json
from typing import Any

from common import load_data

HEAT_ORDER = {"low": 1, "moderate": 2, "moderate-high": 3, "high": 4, "very-high": 5, "extreme": 6, "polymer-dependent": 0, "not-service-material": -1}
LEVEL = {"poor": 0, "poor-fair": 1, "fair": 2, "medium": 2, "medium-high": 3, "good": 4, "high": 4, "very-high": 5, "extreme": 6, "low": 1, "low-medium": 2, "supplier-specific": 0, "polymer-dependent": 0, "not-applicable": 0, "water-soluble": -1}


def normalized_level(value: Any) -> int:
    return LEVEL.get(str(value), 0)


def heat_requirement(temp_c: float | None) -> int:
    if temp_c is None:
        return 0
    if temp_c <= 45:
        return 1
    if temp_c <= 70:
        return 2
    if temp_c <= 95:
        return 4
    if temp_c <= 130:
        return 5
    return 6


def score_material(mid: str, m: dict, args: argparse.Namespace) -> tuple[float, list[str], list[str]]:
    score = 0.0
    positives: list[str] = []
    cautions: list[str] = []

    if m.get("category") == "support" and not args.include_support:
        return -999, positives, cautions
    if args.max_printability and int(m.get("printability", 5)) > args.max_printability:
        return -999, positives, cautions
    if args.max_hotend and m.get("typical_nozzle_c", [0, 999])[0] > args.max_hotend:
        return -999, positives, cautions
    if not args.abrasive_ok and m.get("abrasive") is True:
        return -999, positives, cautions
    if args.no_enclosure and str(m.get("enclosure", "none")) in {"required", "industrial-heated"}:
        return -999, positives, cautions
    if args.no_drying and str(m.get("drying")) == "required":
        return -999, positives, cautions

    req_heat = heat_requirement(args.service_temperature)
    mat_heat = HEAT_ORDER.get(str(m.get("heat_class")), 0)
    if req_heat:
        if mat_heat >= req_heat:
            score += 5
            positives.append("heat class meets broad requirement")
        else:
            score -= 8
            cautions.append("heat class may be insufficient")

    if args.outdoor:
        uv = normalized_level(m.get("uv_class"))
        score += uv * 1.5
        if uv >= 4:
            positives.append("good outdoor/UV class")
        elif uv <= 1:
            cautions.append("poor outdoor/UV class")

    for flag, field, label in [
        (args.impact, "impact_class", "impact"),
        (args.fatigue, "fatigue_class", "fatigue"),
        (args.wear, "wear_class", "wear"),
        (args.chemical, "chemical_class", "chemical resistance"),
    ]:
        if flag:
            value = normalized_level(m.get(field))
            score += value * 1.5
            if value >= 4:
                positives.append(f"high {label} class")
            elif value <= 1:
                cautions.append(f"low {label} class")

    flex = str(m.get("flexibility"))
    if args.flexible:
        if flex in {"flexible", "very-flexible"}:
            score += 8
            positives.append("flexible")
        else:
            score -= 8
    if args.rigid:
        if flex == "rigid":
            score += 5
            positives.append("rigid")
        elif flex in {"flexible", "very-flexible"}:
            score -= 6

    score += max(0, 6 - int(m.get("printability", 5))) * 0.6
    if m.get("abrasive"):
        cautions.append("abrasion-resistant nozzle required")
    if m.get("drying") == "required":
        cautions.append("drying required")
    if m.get("enclosure") in {"required", "industrial-heated"}:
        cautions.append(f"enclosure: {m.get('enclosure')}")

    return score, positives, cautions


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--service-temperature", type=float, help="Approximate service temperature in C; broad filtering only")
    p.add_argument("--outdoor", action="store_true")
    p.add_argument("--impact", action="store_true")
    p.add_argument("--fatigue", action="store_true")
    p.add_argument("--wear", action="store_true")
    p.add_argument("--chemical", action="store_true")
    p.add_argument("--flexible", action="store_true")
    p.add_argument("--rigid", action="store_true")
    p.add_argument("--no-enclosure", action="store_true")
    p.add_argument("--no-drying", action="store_true")
    p.add_argument("--abrasive-ok", action="store_true")
    p.add_argument("--max-hotend", type=float)
    p.add_argument("--max-printability", type=int, choices=range(1, 6))
    p.add_argument("--include-support", action="store_true")
    p.add_argument("--top", type=int, default=8)
    p.add_argument("--json", action="store_true")
    return p


def main() -> int:
    args = parser().parse_args()
    materials = load_data("materials.yaml")["materials"]
    ranked = []
    for mid, m in materials.items():
        score, positives, cautions = score_material(mid, m, args)
        if score <= -900:
            continue
        ranked.append({
            "id": mid,
            "name": m["display_name"],
            "score": round(score, 2),
            "positives": positives,
            "cautions": cautions,
            "uses": m.get("uses", []),
            "printability": m.get("printability"),
            "process_range_note": {
                "nozzle_c": m.get("typical_nozzle_c"),
                "bed_c": m.get("typical_bed_c"),
            },
        })
    ranked.sort(key=lambda x: x["score"], reverse=True)
    result = {
        "recommendations": ranked[: args.top],
        "warning": "Broad family ranking only. Verify the exact filament datasheet, printer profile, conditioning, and printed test coupons.",
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in result["recommendations"]:
            print(f"{item['id']:18s} score={item['score']:5.1f}  {item['name']}")
            if item["positives"]:
                print("  + " + "; ".join(item["positives"]))
            if item["cautions"]:
                print("  ! " + "; ".join(item["cautions"]))
        print("\n" + result["warning"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
