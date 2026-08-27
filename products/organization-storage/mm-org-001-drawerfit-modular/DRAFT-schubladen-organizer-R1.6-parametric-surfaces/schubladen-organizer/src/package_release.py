#!/usr/bin/env python3
"""Create a profile-specific R1.6 DRAFT package from an explicit allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from surface_profiles import formatted_export, resolve_surface_profile, surface_choices


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface", choices=surface_choices(ROOT))
    args = parser.parse_args()
    surface_id, _, surface_profile = resolve_surface_profile(ROOT, args.surface)
    params = json.loads((ROOT / "config" / "model-params.json").read_text(encoding="utf-8"))
    output_dir = ROOT / "output" / "DRAFT"
    current_outputs = [
        output_dir / "DRAFT-driver-front-surface.stl",
        output_dir / "DRAFT-driver-back-surface.stl",
        output_dir / "DRAFT-hardware-front-surface.stl",
        output_dir / "DRAFT-hardware-back-surface.stl",
        output_dir / "DRAFT-screwdriver-comb.stl",
        output_dir / "DRAFT-drawer-fit-corner-coupon.stl",
        output_dir / "DRAFT-surface-texture-coupon.stl",
        output_dir / "DRAFT-connector-coupon-male.stl",
        output_dir / "DRAFT-connector-coupon-female.stl",
        output_dir / formatted_export(params, "assembly_filename_template", surface_id),
    ]
    for path in current_outputs:
        if not path.is_file():
            raise SystemExit(f"required release output is missing: {path}")

    geometry_hashes = [f"{sha256_file(path)}  {path.relative_to(ROOT)}" for path in current_outputs]
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
        )
    ]
    source_files = relative_files("src", ("*.py", "*.mjs"))
    config_files = relative_files("config", ("*.json",))
    watermark_files = relative_files("assets/just-innovation-watermark")
    report_names = (
        "validation-report.md",
        "surface-texture-validation.json",
        "build-final.json",
        "build-pipeline.json",
        "mesh-validation.json",
        "stl-repair.json",
        "three-mf-package.json",
        "geometry-sha256.txt",
        "carbon-texture-plan-floor.json",
        "carbon-texture-plan-wall.json",
        "carbon-wave-texture-plan-floor.json",
        "micro-cast-texture-plan.json",
        "watermark-evidence.md",
        "watermark-selection.json",
        "watermark-underside.png",
        "watermark-closeup.png",
        "watermark-section.png",
        "watermark-layer-preview.png",
        f"DRAFT-R1.6-{surface_id}-model-preview.png",
        f"DRAFT-R1.6-{surface_id}-hardware-closeup.png",
        f"DRAFT-R1.6-{surface_id}-texture-coupon.png",
    )
    report_files = [ROOT / "reports" / name for name in report_names if (ROOT / "reports" / name).is_file()]
    files = sorted(set(top_level + source_files + config_files + watermark_files + report_files + current_outputs))
    missing = [path for path in files if not path.is_file()]
    if missing:
        raise SystemExit("release allowlist contains missing files: " + ", ".join(map(str, missing)))

    manifest = {
        "schema_version": 1,
        "status": "DRAFT",
        "revision": params["model_revision"],
        "surface_profile": surface_id,
        "representation": surface_profile["representation"],
        "assembly": formatted_export(params, "assembly_filename_template", surface_id),
        "one_command_rebuild": f"python3 rebuild.py --surface {surface_id}",
        "files": [
            {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in files
        ],
    }
    manifest_path = ROOT / "reports" / "release-package-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    files.append(manifest_path)
    files.sort()

    destination = ROOT.parent / formatted_export(params, "release_zip_filename_template", surface_id)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for path in files:
            archive.write(path, Path("schubladen-organizer") / path.relative_to(ROOT))

    with zipfile.ZipFile(destination) as archive:
        bad_file = archive.testzip()
        entries = archive.namelist()
    validation = {
        "status": "PASS" if bad_file is None else "FAIL",
        "surface_profile": surface_id,
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
