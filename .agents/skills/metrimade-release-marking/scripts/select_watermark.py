#!/usr/bin/env python3
"""Select the most informative exact metriMade watermark tier that fits a safe region."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


SUPPORTED_ASSET_REVISIONS = {"MM-WM-001-R1", "MM-WM-001-R2"}
DOMAIN = "metriMade.com"
TIER_PRIORITY = {"full": 1, "compact": 2, "micro": 3}


def positive(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def load_metadata(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read generated watermark metadata {path}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError(f"generated watermark metadata must be a JSON object: {path}")
    return data


def resolve_metadata_paths(inputs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        candidate = raw.resolve()
        if candidate.is_file():
            paths.append(candidate)
        elif candidate.is_dir():
            matches = sorted(candidate.rglob("metrimade-watermark-*.json"))
            if not matches:
                raise ValueError(f"metadata directory contains no generated watermark JSON: {candidate}")
            paths.extend(path.resolve() for path in matches)
        else:
            raise ValueError(f"metadata input does not exist: {candidate}")
    return sorted(set(paths))


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


def expected_visible_text(asset_revision: str, tier: str, product_id: object, version: object) -> list[str]:
    if asset_revision == "MM-WM-001-R1" or tier == "full":
        return [DOMAIN, f"{product_id} · v{version}"]
    if tier == "compact":
        return [DOMAIN, str(product_id), f"v{version}"]
    return [str(product_id), f"v{version}"]


def validate_candidate(metadata_path: Path) -> tuple[dict[str, object], list[str]]:
    metadata = load_metadata(metadata_path)
    errors: list[str] = []
    asset_revision = metadata.get("asset_revision")
    if asset_revision not in SUPPORTED_ASSET_REVISIONS:
        errors.append(f"asset_revision must be one of {sorted(SUPPORTED_ASSET_REVISIONS)}")
    if metadata.get("domain") != DOMAIN:
        errors.append(f"controlled domain must be {DOMAIN}")

    product_id = metadata.get("product_id")
    version = metadata.get("version")
    tier = "full" if asset_revision == "MM-WM-001-R1" else metadata.get("layout_tier")
    if tier not in TIER_PRIORITY:
        errors.append(f"layout_tier must be one of {sorted(TIER_PRIORITY)}")
        tier = "full"
    priority = TIER_PRIORITY[tier]
    if asset_revision == "MM-WM-001-R2" and metadata.get("layout_priority") != priority:
        errors.append(f"layout_priority must be {priority} for {tier}")

    expected_visible = expected_visible_text(str(asset_revision), tier, product_id, version)
    if metadata.get("visible_text") != expected_visible:
        errors.append(f"visible_text must exactly match the {tier} identity contract")
    expected_domain_visible = tier != "micro"
    if asset_revision == "MM-WM-001-R2" and metadata.get("domain_visible") is not expected_domain_visible:
        errors.append(f"domain_visible must be {expected_domain_visible} for {tier}")

    digital = metadata.get("digital_validation")
    if not isinstance(digital, dict) or digital.get("result") != "PASS":
        errors.append("digital_validation must contain PASS")
        digital = {}

    envelope = metadata.get("layout_envelope_mm")
    if (
        not isinstance(envelope, list)
        or len(envelope) != 3
        or not all(isinstance(value, (int, float)) and value > 0 for value in envelope)
    ):
        errors.append("layout_envelope_mm must contain width, height, and depth")
        width = height = depth = 0.0
    else:
        width, height, depth = map(float, envelope)
    if depth and not 0.4 <= depth <= 0.8:
        errors.append("recess depth must remain between 0.40 and 0.80 mm")

    if depth:
        missing = [str(path) for path in expected_artifacts(metadata_path, depth) if not path.is_file()]
        if missing:
            errors.append("generated package is incomplete: " + ", ".join(missing))

    return {
        "asset_revision": asset_revision,
        "product_id": product_id,
        "version": version,
        "tier": tier,
        "priority": priority,
        "domain_visible": expected_domain_visible,
        "visible_text": expected_visible,
        "profile_width_mm": width,
        "profile_height_mm": height,
        "depth_mm": depth,
        "physical_test": digital.get("physical_test") or "PENDING",
        "metadata_path": metadata_path,
    }, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--metadata",
        type=Path,
        action="append",
        required=True,
        help="Generated metadata JSON or directory; repeat to supply multiple tiers.",
    )
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
    candidates: list[dict[str, object]] = []
    try:
        metadata_paths = resolve_metadata_paths(args.metadata)
    except ValueError as error:
        metadata_paths = []
        errors.append(str(error))

    for path in metadata_paths:
        try:
            candidate, candidate_errors = validate_candidate(path)
        except ValueError as error:
            errors.append(str(error))
            continue
        candidates.append(candidate)
        errors.extend(f"{path}: {message}" for message in candidate_errors)

    identities = {
        (candidate["asset_revision"], candidate["product_id"], candidate["version"])
        for candidate in candidates
    }
    if len(identities) > 1:
        errors.append("all supplied tiers must use the same asset revision, product ID, and version")
    tiers = [str(candidate["tier"]) for candidate in candidates]
    if len(tiers) != len(set(tiers)):
        errors.append("supply at most one metadata package per layout tier")

    depth_values = {float(candidate["depth_mm"]) for candidate in candidates if candidate["depth_mm"]}
    if len(depth_values) > 1:
        errors.append("all supplied tiers must use the same engraving depth")
    depth = next(iter(depth_values), 0.0)
    if depth and depth < args.layer_height:
        errors.append("recess depth is smaller than one layer and may disappear in slicing")
    elif depth and depth < 2.0 * args.layer_height:
        warnings.append("recess spans fewer than two nominal layers; inspect exact slicer paths")
    if depth:
        layer_count = depth / args.layer_height
        if not math.isclose(layer_count, round(layer_count), rel_tol=0.0, abs_tol=1e-6):
            warnings.append("recess depth is not an integer multiple of layer height")

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

    choices: list[tuple[int, float, int, float, float, dict[str, object]]] = []
    if safe_width > 0 and safe_height > 0:
        for candidate in candidates:
            profile_width = float(candidate["profile_width_mm"])
            profile_height = float(candidate["profile_height_mm"])
            for rotation, width, height in (
                (0, profile_width, profile_height),
                (90, profile_height, profile_width),
            ):
                if width <= safe_width and height <= safe_height:
                    margin = min(safe_width - width, safe_height - height)
                    choices.append(
                        (int(candidate["priority"]), -margin, rotation, width, height, candidate)
                    )

    selection: dict[str, object] | None = None
    selected_candidate: dict[str, object] | None = None
    if choices and not errors:
        _, _, rotation, width, height, selected_candidate = min(choices, key=lambda item: item[:3])
        selection = {
            "layout_tier": selected_candidate["tier"],
            "layout_priority": selected_candidate["priority"],
            "domain_visible": selected_candidate["domain_visible"],
            "visible_text": selected_candidate["visible_text"],
            "rotation_deg": rotation,
            "uniform_scale": 1.0,
            "actual_envelope_mm": [round(width, 4), round(height, 4)],
            "depth_mm": round(depth, 4),
            "metadata": str(selected_candidate["metadata_path"]),
            "generated_directory": str(Path(selected_candidate["metadata_path"]).parent),
        }
    elif candidates and safe_width > 0 and safe_height > 0 and not errors:
        footprints = ", ".join(
            f"{candidate['tier']}={float(candidate['profile_width_mm']):.3f}x"
            f"{float(candidate['profile_height_mm']):.3f} mm"
            for candidate in sorted(candidates, key=lambda item: int(item["priority"]))
        )
        errors.append(
            "none of the exact generated layouts fits; use another safe region or revise the product geometry "
            f"({footprints})"
        )

    if args.nozzle != 0.4 or args.layer_height != 0.2:
        warnings.append(
            "process differs from the 0.40 mm nozzle / 0.20 mm layer reference; pass a generated physical coupon before release"
        )
    physical_status = selected_candidate["physical_test"] if selected_candidate else "PENDING"
    if physical_status != "PASS":
        warnings.append("selected profile remains physically unqualified until the intended-process coupon passes")

    identity = next(iter(identities), (None, None, None)) if len(identities) == 1 else (None, None, None)
    result = {
        "status": "PASS" if not errors and selection else "BLOCK",
        "asset_id": identity[0],
        "brand": "metriMade",
        "domain": DOMAIN,
        "product_id": identity[1],
        "version": identity[2],
        "available_layouts": [
            {
                "tier": candidate["tier"],
                "priority": candidate["priority"],
                "envelope_mm": [
                    candidate["profile_width_mm"],
                    candidate["profile_height_mm"],
                    candidate["depth_mm"],
                ],
                "metadata": str(candidate["metadata_path"]),
            }
            for candidate in sorted(candidates, key=lambda item: int(item["priority"]))
        ],
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
        "orientation_check": "verify the selected visible identity directly on the exported finished underside",
        "physical_qualification": physical_status,
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
