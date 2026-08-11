#!/usr/bin/env python3
"""Manage a versioned local printed/purchased/hybrid parts library."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import DATA_ROOT

DEFAULT_LIBRARY = DATA_ROOT / "parts-library.json"
VALID_STATUS = {"concept", "experimental", "qualified-local", "deprecated"}


def load_library(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"_meta": {"version": "1.0.0", "status_definitions": sorted(VALID_STATUS)}, "parts": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_library(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def find_part(data: dict[str, Any], part_id: str) -> dict[str, Any] | None:
    return next((p for p in data.get("parts", []) if p.get("part_id") == part_id), None)


def validate_entry(entry: dict[str, Any]) -> list[str]:
    errors = []
    for key in ["part_id", "revision", "status", "source_type", "category"]:
        if not entry.get(key):
            errors.append(f"missing {key}")
    if entry.get("status") not in VALID_STATUS:
        errors.append(f"invalid status: {entry.get('status')}")
    if entry.get("source_type") not in {"printed", "purchased", "hybrid"}:
        errors.append("source_type must be printed, purchased, or hybrid")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("list")
    s = sub.add_parser("search")
    s.add_argument("query")
    a = sub.add_parser("add")
    a.add_argument("--entry", required=True, type=Path)
    v = sub.add_parser("validate")
    v.add_argument("--part-id")
    pr = sub.add_parser("promote")
    pr.add_argument("--part-id", required=True)
    pr.add_argument("--status", required=True, choices=sorted(VALID_STATUS))
    args = p.parse_args()

    data = load_library(args.library)

    if args.command == "init":
        save_library(args.library, data)
        print(args.library)
        return 0
    if args.command == "list":
        print(json.dumps(data.get("parts", []), indent=2, ensure_ascii=False))
        return 0
    if args.command == "search":
        q = args.query.lower()
        matches = []
        for entry in data.get("parts", []):
            haystack = json.dumps(entry, ensure_ascii=False).lower()
            if q in haystack:
                matches.append(entry)
        print(json.dumps(matches, indent=2, ensure_ascii=False))
        return 0
    if args.command == "add":
        entry = json.loads(args.entry.read_text(encoding="utf-8"))
        errors = validate_entry(entry)
        if errors:
            print(json.dumps({"passed": False, "errors": errors}, indent=2))
            return 1
        if find_part(data, entry["part_id"]):
            print(json.dumps({"passed": False, "errors": ["part_id already exists"]}, indent=2))
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
        reports = [{"part_id": e.get("part_id"), "errors": validate_entry(e)} for e in entries]
        passed = all(not r["errors"] for r in reports)
        print(json.dumps({"passed": passed, "reports": reports}, indent=2))
        return 0 if passed else 1
    if args.command == "promote":
        entry = find_part(data, args.part_id)
        if not entry:
            print(json.dumps({"passed": False, "errors": ["part not found"]}, indent=2))
            return 1
        if args.status == "qualified-local":
            if not entry.get("validation"):
                print(json.dumps({"passed": False, "errors": ["qualification requires linked validation"]}, indent=2))
                return 1
            if not entry.get("test_evidence"):
                print(json.dumps({"passed": False, "errors": ["qualification requires linked test evidence"]}, indent=2))
                return 1
            process = entry.get("material_process", {})
            required = ["printer", "material", "nozzle_mm", "profile_id"]
            missing = [k for k in required if not process.get(k)]
            if missing:
                print(json.dumps({"passed": False, "errors": [f"qualification missing material_process fields: {missing}"]}, indent=2))
                return 1
        entry["status"] = args.status
        save_library(args.library, data)
        print(json.dumps({"passed": True, "part_id": args.part_id, "status": args.status}, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
