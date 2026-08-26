from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from .common import ValidationInputError, check, load_data, report, resolve_path, sha256_file, unique_ids, write_json


def freeze_project(source: Path, output: Path, *, force: bool = False, profile: str = "release") -> dict[str, Any]:
    inputs = [source]
    if not source.is_file():
        return report("freeze-project", [check("project-file", "FAIL", f"Project not found: {source}")], inputs=inputs, profile=profile)
    if output.suffix.lower() != ".json":
        return report("freeze-project", [check("output-format", "FAIL", "Frozen project output must use .json")], inputs=inputs, profile=profile)
    if output.resolve() == source.resolve():
        return report("freeze-project", [check("non-destructive-output", "FAIL", "Refusing to overwrite the source project")], inputs=inputs, profile=profile)
    if output.parent.resolve() != source.parent.resolve():
        return report("freeze-project", [check("portable-path-base", "FAIL", "Write the frozen project beside the source so relative artifact paths retain meaning")], inputs=inputs, profile=profile)
    if output.exists() and not force:
        return report("freeze-project", [check("output-exists", "FAIL", f"Output already exists: {output}")], inputs=inputs, profile=profile)

    try:
        loaded = load_data(source)
        if not isinstance(loaded, dict):
            raise ValidationInputError("project root must be an object")
        project = loaded.get("project")
        if not isinstance(project, dict) or not isinstance(project.get("id"), str) or not isinstance(project.get("revision"), str):
            raise ValidationInputError("project.id and project.revision must be strings")
        if project.get("units") != "mm":
            raise ValidationInputError("project.units must be 'mm'")
        if project.get("risk_class") not in {"decorative", "normal-functional", "structural", "safety-critical"}:
            raise ValidationInputError("project.risk_class is invalid")
        artifact_rows = loaded.get("artifacts")
        if not isinstance(artifact_rows, list) or not artifact_rows:
            raise ValidationInputError("artifacts must be a non-empty array")
        unique_ids(artifact_rows, "artifact")
        check_rows = loaded.get("checks")
        if not isinstance(check_rows, list) or not check_rows:
            raise ValidationInputError("checks must be a non-empty array")
        unique_ids(check_rows, "check")
        release = loaded.get("release")
        if not isinstance(release, dict) or not isinstance(release.get("required_approvals"), list) or not isinstance(release.get("approvals"), dict):
            raise ValidationInputError("release requires required_approvals and approvals")
    except Exception as exc:
        return report("freeze-project", [check("project-contract", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=inputs, profile=profile)

    frozen = copy.deepcopy(loaded)
    checks: list[dict[str, Any]] = []
    artifact_metrics: dict[str, Any] = {}
    for artifact in frozen["artifacts"]:
        artifact_id = artifact["id"]
        required = bool(artifact.get("required", True))
        raw_path = artifact.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            checks.append(check(f"artifact:{artifact_id}:path", "FAIL", "Artifact path must be a non-empty string", required=required))
            continue
        if not isinstance(artifact.get("kind"), str) or not artifact.get("kind", "").strip():
            checks.append(check(f"artifact:{artifact_id}:kind", "FAIL", "Artifact kind must be a non-empty string", required=required))
            continue
        path = resolve_path(source.parent, raw_path)
        inputs.append(path)
        if not path.is_file():
            checks.append(check(f"artifact:{artifact_id}", "FAIL" if required else "NOT_RUN", f"Artifact not found: {path}", required=required))
            continue
        digest = sha256_file(path)
        artifact["sha256"] = digest
        artifact.setdefault("revision", project["revision"])
        artifact_metrics[artifact_id] = {"path": str(path), "sha256": digest, "revision": artifact["revision"]}
        checks.append(check(f"artifact:{artifact_id}", "PASS", "Artifact hash and revision frozen", required=required, metrics=artifact_metrics[artifact_id]))

    if any(item["status"] == "FAIL" for item in checks):
        return report("freeze-project", checks, inputs=inputs, profile=profile, metrics={"output": str(output), "artifacts": artifact_metrics})
    frozen["lock"] = {
        "schema_version": "1.0",
        "source_project_sha256": sha256_file(source),
        "tool": "validate-printable-3d-projects",
    }
    write_json(output, frozen)
    checks.append(check("frozen-project-written", "PASS", f"Wrote immutable artifact hashes to {output}", evidence=[str(output)]))
    return report("freeze-project", checks, inputs=inputs, profile=profile, metrics={"output": str(output.resolve()), "artifacts": artifact_metrics})
