#!/usr/bin/env python3
"""Validate a documented 3D design preflight result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = SKILL_ROOT / "schemas"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_validator() -> Draft202012Validator:
    result_schema = load_json(SCHEMA_ROOT / "preflight-result.schema.json")
    interface_schema = load_json(SCHEMA_ROOT / "interface-contract.schema.json")
    registry = Registry().with_resource(
        interface_schema["$id"],
        Resource.from_contents(interface_schema),
    )
    return Draft202012Validator(
        result_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def error_path(error: Any) -> str:
    path = ".".join(str(item) for item in error.absolute_path)
    return path or "$"


def validate_document(
    document: Any,
    *,
    expected_project_id: str | None = None,
    expected_project_revision: str | None = None,
) -> tuple[list[str], list[str]]:
    errors = [
        f"{error_path(error)}: {error.message}"
        for error in sorted(
            build_validator().iter_errors(document),
            key=lambda item: tuple(str(part) for part in item.absolute_path),
        )
    ]
    warnings: list[str] = []
    if not isinstance(document, dict):
        return errors, warnings

    traceability = document.get("traceability")
    if isinstance(traceability, dict):
        if expected_project_id is not None and traceability.get("project_id") != expected_project_id:
            errors.append(
                "traceability.project_id does not match expected project id "
                f"{expected_project_id!r}"
            )
        if (
            expected_project_revision is not None
            and traceability.get("project_revision") != expected_project_revision
        ):
            errors.append(
                "traceability.project_revision does not match expected project revision "
                f"{expected_project_revision!r}"
            )
        if (
            traceability.get("mode") == "RETROSPECTIVE"
            and "backfill_missing_preflight" not in traceability.get("change_triggers", [])
            and traceability.get("previous_assessment_id") is None
        ):
            errors.append(
                "initial RETROSPECTIVE assessment must include "
                "backfill_missing_preflight in traceability.change_triggers"
            )

    decision = document.get("decision")
    if isinstance(decision, dict) and decision.get("design_release") in {"HOLD", "CONCEPT_ONLY"}:
        warnings.append(
            "preflight is structurally valid but its decision blocks production design release"
        )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    parser.add_argument("--project-id")
    parser.add_argument("--project-revision")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    try:
        document = load_json(args.result)
        errors, warnings = validate_document(
            document,
            expected_project_id=args.project_id,
            expected_project_revision=args.project_revision,
        )
    except (OSError, json.JSONDecodeError) as exc:
        document = None
        errors = [str(exc)]
        warnings = []

    decision = document.get("decision") if isinstance(document, dict) else None
    report = {
        "validator": "3d-design-preflight",
        "result": str(args.result.resolve()),
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
        "decision": decision if isinstance(decision, dict) else None,
    }
    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
