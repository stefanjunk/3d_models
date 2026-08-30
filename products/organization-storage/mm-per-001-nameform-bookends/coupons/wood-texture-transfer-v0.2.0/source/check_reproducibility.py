#!/usr/bin/env python3
"""Rebuild the direct-transfer artifacts and compare their exact hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


JOB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[6]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=JOB_ROOT / "reports/reproducibility-report.json",
    )
    args = parser.parse_args()
    canonical = {
        "blend24": JOB_ROOT / "build/wood-001-tile-16bit-blend24.png",
        "coupon": JOB_ROOT / "exports/DRAFT-nameform-wood-direct-transfer-coupon-v0.2.0.stl",
        "nameform_left": JOB_ROOT
        / "exports/nameform/DRAFT-nameform-STE-FAN-left-wood-direct-v0.3.0-tx0.2.0.stl",
        "nameform_right": JOB_ROOT
        / "exports/nameform/DRAFT-nameform-STE-FAN-right-wood-direct-v0.3.0-tx0.2.0.stl",
    }
    relative = {key: path.relative_to(JOB_ROOT) for key, path in canonical.items()}
    with tempfile.TemporaryDirectory(prefix="nameform-wood-transfer-repro-") as temp:
        rebuilt_root = Path(temp)
        command = [
            sys.executable,
            str(JOB_ROOT / "source/generate_transfer.py"),
            "--spec",
            str(JOB_ROOT / "transfer-spec.json"),
            "--output-root",
            str(rebuilt_root),
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        comparisons = []
        for artifact_id, canonical_path in canonical.items():
            rebuilt_path = rebuilt_root / relative[artifact_id]
            canonical_hash = sha256(canonical_path) if canonical_path.is_file() else None
            rebuilt_hash = sha256(rebuilt_path) if rebuilt_path.is_file() else None
            comparisons.append(
                {
                    "artifact_id": artifact_id,
                    "canonical_path": str(canonical_path),
                    "canonical_sha256": canonical_hash,
                    "rebuilt_sha256": rebuilt_hash,
                    "exact_match": canonical_hash is not None and canonical_hash == rebuilt_hash,
                }
            )
    checks = {
        "generator_exit_zero": completed.returncode == 0,
        "exact_artifact_hashes": all(item["exact_match"] for item in comparisons),
    }
    report = {
        "schema_version": "1.0",
        "tool": "MM-PER-001 direct wood transfer reproducibility check",
        "tool_version": "0.2.0",
        "profile": "draft",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "inputs": [
            {
                "path": str(JOB_ROOT / "source/generate_transfer.py"),
                "sha256": sha256(JOB_ROOT / "source/generate_transfer.py"),
            },
            {
                "path": str(JOB_ROOT / "transfer-spec.json"),
                "sha256": sha256(JOB_ROOT / "transfer-spec.json"),
            },
            {
                "path": str(
                    REPO_ROOT / "libraries/surface-textures/wood-001/master/wood-001-tile-16bit.png"
                ),
                "sha256": sha256(
                    REPO_ROOT / "libraries/surface-textures/wood-001/master/wood-001-tile-16bit.png"
                ),
            },
        ],
        "checks": checks,
        "comparisons": comparisons,
        "generator_return_code": completed.returncode,
        "limitations": [
            "Exact reproduction is scoped to the current local Python, Pillow, Trimesh, Manifold3D and CadQuery environment."
        ],
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    if args.json_out.exists():
        raise FileExistsError(f"refusing to overwrite {args.json_out}")
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": checks}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
