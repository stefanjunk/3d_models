#!/usr/bin/env python3
"""Recommend print, buy, or hybrid for a component under explicit constraints."""
from __future__ import annotations

import argparse
import json

from common import load_data


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--component", required=True)
    p.add_argument("--mode", choices=["integrated-print", "balanced-hybrid", "standard-hardware"], default="balanced-hybrid")
    p.add_argument("--load", choices=["low", "medium", "high"], default="medium")
    p.add_argument("--precision", choices=["low", "medium", "high"], default="medium")
    p.add_argument("--cycles", choices=["one-time", "low", "medium", "high"], default="medium")
    p.add_argument("--speed", choices=["static", "low", "high"], default="static")
    p.add_argument("--safety-critical", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    rules = load_data("component-rules.yaml")["components"]
    if args.component not in rules:
        result = {
            "component": args.component,
            "recommendation": "research-hybrid",
            "reason": "Unknown component type; decompose required precision, load, wear, fatigue, certification, and commodity availability.",
        }
    else:
        r = rules[args.component]
        scores = {"print": 0, "buy": 0, "hybrid": 0}
        scores[r["default"]] += 4
        reasons = [f"rule default: {r['default']}"]

        mode_adjust = {
            "integrated-print": {"print": 3, "hybrid": 1, "buy": -1},
            "balanced-hybrid": {"hybrid": 3, "print": 0, "buy": 0},
            "standard-hardware": {"buy": 3, "hybrid": 2, "print": -2},
        }[args.mode]
        for k, v in mode_adjust.items():
            scores[k] += v

        if args.safety_critical:
            scores["buy"] += 8
            scores["hybrid"] += 4
            scores["print"] -= 10
            reasons.append("safety-critical favors rated purchased load-path components")
        if args.precision == "high":
            scores["buy"] += 5
            scores["hybrid"] += 3
            scores["print"] -= 3
            reasons.append("high precision")
        if args.load == "high":
            scores["buy"] += 4
            scores["hybrid"] += 3
            scores["print"] -= 2
            reasons.append("high load")
        if args.cycles == "high":
            scores["buy"] += 4
            scores["hybrid"] += 3
            scores["print"] -= 2
            reasons.append("high cycle count")
        if args.speed == "high":
            scores["buy"] += 5
            scores["hybrid"] += 2
            scores["print"] -= 4
            reasons.append("high speed/wear/balance")

        recommendation = max(scores, key=scores.get)
        result = {
            "component": args.component,
            "recommendation": recommendation,
            "scores": scores,
            "reasons": reasons,
            "print_benefits": r.get("print_benefits", []),
            "buy_when": r.get("buy_when", []),
            "hybrid_pattern": r.get("hybrid_pattern"),
            "warning": "This is a decision aid. Supplier ratings, actual loads, interfaces, and test evidence override the generic rule.",
        }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
