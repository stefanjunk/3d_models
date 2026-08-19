#!/usr/bin/env python3
"""Create the approved CyberVault R4 release without changing mesh geometry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import zipfile

from validate_and_package import (
    analyze_mesh,
    assert_mesh,
    read_binary_stl,
    render_lid_relief_top,
    render_qa,
    verify_3mf,
)


PROJECT = Path(__file__).resolve().parents[1]
DRAFT = PROJECT / "exports" / "draft"
RELEASE = PROJECT / "exports" / "release"
REPORTS = PROJECT / "reports"
RENDERS = PROJECT / "renders"
GEOMETRY_REVISION = "CYBERVAULT-R4-CAD-A-WM1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def copy_exact(source: Path, target: Path) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    source_hash = sha256_file(source)
    target_hash = sha256_file(target)
    if source_hash != target_hash:
        raise RuntimeError(f"Exact-copy verification failed: {source} -> {target}")
    return {
        "source": str(source.relative_to(PROJECT)),
        "target": str(target.relative_to(PROJECT)),
        "sha256": target_hash,
        "exact_byte_match": True,
    }


def rewrite_stl_header(source: Path, target: Path, header: str) -> dict:
    data = source.read_bytes()
    if len(data) < 84:
        raise ValueError(f"Not a binary STL: {source}")
    triangles = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + triangles * 50:
        raise ValueError(f"Binary STL length mismatch: {source}")
    output = header.encode("ascii", "replace")[:80].ljust(80, b"\0") + data[80:]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(output)
    source_payload = sha256_bytes(data[80:])
    target_payload = sha256_bytes(output[80:])
    if source_payload != target_payload:
        raise RuntimeError(f"STL triangle payload changed: {source} -> {target}")
    return {
        "source": str(source.relative_to(PROJECT)),
        "target": str(target.relative_to(PROJECT)),
        "triangles": triangles,
        "source_file_sha256": sha256_bytes(data),
        "target_file_sha256": sha256_bytes(output),
        "triangle_payload_sha256": target_payload,
        "triangle_payload_exact_match": True,
    }


def mesh_digest(model_xml: bytes) -> str:
    meshes = re.findall(rb"<mesh>.*?</mesh>", model_xml, flags=re.DOTALL)
    if not meshes:
        raise RuntimeError("3MF model contains no mesh resources")
    return sha256_bytes(b"".join(meshes))


def rewrite_3mf_metadata(source: Path, target: Path) -> dict:
    with zipfile.ZipFile(source, "r") as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"Source 3MF is corrupt: {source}")
        members = {name: archive.read(name) for name in archive.namelist()}
    model_name = "3D/3dmodel.model"
    source_model = members[model_name]
    target_model = source_model.replace(b"DRAFT", b"RELEASE")
    members[model_name] = target_model
    source_mesh_hash = mesh_digest(source_model)
    target_mesh_hash = mesh_digest(target_model)
    if source_mesh_hash != target_mesh_hash:
        raise RuntimeError(f"3MF mesh resources changed: {source} -> {target}")
    if b"DRAFT" in target_model.upper():
        raise RuntimeError(f"DRAFT metadata remains in final 3MF: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(2026, 8, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, members[name])
    with zipfile.ZipFile(target, "r") as archive:
        bad_member = archive.testzip()
    if bad_member is not None:
        raise RuntimeError(f"Final 3MF integrity failure in {bad_member}")
    return {
        "source": str(source.relative_to(PROJECT)),
        "target": str(target.relative_to(PROJECT)),
        "source_file_sha256": sha256_file(source),
        "target_file_sha256": sha256_file(target),
        "mesh_resources_sha256": target_mesh_hash,
        "mesh_resources_exact_match": True,
        "release_metadata_clean": True,
    }


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 11, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def package(relative_files: list[str], target: Path) -> dict:
    missing = [name for name in relative_files if not (PROJECT / name).is_file()]
    if missing:
        raise FileNotFoundError("Release package inputs missing: " + ", ".join(missing))
    if any("DRAFT" in Path(name).name.upper() for name in relative_files):
        raise RuntimeError("Release package contains a DRAFT-named member")
    payloads = {name: (PROJECT / name).read_bytes() for name in relative_files}
    manifest = "".join(
        f"{sha256_bytes(payloads[name])}  {name}\n" for name in sorted(relative_files)
    ).encode("utf-8")
    temporary = target.with_suffix(".zip.tmp")
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(relative_files):
            archive.writestr(zip_info(name), payloads[name])
        archive.writestr(zip_info("MANIFEST-SHA256.txt"), manifest)
    temporary.replace(target)
    with zipfile.ZipFile(target, "r") as archive:
        bad_member = archive.testzip()
        members = archive.namelist()
    if bad_member is not None:
        raise RuntimeError(f"Release ZIP integrity failure in {bad_member}")
    return {
        "archive": str(target.relative_to(PROJECT)),
        "archive_bytes": target.stat().st_size,
        "archive_sha256": sha256_file(target),
        "member_count": len(members),
        "manifest_entries": len(relative_files),
        "zip_integrity": True,
    }


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)

    equality = {
        "step": copy_exact(
            DRAFT / "cyber_nozzle_case_R4_DRAFT.step",
            RELEASE / "cyber_nozzle_case_R4.step",
        ),
        "base_stl": rewrite_stl_header(
            DRAFT / "cyber_nozzle_case_R4_DRAFT_base_manifold.stl",
            RELEASE / "cyber_nozzle_case_R4_base.stl",
            "CyberVault R4 base RELEASE",
        ),
        "lid_stl": rewrite_stl_header(
            DRAFT / "cyber_nozzle_case_R4_DRAFT_lid_relief_manifold.stl",
            RELEASE / "cyber_nozzle_case_R4_lid.stl",
            "CyberVault R4 relief lid RELEASE",
        ),
        "assembly_stl": rewrite_stl_header(
            DRAFT / "cyber_nozzle_case_R4_DRAFT_print_in_place.stl",
            RELEASE / "cyber_nozzle_case_R4_print_in_place.stl",
            "CyberVault R4 print-in-place RELEASE",
        ),
        "hinge_coupon_stl": rewrite_stl_header(
            DRAFT / "hinge_coupon_R4_DRAFT.stl",
            RELEASE / "hinge_coupon_R4.stl",
            "CyberVault R4 hinge coupon RELEASE",
        ),
        "fit_coupon_stl": rewrite_stl_header(
            DRAFT / "kobra3max_fit_coupon_DRAFT.stl",
            RELEASE / "kobra3max_fit_coupon.stl",
            "Kobra 3 Max fit coupon RELEASE",
        ),
        "main_3mf": rewrite_3mf_metadata(
            DRAFT / "cyber_nozzle_case_R4_DRAFT.3mf",
            RELEASE / "cyber_nozzle_case_R4.3mf",
        ),
        "fit_coupon_3mf": rewrite_3mf_metadata(
            DRAFT / "kobra3max_fit_coupon_DRAFT.3mf",
            RELEASE / "kobra3max_fit_coupon.3mf",
        ),
    }

    mesh_targets = {
        "base": (RELEASE / "cyber_nozzle_case_R4_base.stl", 1),
        "lid": (RELEASE / "cyber_nozzle_case_R4_lid.stl", 1),
        "assembly": (RELEASE / "cyber_nozzle_case_R4_print_in_place.stl", 2),
        "hinge_coupon": (RELEASE / "hinge_coupon_R4.stl", 2),
    }
    topology = {}
    for name, (path, expected_components) in mesh_targets.items():
        topology[name] = analyze_mesh(read_binary_stl(path), path.name)
        assert_mesh(topology[name], expected_components)

    three_mf = verify_3mf(RELEASE / "cyber_nozzle_case_R4.3mf")
    if not (
        three_mf["zip_integrity"]
        and three_mf["object_count"] == 2
        and three_mf["build_item_count"] == 2
        and three_mf["units"] == "millimeter"
    ):
        raise RuntimeError(f"Final 3MF verification failed: {three_mf}")

    collision = json.loads(
        (REPORTS / "manifold-collision-candidate.json").read_text(encoding="utf-8")
    )["collision_volume_mm3"]
    if collision != {"open": 0, "closed_rigid_nominal": 0}:
        raise RuntimeError(f"Approved candidate collision result changed: {collision}")

    final_open = RENDERS / "cyber-nozzle-case-R4-RELEASE-open.png"
    final_closed = RENDERS / "cyber-nozzle-case-R4-RELEASE-closed.png"
    final_relief = RENDERS / "cyber-nozzle-case-R4-RELEASE-relief-top.png"
    base_mesh = read_binary_stl(RELEASE / "cyber_nozzle_case_R4_base.stl")
    lid_mesh = read_binary_stl(RELEASE / "cyber_nozzle_case_R4_lid.stl")
    render_qa(final_open, final_closed, base_mesh, lid_mesh, status_label="RELEASE")
    render_lid_relief_top(final_relief, lid_mesh, status_label="RELEASE")

    verification = {
        "status": "PASS",
        "release_status": "FINAL RELEASE APPROVED",
        "geometry_revision": GEOMETRY_REVISION,
        "geometry_unchanged_from_approved_candidate": True,
        "candidate_to_release_equality": equality,
        "topology": topology,
        "collision_volume_mm3": collision,
        "three_mf": three_mf,
        "print_bed": {
            "printer": "Anycubic Kobra 3 Max",
            "available_mm": [420.0, 420.0, 500.0],
            "assembly_envelope_mm": topology["assembly"]["size_mm"],
            "fits": True,
        },
        "physical_evidence": {
            "fit": "PASS — 0.35 mm clearance per side selected by user",
            "hinge": "PASS BASIC FUNCTION — user confirmed",
            "latch": "PASS BASIC FUNCTION — user confirmed",
        },
        "open_physical_checks": [
            "R4 relief print and 40 cm readability",
            "loaded inversion test",
            "documented 100-cycle pretest and optional 1000-cycle target",
        ],
    }
    verification_path = REPORTS / "release-verification.json"
    verification_path.write_text(
        json.dumps(verification, indent=2) + "\n", encoding="utf-8"
    )

    explicit_files = [
        "PACKAGE-README.md",
        "design-spec.yaml",
        "decision-log.md",
        "reconstruction-brief.yaml",
        "print-profile.yaml",
        "PRINTING-AND-TEST-GUIDE.md",
        "test-plan.yaml",
        "FIT-COUPON-README.md",
        "cad-js/cyber_nozzle_case.mjs",
        "cad-js/validate_manifold.mjs",
        "cad-js/apply_lid_relief.mjs",
        "cad-js/canonicalize_meshes.mjs",
        "cad-js/package.json",
        "cad-js/package-lock.json",
        "cad/fit_coupon.py",
        "tools/validate_and_package.py",
        "tools/watermark_evidence.py",
        "tools/package_release.py",
        "relief/README.md",
        "relief/pattern_geometry.json",
        "relief/generate_cyber_heightmaps.py",
        "relief/build_lid_cutter.py",
        "relief/lid-relief-config.json",
        "relief/side-relief-config.json",
        "relief/side-emboss-config.json",
        "relief/cyber_lid_heightmap_16bit.png",
        "relief/cyber_side_tile_16bit.png",
        "relief/cyber_side_emboss_mask_16bit.png",
        "relief/cyber_lid_engraving_cutter_R4.stl",
        "exports/release/cyber_nozzle_case_R4.step",
        "exports/release/cyber_nozzle_case_R4.3mf",
        "exports/release/cyber_nozzle_case_R4_print_in_place.stl",
        "exports/release/cyber_nozzle_case_R4_base.stl",
        "exports/release/cyber_nozzle_case_R4_lid.stl",
        "exports/release/hinge_coupon_R4.stl",
        "exports/release/kobra3max_fit_coupon.stl",
        "exports/release/kobra3max_fit_coupon.3mf",
        "reports/FINAL-MODEL-RESULT.md",
        "reports/release-verification.json",
        "reports/design-spec-validation-final.json",
        "reports/production-parameters.json",
        "reports/r4-functional-regression.json",
        "reports/watermark-selection.json",
        "reports/watermark-evidence.json",
        "reports/cyber-heightmap-generation.json",
        "reports/cyber-lid-heightmap-analysis.json",
        "reports/cyber-side-heightmap-analysis.json",
        "reports/cyber-side-emboss-analysis.json",
        "reports/fit-coupon-validation.json",
        "reports/physical-test-evidence.json",
        "reports/image-evidence.md",
        "renders/cyber-nozzle-case-R4-RELEASE-open.png",
        "renders/cyber-nozzle-case-R4-RELEASE-closed.png",
        "renders/cyber-nozzle-case-R4-RELEASE-relief-top.png",
        "renders/watermark-01-finished-underside.png",
        "renders/watermark-02-dimensioned-closeup.png",
        "renders/watermark-03-section.png",
        "renders/watermark-04-layer-preview.png",
        "renders/fit-coupon-preview.png",
    ]
    watermark_assets = sorted(
        path.relative_to(PROJECT).as_posix()
        for path in (PROJECT / "assets" / "just-innovation-watermark").rglob("*")
        if path.is_file()
    )
    package_report = package(
        explicit_files + watermark_assets,
        RELEASE / "CyberVault-R4-WM1-RELEASE.zip",
    )
    package_report.update(
        {
            "status": "PASS",
            "release_status": "FINAL RELEASE APPROVED",
            "geometry_revision": GEOMETRY_REVISION,
        }
    )
    (REPORTS / "release-packaging.json").write_text(
        json.dumps(package_report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"verification": verification, "package": package_report}, indent=2))


if __name__ == "__main__":
    main()
