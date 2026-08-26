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
        metrics={"skill": data.get("skill"), "artifact_role_count": len(artifacts), "check_count": len(declared_checks), "manual_gate_count": len(gates)},
    )
