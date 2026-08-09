#!/usr/bin/env python3
"""Validate an operation-plan YAML/JSON against the supplied schema."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import dump_json, load_structured


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("plan")
    p.add_argument("--json-out")
    args = p.parse_args()
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("jsonschema is required: python -m pip install jsonschema") from exc
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "operation-plan.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = load_structured(args.plan)
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    report = {
        "file": str(Path(args.plan).resolve()),
        "valid": not errors,
        "errors": [{"path": list(e.path), "message": e.message} for e in errors],
    }
    print(dump_json(report, args.json_out))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
