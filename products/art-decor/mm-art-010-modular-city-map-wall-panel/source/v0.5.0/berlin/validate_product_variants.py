#!/usr/bin/env python3
"""Validate MM-ART-010 revision 0.5.0 variant and packaging contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
CATALOG = PRODUCT / "product-variants.json"
CANDIDATE = "digital-candidate-r7"
PACKAGING_REPORTS = PRODUCT / "validation" / "v0.5.0" / "berlin" / CANDIDATE / "3mf"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    data = json.loads(CATALOG.read_text())
    errors: list[str] = []
    expected_tools = [1, 2, 3, 4]

    if data.get("project_id") != "MM-ART-010":
        errors.append("unexpected project_id")
    authority = data.get("geometry_authority", {})
    if authority.get("revision") != "0.5.0" or authority.get("candidate") != CANDIDATE:
        errors.append(f"geometry authority must be revision 0.5.0 {CANDIDATE}")

    axes = data.get("variant_axes", {})
    palette_axis = axes.get("palette_preset", {})
    if palette_axis.get("status") != "implemented" or palette_axis.get("affects_geometry") is not False:
        errors.append("palette_preset must be an implemented non-geometric axis")
    if palette_axis.get("default") != "berlin_oak_mint_midnight_sky":
        errors.append("the selected Berlin pilot palette must be the default")

    size_axis = axes.get("assembled_size_mm", {})
    if size_axis.get("status") != "reserved-single-production-value":
        errors.append("assembled_size_mm must remain reserved")
    if size_axis.get("slicer_uniform_scale_allowed") is not False:
        errors.append("uniform production scaling in the slicer must remain prohibited")
    if size_axis.get("current_production_values") != [[600.0, 400.0]]:
        errors.append("only the qualified 600 x 400 mm size may be listed")

    extent_axis = axes.get("map_extent", {})
    if extent_axis.get("status") != "deferred" or extent_axis.get("automatic_source_substitution_allowed") is not False:
        errors.append("map_extent must remain deferred and fail closed")

    marker_axis = axes.get("site_marker", {})
    if marker_axis.get("status") != "implemented-digital-candidate":
        errors.append("site_marker must identify the implemented DRAFT digital candidate")
    if marker_axis.get("default", {}).get("semantic_tool") != 4:
        errors.append("site_marker must reuse tool 4")

    semantic = data.get("semantic_tool_order", [])
    if [item.get("tool") for item in semantic] != expected_tools:
        errors.append("semantic tool order must remain 1,2,3,4")
    if len({item.get("source_body") for item in semantic}) != 4:
        errors.append("semantic tool order needs four unique source bodies")
    if len({item.get("semantic_role") for item in semantic}) != 4:
        errors.append("semantic tool order needs four unique semantic roles")

    palettes = data.get("palette_variants", {})
    if set(palette_axis.get("allowed", [])) != set(palettes):
        errors.append("allowed palette presets and palette_variants keys differ")
    for palette_name, palette in palettes.items():
        if palette.get("changes_geometry") is not False:
            errors.append(f"palette {palette_name} is not explicitly non-geometric")
        if [item.get("tool") for item in palette.get("machine_map", [])] != expected_tools:
            errors.append(f"palette {palette_name} does not map tools 1,2,3,4 exactly once")

    for example in data.get("configured_examples", []):
        variant_id = example.get("variant_id")
        if example.get("geometry_candidate") != CANDIDATE:
            errors.append(f"variant {variant_id} changed the geometry candidate")
        if example.get("palette_preset") not in palettes:
            errors.append(f"variant {variant_id} references an unknown palette")
        if example.get("assembled_size_mm") != [600.0, 400.0]:
            errors.append(f"variant {variant_id} uses an unqualified size")
        if example.get("site_marker") != "enabled-default-v0.5.0":
            errors.append(f"variant {variant_id} does not bind the approved default marker")

    packaging = []
    for mode in ("boundary-crop", "context-outline"):
        for half in ("left", "right"):
            path = PACKAGING_REPORTS / f"berlin-{mode}-{half}-packaging.json"
            if not path.is_file():
                errors.append(f"missing geometry packaging evidence: {path.relative_to(PRODUCT)}")
                continue
            report = json.loads(path.read_text())
            assignments = report.get("normalization", {}).get("extruder_assignments")
            if report.get("status") != "PASS":
                errors.append(f"{path.name} packaging status is not PASS")
            if assignments != expected_tools:
                errors.append(f"{path.name} does not preserve four ordered tool assignments")
            packaging.append({
                "path": str(path.relative_to(PRODUCT)),
                "sha256": sha256(path),
                "extruder_assignments": assignments,
            })

    result = {
        "schema_version": "1.0",
        "project": "MM-ART-010",
        "configuration_revision": data.get("configuration_revision"),
        "status": "PASS" if not errors else "FAIL",
        "catalog": {"path": str(CATALOG.relative_to(PRODUCT)), "sha256": sha256(CATALOG)},
        "geometry_authority": authority,
        "palette_variant_changes_geometry": False,
        "concept_gate_required_for_palette_selection": False,
        "slicer_or_ace_mapping_required": True,
        "current_production_size_mm": [600.0, 400.0],
        "nondefault_size_status": "REQUIRES_PARAMETRIC_REGENERATION_AND_REVALIDATION",
        "map_extent_status": "DEFERRED",
        "site_marker_status": "DRAFT_DIGITAL_PASS_PHYSICAL_REVIEW_REQUIRED",
        "packaging_evidence": packaging,
        "errors": errors,
    }
    payload = json.dumps(result, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload)
    print(payload, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
