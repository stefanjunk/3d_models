#!/usr/bin/env python3
"""Manage the evidence-backed local functional-part library."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = SKILL_ROOT / "data" / "parts-library.json"
VALID_STATUS = {"concept", "experimental", "qualified-local", "deprecated"}


def load_library(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_meta": {"version": "1.0.0", "status_definitions": sorted(VALID_STATUS)}, "parts": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_library(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def find_part(data: dict[str, Any], part_id: str) -> dict[str, Any] | None:
    return next((part for part in data.get("parts", []) if part.get("part_id") == part_id), None)


def validate_entry(entry: dict[str, Any]) -> list[str]:
    errors = [
        f"missing {key}"
        for key in ("part_id", "revision", "status", "source_type", "category")
        if not entry.get(key)
    ]
    if entry.get("status") not in VALID_STATUS:
        errors.append(f"invalid status: {entry.get('status')}")
    if entry.get("source_type") not in {"printed", "purchased", "hybrid"}:
        errors.append("source_type must be printed, purchased, or hybrid")
    return errors


def evidence_path_errors(
    item: dict[str, Any],
    evidence_root: Path,
    expected_type: str,
    require_measurements: bool,
    expected_revision: str,
    expected_process: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if item.get("evidence_type") != expected_type:
        errors.append(f"evidence_type must be {expected_type}")
    path_value = item.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        return [*errors, "evidence path is required"]
    path = (evidence_root / path_value).resolve()
    if not path.is_relative_to(evidence_root.resolve()):
        return [*errors, "evidence path escapes evidence root"]
    if not path.is_file():
        return [*errors, "evidence file does not exist"]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if item.get("sha256") != digest:
        errors.append("evidence sha256 mismatch")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return [*errors, "evidence report must be valid JSON"]
    if not isinstance(report, dict):
        return [*errors, "evidence report must be a JSON object"]
    if report.get("passed") is not True:
        errors.append("evidence report did not pass")
    if report.get("part_revision") != expected_revision:
        errors.append("evidence report part_revision mismatch")
    report_process = report.get("material_process", {})
    if not all(
        report_process.get(key) == expected_process.get(key)
        for key in ("printer", "material", "nozzle_mm", "profile_id")
    ):
        errors.append("evidence report material_process mismatch")
    if require_measurements and not isinstance(report.get("measurements"), dict):
        errors.append("physical-test report requires measurements")
    elif require_measurements and not report.get("measurements"):
        errors.append("physical-test report requires nonempty measurements")
    return errors


def qualification_errors(entry: dict[str, Any], evidence_root: Path) -> list[str]:
    process = entry.get("material_process", {})
    missing = [
        key
        for key in ("printer", "material", "nozzle_mm", "profile_id")
        if not process.get(key)
    ]
    errors = [f"qualification missing material_process fields: {missing}"] if missing else []
    revision = entry.get("revision")
    matching_validation = []
    for item in entry.get("validation") or []:
        matches = item.get("passed") is True and item.get("part_revision") == revision
        matches = matches and all(
            item.get("material_process", {}).get(key) == process.get(key)
            for key in ("printer", "material", "nozzle_mm", "profile_id")
        )
        if matches and not evidence_path_errors(
            item, evidence_root, "geometry-validation", False, str(revision), process
        ):
            matching_validation.append(item)
    matching_tests = []
    for item in entry.get("test_evidence") or []:
        matches = item.get("passed") is True and item.get("part_revision") == revision
        matches = matches and all(
            item.get("material_process", {}).get(key) == process.get(key)
            for key in ("printer", "material", "nozzle_mm", "profile_id")
        )
        if matches and not evidence_path_errors(
            item, evidence_root, "physical-test", True, str(revision), process
        ):
            matching_tests.append(item)
    if not matching_validation:
        errors.append("no passing validation matches part revision and material process")
    if not matching_tests:
        errors.append("no passing test matches part revision and material process")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--evidence-root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("list")
    search = commands.add_parser("search")
    search.add_argument("query")
    add = commands.add_parser("add")
    add.add_argument("--entry", required=True, type=Path)
    validate = commands.add_parser("validate")
    validate.add_argument("--part-id")
    promote = commands.add_parser("promote")
    promote.add_argument("--part-id", required=True)
    promote.add_argument("--status", required=True, choices=sorted(VALID_STATUS))
    args = parser.parse_args()

    data = load_library(args.library)
    if args.command == "init":
        save_library(args.library, data)
        print(args.library)
        return 0
    if args.command == "list":
        print(json.dumps(data.get("parts", []), indent=2, ensure_ascii=False))
        return 0
    if args.command == "search":
        query = args.query.lower()
        matches = [part for part in data.get("parts", []) if query in json.dumps(part).lower()]
        print(json.dumps(matches, indent=2, ensure_ascii=False))
        return 0
    if args.command == "add":
        entry = json.loads(args.entry.read_text(encoding="utf-8"))
        errors = validate_entry(entry)
        if entry.get("status") == "qualified-local":
            errors.append("qualified-local can be reached only through promote")
        if find_part(data, str(entry.get("part_id"))):
            errors.append("part_id already exists")
        if errors:
            print(json.dumps({"passed": False, "errors": errors}, indent=2))
            return 1
        entry.setdefault("validation", [])
        entry.setdefault("test_evidence", [])
        data.setdefault("parts", []).append(entry)
        save_library(args.library, data)
        print(json.dumps({"passed": True, "part_id": entry["part_id"]}, indent=2))
        return 0
    if args.command == "validate":
        entries = data.get("parts", [])
        if args.part_id:
            entry = find_part(data, args.part_id)
            if not entry:
                print(json.dumps({"passed": False, "errors": ["part not found"]}, indent=2))
                return 1
            entries = [entry]
        reports = []
        for entry in entries:
            errors = validate_entry(entry)
            if entry.get("status") == "qualified-local":
                errors.extend(qualification_errors(entry, args.evidence_root))
            reports.append({"part_id": entry.get("part_id"), "errors": errors})
        passed = all(not report["errors"] for report in reports)
        print(json.dumps({"passed": passed, "reports": reports}, indent=2))
        return 0 if passed else 1
    entry = find_part(data, args.part_id)
    if not entry:
        print(json.dumps({"passed": False, "errors": ["part not found"]}, indent=2))
        return 1
    if args.status == "qualified-local":
        errors = qualification_errors(entry, args.evidence_root)
        if errors:
            print(json.dumps({"passed": False, "errors": errors}, indent=2))
            return 1
    entry["status"] = args.status
    save_library(args.library, data)
    print(json.dumps({"passed": True, "part_id": args.part_id, "status": args.status}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
