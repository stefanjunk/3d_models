#!/usr/bin/env python3
"""Exercise the fail-closed NameForm split planner without generating CAD."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import nameform_letter_only as nf


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def success_case(name: str, expected_left: str, expected_right: str) -> dict:
    plan = nf.automatic_pair_plan(name)
    passed = (
        plan.left_text == expected_left
        and plan.right_text == expected_right
        and nf.estimated_part_width(nf.packed_width(plan.left_text)) <= nf.MAX_PART_X
        and nf.estimated_part_width(nf.packed_width(plan.right_text)) <= nf.MAX_PART_X
    )
    return {
        "name": name,
        "expected": "PASS",
        "actual": "PASS" if passed else "FAIL",
        "selected_split": [plan.left_text, plan.right_text],
        "expected_split": [expected_left, expected_right],
        "plan": plan.as_report(),
    }


def failure_case(name: str, expected_message: str) -> dict:
    try:
        plan = nf.automatic_pair_plan(name)
    except ValueError as exc:
        message = str(exc)
        passed = expected_message in message
        return {
            "name": name,
            "expected": "FAIL_CLOSED",
            "actual": "PASS" if passed else "FAIL",
            "message": message,
            "expected_message_fragment": expected_message,
        }
    return {
        "name": name,
        "expected": "FAIL_CLOSED",
        "actual": "FAIL",
        "message": "planner unexpectedly accepted the input",
        "selected_plan": plan.as_report(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    if args.json_out.exists():
        raise FileExistsError(f"refusing to overwrite report: {args.json_out}")
    cases = [
        success_case("STEFAN", "STE", "FAN"),
        success_case("MARITA", "MA", "RITA"),
        success_case("ANNA", "AN", "NA"),
        success_case("MIA", "M", "IA"),
        failure_case("ALEXANDER", "cannot fit"),
        failure_case("Marita", "unsupported character"),
        failure_case("ANNA MARIA", "unsupported character"),
    ]
    explicit = nf.explicit_pair_plan("MA", "RITA")
    cases.append(
        {
            "name": "explicit MA | RITA",
            "expected": "PASS",
            "actual": "PASS"
            if (explicit.left_text, explicit.right_text) == ("MA", "RITA")
            else "FAIL",
            "plan": explicit.as_report(),
        }
    )
    source_paths = [Path(__file__).resolve(), Path(nf.__file__).resolve(), nf.FONT_PATH]
    payload = {
        "schema_version": "1.0",
        "tool": "NameForm parametric plan sweep",
        "tool_version": nf.REVISION,
        "status": "PASS" if all(case["actual"] == "PASS" for case in cases) else "FAIL",
        "inputs": [
            {
                "path": str(path.relative_to(nf.REPO_ROOT)),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in source_paths
        ],
        "cases": cases,
        "limits": {
            "cap_height_mm": nf.CAP_HEIGHT,
            "maximum_part_x_mm": nf.MAX_PART_X,
            "supported_scope": "uppercase single-name variants; explicit uppercase halves",
            "fail_closed_scope": "lowercase, spaces, missing glyphs, and names that do not fit at fixed cap height",
        },
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
