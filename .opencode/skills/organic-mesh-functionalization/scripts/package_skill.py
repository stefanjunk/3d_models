#!/usr/bin/env python3
"""Validate and zip the package without caches or generated scratch files."""
from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-root", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    root = args.package_root.resolve()
    skill = root / ".opencode" / "skills" / "organic-mesh-functionalization"
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(skill / "tests"), "-v"], check=True, cwd=root)
    subprocess.run([sys.executable, str(skill / "scripts" / "build_manifest.py"), "--package-root", str(root)], check=True)
    out = args.output or root.with_suffix(".zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            z.write(path, arcname=str(Path(root.name) / path.relative_to(root)))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
