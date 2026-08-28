#!/usr/bin/env python3
"""Create a deterministic-ish ZIP of the skill package."""
from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path


METRIMADE_WATERMARK_FILES = (
    "README.md",
    "RIGHTS-NOTICE.md",
    "THIRD-PARTY-NOTICES.md",
    "design-spec.yaml",
    "provenance.json",
    "source/metrimade-watermark.scad",
    "test-plan.yaml",
    "tools/generate_watermark.py",
    "validation/physical-test-record.csv",
    "validation/concept-r2-watermark-tiers.svg",
    "validation/concept-r2-watermark-tiers.png",
    "validation/validation-report.md",
)


def add_file(zf: zipfile.ZipFile, source: Path, archive_path: Path) -> None:
    info = zipfile.ZipInfo(str(archive_path).replace(os.sep, "/"), date_time=(2026, 8, 9, 0, 0, 0))
    info.external_attr = (source.stat().st_mode & 0xFFFF) << 16
    zf.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package-root", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    root = args.package_root.resolve()
    output = args.output or root.parent / f"{root.name}.zip"
    workspace_watermark = root.parents[2] / "tools" / "metrimade-watermark"
    missing_watermark = [
        relative
        for relative in METRIMADE_WATERMARK_FILES
        if not (workspace_watermark / relative).is_file()
    ]
    if missing_watermark:
        raise SystemExit(
            "Cannot package functional-3d-design without MM-WM-001-R2 files: "
            + ", ".join(missing_watermark)
        )
    skip_names = {"__pycache__", ".git"}
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_dir() or any(part in skip_names for part in path.parts):
                continue
            if path.resolve() == output.resolve():
                continue
            arc = path.relative_to(root.parent)
            add_file(zf, path, arc)
        for relative in METRIMADE_WATERMARK_FILES:
            add_file(
                zf,
                workspace_watermark / relative,
                Path(root.name) / "assets" / "metrimade-watermark" / relative,
            )
    print(output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
