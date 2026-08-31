#!/usr/bin/env python3
"""Export a deterministic standards-core 3MF beside the Anycubic project 3MF."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import trimesh


CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"
FIXED_ZIP_TIME = (2026, 8, 31, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def number(value: float) -> str:
    return (f"{float(value):.6f}").rstrip("0").rstrip(".") or "0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-stl", required=True, type=Path)
    parser.add_argument("--output-3mf", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    source = args.source_stl.resolve()
    output = args.output_3mf.resolve()
    report_path = args.report.resolve()
    if not source.is_file():
        raise SystemExit(f"Missing STL source: {source}")
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing 3MF: {output}")

    loaded = trimesh.load_mesh(source, process=True)
    if isinstance(loaded, trimesh.Scene):
        mesh = loaded.to_geometry()
    else:
        mesh = loaded
    mesh.merge_vertices()
    if not mesh.is_watertight or not mesh.is_winding_consistent:
        raise SystemExit("Source mesh is not a closed, consistently wound manufacturing mesh")

    ET.register_namespace("", CORE_NS)
    model = ET.Element(f"{{{CORE_NS}}}model", {"unit": "millimeter", f"{{{XML_NS}}}lang": "de-DE"})
    resources = ET.SubElement(model, f"{{{CORE_NS}}}resources")
    materials = ET.SubElement(resources, f"{{{CORE_NS}}}basematerials", {"id": "1"})
    ET.SubElement(materials, f"{{{CORE_NS}}}base", {"name": "PETG provisional", "displaycolor": "#08777DFF"})
    obj = ET.SubElement(
        resources,
        f"{{{CORE_NS}}}object",
        {"id": "2", "type": "model", "name": "DRAFT R7-C01 interface measurement coupon"},
    )
    mesh_node = ET.SubElement(obj, f"{{{CORE_NS}}}mesh")
    vertices_node = ET.SubElement(mesh_node, f"{{{CORE_NS}}}vertices")
    triangles_node = ET.SubElement(mesh_node, f"{{{CORE_NS}}}triangles")
    for x, y, z in mesh.vertices:
        ET.SubElement(vertices_node, f"{{{CORE_NS}}}vertex", {"x": number(x), "y": number(y), "z": number(z)})
    for a, b, c in mesh.faces:
        ET.SubElement(
            triangles_node,
            f"{{{CORE_NS}}}triangle",
            {"v1": str(int(a)), "v2": str(int(b)), "v3": str(int(c)), "pid": "1", "p1": "0", "p2": "0", "p3": "0"},
        )
    build = ET.SubElement(model, f"{{{CORE_NS}}}build")
    ET.SubElement(build, f"{{{CORE_NS}}}item", {"objectid": "2"})
    model_bytes = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(model, encoding="utf-8")
    content_types = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="{CONTENT_NS}">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        "</Types>"
    ).encode()
    relationships = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="{REL_NS}">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        "</Relationships>"
    ).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in (
            ("[Content_Types].xml", content_types),
            ("_rels/.rels", relationships),
            ("3D/3dmodel.model", model_bytes),
        ):
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)

    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "tool": "R7-C01 deterministic Core 3MF exporter",
        "source": record(source),
        "output": record(output),
        "metrics": {
            "vertices": int(len(mesh.vertices)),
            "triangles": int(len(mesh.faces)),
            "components": int(len(mesh.split(only_watertight=False))),
            "watertight": bool(mesh.is_watertight),
            "winding_consistent": bool(mesh.is_winding_consistent),
        },
        "limitations": [
            "This neutral Core 3MF contains no printer, process or filament profile.",
            "Use the separate Anycubic project 3MF for the preserved destination-slicer setup.",
            "No printer upload or print-start action is performed.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output), "report": str(report_path)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
