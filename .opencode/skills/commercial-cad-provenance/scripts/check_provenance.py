#!/usr/bin/env python3
"""Validate conservative commercial-use provenance for CAD artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


POLICY_PATH = Path(__file__).parents[1] / "references" / "commercial-license-policy.json"
POLICY = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
PERMISSIVE = set(POLICY["allowed"]["permissive"])
ATTRIBUTION = set(POLICY["allowed"]["attribution_required"])
SELF_OWNED = set(POLICY["allowed"]["self_owned_only"])
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
KNOWN_KINDS = {
    "generated_geometry",
    "library",
    "embedded_data",
    "third_party_asset",
    "downloaded_cad",
}
THIRD_PARTY_FILE_KINDS = {
    "generated_geometry",
    "library",
    "embedded_data",
    "third_party_asset",
    "downloaded_cad",
}


def resolve_inside(root: Path, relative_path: str, label: str) -> tuple[Path | None, str | None]:
    path = (root / relative_path).resolve()
    if not path.is_relative_to(root.resolve()):
        return None, f"{label} escapes manifest directory"
    if not path.is_file():
        return None, f"{label} does not exist: {relative_path}"
    return path, None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_item(item: dict[str, Any], manifest_root: Path) -> list[str]:
    problems: list[str] = []
    item_id = str(item.get("id") or "<missing-id>")
    origin = item.get("origin")
    license_id = item.get("license")
    kind = item.get("kind")

    for field in ("id", "kind", "origin", "license"):
        if not item.get(field):
            problems.append(f"{item_id}: missing {field}")

    if kind not in KNOWN_KINDS:
        problems.append(f"{item_id}: unsupported kind {kind!r}")

    if origin == "self" and license_id in SELF_OWNED:
        if kind != "generated_geometry":
            problems.append(f"{item_id}: self-owned proprietary entries must be generated_geometry")
        return problems

    if origin != "third_party":
        problems.append(f"{item_id}: unsupported origin/license combination")
        return problems

    if license_id not in PERMISSIVE | ATTRIBUTION:
        problems.append(f"{item_id}: license {license_id!r} is not allowlisted")

    if not item.get("source_url"):
        problems.append(f"{item_id}: missing source_url")

    if kind in THIRD_PARTY_FILE_KINDS:
        if not item.get("version_or_commit"):
            problems.append(f"{item_id}: missing version_or_commit")
        artifact_path = str(item.get("artifact_path") or "")
        artifact_digest = str(item.get("sha256") or "")
        if not artifact_path:
            problems.append(f"{item_id}: missing artifact_path")
        if not SHA256.fullmatch(artifact_digest):
            problems.append(f"{item_id}: third-party item requires a valid sha256")
        if artifact_path and SHA256.fullmatch(artifact_digest):
            artifact, error = resolve_inside(manifest_root, artifact_path, f"{item_id}: artifact_path")
            if error:
                problems.append(error)
            elif artifact and file_sha256(artifact).lower() != artifact_digest.lower():
                problems.append(f"{item_id}: artifact sha256 mismatch")

        license_file = str(item.get("license_file") or "")
        license_digest = str(item.get("license_sha256") or "")
        if not license_file:
            problems.append(f"{item_id}: missing license_file")
        if not SHA256.fullmatch(license_digest):
            problems.append(f"{item_id}: requires valid license_sha256")
        if license_file and SHA256.fullmatch(license_digest):
            license_path, error = resolve_inside(
                manifest_root, license_file, f"{item_id}: license_file"
            )
            if error:
                problems.append(error)
            elif license_path and file_sha256(license_path).lower() != license_digest.lower():
                problems.append(f"{item_id}: license sha256 mismatch")

    distribution = item.get("distribution", "build_only")
    if distribution not in {"build_only", "redistributed"}:
        problems.append(f"{item_id}: invalid distribution")
    if kind in {"third_party_asset", "downloaded_cad", "generated_geometry"} and distribution != "redistributed":
        problems.append(f"{item_id}: CAD assets must declare redistributed distribution")

    if license_id in ATTRIBUTION:
        attribution = item.get("attribution") or {}
        for field in ("title", "author", "license_url", "modifications"):
            if not attribution.get(field):
                problems.append(f"{item_id}: CC-BY attribution missing {field}")

    return problems


def attribution_markdown(project: str, items: list[dict[str, Any]]) -> str:
    lines = [f"# Attributions: {project}", ""]
    attributed = [item for item in items if item.get("license") in ATTRIBUTION]
    if not attributed:
        lines.extend(["No CC-BY assets are included.", ""])
        return "\n".join(lines)

    for item in attributed:
        attribution = item["attribution"]
        lines.extend(
            [
                f"## {attribution['title']}",
                "",
                f"- Author: {attribution['author']}",
                f"- Source: {item['source_url']}",
                f"- License: [{item['license']}]({attribution['license_url']})",
                f"- Modifications: {attribution['modifications']}",
                f"- SHA-256: `{item.get('sha256', 'not-applicable')}`",
                "",
            ]
        )
    return "\n".join(lines)


def third_party_notices_markdown(project: str, items: list[dict[str, Any]]) -> str:
    lines = [f"# Third-Party Notices: {project}", ""]
    third_party = [item for item in items if item.get("origin") == "third_party"]
    if not third_party:
        lines.extend(["No third-party code, data, or CAD assets are distributed.", ""])
        return "\n".join(lines)
    for item in third_party:
        lines.extend(
            [
                f"## {item['id']}",
                "",
                f"- Kind: {item['kind']}",
                f"- Source: {item['source_url']}",
                f"- Version/commit: {item['version_or_commit']}",
                f"- License: {item['license']}",
                f"- Distribution: {item.get('distribution', 'build_only')}",
            ]
        )
        if item.get("license_file"):
            lines.append(f"- License file: `{item['license_file']}`")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--attributions")
    parser.add_argument("--third-party-notices")
    parser.add_argument("--report")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    manifest_root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    project = str(manifest.get("project") or "")
    items = manifest.get("items")
    blockers: list[str] = []
    if not project:
        blockers.append("missing project")
    if not isinstance(items, list):
        blockers.append("items must be an array")
        items = []
    for item in items:
        if not isinstance(item, dict):
            blockers.append("items must contain objects")
            continue
        blockers.extend(validate_item(item, manifest_root))

    status = "COMMERCIAL_LICENSE_PASS" if not blockers else "BLOCKED_LIBRARY_ASSET"
    report = {
        "status": status,
        "project": project,
        "checked_items": len(items),
        "approved_item_ids": sorted(
            str(item["id"])
            for item in items
            if isinstance(item, dict) and item.get("id") and not blockers
        ),
        "manifest_sha256": file_sha256(manifest_path),
        "policy_sha256": file_sha256(POLICY_PATH),
        "blockers": blockers,
        "policy": {
            "permissive": sorted(PERMISSIVE),
            "attribution": sorted(ATTRIBUTION),
            "self_owned": sorted(SELF_OWNED),
        },
    }

    if not blockers:
        attribution_target = Path(args.attributions) if args.attributions else manifest_root / "ATTRIBUTIONS.md"
        notice_target = (
            Path(args.third_party_notices)
            if args.third_party_notices
            else manifest_root / "THIRD_PARTY_NOTICES.md"
        )
        target = attribution_target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(attribution_markdown(project, items), encoding="utf-8")
        notice_target.parent.mkdir(parents=True, exist_ok=True)
        notice_target.write_text(third_party_notices_markdown(project, items), encoding="utf-8")
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
