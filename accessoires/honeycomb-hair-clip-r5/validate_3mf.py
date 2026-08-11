#!/usr/bin/env python3
"""Minimal structural audit for a core 3MF mesh package."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


def audit(path: Path):
    with zipfile.ZipFile(path) as archive:
        bad_member = archive.testzip()
        names = set(archive.namelist())
        required = {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}
        missing = sorted(required - names)
        model = ET.fromstring(archive.read("3D/3dmodel.model")) if not missing else None

    if model is None:
        return {"file": str(path), "archive_bad_member": bad_member, "missing_members": missing, "overall_pass": False}

    namespace = {"m": CORE}
    vertices = model.findall(".//m:vertices/m:vertex", namespace)
    triangles = model.findall(".//m:triangles/m:triangle", namespace)
    objects = model.findall(".//m:resources/m:object", namespace)
    build_items = model.findall(".//m:build/m:item", namespace)
    indices = []
    for triangle in triangles:
        indices.extend(int(triangle.attrib[key]) for key in ("v1", "v2", "v3"))
    indices_valid = bool(vertices) and all(0 <= value < len(vertices) for value in indices)
    result = {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "archive_bad_member": bad_member,
        "missing_members": missing,
        "unit": model.attrib.get("unit"),
        "objects": len(objects),
        "build_items": len(build_items),
        "vertices": len(vertices),
        "triangles": len(triangles),
        "triangle_indices_valid": indices_valid,
    }
    result["overall_pass"] = (
        bad_member is None
        and not missing
        and result["unit"] == "millimeter"
        and result["objects"] == 1
        and result["build_items"] == 1
        and result["vertices"] > 0
        and result["triangles"] > 0
        and indices_valid
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("three_mf", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.three_mf)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    raise SystemExit(0 if result["overall_pass"] else 2)


if __name__ == "__main__":
    main()

