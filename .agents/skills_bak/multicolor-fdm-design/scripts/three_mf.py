from __future__ import annotations

import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

from common import normalize_hex

CORE_NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
MODEL_REL = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
THUMB_REL = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"
MODEL_CONTENT = "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"

ET.register_namespace("", CORE_NS)


def _mesh_from_path(path: Path) -> trimesh.Trimesh:
    # STL commonly stores every triangle with duplicate vertices. Weld coincident
    # vertices before 3MF export so topology checks reflect the actual solid.
    loaded = trimesh.load(path, force="scene", process=True)
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError(f"No triangle mesh found in {path}")
        mesh = trimesh.util.concatenate(meshes)
    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    else:
        raise ValueError(f"Unsupported geometry in {path}: {type(loaded).__name__}")
    mesh.merge_vertices(merge_tex=True, merge_norm=True)
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(mesh, multibody=True)
    return mesh


def write_multicolor_3mf(
    parts: list[dict[str, Any]],
    output: Path,
    *,
    title: str = "Multicolor FDM assembly",
    thumbnail: Path | None = None,
) -> dict[str, Any]:
    if not parts:
        raise ValueError("At least one part is required")
    model = ET.Element(f"{{{CORE_NS}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    ET.SubElement(model, f"{{{CORE_NS}}}metadata", {"name": "Title"}).text = title
    resources = ET.SubElement(model, f"{{{CORE_NS}}}resources")
    base_materials = ET.SubElement(resources, f"{{{CORE_NS}}}basematerials", {"id": "1"})
    for part in parts:
        ET.SubElement(
            base_materials,
            f"{{{CORE_NS}}}base",
            {
                "name": str(part.get("material_name") or part.get("id") or "material"),
                "displaycolor": normalize_hex(str(part.get("display_hex", "#808080"))),
            },
        )

    loaded_parts: list[tuple[dict[str, Any], trimesh.Trimesh, int]] = []
    for index, part in enumerate(parts):
        path = Path(part["path"])
        mesh = _mesh_from_path(path)
        if len(mesh.faces) == 0:
            raise ValueError(f"Part has no faces: {path}")
        object_id = index + 2
        loaded_parts.append((part, mesh, object_id))
        obj = ET.SubElement(
            resources,
            f"{{{CORE_NS}}}object",
            {"id": str(object_id), "type": "model", "name": str(part.get("id", path.stem)), "pid": "1", "pindex": str(index)},
        )
        mesh_node = ET.SubElement(obj, f"{{{CORE_NS}}}mesh")
        vertices = ET.SubElement(mesh_node, f"{{{CORE_NS}}}vertices")
        for vertex in np.asarray(mesh.vertices, dtype=float):
            ET.SubElement(vertices, f"{{{CORE_NS}}}vertex", {"x": f"{vertex[0]:.9g}", "y": f"{vertex[1]:.9g}", "z": f"{vertex[2]:.9g}"})
        triangles = ET.SubElement(mesh_node, f"{{{CORE_NS}}}triangles")
        for face in np.asarray(mesh.faces, dtype=np.int64):
            ET.SubElement(triangles, f"{{{CORE_NS}}}triangle", {"v1": str(int(face[0])), "v2": str(int(face[1])), "v3": str(int(face[2]))})

    assembly_id = len(parts) + 2
    assembly = ET.SubElement(resources, f"{{{CORE_NS}}}object", {"id": str(assembly_id), "type": "model", "name": "multicolor_assembly"})
    components = ET.SubElement(assembly, f"{{{CORE_NS}}}components")
    for _, _, object_id in loaded_parts:
        ET.SubElement(components, f"{{{CORE_NS}}}component", {"objectid": str(object_id)})
    build = ET.SubElement(model, f"{{{CORE_NS}}}build")
    ET.SubElement(build, f"{{{CORE_NS}}}item", {"objectid": str(assembly_id)})

    model_xml = ET.tostring(model, encoding="utf-8", xml_declaration=True)

    types = ET.Element(f"{{{CONTENT_NS}}}Types")
    ET.SubElement(types, f"{{{CONTENT_NS}}}Default", {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    ET.SubElement(types, f"{{{CONTENT_NS}}}Default", {"Extension": "png", "ContentType": "image/png"})
    ET.SubElement(types, f"{{{CONTENT_NS}}}Override", {"PartName": "/3D/3dmodel.model", "ContentType": MODEL_CONTENT})
    content_xml = ET.tostring(types, encoding="utf-8", xml_declaration=True)

    rels = ET.Element(f"{{{REL_NS}}}Relationships")
    ET.SubElement(rels, f"{{{REL_NS}}}Relationship", {"Id": "rel0", "Type": MODEL_REL, "Target": "/3D/3dmodel.model"})
    if thumbnail:
        ET.SubElement(rels, f"{{{REL_NS}}}Relationship", {"Id": "rel1", "Type": THUMB_REL, "Target": "/Metadata/thumbnail.png"})
    rels_xml = ET.tostring(rels, encoding="utf-8", xml_declaration=True)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_xml)
        archive.writestr("_rels/.rels", rels_xml)
        archive.writestr("3D/3dmodel.model", model_xml)
        if thumbnail:
            archive.write(thumbnail, "Metadata/thumbnail.png")

    return {
        "output": str(output.resolve()),
        "part_count": len(parts),
        "materials": [part.get("material_name") or part.get("id") for part in parts],
        "objects": [
            {
                "id": part.get("id"),
                "path": str(Path(part["path"]).resolve()),
                "vertices": int(len(mesh.vertices)),
                "faces": int(len(mesh.faces)),
                "watertight": bool(mesh.is_watertight),
                "volume_mm3": float(mesh.volume) if mesh.is_volume else None,
            }
            for part, mesh, _ in loaded_parts
        ],
    }
