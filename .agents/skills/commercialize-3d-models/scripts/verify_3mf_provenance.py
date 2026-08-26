#!/usr/bin/env python3
"""Verify required project provenance metadata in a 3MF package."""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from embed_3mf_provenance import PROV_NS, PROV_PREFIX, locate_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify 3MF provenance metadata.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--expect-release-id", required=True)
    parser.add_argument("--expect-designer")
    parser.add_argument("--expect-ai-use")
    parser.add_argument("--expect-manifest-uri")
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def main() -> int:
    args = parse_args()
    path = args.file.expanduser().resolve()
    failures: list[str] = []
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                failures.append("archive contains duplicate member names")
            model_name = locate_model(archive, set(names))
            xml_bytes = archive.read(model_name)
    except (OSError, zipfile.BadZipFile, KeyError, ValueError) as exc:
        print(f"BLOCK: cannot read 3MF: {exc}", file=sys.stderr)
        return 2

    namespaces: dict[str, str] = {}
    try:
        for _, item in ET.iterparse(io.BytesIO(xml_bytes), events=("start-ns",)):
            prefix, uri = item
            namespaces[prefix] = uri
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        print(f"BLOCK: invalid model XML: {exc}", file=sys.stderr)
        return 2

    if namespaces.get(PROV_PREFIX) != PROV_NS:
        failures.append(f"{PROV_PREFIX} namespace is absent or not {PROV_NS}")

    values: dict[str, tuple[str, str]] = {}
    for child in root:
        if local_name(child.tag) != "metadata":
            continue
        name = child.attrib.get("name", "")
        values[name] = ((child.text or "").strip(), child.attrib.get("preserve", ""))

    expected = {
        f"{PROV_PREFIX}:ReleaseID": args.expect_release_id,
    }
    if args.expect_designer is not None:
        expected["Designer"] = args.expect_designer
    if args.expect_ai_use is not None:
        expected[f"{PROV_PREFIX}:AIUse"] = args.expect_ai_use
    if args.expect_manifest_uri is not None:
        expected[f"{PROV_PREFIX}:ProvenanceManifest"] = args.expect_manifest_uri

    for name, value in expected.items():
        actual = values.get(name, ("", ""))[0]
        if actual != value:
            failures.append(f"{name} mismatch: expected {value!r}, got {actual!r}")
    for name in (
        f"{PROV_PREFIX}:ReleaseID",
        f"{PROV_PREFIX}:AIUse",
        f"{PROV_PREFIX}:ProvenanceManifest",
    ):
        if name not in values:
            failures.append(f"required metadata missing: {name}")
        elif values[name][1] != "1":
            failures.append(f"custom metadata lacks preserve=1: {name}")
    for name in ("Designer", "LicenseTerms"):
        if not values.get(name, ("", ""))[0]:
            failures.append(f"required standard metadata missing: {name}")

    if failures:
        for failure in failures:
            print(f"BLOCK: {failure}")
        return 2
    print(f"PASS: verified provenance metadata in {path}")
    print(f"Release ID: {args.expect_release_id}")
    print(f"Namespace: {PROV_NS} (project-internal)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
