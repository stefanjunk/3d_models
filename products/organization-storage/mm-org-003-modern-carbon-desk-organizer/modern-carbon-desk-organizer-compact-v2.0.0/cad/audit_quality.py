#!/usr/bin/env python3
"""Reproduce the MM-ORG-003 draft.1 to draft.2 quality audit from STEP masters."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cadquery as cq
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "exports" / "master"
OUTPUT = ROOT / "validation" / "quality-audit-draft.1-to-draft.2.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def step(stem: str, revision: str) -> tuple[Path, cq.Shape]:
    path = MASTER / f"{stem}-{revision}.step"
    return path, cq.importers.importStep(str(path)).val()


def inside(shape: cq.Shape, points: list[tuple[float, float, float]]) -> list[bool]:
    return [bool(shape.isInside(cq.Vector(*point))) for point in points]


def main() -> None:
    stems = {
        "housing": "DRAFT-MM-ORG-003-compact-housing",
        "drawer": "DRAFT-MM-ORG-003-compact-drawer-print-twice",
        "sorter": "DRAFT-MM-ORG-003-compact-top-sorter",
        "texture_coupon": "DRAFT-MM-ORG-003-compact-texture-coupon",
    }
    models: dict[str, dict[str, cq.Shape]] = {"2.0.0-draft.1": {}, "2.0.0-draft.2": {}}
    inputs = []
    for revision in models:
        for name, stem in stems.items():
            path, shape = step(stem, revision)
            models[revision][name] = shape
            inputs.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    housing_points = [
        (3.3, 187.3, 27.75),
        (206.7, 187.3, 27.75),
        (3.3, 187.3, 80.25),
        (206.7, 187.3, 80.25),
    ]
    sorter_points = [
        (3.5, 3.5, 32.5),
        (206.5, 3.5, 32.5),
        (3.5, 186.5, 32.5),
        (206.5, 186.5, 32.5),
    ]

    old = models["2.0.0-draft.1"]
    new = models["2.0.0-draft.2"]
    old_collision_y0 = float(
        old["housing"].intersect(old["drawer"].translate((3.45, 0.0, 3.25))).Volume()
    )
    old_collision_preview = float(
        old["housing"].intersect(old["drawer"].translate((3.45, 0.6, 3.25))).Volume()
    )
    positions = np.linspace(-181.9, 0.0, 9)
    new_collision = [
        float(new["housing"].intersect(new["drawer"].translate((3.45, float(y), 3.25))).Volume())
        for y in positions
    ]
    seated_sorter = new["sorter"].translate((0.0, 0.0, 108.0))
    stack_collision = float(new["housing"].intersect(seated_sorter).Volume())
    old_coupon_box = old["texture_coupon"].BoundingBox()
    new_coupon_box = new["texture_coupon"].BoundingBox()

    checks = [
        {
            "id": "baseline-defect-reproduced",
            "status": "PASS" if old_collision_y0 > 0 and old_collision_preview > old_collision_y0 else "FAIL",
            "required": True,
            "message": "Draft.1 drawer/housing overlap is reproduced from immutable STEP masters.",
            "metrics": {
                "intersection_y0_mm3": old_collision_y0,
                "intersection_old_preview_y0_6_mm3": old_collision_preview,
            },
        },
        {
            "id": "housing-rear-corners",
            "status": "PASS" if not any(inside(old["housing"], housing_points)) and all(inside(new["housing"], housing_points)) else "FAIL",
            "required": True,
            "message": "All four housing rear-corner probes change from void in draft.1 to material in draft.2.",
            "metrics": {
                "points_mm": housing_points,
                "draft_1_inside": inside(old["housing"], housing_points),
                "draft_2_inside": inside(new["housing"], housing_points),
            },
        },
        {
            "id": "sorter-corners",
            "status": "PASS" if not any(inside(old["sorter"], sorter_points)) and all(inside(new["sorter"], sorter_points)) else "FAIL",
            "required": True,
            "message": "All four sorter containment-corner probes change from void in draft.1 to material in draft.2.",
            "metrics": {
                "points_mm": sorter_points,
                "draft_1_inside": inside(old["sorter"], sorter_points),
                "draft_2_inside": inside(new["sorter"], sorter_points),
            },
        },
        {
            "id": "drawer-full-travel",
            "status": "PASS" if max(new_collision) <= 1e-6 else "FAIL",
            "required": True,
            "message": "Draft.2 drawer has zero B-Rep intersection at nine full-travel samples.",
            "metrics": {
                "positions_mm": [float(value) for value in positions],
                "intersection_volumes_mm3": new_collision,
                "maximum_mm3": max(new_collision),
            },
        },
        {
            "id": "sorter-seat",
            "status": "PASS" if stack_collision <= 1e-6 else "FAIL",
            "required": True,
            "message": "Draft.2 sorter seats without unintended B-Rep intersection.",
            "metrics": {"intersection_mm3": stack_collision},
        },
        {
            "id": "finger-scoop",
            "status": "PASS"
            if old["drawer"].isInside(cq.Vector(101.55, 1.6, 48.0))
            and not new["drawer"].isInside(cq.Vector(101.55, -1.6, 48.0))
            else "FAIL",
            "required": True,
            "message": "The old fascia retained material at the scoop probe; draft.2 removes it.",
            "metrics": {
                "draft_1_probe_inside": bool(old["drawer"].isInside(cq.Vector(101.55, 1.6, 48.0))),
                "draft_2_probe_inside": bool(new["drawer"].isInside(cq.Vector(101.55, -1.6, 48.0))),
            },
        },
        {
            "id": "vertical-texture-coupon",
            "status": "PASS" if old_coupon_box.ylen > old_coupon_box.zlen and new_coupon_box.zlen > new_coupon_box.ylen else "FAIL",
            "required": True,
            "message": "Draft.2 changes the coupon from a flat plate to a representative vertical product wall.",
            "metrics": {
                "draft_1_extents_mm": [old_coupon_box.xlen, old_coupon_box.ylen, old_coupon_box.zlen],
                "draft_2_extents_mm": [new_coupon_box.xlen, new_coupon_box.ylen, new_coupon_box.zlen],
            },
        },
    ]
    payload = {
        "schema_version": "1.0",
        "tool": "MM-ORG-003-quality-audit",
        "tool_version": "1.0.0",
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "profile": "corrective-digital-draft",
        "inputs": inputs,
        "checks": checks,
        "limitations": [
            "STEP/B-Rep checks qualify digital geometry only.",
            "Nominal 0.45 mm drawer clearance remains unqualified for the exact printing process.",
            "Carbon appearance, tactility and snagging require the vertical-wall coupon under controlled lighting.",
            "Exact slicer and G-code evidence are not available without a complete destination profile set.",
        ],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report": str(OUTPUT)}, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
