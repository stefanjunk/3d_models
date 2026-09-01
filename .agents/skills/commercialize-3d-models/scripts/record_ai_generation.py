#!/usr/bin/env python3
"""Attach a hashed AI generation run record to commercial provenance history."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot parse {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TypeError(f"{label} must contain a JSON object: {path}")
    return value


def atomic_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return slug[:64] or "generation-run"


def verify_hash(value: Any, label: str) -> str:
    text = str(value or "").strip().lower()
    if not HASH_RE.fullmatch(text):
        raise RuntimeError(f"{label} does not contain a valid SHA-256")
    return text


def verify_linked_file(record_dir: Path, item: dict[str, Any], label: str) -> None:
    raw_path = item.get("archived_path") or item.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise RuntimeError(f"{label} has no archived_path/path")
    path = Path(raw_path)
    if not path.is_absolute():
        path = record_dir / path
    path = path.resolve()
    if not path.is_file():
        raise RuntimeError(f"{label} linked file is missing: {path}")
    expected = verify_hash(item.get("sha256"), f"{label}.sha256")
    if sha256_file(path) != expected:
        raise RuntimeError(f"{label} linked-file SHA-256 does not match: {path}")


def validate_generation_record(
    path: Path, record: dict[str, Any], allow_failed: bool
) -> None:
    status = str(record.get("status") or "").strip().lower()
    if status != "succeeded" and not (allow_failed and status == "failed"):
        raise RuntimeError(
            "generation record status must be succeeded; use --allow-failed to archive a failed attempt"
        )
    if not record.get("run_id") or not record.get("operation"):
        raise RuntimeError("generation record needs run_id and operation")
    provider = record.get("provider")
    if not isinstance(provider, (str, dict)) or not provider:
        raise RuntimeError("generation record needs a provider string or object")
    input_item = record.get("input")
    if not isinstance(input_item, dict):
        raise TypeError("generation record needs an input object")
    verify_linked_file(path.parent, input_item, "input")
    outputs = record.get("outputs")
    if status == "succeeded":
        if not isinstance(outputs, list) or not outputs:
            raise RuntimeError("successful generation record needs output files")
        for index, item in enumerate(outputs):
            if not isinstance(item, dict):
                raise TypeError(f"output {index} is not an object")
            verify_linked_file(path.parent, item, f"output {index}")


def append_unique(values: list[Any], value: str) -> None:
    if value not in values:
        values.append(value)


def optional_list(container: dict[str, Any], key: str) -> list[Any]:
    value = container.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError(f"provenance ai_use.{key} must be a list")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Commercial clearance root")
    parser.add_argument("run_record", type=Path, help="AI/Step1X run JSON")
    parser.add_argument("--provider", required=True)
    parser.add_argument(
        "--role", action="append", required=True, help="Repeat for each AI role"
    )
    parser.add_argument("--allow-failed", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    run_path = args.run_record.expanduser().resolve()
    provenance_path = project / "07-release" / "provenance.json"
    evidence_dir = project / "02-tools" / "evidence" / "ai-generation"
    if not project.is_dir() or not provenance_path.is_file():
        print(
            f"ERROR: commercial clearance workspace/provenance not found: {project}",
            file=sys.stderr,
        )
        return 2
    if not run_path.is_file():
        print(f"ERROR: run record not found: {run_path}", file=sys.stderr)
        return 2
    if not args.provider.strip() or any(not role.strip() for role in args.role):
        print("ERROR: provider and roles must not be empty", file=sys.stderr)
        return 2
    try:
        run_record = read_object(run_path, "generation record")
        validate_generation_record(run_path, run_record, args.allow_failed)
        provenance = read_object(provenance_path, "provenance manifest")
        record_hash = sha256_file(run_path)
        run_id = str(run_record.get("run_id") or run_path.stem)
        destination_relative = Path("02-tools/evidence/ai-generation") / (
            f"{record_hash[:12]}-{safe_slug(run_id)}.json"
        )
        destination = project / destination_relative
        evidence_dir.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if sha256_file(destination) != record_hash:
                raise RuntimeError(f"evidence destination collision: {destination}")
        else:
            shutil.copy2(run_path, destination)
        if sha256_file(destination) != record_hash:
            raise RuntimeError("copied generation evidence failed its SHA-256 check")

        ai = provenance.get("ai_use")
        if ai is None:
            ai = {}
            provenance["ai_use"] = ai
        elif not isinstance(ai, dict):
            raise RuntimeError("provenance ai_use must be an object")
        ai["used"] = "yes"
        roles = optional_list(ai, "roles")
        providers = optional_list(ai, "providers")
        for role in args.role:
            append_unique(roles, role)
        append_unique(providers, args.provider)
        ai["roles"] = roles
        ai["providers"] = providers
        history = optional_list(ai, "generation_records")
        entry = {
            "provider": args.provider,
            "roles": list(dict.fromkeys(args.role)),
            "record_path": destination_relative.as_posix(),
            "sha256": record_hash,
            "run_id": run_id,
            "run_status": run_record.get("status"),
        }
        existing = [
            item
            for item in history
            if isinstance(item, dict)
            and str(item.get("sha256") or "").lower() == record_hash
        ]
        if not existing:
            history.append(entry)
        ai["generation_records"] = history
        atomic_json(provenance_path, provenance)
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        return 0
    except (RuntimeError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
