#!/usr/bin/env python3
"""Package the nine local module meshes and comb into a deterministic 3MF assembly."""

from __future__ import annotations

import json
import struct
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import numpy as np


ROOT = Path(__file__).resolve().parent.parent
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 26, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    return info


def fmt(value: float) -> str:
    if abs(value) < 5.0e-8:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def mesh_cache(path: Path) -> tuple[np.memmap, np.memmap]:
    with path.open("rb") as handle:
        header = handle.read(16)
    magic, vertex_count, triangle_count, properties = struct.unpack("<4sIII", header)
    if magic != b"MSH1" or properties != 3:
        raise ValueError(f"unsupported indexed mesh cache: {path}")
    vertices = np.memmap(path, dtype="<f4", mode="r", offset=16, shape=(vertex_count, 3))
    faces = np.memmap(
        path,
        dtype="<u4",
        mode="r",
        offset=16 + vertex_count * 12,
        shape=(triangle_count, 3),
    )
    return vertices, faces


def write_mesh_object(stream, object_id: int, name: str, cache: Path) -> dict:
    vertices, faces = mesh_cache(cache)
    stream.write(f'<object id="{object_id}" type="model" name={quoteattr(name)}><mesh><vertices>'.encode())
    for x, y, z in np.asarray(vertices, dtype=np.float64):
        stream.write(f'<vertex x="{fmt(x)}" y="{fmt(y)}" z="{fmt(z)}"/>'.encode())
    stream.write(b"</vertices><triangles>")
    for a, b, c in np.asarray(faces):
        stream.write(f'<triangle v1="{int(a)}" v2="{int(b)}" v3="{int(c)}"/>'.encode())
    stream.write(b"</triangles></mesh></object>")
    return {"name": name, "vertices": int(len(vertices)), "triangles": int(len(faces))}


def transform_string(translation: list[float]) -> str:
    tx, ty, tz = translation
    return f"1 0 0 0 1 0 0 0 1 {fmt(tx)} {fmt(ty)} {fmt(tz)}"


def main() -> None:
    params = json.loads((ROOT / "config" / "model-params.json").read_text(encoding="utf-8"))
    build = json.loads((ROOT / "reports" / "build-report.json").read_text(encoding="utf-8"))
    items = [
        {
            "name": module["id"],
            "cache": ROOT / module["mesh_cache"],
            "translation": module["assembly_translation_mm"],
        }
        for module in build["modules"]
    ]
    comb = build["accessories"]["screwdriver_comb"]
    items.append(
        {
            "name": "screwdriver-comb",
            "cache": ROOT / comb["mesh_cache"],
            "translation": comb["assembly_translation_mm"],
        }
    )
    if len(items) != 10:
        raise SystemExit(f"safe-core assembly requires exactly 10 objects, found {len(items)}")
    for item in items:
        if not item["cache"].is_file():
            raise SystemExit(f"missing mesh cache: {item['cache']}; run npm run build first")

    output = ROOT / "output" / "DRAFT" / params["export"]["assembly_3mf"]
    title = escape(f"MM-ORG-001 v0.1.0-draft.1 common-220 assembly DRAFT")
    rels_xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="{REL_NS}">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        "</Relationships>"
    ).encode()
    types_xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="{CONTENT_NS}">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        "</Types>"
    ).encode()

    object_reports: list[dict] = []
    with zipfile.ZipFile(output, "w", allowZip64=True) as archive:
        archive.writestr(zip_info("[Content_Types].xml"), types_xml)
        archive.writestr(zip_info("_rels/.rels"), rels_xml)
        with archive.open(zip_info("3D/3dmodel.model"), "w", force_zip64=True) as model:
            model.write(
                (
                    f'<?xml version="1.0" encoding="UTF-8"?>\n<model xmlns="{CORE_NS}" unit="millimeter" xml:lang="de-DE">'
                    f'<metadata name="Title">{title}</metadata>'
                    '<metadata name="Application">MM-ORG-001 Manifold3D DRAFT pipeline</metadata>'
                    '<metadata name="Description">Nine modules plus removable comb; not release-approved</metadata><resources>'
                ).encode()
            )
            for object_id, item in enumerate(items, start=1):
                object_reports.append(write_mesh_object(model, object_id, item["name"], item["cache"]))
            model.write(b"</resources><build>")
            for object_id, item in enumerate(items, start=1):
                transform = transform_string(item["translation"])
                model.write(f'<item objectid="{object_id}" transform="{transform}"/>'.encode())
            model.write(b"</build></model>")

    report = {
        "status": "DRAFT_NOT_FOR_RELEASE",
        "file": str(output.relative_to(ROOT)),
        "core_namespace": CORE_NS,
        "object_count": len(items),
        "build_item_count": len(items),
        "objects": [
            {**mesh, "translation_mm": item["translation"]}
            for mesh, item in zip(object_reports, items, strict=True)
        ],
    }
    (ROOT / "reports" / "three-mf-package.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"packaged {len(items)} objects into {output}")


if __name__ == "__main__":
    main()
