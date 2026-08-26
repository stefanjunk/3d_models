#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from common import save_json, sha256_file
from three_mf import CORE_NS

NS = {"m": CORE_NS}


def parse_int(value: str | None, field: str, errors: list[str]) -> int | None:
    try:
        return int(str(value))
    except Exception:
        errors.append(f"Invalid integer for {field}: {value!r}")
        return None


def validate(path: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "valid": False,
        "errors": [],
        "warnings": [],
        "package_members": [],
        "materials": [],
        "objects": [],
        "build_items": [],
    }
    errors: list[str] = report["errors"]
    required = {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = set(archive.namelist())
            report["package_members"] = sorted(names)
            missing = sorted(required - names)
            if missing:
                errors.append(f"Missing package members: {missing}")
                return report
            root = ET.fromstring(archive.read("3D/3dmodel.model"))
    except Exception as exc:
        errors.append(f"Package/XML error: {type(exc).__name__}: {exc}")
        return report

    resources = root.find("m:resources", NS)
    if resources is None:
        errors.append("Missing resources element")
        return report

    material_groups: dict[int, int] = {}
    for group in resources.findall("m:basematerials", NS):
        gid = parse_int(group.get("id"), "basematerials.id", errors)
        if gid is None:
            continue
        bases = group.findall("m:base", NS)
        material_groups[gid] = len(bases)
        for index, base in enumerate(bases):
            report["materials"].append({"group_id": gid, "index": index, "name": base.get("name"), "displaycolor": base.get("displaycolor")})

    object_ids: set[int] = set()
    component_refs: list[tuple[int, int]] = []
    for obj in resources.findall("m:object", NS):
        oid = parse_int(obj.get("id"), "object.id", errors)
        if oid is None:
            continue
        if oid in object_ids:
            errors.append(f"Duplicate object id {oid}")
        object_ids.add(oid)
        item: dict[str, Any] = {"id": oid, "name": obj.get("name"), "type": obj.get("type")}
        pid = obj.get("pid")
        pindex = obj.get("pindex")
        if pid is not None:
            pid_i = parse_int(pid, f"object {oid} pid", errors)
            pindex_i = parse_int(pindex, f"object {oid} pindex", errors)
            item["pid"] = pid_i
            item["pindex"] = pindex_i
            if pid_i not in material_groups:
                errors.append(f"Object {oid} references missing material group {pid_i}")
            elif pindex_i is not None and not (0 <= pindex_i < material_groups[pid_i]):
                errors.append(f"Object {oid} material index {pindex_i} out of range")

        mesh_node = obj.find("m:mesh", NS)
        components = obj.find("m:components", NS)
        if mesh_node is not None:
            vertices_nodes = mesh_node.findall("m:vertices/m:vertex", NS)
            triangle_nodes = mesh_node.findall("m:triangles/m:triangle", NS)
            vertices = np.array([[float(v.get("x", 0)), float(v.get("y", 0)), float(v.get("z", 0))] for v in vertices_nodes], dtype=float)
            faces = []
            for triangle in triangle_nodes:
                face = [parse_int(triangle.get(key), f"object {oid} triangle {key}", errors) for key in ("v1", "v2", "v3")]
                if any(index is None for index in face):
                    continue
                if len(set(face)) != 3:
                    errors.append(f"Object {oid} has a triangle with repeated indices: {face}")
                if any(index < 0 or index >= len(vertices) for index in face):
                    errors.append(f"Object {oid} has triangle index out of bounds: {face}")
                else:
                    faces.append(face)
            mesh = trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces, dtype=np.int64), process=False)
            item.update({
                "kind": "mesh",
                "vertices": int(len(vertices)),
                "faces": int(len(faces)),
                "watertight": bool(mesh.is_watertight),
                "winding_consistent": bool(mesh.is_winding_consistent),
                "connected_bodies": int(mesh.body_count) if len(mesh.faces) else 0,
                "volume_mm3": float(mesh.volume) if mesh.is_volume else None,
                "bounds_mm": mesh.bounds.round(6).tolist() if len(mesh.vertices) else None,
            })
            if not mesh.is_watertight:
                report["warnings"].append(f"Mesh object {oid} is not watertight")
        elif components is not None:
            refs = []
            for component in components.findall("m:component", NS):
                ref = parse_int(component.get("objectid"), f"component in object {oid}", errors)
                if ref is not None:
                    refs.append(ref)
                    component_refs.append((oid, ref))
            item.update({"kind": "components", "component_object_ids": refs})
        else:
            errors.append(f"Object {oid} has neither mesh nor components")
        report["objects"].append(item)

    for owner, ref in component_refs:
        if ref not in object_ids:
            errors.append(f"Component object {owner} references missing object {ref}")

    build = root.find("m:build", NS)
    if build is None:
        errors.append("Missing build element")
    else:
        for item in build.findall("m:item", NS):
            ref = parse_int(item.get("objectid"), "build.item.objectid", errors)
            if ref is not None:
                report["build_items"].append(ref)
                if ref not in object_ids:
                    errors.append(f"Build references missing object {ref}")

    report["valid"] = not errors
    report["mesh_object_count"] = sum(1 for item in report["objects"] if item.get("kind") == "mesh")
    report["assembly_object_count"] = sum(1 for item in report["objects"] if item.get("kind") == "components")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a multicolor 3MF package and its mesh references.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = validate(args.file)
    if args.json_out:
        save_json(args.json_out, report)
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
