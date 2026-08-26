#!/usr/bin/env python3
"""Validate placement of an exact generated metriMade.com watermark profile."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


ASSET_REVISION = "MM-WM-001-R1"
DOMAIN = "metriMade.com"


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def load_metadata(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read generated watermark metadata: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("generated watermark metadata must be a JSON object")
    return data


def expected_artifacts(metadata_path: Path, depth: float) -> list[Path]:
    stem = metadata_path.stem
    depth_code = int(round(depth * 100))
    return [
        metadata_path.with_name(f"{stem}.svg"),
        metadata_path.with_name(f"{stem}.dxf"),
        metadata_path.with_name(f"{stem}.scad"),
        metadata_path.with_name(f"{stem}.png"),
        metadata_path.with_name(f"{stem}-icon-source.svg"),
        metadata_path.with_name(f"{stem}-cutter-d{depth_code:03d}.stl"),
        metadata_path.with_name(f"{stem}-coupon-d{depth_code:03d}.stl"),
        metadata_path.with_name("manifest.sha256"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--surface-width", type=positive, required=True)
    parser.add_argument("--surface-height", type=positive, required=True)
    parser.add_argument("--host-wall", type=positive, required=True)
    parser.add_argument("--nozzle", type=positive, default=0.4)
    parser.add_argument("--layer-height", type=positive, default=0.2)
    parser.add_argument("--edge-clearance", type=positive)
    parser.add_argument("--json-out")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    metadata_path = args.metadata.resolve()
    try:
        metadata = load_metadata(metadata_path)
    except ValueError as error:
        metadata = {}
        errors.append(str(error))

    if metadata.get("asset_revision") != ASSET_REVISION:
        errors.append(f"metadata asset_revision must be {ASSET_REVISION}")
    if metadata.get("domain") != DOMAIN:
        errors.append(f"metadata domain must be {DOMAIN}")
    product_id = metadata.get("product_id")
    version = metadata.get("version")
    expected_visible = [DOMAIN, f"{product_id} · v{version}"]
    if metadata.get("visible_text") != expected_visible:
        errors.append("metadata visible_text must exactly match domain, product ID, and version")
    digital = metadata.get("digital_validation")
    if not isinstance(digital, dict) or digital.get("result") != "PASS":
        errors.append("generated watermark metadata must contain a digital_validation PASS")

    envelope = metadata.get("layout_envelope_mm")
    if (
        not isinstance(envelope, list)
        or len(envelope) != 3
        or not all(isinstance(value, (int, float)) and value > 0 for value in envelope)
    ):
        errors.append("metadata layout_envelope_mm must contain width, height, and depth")
        profile_width = profile_height = depth = 0.0
    else:
        profile_width, profile_height, depth = map(float, envelope)

    if depth and not 0.4 <= depth <= 0.8:
        errors.append("generated recess depth must remain between 0.40 and 0.80 mm")
    if depth and depth < args.layer_height:
        errors.append("recess depth is smaller than one layer and may disappear in slicing")
    elif depth and depth < 2.0 * args.layer_height:
        warnings.append("recess spans fewer than two nominal layers; inspect exact slicer paths")
    if depth:
        layer_count = depth / args.layer_height
        if not math.isclose(layer_count, round(layer_count), rel_tol=0.0, abs_tol=1e-6):
            warnings.append("recess depth is not an integer multiple of layer height")

    missing_artifacts = [str(path) for path in expected_artifacts(metadata_path, depth) if not path.is_file()] if depth else []
    if missing_artifacts:
        errors.append("generated package is incomplete: " + ", ".join(missing_artifacts))

    edge_clearance = round(args.edge_clearance or max(2.0, 2.0 * args.nozzle), 6)
    feature_clearance = round(max(3.0, 4.0 * args.nozzle), 6)
    safe_width = args.surface_width - 2.0 * edge_clearance
    safe_height = args.surface_height - 2.0 * edge_clearance
    minimum_host_wall = round(max(1.2, depth + 0.8), 6) if depth else 1.2
    if args.host_wall < minimum_host_wall:
        errors.append(
            f"host wall {args.host_wall:.3f} mm is below the required {minimum_host_wall:.3f} mm"
        )
    if safe_width <= 0 or safe_height <= 0:
        errors.append("edge clearance consumes the candidate surface")

    choices: list[tuple[int, float, float, float]] = []
    if profile_width and profile_height and safe_width > 0 and safe_height > 0:
        for rotation, width, height in (
            (0, profile_width, profile_height),
            (90, profile_height, profile_width),
        ):
            if width <= safe_width and height <= safe_height:
                margin = min(safe_width - width, safe_height - height)
                choices.append((rotation, width, height, margin))

    selection: dict[str, object] | None = None
    if choices:
        rotation, width, height, _ = max(choices, key=lambda item: (item[3], -item[0]))
        selection = {
            "rotation_deg": rotation,
            "uniform_scale": 1.0,
            "actual_envelope_mm": [round(width, 4), round(height, 4)],
            "depth_mm": round(depth, 4),
            "metadata": str(metadata_path),
            "generated_directory": str(metadata_path.parent),
        }
    elif profile_width and profile_height and safe_width > 0 and safe_height > 0:
        errors.append(
            "exact generated profile does not fit; use a larger safe region, another surface, or revise the product geometry"
        )

    if args.nozzle != 0.4 or args.layer_height != 0.2:
        warnings.append(
            "process differs from the 0.40 mm nozzle / 0.20 mm layer reference; pass a generated physical coupon before release"
        )
    physical_status = digital.get("physical_test") if isinstance(digital, dict) else None
    if physical_status != "PASS":
        warnings.append("generated profile remains physically unqualified until the intended-process coupon passes")

    result = {
        "status": "PASS" if not errors and selection else "BLOCK",
        "asset_id": ASSET_REVISION,
        "brand": "metriMade",
        "domain": DOMAIN,
        "product_id": product_id,
        "version": version,
        "operation": "recessed",
        "preferred_surface": "flat-nonfunctional-low-stress-underside",
        "candidate_surface_mm": [args.surface_width, args.surface_height],
        "safe_rectangle_mm": [round(max(0.0, safe_width), 4), round(max(0.0, safe_height), 4)],
        "edge_clearance_mm": edge_clearance,
        "recommended_feature_clearance_mm": feature_clearance,
        "minimum_host_wall_mm": minimum_host_wall,
        "minimum_remaining_wall_mm": 0.8,
        "residual_host_wall_mm": round(args.host_wall - depth, 4) if depth else None,
        "selection": selection,
        "orientation_check": "verify both identity lines directly on the exported finished underside",
        "physical_qualification": physical_status or "PENDING",
        "errors": errors,
        "warnings": warnings,
    }
    output = json.dumps(result, indent=2)
    if args.json_out:
        target = Path(args.json_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
