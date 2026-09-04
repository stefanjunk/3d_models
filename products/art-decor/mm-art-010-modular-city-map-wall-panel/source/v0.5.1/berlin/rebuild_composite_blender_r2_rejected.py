#!/usr/bin/env python3
"""Rejected revision 0.5.1 composite cleanup retained as negative evidence.

The post-triangulation 0.0005 mm dissolve removed the original sliver but
split the boundary-crop left composite into two positive watertight
components.  It is intentionally not used for manufacturing candidates.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import bmesh


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parents[1] / "v0.5.0" / "berlin" / "rebuild_composite_blender.py"


def load_previous():
    spec = importlib.util.spec_from_file_location("mm_art_010_composite_v050", PREVIOUS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load previous composite builder: {PREVIOUS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_mesh(obj) -> None:
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=5e-4)
    bmesh.ops.dissolve_limit(
        bm,
        angle_limit=1e-4,
        verts=bm.verts,
        edges=bm.edges,
        use_dissolve_boundaries=False,
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=5e-4)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.validate(clean_customdata=True)
    mesh.update()


if __name__ == "__main__":
    previous = load_previous()
    previous.clean_mesh = clean_mesh
    previous.main()
