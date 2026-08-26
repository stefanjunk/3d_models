#!/usr/bin/env python3
"""Write a SHA-256 package inventory for provenance and reproducibility."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-root", type=Path, default=Path.cwd())
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    root = args.package_root.resolve()
    out = (args.out or root / "PACKAGE_MANIFEST.json").resolve()
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() or "__pycache__" in path.parts or ".git" in path.parts:
            continue
        if path.resolve() == out:
            continue
        files.append({
            "path": str(path.relative_to(root)).replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    data = {
        "package": root.name,
        "version": "1.0.0",
        "created_utc_date": "2026-08-09",
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "files": files,
    }
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
