#!/usr/bin/env python3
"""Stream indexed module meshes into a standards-namespaced 3MF assembly."""

from __future__ import annotations

import argparse
import json
import struct
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import numpy as np

from surface_profiles import formatted_export, resolve_surface_profile, surface_choices


ROOT = Path(__file__).resolve().parent.parent
CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 12, 0, 0, 0))
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


def write_lines(stream, lines: list[str]) -> None:
    stream.write(("".join(lines)).encode("utf-8"))


def write_mesh_object(stream, object_id: int, name: str, cache: Path, translation: tuple[float, float, float]) -> dict:
    vertices, faces = mesh_cache(cache)
    stream.write(f'<object id="{object_id}" type="model" name={quoteattr(name)}><mesh><vertices>'.encode("utf-8"))
    bounds_min = np.array([np.inf, np.inf, np.inf], dtype=np.float64)
    bounds_max = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float64)
    block_size = 32768
    offset = np.asarray(translation, dtype=np.float64)
    for first in range(0, len(vertices), block_size):
        block = np.asarray(vertices[first : first + block_size], dtype=np.float64) + offset
        bounds_min = np.minimum(bounds_min, block.min(axis=0))
        bounds_max = np.maximum(bounds_max, block.max(axis=0))
        write_lines(
            stream,
            [f'<vertex x="{fmt(x)}" y="{fmt(y)}" z="{fmt(z)}"/>' for x, y, z in block],
        )
    stream.write(b"</vertices><triangles>")
    for first in range(0, len(faces), block_size):
        block = np.asarray(faces[first : first + block_size])
        write_lines(
            stream,
            [f'<triangle v1="{int(a)}" v2="{int(b)}" v3="{int(c)}"/>' for a, b, c in block],
        )
    stream.write(b"</triangles></mesh></object>")
    return {
        "name": name,
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "bounds_min_mm": bounds_min.tolist(),
        "bounds_max_mm": bounds_max.tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality", choices=("final",), default="final")
    parser.add_argument("--surface", choices=surface_choices(ROOT))
    args = parser.parse_args()
    surface_id, _, surface_profile = resolve_surface_profile(ROOT, args.surface)
    params = json.loads((ROOT / "config" / "model-params.json").read_text(encoding="utf-8"))
    zone = float(params["layout"]["screwdriver_zone_width"])
    split = float(params["layout"]["depth_split"])
    cache_dir = ROOT / "reports" / "mesh-cache"
    items = [
        ("driver-front", cache_dir / "driver-front.meshbin", (0.0, 0.0, 0.0)),
        ("driver-back", cache_dir / "driver-back.meshbin", (0.0, split, 0.0)),
        ("hardware-front", cache_dir / "hardware-front.meshbin", (zone, 0.0, 0.0)),
        ("hardware-back", cache_dir / "hardware-back.meshbin", (zone, split, 0.0)),
    ]
    for _, cache, _ in items:
        if not cache.is_file():
            raise SystemExit(f"missing indexed mesh cache: {cache}; run the module build first")

    destination = ROOT / "output" / "DRAFT" / formatted_export(params, "assembly_filename_template", surface_id)
    title = escape(formatted_export(params, "assembly_title_template", surface_id))
    rels_xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="{REL_NS}">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        "</Relationships>"
    ).encode("utf-8")
    types_xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="{CONTENT_NS}">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        "</Types>"
    ).encode("utf-8")

    object_reports = []
    with zipfile.ZipFile(destination, "w", allowZip64=True) as archive:
        archive.writestr(zip_info("[Content_Types].xml"), types_xml)
        archive.writestr(zip_info("_rels/.rels"), rels_xml)
        with archive.open(zip_info("3D/3dmodel.model"), "w", force_zip64=True) as model:
            model.write(
                (
                    f'<?xml version="1.0" encoding="UTF-8"?>\n<model xmlns="{CORE_NS}" unit="millimeter" xml:lang="de-DE">'
                    f'<metadata name="Title">{title}</metadata>'
                    '<metadata name="Application">Parametric Manifold3D organizer pipeline</metadata><resources>'
                ).encode("utf-8")
            )
            for object_id, (name, cache, translation) in enumerate(items, start=1):
                object_reports.append(write_mesh_object(model, object_id, name, cache, translation))
            model.write(b"</resources><build>")
            for object_id in range(1, len(items) + 1):
                model.write(f'<item objectid="{object_id}"/>'.encode("utf-8"))
            model.write(b"</build></model>")

    report = {
        "status": "PASS",
        "surface_profile": surface_id,
        "representation": surface_profile["representation"],
        "file": str(destination.relative_to(ROOT)),
        "streamed": True,
        "core_namespace": CORE_NS,
        "objects": object_reports,
        "build_items": len(items),
        "assembly_bounds_mm": {
            "min": [min(obj["bounds_min_mm"][axis] for obj in object_reports) for axis in range(3)],
            "max": [max(obj["bounds_max_mm"][axis] for obj in object_reports) for axis in range(3)],
        },
    }
    (ROOT / "reports" / "three-mf-package.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"stream-packaged {len(items)} indexed objects into {destination}")


if __name__ == "__main__":
    main()
