#!/usr/bin/env python3
"""Create a personalized MM-PER-001 v0.3.0 DRAFT pair.

Marked output is the default because both independently distributed parts need
the product-specific metriMade identity. This script never slices, uploads, or
starts a print.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source" / "v0.3.0"
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_v030 as package  # noqa: E402
import nameform_bookends as nb  # noqa: E402


def safe_slug(left: str, right: str) -> str:
    value = f"{left}-{right}".replace(" ", "_").replace("'", "")
    value = re.sub(r"[^0-9A-Za-zÄÖÜäöüẞß_-]+", "-", value)
    return value.strip("-_") or "pair"


def plan_payload(plan: nb.PairText) -> dict:
    return {
        "status": "PLAN_PASS",
        "product_id": nb.PRODUCT_ID,
        "revision": nb.REVISION,
        "text": asdict(plan),
        "part_envelope_mm": [
            nb.WING_W + nb.FOOT_L,
            nb.SIDE_DEPTH + nb.TEXT_RAISE,
            nb.TOTAL_H,
        ],
        "manufacturing_state": "DRAFT — exact slicer and physical tests pending",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--name", default=nb.DEFAULT_NAME,
        help="whole input name; automatically width-balanced across the pair",
    )
    parser.add_argument("--left-text", help="explicit text for the left part")
    parser.add_argument("--right-text", help="explicit text for the right part")
    parser.add_argument(
        "--same-on-both", action="store_true",
        help="put the complete --name on both parts",
    )
    parser.add_argument(
        "--plan-only", action="store_true",
        help="validate and show the split without building CAD",
    )
    parser.add_argument(
        "--out-dir", type=Path,
        help="output directory; required unless --plan-only is used",
    )
    parser.add_argument("--assembly-gap", type=float, default=240.0)
    parser.add_argument(
        "--unmarked-master", action="store_true",
        help="engineering-only output without the mandatory product mark",
    )
    args = parser.parse_args()

    try:
        plan = nb.pair_text(
            args.name, args.left_text, args.right_text, args.same_on_both
        )
    except (ValueError, FileNotFoundError, AssertionError) as exc:
        parser.error(str(exc))

    payload = plan_payload(plan)
    if args.plan_only:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0
    if args.out_dir is None:
        parser.error("--out-dir is required unless --plan-only is used")
    if args.assembly_gap <= 0:
        parser.error("--assembly-gap must be positive")

    slug = safe_slug(plan.left, plan.right)
    label = "MASTER" if args.unmarked_master else "DRAFT"
    prefix = f"{label}-nameform-{slug}"
    targets = {
        "left_step": args.out_dir / f"{prefix}-left.step",
        "left_stl": args.out_dir / f"{prefix}-left.stl",
        "left_3mf": args.out_dir / f"{prefix}-left.3mf",
        "right_step": args.out_dir / f"{prefix}-right.step",
        "right_stl": args.out_dir / f"{prefix}-right.stl",
        "right_3mf": args.out_dir / f"{prefix}-right.3mf",
        "assembly_step": args.out_dir / f"{prefix}-assembly.step",
        "report": args.out_dir / f"{prefix}-report.json",
    }
    existing = [str(path) for path in targets.values() if path.exists()]
    if existing:
        parser.error("refusing to overwrite existing output(s): " + ", ".join(existing))

    left, right, plan = nb.build_pair(
        args.name,
        args.left_text,
        args.right_text,
        args.same_on_both,
        watermark=not args.unmarked_master,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    nb.export_step(left, targets["left_step"])
    nb.export_stl(left, targets["left_stl"])
    package.export_3mf(
        targets["left_stl"], targets["left_3mf"], "left", plan.left
    )
    nb.export_step(right, targets["right_step"])
    nb.export_stl(right, targets["right_stl"])
    package.export_3mf(
        targets["right_stl"], targets["right_3mf"], "right", plan.right
    )
    nb.export_assembly(left, right, args.assembly_gap, targets["assembly_step"])

    payload.update({
        "status": "DRAFT_DIGITAL_GEOMETRY_BUILT",
        "watermark": (
            "omitted — engineering master"
            if args.unmarked_master
            else "MM-WM-001-R1 recessed on both parts"
        ),
        "geometry": nb.report(left, right, plan),
        "artifacts": {
            key: {
                "path": str(path.resolve()),
                "sha256": package.sha256(path),
                "bytes": path.stat().st_size,
            }
            for key, path in targets.items()
            if key != "report"
        },
        "required_next_checks": [
            "validate the two 3MF packages",
            "run the exact slicer/profile and inspect thin text/first layer",
            "print and approve the watermark coupon",
            "run test-plan.yaml on the unchanged pair",
        ],
    })
    targets["report"].write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
