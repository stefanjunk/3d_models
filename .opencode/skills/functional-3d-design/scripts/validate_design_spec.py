#!/usr/bin/env python3
"""Validate the minimum engineering package required before detailed CAD."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DECISIONS = {"PRINT", "BUY", "INTEGRATE", "ELIMINATE", "NEEDS_TEST"}
NOZZLE_CLASSES = {0.4, 0.6, 0.8}
PRIMARY_MATERIALS = {"PLA", "PETG"}
SPECIALIST_MATERIALS = {"ABS", "ASA", "TPU", "PA-CF"}
PLACEHOLDERS = {"tbd", "todo", "unknown", "n/a", "na", "later", "?"}
TEST_TYPES = {"coupon", "dimensional", "assembly", "load", "life", "wear", "creep", "cycle", "slicer"}
COMPARATORS = {"<", "<=", "==", ">=", ">"}
PROCESS_STATUSES = {"supported", "conditional", "unsupported", "unverified"}
POLICY_PATH = (
    Path(__file__).parents[2]
    / "commercial-cad-provenance"
    / "references"
    / "commercial-license-policy.json"
)


def missing(record: dict[str, Any], fields: tuple[str, ...], prefix: str) -> list[str]:
    return [f"{prefix}.{field}" for field in fields if record.get(field) in (None, "", [])]


def meaningful(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in PLACEHOLDERS
    return value not in (None, "", [])


def positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_inside(root: Path, relative_path: Any, label: str) -> tuple[Path | None, str | None]:
    if not meaningful(relative_path):
        return None, f"{label} is required"
    path = (root / str(relative_path)).resolve()
    if not path.is_relative_to(root.resolve()):
        return None, f"{label} escapes project directory"
    if not path.is_file():
        return None, f"{label} does not exist"
    return path, None


def measurable_acceptance(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return (
        meaningful(value.get("metric"))
        and value.get("comparator") in COMPARATORS
        and isinstance(value.get("value"), (int, float))
        and not isinstance(value.get("value"), bool)
        and meaningful(value.get("unit"))
    )


def validate(
    spec: dict[str, Any],
    provenance: dict[str, Any],
    provenance_manifest: dict[str, Any],
    provenance_manifest_hash: str,
    manufacturing: dict[str, Any],
) -> list[str]:
    blockers = missing(spec, ("project", "intent", "commercial_product"), "root")
    project = str(spec.get("project") or "")
    if spec.get("commercial_product") is not True:
        blockers.append("root.commercial_product must be true")
    functions = spec.get("functions")
    components = spec.get("components")
    tests = spec.get("test_plan")
    function_ids: set[str] = set()
    component_ids: set[str] = set()
    printed_component_ids: set[str] = set()

    if not isinstance(functions, list) or not functions:
        blockers.append("functions")
    else:
        for index, function in enumerate(functions):
            blockers.extend(
                missing(
                    function,
                    ("id", "description", "load_case", "life_requirement", "failure_modes"),
                    f"functions[{index}]",
                )
            )
            if meaningful(function.get("id")):
                function_ids.add(str(function["id"]))
            load_case = function.get("load_case")
            if not isinstance(load_case, dict):
                blockers.append(f"functions[{index}].load_case must be structured")
            else:
                if not positive_number(load_case.get("magnitude")):
                    blockers.append(f"functions[{index}].load_case.magnitude")
                for field in ("unit", "direction", "duration"):
                    if not meaningful(load_case.get(field)):
                        blockers.append(f"functions[{index}].load_case.{field}")
            life = function.get("life_requirement")
            if not isinstance(life, dict):
                blockers.append(f"functions[{index}].life_requirement must be structured")
            else:
                if not positive_number(life.get("value")):
                    blockers.append(f"functions[{index}].life_requirement.value")
                if not meaningful(life.get("unit")):
                    blockers.append(f"functions[{index}].life_requirement.unit")
            modes = function.get("failure_modes")
            if not isinstance(modes, list) or not modes or not all(meaningful(mode) for mode in modes):
                blockers.append(f"functions[{index}].failure_modes")

    if not isinstance(components, list) or not components:
        blockers.append("components")
    else:
        for index, component in enumerate(components):
            blockers.extend(missing(component, ("id", "decision", "reason"), f"components[{index}]"))
            decision = component.get("decision")
            if meaningful(component.get("id")):
                component_ids.add(str(component["id"]))
            if decision not in DECISIONS:
                blockers.append(f"components[{index}].decision")
            if decision == "NEEDS_TEST":
                blockers.append(f"components[{index}].decision unresolved")
            if decision in {"PRINT", "INTEGRATE"}:
                if meaningful(component.get("id")):
                    printed_component_ids.add(str(component["id"]))
                blockers.extend(
                    missing(
                        component,
                        ("material_class", "nozzle_classes", "geometry_origin", "provenance_item_id"),
                        f"components[{index}]",
                    )
                )
                nozzles = component.get("nozzle_classes")
                if not isinstance(nozzles, list) or not nozzles or not set(nozzles).issubset(NOZZLE_CLASSES):
                    blockers.append(f"components[{index}].nozzle_classes")
                material = component.get("material_class")
                if material not in PRIMARY_MATERIALS | SPECIALIST_MATERIALS:
                    blockers.append(f"components[{index}].material_class")
                if material in SPECIALIST_MATERIALS and not meaningful(
                    component.get("specialist_material_reason")
                ):
                    blockers.append(f"components[{index}].specialist_material_reason")
            if decision == "BUY" and not component.get("interface_dimensions_mm"):
                blockers.append(f"components[{index}].interface_dimensions_mm")
            if decision == "BUY" and not meaningful(component.get("dimensional_source")):
                blockers.append(f"components[{index}].dimensional_source")

    if not isinstance(tests, list) or not tests:
        blockers.append("test_plan")
        test_ids: set[str] = set()
    else:
        test_ids = set()
        targeted_ids: set[str] = set()
        for index, test in enumerate(tests):
            blockers.extend(
                missing(test, ("id", "type", "targets", "acceptance"), f"test_plan[{index}]")
            )
            if meaningful(test.get("id")):
                test_ids.add(str(test["id"]))
            if test.get("type") not in TEST_TYPES:
                blockers.append(f"test_plan[{index}].type")
            targets = test.get("targets")
            if not isinstance(targets, list) or not targets:
                blockers.append(f"test_plan[{index}].targets")
            else:
                for target in targets:
                    if target not in component_ids | function_ids:
                        blockers.append(f"test_plan[{index}].targets unknown {target}")
                    else:
                        targeted_ids.add(str(target))
            if not measurable_acceptance(test.get("acceptance")):
                blockers.append(f"test_plan[{index}].acceptance must be measurable")
        for component_id in sorted(printed_component_ids - targeted_ids):
            blockers.append(f"component {component_id} has no linked test")

    if provenance.get("status") != "COMMERCIAL_LICENSE_PASS":
        blockers.append("provenance_report is not COMMERCIAL_LICENSE_PASS")
    if provenance.get("project") != project:
        blockers.append("provenance_report project mismatch")
    if provenance_manifest.get("project") != project:
        blockers.append("provenance_manifest project mismatch")
    if provenance.get("manifest_sha256") != provenance_manifest_hash:
        blockers.append("provenance_report manifest hash mismatch")
    if provenance.get("policy_sha256") != file_sha256(POLICY_PATH):
        blockers.append("provenance_report policy hash mismatch")
    approved_ids = set(provenance.get("approved_item_ids") or [])
    if provenance.get("checked_items") != len(provenance_manifest.get("items") or []):
        blockers.append("provenance_report checked_items mismatch")
    for index, component in enumerate(components or []):
        if component.get("decision") in {"PRINT", "INTEGRATE"}:
            provenance_id = component.get("provenance_item_id")
            if provenance_id not in approved_ids:
                blockers.append(f"components[{index}].provenance_item_id not approved")

    if manufacturing.get("project") != project:
        blockers.append("manufacturing_profile project mismatch")
    if manufacturing.get("strategy") != "generic-customer-qualified-fdm":
        blockers.append("manufacturing_profile strategy")
    matrix = manufacturing.get("support_matrix")
    if not isinstance(matrix, list) or not matrix:
        blockers.append("manufacturing_profile support_matrix")
        matrix = []
    entries: dict[tuple[str, float, str], dict[str, Any]] = {}
    for index, entry in enumerate(matrix):
        component_id = entry.get("component_id")
        nozzle = entry.get("nozzle_mm")
        material = entry.get("material")
        status = entry.get("status")
        if component_id not in printed_component_ids:
            blockers.append(f"manufacturing_profile.support_matrix[{index}].component_id")
        if nozzle not in NOZZLE_CLASSES:
            blockers.append(f"manufacturing_profile.support_matrix[{index}].nozzle_mm")
        if material not in PRIMARY_MATERIALS | SPECIALIST_MATERIALS:
            blockers.append(f"manufacturing_profile.support_matrix[{index}].material")
        if status not in PROCESS_STATUSES:
            blockers.append(f"manufacturing_profile.support_matrix[{index}].status")
        if component_id in printed_component_ids and nozzle in NOZZLE_CLASSES and material:
            entries[(str(component_id), float(nozzle), str(material))] = entry
        if status == "conditional":
            coupons = entry.get("required_coupons")
            if not isinstance(coupons, list) or not coupons:
                blockers.append(f"manufacturing_profile.support_matrix[{index}].required_coupons")
            elif not set(coupons).issubset(test_ids):
                blockers.append(f"manufacturing_profile.support_matrix[{index}] unknown coupon")

    for index, component in enumerate(components or []):
        if component.get("decision") not in {"PRINT", "INTEGRATE"}:
            continue
        component_id = str(component.get("id"))
        material = str(component.get("material_class"))
        for nozzle in component.get("nozzle_classes") or []:
            entry = entries.get((component_id, float(nozzle), material))
            if not entry:
                blockers.append(
                    f"manufacturing_profile support_matrix missing {component_id}/{nozzle}/{material}"
                )
            elif entry.get("status") not in {"supported", "conditional"}:
                blockers.append(
                    f"manufacturing_profile support_matrix blocks {component_id}/{nozzle}/{material}"
                )
    return blockers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--provenance-report", required=True)
    parser.add_argument("--manufacturing-profile", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()

    spec_path = Path(args.spec).resolve()
    project_root = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    provenance_path, error = resolve_inside(
        project_root, spec.get("provenance_report"), "root.provenance_report"
    )
    if error:
        blockers.append(error)
    manifest_path, error = resolve_inside(
        project_root, spec.get("provenance_manifest"), "root.provenance_manifest"
    )
    if error:
        blockers.append(error)
    manufacturing_path, error = resolve_inside(
        project_root, spec.get("manufacturing_profile"), "root.manufacturing_profile"
    )
    if error:
        blockers.append(error)
    if provenance_path and provenance_path != Path(args.provenance_report).resolve():
        blockers.append("CLI provenance report differs from design spec")
    if manufacturing_path and manufacturing_path != Path(args.manufacturing_profile).resolve():
        blockers.append("CLI manufacturing profile differs from design spec")

    provenance = json.loads(provenance_path.read_text(encoding="utf-8")) if provenance_path else {}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path else {}
    manufacturing = (
        json.loads(manufacturing_path.read_text(encoding="utf-8"))
        if manufacturing_path
        else {}
    )
    if not blockers:
        blockers.extend(
            validate(
                spec,
                provenance,
                manifest,
                file_sha256(manifest_path),
                manufacturing,
            )
        )
    status = "ENGINEERING_DECISION_PASS" if not blockers else "ENGINEERING_DECISION_BLOCKED"
    report = {"status": status, "project": spec.get("project"), "blockers": blockers}
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
