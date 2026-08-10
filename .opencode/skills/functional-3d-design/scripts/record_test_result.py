#!/usr/bin/env python3
"""Append a physical test result and link it to a local part entry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part-id", required=True)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--library", type=Path, default=SKILL_ROOT / "data" / "parts-library.json")
    parser.add_argument("--log", type=Path, default=SKILL_ROOT / "data" / "test-results.jsonl")
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    result.setdefault("recorded_at", dt.datetime.now(dt.timezone.utc).isoformat())
    result["part_id"] = args.part_id
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False) + "\n")

    library = json.loads(args.library.read_text(encoding="utf-8"))
    entry = next((item for item in library.get("parts", []) if item.get("part_id") == args.part_id), None)
    if entry is None:
        print(json.dumps({"passed": False, "error": "part not found", "log": str(args.log)}, indent=2))
        return 1
    reference = {
        "path": str(args.result),
        "evidence_type": "physical-test",
        "sha256": hashlib.sha256(args.result.read_bytes()).hexdigest(),
        "passed": result.get("passed") is True,
        "recorded_at": result["recorded_at"],
        "part_revision": result.get("part_revision"),
        "material_process": result.get("material_process", {}),
        "measurements": result.get("measurements", {}),
    }
    if reference not in entry.setdefault("test_evidence", []):
        entry["test_evidence"].append(reference)
    args.library.write_text(json.dumps(library, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "part_id": args.part_id, "log": str(args.log)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
