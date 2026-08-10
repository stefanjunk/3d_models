#!/usr/bin/env python3
"""Validate the two human approvals required before 3D geometry work."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct
from typing import Any

from PIL import Image, UnidentifiedImageError


APPROVED = "APPROVED"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def meaningful(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_artifact(root: Path, value: Any, label: str) -> tuple[Path | None, str | None]:
    if not meaningful(value):
        return None, f"{label} is required"
    path = (root / str(value)).resolve()
    if not path.is_relative_to(root.resolve()):
        return None, f"{label} escapes object folder"
    if not path.is_file():
        return None, f"{label} does not exist"
    return path, None


def is_supported_image(path: Path) -> bool:
    data = path.read_bytes()
    structurally_supported = False
    if data.startswith(PNG_SIGNATURE):
        if len(data) < 33 or data[12:16] != b"IHDR" or b"IEND" not in data[-32:]:
            return False
        width, height = struct.unpack(">II", data[16:24])
        structurally_supported = width > 0 and height > 0
    elif data.startswith(JPEG_SIGNATURE):
        structurally_supported = len(data) > 4 and data.endswith(b"\xff\xd9")
    elif data.startswith(b"RIFF") and len(data) >= 20 and data[8:12] == b"WEBP":
        structurally_supported = data[12:16] in {b"VP8 ", b"VP8L", b"VP8X"}
    if not structurally_supported:
        return False
    try:
        with Image.open(path) as image:
            image.verify()
            return image.format in {"PNG", "JPEG", "WEBP"}
    except (OSError, UnidentifiedImageError):
        return False


def parse_timestamp(value: Any, label: str, blockers: list[str]) -> dt.datetime | None:
    if not meaningful(value):
        blockers.append(f"{label} is required")
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        blockers.append(f"{label} must be ISO 8601")
        return None
    if parsed.tzinfo is None:
        blockers.append(f"{label} must include a timezone")
        return None
    return parsed


def validate_intake_path(path: Path, expected_project: str | None = None) -> list[str]:
    path = path.resolve()
    root = path.parent
    intake = json.loads(path.read_text(encoding="utf-8"))
    blockers: list[str] = []

    if not meaningful(intake.get("project")):
        blockers.append("project is required")
    elif expected_project is not None and intake.get("project") != expected_project:
        blockers.append("project does not match expected project")

    requirements_path, error = resolve_artifact(
        root, intake.get("requirements_summary"), "requirements_summary"
    )
    if error:
        blockers.append(error)
    if intake.get("requirements_status") != APPROVED:
        blockers.append("requirements_status must be APPROVED")
    requirements_approved_at = parse_timestamp(
        intake.get("requirements_approved_at"), "requirements_approved_at", blockers
    )
    if not meaningful(intake.get("requirements_approval_note")):
        blockers.append("requirements_approval_note is required")
    if requirements_path and intake.get("requirements_summary_sha256") != sha256_file(requirements_path):
        blockers.append("requirements_summary_sha256 mismatch")
    if intake.get("concept_requirements_sha256") != intake.get("requirements_summary_sha256"):
        blockers.append("concept_requirements_sha256 does not bind the approved requirements")

    prompt_path, error = resolve_artifact(
        root, intake.get("concept_prompt"), "concept_prompt"
    )
    if error:
        blockers.append(error)
    concept_path, error = resolve_artifact(
        root, intake.get("concept_image"), "concept_image"
    )
    if error:
        blockers.append(error)
    if concept_path and not is_supported_image(concept_path):
        blockers.append("concept_image is not a supported PNG, JPEG, or WebP file")
    if intake.get("concept_status") != APPROVED:
        blockers.append("concept_status must be APPROVED")
    concept_approved_at = parse_timestamp(
        intake.get("concept_approved_at"), "concept_approved_at", blockers
    )
    if not meaningful(intake.get("concept_approval_note")):
        blockers.append("concept_approval_note is required")
    if concept_path and intake.get("concept_image_sha256") != sha256_file(concept_path):
        blockers.append("concept_image_sha256 mismatch")
    if prompt_path and intake.get("concept_prompt_sha256") != sha256_file(prompt_path):
        blockers.append("concept_prompt_sha256 mismatch")
    if requirements_approved_at and concept_approved_at and concept_approved_at <= requirements_approved_at:
        blockers.append("concept approval must be later than requirements approval")

    return blockers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intake", type=Path)
    parser.add_argument("--expected-project")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    blockers = validate_intake_path(args.intake, args.expected_project)
    data = {
        "status": "DESIGN_INTAKE_PASS" if not blockers else "DESIGN_INTAKE_BLOCKED",
        "blockers": blockers,
    }
    text = json.dumps(data, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
