#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from common import save_json, sha256_file


def image_info(material: Any) -> dict[str, Any] | None:
    image = getattr(material, "image", None)
    if image is None:
        image = getattr(material, "baseColorTexture", None)
    if image is None:
        return None
    try:
        return {"width": int(image.width), "height": int(image.height), "mode": str(image.mode)}
    except Exception:
        return {"type": type(image).__name__}


def geometry_report(name: str, mesh: trimesh.Trimesh) -> dict[str, Any]:
    uv = getattr(mesh.visual, "uv", None)
    material = getattr(mesh.visual, "material", None)
    return {
        "name": name,
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "bounds_mm": np.asarray(mesh.bounds).round(6).tolist(),
        "extents_mm": np.asarray(mesh.extents).round(6).tolist(),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "euler_number": int(mesh.euler_number),
        "connected_bodies": int(mesh.body_count),
        "volume_mm3": float(mesh.volume) if mesh.is_volume else None,
        "visual_kind": str(getattr(mesh.visual, "kind", type(mesh.visual).__name__)),
        "uv_count": int(len(uv)) if uv is not None else 0,
        "uv_range": [np.min(uv, axis=0).round(6).tolist(), np.max(uv, axis=0).round(6).tolist()] if uv is not None and len(uv) else None,
        "material_type": type(material).__name__ if material is not None else None,
        "texture": image_info(material),
    }


def obj_dependencies(path: Path) -> list[dict[str, str]]:
    dependencies: list[dict[str, str]] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    mtl_names = re.findall(r"^mtllib\s+(.+)$", text, flags=re.MULTILINE)
    for mtl_name in mtl_names:
        mtl_path = (path.parent / mtl_name.strip()).resolve()
        if not mtl_path.exists():
            dependencies.append({"path": str(mtl_path), "status": "missing"})
            continue
        dependencies.append({"path": str(mtl_path), "status": "present", "sha256": sha256_file(mtl_path)})
        mtl_text = mtl_path.read_text(encoding="utf-8", errors="ignore")
        for tex in re.findall(r"^(?:map_Kd|map_BaseColor)\s+(.+)$", mtl_text, flags=re.MULTILINE | re.IGNORECASE):
            tex_path = (mtl_path.parent / tex.strip()).resolve()
            item = {"path": str(tex_path), "status": "present" if tex_path.exists() else "missing"}
            if tex_path.exists():
                item["sha256"] = sha256_file(tex_path)
            dependencies.append(item)
    return dependencies


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect mesh, UV and texture metadata for OBJ/GLB/glTF assets.")
    parser.add_argument("asset", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    report: dict[str, Any] = {
        "asset": str(args.asset.resolve()),
        "sha256": sha256_file(args.asset),
        "suffix": args.asset.suffix.lower(),
        "draco_marker_present": False,
        "dependencies": [],
        "geometries": [],
        "warnings": [],
    }
    raw = args.asset.read_bytes()
    report["draco_marker_present"] = b"KHR_draco_mesh_compression" in raw
    if args.asset.suffix.lower() == ".obj":
        report["dependencies"] = obj_dependencies(args.asset)

    try:
        loaded = trimesh.load(args.asset, force="scene", process=False)
        scene = loaded if isinstance(loaded, trimesh.Scene) else trimesh.Scene(loaded)
        for name, geometry in scene.geometry.items():
            if isinstance(geometry, trimesh.Trimesh):
                report["geometries"].append(geometry_report(name, geometry))
        report["geometry_count"] = len(report["geometries"])
        if report["geometry_count"] != 1:
            report["warnings"].append("Texture-to-color conversion is most reliable with one normalized textured mesh.")
        if not any(item.get("uv_count", 0) for item in report["geometries"]):
            report["warnings"].append("No UV coordinates detected; image texture sampling is unavailable.")
        if report["draco_marker_present"]:
            report["warnings"].append("KHR_draco_mesh_compression marker detected; some texture-to-color importers do not support Draco-compressed GLB.")
        report["ok"] = bool(report["geometries"])
    except Exception as exc:
        report["ok"] = False
        report["error"] = f"{type(exc).__name__}: {exc}"

    if args.json_out:
        save_json(args.json_out, report)
    print(json.dumps(report, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
