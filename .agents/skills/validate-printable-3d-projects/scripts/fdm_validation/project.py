from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from .common import (
    ValidationInputError,
    check,
    load_data,
    report,
    resolve_path,
    sha256_file,
    unique_ids,
    write_json,
)
from .autonomy import validate_approvals
from .gcode import analyze as analyze_gcode
from .geometry import compare as compare_meshes
from .interfaces import validate_contract
from .mesh import audit as audit_mesh
from .skillcheck import validate as validate_skill
from .threemf import validate as validate_3mf


def _external_status(data: dict[str, Any]) -> str:
    status = data.get("status")
    if status in {"PASS", "FAIL", "NOT_RUN", "REVIEW_REQUIRED"}:
        return status
    for key in ("passed", "valid", "success"):
        if data.get(key) is True:
            return "PASS"
        if data.get(key) is False:
            return "FAIL"
    return "REVIEW_REQUIRED"


def _external_hashes(data: dict[str, Any]) -> set[str]:
    hashes: set[str] = set()
    for item in data.get("inputs", []):
        if isinstance(item, dict) and isinstance(item.get("sha256"), str):
            hashes.add(item["sha256"])
    for key in ("input_hashes", "hashes"):
        value = data.get(key)
        if isinstance(value, dict):
            hashes.update(item for item in value.values() if isinstance(item, str))
        elif isinstance(value, list):
            hashes.update(item for item in value if isinstance(item, str))
    return hashes


def validate_project(project_path: Path, profile: str = "release") -> dict[str, Any]:
    if not project_path.is_file():
        return report("validate-project", [check("project-file", "FAIL", f"Project not found: {project_path}")], inputs=[project_path], profile=profile)
    try:
        data = load_data(project_path)
        if not isinstance(data, dict):
            raise ValidationInputError("project root must be an object")
        if data.get("schema_version") != "1.0":
            raise ValidationInputError("schema_version must be '1.0'")
        project = data.get("project")
        if not isinstance(project, dict) or not project.get("id") or not project.get("revision"):
            raise ValidationInputError("project.id and project.revision are required")
        if project.get("units") != "mm":
            raise ValidationInputError("project.units must be 'mm'")
        artifacts_list = data.get("artifacts")
        checks_list = data.get("checks")
        if not isinstance(artifacts_list, list) or not isinstance(checks_list, list):
            raise ValidationInputError("artifacts and checks must be arrays")
        if not artifacts_list or not checks_list:
            raise ValidationInputError("artifacts and checks must each contain at least one item")
        artifacts = unique_ids(artifacts_list, "artifact")
        check_defs = unique_ids(checks_list, "check")
    except Exception as exc:
        return report("validate-project", [check("project-contract", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[project_path], profile=profile)

    base = project_path.parent
    aggregate_checks: list[dict[str, Any]] = []
    artifact_state: dict[str, dict[str, Any]] = {}
    all_inputs = [project_path]
    for artifact_id, artifact in artifacts.items():
        raw_path = artifact.get("path")
        required = bool(artifact.get("required", True))
        if not isinstance(raw_path, str) or not raw_path.strip():
            aggregate_checks.append(check(f"artifact:{artifact_id}:path", "FAIL", "Artifact path must be a non-empty string", required=required))
            continue
        path = resolve_path(base, raw_path)
        all_inputs.append(path)
        row: dict[str, Any] = {
            "id": artifact_id,
            "path": str(path),
            "kind": artifact.get("kind"),
            "revision": artifact.get("revision"),
            "exists": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        artifact_state[artifact_id] = row
        if not isinstance(artifact.get("kind"), str) or not artifact.get("kind", "").strip():
            aggregate_checks.append(check(f"artifact:{artifact_id}:kind", "FAIL", "Artifact kind must be a non-empty string", required=required))
        if not path.is_file():
            aggregate_checks.append(check(f"artifact:{artifact_id}", "FAIL" if required else "NOT_RUN", f"Artifact not found: {path}", required=required))
            continue
        expected_hash = artifact.get("sha256")
        expected_revision = artifact.get("revision")
        if expected_hash is not None and (not isinstance(expected_hash, str) or re.fullmatch(r"[0-9a-f]{64}", expected_hash) is None):
            aggregate_checks.append(check(f"artifact:{artifact_id}:hash-format", "FAIL", "Expected SHA-256 must be 64 lowercase hexadecimal characters", required=required))
        if profile == "release" and required and not expected_hash:
            aggregate_checks.append(check(f"artifact:{artifact_id}:hash-declared", "REVIEW_REQUIRED", "Required release artifact has no expected SHA-256 in the contract", required=True))
        if expected_hash and expected_hash != row["sha256"]:
            aggregate_checks.append(check(f"artifact:{artifact_id}:hash", "FAIL", "Artifact SHA-256 does not match contract", required=required, metrics={"expected": expected_hash, "actual": row["sha256"]}))
        else:
            aggregate_checks.append(check(f"artifact:{artifact_id}:hash", "PASS", "Artifact exists and hash contract is satisfied", required=required, metrics={"sha256": row["sha256"]}))
        if expected_revision and expected_revision != project["revision"]:
            aggregate_checks.append(check(f"artifact:{artifact_id}:revision", "FAIL", f"Artifact revision {expected_revision!r} differs from project revision {project['revision']!r}", required=required))

    nested_reports: dict[str, Any] = {}

    def artifact_path(artifact_id: Any) -> Path:
        if artifact_id not in artifacts:
            raise ValidationInputError(f"unknown artifact id {artifact_id!r}")
        return resolve_path(base, str(artifacts[artifact_id].get("path", "")))

    for check_id, definition in check_defs.items():
        required = bool(definition.get("required", True))
        check_type = definition.get("type")
        try:
            if check_type == "mesh":
                nested = audit_mesh(artifact_path(definition.get("artifact")), definition.get("policy", {}), profile=profile)
            elif check_type == "mesh_compare":
                nested = compare_meshes(artifact_path(definition.get("reference")), artifact_path(definition.get("candidate")), definition.get("policy", {}), profile=profile)
            elif check_type == "gcode":
                nested = analyze_gcode(artifact_path(definition.get("artifact")), definition.get("policy", {}), profile=profile)
            elif check_type == "3mf":
                nested = validate_3mf(artifact_path(definition.get("artifact")), definition.get("policy", {}), profile=profile)
            elif check_type == "interfaces":
                contract = artifact_path(definition["artifact"]) if definition.get("artifact") else resolve_path(base, definition.get("path", ""))
                nested = validate_contract(contract, profile=profile)
            elif check_type == "skill":
                root = resolve_path(base, definition.get("path", ""))
                nested = validate_skill(root, runtime=str(definition.get("runtime", "portable")), profile=profile)
            elif check_type == "external_report":
                path = artifact_path(definition.get("artifact"))
                external = load_data(path)
                if not isinstance(external, dict):
                    raise ValidationInputError("external report root must be an object")
                external_status = _external_status(external)
                expected_input_ids = definition.get("expected_inputs", [])
                if not isinstance(expected_input_ids, list):
                    raise ValidationInputError("external_report.expected_inputs must be an array")
                unknown_inputs = sorted(item for item in expected_input_ids if item not in artifact_state)
                if unknown_inputs:
                    raise ValidationInputError("external report references unknown expected input(s): " + ", ".join(map(str, unknown_inputs)))
                expected_hashes = {
                    artifact_state[item]["sha256"]
                    for item in expected_input_ids
                    if artifact_state[item]["sha256"]
                }
                supplied_hashes = _external_hashes(external)
                missing_hashes = sorted(expected_hashes - supplied_hashes)
                nested_checks = [check("external-status", external_status, f"External report status: {external_status}")]
                if required and profile == "release" and not expected_input_ids:
                    nested_checks.append(check("external-input-declarations", "REVIEW_REQUIRED", "Required release report declares no expected input artifacts"))
                if expected_hashes:
                    nested_checks.append(check("external-input-freshness", "PASS" if not missing_hashes else "FAIL", "External report is tied to expected input hashes" if not missing_hashes else "External report is stale or lacks hashes: " + ", ".join(missing_hashes), metrics={"expected_hashes": sorted(expected_hashes), "supplied_hashes": sorted(supplied_hashes)}))
                nested = report("external-report", nested_checks, inputs=[path], profile=profile)
            elif check_type == "approvals":
                human_ledger_id = definition.get("human_ledger_artifact")
                secret_value = definition.get("human_secret_path")
                nested = validate_approvals(
                    artifact_path(definition.get("policy_artifact")),
                    artifact_path(definition.get("agent_ledger_artifact")),
                    target_stage=str(definition.get("target_stage", "print-candidate")),
                    human_ledger_path=artifact_path(human_ledger_id) if human_ledger_id else None,
                    human_secret_file=resolve_path(base, secret_value) if isinstance(secret_value, str) and secret_value else None,
                    profile=profile,
                )
            elif check_type in {"physical", "review"}:
                declared = definition.get("status", "REVIEW_REQUIRED")
                if declared not in {"PASS", "FAIL", "NOT_RUN", "REVIEW_REQUIRED"}:
                    declared = "FAIL"
                evidence_id = definition.get("evidence_artifact")
                evidence_ok = evidence_id in artifact_state and bool(artifact_state[evidence_id]["exists"])
                if declared == "PASS" and not evidence_ok:
                    declared = "FAIL"
                    message = "Declared PASS has no existing evidence artifact"
                else:
                    message = str(definition.get("criterion", "Human or physical review"))
                nested = report(check_type, [check(check_id, declared, message, evidence=[evidence_id] if evidence_ok else [])], profile=profile)
            else:
                raise ValidationInputError(f"unknown check type {check_type!r}")
        except Exception as exc:
            nested = report(str(check_type or "unknown"), [check("execution", "FAIL", f"{type(exc).__name__}: {exc}")], profile=profile)
        nested_reports[check_id] = nested
        if definition.get("report"):
            write_json(resolve_path(base, definition["report"]), nested)
        aggregate_checks.append(check(f"check:{check_id}", nested["status"], f"{check_type} check returned {nested['status']}", required=required, metrics={"tool": nested.get("tool")}))

    release = data.get("release", {})
    if not isinstance(release, dict):
        release = {}
    approvals = release.get("approvals", {}) if isinstance(release.get("approvals", {}), dict) else {}
    for approval in release.get("required_approvals", []):
        value = approvals.get(approval)
        passed = value in {"approved", "PASS", True}
        aggregate_checks.append(check(f"approval:{approval}", "PASS" if passed else "REVIEW_REQUIRED", f"Approval {approval}: {value!r}", required=True))

    risk = project.get("risk_class")
    if risk in {"structural", "safety-critical"} and not any(definition.get("type") == "physical" for definition in check_defs.values()):
        aggregate_checks.append(check("risk-physical-evidence", "REVIEW_REQUIRED", f"{risk} project requires an explicit physical evidence gate", required=True))
    result = report(
        "validate-project",
        aggregate_checks,
        inputs=all_inputs,
        profile=profile,
        metrics={
            "project": project,
            "artifacts": artifact_state,
            "nested_reports": nested_reports,
            "check_count": len(check_defs),
        },
        limitations=[
            "An aggregate PASS is scoped only to declared checks and thresholds.",
            "Safety, legal, aesthetic, and service claims still require the declared qualified review and physical evidence.",
        ],
    )
    return result
