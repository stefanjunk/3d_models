#!/usr/bin/env python3
"""Run deterministic topology, image-depth, and optional CAD backend tests."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import tempfile
import traceback

import numpy as np
import trimesh

from heightmap_common import load_image_float, save_png, write_json
from relief_patch import (
    HeightSampler, SurfaceGrid, build_closed_patch, build_surface_grids, make_plane,
)
from validate_mesh import edge_counts, load_mesh, report_for
from mesh_boolean import openscad_boolean

SKILL_ROOT=Path(__file__).resolve().parents[1]


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def topology_check(name: str, mesh: trimesh.Trimesh, allow_multiple: bool=False) -> dict:
    boundary,nonmanifold=edge_counts(mesh)
    check(np.all(np.isfinite(mesh.vertices)),f"{name}: non-finite vertices")
    check(mesh.is_watertight,f"{name}: not watertight")
    check(mesh.is_winding_consistent,f"{name}: inconsistent winding")
    check(mesh.is_volume,f"{name}: not a volume")
    check(boundary==0 and nonmanifold==0,f"{name}: invalid edge incidence")
    if not allow_multiple:
        check(mesh.body_count==1,f"{name}: expected one body, got {mesh.body_count}")
    return {
        "vertices":int(len(mesh.vertices)),"triangles":int(len(mesh.faces)),
        "body_count":int(mesh.body_count),"watertight":True,"is_volume":True,
    }


def run_tests(skip_cadquery: bool,skip_openscad: bool)->dict:
    results={"core":[],"optional":[],"failures":[]}
    with tempfile.TemporaryDirectory(prefix="heightmap-self-test-") as td:
        temp=Path(td)
        # Preserve true 16-bit grayscale rather than silently reducing it to 8-bit.
        original=np.linspace(0,1,257,dtype=np.float32).reshape(1,-1)
        save_png(original,temp/"16bit.png",16)
        loaded,meta=load_image_float(temp/"16bit.png")
        check(meta["source_dtype"]=="uint16","16-bit PNG did not load as uint16")
        check(float(np.max(np.abs(original-loaded))) < 2/65535,"16-bit round-trip error is excessive")
        results["core"].append({"name":"16-bit-heightmap-roundtrip","passed":True})

        # Asymmetric sampler test: flip_u must reverse the sampled horizontal ramp.
        image=np.tile(np.linspace(0,1,16,dtype=np.float32),(8,1))
        sampler=HeightSampler(image)
        grid=make_plane({"type":"plane","width_mm":8,"height_mm":4},1.0)[0]
        normal=sampler.sample(grid,{"mode":"surface_uv"})
        flipped=sampler.sample(grid,{"mode":"surface_uv","flip_u":True})
        check(np.allclose(normal[:,0],flipped[:,-1],atol=1e-5),"flip_u mapping failed")
        results["core"].append({"name":"mapping-flip","passed":True})

        specs=[
            ("plane",{"type":"plane","width_mm":10,"height_mm":8},False),
            ("cylinder",{"type":"cylinder","radius_mm":5,"height_mm":8},False),
            ("cone",{"type":"cone","radius_bottom_mm":6,"radius_top_mm":4,"height_mm":8},False),
            ("rounded_rectangle_wall",{"type":"rounded_rectangle_wall","width_mm":12,"depth_mm":8,"corner_radius_mm":2,"height_mm":6},False),
            ("polygon_wall",{"type":"polygon_wall","sides":6,"radius_mm":8,"height_mm":6},False),
            ("sphere",{"type":"sphere","radius_mm":8,"latitude_min_deg":-50,"latitude_max_deg":50},False),
            ("torus",{"type":"torus","major_radius_mm":8,"minor_radius_mm":2},True),
            ("polygon_ring_plane",{"type":"polygon_ring_plane","sides":6,"outer_radius_mm":8,"inner_radius_mm":6,"edge_gap_mm":0.05},True),
        ]
        for name,spec,allow_multiple in specs:
            grids=build_surface_grids(spec,1.1,temp)
            meshes=[]
            for grid_part in grids:
                heights=0.20+0.80*(0.5+0.5*np.sin(2*math.pi*grid_part.u)*np.cos(2*math.pi*grid_part.v))
                meshes.append(build_closed_patch(grid_part,heights,mode="engrave",depth_mm=0.5,overlap_mm=0.08))
            mesh=trimesh.util.concatenate(meshes)
            summary=topology_check(name,mesh,allow_multiple)
            results["core"].append({"name":name,"passed":True,**summary})

        # Imported arbitrary sampled surface.
        u=np.linspace(0,1,9); v=np.linspace(0,1,7); U,V=np.meshgrid(u,v,indexing="xy")
        P=np.stack((10*U,8*V,0.5*np.sin(math.pi*U)*np.sin(math.pi*V)),axis=-1)
        np.savez(temp/"grid.npz",positions=P,u_length_mm=10.0,v_length_mm=8.0)
        grid=build_surface_grids({"type":"grid_npz","npz":"grid.npz"},1.0,temp)[0]
        mesh=build_closed_patch(grid,0.2+0.8*grid.u,mode="emboss",depth_mm=0.5,overlap_mm=0.08)
        results["core"].append({"name":"grid_npz","passed":True,**topology_check("grid_npz",mesh)})

        if not skip_cadquery:
            try:
                import cadquery as cq
                model=cq.Workplane("XY").box(10,10,10)
                cq.exporters.export(model,str(temp/"cq-box.stl"),tolerance=0.2,angularTolerance=0.3)
                report=report_for(load_mesh(temp/"cq-box.stl"))
                check(report["watertight"] and report["body_count"]==1,"CadQuery export validation failed")
                results["optional"].append({"name":"cadquery-export","passed":True,"triangles":report["triangles"]})
            except Exception as exc:
                results["optional"].append({"name":"cadquery-export","passed":False,"skipped_or_error":str(exc)})

        if not skip_openscad:
            exe=shutil.which("openscad")
            if exe:
                base=trimesh.creation.box((12,12,12))
                tool=trimesh.creation.box((5,5,16))
                base.export(temp/"base.stl"); tool.export(temp/"tool.stl")
                openscad_boolean(temp/"base.stl",[temp/"tool.stl"],temp/"difference.stl","difference",exe)
                report=report_for(load_mesh(temp/"difference.stl"))
                check(report["watertight"] and report["body_count"]==1,"OpenSCAD Boolean validation failed")
                results["optional"].append({"name":"openscad-boolean","passed":True,"triangles":report["triangles"]})
            else:
                results["optional"].append({"name":"openscad-boolean","passed":False,"skipped_or_error":"executable not found"})
    results["passed"]=not results["failures"]
    return results


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-cadquery",action="store_true")
    p.add_argument("--skip-openscad",action="store_true")
    p.add_argument("--report",type=Path,default=SKILL_ROOT/"tests/self-test-report.json")
    args=p.parse_args()
    try:
        result=run_tests(args.skip_cadquery,args.skip_openscad)
    except Exception as exc:
        result={"passed":False,"failures":[{"error":str(exc),"traceback":traceback.format_exc()}]}
    write_json(result,args.report)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result.get("passed") else 1

if __name__=="__main__":
    raise SystemExit(main())
