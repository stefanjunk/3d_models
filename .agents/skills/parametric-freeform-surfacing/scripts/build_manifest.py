#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic package manifest and SHA-256 list.")
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checksums", type=Path, required=True)
    args = parser.parse_args()
    root = args.package_root.resolve()
    output = args.output.resolve()
    checksums = args.checksums.resolve()
    excluded_names = {output.name, checksums.name}
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in excluded_names or "__pycache__" in path.parts or "build" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        files.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest(path)})
    manifest = {
        "package": "opencode-parametric-freeform-surfacing",
        "version": "1.0.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "files": files,
    }
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksums.write_text("".join(f"{item['sha256']}  {item['path']}\n" for item in files), encoding="utf-8")
    print(f"Wrote {output} and {checksums} ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
