#!/usr/bin/env python3
"""Initialize a fail-closed commercial 3D clearance workspace."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


ASSETS = Path(__file__).resolve().parent.parent / "assets"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a commercial 3D rights, provenance, and safety workspace."
    )
    parser.add_argument("--name", required=True, help="Product/project name")
    parser.add_argument(
        "--seller-country",
        required=True,
        help="Seller country code or unambiguous country name",
    )
    parser.add_argument(
        "--markets",
        required=True,
        help="Comma-separated target market codes; use exact country rows later",
    )
    parser.add_argument(
        "--release-type",
        required=True,
        choices=("digital", "physical", "both"),
        help="Planned commercial release type",
    )
    parser.add_argument("--release-id", help="Stable human-readable release ID")
    parser.add_argument(
        "--output", required=True, type=Path, help="New, non-existing output directory"
    )
    return parser.parse_args()


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").upper()
    return value[:32] or "MODEL"


def read_json(name: str) -> dict:
    with (ASSETS / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def copy_template(asset_name: str, destination: Path, replacements: dict[str, str]) -> None:
    text = (ASSETS / asset_name).read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    destination.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    destination = args.output.expanduser().resolve()
    if destination.exists():
        print(f"ERROR: output already exists; refusing to overwrite: {destination}", file=sys.stderr)
        return 2

    markets = [item.strip().upper() for item in args.markets.split(",") if item.strip()]
    if not markets:
        print("ERROR: at least one target market is required", file=sys.stderr)
        return 2

    release_types = (
        ["digital", "physical"] if args.release_type == "both" else [args.release_type]
    )
    project_id = str(uuid.uuid4())
    today = datetime.now(timezone.utc)
    created_at = today.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    release_id = (
        args.release_id.strip()
        if args.release_id
        else f"{slug(args.name)}-{today:%Y%m%d}-{project_id[:8].upper()}"
    )
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,79}", release_id):
        print(
            "ERROR: release ID must be 3-80 characters using letters, numbers, dot, underscore, or hyphen",
            file=sys.stderr,
        )
        return 2

    directories = [
        "01-sources/evidence",
        "02-tools/evidence",
        "03-components/evidence",
        "04-authorship/prompts",
        "04-authorship/versions",
        "05-clearance/searches",
        "05-clearance/contracts",
        "06-engineering/risk-assessment",
        "06-engineering/test-reports",
        "06-engineering/materials-and-batches",
        "07-release/artifacts",
        "08-approvals",
        "09-incidents/complaints",
        "09-incidents/corrections",
        "09-incidents/recalls",
        "reports",
    ]

    destination.mkdir(parents=True, exist_ok=False)
    for relative in directories:
        (destination / relative).mkdir(parents=True, exist_ok=False)

    project = read_json("project.template.json")
    project.update(
        {
            "project_id": project_id,
            "release_id": release_id,
            "product_name": args.name,
            "seller_country": args.seller_country,
            "target_markets": markets,
            "release_types": release_types,
            "created_at": created_at,
        }
    )
    write_json(destination / "project.json", project)

    provenance = read_json("provenance.template.json")
    provenance.update(
        {
            "project_id": project_id,
            "release_id": release_id,
            "product_name": args.name,
            "release_types": release_types,
            "target_markets": markets,
        }
    )
    provenance["seller"]["country"] = args.seller_country
    write_json(destination / "07-release/provenance.json", provenance)

    approval = read_json("release-approval.template.json")
    approval.update({"project_id": project_id, "release_id": release_id})
    write_json(destination / "08-approvals/release-approval.json", approval)

    copies = {
        "source-register.csv": "01-sources/source-register.csv",
        "tool-register.csv": "02-tools/tool-register.csv",
        "component-register.csv": "03-components/component-register.csv",
        "human-contribution-log.csv": "04-authorship/human-contribution-log.csv",
        "market-matrix.csv": "05-clearance/market-matrix.csv",
        "RIGHTS-CLEARANCE.template.md": "05-clearance/RIGHTS-CLEARANCE.md",
        "PRODUCT-TECHNICAL-FILE.template.md": "06-engineering/PRODUCT-TECHNICAL-FILE.md",
        "COMMERCIAL-MODEL-LICENSE.template.md": "07-release/COMMERCIAL-MODEL-LICENSE.md",
        "THIRD-PARTY-NOTICES.template.md": "07-release/THIRD-PARTY-NOTICES.md",
        "AI-DISCLOSURE.template.md": "07-release/AI-DISCLOSURE.md",
        "CONTRIBUTOR-IP-AGREEMENT.checklist.md": "05-clearance/CONTRIBUTOR-IP-AGREEMENT.checklist.md",
        "MODEL-AND-PROPERTY-RELEASE.checklist.md": "05-clearance/MODEL-AND-PROPERTY-RELEASE.checklist.md",
        "TOOL-ONBOARDING.checklist.md": "02-tools/TOOL-ONBOARDING.checklist.md",
        "MARKET-LAUNCH.checklist.md": "05-clearance/MARKET-LAUNCH.checklist.md",
    }
    replacements = {
        "[PRODUCT]": args.name,
        "[PRODUCT NAME]": args.name,
        "[RELEASE ID]": release_id,
        "[PROJECT ID / RELEASE ID]": f"{project_id} / {release_id}",
        "[PROJECT ID]": project_id,
    }
    for asset_name, relative in copies.items():
        copy_template(asset_name, destination / relative, replacements)

    shutil.copy2(
        ASSETS / "geometry-watermark.scad",
        destination / "04-authorship/geometry-watermark.scad",
    )

    print(f"Created commercial 3D clearance workspace: {destination}")
    print(f"Project ID: {project_id}")
    print(f"Release ID: {release_id}")
    print("Initial status: BLOCK until every required register and release gate is cleared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
