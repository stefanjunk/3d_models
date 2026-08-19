#!/usr/bin/env python3
"""Create the revisioned DRAFT project package from an explicit allowlist."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_files(directory: str, patterns: tuple[str, ...] = ("*",)) -> list[Path]:
    base = ROOT / directory
    found: set[Path] = set()
    for pattern in patterns:
        found.update(path for path in base.rglob(pattern) if path.is_file())
    return sorted(found)


def main() -> None:
    params = json.loads((ROOT / "config" / "model-params.json").read_text(encoding="utf-8"))
    output_dir = ROOT / "output" / "DRAFT"
    current_outputs = [
        output_dir / "DRAFT-driver-front-textured.stl",
        output_dir / "DRAFT-driver-back-textured.stl",
        output_dir / "DRAFT-hardware-front-textured.stl",
        output_dir / "DRAFT-hardware-back-textured.stl",
        output_dir / "DRAFT-screwdriver-comb.stl",
        output_dir / "DRAFT-drawer-fit-corner-coupon.stl",
        output_dir / "DRAFT-relief-depth-coupon.stl",
        output_dir / "DRAFT-connector-coupon-male.stl",
        output_dir / "DRAFT-connector-coupon-female.stl",
        output_dir / params["export"]["assembly_filename"],
    ]
    for path in current_outputs:
        if not path.is_file():
            raise SystemExit(f"required release output is missing: {path}")

    geometry_hashes = [
        f"{sha256_file(path)}  {path.relative_to(ROOT)}" for path in current_outputs
    ]
    (ROOT / "reports" / "geometry-sha256.txt").write_text("\n".join(geometry_hashes) + "\n", encoding="utf-8")

    top_level = [
        ROOT / name
        for name in (
            "README.md",
            "BOM.md",
            "assembly-guide.md",
            "decision-log.md",
            "design-spec.yaml",
            "print-profile.md",
            "requirements.txt",
            "rebuild.py",
            "package.json",
            "package-lock.json",
            "concept-R1.png",
        )
    ]
    source_files = relative_files("src", ("*.py", "*.mjs"))
    config_files = relative_files("config", ("*.json",))
    relief_files = relative_files("relief/organizer")
    watermark_files = relative_files("assets/just-innovation-watermark")
    texture_files = [
        ROOT / "texture" / "steel-rivets-source-R1.png",
        ROOT / "texture" / "steel1-source-R1.3.png",
        ROOT / "texture" / "steel-rivets-relief-manifest.json",
        ROOT / "texture" / "steel-rivets-vector-preview.png",
    ]
    report_names = (
        "validation-report.md",
        "continuous16-validation.json",
        "build-final.json",
        "build-pipeline.json",
        "mesh-validation.json",
        "stl-repair.json",
        "three-mf-package.json",
        "geometry-sha256.txt",
        "watermark-evidence.md",
        "watermark-selection.json",
        "watermark-underside.png",
        "watermark-closeup.png",
        "watermark-section.png",
        "watermark-layer-preview.png",
        "DRAFT-R1.1-continuous16-model-preview.png",
        "DRAFT-R1.1-continuous16-relief-closeup.png",
        "aspect-diagnostic.json",
        "aspect-diagnostic-build.png",
        "aspect-diagnostic-geometry-preview.png",
    )
    report_files = [ROOT / "reports" / name for name in report_names]
    files = sorted(set(top_level + source_files + config_files + relief_files + watermark_files + texture_files + report_files + current_outputs))
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise SystemExit("release allowlist contains missing files: " + ", ".join(map(str, missing)))

    manifest = {
        "schema_version": 1,
        "status": "DRAFT",
        "revision": params["model_revision"],
        "assembly": params["export"]["assembly_filename"],
        "one_command_rebuild": "python3 rebuild.py /path/to/new-texture.png",
        "files": [
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        ],
    }
    manifest_path = ROOT / "reports" / "release-package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    files.append(manifest_path)
    files.sort()

    destination = ROOT.parent / params["export"]["release_zip_filename"]
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for path in files:
            archive.write(path, Path("schubladen-organizer") / path.relative_to(ROOT))

    with zipfile.ZipFile(destination) as archive:
        bad_file = archive.testzip()
        entries = archive.namelist()
    validation = {
        "status": "PASS" if bad_file is None else "FAIL",
        "file": str(destination),
        "bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "entries": len(entries),
        "bad_file": bad_file,
    }
    (ROOT / "reports" / "release-package-validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
