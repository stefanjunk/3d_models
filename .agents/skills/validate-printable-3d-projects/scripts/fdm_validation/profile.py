from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import ValidationInputError, check, load_data, report, unique_ids


CHECK_TYPES = {"mesh", "mesh_compare", "gcode", "3mf", "interfaces", "skill", "external_report", "approvals", "physical", "review"}
BLOCKING_STATUSES = {"FAIL", "NOT_RUN", "REVIEW_REQUIRED"}


def validate_profile(path: Path, profile: str = "release") -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    try:
        data = load_data(path)
        if not isinstance(data, dict):
            raise ValidationInputError("profile root must be an object")
        if data.get("schema_version") != "1.0":
            raise ValidationInputError("schema_version must be '1.0'")
        if not isinstance(data.get("skill"), str) or not data["skill"].strip():
            raise ValidationInputError("skill must be a non-empty string")
        artifacts = unique_ids(data.get("artifact_roles", []), "artifact role")
        declared_checks = unique_ids(data.get("checks", []), "profile check")
        gates = unique_ids(data.get("manual_gates", []), "manual gate")
        if not artifacts or not declared_checks:
            raise ValidationInputError("artifact_roles and checks must be non-empty")
    except Exception as exc:
        return report("validate-profile", [check("profile-contract", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[path], profile=profile)

    checks.append(check("profile-contract", "PASS", "Profile structure and IDs are valid"))
    for artifact_id, definition in artifacts.items():
        kind = definition.get("kind")
        valid = isinstance(kind, str) and bool(kind.strip()) and isinstance(definition.get("required"), bool)
        checks.append(check(f"artifact-role:{artifact_id}", "PASS" if valid else "FAIL", f"Artifact role kind: {kind!r}"))

    for check_id, definition in declared_checks.items():
        check_type = definition.get("type")
        roles = definition.get("artifact_roles")
        status = "PASS" if check_type in CHECK_TYPES and isinstance(definition.get("required"), bool) and isinstance(roles, list) else "FAIL"
        checks.append(check(f"check-type:{check_id}", status, f"Declared check type: {check_type!r}"))
        for role in roles if isinstance(roles, list) else []:
            checks.append(check(f"check-role:{check_id}:{role}", "PASS" if role in artifacts else "FAIL", f"Referenced artifact role: {role!r}"))

    for gate_id, definition in gates.items():
        kind = definition.get("kind")
        valid = kind in {"physical", "review", "approval"} and isinstance(definition.get("required"), bool)
        checks.append(check(f"manual-gate:{gate_id}", "PASS" if valid else "FAIL", f"Manual gate kind: {kind!r}"))

    risk_requirements = data.get("risk_class_requirements")
    if risk_requirements is not None:
        if not isinstance(risk_requirements, list) or not risk_requirements:
            checks.append(check("risk-class-requirements", "FAIL", "risk_class_requirements must be a non-empty array when present"))
        else:
            seen: set[str] = set()
            for entry in risk_requirements:
                if not isinstance(entry, dict):
                    checks.append(check("risk-class-requirements", "FAIL", "each risk_class_requirements entry must be an object"))
                    continue
                risk_class = entry.get("risk_class")
                if not isinstance(risk_class, str) or not risk_class:
                    checks.append(check("risk-class-requirements", "FAIL", "risk_class must be a non-empty string"))
                    continue
                if risk_class in seen:
                    checks.append(check(f"risk-class:{risk_class}", "FAIL", f"Duplicate risk class: {risk_class!r}"))
                    continue
                seen.add(risk_class)
                named_checks = entry.get("checks") or []
                named_gates = entry.get("manual_gates") or []
                if not isinstance(named_checks, list) or not named_checks:
                    checks.append(check(f"risk-class:{risk_class}", "FAIL", "checks must be a non-empty array"))
                    continue
                problems: list[str] = []
                for ref in named_checks:
                    if ref not in declared_checks:
                        problems.append(f"undeclared check {ref!r}")
                    elif declared_checks[ref].get("required") is not True:
                        problems.append(f"check {ref!r} is not required:true")
                for ref in named_gates if isinstance(named_gates, list) else []:
                    if ref not in gates:
                        problems.append(f"undeclared manual gate {ref!r}")
                    elif gates[ref].get("required") is not True:
                        problems.append(f"manual gate {ref!r} is not required:true")
                checks.append(
                    check(
                        f"risk-class:{risk_class}",
                        "FAIL" if problems else "PASS",
                        "; ".join(problems) if problems else f"Minimum set for {risk_class} is declared and required",
                        metrics={"checks": len(named_checks), "manual_gates": len(named_gates) if isinstance(named_gates, list) else 0},
                    )
                )

    release_policy = data.get("release_policy")
    if not isinstance(release_policy, dict):
        checks.append(check("release-policy", "FAIL", "release_policy must be an object"))
    else:
        declared_statuses = release_policy.get("block_statuses", [])
        statuses = set(declared_statuses) if isinstance(declared_statuses, list) else set()
        checks.append(check("release-policy:block-statuses", "PASS" if statuses == BLOCKING_STATUSES else "FAIL", "Release must block FAIL, NOT_RUN, and REVIEW_REQUIRED", metrics={"declared": sorted(statuses)}))
        for key in ("require_sha256", "require_fresh_external_reports"):
            checks.append(check(f"release-policy:{key}", "PASS" if release_policy.get(key) is True else "FAIL", f"{key} must be true"))

    return report(
        "validate-profile",
        checks,
        inputs=[path],
        profile=profile,
        metrics={"skill": data.get("skill"), "artifact_role_count": len(artifacts), "check_count": len(declared_checks), "manual_gate_count": len(gates), "risk_classes_declared": sorted(e.get("risk_class") for e in risk_requirements if isinstance(e, dict) and isinstance(e.get("risk_class"), str)) if isinstance(risk_requirements, list) else []},
    )
