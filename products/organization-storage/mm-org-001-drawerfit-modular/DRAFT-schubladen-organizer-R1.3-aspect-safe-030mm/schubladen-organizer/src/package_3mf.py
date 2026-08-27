#!/usr/bin/env python3
"""Stream indexed module meshes into deterministic Core-namespace 3MF assemblies."""

from __future__ import annotations

import argparse
import hashlib
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
MODULES = ("driver-front", "driver-back", "hardware-front", "hardware-back")
R2_DESTINATION = "output/DRAFT/DRAFT-R2-procedural-wood-assembly.3mf"
R2_REPORT = "reports/three-mf-package-R2-procedural-wood-unmarked.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_identity(path: Path) -> dict:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path)}


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
    if len(header) != 16:
        raise ValueError(f"truncated indexed mesh cache: {path}")
    magic, vertex_count, triangle_count, properties = struct.unpack("<4sIII", header)
    if magic != b"MSH1" or properties != 3:
        raise ValueError(f"unsupported indexed mesh cache: {path}")
    expected = 16 + vertex_count * 12 + triangle_count * 12
    if path.stat().st_size != expected:
        raise ValueError(f"indexed mesh cache length mismatch: {path}")
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


def write_mesh_object(
    stream,
    object_id: int,
    name: str,
    cache: Path,
    vertex_translation: tuple[float, float, float],
) -> dict:
    vertices, faces = mesh_cache(cache)
    stream.write(f'<object id="{object_id}" type="model" name={quoteattr(name)}><mesh><vertices>'.encode("utf-8"))
    bounds_min = np.array([np.inf, np.inf, np.inf], dtype=np.float64)
    bounds_max = np.array([-np.inf, -np.inf, -np.inf], dtype=np.float64)
    block_size = 32768
    offset = np.asarray(vertex_translation, dtype=np.float64)
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
        "id": object_id,
        "name": name,
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "bounds_min_mm": bounds_min.tolist(),
        "bounds_max_mm": bounds_max.tolist(),
    }


def assembly_translations(params: dict) -> dict[str, tuple[float, float, float]]:
    zone = float(params["layout"]["screwdriver_zone_width"])
    split = float(params["layout"]["depth_split"])
    return {
        "driver-front": (0.0, 0.0, 0.0),
        "driver-back": (0.0, split, 0.0),
        "hardware-front": (zone, 0.0, 0.0),
        "hardware-back": (zone, split, 0.0),
    }


def transform_text(translation: tuple[float, float, float]) -> str:
    x, y, z = translation
    return f"1 0 0 0 1 0 0 0 1 {fmt(x)} {fmt(y)} {fmt(z)}"


def package(
    items: list[tuple[str, Path, tuple[float, float, float]]],
    destination: Path,
    metadata: dict[str, str],
    use_build_transforms: bool,
) -> tuple[list[dict], dict, bool]:
    destination.parent.mkdir(parents=True, exist_ok=True)
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

    object_reports: list[dict] = []
    with zipfile.ZipFile(destination, "w", allowZip64=True) as archive:
        archive.writestr(zip_info("[Content_Types].xml"), types_xml)
        archive.writestr(zip_info("_rels/.rels"), rels_xml)
        with archive.open(zip_info("3D/3dmodel.model"), "w", force_zip64=True) as model:
            model.write(
                (
                    f'<?xml version="1.0" encoding="UTF-8"?>\n<model xmlns="{CORE_NS}" unit="millimeter" xml:lang="de-DE">'
                    + "".join(
                        f'<metadata name={quoteattr(name)}>{escape(value)}</metadata>'
                        for name, value in metadata.items()
                    )
                    + "<resources>"
                ).encode("utf-8")
            )
            for object_id, (name, cache, translation) in enumerate(items, start=1):
                vertex_translation = (0.0, 0.0, 0.0) if use_build_transforms else translation
                report = write_mesh_object(model, object_id, name, cache, vertex_translation)
                report["mesh_cache"] = str(cache.relative_to(ROOT))
                report["assembly_translation_mm"] = list(translation)
                report["assembly_bounds_min_mm"] = [
                    report["bounds_min_mm"][axis] + (translation[axis] if use_build_transforms else 0.0)
                    for axis in range(3)
                ]
                report["assembly_bounds_max_mm"] = [
                    report["bounds_max_mm"][axis] + (translation[axis] if use_build_transforms else 0.0)
                    for axis in range(3)
                ]
                object_reports.append(report)
            model.write(b"</resources><build>")
            for object_id, (_, _, translation) in enumerate(items, start=1):
                if use_build_transforms:
                    model.write(
                        f'<item objectid="{object_id}" transform="{transform_text(translation)}"/>'.encode("utf-8")
                    )
                else:
                    model.write(f'<item objectid="{object_id}"/>'.encode("utf-8"))
            model.write(b"</build></model>")

    assembly_bounds = {
        "min": [min(item["assembly_bounds_min_mm"][axis] for item in object_reports) for axis in range(3)],
        "max": [max(item["assembly_bounds_max_mm"][axis] for item in object_reports) for axis in range(3)],
    }
    with zipfile.ZipFile(destination) as archive:
        crc_pass = archive.testzip() is None
    return object_reports, assembly_bounds, crc_pass


def verify_r2_cache_identity(module: str, cache: Path, report_path: Path, revision: str) -> None:
    report = read_json(report_path)
    if report.get("status") != "DRAFT" or report.get("revision") != revision:
        raise SystemExit(f"wrong or non-DRAFT R2 module report: {report_path}")
    if report.get("module", {}).get("id") != module:
        raise SystemExit(f"wrong module identity in {report_path}")
    identity = report.get("identities", {}).get("artifacts", {}).get("mesh_cache", {})
    if identity.get("path") != str(cache.relative_to(ROOT)) or identity.get("sha256") != sha256_file(cache):
        raise SystemExit(f"stale or mismatched R2 indexed mesh cache: {cache}")
    for input_identity in report.get("identities", {}).get("inputs", {}).values():
        source = ROOT / input_identity.get("path", "")
        if not source.is_file() or input_identity.get("sha256") != sha256_file(source):
            raise SystemExit(f"stale R2 module report input identity: {report_path}")
        if cache.stat().st_mtime_ns < source.stat().st_mtime_ns:
            raise SystemExit(f"stale R2 indexed mesh cache: {cache}")


def package_r2_unmarked(params: dict) -> None:
    if not str(params.get("model_revision", "")).startswith("R2-procedural-wood"):
        raise SystemExit("--r2-unmarked requires an R2-procedural-wood model revision")
    translations = assembly_translations(params)
    cache_dir = ROOT / "reports" / "mesh-cache"
    items: list[tuple[str, Path, tuple[float, float, float]]] = []
    module_report_paths: list[Path] = []
    for module in MODULES:
        cache = cache_dir / f"R2-{module}-procedural-wood-unmarked.meshbin"
        report_path = ROOT / "reports" / f"build-final-R2-{module}-procedural-wood-unmarked.json"
        if not cache.is_file():
            raise SystemExit(f"missing R2 indexed mesh cache: {cache}; run the R2 module build first")
        if not report_path.is_file():
            raise SystemExit(f"missing R2 module report: {report_path}")
        verify_r2_cache_identity(module, cache, report_path, params["model_revision"])
        items.append((module, cache, translations[module]))
        module_report_paths.append(report_path)

    destination = ROOT / R2_DESTINATION
    metadata = {
        "Title": "Schubladen-Organizer R2 procedural wood DRAFT unmarked",
        "Application": "Parametric Manifold3D organizer R2 DRAFT pipeline",
        "Status": "DRAFT",
        "Marking": "unmarked",
        "Description": "DRAFT procedural-wood assembly; watermark not loaded or applied.",
    }
    objects, bounds, crc_pass = package(items, destination, metadata, use_build_transforms=True)
    expected_bounds = {"min": [0.0, 0.0, 0.0], "max": [227.0, 357.0, 64.0]}
    envelope_pass = all(
        abs(bounds[key][axis] - expected_bounds[key][axis]) <= 1.0e-6
        for key in ("min", "max")
        for axis in range(3)
    )
    if not crc_pass or not envelope_pass:
        raise SystemExit(f"R2 3MF package failed CRC/envelope checks: CRC={crc_pass}, envelope={bounds}")
    report = {
        "status": "DRAFT",
        "validation_status": "PASS",
        "revision": params["model_revision"],
        "route": "r2-unmarked",
        "file": str(destination.relative_to(ROOT)),
        "file_bytes": destination.stat().st_size,
        "streamed": True,
        "deterministic_zip_metadata": True,
        "core_namespace": CORE_NS,
        "crc_pass": crc_pass,
        "objects": objects,
        "build_items": len(items),
        "build_transforms_from_model_params": True,
        "assembly_bounds_mm": bounds,
        "expected_assembly_bounds_mm": expected_bounds,
        "envelope_pass": envelope_pass,
        "watermark": {"loaded": False, "applied": False},
        "metadata": metadata,
        "identities": {
            "inputs": {
                "model_params": file_identity(ROOT / "config" / "model-params.json"),
                "package_source": file_identity(Path(__file__).resolve()),
                "module_reports": [file_identity(path) for path in module_report_paths],
                "mesh_caches": [file_identity(cache) for _, cache, _ in items],
            },
            "artifacts": {"three_mf": file_identity(destination)},
        },
    }
    report_path = ROOT / R2_REPORT
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"stream-packaged {len(items)} R2 unmarked indexed objects into {destination}")


def package_legacy(params: dict) -> None:
    translations = assembly_translations(params)
    cache_dir = ROOT / "reports" / "mesh-cache"
    items = [(module, cache_dir / f"{module}.meshbin", translations[module]) for module in MODULES]
    for _, cache, _ in items:
        if not cache.is_file():
            raise SystemExit(f"missing indexed mesh cache: {cache}; run the module build first")
    destination = ROOT / "output" / "DRAFT" / params["export"]["assembly_filename"]
    metadata = {
        "Title": params["export"]["assembly_title"],
        "Application": "Parametric Manifold3D organizer pipeline",
    }
    objects, bounds, crc_pass = package(items, destination, metadata, use_build_transforms=False)
    report = {
        "status": "PASS" if crc_pass else "FAIL",
        "file": str(destination.relative_to(ROOT)),
        "streamed": True,
        "core_namespace": CORE_NS,
        "crc_pass": crc_pass,
        "objects": objects,
        "build_items": len(items),
        "assembly_bounds_mm": bounds,
    }
    (ROOT / "reports" / "three-mf-package.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(f"stream-packaged {len(items)} indexed objects into {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality", choices=("final",), default="final")
    parser.add_argument("--r2-unmarked", action="store_true", help="Package only the R2 procedural-wood DRAFT caches")
    args = parser.parse_args()
    params = read_json(ROOT / "config" / "model-params.json")
    if args.r2_unmarked:
        package_r2_unmarked(params)
    else:
        package_legacy(params)


if __name__ == "__main__":
    main()
