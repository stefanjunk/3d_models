#!/usr/bin/env python3
"""Conservative print-vs-buy screen for power transmission components."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=("gear", "rack", "belt", "chain", "pulley", "sprocket"), required=True)
    parser.add_argument("--speed-class", choices=("low", "medium", "high"), required=True)
    parser.add_argument("--load-class", choices=("low", "medium", "high"), required=True)
    parser.add_argument("--life-class", choices=("prototype", "intermittent", "continuous"), required=True)
    parser.add_argument("--scale", choices=("small", "large"), required=True)
    args = parser.parse_args()

    always_buy = args.type in {"belt", "chain"}
    demanding = (
        args.speed_class == "high"
        or args.load_class == "high"
        or args.life_class == "continuous"
        or args.scale == "small"
    )
    print_candidate = (
        args.type in {"gear", "rack", "pulley", "sprocket"}
        and args.speed_class == "low"
        and args.load_class == "low"
        and args.life_class in {"prototype", "intermittent"}
        and args.scale == "large"
    )

    if always_buy or demanding or not print_candidate:
        decision = "BUY_STANDARD_COMPONENT"
        required_tests = ["assembly_alignment", "purchased_component_verification"]
        code = 0
    else:
        decision = "PRINT_CANDIDATE_NEEDS_TEST"
        required_tests = [
            "tooth_fidelity",
            "backlash",
            "torque_test",
            "wear_test",
            "life_test",
            "lubrication_and_temperature_review",
        ]
        code = 1

    report = {
        "decision": decision,
        "inputs": vars(args),
        "required_tests": required_tests,
        "limitations": [
            "screening classes do not replace numeric gear or belt calculations",
            "does not establish tooth strength, contact stress, thermal behavior, or safety factor",
        ],
    }
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
