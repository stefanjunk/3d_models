#!/usr/bin/env python3
"""Create or verify the deterministic package manifest and SHA-256 list."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PACKAGE_MANIFEST.json"
CHECKSUMS = ROOT / "CHECKSUMS.sha256"
EXCLUDED_FROM_MANIFEST = {"PACKAGE_MANIFEST.json", "CHECKSUMS.sha256"}
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_files(*, include_manifest: bool) -> list[Path]:
    excluded = {"CHECKSUMS.sha256"}
    if not include_manifest:
        excluded.add("PACKAGE_MANIFEST.json")
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name not in excluded
        and not any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts)
        and path.suffix != ".pyc"
    )


def manifest_data() -> dict:
    catalog = json.loads((ROOT / "catalog/catalog.json").read_text(encoding="utf-8"))
    design_spec = yaml.safe_load((ROOT / "design-spec.yaml").read_text(encoding="utf-8"))
    provenance = design_spec.get("provenance", {})
    base_release = provenance.get("base_release", {})
    draft_checkpoint = provenance.get("draft_checkpoint", {})
    if not (
        base_release.get("version") == "1.0.0"
        and base_release.get("release_date")
        and draft_checkpoint.get("revision") == design_spec.get("project", {}).get("revision")
        and draft_checkpoint.get("artifact_date")
        and draft_checkpoint.get("status") == design_spec.get("project", {}).get("release_status")
        and draft_checkpoint.get("final") is False
    ):
        raise ValueError("design-spec.yaml has incomplete or inconsistent base-release/DRAFT-checkpoint provenance")
    files = package_files(include_manifest=False)
    entries = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    extensions = Counter(path.suffix or "[none]" for path in files)
    return {
        "name": "FDM Mechanics Library",
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "spec_revision": design_spec.get("project", {}).get("revision"),
        "package_status": design_spec.get("project", {}).get("release_status"),
        "base_release_provenance": {
            "version": base_release["version"],
            "release_date": str(base_release["release_date"]),
        },
        "draft_artifact_checkpoint": {
            "revision": draft_checkpoint["revision"],
            "artifact_date": str(draft_checkpoint["artifact_date"]),
            "status": draft_checkpoint["status"],
            "final": False,
        },
        "sample_count": len(catalog),
        "family_count": len({record["family_number"] for record in catalog}),
        "print_plate_stl_count": len(list((ROOT / "samples").glob("**/print_plate.stl"))),
        "separated_part_stl_count": len(list((ROOT / "samples").glob("**/parts/part_*.stl"))),
        "preview_count": len(list((ROOT / "samples").glob("**/preview.png"))),
        "parametric_script_count": len(list((ROOT / "samples").glob("**/model.scad"))),
        "file_count_excluding_manifest_and_checksum": len(files),
        "total_size_bytes_excluding_manifest_and_checksum": sum(path.stat().st_size for path in files),
        "files_by_extension": dict(sorted(extensions.items())),
        "manifest_note": "This manifest intentionally excludes PACKAGE_MANIFEST.json and CHECKSUMS.sha256 to avoid circular hashes.",
        "files": entries,
    }


def checksum_text() -> str:
    lines = [
        f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}"
        for path in package_files(include_manifest=True)
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify without changing files")
    args = parser.parse_args()

    expected_manifest = manifest_data()
    if args.check:
        manifest_ok = MANIFEST.is_file() and json.loads(MANIFEST.read_text(encoding="utf-8")) == expected_manifest
        checksums_ok = CHECKSUMS.is_file() and CHECKSUMS.read_text(encoding="utf-8") == checksum_text()
        result = {"manifest_current": manifest_ok, "checksums_current": checksums_ok, "passed": manifest_ok and checksums_ok}
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1

    MANIFEST.write_text(json.dumps(expected_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CHECKSUMS.write_text(checksum_text(), encoding="utf-8")
    print(json.dumps({
        "manifest_files": expected_manifest["file_count_excluding_manifest_and_checksum"],
        "checksum_entries": len(package_files(include_manifest=True)),
        "sample_count": expected_manifest["sample_count"],
        "family_count": expected_manifest["family_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
