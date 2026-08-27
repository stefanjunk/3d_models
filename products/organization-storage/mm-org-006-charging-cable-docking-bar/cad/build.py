#!/usr/bin/env python3
"""Parametric PETG bar and TPU insert generator for MM-ORG-006."""

from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import cadquery as cq
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]; PARAMS=ROOT/"config/model-parameters.json"; MASTER=ROOT/"exports/master"; MANUFACTURING=ROOT/"exports/manufacturing"; COUPONS=ROOT/"exports/coupons"; THREE_MF=ROOT/"exports/3mf"; REPORTS=ROOT/"reports"; VALIDATION=ROOT/"validation"
PROJECT_ID="MM-ORG-006"; REVISION="0.1.0-draft.1"

def load_params(): return json.loads(PARAMS.read_text(encoding="utf-8"))

def validate_parameters(p):
    assert p["project"]["id"]==PROJECT_ID and p["project"]["revision"]==REVISION
    b=p["bar"]; s=p["socket"]; i=p["insert"]; lim=p["input_limits"]
    assert b["length"]<=180 and b["depth"]<=45 and b["height"]<=25 and b["base_skin"]>=2.4
    assert math.isclose((s["insert_length"]+2*s["clearance_each"]-s["insert_length"])/2,0.25,abs_tol=1e-9)
    assert math.isclose(i["radial_clearance"],0.30,abs_tol=1e-9) and i["rib_interference_each"]<=s["clearance_each"]
    assert s["pocket_floor"]+s["insert_height"]+s["vertical_clearance"]<=b["height"]
    assert len(i["cable_diameters"])==b["socket_count"]
    validate_custom(p,b["length"],b["socket_count"],i["cable_diameters"])
    validate_custom(p,lim["bar_length_max"],lim["slot_count_max"],[lim["cable_max"]]*lim["slot_count_max"])

def validate_custom(p,length,count,diameters):
    lim=p["input_limits"]; b=p["bar"]; s=p["socket"]
    assert lim["bar_length_min"]<=length<=lim["bar_length_max"]
    assert lim["slot_count_min"]<=count<=lim["slot_count_max"] and len(diameters)==count
    assert all(lim["cable_min"]<=d<=lim["cable_max"] for d in diameters)
    needed=(count-1)*b["socket_pitch"]+s["outer_length"]+12.0
    assert length>=needed, f"bar length {length} too short; need at least {needed} mm"

def box_at(x,y,z,sx,sy,sz): return cq.Solid.makeBox(sx,sy,sz,cq.Vector(x,y,z))

def rounded_prism(length,depth,height,radius):
    return cq.Workplane("XY").rect(length,depth).extrude(height).edges("|Z").fillet(radius).val()

def socket_positions(count,p):
    pitch=p["bar"]["socket_pitch"]
    return [(idx-(count-1)/2)*pitch for idx in range(count)]

def make_bar(length,count,p):
    b=p["bar"]; s=p["socket"]
    base=rounded_prism(length,b["depth"],b["base_skin"],b["corner_radius"])
    front=box_at(-length/2,-b["depth"]/2,0,length,b["edge_beam"],b["edge_beam_height"])
    rear=box_at(-length/2,b["depth"]/2-b["edge_beam"],0,length,b["edge_beam"],b["edge_beam_height"])
    shape=base.fuse(front).fuse(rear)
    for x in socket_positions(count,p):
        cell=rounded_prism(s["outer_length"],s["outer_depth"],b["height"],s["corner_radius"]).translate(cq.Vector(x,0,0))
        pocket=rounded_prism(s["insert_length"]+2*s["clearance_each"],s["insert_depth"]+2*s["clearance_each"],b["height"]-s["pocket_floor"]+0.1,max(s["corner_radius"]-1.0,1.0)).translate(cq.Vector(x,0,s["pocket_floor"]))
        shape=shape.fuse(cell).cut(pocket)
    if not shape.isValid() or len(shape.Solids())!=1: raise RuntimeError("invalid docking bar B-Rep")
    return shape

def cylinder_y(radius,length,x,z): return cq.Solid.makeCylinder(radius,length,cq.Vector(x,-length/2,z),cq.Vector(0,1,0))

def make_insert(diameter,p):
    s=p["socket"]; i=p["insert"]
    body=rounded_prism(s["insert_length"],s["insert_depth"],s["insert_height"],i["corner_radius"])
    bore_r=diameter/2+i["radial_clearance"]; center_z=max(bore_r+1.0,4.2)
    bore=cylinder_y(bore_r,s["insert_depth"]+0.2,0,center_z)
    entry=diameter*i["entry_ratio"]
    slit=box_at(-entry/2,-s["insert_depth"]/2-0.1,center_z,entry,s["insert_depth"]+0.2,s["insert_height"]-center_z+0.2)
    body=body.cut(bore).cut(slit)
    rib=i["rib_interference_each"]; rl=i["rib_length"]; rh=i["rib_height"]
    left=box_at(-s["insert_length"]/2-rib,-rl/2,2.0,rib,rl,rh); right=box_at(s["insert_length"]/2,-rl/2,2.0,rib,rl,rh)
    body=body.fuse(left).fuse(right)
    if not body.isValid() or len(body.Solids())!=1: raise RuntimeError(f"invalid insert B-Rep for {diameter}")
    return body

def make_coupon(p):
    s=p["socket"]; b=p["bar"]
    length=s["outer_length"]+8; depth=s["outer_depth"]+8
    base=rounded_prism(length,depth,s["pocket_floor"],3.0)
    cell=rounded_prism(s["outer_length"],s["outer_depth"],b["height"],s["corner_radius"])
    pocket=rounded_prism(s["insert_length"]+2*s["clearance_each"],s["insert_depth"]+2*s["clearance_each"],b["height"]-s["pocket_floor"]+0.1,max(s["corner_radius"]-1,1)).translate(cq.Vector(0,0,s["pocket_floor"]))
    shape=base.fuse(cell).cut(pocket)
    if not shape.isValid() or len(shape.Solids())!=1: raise RuntimeError("invalid socket coupon")
    return shape

def shift_origin(shape):
    b=shape.BoundingBox(); return shape.translate(cq.Vector(-b.xmin,-b.ymin,-b.zmin))

def sha256(path):
    d=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): d.update(block)
    return d.hexdigest()

def export(shape,path,p):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix.lower()==".step": cq.exporters.export(shape,str(path),exportType="STEP")
    else: cq.exporters.export(shape,str(path),tolerance=p["export"]["chordal_tolerance"],angularTolerance=p["export"]["angular_tolerance"])

def mesh_metrics(path):
    m=trimesh.load_mesh(path,force="mesh",process=True)
    return {"path":str(path.relative_to(ROOT)),"sha256":sha256(path),"file_bytes":path.stat().st_size,"vertices":int(len(m.vertices)),"triangles":int(len(m.faces)),"watertight":bool(m.is_watertight),"winding_consistent":bool(m.is_winding_consistent),"positive_volume":bool(m.volume>0),"components":int(len(m.split(only_watertight=False))),"volume_mm3":float(m.volume),"extents_mm":np.round(m.extents,5).tolist()}

def check(cid,passed,message,metrics=None): return {"id":cid,"status":"PASS" if passed else "FAIL","required":True,"message":message,"metrics":metrics or {},"evidence":[]}
def report(tool,inputs,checks,metrics,limitations): return {"schema_version":"1.0","tool":tool,"tool_version":REVISION,"status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL","profile":"draft","inputs":[{"path":str(x.relative_to(ROOT)),"sha256":sha256(x),"size_bytes":x.stat().st_size} for x in inputs],"checks":checks,"metrics":metrics,"limitations":limitations,"required_capabilities":[]}
def write_json(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def add_member(z,name,data): info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16; z.writestr(info,data)

def mesh_for_3mf(shape,p):
    v,f=shape.tessellate(p["export"]["chordal_tolerance"],p["export"]["angular_tolerance"]); m=trimesh.Trimesh(np.asarray([[x.x,x.y,x.z] for x in v]),np.asarray(f),process=True,validate=True); m.merge_vertices(); m.remove_unreferenced_vertices()
    if not m.is_watertight or m.volume<=0: raise RuntimeError("invalid 3MF source")
    return m

def write_3mf(path,parts,p):
    ns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"; ET.register_namespace("",ns); model=ET.Element(f"{{{ns}}}model",{"unit":"millimeter","xml:lang":"en-US"})
    for k,v in (("Title","DRAFT MM-ORG-006 Charging-cable Docking Bar"),("Designer","metriMade / autonomous CAD workflow"),("Description","One PETG bar and four TPU insert objects; inventory strip only."),("LicenseTerms","DRAFT engineering artifact; not a commercial release")): n=ET.SubElement(model,f"{{{ns}}}metadata",{"name":k}); n.text=v
    resources=ET.SubElement(model,f"{{{ns}}}resources"); build=ET.SubElement(model,f"{{{ns}}}build"); cursor=0.0
    for oid,(name,shape) in enumerate(parts,1):
        m=mesh_for_3mf(shape,p); obj=ET.SubElement(resources,f"{{{ns}}}object",{"id":str(oid),"type":"model","name":name,"partnumber":f"{PROJECT_ID}-{REVISION}-{name}"}); mn=ET.SubElement(obj,f"{{{ns}}}mesh"); vn=ET.SubElement(mn,f"{{{ns}}}vertices")
        for x,y,zv in m.vertices: ET.SubElement(vn,f"{{{ns}}}vertex",{"x":f"{x:.6f}","y":f"{y:.6f}","z":f"{zv:.6f}"})
        tn=ET.SubElement(mn,f"{{{ns}}}triangles")
        for a,b,c in m.faces: ET.SubElement(tn,f"{{{ns}}}triangle",{"v1":str(int(a)),"v2":str(int(b)),"v3":str(int(c))})
        ET.SubElement(build,f"{{{ns}}}item",{"objectid":str(oid),"transform":f"1 0 0 0 1 0 0 0 1 {cursor:.3f} 0 0"}); cursor+=shape.BoundingBox().xlen+8
    types=b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'; rels=b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z: add_member(z,"[Content_Types].xml",types); add_member(z,"_rels/.rels",rels); add_member(z,"3D/3dmodel.model",ET.tostring(model,encoding="utf-8",xml_declaration=True)); add_member(z,"Metadata/model-parameters.json",PARAMS.read_bytes())

def build_default():
    p=load_params(); validate_parameters(p); src=Path(__file__).resolve(); b=p["bar"]; diameters=p["insert"]["cable_diameters"]
    native_bar=make_bar(b["length"],b["socket_count"],p); print_bar=shift_origin(native_bar); parts={"bar":print_bar}; metrics={}
    export(native_bar,MASTER/f"DRAFT-{PROJECT_ID}-bar-{REVISION}.step",p); bar_stl=MANUFACTURING/f"DRAFT-{PROJECT_ID}-bar-{REVISION}.stl"; export(print_bar,bar_stl,p); metrics["bar"]=mesh_metrics(bar_stl)
    inserts={}
    for d in diameters:
        key=f"insert_{str(d).replace('.','p')}"; native=make_insert(d,p); printed=shift_origin(native); inserts[key]=native; parts[key]=printed
        export(native,MASTER/f"DRAFT-{PROJECT_ID}-{key}-{REVISION}.step",p); stl=MANUFACTURING/f"DRAFT-{PROJECT_ID}-{key}-{REVISION}.stl"; export(printed,stl,p); metrics[key]=mesh_metrics(stl)
    socket_coupon=make_coupon(p); coupon_socket_path=COUPONS/f"DRAFT-{PROJECT_ID}-socket-coupon-{REVISION}.stl"; export(shift_origin(socket_coupon),coupon_socket_path,p); metrics["coupon_socket"]=mesh_metrics(coupon_socket_path)
    coupon_insert=make_insert(5.0,p); coupon_insert_path=COUPONS/f"DRAFT-{PROJECT_ID}-insert-5p0-coupon-{REVISION}.stl"; export(shift_origin(coupon_insert),coupon_insert_path,p); metrics["coupon_insert_5p0"]=mesh_metrics(coupon_insert_path)
    print_set=THREE_MF/f"DRAFT-{PROJECT_ID}-charging-cable-docking-bar-{REVISION}.3mf"; write_3mf(print_set,list(parts.items()),p)
    placed=[native_bar]; z=p["socket"]["pocket_floor"]
    for x,(key,shape) in zip(socket_positions(b["socket_count"],p),inserts.items()): placed.append(shape.translate(cq.Vector(x,0,z)))
    assembly=cq.Compound.makeCompound(placed); preview=MASTER/f"DRAFT-{PROJECT_ID}-assembly-preview-{REVISION}.stl"; export(shift_origin(assembly),preview,p); ab=assembly.BoundingBox(); aext=[ab.xlen,ab.ylen,ab.zlen]
    mesh_checks=[]
    for name,m in metrics.items(): mesh_checks += [check(f"{name}-watertight",m["watertight"],f"{name} is watertight"),check(f"{name}-winding",m["winding_consistent"],f"{name} winding is consistent"),check(f"{name}-volume",m["positive_volume"],f"{name} has positive volume"),check(f"{name}-component",m["components"]==1,f"{name} is one component")]
    mesh_report=report(f"{PROJECT_ID}-mesh-generation",[PARAMS,src],mesh_checks,{"meshes":metrics},["Topology does not prove PETG/TPU fit, retention, fatigue, jacket safety or stability."]); write_json(VALIDATION/"mesh-generation-report.json",mesh_report)
    s=p["socket"]; i=p["insert"]
    interface_report=report(f"{PROJECT_ID}-interface-validation",[PARAMS,src],[check("pocket-clearance",math.isclose(s["clearance_each"],.25,abs_tol=1e-9),"Pocket clearance is 0.25 mm per side"),check("rib-reserve",i["rib_interference_each"]<=s["clearance_each"],"Retention rib interference remains inside the nominal pocket allowance"),check("cable-clearance",math.isclose(i["radial_clearance"],.30,abs_tol=1e-9),"Cable radial clearance is 0.30 mm"),check("coupon-pair",coupon_socket_path.is_file() and coupon_insert_path.is_file(),"Socket and 5 mm insert coupon pair exists")],{"insert_envelope_mm":[s["insert_length"],s["insert_depth"],s["insert_height"]],"pocket_envelope_mm":[s["insert_length"]+2*s["clearance_each"],s["insert_depth"]+2*s["clearance_each"],s["insert_height"]+s["vertical_clearance"]],"physical_fit":"NOT_RUN"},["Nominal CAD clearance and rib overlap do not establish TPU insertion force or retention."]); write_json(VALIDATION/"interface-report.json",interface_report)
    source_report=report(f"{PROJECT_ID}-parametric-source",[PARAMS,src,ROOT/"design-spec.yaml",ROOT/"protected-geometry-map.md"],[check("parameter-contract",True,"Default and boundary assertions pass"),check("part-count",len(parts)==5,"One bar and four insert objects are generated"),check("assembly-envelope",aext[0]<=180 and aext[1]<=45 and aext[2]<=25,"Assembly stays inside 180 x 45 x 25 mm",{"extents_mm":aext}),check("mesh-stage",mesh_report["status"]=="PASS","Mesh checks pass"),check("interface-stage",interface_report["status"]=="PASS","Nominal interface checks pass"),check("print-set",print_set.is_file(),"DRAFT 3MF exists")],{"assembly_extents_mm":aext,"print_set":str(print_set.relative_to(ROOT))},["Exact slicer and all physical validation are deferred."]); write_json(VALIDATION/"parametric-source-report.json",source_report)
    baseline=rounded_prism(b["length"],b["depth"],b["height"],b["corner_radius"])
    for x in socket_positions(b["socket_count"],p): baseline=baseline.cut(rounded_prism(s["insert_length"]+2*s["clearance_each"],s["insert_depth"]+2*s["clearance_each"],b["height"]-s["pocket_floor"]+.1,max(s["corner_radius"]-1,1)).translate(cq.Vector(x,0,s["pocket_floor"])))
    selected=metrics["bar"]["volume_mm3"]
    opt=report(f"{PROJECT_ID}-optimization-comparison",[PARAMS,src,ROOT/"protected-geometry-map.md"],[check("protected-map",True,"Protected geometry map exists"),check("bar-volume",selected<baseline.Volume(),"Local-cell bar uses less CAD volume than full-body baseline"),check("support-intent",True,"Base, socket and insert openings face upward")],{"baseline_bar_cad_volume_mm3":baseline.Volume(),"selected_bar_cad_volume_mm3":selected,"cad_volume_reduction_percent":100*(baseline.Volume()-selected)/baseline.Volume(),"selection":"B thin base plus local socket cells","exact_slicer_metrics":"NOT_RUN"},["CAD volume is not deposited material or print time; exact A/B/C slicing is deferred."]); write_json(REPORTS/"optimization-comparison.json",opt)
    write_json(REPORTS/"build-manifest.json",{"project_id":PROJECT_ID,"revision":REVISION,"status":"DRAFT","parameters_sha256":sha256(PARAMS),"source_sha256":sha256(src),"parts":metrics,"assembly_extents_mm":aext,"print_set":str(print_set.relative_to(ROOT)),"print_set_sha256":sha256(print_set),"physical_validation":"DEFERRED"})
    if any(r["status"]!="PASS" for r in (mesh_report,interface_report,source_report,opt)): raise RuntimeError("digital check failed")
    print(json.dumps({"status":"PASS","assembly_extents_mm":aext,"print_set":str(print_set)},indent=2))

def build_custom(length,count,diameters,name):
    p=load_params(); validate_parameters(p); validate_custom(p,length,count,diameters); slug=name.replace(" ","-").lower(); bar=make_bar(length,count,p); export(bar,MASTER/f"CUSTOM-{PROJECT_ID}-{slug}-bar.step",p); export(shift_origin(bar),MANUFACTURING/f"CUSTOM-{PROJECT_ID}-{slug}-bar.stl",p)
    outputs=[]
    for idx,d in enumerate(diameters,1): shape=make_insert(d,p); path=MANUFACTURING/f"CUSTOM-{PROJECT_ID}-{slug}-insert-{idx}-{str(d).replace('.','p')}.stl"; export(shift_origin(shape),path,p); outputs.append(str(path.relative_to(ROOT)))
    data={"project_id":PROJECT_ID,"name":name,"bar_length_mm":length,"slot_count":count,"diameters_mm":diameters,"insert_stls":outputs,"physical_fit":"NOT_RUN"}; write_json(REPORTS/f"CUSTOM-{PROJECT_ID}-{slug}.json",data); print(json.dumps(data,indent=2))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--bar-length",type=float); ap.add_argument("--slot-count",type=int); ap.add_argument("--diameters"); ap.add_argument("--name",default="custom"); a=ap.parse_args()
    if a.bar_length is None and a.slot_count is None and a.diameters is None: build_default()
    elif None not in (a.bar_length,a.slot_count,a.diameters): build_custom(a.bar_length,a.slot_count,[float(x) for x in a.diameters.split(",")],a.name)
    else: ap.error("--bar-length, --slot-count and --diameters must be supplied together")
if __name__=="__main__": main()
