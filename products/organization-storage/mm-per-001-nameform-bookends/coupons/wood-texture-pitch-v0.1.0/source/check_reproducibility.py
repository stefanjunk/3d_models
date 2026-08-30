#!/usr/bin/env python3
"""Rebuild the coupon in a temporary directory and compare exact outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
COUPON_DIR = HERE.parent
GENERATOR = HERE / "generate_coupon.py"
SPEC = COUPON_DIR / "coupon-spec.json"
OUTPUTS = (
    "exports/DRAFT-nameform-wood-texture-pitch-coupon-v0.1.0.stl",
    "build/heightmaps/wood-001-pitch-0p45-16bit.png",
    "build/heightmaps/wood-001-pitch-0p50-16bit.png",
    "build/heightmaps/wood-001-pitch-0p60-16bit.png",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=COUPON_DIR / "reports" / "reproducibility.json",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run the comparison without writing a report file.",
    )
    args = parser.parse_args()
    report_path = args.report.resolve()
    if not args.check_only and report_path.exists():
        raise FileExistsError(f"refusing to overwrite existing report: {report_path}")

    with tempfile.TemporaryDirectory(prefix="nameform-wood-coupon-") as temporary:
        rebuilt_root = Path(temporary)
        process = subprocess.run(
            [
                sys.executable,
                str(GENERATOR),
                "--spec",
                str(SPEC),
                "--output-root",
                str(rebuilt_root),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        comparisons = []
        for relative in OUTPUTS:
            committed = COUPON_DIR / relative
            rebuilt = rebuilt_root / relative
            committed_hash = sha256(committed) if committed.is_file() else None
            rebuilt_hash = sha256(rebuilt) if rebuilt.is_file() else None
            comparisons.append(
                {
                    "path": relative,
                    "committed_sha256": committed_hash,
                    "rebuilt_sha256": rebuilt_hash,
                    "byte_identical": committed_hash is not None
                    and committed_hash == rebuilt_hash,
                }
            )

    passed = process.returncode == 0 and all(
        item["byte_identical"] for item in comparisons
    )
    report = {
        "schema_version": "1.0",
        "tool": "MM-PER-001 coupon reproducibility check",
        "status": "PASS" if passed else "FAIL",
        "profile": "draft",
        "inputs": [
            {"path": str(GENERATOR), "sha256": sha256(GENERATOR)},
            {"path": str(SPEC), "sha256": sha256(SPEC)},
            *[
                {
                    "path": str(COUPON_DIR / relative),
                    "sha256": sha256(COUPON_DIR / relative),
                }
                for relative in OUTPUTS
            ],
        ],
        "artifacts": [],
        "checks": [
            {
                "id": "generator-exit",
                "status": "PASS" if process.returncode == 0 else "FAIL",
                "actual": process.returncode,
            },
            *[
                {
                    "id": f"byte-identical:{item['path']}",
                    "status": "PASS" if item["byte_identical"] else "FAIL",
                    "committed_sha256": item["committed_sha256"],
                    "rebuilt_sha256": item["rebuilt_sha256"],
                }
                for item in comparisons
            ],
        ],
        "metrics": {"compared_outputs": len(comparisons)},
        "limitations": [
            "This check establishes deterministic digital regeneration only; physical surface appearance remains human-controlled."
        ],
    }
    if not args.check_only:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "report": None if args.check_only else str(report_path),
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
