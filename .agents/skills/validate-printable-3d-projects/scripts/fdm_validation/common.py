from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable

from . import __version__

VALID_STATUS = {"PASS", "FAIL", "NOT_RUN", "REVIEW_REQUIRED"}


class ValidationInputError(ValueError):
    """Raised for a malformed validation contract or unsupported input."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise ValidationInputError(
            f"{path} is not JSON and PyYAML is unavailable; use JSON or install PyYAML"
        ) from exc
    return yaml.safe_load(text)


def write_json(path: Path | None, value: Any) -> str:
    rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return rendered


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def check(
    check_id: str,
    status: str,
    message: str,
    *,
    required: bool = True,
    metrics: dict[str, Any] | None = None,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    if status not in VALID_STATUS:
        raise ValidationInputError(f"invalid check status {status!r}")
    return {
        "id": check_id,
        "status": status,
        "required": bool(required),
        "message": message,
        "metrics": metrics or {},
        "evidence": evidence or [],
    }


def status_from_checks(checks: Iterable[dict[str, Any]], profile: str = "release") -> str:
    items = list(checks)
    if any(item.get("status") == "FAIL" for item in items):
        return "FAIL"
    required = [item for item in items if item.get("required", True)]
    if any(item.get("status") == "NOT_RUN" for item in required):
        return "NOT_RUN"
    if any(item.get("status") == "REVIEW_REQUIRED" for item in required):
        return "REVIEW_REQUIRED"
    if profile == "release" and any(item.get("status") != "PASS" for item in required):
        return "REVIEW_REQUIRED"
    return "PASS"


def report(
    tool: str,
    checks: list[dict[str, Any]],
    *,
    inputs: list[Path] | None = None,
    profile: str = "release",
    metrics: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
    capabilities: list[str] | None = None,
) -> dict[str, Any]:
    input_rows = []
    for path in inputs or []:
        row: dict[str, Any] = {"path": str(path.resolve())}
        if path.is_file():
            row.update({"sha256": sha256_file(path), "size_bytes": path.stat().st_size})
        else:
            row.update({"sha256": None, "size_bytes": None})
        input_rows.append(row)
    return {
        "schema_version": "1.0",
        "tool": tool,
        "tool_version": __version__,
        "profile": profile,
        "status": status_from_checks(checks, profile),
        "inputs": input_rows,
        "checks": checks,
        "metrics": metrics or {},
        "limitations": limitations or [],
        "required_capabilities": capabilities or [],
    }


def exit_code(status: str, profile: str = "release") -> int:
    if status == "PASS":
        return 0
    if profile == "draft" and status in {"NOT_RUN", "REVIEW_REQUIRED"}:
        return 0
    if status == "FAIL":
        return 1
    if status in {"NOT_RUN", "REVIEW_REQUIRED"}:
        return 2
    return 3


def resolve_path(base: Path, value: str | os.PathLike[str]) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else (base / candidate).resolve()


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationInputError(f"{label} must be an object")
    return value


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationInputError(f"{label} must be an array")
    return value


def unique_ids(items: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            raise ValidationInputError(f"{label}[{index}].id must be a non-empty string")
        if item_id in result:
            raise ValidationInputError(f"duplicate {label} id {item_id!r}")
        result[item_id] = item
    return result
