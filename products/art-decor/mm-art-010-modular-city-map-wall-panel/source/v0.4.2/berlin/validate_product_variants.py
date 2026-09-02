#!/usr/bin/env python3
"""Validate that MM-ART-010 palette variants do not mutate geometry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
CATALOG = PRODUCT / "product-variants.json"
PACKAGING_REPORTS = PRODUCT / "validation" / "v0.4.0" / "berlin" / "digital-candidate-r9" / "anycubic-packaging"


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

    if data.get("project_id") != "MM-ART-010":
        errors.append("unexpected project_id")
    authority = data.get("geometry_authority", {})
    if authority.get("revision") != "0.4.0" or authority.get("candidate") != "digital-candidate-r9":
        errors.append("geometry authority must remain revision 0.4.0 digital-candidate-r9")

    axes = data.get("variant_axes", {})
    palette_axis = axes.get("palette_preset", {})
    if palette_axis.get("status") != "implemented" or palette_axis.get("affects_geometry") is not False:
        errors.append("palette_preset must be an implemented non-geometric axis")
    size_axis = axes.get("assembled_size_mm", {})
    if size_axis.get("status") != "reserved-single-production-value":
        errors.append("assembled_size_mm must remain reserved until a non-default size is regenerated and validated")
    if size_axis.get("slicer_uniform_scale_allowed") is not False:
        errors.append("uniform production scaling in the slicer must remain prohibited")
    if size_axis.get("current_production_values") != [[600.0, 400.0]]:
        errors.append("only the validated 600 x 400 mm production size may currently be listed")
    extent_axis = axes.get("map_extent", {})
    if extent_axis.get("status") != "deferred" or extent_axis.get("automatic_source_substitution_allowed") is not False:
        errors.append("map_extent must remain deferred and fail closed")

    semantic = data.get("semantic_tool_order", [])
    expected_tools = [1, 2, 3, 4]
    if [item.get("tool") for item in semantic] != expected_tools:
        errors.append("semantic tool order must remain 1,2,3,4")
    if len({item.get("source_body") for item in semantic}) != 4:
        errors.append("semantic tool order needs four unique source bodies")
    if len({item.get("semantic_role") for item in semantic}) != 4:
        errors.append("semantic tool order needs four unique semantic roles")

    palette_names = set(palette_axis.get("allowed", []))
    palettes = data.get("palette_variants", {})
    if palette_names != set(palettes):
        errors.append("allowed palette presets and palette_variants keys differ")
    for palette_name, palette in palettes.items():
        if palette.get("changes_geometry") is not False:
            errors.append(f"palette {palette_name} is not explicitly non-geometric")
        mapping = palette.get("machine_map", [])
        if [item.get("tool") for item in mapping] != expected_tools:
            errors.append(f"palette {palette_name} does not map tools 1,2,3,4 exactly once")

    for example in data.get("configured_examples", []):
        if example.get("geometry_candidate") != "digital-candidate-r9":
            errors.append(f"variant {example.get('variant_id')} changed the geometry candidate")
        if example.get("palette_preset") not in palettes:
            errors.append(f"variant {example.get('variant_id')} references an unknown palette")
        if example.get("assembled_size_mm") != [600.0, 400.0]:
            errors.append(f"variant {example.get('variant_id')} uses an unqualified size")

    packaging = []
    for mode in ("boundary-crop", "context-outline"):
        for half in ("left", "right"):
            path = PACKAGING_REPORTS / f"{mode}-{half}.json"
            if not path.is_file():
                errors.append(f"missing geometry packaging evidence: {path.relative_to(PRODUCT)}")
                continue
            report = json.loads(path.read_text())
            assignments = report.get("normalization", {}).get("extruder_assignments")
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
        "configuration_revision": "0.4.2",
        "status": "PASS" if not errors else "FAIL",
        "catalog": {"path": str(CATALOG.relative_to(PRODUCT)), "sha256": sha256(CATALOG)},
        "geometry_authority": authority,
        "palette_variant_changes_geometry": False,
        "concept_gate_required_for_palette_selection": False,
        "slicer_or_ace_mapping_required": True,
        "current_production_size_mm": [600.0, 400.0],
        "nondefault_size_status": "REQUIRES_PARAMETRIC_REGENERATION_AND_REVALIDATION",
        "map_extent_status": "DEFERRED",
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
