"""Validate a hybrid printable-design plan and generate architecture/organic briefs.

Uses only the Python standard library. The JSON Schema is provided for editors and
full schema validators; this script adds cross-reference and workflow checks that a
plain schema cannot express conveniently.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

AUTHORITIES = {"parametric", "organic", "hybrid", "purchased", "negative/tooling"}
REPRESENTATIONS = {"brep", "mesh", "heightmap", "texture", "cots", "negative_volume", "mixed"}
INTERFACE_KINDS = {
    "fused_overlap",
    "keyed_insert",
    "adhesive_backer",
    "dovetail_slide",
    "shell_over_core",
    "relief_substrate",
    "fastener",
    "flexible_flange",
    "purchased_mate",
    "other",
}
VALID_GATES = {"architecture", "proxy", "component", "integration", "manufacturing", "physical"}
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Plan not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def is_vec3(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(is_number(v) for v in value)


def is_matrix4(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 16 and all(is_number(v) for v in value)


def envelope_ok(value: Any) -> bool:
    if not isinstance(value, dict) or not is_vec3(value.get("min")) or not is_vec3(value.get("max")):
        return False
    return all(float(lo) < float(hi) for lo, hi in zip(value["min"], value["max"]))


def envelope_extents(value: dict[str, Any]) -> list[float]:
    return [float(hi) - float(lo) for lo, hi in zip(value["min"], value["max"])]


def contains_envelope(outer: dict[str, Any], inner: dict[str, Any], tolerance: float = 1e-9) -> bool:
    return all(
        float(ilo) >= float(olo) - tolerance and float(ihi) <= float(ohi) + tolerance
        for olo, ohi, ilo, ihi in zip(outer["min"], outer["max"], inner["min"], inner["max"])
    )


def norm(vector: Iterable[float]) -> float:
    return math.sqrt(sum(float(v) ** 2 for v in vector))


def dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(float(x) * float(y) for x, y in zip(a, b))


def ids_with_duplicates(items: list[dict[str, Any]], label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{label}[{index}] has no non-empty id")
            continue
        if not ID_PATTERN.match(item_id):
            errors.append(f"{label} id {item_id!r} must contain only letters, digits, '_' or '-' and start alphanumeric")
        if item_id in result:
            errors.append(f"Duplicate {label} id: {item_id}")
        result[item_id] = item
    return result


def validate_plan(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    project = data.get("project")
    components = data.get("components")
    interfaces = data.get("interfaces")
    keepouts = data.get("keepouts")
    validations = data.get("validation")
    decisions = data.get("decision_log")

    if not isinstance(project, dict):
        errors.append("project must be an object")
        project = {}
    if not isinstance(components, list) or not components:
        errors.append("components must be a non-empty array")
        components = []
    if not isinstance(interfaces, list):
        errors.append("interfaces must be an array")
        interfaces = []
    if not isinstance(keepouts, list):
        errors.append("keepouts must be an array")
        keepouts = []
    if not isinstance(validations, list):
        errors.append("validation must be an array")
        validations = []
    if not isinstance(decisions, list):
        errors.append("decision_log must be an array")
        decisions = []

    if project.get("units") != "mm":
        errors.append("project.units must be 'mm'")
    if not project.get("source_modes"):
        errors.append("project.source_modes must not be empty")
    if not isinstance(project.get("assembly_sequence"), list) or not project.get("assembly_sequence"):
        warnings.append("project.assembly_sequence is empty; trapped or inaccessible parts may be missed")

    master_envelope = project.get("master_envelope_mm")
    if not envelope_ok(master_envelope):
        errors.append("project.master_envelope_mm must contain numeric min/max vec3 with min < max")
        master_envelope = None

    requirements = project.get("requirements", [])
    if not isinstance(requirements, list):
        errors.append("project.requirements must be an array")
        requirements = []
    requirement_ids = ids_with_duplicates(requirements, "requirement", errors)
    if not requirement_ids:
        warnings.append("No requirements are recorded; component and interface allocation will be weak")

    component_by_id = ids_with_duplicates(components, "component", errors)
    interface_by_id = ids_with_duplicates(interfaces, "interface", errors)
    keepout_by_id = ids_with_duplicates(keepouts, "keepout", errors)
    ids_with_duplicates(validations, "validation", errors)
    decision_by_id = ids_with_duplicates(decisions, "decision", errors)

    for decision_id, decision in decision_by_id.items():
        status = decision.get("status")
        if status not in {"open", "provisional", "resolved"}:
            errors.append(f"Decision {decision_id}: unknown status {status!r}")
        if not isinstance(decision.get("topic"), str) or not decision["topic"].strip():
            errors.append(f"Decision {decision_id}: topic must be a non-empty string")
        if not isinstance(decision.get("current_basis"), str):
            errors.append(f"Decision {decision_id}: current_basis must be a string")
        if not isinstance(decision.get("evidence_needed"), str):
            errors.append(f"Decision {decision_id}: evidence_needed must be a string")
        blocks = decision.get("blocks_gates")
        if not isinstance(blocks, list):
            errors.append(f"Decision {decision_id}: blocks_gates must be an array")
            blocks = []
        unknown_gates = set(blocks) - (VALID_GATES | {"release"})
        if unknown_gates:
            errors.append(f"Decision {decision_id}: unknown blocked gates: {', '.join(sorted(unknown_gates))}")
        if status in {"open", "provisional"} and not decision.get("evidence_needed", "").strip():
            warnings.append(f"Decision {decision_id}: unresolved decision has no evidence_needed")
        if status == "resolved" and blocks:
            warnings.append(f"Decision {decision_id}: resolved decision still blocks gates")

    for component_id, component in component_by_id.items():
        authority = component.get("authority")
        representation = component.get("representation")
        if authority not in AUTHORITIES:
            errors.append(f"Component {component_id}: unknown authority {authority!r}")
        if representation not in REPRESENTATIONS:
            errors.append(f"Component {component_id}: unknown representation {representation!r}")
        if not component.get("functions"):
            warnings.append(f"Component {component_id}: no function/appearance/manufacturing reason is recorded")

        envelope = component.get("envelope_mm")
        if not envelope_ok(envelope):
            errors.append(f"Component {component_id}: invalid envelope_mm")
        elif master_envelope and not contains_envelope(master_envelope, envelope):
            warnings.append(f"Component {component_id}: envelope extends outside project master envelope")

        scale = component.get("source_to_mm_scale")
        if not is_number(scale) or float(scale) <= 0:
            errors.append(f"Component {component_id}: source_to_mm_scale must be positive")
        transform = component.get("placement_transform")
        if not is_matrix4(transform):
            errors.append(f"Component {component_id}: placement_transform must contain 16 finite numbers")
        elif any(abs(float(a) - float(b)) > 1e-6 for a, b in zip(transform[12:16], [0.0, 0.0, 0.0, 1.0])):
            warnings.append(f"Component {component_id}: transform bottom row is not [0,0,0,1] under the declared convention")

        listed_interfaces = component.get("interface_ids", [])
        if not isinstance(listed_interfaces, list):
            errors.append(f"Component {component_id}: interface_ids must be an array")
            listed_interfaces = []
        for interface_id in listed_interfaces:
            if interface_id not in interface_by_id:
                errors.append(f"Component {component_id}: references missing interface {interface_id}")

        acceptance = component.get("acceptance")
        if not isinstance(acceptance, dict):
            errors.append(f"Component {component_id}: acceptance must be an object")
        else:
            expected_components = acceptance.get("expected_components")
            if not isinstance(expected_components, int) or expected_components < 1:
                errors.append(f"Component {component_id}: acceptance.expected_components must be >= 1")
            if not is_number(acceptance.get("max_bounds_error_mm")) or float(acceptance["max_bounds_error_mm"]) < 0:
                errors.append(f"Component {component_id}: acceptance.max_bounds_error_mm must be non-negative")

        image_job = component.get("image_to_3d")
        if authority == "organic" and not isinstance(image_job, dict):
            errors.append(f"Organic component {component_id}: image_to_3d brief is required")
        if isinstance(image_job, dict):
            if not image_job.get("input_views"):
                errors.append(f"Component {component_id}: image_to_3d.input_views must not be empty")
            if not image_job.get("positive_prompt"):
                errors.append(f"Component {component_id}: image_to_3d.positive_prompt must not be empty")
            band = image_job.get("sacrificial_interface_band_mm")
            if not is_number(band) or float(band) < 0:
                errors.append(f"Component {component_id}: sacrificial_interface_band_mm must be non-negative")
            landmarks = image_job.get("landmarks", [])
            if not isinstance(landmarks, list):
                errors.append(f"Component {component_id}: landmarks must be an array")
            elif len(landmarks) < 3 and component.get("interface_ids"):
                warnings.append(f"Component {component_id}: fewer than three registration landmarks are defined")
            if representation == "mesh" and authority == "organic" and float(band or 0) == 0:
                warnings.append(f"Component {component_id}: no sacrificial interface band is reserved")

        if len(component_by_id) > 1 and authority not in {"negative/tooling"} and not listed_interfaces:
            warnings.append(f"Component {component_id}: isolated from the interface graph")

    for interface_id, interface in interface_by_id.items():
        a = interface.get("a")
        b = interface.get("b")
        owner = interface.get("owner")
        kind = interface.get("kind")
        if a not in component_by_id or b not in component_by_id:
            errors.append(f"Interface {interface_id}: endpoints must reference existing components ({a!r}, {b!r})")
            continue
        if a == b:
            errors.append(f"Interface {interface_id}: endpoints must be different")
        if owner not in {a, b}:
            errors.append(f"Interface {interface_id}: owner must be one endpoint, got {owner!r}")
        if kind not in INTERFACE_KINDS:
            errors.append(f"Interface {interface_id}: unknown kind {kind!r}")

        for endpoint in (a, b):
            listed = component_by_id[endpoint].get("interface_ids", [])
            if interface_id not in listed:
                errors.append(f"Interface {interface_id}: endpoint {endpoint} does not list the interface in interface_ids")

        frame = interface.get("local_frame")
        if not isinstance(frame, dict) or not all(is_vec3(frame.get(key)) for key in ("origin_mm", "x_axis", "y_axis", "z_axis")):
            errors.append(f"Interface {interface_id}: local_frame must contain origin_mm and three numeric axes")
        else:
            axes = [frame["x_axis"], frame["y_axis"], frame["z_axis"]]
            if any(abs(norm(axis) - 1.0) > 1e-3 for axis in axes):
                warnings.append(f"Interface {interface_id}: local-frame axes are not unit length")
            if any(abs(dot(axes[i], axes[j])) > 1e-3 for i, j in ((0, 1), (0, 2), (1, 2))):
                warnings.append(f"Interface {interface_id}: local-frame axes are not orthogonal")

        allowances = interface.get("allowances")
        allowance_keys = (
            "functional_clearance_per_side_mm",
            "process_compensation_per_side_mm",
            "assembly_allowance_per_side_mm",
            "adhesive_gap_per_side_mm",
            "boolean_overlap_mm",
            "registration_uncertainty_mm",
            "solver_margin_mm",
        )
        if not isinstance(allowances, dict):
            errors.append(f"Interface {interface_id}: allowances must be an object")
            allowances = {}
        for key in allowance_keys:
            value = allowances.get(key)
            if not is_number(value) or float(value) < 0:
                errors.append(f"Interface {interface_id}: allowance {key} must be non-negative")

        overlap = float(allowances.get("boolean_overlap_mm", 0) or 0)
        clearance = sum(
            float(allowances.get(key, 0) or 0)
            for key in (
                "functional_clearance_per_side_mm",
                "process_compensation_per_side_mm",
                "assembly_allowance_per_side_mm",
                "adhesive_gap_per_side_mm",
            )
        )
        if kind == "fused_overlap" and overlap <= 0:
            errors.append(f"Interface {interface_id}: fused_overlap requires positive boolean_overlap_mm")
        if overlap > 0 and clearance > 0:
            warnings.append(f"Interface {interface_id}: both positive overlap and positive gap/clearance terms are defined; confirm the intended bodies")

        for keepout_id in interface.get("keepout_ids", []):
            if keepout_id not in keepout_by_id:
                errors.append(f"Interface {interface_id}: references missing keepout {keepout_id}")

        seam_band = interface.get("seam_band_mm")
        if not is_number(seam_band) or float(seam_band) < 0:
            errors.append(f"Interface {interface_id}: seam_band_mm must be non-negative")
            seam_band_value = 0.0
        else:
            seam_band_value = float(seam_band)

        for endpoint in (a, b):
            component = component_by_id[endpoint]
            image_job = component.get("image_to_3d")
            if isinstance(image_job, dict):
                organic_band = float(image_job.get("sacrificial_interface_band_mm", 0) or 0)
                if organic_band + 1e-9 < seam_band_value:
                    errors.append(
                        f"Interface {interface_id}: seam band {seam_band_value:g} mm exceeds {endpoint}'s "
                        f"organic sacrificial band {organic_band:g} mm"
                    )

        requirements_obj = interface.get("requirements")
        if not isinstance(requirements_obj, dict):
            errors.append(f"Interface {interface_id}: requirements must be an object")
        elif not interface.get("verification"):
            errors.append(f"Interface {interface_id}: at least one verification method is required")

        if component_by_id.get(owner, {}).get("authority") == "organic" and kind not in {"relief_substrate", "other"}:
            warnings.append(f"Interface {interface_id}: organic component {owner} owns nominal geometry; confirm this is intentional")

    for keepout_id, keepout in keepout_by_id.items():
        if keepout.get("type") == "aabb":
            proxy = {"min": keepout.get("min_mm"), "max": keepout.get("max_mm")}
            if not envelope_ok(proxy):
                errors.append(f"Keepout {keepout_id}: AABB needs numeric min_mm/max_mm with min < max")

    recorded_gates = set()
    for validation in validations:
        gate = validation.get("gate")
        if gate not in VALID_GATES:
            errors.append(f"Validation {validation.get('id', '<unknown>')}: unknown gate {gate!r}")
        else:
            recorded_gates.add(gate)
        if not validation.get("method") or not validation.get("acceptance"):
            errors.append(f"Validation {validation.get('id', '<unknown>')}: method and acceptance are required")
    missing_gates = VALID_GATES - recorded_gates
    if missing_gates:
        warnings.append("No validation entries for gates: " + ", ".join(sorted(missing_gates)))

    return errors, warnings


def decision_state(data: dict[str, Any]) -> dict[str, Any]:
    decisions = data.get("decision_log", [])
    if not isinstance(decisions, list):
        decisions = []
    unresolved = [
        item for item in decisions
        if isinstance(item, dict) and item.get("status") in {"open", "provisional"}
    ]
    blocked_gates = sorted({
        gate
        for item in unresolved
        for gate in item.get("blocks_gates", [])
        if gate in VALID_GATES | {"release"}
    })
    return {
        "unresolved_decisions": [str(item.get("id", "<unknown>")) for item in unresolved],
        "blocked_gates": blocked_gates,
        "release_blocked": "release" in blocked_gates,
    }


def md_cell(value: Any) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ")


def fmt_vec(values: Iterable[float]) -> str:
    return "[" + ", ".join(f"{float(v):g}" for v in values) + "]"


def fmt_envelope(envelope: Any) -> str:
    if not envelope_ok(envelope):
        return "invalid"
    extents = envelope_extents(envelope)
    return f"{fmt_vec(envelope['min'])} → {fmt_vec(envelope['max'])} ({' × '.join(f'{v:g}' for v in extents)} mm)"


def model_clearance(allowances: dict[str, Any]) -> float:
    return sum(
        float(allowances.get(key, 0) or 0)
        for key in (
            "functional_clearance_per_side_mm",
            "process_compensation_per_side_mm",
            "assembly_allowance_per_side_mm",
        )
    )


def build_report(data: dict[str, Any], errors: list[str], warnings: list[str]) -> str:
    project = data.get("project", {})
    components = data.get("components", [])
    interfaces = data.get("interfaces", [])
    keepouts = data.get("keepouts", [])
    validations = data.get("validation", [])
    decisions = data.get("decision_log", [])
    readiness = decision_state(data)

    lines: list[str] = [
        f"# Hybrid design architecture — {project.get('title', 'Untitled')}",
        "",
        f"- Project ID: `{project.get('id', '')}`",
        f"- Claim: `{project.get('claim', '')}`",
        f"- Sources: {', '.join(project.get('source_modes', []))}",
        f"- Units: `{project.get('units', '')}`",
        f"- Master envelope: {fmt_envelope(project.get('master_envelope_mm'))}",
        f"- Plan integrity: {'PASS' if not errors else 'FAIL'} ({len(errors)} errors, {len(warnings)} warnings)",
        f"- Release readiness: {'BLOCKED' if readiness['release_blocked'] else 'not blocked by decision log'}",
        f"- Blocked gates: {', '.join(readiness['blocked_gates']) or 'none'}",
        "",
        "## Requirements",
        "",
        "| ID | Priority | Evidence | Statement | Verification |",
        "|---|---|---|---|---|",
    ]
    for req in project.get("requirements", []):
        lines.append(
            "| " + " | ".join(
                md_cell(req.get(key)) for key in ("id", "priority", "evidence_class", "statement", "verification")
            ) + " |"
        )

    lines.extend([
        "",
        "## Decision and gate log",
        "",
        "| ID | Status | Topic | Current basis | Evidence needed | Blocks |",
        "|---|---|---|---|---|---|",
    ])
    for decision in decisions:
        lines.append(
            "| " + " | ".join(
                [
                    md_cell(decision.get("id")),
                    md_cell(decision.get("status")),
                    md_cell(decision.get("topic")),
                    md_cell(decision.get("current_basis")),
                    md_cell(decision.get("evidence_needed")),
                    md_cell(", ".join(decision.get("blocks_gates", []))),
                ]
            ) + " |"
        )

    lines.extend([
        "",
        "## Components",
        "",
        "| ID | Authority | Representation | Role | Envelope | Material/body | Interfaces |",
        "|---|---|---|---|---|---|---|",
    ])
    for component in components:
        manufacturing = component.get("manufacturing", {})
        material_body = f"{manufacturing.get('material', '')} / {manufacturing.get('color_body', '')}"
        lines.append(
            "| " + " | ".join(
                [
                    md_cell(component.get("id")),
                    md_cell(component.get("authority")),
                    md_cell(component.get("representation")),
                    md_cell(component.get("role")),
                    md_cell(fmt_envelope(component.get("envelope_mm"))),
                    md_cell(material_body),
                    md_cell(", ".join(component.get("interface_ids", []))),
                ]
            ) + " |"
        )

    lines.extend([
        "",
        "## Interfaces",
        "",
        "| ID | Pair | Owner | Kind | Modeled clearance/side | Adhesive gap/side | Boolean overlap | Seam band | Keep-outs |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ])
    for interface in interfaces:
        allowances = interface.get("allowances", {})
        lines.append(
            "| " + " | ".join(
                [
                    md_cell(interface.get("id")),
                    md_cell(f"{interface.get('a')} ↔ {interface.get('b')}"),
                    md_cell(interface.get("owner")),
                    md_cell(interface.get("kind")),
                    f"{model_clearance(allowances):g} mm",
                    f"{float(allowances.get('adhesive_gap_per_side_mm', 0) or 0):g} mm",
                    f"{float(allowances.get('boolean_overlap_mm', 0) or 0):g} mm",
                    f"{float(interface.get('seam_band_mm', 0) or 0):g} mm",
                    md_cell(", ".join(interface.get("keepout_ids", []))),
                ]
            ) + " |"
        )

    lines.extend(["", "## Organic/image-to-3D jobs", ""])
    organic_jobs = [c for c in components if isinstance(c.get("image_to_3d"), dict)]
    if organic_jobs:
        lines.extend([
            "| Component | Mode | Views | Sacrificial band | Landmarks |",
            "|---|---|---|---:|---:|",
        ])
        for component in organic_jobs:
            job = component["image_to_3d"]
            lines.append(
                f"| {md_cell(component.get('id'))} | {md_cell(job.get('generation_mode'))} | "
                f"{md_cell(', '.join(job.get('input_views', [])))} | "
                f"{float(job.get('sacrificial_interface_band_mm', 0) or 0):g} mm | "
                f"{len(job.get('landmarks', []))} |"
            )
    else:
        lines.append("No image-to-3D jobs are defined.")

    lines.extend(["", "## Keep-outs", ""])
    if keepouts:
        for keepout in keepouts:
            bounds = ""
            if keepout.get("type") == "aabb":
                bounds = f" {fmt_vec(keepout.get('min_mm', []))} → {fmt_vec(keepout.get('max_mm', []))}"
            lines.append(f"- `{keepout.get('id')}` ({keepout.get('type')}): {keepout.get('purpose')}.{bounds}")
    else:
        lines.append("No keep-outs are defined.")

    lines.extend(["", "## Assembly sequence", ""])
    for index, step in enumerate(project.get("assembly_sequence", []), start=1):
        lines.append(f"{index}. {step}")

    lines.extend(["", "## Validation gates", ""])
    for item in validations:
        lines.append(f"- `{item.get('gate')}` / `{item.get('id')}` — {item.get('method')} Acceptance: {item.get('acceptance')}")

    lines.extend(["", "## Plan diagnostics", ""])
    if errors:
        lines.append("### Errors")
        lines.append("")
        lines.extend(f"- {message}" for message in errors)
        lines.append("")
    if warnings:
        lines.append("### Warnings")
        lines.append("")
        lines.extend(f"- {message}" for message in warnings)
        lines.append("")
    if not errors and not warnings:
        lines.append("No errors or warnings.")

    return "\n".join(lines).rstrip() + "\n"


def interface_summary(interface: dict[str, Any]) -> list[str]:
    allowances = interface.get("allowances", {})
    geometry = json.dumps(interface.get("nominal_geometry", {}), ensure_ascii=False, sort_keys=True)
    return [
        f"- `{interface.get('id')}`: {interface.get('a')} ↔ {interface.get('b')}",
        f"  - nominal owner: `{interface.get('owner')}`; kind: `{interface.get('kind')}`",
        f"  - nominal geometry: `{geometry}`",
        f"  - local origin: `{fmt_vec(interface.get('local_frame', {}).get('origin_mm', [0, 0, 0]))}`",
        f"  - assembly: {interface.get('joining', {}).get('method')} along {interface.get('joining', {}).get('assembly_direction')}",
        f"  - modeled non-adhesive clearance per side: `{model_clearance(allowances):g} mm`",
        f"  - adhesive gap per side: `{float(allowances.get('adhesive_gap_per_side_mm', 0) or 0):g} mm`",
        f"  - Boolean overlap: `{float(allowances.get('boolean_overlap_mm', 0) or 0):g} mm`",
        f"  - seam/edit band: `{float(interface.get('seam_band_mm', 0) or 0):g} mm`",
        f"  - keep-outs: {', '.join(interface.get('keepout_ids', [])) or 'none'}",
    ]


def build_component_brief(data: dict[str, Any], component: dict[str, Any]) -> str:
    project = data.get("project", {})
    job = component.get("image_to_3d", {})
    component_id = component.get("id")
    related = [
        interface
        for interface in data.get("interfaces", [])
        if component_id in {interface.get("a"), interface.get("b")}
    ]
    source = component.get("source", {})
    acceptance = component.get("acceptance", {})
    style = project.get("global_style", {})

    lines = [
        f"# Image-to-3D component brief — {component_id}: {component.get('name')}",
        "",
        "## Identity and authority",
        "",
        f"- Role: {component.get('role')}",
        f"- Authority: `{component.get('authority')}`; representation: `{component.get('representation')}`",
        f"- Source: `{source.get('kind')}` — {', '.join(source.get('refs', []))}",
        f"- Source confidence: `{source.get('confidence')}`",
        f"- Target project envelope: `{fmt_envelope(component.get('envelope_mm'))}`",
        f"- Source-to-mm scale currently recorded: `{component.get('source_to_mm_scale')}`",
        f"- Project frame: {project.get('coordinate_frame', {}).get('transform_convention', '')}",
        "",
        "The generated mesh does not own critical mating geometry. Preserve a thick sacrificial root/band and trim it with the parametric interface kit after registration.",
        "",
        "## Generation plate",
        "",
        f"- Mode: `{job.get('generation_mode')}`",
        f"- Required views: {', '.join(job.get('input_views', []))}",
        f"- Positive prompt: {job.get('positive_prompt')}",
        f"- Exclude: {', '.join(job.get('exclude', []))}",
        f"- Sacrificial interface band: `{float(job.get('sacrificial_interface_band_mm', 0) or 0):g} mm`",
        "- Plate setup: full uncropped silhouette; isolated target; neutral/transparent background; broad diffuse light; matte clay; no ruler, labels, arrows, scenery, or neighbouring product body.",
        "- Keep evidence crops with context separate from these generation plates.",
        "",
        "## Shared style lock",
        "",
        f"- Summary: {style.get('summary', '')}",
        f"- Motifs: {', '.join(style.get('motifs', []))}",
        f"- Global exclusions: {', '.join(style.get('exclude', []))}",
        f"- Generation material: {style.get('generation_material', '')}",
        f"- Detail hierarchy: {style.get('detail_hierarchy', '')}",
        "",
        "## Protected visual geometry",
        "",
    ]
    protected = job.get("protected_features", [])
    lines.extend(f"- {item}" for item in protected or ["No protected features recorded — resolve before final generation."])
    lines.extend(["", "## Required negative spaces", ""])
    negative_spaces = job.get("negative_spaces", [])
    lines.extend(f"- {item}" for item in negative_spaces or ["No required negative spaces recorded."])

    lines.extend(["", "## Registration landmarks", "", "| ID | Project point (mm) | Meaning |", "|---|---|---|"])
    for landmark in job.get("landmarks", []):
        lines.append(f"| {md_cell(landmark.get('id'))} | {md_cell(fmt_vec(landmark.get('point_mm', [])))} | {md_cell(landmark.get('meaning'))} |")

    lines.extend(["", "## Interfaces and keep-outs", ""])
    for interface in related:
        lines.extend(interface_summary(interface))
    if not related:
        lines.append("No interface is defined. Do not generate final geometry until the interface graph is complete.")

    lines.extend([
        "",
        "## Candidate acceptance order",
        "",
        "1. Correct semantic identity, handedness, and expected component count.",
        "2. Target envelope, silhouette, and required negative spaces.",
        "3. Sufficient sacrificial root and no protected detail in the seam band.",
        "4. No functional keep-out collision after recorded placement.",
        "5. Printable feature hierarchy and topology suitable for the selected integration route.",
        "6. Surface detail and texture only after a clay render passes.",
        "",
        f"Expected mesh components: `{acceptance.get('expected_components')}`",
        f"Require watertight at intake: `{acceptance.get('require_watertight')}`",
        f"Maximum project-bounds error after registration: `{acceptance.get('max_bounds_error_mm')} mm`",
        "",
        "Checks:",
        "",
    ])
    lines.extend(f"- {item}" for item in acceptance.get("checks", []))
    lines.extend([
        "",
        "## Return package",
        "",
        "- raw model output with original nodes/materials and model/settings/seed where available;",
        "- generation plates, masks, and named view convention;",
        "- clay renders from required views;",
        "- no destructive repair, scale bake, or fusion with the product core before intake;",
        "- explicit note for invented backside/hidden regions.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Hybrid design plan JSON")
    parser.add_argument("--report", type=Path, help="Write a Markdown architecture report")
    parser.add_argument("--briefs-dir", type=Path, help="Write one Markdown brief per image-to-3D component")
    parser.add_argument("--json-report", type=Path, help="Write machine-readable validation diagnostics")
    parser.add_argument("--validate-only", action="store_true", help="Validate without emitting Markdown to stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_json(args.plan)
    errors, warnings = validate_plan(data)
    readiness = decision_state(data)
    report = build_report(data, errors, warnings)

    if args.report:
        write_text(args.report, report)
    elif not args.validate_only:
        sys.stdout.write(report)

    if args.briefs_dir:
        for component in data.get("components", []):
            if isinstance(component.get("image_to_3d"), dict):
                filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(component.get("id", "component"))) + ".md"
                write_text(args.briefs_dir / filename, build_component_brief(data, component))

    if args.json_report:
        write_text(
            args.json_report,
            json.dumps(
                {
                    "valid": not errors,
                    "errors": errors,
                    "warnings": warnings,
                    **readiness,
                },
                indent=2,
                ensure_ascii=False,
            ) + "\n",
        )

    print(f"Plan {'PASS' if not errors else 'FAIL'}: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
    print(
        f"Decision log: {len(readiness['unresolved_decisions'])} unresolved; "
        f"blocked gates: {', '.join(readiness['blocked_gates']) or 'none'}",
        file=sys.stderr,
    )
    for message in errors:
        print(f"ERROR: {message}", file=sys.stderr)
    for message in warnings:
        print(f"WARNING: {message}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
