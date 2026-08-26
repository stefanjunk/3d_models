#!/usr/bin/env python3
"""Create a deterministic-ish ZIP of the skill package."""
from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-root", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    root = args.package_root.resolve()
    output = args.output or root.parent / f"{root.name}.zip"
    skip_names = {"__pycache__", ".git"}
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_dir() or any(part in skip_names for part in path.parts):
                continue
            if path.resolve() == output.resolve():
                continue
            arc = path.relative_to(root.parent)
            info = zipfile.ZipInfo(str(arc).replace(os.sep, "/"), date_time=(2026, 8, 9, 0, 0, 0))
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
