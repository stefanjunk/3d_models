from __future__ import annotations

import math
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

from .common import check, report

CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
NS = {"m": CORE_NS}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
MODEL_REL = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
MODEL_CONTENT = "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"


def _integer(value: str | None, label: str, errors: list[str]) -> int | None:
    try:
        return int(str(value))
    except Exception:
        errors.append(f"{label} is not an integer: {value!r}")
        return None


def validate(path: Path, policy: dict[str, Any] | None = None, profile: str = "release") -> dict[str, Any]:
    policy = policy or {}
    if not path.is_file():
        return report("validate-3mf", [check("3mf-file", "FAIL", f"3MF not found: {path}")], inputs=[path], profile=profile)
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {"package_members": [], "materials": [], "objects": [], "build_items": []}
    required_members = {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            listed_names = [info.filename for info in infos]
            names = set(listed_names)
            metrics["package_members"] = sorted(names)
            if len(names) != len(listed_names):
                errors.append("ZIP contains duplicate member names")
            if len(infos) > int(policy.get("max_package_members", 10000)):
                errors.append("ZIP contains more members than the configured limit")
            max_uncompressed = float(policy.get("max_uncompressed_mib", 512)) * 1024 * 1024
            total_uncompressed = sum(info.file_size for info in infos)
            metrics["uncompressed_size_bytes"] = total_uncompressed
            if total_uncompressed > max_uncompressed:
                errors.append("ZIP uncompressed size exceeds the configured limit")
            maximum_ratio = float(policy.get("max_compression_ratio", 200))
            for info in infos:
                member = PurePosixPath(info.filename)
                if member.is_absolute() or ".." in member.parts:
                    errors.append(f"unsafe ZIP member path: {info.filename}")
                ratio = info.file_size / max(info.compress_size, 1)
                if ratio > maximum_ratio:
                    errors.append(f"ZIP member compression ratio exceeds limit: {info.filename}")
            corrupt = archive.testzip()
            if corrupt:
                errors.append(f"ZIP CRC check failed: {corrupt}")
            missing = sorted(required_members - names)
            if missing:
                errors.append("missing package members: " + ", ".join(missing))
                root = None
            else:
                content_root = ET.fromstring(archive.read("[Content_Types].xml"))
                overrides = {
                    item.get("PartName"): item.get("ContentType")
                    for item in content_root.findall(f"{{{CONTENT_NS}}}Override")
                }
                if overrides.get("/3D/3dmodel.model") != MODEL_CONTENT:
                    errors.append("content types do not declare the standard 3D model part")
                rel_root = ET.fromstring(archive.read("_rels/.rels"))
                model_targets = [
                    item.get("Target", "").lstrip("/")
                    for item in rel_root.findall(f"{{{REL_NS}}}Relationship")
                    if item.get("Type") == MODEL_REL
                ]
                if "3D/3dmodel.model" not in model_targets:
                    errors.append("root relationships do not target the standard 3D model part")
                root = ET.fromstring(archive.read("3D/3dmodel.model"))
    except Exception as exc:
        return report("validate-3mf", [check("3mf-package", "FAIL", f"{type(exc).__name__}: {exc}")], inputs=[path], profile=profile)
    if root is None:
        return report("validate-3mf", [check("3mf-package", "FAIL", "; ".join(errors))], inputs=[path], profile=profile, metrics=metrics)

    model_unit = root.get("unit", "millimeter")
    metrics["model_unit"] = model_unit
    required_unit = policy.get("require_unit")
    if required_unit is not None and model_unit != required_unit:
        errors.append(f"model unit {model_unit!r} differs from required unit {required_unit!r}")
    resources = root.find("m:resources", NS)
    object_ids: set[int] = set()
    component_refs: list[tuple[int, int]] = []
    material_groups: dict[int, int] = {}
    mesh_payloads: list[tuple[int, list[list[float]], list[list[int]]]] = []
    if resources is None:
        errors.append("missing resources element")
    else:
        for group in resources.findall("m:basematerials", NS):
            group_id = _integer(group.get("id"), "basematerials.id", errors)
            if group_id is None:
                continue
            bases = group.findall("m:base", NS)
            material_groups[group_id] = len(bases)
            for index, base in enumerate(bases):
                metrics["materials"].append({"group_id": group_id, "index": index, "name": base.get("name"), "displaycolor": base.get("displaycolor")})
        for obj in resources.findall("m:object", NS):
            object_id = _integer(obj.get("id"), "object.id", errors)
            if object_id is None:
                continue
            if object_id in object_ids:
                errors.append(f"duplicate object id {object_id}")
            object_ids.add(object_id)
            item: dict[str, Any] = {"id": object_id, "name": obj.get("name"), "type": obj.get("type")}
            object_pid = None
            if obj.get("pid") is not None:
                pid = _integer(obj.get("pid"), f"object {object_id}.pid", errors)
                pindex = _integer(obj.get("pindex"), f"object {object_id}.pindex", errors)
                object_pid = pid
                item.update({"pid": pid, "pindex": pindex})
                if pid not in material_groups:
                    errors.append(f"object {object_id} references missing material group {pid}")
                elif pindex is not None and not 0 <= pindex < material_groups[pid]:
                    errors.append(f"object {object_id} material index {pindex} is out of range")
            mesh_node = obj.find("m:mesh", NS)
            components = obj.find("m:components", NS)
            if mesh_node is not None:
                vertices = []
                for vertex in mesh_node.findall("m:vertices/m:vertex", NS):
                    try:
                        coordinates = [float(vertex.get(axis, "nan")) for axis in ("x", "y", "z")]
                        if not all(math.isfinite(value) for value in coordinates):
                            raise ValueError("non-finite coordinate")
                        vertices.append(coordinates)
                    except Exception:
                        errors.append(f"object {object_id} has invalid vertex coordinates")
                faces = []
                for triangle in mesh_node.findall("m:triangles/m:triangle", NS):
                    face = [_integer(triangle.get(key), f"object {object_id}.{key}", errors) for key in ("v1", "v2", "v3")]
                    if any(value is None for value in face):
                        continue
                    integer_face = [int(value) for value in face]
                    if len(set(integer_face)) != 3:
                        errors.append(f"object {object_id} triangle repeats indices {integer_face}")
                    if any(value < 0 or value >= len(vertices) for value in integer_face):
                        errors.append(f"object {object_id} triangle index out of range {integer_face}")
                    else:
                        faces.append(integer_face)
                    triangle_pid = triangle.get("pid")
                    if triangle_pid is not None or object_pid is not None:
                        pid = _integer(triangle_pid, f"object {object_id} triangle.pid", errors) if triangle_pid is not None else object_pid
                        if pid not in material_groups:
                            errors.append(f"object {object_id} triangle references missing material group {pid}")
                        else:
                            for property_name in ("p1", "p2", "p3"):
                                property_value = triangle.get(property_name, triangle.get("p1", "0"))
                                index = _integer(property_value, f"object {object_id} triangle.{property_name}", errors)
                                if index is not None and not 0 <= index < material_groups[pid]:
                                    errors.append(f"object {object_id} triangle material index {index} is out of range")
                    elif any(triangle.get(name) is not None for name in ("p1", "p2", "p3")):
                        errors.append(f"object {object_id} triangle declares property indices without a property resource id")
                item.update({"kind": "mesh", "vertices": len(vertices), "faces": len(faces)})
                mesh_payloads.append((object_id, vertices, faces))
            elif components is not None:
                refs = []
                for component in components.findall("m:component", NS):
                    ref = _integer(component.get("objectid"), f"object {object_id} component", errors)
                    if ref is not None:
                        refs.append(ref)
                        component_refs.append((object_id, ref))
                    transform = component.get("transform")
                    if transform is not None:
                        try:
                            values = [float(value) for value in transform.split()]
                            if len(values) != 12 or not all(math.isfinite(value) for value in values):
                                raise ValueError
                        except Exception:
                            errors.append(f"object {object_id} component has invalid transform")
                item.update({"kind": "components", "component_object_ids": refs})
            else:
                errors.append(f"object {object_id} has neither mesh nor components")
            metrics["objects"].append(item)
    for owner, ref in component_refs:
        if ref not in object_ids:
            errors.append(f"component object {owner} references missing object {ref}")
    component_graph: dict[int, list[int]] = {}
    for owner, ref in component_refs:
        component_graph.setdefault(owner, []).append(ref)
    visiting: set[int] = set()
    visited: set[int] = set()

    def visit(node: int) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        cyclic = any(visit(child) for child in component_graph.get(node, []))
        visiting.remove(node)
        visited.add(node)
        return cyclic

    if any(visit(node) for node in sorted(component_graph)):
        errors.append("component graph contains a cycle")
    build = root.find("m:build", NS)
    if build is None:
        errors.append("missing build element")
    else:
        for item in build.findall("m:item", NS):
            ref = _integer(item.get("objectid"), "build.item.objectid", errors)
            if ref is not None:
                metrics["build_items"].append(ref)
                if ref not in object_ids:
                    errors.append(f"build references missing object {ref}")
            transform = item.get("transform")
            if transform is not None:
                try:
                    values = [float(value) for value in transform.split()]
                    if len(values) != 12 or not all(math.isfinite(value) for value in values):
                        raise ValueError
                except Exception:
                    errors.append("build item has invalid transform")
        if not metrics["build_items"]:
            errors.append("build element contains no items")

    require_watertight = bool(policy.get("require_watertight_meshes", False))
    require_positive = bool(policy.get("require_positive_volume", False))
    if mesh_payloads and (require_watertight or require_positive or policy.get("inspect_meshes", True)):
        try:
            import numpy as np
            import trimesh

            by_id = {item["id"]: item for item in metrics["objects"]}
            for object_id, vertices, faces in mesh_payloads:
                mesh = trimesh.Trimesh(vertices=np.asarray(vertices), faces=np.asarray(faces, dtype=int), process=False)
                row = by_id[object_id]
                row.update({
                    "watertight": bool(mesh.is_watertight),
                    "winding_consistent": bool(mesh.is_winding_consistent),
                    "positive_volume": bool(mesh.is_volume and mesh.volume > 0),
                    "volume_mm3": float(mesh.volume),
                    "bounds_mm": mesh.bounds.tolist() if len(mesh.vertices) else None,
                })
                if require_watertight and not mesh.is_watertight:
                    errors.append(f"mesh object {object_id} is not watertight")
                elif not mesh.is_watertight:
                    warnings.append(f"mesh object {object_id} is not watertight")
                if require_positive and not (mesh.is_volume and mesh.volume > 0):
                    errors.append(f"mesh object {object_id} is not a positive volume")
        except Exception as exc:
            if require_watertight or require_positive:
                warnings.append(f"required embedded mesh topology check not run: {type(exc).__name__}: {exc}")

    checks = [check("3mf-structure", "PASS" if not errors else "FAIL", "3MF package and references are valid" if not errors else "; ".join(errors), metrics={"error_count": len(errors)})]
    if (require_watertight or require_positive) and any("not run" in item for item in warnings):
        checks.append(check("3mf-mesh-topology", "NOT_RUN", next(item for item in warnings if "not run" in item)))
    minimum_parts = policy.get("min_mesh_objects")
    if minimum_parts is not None:
        actual = len(mesh_payloads)
        checks.append(check("3mf-part-count", "PASS" if actual >= int(minimum_parts) else "FAIL", f"Mesh objects {actual}; minimum {minimum_parts}", metrics={"actual": actual, "minimum": minimum_parts}))
    metrics["warnings"] = warnings
    return report(
        "validate-3mf",
        checks,
        inputs=[path],
        profile=profile,
        metrics=metrics,
        limitations=[
            "Standard 3MF structure does not prove destination-slicer slot mapping or vendor project metadata behavior.",
            "Pairwise color-body overlap and clearance belong in an interface contract.",
        ],
    )
