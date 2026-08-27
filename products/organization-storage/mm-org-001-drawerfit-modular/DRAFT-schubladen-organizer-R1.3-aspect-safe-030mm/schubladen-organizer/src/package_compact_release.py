#!/usr/bin/env python3
"""Create a smaller ZIP without four STL copies already contained in the 3MF."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OMITTED_DUPLICATES = {
    "output/DRAFT/DRAFT-driver-front-textured.stl",
    "output/DRAFT/DRAFT-driver-back-textured.stl",
    "output/DRAFT/DRAFT-hardware-front-textured.stl",
    "output/DRAFT/DRAFT-hardware-back-textured.stl",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    params = json.loads((ROOT / "config" / "model-params.json").read_text(encoding="utf-8"))
    full_manifest_path = ROOT / "reports" / "release-package-manifest.json"
    full_manifest = json.loads(full_manifest_path.read_text(encoding="utf-8"))
    paths = [ROOT / item["path"] for item in full_manifest["files"] if item["path"] not in OMITTED_DUPLICATES]
    paths.extend([full_manifest_path])
    compact_manifest = {
        "schema_version": 1,
        "status": "DRAFT",
        "revision": params["model_revision"],
        "purpose": "compact transfer package",
        "included_manufacturing": "assembly 3MF plus accessory/coupon STLs",
        "omitted_duplicates": sorted(OMITTED_DUPLICATES),
        "recovery": "The four omitted module STLs are present as meshes in the assembly 3MF and can also be regenerated with python3 rebuild.py.",
    }
    compact_manifest_path = ROOT / "reports" / "compact-package-manifest.json"
    compact_manifest_path.write_text(json.dumps(compact_manifest, indent=2) + "\n", encoding="utf-8")
    paths.append(compact_manifest_path)
    paths = sorted(set(paths))
    destination = ROOT.parent / "DRAFT-schubladen-organizer-R1.3-aspect-safe-030mm-compact.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
        for path in paths:
            archive.write(path, Path("schubladen-organizer") / path.relative_to(ROOT))
    with zipfile.ZipFile(destination) as archive:
        bad = archive.testzip()
        entries = len(archive.namelist())
    result = {
        "status": "PASS" if bad is None else "FAIL",
        "file": str(destination),
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "entries": entries,
        "bad_file": bad,
    }
    print(json.dumps(result, indent=2))
    if bad is not None:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
