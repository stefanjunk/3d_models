#!/usr/bin/env python3
"""Run the vendor-aware 3MF geometry validator for revision 0.5.3."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[2]
ENGINE = PRODUCT / "source" / "v0.5.0" / "berlin" / "validate_anycubic_project_geometry.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-3mf", type=Path, required=True)
    parser.add_argument("--packaging-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite existing report: {args.output}")
    spec = importlib.util.spec_from_file_location("mm_art_010_validate_v053_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validation engine: {ENGINE}")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    original_argv = __import__("sys").argv
    temporary = args.output.with_suffix(".engine.tmp.json")
    if temporary.exists():
        raise SystemExit(f"refusing to overwrite temporary report: {temporary}")
    try:
        __import__("sys").argv = [
            str(ENGINE),
            "--project-3mf", str(args.project_3mf),
            "--packaging-report", str(args.packaging_report),
            "--output", str(temporary),
        ]
        engine.main()
    finally:
        __import__("sys").argv = original_argv
    report = json.loads(temporary.read_text())
    report["revision"] = "0.5.3"
    report["input_hashes"] = {
        "project_3mf": sha256(args.project_3mf),
        "packaging_report": sha256(args.packaging_report),
    }
    report["validator"] = {
        "wrapper": str(Path(__file__).resolve()),
        "wrapper_sha256": sha256(Path(__file__).resolve()),
        "validated_engine": str(ENGINE.resolve()),
        "validated_engine_sha256": sha256(ENGINE),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    temporary.unlink()
    print(json.dumps({"status": report["status"], "report": str(args.output), "totals": report["totals"]}))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
