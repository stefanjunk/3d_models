#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


root = Path(__file__).resolve().parents[1]
files = {}
for path in sorted(root.rglob("*")):
    relative = path.relative_to(root)
    if not path.is_file() or relative == Path("build/manifest.json") or "__pycache__" in relative.parts or path.suffix == ".pyc":
        continue
    files[str(relative)] = {"sha256": sha256(path), "bytes": path.stat().st_size}
(root / "build/manifest.json").write_text(json.dumps({"schema_version": "1.0", "files": files}, indent=2) + "\n")
print(json.dumps({"status": "PASS", "files": len(files)}))
