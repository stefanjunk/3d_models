#!/usr/bin/env python3
"""Embed release/provenance metadata into an unsigned 3MF copy.

The custom c3dp namespace is internal and non-standard:
urn:commercial-3d-provenance:1.0
"""

from __future__ import annotations

import argparse
import io
import os
import re
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath


PROV_PREFIX = "c3dp"
PROV_NS = "urn:commercial-3d-provenance:1.0"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
MAX_MODEL_XML = 128 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add human-readable and machine-readable provenance to a 3MF copy."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--designer", required=True)
    parser.add_argument("--license-terms", required=True)
    parser.add_argument("--ai-use", required=True)
    parser.add_argument("--manifest-uri", required=True)
    parser.add_argument("--project-id")
    parser.add_argument("--copyright")
    parser.add_argument("--title")
    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe_target(target: str) -> str | None:
    normalized = target.replace("\\", "/").lstrip("/")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None
    return PurePosixPath(*parts).as_posix()


def locate_model(archive: zipfile.ZipFile, names: set[str]) -> str:
    if "_rels/.rels" in names:
        try:
            rel_root = ET.fromstring(archive.read("_rels/.rels"))
        except ET.ParseError as exc:
            raise ValueError(f"invalid _rels/.rels: {exc}") from exc
        targets: list[str] = []
        for relation in rel_root:
            relation_type = relation.attrib.get("Type", "")
            if relation_type.rstrip("/").endswith("/3dmodel"):
                target = safe_target(relation.attrib.get("Target", ""))
                if target and target in names:
                    targets.append(target)
        if len(targets) == 1:
            return targets[0]
        if len(targets) > 1:
            raise ValueError("multiple root 3D model relationships found")

    preferred = "3D/3dmodel.model"
    if preferred in names:
        return preferred
    candidates = sorted(
        name for name in names if name.lower().endswith(".model") and name.startswith("3D/")
    )
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("could not identify a single root 3MF model part")


def collect_namespaces(xml_bytes: bytes) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for _, item in ET.iterparse(io.BytesIO(xml_bytes), events=("start-ns",)):
        prefix, uri = item
        if (prefix, uri) not in result:
            result.append((prefix, uri))
    return result


def register_namespaces(namespaces: list[tuple[str, str]]) -> None:
    for prefix, uri in namespaces:
        if prefix == PROV_PREFIX and uri != PROV_NS:
            raise ValueError(f"input already uses prefix {PROV_PREFIX} for another namespace")
        if prefix == "xml" or re.fullmatch(r"ns\d+", prefix or ""):
            continue
        try:
            ET.register_namespace(prefix, uri)
        except ValueError:
            continue
    ET.register_namespace(PROV_PREFIX, PROV_NS)


def set_metadata(root: ET.Element, namespace: str, name: str, value: str, preserve: bool) -> None:
    metadata_tag = f"{{{namespace}}}metadata"
    matches = [
        child
        for child in root
        if child.tag == metadata_tag and child.attrib.get("name") == name
    ]
    if matches:
        element = matches[0]
        for duplicate in matches[1:]:
            root.remove(duplicate)
    else:
        element = ET.Element(metadata_tag)
        resources_index = next(
            (
                index
                for index, child in enumerate(root)
                if local_name(child.tag) == "resources"
            ),
            len(root),
        )
        root.insert(resources_index, element)
    element.attrib.clear()
    element.set("name", name)
    if preserve:
        element.set("preserve", "1")
    element.text = value


def modify_model(xml_bytes: bytes, args: argparse.Namespace) -> bytes:
    if len(xml_bytes) > MAX_MODEL_XML:
        raise ValueError("root model XML is larger than the 128 MiB safety limit")
    namespaces = collect_namespaces(xml_bytes)
    register_namespaces(namespaces)
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"invalid root model XML: {exc}") from exc
    if local_name(root.tag) != "model" or not root.tag.startswith("{"):
        raise ValueError("root model part is not a namespace-qualified 3MF model")
    namespace = root.tag[1:].split("}", 1)[0]

    root.set(f"xmlns:{PROV_PREFIX}", PROV_NS)
    standard = {
        "Designer": args.designer,
        "LicenseTerms": args.license_terms,
    }
    if args.title:
        standard["Title"] = args.title
    if args.copyright:
        standard["Copyright"] = args.copyright
    custom = {
        f"{PROV_PREFIX}:ReleaseID": args.release_id,
        f"{PROV_PREFIX}:AIUse": args.ai_use,
        f"{PROV_PREFIX}:ProvenanceManifest": args.manifest_uri,
    }
    if args.project_id:
        custom[f"{PROV_PREFIX}:ProjectID"] = args.project_id
    for name, value in standard.items():
        set_metadata(root, namespace, name, value, preserve=False)
    for name, value in custom.items():
        set_metadata(root, namespace, name, value, preserve=True)

    buffer = io.BytesIO()
    ET.ElementTree(root).write(
        buffer, encoding="utf-8", xml_declaration=True, short_empty_elements=True
    )
    return buffer.getvalue()


def main() -> int:
    args = parse_args()
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: input does not exist: {source}", file=sys.stderr)
        return 2
    if source == output:
        print("ERROR: input and output must differ", file=sys.stderr)
        return 2
    if output.exists():
        print(f"ERROR: output exists; refusing to overwrite: {output}", file=sys.stderr)
        return 2
    for label in ("release_id", "designer", "license_terms", "ai_use", "manifest_uri"):
        if not str(getattr(args, label)).strip():
            print(f"ERROR: {label} must not be empty", file=sys.stderr)
            return 2

    try:
        with zipfile.ZipFile(source, "r") as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            if len(names) != len(set(names)):
                raise ValueError("archive contains duplicate member names")
            if "[Content_Types].xml" not in names:
                raise ValueError("archive lacks [Content_Types].xml")
            if any(
                name.startswith("_xmlsignatures/")
                or name.endswith("origin.sigs")
                or "digital-signature" in name.lower()
                for name in names
            ):
                raise ValueError(
                    "input appears signed; embedding would invalidate signatures. Embed before signing."
                )
            if any(item.flag_bits & 0x1 for item in infos):
                raise ValueError("encrypted 3MF members are not supported")
            model_name = locate_model(archive, set(names))
            model_xml = modify_model(archive.read(model_name), args)

            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "wb", dir=output.parent, delete=False
            ) as temporary_handle:
                temporary = Path(temporary_handle.name)
            try:
                with zipfile.ZipFile(temporary, "w") as destination:
                    for info in infos:
                        data = model_xml if info.filename == model_name else archive.read(info.filename)
                        destination.writestr(info, data)
                os.replace(temporary, output)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
    except (OSError, zipfile.BadZipFile, KeyError, ValueError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        with zipfile.ZipFile(output, "r") as check_archive:
            check_model = locate_model(check_archive, set(check_archive.namelist()))
            check_bytes = check_archive.read(check_model)
            if args.release_id.encode("utf-8") not in check_bytes:
                raise ValueError("post-write verification did not find release ID")
    except (OSError, zipfile.BadZipFile, KeyError, ValueError) as exc:
        output.unlink(missing_ok=True)
        print(f"ERROR: post-write verification failed: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote provenance-enhanced 3MF copy: {output}")
    print(f"Custom namespace: {PROV_NS} (project-internal, not an official standard)")
    print("Next: re-open in target CAD/slicers, inspect metadata survival, hash, and sign.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
