#!/usr/bin/env python3
"""Append a test result and link it to a local parts-library entry."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from common import DATA_ROOT


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--part-id", required=True)
    p.add_argument("--result", required=True, type=Path, help="JSON result file")
    p.add_argument("--library", type=Path, default=DATA_ROOT / "parts-library.json")
    p.add_argument("--log", type=Path, default=DATA_ROOT / "test-results.jsonl")
    args = p.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    result.setdefault("recorded_at", dt.datetime.now(dt.timezone.utc).isoformat())
    result["part_id"] = args.part_id
    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(result, ensure_ascii=False) + "\n")

    library = json.loads(args.library.read_text(encoding="utf-8"))
    entry = next((x for x in library.get("parts", []) if x.get("part_id") == args.part_id), None)
    if entry is None:
        print(json.dumps({"passed": False, "error": "part not found", "log": str(args.log)}, indent=2))
        return 1
    evidence = entry.setdefault("test_evidence", [])
    reference = {"path": str(args.result), "passed": bool(result.get("passed")), "recorded_at": result["recorded_at"]}
    if reference not in evidence:
        evidence.append(reference)
    args.library.write_text(json.dumps(library, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": True, "part_id": args.part_id, "log": str(args.log)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
