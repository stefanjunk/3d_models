#!/usr/bin/env python3
"""Build a SHA-256 package manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import sha256_file


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-root", type=Path, required=True)
    p.add_argument("--output", default="PACKAGE_MANIFEST.json")
    args = p.parse_args()
    root = args.package_root.resolve()
    output = root / args.output
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        files.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    payload = {"package": root.name, "file_count": len(files), "files": files}
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
