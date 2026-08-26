#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import resolve_manifest_path, save_json
from three_mf import write_multicolor_3mf


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble aligned color-part meshes into a standards-based multi-part 3MF.")
    parser.add_argument("--parts-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="Multicolor FDM assembly")
    parser.add_argument("--thumbnail", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.parts_manifest.read_text(encoding="utf-8"))
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        raise SystemExit("Manifest must contain a non-empty 'parts' list")
    normalized = []
    for part in parts:
        entry = dict(part)
        entry["path"] = str(resolve_manifest_path(args.parts_manifest.resolve(), str(part["path"])))
        normalized.append(entry)
    report = write_multicolor_3mf(normalized, args.output, title=args.title, thumbnail=args.thumbnail)
    report["manifest"] = str(args.parts_manifest.resolve())
    if args.report:
        save_json(args.report, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
