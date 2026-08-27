#!/usr/bin/env python3
"""Create deterministic set hashes for the exact DRAFT release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def set_record(root: Path, paths: list[Path]) -> dict:
    records = []
    set_digest = hashlib.sha256()
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        file_hash = sha256(path)
        records.append({"path": relative, "bytes": path.stat().st_size, "sha256": file_hash})
        set_digest.update(relative.encode("utf-8"))
        set_digest.update(b"\0")
        set_digest.update(file_hash.encode("ascii"))
        set_digest.update(b"\n")
    return {"sha256": set_digest.hexdigest(), "fileCount": len(records), "files": records}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    source_paths = sorted((root / "src").glob("*.mjs")) + [
        root / "package.json",
        root / "package-lock.json",
        root / "assets/just-innovation-watermark/exports/dxf/just-innovation-compact.dxf",
    ]
    result = {
        "schemaVersion": 1,
        "revision": 3,
        "status": "DRAFT",
        "meshSet": set_record(root, list((root / "build/draft-r3/stl").glob("*.stl"))),
        "stepSet": set_record(root, list((root / "build/draft-r3/step").glob("*.step"))),
        "sourceSet": set_record(root, source_paths),
    }
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "meshSetSha256": result["meshSet"]["sha256"],
        "stepSetSha256": result["stepSet"]["sha256"],
        "sourceSetSha256": result["sourceSet"]["sha256"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
