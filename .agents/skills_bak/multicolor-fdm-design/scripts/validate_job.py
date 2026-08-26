#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema

from common import load_yaml, save_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a multicolor-job YAML file.")
    parser.add_argument("job", type=Path)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    script_root = Path(__file__).resolve().parents[1]
    schema_path = args.schema or script_root / "assets/schemas/multicolor-job.schema.json"
    report = {"job": str(args.job), "schema": str(schema_path), "valid": False, "errors": []}
    try:
        job = load_yaml(args.job)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(job), key=lambda e: list(e.path))
        report["errors"] = [
            {"path": "/".join(str(p) for p in error.path), "message": error.message}
            for error in errors
        ]
        report["valid"] = not errors
    except Exception as exc:  # surfaced in machine-readable form
        report["errors"].append({"path": "", "message": f"{type(exc).__name__}: {exc}"})

    if args.json_out:
        save_json(args.json_out, report)
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
