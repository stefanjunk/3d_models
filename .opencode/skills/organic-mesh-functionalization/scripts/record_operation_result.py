#!/usr/bin/env python3
"""Validate and append an operation-result record to a project-local JSONL history."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import load_structured


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("record")
    p.add_argument("--history", default="validation/operation-history.jsonl")
    args = p.parse_args()
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("jsonschema is required") from exc
    skill = Path(__file__).resolve().parents[1]
    schema = json.loads((skill / "schemas" / "operation-result.schema.json").read_text(encoding="utf-8"))
    data = load_structured(args.record)
    jsonschema.Draft202012Validator(schema).validate(data)
    history = Path(args.history)
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, sort_keys=True) + "\n")
    print(history.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
