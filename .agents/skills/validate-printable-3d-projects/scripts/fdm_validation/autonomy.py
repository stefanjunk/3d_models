from __future__ import annotations

import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any

from .common import ValidationInputError, check, load_data, report, resolve_path, sha256_file, write_json


STAGE_IDS = (
    "requirements-normalization",
    "concept",
    "decomposition",
    "parametric-source",
    "mesh-generation",
    "interface-validation",
    "slicer-preflight",
    "print-candidate",
    "physical-print",
    "fit-and-function",
    "appearance",
    "safety",
    "commercial-release",
)
MODES = {"manual", "guided", "autonomous-to-print-candidate", "custom"}
EVIDENCE_MODES = {"agent-attestation", "deterministic-pass", "human-evidence"}
TOOL_ACTIONS = (
    "local_workspace_write",
    "local_build_export_test",
    "network",
    "dependency_install",
    "destructive_overwrite",
    "external_upload",
    "printer_upload",
    "printer_start",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CONCEPT_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".svg", ".webp"}
READINESS_ORDER = {f"R{index}": index for index in range(6)}
CRITICALITY_ORDER = {f"K{index}": index for index in range(5)}
CONFIDENCE_BANDS = {
    "HIGH",
    "MEDIUM_HIGH",
    "CONDITIONAL",
    "LOW_UNKNOWN",
    "NOT_AUTONOMOUSLY_RELEASABLE",
}
AUTONOMY_CEILING_STAGES = {
    "manual": set(),
    "guided": set(STAGE_IDS[3:7]),
    "autonomous-to-print-candidate": set(STAGE_IDS[: STAGE_IDS.index("print-candidate") + 1]),
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _policy_data(path: Path) -> dict[str, Any]:
    value = load_data(path)
    if not isinstance(value, dict):
        raise ValidationInputError("autonomy policy root must be an object")
    return value


def _stage_map(policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    stages = policy.get("stages")
    if not isinstance(stages, list):
        raise ValidationInputError("stages must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            raise ValidationInputError(f"stages[{index}] must be an object")
        stage_id = stage.get("id")
        if not isinstance(stage_id, str) or not stage_id:
            raise ValidationInputError(f"stages[{index}].id must be a non-empty string")
        if stage_id in result:
            raise ValidationInputError(f"duplicate stage {stage_id!r}")
        result[stage_id] = stage
    return result


def _preflight_summary(path: Path) -> dict[str, Any]:
    value = load_data(path)
    if not isinstance(value, dict):
        raise ValidationInputError("preflight result root must be an object")
    decision = value.get("decision")
    readiness = value.get("readiness")
    criticality = value.get("criticality")
    gates = value.get("gates")
    traceability = value.get("traceability")
    if not all(isinstance(item, dict) for item in (decision, readiness, criticality, gates, traceability)):
        raise ValidationInputError("preflight result is missing decision, readiness, criticality, gates, or traceability")

    lane = decision.get("lane")
    release = decision.get("design_release")
    confidence = decision.get("confidence")
    readiness_level = readiness.get("level")
    criticality_level = criticality.get("level")
    if lane not in {"A", "B", "C", "D", "E"}:
        raise ValidationInputError("preflight decision.lane must be A-E")
    if release not in {"GO", "GO_WITH_CONTROLS", "HOLD", "CONCEPT_ONLY"}:
        raise ValidationInputError("preflight decision.design_release is invalid")
    if confidence not in CONFIDENCE_BANDS:
        raise ValidationInputError("preflight decision.confidence is invalid")
    if readiness_level not in READINESS_ORDER:
        raise ValidationInputError("preflight readiness.level must be R0-R5")
    if criticality_level not in CRITICALITY_ORDER:
        raise ValidationInputError("preflight criticality.level must be K0-K4")
    gate_values = [gates.get(f"G{index}") for index in range(7)]
    if any(item not in {"PASS", "WARN", "FAIL"} for item in gate_values):
        raise ValidationInputError("preflight gates G0-G6 must be PASS, WARN, or FAIL")
    project_id = traceability.get("project_id")
    project_revision = traceability.get("project_revision")
    if not isinstance(project_id, str) or not project_id.strip():
        raise ValidationInputError("preflight traceability.project_id must be a non-empty string")
    if not isinstance(project_revision, str) or not project_revision.strip():
        raise ValidationInputError("preflight traceability.project_revision must be a non-empty string")
    assessment_id = value.get("assessment_id")
    assessment_version = value.get("assessment_version")
    if not isinstance(assessment_id, str) or not assessment_id.strip():
        raise ValidationInputError("preflight assessment_id must be a non-empty string")
    if not isinstance(assessment_version, str) or not assessment_version.strip():
        raise ValidationInputError("preflight assessment_version must be a non-empty string")

    has_block = (
        "FAIL" in gate_values
        or release in {"HOLD", "CONCEPT_ONLY"}
        or confidence in {"LOW_UNKNOWN", "NOT_AUTONOMOUSLY_RELEASABLE"}
        or READINESS_ORDER[readiness_level] < 3
        or criticality_level == "K4"
        or lane == "E"
    )
    if has_block or lane == "D" or CRITICALITY_ORDER[criticality_level] >= 3:
        ceiling = "manual"
    elif lane == "C" or criticality_level == "K2":
        ceiling = "guided"
    else:
        ceiling = "autonomous-to-print-candidate"

    return {
        "assessment_id": assessment_id,
        "assessment_version": assessment_version,
        "project_id": project_id,
        "project_revision": project_revision,
        "lane": lane,
        "readiness": readiness_level,
        "criticality": criticality_level,
        "design_release": release,
        "confidence": confidence,
        "gates": {f"G{index}": gate_values[index] for index in range(7)},
        "autonomy_ceiling": ceiling,
    }


def _mode_fits_ceiling(policy: dict[str, Any], ceiling: str) -> bool:
    allowed = AUTONOMY_CEILING_STAGES[ceiling]
    stages = _stage_map(policy)
    return all(stage_id in allowed for stage_id, stage in stages.items() if stage.get("approval") == "agent")


def _bound_preflight_guard(preflight_path: Path, policy_path: Path) -> dict[str, Any]:
    summary = _preflight_summary(preflight_path)
    return {
        "path": _portable_path(preflight_path, policy_path.parent),
        "sha256": sha256_file(preflight_path),
        **summary,
    }


def default_policy(
    project_id: str,
    mode: str,
    authorized_by: str,
    *,
    preflight_guard: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not project_id.strip():
        raise ValidationInputError("project_id must be non-empty")
    if mode not in MODES:
        raise ValidationInputError(f"unsupported autonomy mode {mode!r}")
    if not authorized_by.strip():
        raise ValidationInputError("authorized_by must be non-empty")
    stages = []
    for stage_id in STAGE_IDS:
        index = STAGE_IDS.index(stage_id)
        if mode == "manual" or mode == "custom":
            approval = "human"
        elif mode == "guided":
            approval = "agent" if 3 <= index <= 6 else "human"
        else:
            approval = "agent" if index <= STAGE_IDS.index("print-candidate") else "human"
        if approval == "human":
            evidence_mode = "human-evidence"
        elif index <= STAGE_IDS.index("decomposition"):
            evidence_mode = "agent-attestation"
        else:
            evidence_mode = "deterministic-pass"
        stages.append({
            "id": stage_id,
            "approval": approval,
            "evidence_mode": evidence_mode,
            "require_hashed_report_inputs": evidence_mode == "deterministic-pass",
        })
    policy = {
        "schema_version": "1.1" if preflight_guard is not None else "1.0",
        "policy_id": f"{project_id}-{mode}-v1",
        "project_id": project_id,
        "mode": mode,
        "authorization": {
            "type": "human-delegation",
            "authorized_by": authorized_by,
            "scope": "workflow-stages-only",
        },
        "stages": stages,
        "auto_approval_conditions": {
            "require_all_evidence_pass": True,
            "block_statuses": ["FAIL", "NOT_RUN", "REVIEW_REQUIRED"],
            "require_evidence_sha256": True,
        },
        "human_approval_proof": "hmac-sha256",
        "tool_policy": {
            "local_workspace_write": "allow",
            "local_build_export_test": "allow",
            "network": "ask",
            "dependency_install": "ask",
            "destructive_overwrite": "deny",
            "external_upload": "ask",
            "printer_upload": "deny",
            "printer_start": "deny",
        },
    }
    if preflight_guard is not None:
        policy["preflight_guard"] = preflight_guard
    return policy


def init_policy(
    project_id: str,
    mode: str,
    authorized_by: str,
    output: Path,
    *,
    preflight_path: Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    if output.exists() and not force:
        return report("init-autonomy", [check("output", "FAIL", f"Refusing to overwrite existing file: {output}")], inputs=[output])
    guard = None
    if preflight_path is not None:
        try:
            guard = _bound_preflight_guard(preflight_path, output)
        except Exception as exc:
            return report(
                "init-autonomy",
                [check("preflight-guard", "FAIL", f"{type(exc).__name__}: {exc}")],
                inputs=[preflight_path],
            )
        if guard["project_id"] != project_id:
            return report(
                "init-autonomy",
                [check("preflight-guard", "FAIL", "preflight project_id differs from autonomy project_id")],
                inputs=[preflight_path],
            )
    value = default_policy(project_id, mode, authorized_by, preflight_guard=guard)
    if guard is not None and not _mode_fits_ceiling(value, guard["autonomy_ceiling"]):
        return report(
            "init-autonomy",
            [
                check(
                    "preflight-autonomy-ceiling",
                    "FAIL",
                    f"Requested mode {mode!r} exceeds preflight ceiling {guard['autonomy_ceiling']!r}",
                    metrics=guard,
                )
            ],
            inputs=[preflight_path],
        )
    write_json(output, value)
    return report(
        "init-autonomy",
        [check("policy", "PASS", f"Created {mode} autonomy policy")],
        inputs=[output, *([preflight_path] if preflight_path is not None else [])],
        metrics={
            "policy_id": value["policy_id"],
            "mode": mode,
            "authorized_by": authorized_by,
            "output": str(output.resolve()),
            "preflight_bound": guard is not None,
            "autonomy_ceiling": guard.get("autonomy_ceiling") if guard else None,
        },
    )


def validate_policy(path: Path, profile: str = "release") -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    try:
        policy = _policy_data(path)
        if policy.get("schema_version") not in {"1.0", "1.1"}:
            raise ValidationInputError("schema_version must be '1.0' or '1.1'")
        for key in ("policy_id", "project_id"):
            if not isinstance(policy.get(key), str) or not policy[key].strip():
                raise ValidationInputError(f"{key} must be a non-empty string")
        mode = policy.get("mode")
        if mode not in MODES:
            raise ValidationInputError(f"mode must be one of {sorted(MODES)}")
        stages = _stage_map(policy)
        if tuple(stages) != STAGE_IDS:
            raise ValidationInputError("stages must use the complete standard sequence")
        authorization = policy.get("authorization")
        if not isinstance(authorization, dict) or authorization.get("type") != "human-delegation":
            raise ValidationInputError("authorization.type must be 'human-delegation'")
        if not isinstance(authorization.get("authorized_by"), str) or not authorization["authorized_by"].strip():
            raise ValidationInputError("authorization.authorized_by must be a non-empty string")
        if authorization.get("scope") != "workflow-stages-only":
            raise ValidationInputError("authorization.scope must be 'workflow-stages-only'")
    except Exception as exc:
        return report("validate-autonomy", [check("policy-contract", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[path], profile=profile)

    checks.append(check("policy-contract", "PASS", "Policy identity, mode, and stage order are valid"))
    preflight_path: Path | None = None
    guard = policy.get("preflight_guard")
    if policy.get("schema_version") == "1.1" and not isinstance(guard, dict):
        checks.append(check("preflight-binding", "FAIL", "Schema 1.1 requires a hash-bound preflight_guard"))
    elif isinstance(guard, dict):
        try:
            guard_path = guard.get("path")
            guard_hash = guard.get("sha256")
            if not isinstance(guard_path, str) or not guard_path:
                raise ValidationInputError("preflight_guard.path must be a non-empty string")
            if not isinstance(guard_hash, str) or not HEX64.fullmatch(guard_hash):
                raise ValidationInputError("preflight_guard.sha256 must be lowercase SHA-256")
            preflight_path = resolve_path(path.parent, guard_path)
            if not preflight_path.is_file():
                raise ValidationInputError(f"bound preflight is missing: {preflight_path}")
            if sha256_file(preflight_path) != guard_hash:
                raise ValidationInputError("bound preflight hash is stale")
            current = _preflight_summary(preflight_path)
            for key, expected in current.items():
                if guard.get(key) != expected:
                    raise ValidationInputError(f"preflight_guard.{key} does not match the bound artifact")
            if current["project_id"] != policy["project_id"]:
                raise ValidationInputError("bound preflight project_id differs from policy project_id")
            if not _mode_fits_ceiling(policy, current["autonomy_ceiling"]):
                raise ValidationInputError(
                    f"agent stage authority exceeds preflight ceiling {current['autonomy_ceiling']!r}"
                )
        except Exception as exc:
            checks.append(check("preflight-binding", "FAIL", f"{type(exc).__name__}: {exc}"))
        else:
            checks.append(
                check(
                    "preflight-binding",
                    "PASS",
                    "Autonomy is bound to the current preflight artifact and its risk ceiling",
                    metrics=current,
                )
            )
    else:
        checks.append(
            check(
                "preflight-binding",
                "REVIEW_REQUIRED",
                "Legacy 1.0 policy is not bound to a preflight; migrate before unattended coordination",
                required=False,
            )
        )
    for stage_id, stage in stages.items():
        approval = stage.get("approval")
        evidence_mode = stage.get("evidence_mode")
        valid = approval in {"agent", "human"} and evidence_mode in EVIDENCE_MODES
        valid = valid and isinstance(stage.get("require_hashed_report_inputs"), bool)
        if approval == "human" and evidence_mode != "human-evidence":
            valid = False
        if approval == "agent" and evidence_mode == "human-evidence":
            valid = False
        checks.append(check(f"stage:{stage_id}", "PASS" if valid else "FAIL", f"approval={approval!r}, evidence_mode={evidence_mode!r}"))

    mode = policy["mode"]
    print_candidate_index = STAGE_IDS.index("print-candidate")
    if mode == "manual":
        valid_mode = all(stage.get("approval") == "human" for stage in stages.values())
    elif mode == "guided":
        valid_mode = all(stages[item].get("approval") == "agent" for item in STAGE_IDS[3:7]) and stages["print-candidate"].get("approval") == "human"
    elif mode == "autonomous-to-print-candidate":
        valid_mode = all(stages[item].get("approval") == "agent" for item in STAGE_IDS[: print_candidate_index + 1])
        valid_mode = valid_mode and all(stages[item].get("approval") == "human" for item in STAGE_IDS[print_candidate_index + 1 :])
    else:
        valid_mode = True
    checks.append(check("mode-stage-boundary", "PASS" if valid_mode else "FAIL", f"Stage authorities match mode {mode!r}"))

    conditions = policy.get("auto_approval_conditions")
    valid_conditions = isinstance(conditions, dict)
    if valid_conditions:
        valid_conditions = conditions.get("require_all_evidence_pass") is True
        valid_conditions = valid_conditions and conditions.get("require_evidence_sha256") is True
        valid_conditions = valid_conditions and set(conditions.get("block_statuses", [])) == {"FAIL", "NOT_RUN", "REVIEW_REQUIRED"}
    checks.append(check("auto-approval-conditions", "PASS" if valid_conditions else "FAIL", "Auto approval is fail-closed and hash-bound"))

    proof = policy.get("human_approval_proof")
    checks.append(check("human-approval-proof", "PASS" if proof in {"manual-assertion", "hmac-sha256"} else "FAIL", f"Human proof mode: {proof!r}"))
    tool_policy = policy.get("tool_policy")
    valid_tools = isinstance(tool_policy, dict) and set(tool_policy) == set(TOOL_ACTIONS)
    if valid_tools:
        valid_tools = all(tool_policy[item] in {"allow", "ask", "deny"} for item in TOOL_ACTIONS)
        valid_tools = valid_tools and tool_policy["printer_start"] == "deny"
        valid_tools = valid_tools and tool_policy["printer_upload"] != "allow"
        valid_tools = valid_tools and tool_policy["destructive_overwrite"] != "allow"
        valid_tools = valid_tools and tool_policy["external_upload"] != "allow"
        valid_tools = valid_tools and tool_policy["dependency_install"] != "allow"
    checks.append(check("tool-policy-boundary", "PASS" if valid_tools else "FAIL", "Installation, external upload, printer control, and destructive overwrite remain outside workflow auto approval"))
    return report(
        "validate-autonomy",
        checks,
        inputs=[path, *([preflight_path] if preflight_path is not None else [])],
        profile=profile,
        metrics={"policy_id": policy["policy_id"], "project_id": policy["project_id"], "mode": mode, "authorized_by": policy["authorization"]["authorized_by"], "policy_sha256": sha256_file(path)},
        limitations=[
            "Workflow approval never grants OpenCode, operating-system, network, upload, or printer permissions.",
            *(["Schema 1.0 policies remain legacy-compatible but are not eligible for unattended Orca coordination."] if guard is None else []),
        ],
    )


def _portable_path(path: Path, base: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _evidence_rows(paths: list[Path], base: Path, *, reports: bool) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    if not paths:
        return rows, ["at least one evidence file is required"]
    for path in paths:
        resolved = path.resolve()
        if not resolved.is_file():
            failures.append(f"evidence not found: {resolved}")
            continue
        row: dict[str, Any] = {"path": _portable_path(resolved, base), "sha256": sha256_file(resolved), "size_bytes": resolved.stat().st_size}
        if reports:
            try:
                value = load_data(resolved)
            except Exception as exc:
                failures.append(f"invalid evidence report {resolved}: {type(exc).__name__}: {exc}")
                rows.append(row)
                continue
            if not isinstance(value, dict):
                failures.append(f"evidence report root is not an object: {resolved}")
                rows.append(row)
                continue
            row.update({"report_status": value.get("status"), "report_tool": value.get("tool")})
            if value.get("status") != "PASS":
                failures.append(f"evidence report is not PASS: {resolved}")
            report_checks = value.get("checks")
            if not isinstance(report_checks, list) or not report_checks:
                failures.append(f"evidence report has no executable checks: {resolved}")
            elif any(isinstance(item, dict) and item.get("required", True) and item.get("status") != "PASS" for item in report_checks):
                failures.append(f"evidence report contains a non-PASS required check: {resolved}")
            row["hashed_report_inputs"] = bool(value.get("inputs")) and all(
                isinstance(item, dict) and isinstance(item.get("sha256"), str) and HEX64.fullmatch(item["sha256"])
                for item in value.get("inputs", [])
            )
        rows.append(row)
    return rows, failures


def _is_supported_concept_image(path: Path) -> bool:
    if path.suffix.lower() not in CONCEPT_IMAGE_SUFFIXES or not path.is_file():
        return False
    with path.open("rb") as handle:
        prefix = handle.read(512)
    suffix = path.suffix.lower()
    if suffix == ".png":
        return prefix.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return prefix.startswith(b"\xff\xd8\xff")
    if suffix == ".webp":
        return prefix.startswith(b"RIFF") and prefix[8:12] == b"WEBP"
    return b"<svg" in prefix.lower()


def _rows_include_concept_image(rows: list[dict[str, Any]], base: Path) -> bool:
    return any(
        isinstance(row, dict)
        and isinstance(row.get("path"), str)
        and _is_supported_concept_image(resolve_path(base, row["path"]))
        for row in rows
    )


def _new_ledger(kind: str, policy: dict[str, Any], policy_path: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "ledger_type": kind,
        "project_id": policy["project_id"],
        "policy_id": policy["policy_id"],
        "policy_sha256": sha256_file(policy_path),
        "events": [],
    }


def _load_ledger(path: Path | None, kind: str, policy: dict[str, Any], policy_path: Path) -> dict[str, Any]:
    if path is None or not path.exists():
        return _new_ledger(kind, policy, policy_path)
    value = load_data(path)
    if not isinstance(value, dict):
        raise ValidationInputError(f"{kind} ledger root must be an object")
    if value.get("ledger_type") != kind:
        raise ValidationInputError(f"expected {kind} ledger")
    if value.get("project_id") != policy["project_id"] or value.get("policy_id") != policy["policy_id"]:
        raise ValidationInputError("ledger project or policy identity mismatch")
    if value.get("policy_sha256") != sha256_file(policy_path):
        raise ValidationInputError("ledger policy hash is stale")
    if not isinstance(value.get("events"), list):
        raise ValidationInputError("ledger events must be an array")
    return value


def _append_event(ledger: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    events = ledger["events"]
    payload["previous_event_id"] = events[-1]["event_id"] if events else None
    event = dict(payload)
    event["event_id"] = _digest(payload)
    events.append(event)
    return event


def _latest_state(agent: dict[str, Any], human: dict[str, Any]) -> dict[str, str]:
    state: dict[str, str] = {}
    for ledger in (agent, human):
        for event in ledger.get("events", []):
            if isinstance(event, dict) and isinstance(event.get("stage"), str) and isinstance(event.get("decision"), str):
                state[event["stage"]] = event["decision"]
    return state


def _prior_approved(policy: dict[str, Any], stage_id: str, agent: dict[str, Any], human: dict[str, Any]) -> list[str]:
    order = list(_stage_map(policy))
    state = _latest_state(agent, human)
    missing = []
    for prior in order[: order.index(stage_id)]:
        if state.get(prior) not in {"AUTO_APPROVED", "HUMAN_APPROVED"}:
            missing.append(prior)
    return missing


def approve_agent_stage(
    policy_path: Path,
    ledger_path: Path,
    stage_id: str,
    *,
    agent_id: str,
    model_id: str,
    evidence: list[Path],
    attestation: str | None = None,
    human_ledger_path: Path | None = None,
) -> dict[str, Any]:
    if not agent_id.strip() or not model_id.strip():
        return report("approve-agent-stage", [check("actor", "FAIL", "agent_id and model_id must be non-empty")], inputs=[policy_path])
    policy_report = validate_policy(policy_path)
    if policy_report["status"] != "PASS":
        return report("approve-agent-stage", [check("policy", "FAIL", "Autonomy policy is invalid")], inputs=[policy_path])
    policy = _policy_data(policy_path)
    stages = _stage_map(policy)
    if stage_id not in stages:
        return report("approve-agent-stage", [check("stage", "FAIL", f"Unknown stage {stage_id!r}")], inputs=[policy_path])
    stage = stages[stage_id]
    if stage.get("approval") != "agent":
        return report("approve-agent-stage", [check("authority", "FAIL", f"Stage {stage_id!r} requires a human; agent ledger was not changed")], inputs=[policy_path])
    try:
        agent = _load_ledger(ledger_path, "agent", policy, policy_path)
        human = _load_ledger(human_ledger_path, "human", policy, policy_path)
    except Exception as exc:
        return report("approve-agent-stage", [check("ledger", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[policy_path, ledger_path])
    missing = _prior_approved(policy, stage_id, agent, human)
    rows: list[dict[str, Any]] = []
    failures = [f"prior stage is not approved: {item}" for item in missing]
    guard = policy.get("preflight_guard")
    guard_event = None
    if isinstance(guard, dict):
        guard_event = {
            "path": guard.get("path"),
            "sha256": guard.get("sha256"),
            "assessment_id": guard.get("assessment_id"),
            "assessment_version": guard.get("assessment_version"),
            "project_revision": guard.get("project_revision"),
            "lane": guard.get("lane"),
            "readiness": guard.get("readiness"),
            "criticality": guard.get("criticality"),
            "autonomy_ceiling": guard.get("autonomy_ceiling"),
        }
    mode = stage.get("evidence_mode")
    if mode == "deterministic-pass":
        rows, evidence_failures = _evidence_rows(evidence, ledger_path.parent, reports=True)
        failures.extend(evidence_failures)
        if stage.get("require_hashed_report_inputs") and any(not row.get("hashed_report_inputs") for row in rows):
            failures.append("each evidence report must bind at least one input by SHA-256")
    elif mode == "agent-attestation":
        if not isinstance(attestation, str) or not attestation.strip():
            failures.append("agent-attestation stage requires --attestation")
        if stage_id == "concept":
            rows, evidence_failures = _evidence_rows(evidence, ledger_path.parent, reports=False)
            failures.extend(evidence_failures)
            if rows and not _rows_include_concept_image(rows, ledger_path.parent):
                failures.append("concept stage evidence must include a supported product concept image")
        elif evidence:
            rows, evidence_failures = _evidence_rows(evidence, ledger_path.parent, reports=False)
            failures.extend(evidence_failures)
    else:
        failures.append(f"unsupported agent evidence mode {mode!r}")
    decision = "BLOCKED" if failures else "AUTO_APPROVED"
    payload = {
        "stage": stage_id,
        "decision": decision,
        "decided_by": {"type": "agent", "id": agent_id, "model": model_id},
        "authority": {"type": "user-autonomy-policy", "policy_id": policy["policy_id"], "policy_sha256": sha256_file(policy_path)},
        "evidence": rows,
        "attestation": attestation.strip() if isinstance(attestation, str) and attestation.strip() else None,
        "preflight_guard": guard_event,
        "reasons": failures,
    }
    event = _append_event(agent, payload)
    write_json(ledger_path, agent)
    status = "PASS" if decision == "AUTO_APPROVED" else "REVIEW_REQUIRED"
    return report(
        "approve-agent-stage",
        [check("stage-decision", status, f"{stage_id}: {decision}", metrics={"event_id": event["event_id"], "reasons": failures})],
        inputs=[policy_path, ledger_path, *evidence],
        metrics={"stage": stage_id, "decision": decision, "event_id": event["event_id"]},
    )


def request_human_approval(policy_path: Path, stage_id: str, project_id: str, evidence: list[Path], output: Path, *, force: bool = False) -> dict[str, Any]:
    if output.exists() and not force:
        return report("request-human-approval", [check("output", "FAIL", f"Refusing to overwrite existing file: {output}")], inputs=[output])
    policy_result = validate_policy(policy_path)
    if policy_result["status"] != "PASS":
        return report("request-human-approval", [check("policy", "FAIL", "Autonomy policy is invalid")], inputs=[policy_path])
    policy = _policy_data(policy_path)
    stages = _stage_map(policy)
    if project_id != policy["project_id"]:
        return report("request-human-approval", [check("project", "FAIL", "Project ID differs from policy")], inputs=[policy_path])
    if stage_id not in stages or stages[stage_id].get("approval") != "human":
        return report("request-human-approval", [check("authority", "FAIL", f"Stage {stage_id!r} is not human-approved")], inputs=[policy_path])
    rows, failures = _evidence_rows(evidence, output.parent, reports=False)
    if stage_id == "concept" and rows and not _rows_include_concept_image(rows, output.parent):
        failures.append("concept stage evidence must include a supported product concept image")
    if failures:
        return report("request-human-approval", [check("evidence", "FAIL", "; ".join(failures))], inputs=[policy_path, *evidence])
    payload = {
        "schema_version": "1.0",
        "request_type": "human-stage-approval",
        "project_id": project_id,
        "stage": stage_id,
        "requested_decision": "HUMAN_APPROVED",
        "policy_id": policy["policy_id"],
        "policy_sha256": sha256_file(policy_path),
        "evidence": rows,
    }
    payload["request_id"] = _digest(payload)
    write_json(output, payload)
    return report("request-human-approval", [check("request", "PASS", f"Created human approval request for {stage_id}")], inputs=[policy_path, output, *evidence], metrics={"request_id": payload["request_id"]})


def _request_data(request_path: Path, policy: dict[str, Any], policy_path: Path) -> dict[str, Any]:
    value = load_data(request_path)
    if not isinstance(value, dict):
        raise ValidationInputError("approval request root must be an object")
    request_id = value.get("request_id")
    unsigned = {key: item for key, item in value.items() if key != "request_id"}
    if request_id != _digest(unsigned):
        raise ValidationInputError("approval request hash is invalid")
    if value.get("request_type") != "human-stage-approval" or value.get("requested_decision") != "HUMAN_APPROVED":
        raise ValidationInputError("invalid human approval request type or decision")
    if value.get("project_id") != policy["project_id"] or value.get("policy_id") != policy["policy_id"]:
        raise ValidationInputError("approval request identity mismatch")
    if value.get("policy_sha256") != sha256_file(policy_path):
        raise ValidationInputError("approval request policy hash is stale")
    return value


def approve_human_stage(
    policy_path: Path,
    request_path: Path,
    ledger_path: Path,
    *,
    human_id: str,
    agent_ledger_path: Path,
    secret_file: Path | None = None,
    key_id: str | None = None,
) -> dict[str, Any]:
    if not human_id.strip():
        return report("approve-human-stage", [check("actor", "FAIL", "human_id must be non-empty")], inputs=[policy_path, request_path])
    policy_result = validate_policy(policy_path)
    if policy_result["status"] != "PASS":
        return report("approve-human-stage", [check("policy", "FAIL", "Autonomy policy is invalid")], inputs=[policy_path])
    policy = _policy_data(policy_path)
    try:
        request = _request_data(request_path, policy, policy_path)
        stage_id = request["stage"]
        stage = _stage_map(policy)[stage_id]
        if stage.get("approval") != "human":
            raise ValidationInputError(f"stage {stage_id!r} is not human-approved")
        agent = _load_ledger(agent_ledger_path, "agent", policy, policy_path)
        human = _load_ledger(ledger_path, "human", policy, policy_path)
        missing = _prior_approved(policy, stage_id, agent, human)
        if missing:
            raise ValidationInputError("prior stages are not approved: " + ", ".join(missing))
        evidence_rows = []
        for row in request.get("evidence", []):
            if not isinstance(row, dict) or not isinstance(row.get("path"), str) or not isinstance(row.get("sha256"), str):
                raise ValidationInputError("approval request contains malformed evidence")
            evidence_path = resolve_path(request_path.parent, row["path"])
            if not evidence_path.is_file() or sha256_file(evidence_path) != row["sha256"]:
                raise ValidationInputError(f"approval request evidence is missing or stale: {evidence_path}")
            translated = dict(row)
            translated["path"] = _portable_path(evidence_path, ledger_path.parent)
            evidence_rows.append(translated)
    except Exception as exc:
        return report("approve-human-stage", [check("request", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[policy_path, request_path, agent_ledger_path, ledger_path])
    payload: dict[str, Any] = {
        "stage": stage_id,
        "decision": "HUMAN_APPROVED",
        "decided_by": {"type": "human", "id": human_id},
        "authority": {"type": "manual-decision", "request_id": request["request_id"], "policy_id": policy["policy_id"], "policy_sha256": sha256_file(policy_path)},
        "evidence": evidence_rows,
        "reasons": [],
    }
    payload["previous_event_id"] = human["events"][-1]["event_id"] if human["events"] else None
    proof_mode = policy.get("human_approval_proof")
    if proof_mode == "hmac-sha256":
        if secret_file is None or not secret_file.is_file() or not key_id:
            return report("approve-human-stage", [check("human-proof", "NOT_RUN", "Policy requires --secret-file and --key-id; human ledger was not changed")], inputs=[policy_path, request_path])
        signed_hash = _digest(payload)
        signature = hmac.new(secret_file.read_bytes(), signed_hash.encode("ascii"), hashlib.sha256).hexdigest()
        payload["proof"] = {"type": "hmac-sha256", "key_id": key_id, "signed_payload_sha256": signed_hash, "signature": signature}
    else:
        payload["proof"] = {"type": "manual-assertion"}
    event = _append_event(human, payload)
    write_json(ledger_path, human)
    return report("approve-human-stage", [check("human-decision", "PASS", f"{stage_id}: HUMAN_APPROVED", metrics={"event_id": event["event_id"], "proof": proof_mode})], inputs=[policy_path, request_path, ledger_path], metrics={"stage": stage_id, "decision": "HUMAN_APPROVED", "event_id": event["event_id"]})


def _verify_ledger(
    ledger: dict[str, Any],
    kind: str,
    policy: dict[str, Any],
    policy_path: Path,
    ledger_path: Path,
    human_secret_file: Path | None,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    expected_previous = None
    last_approved_index = -1
    stages = _stage_map(policy)
    for index, event in enumerate(ledger.get("events", [])):
        label = f"{kind}-event:{index}"
        if not isinstance(event, dict):
            checks.append(check(label, "FAIL", "Ledger event must be an object"))
            continue
        payload = {key: value for key, value in event.items() if key != "event_id"}
        event_id = event.get("event_id")
        valid_chain = event.get("previous_event_id") == expected_previous and event_id == _digest(payload)
        checks.append(check(f"{label}:chain", "PASS" if valid_chain else "FAIL", "Event hash and previous-event link are valid"))
        expected_previous = event_id
        stage_id = event.get("stage")
        stage_valid = stage_id in stages
        if stage_valid:
            stage_index = list(stages).index(stage_id)
            if event.get("decision") in {"AUTO_APPROVED", "HUMAN_APPROVED"}:
                stage_valid = stage_index >= last_approved_index
                last_approved_index = max(last_approved_index, stage_index)
        checks.append(check(f"{label}:stage", "PASS" if stage_valid else "FAIL", f"Stage order and identity: {stage_id!r}"))
        actor = event.get("decided_by")
        decision = event.get("decision")
        if kind == "agent":
            valid_actor = isinstance(actor, dict) and actor.get("type") == "agent" and decision in {"AUTO_APPROVED", "BLOCKED"}
            valid_actor = valid_actor and isinstance(actor.get("id"), str) and bool(actor["id"].strip()) and isinstance(actor.get("model"), str) and bool(actor["model"].strip())
            valid_actor = valid_actor and stage_id in stages and stages[stage_id].get("approval") == "agent"
        else:
            valid_actor = isinstance(actor, dict) and actor.get("type") == "human" and decision in {"HUMAN_APPROVED", "REJECTED"}
            valid_actor = valid_actor and isinstance(actor.get("id"), str) and bool(actor["id"].strip())
            valid_actor = valid_actor and stage_id in stages and stages[stage_id].get("approval") == "human"
        checks.append(check(f"{label}:actor", "PASS" if valid_actor else "FAIL", f"Decision {decision!r} is consistent with {kind} authority"))
        authority = event.get("authority")
        authority_type = "user-autonomy-policy" if kind == "agent" else "manual-decision"
        valid_authority = isinstance(authority, dict) and authority.get("type") == authority_type
        valid_authority = valid_authority and authority.get("policy_id") == policy["policy_id"] and authority.get("policy_sha256") == sha256_file(policy_path)
        checks.append(check(f"{label}:authority", "PASS" if valid_authority else "FAIL", "Authority is tied to the current policy"))
        evidence_valid = True
        for row in event.get("evidence", []):
            if not isinstance(row, dict) or not isinstance(row.get("path"), str) or not isinstance(row.get("sha256"), str):
                evidence_valid = False
                continue
            evidence_path = resolve_path(ledger_path.parent, row["path"])
            if not evidence_path.is_file() or sha256_file(evidence_path) != row["sha256"]:
                evidence_valid = False
        checks.append(check(f"{label}:evidence", "PASS" if evidence_valid else "FAIL", "Evidence files match recorded SHA-256 values"))
        concept_image_valid = True
        if stage_id == "concept" and decision in {"AUTO_APPROVED", "HUMAN_APPROVED"}:
            concept_image_valid = evidence_valid and _rows_include_concept_image(event.get("evidence", []), ledger_path.parent)
            checks.append(check(f"{label}:concept-image", "PASS" if concept_image_valid else "FAIL", "Concept approval binds a product concept image"))
        if kind == "agent" and decision == "AUTO_APPROVED" and stage_id in stages:
            stage = stages[stage_id]
            if stage.get("evidence_mode") == "agent-attestation":
                semantic_valid = isinstance(event.get("attestation"), str) and bool(event["attestation"].strip())
                if stage_id == "concept":
                    semantic_valid = semantic_valid and concept_image_valid
            else:
                semantic_valid = bool(event.get("evidence")) and evidence_valid
                for row in event.get("evidence", []):
                    if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                        semantic_valid = False
                        continue
                    evidence_path = resolve_path(ledger_path.parent, row["path"])
                    try:
                        evidence_report = load_data(evidence_path)
                    except Exception:
                        semantic_valid = False
                        continue
                    if not isinstance(evidence_report, dict) or evidence_report.get("status") != "PASS":
                        semantic_valid = False
                        continue
                    report_checks = evidence_report.get("checks")
                    if not isinstance(report_checks, list) or not report_checks:
                        semantic_valid = False
                    elif any(isinstance(item, dict) and item.get("required", True) and item.get("status") != "PASS" for item in report_checks):
                        semantic_valid = False
                    if stage.get("require_hashed_report_inputs"):
                        inputs = evidence_report.get("inputs")
                        if not isinstance(inputs, list) or not inputs or any(
                            not isinstance(item, dict) or not isinstance(item.get("sha256"), str) or HEX64.fullmatch(item["sha256"]) is None
                            for item in inputs
                        ):
                            semantic_valid = False
            checks.append(check(f"{label}:auto-semantics", "PASS" if semantic_valid else "FAIL", "AUTO_APPROVED is reproducible from the stage evidence rule"))
        if kind == "human" and decision == "HUMAN_APPROVED":
            proof = event.get("proof")
            proof_mode = policy.get("human_approval_proof")
            if proof_mode == "hmac-sha256":
                if human_secret_file is None or not human_secret_file.is_file():
                    checks.append(check(f"{label}:proof", "NOT_RUN", "Human signature requires the verifier's secret file"))
                else:
                    unsigned = {key: value for key, value in payload.items() if key != "proof"}
                    signed_hash = _digest(unsigned)
                    expected = hmac.new(human_secret_file.read_bytes(), signed_hash.encode("ascii"), hashlib.sha256).hexdigest()
                    valid_proof = isinstance(proof, dict) and proof.get("type") == "hmac-sha256"
                    valid_proof = valid_proof and proof.get("signed_payload_sha256") == signed_hash and hmac.compare_digest(str(proof.get("signature", "")), expected)
                    checks.append(check(f"{label}:proof", "PASS" if valid_proof else "FAIL", "Human HMAC proof is valid"))
            else:
                valid_proof = isinstance(proof, dict) and proof.get("type") == "manual-assertion"
                checks.append(check(f"{label}:proof", "PASS" if valid_proof else "FAIL", "Human decision is explicitly recorded as an unsigned manual assertion"))
    return checks


def validate_approvals(
    policy_path: Path,
    agent_ledger_path: Path,
    *,
    target_stage: str,
    human_ledger_path: Path | None = None,
    human_secret_file: Path | None = None,
    profile: str = "release",
) -> dict[str, Any]:
    policy_result = validate_policy(policy_path, profile)
    if policy_result["status"] != "PASS":
        return report("validate-approvals", [check("policy", policy_result["status"], "Autonomy policy is invalid")], inputs=[policy_path], profile=profile)
    policy = _policy_data(policy_path)
    stages = _stage_map(policy)
    if target_stage not in stages:
        return report("validate-approvals", [check("target-stage", "FAIL", f"Unknown target stage {target_stage!r}")], inputs=[policy_path], profile=profile)
    try:
        agent = _load_ledger(agent_ledger_path, "agent", policy, policy_path)
        human = _load_ledger(human_ledger_path, "human", policy, policy_path)
    except Exception as exc:
        return report("validate-approvals", [check("ledger", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[policy_path, agent_ledger_path], profile=profile)
    checks = _verify_ledger(agent, "agent", policy, policy_path, agent_ledger_path, human_secret_file)
    if human_ledger_path is not None and human_ledger_path.exists():
        checks.extend(_verify_ledger(human, "human", policy, policy_path, human_ledger_path, human_secret_file))
    state = _latest_state(agent, human)
    target_index = list(stages).index(target_stage)
    for stage_id in list(stages)[: target_index + 1]:
        expected = "AUTO_APPROVED" if stages[stage_id].get("approval") == "agent" else "HUMAN_APPROVED"
        actual = state.get(stage_id, "PENDING")
        checks.append(check(f"stage-state:{stage_id}", "PASS" if actual == expected else "REVIEW_REQUIRED", f"Expected {expected}, found {actual}"))
    return report(
        "validate-approvals",
        checks,
        inputs=[path for path in (policy_path, agent_ledger_path, human_ledger_path) if path is not None],
        profile=profile,
        metrics={"policy_id": policy["policy_id"], "mode": policy["mode"], "target_stage": target_stage, "stage_state": state},
        limitations=[
            "HMAC proves possession of the verifier-selected key, not a legal identity.",
            "Keep the human key outside every path and environment readable by the agent.",
            "Approval state does not grant tool permissions or start a printer.",
        ],
    )
