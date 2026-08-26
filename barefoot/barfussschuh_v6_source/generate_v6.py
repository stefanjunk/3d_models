#!/usr/bin/env python3
from __future__ import annotations

import json, math, subprocess, textwrap, zipfile
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator
from shapely.geometry import Polygon, Point
from skimage import measure

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "v6_config.json").read_text(encoding="utf-8"))
L = float(CFG["foot_length"] + CFG["toe_clearance"])

# -----------------------------------------------------------------------------
# Functional-design source profiles
# -----------------------------------------------------------------------------
# s, width, center shift, bottom center, top edge, bottom edge rise, top crown
SOLE_TABLE = np.array([
    [0.00, 0.33*CFG["heel_width"], 0.0, 2.00, 6.90, 0.80, 0.08],
    [0.05, 0.88*CFG["heel_width"], 0.0, 0.80, 5.70, 0.70, 0.10],
    [0.12, 1.07*CFG["heel_width"], -1.0, 0.10, 5.00, 0.58, 0.13],
    [0.22, 1.10*CFG["heel_width"], -2.0, 0.00, 4.90, 0.52, 0.15],
    [0.35, 0.99*CFG["waist_width"], -4.0, 0.00, 4.90, 0.46, 0.20],
    [0.48, 1.04*CFG["waist_width"], -4.0, 0.00, 4.90, 0.46, 0.22],
    [0.62, 0.92*CFG["ball_width"], -2.0, 0.00, 4.90, 0.50, 0.18],
    [0.72, 1.05*CFG["ball_width"], 0.0, 0.00, 4.90, 0.56, 0.15],
    [0.82, 1.05*CFG["toe_box_width"], 2.0, 0.30, 5.20, 0.68, 0.12],
    [0.90, 1.03*CFG["toe_box_width"], 4.0, 1.20, 6.10, 0.78, 0.10],
    [0.96, 0.87*CFG["toe_box_width"], CFG["medial_toe_shift"], 3.00, 7.90, 0.88, 0.08],
    [1.00, 0.45*CFG["toe_box_width"], CFG["medial_toe_shift"], 5.00, 9.90, 0.95, 0.05],
], dtype=float)

# upper inner-last: s, width, center shift, height above base
UPPER_TABLE = np.array([
    [0.02, 52.0,  0.0, 55.0],
    [0.06, 58.0,  0.0, 61.0],
    [0.12, 62.0, -1.0, 65.0],
    [0.22, 64.0, -2.0, 62.0],
    [0.34, 63.0, -4.0, 57.0],
    [0.46, 66.0, -4.0, 51.0],
    [0.58, 75.0, -3.0, 42.0],
    [0.68, 88.0, -1.0, 34.0],
    [0.78, 96.0,  1.0, 27.0],
    [0.88, 94.0,  3.0, 22.0],
    [0.96, 74.0,  5.0, 18.0],
    [0.995, 34.0, 5.0, 14.0],
], dtype=float)

ssole = SOLE_TABLE[:,0]
interp = {name: PchipInterpolator(ssole, SOLE_TABLE[:,i]) for i,name in enumerate(
    ["s","width","shift","bottom","top","edge_rise","top_crown"]
) if i>0}

supper = UPPER_TABLE[:,0]
upper_interp = {
    "width": PchipInterpolator(supper, UPPER_TABLE[:,1]),
    "shift": PchipInterpolator(supper, UPPER_TABLE[:,2]),
    "height": PchipInterpolator(supper, UPPER_TABLE[:,3]),
}


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def sole_vals(s: float):
    s = clamp(s)
    return {k: float(f(s)) for k,f in interp.items()}


def upper_vals(s: float):
    s = clamp(s, supper[0], supper[-1])
    return {k: float(f(s)) for k,f in upper_interp.items()}


def sole_bottom_z(x: float, y: float):
    s = clamp(y/L)
    v = sole_vals(s)
    hw = max(1.0, v["width"]/2)
    t = clamp(abs((x-v["shift"])/hw), 0, 1.2)
    return v["bottom"] + v["edge_rise"] * t**2.4


def sole_top_z(x: float, y: float):
    s = clamp(y/L)
    v = sole_vals(s)
    hw = max(1.0, v["width"]/2)
    t = clamp(abs((x-v["shift"])/hw), 0, 1.2)
    return v["top"] + v["top_crown"] * max(0, 1-t*t)


def sole_section_wire(row):
    s,w,shift,bz,tz,edge_rise,top_crown = map(float,row)
    y = s*L
    hw = w/2
    pts=[]
    for i in range(11):
        t=-1+2*i/10
        pts.append(cq.Vector(shift+hw*t, y, bz+edge_rise*abs(t)**2.4))
    # rounded right wall
    for a in np.linspace(0.12,0.88,6):
        z=(bz+edge_rise)*(1-a)+tz*a
        pts.append(cq.Vector(shift+hw+CFG["sole_side_bulge"]*math.sin(math.pi*a), y, z))
    for i in range(11):
        t=1-2*i/10
        pts.append(cq.Vector(shift+hw*t, y, tz+top_crown*(1-t*t)))
    for a in np.linspace(0.12,0.88,6):
        z=tz*(1-a)+(bz+edge_rise)*a
        pts.append(cq.Vector(shift-hw-CFG["sole_side_bulge"]*math.sin(math.pi*a), y, z))
    edge=cq.Edge.makeSpline(pts, periodic=True, tol=1e-4)
    return cq.Wire.assembleEdges([edge])


def build_organic_sole():
    return cq.Solid.makeLoft([sole_section_wire(r) for r in SOLE_TABLE], ruled=False).clean()


def footprint_polygon():
    ss=np.linspace(0,1,240)
    right=[]; left=[]
    for u in ss:
        v=sole_vals(float(u)); right.append((v["shift"]+v["width"]/2,u*L))
    for u in ss[::-1]:
        v=sole_vals(float(u)); left.append((v["shift"]-v["width"]/2,u*L))
    poly=Polygon(right+left).buffer(0)
    if poly.geom_type != "Polygon": poly=max(poly.geoms,key=lambda g:g.area)
    return poly


def planar_outline_wire(poly: Polygon, offset: float, z: float, n=150):
    p=poly.buffer(offset, join_style="round", quad_segs=10)
    if p.geom_type != "Polygon": p=max(p.geoms,key=lambda g:g.area)
    b=p.exterior
    pts=[]
    for i in range(n):
        q=b.interpolate(b.length*i/n)
        pts.append(cq.Vector(q.x,q.y,z))
    e=cq.Edge.makeSpline(pts, periodic=True, tol=1e-3)
    return cq.Wire.assembleEdges([e])


def build_curved_lip(poly: Polygon):
    root=float(CFG["lip_root_z"]); top=float(CFG["lip_top_z"])
    zlev=[root, root+0.24*(top-root), root+0.56*(top-root), root+0.82*(top-root), top]
    ob=float(CFG["lip_outer_bulge"]); ov=float(CFG["lip_textile_overlap"])
    outoff=[0.0, 0.55*ob, 1.00*ob, 0.65*ob, 0.25*ob]
    inoff=[-(ov+2.3), -(ov+1.5), -(ov+0.9), -(ov+0.35), -ov]
    outer=cq.Solid.makeLoft([planar_outline_wire(poly,o,z) for o,z in zip(outoff,zlev)], ruled=False)
    inner=cq.Solid.makeLoft([planar_outline_wire(poly,o,z) for o,z in zip(inoff,zlev)], ruled=False)
    lip=outer.cut(inner).clean()
    if not lip.isValid(): raise RuntimeError("Curved lip invalid")
    return lip


def perimeter_holes(poly: Polygon):
    b=poly.exterior; per=b.length
    count=max(16,int(round(per/CFG["stitch_hole_spacing"])))
    actual=per/count; pts=[]
    inset=float(CFG["stitch_hole_inset"])
    inner=poly.buffer(-inset,join_style="round")
    bi=inner.exterior
    for i in range(count):
        q=bi.interpolate((i+0.5)*bi.length/count)
        pts.append((q.x,q.y))
    return pts,actual


def rounded_flex_cutter(y: float, depth: float, width: float, big=True):
    r=max(width/2,0.6)
    # X-axis cylinder; top of cutter intersects bottom organically
    center_z = -r + depth
    return cq.Solid.makeCylinder(r, 160.0, cq.Vector(-80,y,center_z), cq.Vector(1,0,0))


def apply_functional_cuts(shape: cq.Shape, poly: Polygon):
    cutters=[]
    # Flex zones
    y=float(CFG["ball_flex_position"])*L
    cutters.append(rounded_flex_cutter(y,float(CFG["ball_flex_depth"]),float(CFG["ball_flex_width"])))
    for p in CFG["minor_flex_positions"]:
        cutters.append(rounded_flex_cutter(float(p)*L,float(CFG["minor_flex_depth"]),float(CFG["minor_flex_width"]),False))
    # Shallow transverse air/moisture channels on foot side
    spacing=float(CFG["top_air_channel_spacing"]); radius=float(CFG["top_air_channel_width"])/2
    for y in np.arange(0.12*L,0.90*L,spacing):
        v=sole_vals(y/L); z=v["top"]+radius-float(CFG["top_air_channel_depth"])
        cutters.append(cq.Solid.makeCylinder(radius,150.0,cq.Vector(-75,y,z),cq.Vector(1,0,0)))
    # Stitch holes through attachment seat
    holes,actual=perimeter_holes(poly)
    for x,y in holes:
        cutters.append(cq.Solid.makeCylinder(float(CFG["stitch_hole_diameter"])/2,7.5,cq.Vector(x,y,3.1),cq.Vector(0,0,1)))
    result=shape.cut(*cutters).clean()
    return result, holes, actual


def apply_stitch_holes_only(shape: cq.Shape, poly: Polygon):
    holes,actual=perimeter_holes(poly)
    cutters=[cq.Solid.makeCylinder(float(CFG["stitch_hole_diameter"])/2,8.5,cq.Vector(x,y,3.0),cq.Vector(0,0,1)) for x,y in holes]
    return shape.cut(*cutters).clean(), holes, actual


def hex_ring_mesh(r: float, line: float, h: float):
    """Fast watertight hex-ring prism in local coordinates, extruded +Z."""
    ri=max(0.25,r-line)
    ang=np.arange(6,dtype=float)*math.pi/3.0
    outer=np.column_stack((r*np.cos(ang),r*np.sin(ang)))
    inner=np.column_stack((ri*np.cos(ang),ri*np.sin(ang)))
    verts=[]
    # ob, ib, ot, it
    for z in (0.0,h):
        verts.extend([[x,y,z] for x,y in outer])
        verts.extend([[x,y,z] for x,y in inner])
    verts=np.asarray(verts,float)
    OB=0; IB=6; OT=12; IT=18
    faces=[]
    def quad(a,b,c,d):
        faces.extend([[a,b,c],[a,c,d]])
    for i in range(6):
        j=(i+1)%6
        quad(OB+i,OB+j,OT+j,OT+i)
        quad(IB+i,IT+i,IT+j,IB+j)
        quad(OT+i,OT+j,IT+j,IT+i)
        quad(OB+i,IB+i,IB+j,OB+j)
    m=trimesh.Trimesh(vertices=verts,faces=np.asarray(faces),process=True)
    m.fix_normals()
    return m


def build_bottom_hex(poly: Polygon):
    r=float(CFG["hex_cell_radius"]); line=float(CFG["hex_line_width"])
    relief=float(CFG["hex_bottom_relief"]); embed=float(CFG["hex_bottom_embed"])
    region=poly.buffer(-1.6,join_style="round")
    minx,miny,maxx,maxy=region.bounds
    px=1.5*r; py=math.sqrt(3)*r
    unit=hex_ring_mesh(r,line,embed+relief)
    meshes=[]
    row=0; y=miny-r
    flex_y=[float(CFG["ball_flex_position"])*L]+[float(p)*L for p in CFG["minor_flex_positions"]]
    while y<=maxy+r:
        x=minx-r + (0.75*r if row%2 else 0.0)
        while x<=maxx+r:
            if region.contains(Point(x,y)) and all(abs(y-fy) > r*0.70 for fy in flex_y):
                z=sole_bottom_z(x,y)-embed
                m=unit.copy(); m.apply_translation((x,y,z)); meshes.append(m)
            x+=px
        y+=py; row+=1
    return trimesh.util.concatenate(meshes), len(meshes)


def tangent_at(boundary, arc, eps=1.0):
    per=boundary.length
    p=boundary.interpolate(arc%per); p0=boundary.interpolate((arc-eps)%per); p1=boundary.interpolate((arc+eps)%per)
    tx=p1.x-p0.x; ty=p1.y-p0.y; n=math.hypot(tx,ty); tx/=n; ty/=n
    nx,ny=ty,-tx
    return p,tx,ty,nx,ny


def build_side_hex(poly: Polygon):
    r=float(CFG["hex_cell_radius"]); line=float(CFG["hex_line_width"])
    embed=float(CFG["hex_side_embed"]); relief=float(CFG["hex_side_relief"])
    unit=hex_ring_mesh(r,line,embed+relief)
    b=poly.exterior; per=b.length
    pitch=1.70*r
    count=max(24,int(per/pitch))
    rows=int(CFG["hex_side_rows"]); meshes=[]
    zrows=np.linspace(5.5,10.8,rows)
    for row,z in enumerate(zrows):
        for i in range(count):
            arc=(i+0.5*(row%2))*per/count
            p,tx,ty,nx,ny=tangent_at(b,arc)
            surface_offset=0.65 if z<7 else 1.10
            # local X=tangent, local Y=vertical, local Z=outward
            T=np.eye(4)
            T[:3,0]=[tx,ty,0]
            T[:3,1]=[0,0,1]
            T[:3,2]=[nx,ny,0]
            T[:3,3]=[p.x+nx*(surface_offset-embed), p.y+ny*(surface_offset-embed), float(z)]
            m=unit.copy(); m.apply_transform(T); meshes.append(m)
    return trimesh.util.concatenate(meshes), len(meshes)

def upper_section_wire(s:float, width_add:float, height_add:float, base_drop:float=0.0):
    v=upper_vals(s); y=s*L; base=sole_vals(s)["top"]+0.55+base_drop
    hw=v["width"]/2 + width_add; h=v["height"]+height_add; shift=v["shift"]
    pts=[]
    # flat-ish lower interface
    for i in range(9):
        t=-1+2*i/8
        pts.append(cq.Vector(shift+hw*t,y,base+0.18*(1-t*t)))
    # upper dome right-to-left
    for theta in np.linspace(0.12*math.pi,0.88*math.pi,18):
        pts.append(cq.Vector(shift+hw*math.cos(theta),y,base+h*(math.sin(theta)**1.12)))
    e=cq.Edge.makeSpline(pts,periodic=True,tol=1e-4)
    return cq.Wire.assembleEdges([e])


def upper_loft(width_add,height_add,base_drop=0.0):
    return cq.Solid.makeLoft([upper_section_wire(float(s),width_add,height_add,base_drop) for s in supper],ruled=False).clean()


def collar_cutter():
    return (cq.Workplane("XY",origin=(0,0,float(CFG["collar_cut_z"])))
            .center(0,float(CFG["collar_center_y_ratio"])*L)
            .ellipse(float(CFG["collar_radius_x"]),float(CFG["collar_radius_y"]))
            .extrude(100).val())


def build_upper_voxel_mesh(out_path:Path, wall:float, perforate:bool=False, frame_only:bool=False, pitch:float|None=None):
    """Generate a robust printable upper shell from the same parametric last.

    The shell is a true volumetric band. For `frame_only`, only attachment,
    heel-counter and collar reinforcement zones are retained.
    """
    pitch=float(CFG["fuzzy_shell_voxel"] if pitch is None else pitch)
    xmin,xmax=-64,68; ymin,ymax=0,L; zmin,zmax=3,76
    xs=np.arange(xmin,xmax+pitch,pitch,dtype=np.float32)
    ys=np.arange(ymin,ymax+pitch,pitch,dtype=np.float32)
    zs=np.arange(zmin,zmax+pitch,pitch,dtype=np.float32)
    vol=np.zeros((len(zs),len(ys),len(xs)),dtype=np.bool_)
    xx=xs[None,:]
    cY=float(CFG["collar_center_y_ratio"])*L
    crx=float(CFG["collar_radius_x"]); cry=float(CFG["collar_radius_y"])
    collar_z=float(CFG["collar_cut_z"])
    for j,y in enumerate(ys):
        if y < float(supper[0])*L or y > float(supper[-1])*L:
            continue
        s=float(y/L); v=upper_vals(s)
        base=sole_vals(s)["top"]+0.55
        def inside(width_add,height_add,base_offset):
            b0=base+base_offset
            hw=v["width"]/2+width_add; h=v["height"]+height_add
            X=(xx-v["shift"])/hw
            Z=(zs[:,None]-b0)/h
            return (zs[:,None]>=b0) & (X*X+Z*Z <= 1.0)
        # Deliberately stagger outer/inner lower boundaries so the shell has
        # a finite closed attachment edge instead of a zero-thickness seam.
        outer=inside(wall,wall+0.35,-0.35)
        inner=inside(0.0,0.0,+0.35)
        mat=outer & (~inner)
        # Open the ankle/collar from above.
        collar_xy=((xx/crx)**2 + ((y-cY)/cry)**2)<=1
        mat &= ~((zs[:,None]>=collar_z) & collar_xy)

        if perforate and CFG.get("fuzzy_perforation_enabled",True) and 0.54*L < y < 0.92*L:
            spacing=float(CFG["fuzzy_perforation_spacing"]); rad=float(CFG["fuzzy_perforation_diameter"])/2
            phase=(round(y/spacing)%2)*spacing/2
            for cx in np.arange(-46,52,spacing)+phase:
                radial=((xx-cx)**2)<=rad*rad
                mat &= ~(radial & (zs[:,None] > base+0.50*v["height"]))

        if frame_only:
            lower = zs[:,None] <= base + float(CFG["upper_lower_band_height"])
            heel = (y <= float(CFG["upper_heel_counter_length_ratio"])*L) & (zs[:,None] <= base+float(CFG["upper_heel_counter_height"]))
            collar_r=np.sqrt((xx/crx)**2 + ((y-cY)/cry)**2)
            cuff=(np.abs(collar_r-1.0) < 0.12) & (zs[:,None] >= collar_z-3.5) & (zs[:,None] <= collar_z+4.5)
            mat &= (lower | heel | cuff)
        vol[:,j,:]=mat

    verts,faces,_,_=measure.marching_cubes(vol.astype(np.float32),level=0.5,spacing=(pitch,pitch,pitch))
    xyz=np.column_stack((verts[:,2]+xmin,verts[:,1]+ymin,verts[:,0]+zmin))
    mesh=trimesh.Trimesh(vertices=xyz,faces=faces,process=True)
    mesh.remove_unreferenced_vertices(); mesh.fix_normals()
    mesh.export(out_path)
    return mesh


def build_infill_upper_mesh(out_path:Path):
    return build_upper_voxel_mesh(out_path,float(CFG["upper_infill_envelope_thickness"]),perforate=False,frame_only=False,pitch=float(CFG["upper_envelope_voxel"]))


def build_fuzzy_shell_mesh(out_path:Path):
    return build_upper_voxel_mesh(out_path,float(CFG["upper_fuzzy_wall_thickness"]),perforate=True,frame_only=False,pitch=float(CFG["fuzzy_shell_voxel"]))


def build_upper_frame_mesh(out_path:Path):
    return build_upper_voxel_mesh(out_path,float(CFG["upper_frame_thickness"]),perforate=False,frame_only=True,pitch=float(CFG["upper_frame_voxel"]))

def mirror_stl(src:Path,dst:Path):
    m=trimesh.load(src,force="mesh")
    T=np.eye(4); T[0,0]=-1
    m.apply_transform(T); m.invert(); m.export(dst)


def write_and_run_functional_cut_scad(poly: Polygon):
    holes,actual=perimeter_holes(poly)
    # Sole body cutters
    lines=['$fn=24;','difference(){','  import("v6_sole_body_smooth_left.stl", convexity=20);','  union(){']
    # ball and minor flex grooves: cylinders along X
    grooves=[(float(CFG["ball_flex_position"])*L,float(CFG["ball_flex_width"]),float(CFG["ball_flex_depth"]))]
    grooves += [(float(p)*L,float(CFG["minor_flex_width"]),float(CFG["minor_flex_depth"])) for p in CFG["minor_flex_positions"]]
    for y,w,d in grooves:
        r=max(w/2,0.6); cz=-r+d
        lines.append(f'    translate([0,{y:.5f},{cz:.5f}]) rotate([0,90,0]) cylinder(h=180,r={r:.5f},center=true);')
    # air channels
    spacing=float(CFG["top_air_channel_spacing"]); r=float(CFG["top_air_channel_width"])/2
    for y in np.arange(0.12*L,0.90*L,spacing):
        v=sole_vals(y/L); z=v["top"]+r-float(CFG["top_air_channel_depth"])
        lines.append(f'    translate([0,{y:.5f},{z:.5f}]) rotate([0,90,0]) cylinder(h=170,r={r:.5f},center=true);')
    # stitch holes
    hr=float(CFG["stitch_hole_diameter"])/2
    for x,y in holes:
        lines.append(f'    translate([{x:.5f},{y:.5f},2.8]) cylinder(h=8.8,r={hr:.5f});')
    lines += ['  }','}']
    (HERE/'v6_cut_sole.scad').write_text('\n'.join(lines)+'\n',encoding='utf-8')

    lines2=['$fn=24;','difference(){','  import("v6_curved_lip_smooth_left.stl", convexity=20);','  union(){']
    for x,y in holes:
        lines2.append(f'    translate([{x:.5f},{y:.5f},2.8]) cylinder(h=9.0,r={hr:.5f});')
    lines2 += ['  }','}']
    (HERE/'v6_cut_lip.scad').write_text('\n'.join(lines2)+'\n',encoding='utf-8')

    subprocess.run(['openscad','-o',str(HERE/'v6_sole_body_left.stl'),str(HERE/'v6_cut_sole.scad')],cwd=HERE,check=True,timeout=180)
    subprocess.run(['openscad','-o',str(HERE/'v6_curved_lip_left.stl'),str(HERE/'v6_cut_lip.scad')],cwd=HERE,check=True,timeout=180)
    return holes,actual


def main():
    print("[V6] footprint", flush=True)
    poly=footprint_polygon()
    # Stage 1: smooth CadQuery freeform BREP masters.
    print("[V6] smooth sole/lip", flush=True)
    sole_body=build_organic_sole()
    curved_lip=build_curved_lip(poly)
    if not sole_body.isValid() or not curved_lip.isValid():
        raise RuntimeError("Smooth sole body or curved lip invalid")
    cq.exporters.export(sole_body,str(HERE/"v6_sole_body_smooth_left.step"))
    cq.exporters.export(curved_lip,str(HERE/"v6_curved_lip_smooth_left.step"))
    cq.exporters.export(sole_body,str(HERE/"v6_sole_body_smooth_left.stl"),tolerance=0.24,angularTolerance=0.20)
    cq.exporters.export(curved_lip,str(HERE/"v6_curved_lip_smooth_left.stl"),tolerance=0.20,angularTolerance=0.18)
    master=cq.Compound.makeCompound([sole_body,curved_lip])
    cq.exporters.export(master,str(HERE/"v6_sole_master_smooth_compound_left.step"))

    # Stage 2: deterministic small print features are subtracted in OpenSCAD.
    print("[V6] functional cuts", flush=True)
    holes,actual=write_and_run_functional_cut_scad(poly)
    print("[V6] functional cuts done", flush=True)

    print("[V6] hex relief", flush=True)
    tread,n_tread=build_bottom_hex(poly); tread.export(HERE/"v6_hex_tread_left.stl")
    sidehex,n_side=build_side_hex(poly); sidehex.export(HERE/"v6_hex_side_left.stl")

    body_mesh=trimesh.load(HERE/"v6_sole_body_left.stl",force="mesh")
    lip_mesh=trimesh.load(HERE/"v6_curved_lip_left.stl",force="mesh")
    scene=trimesh.Scene()
    for name,mesh in [("organic_sole_body",body_mesh),("curved_textile_overlap_lip",lip_mesh),("hex_tread",tread),("hex_side_wrap",sidehex)]:
        scene.add_geometry(mesh,node_name=name,geom_name=name)
    print("[V6] sole 3MF", flush=True)
    scene.export(HERE/"v6_sole_left.3mf")
    T=np.eye(4); T[0,0]=-1
    rscene=trimesh.Scene()
    for name,mesh in [("organic_sole_body",body_mesh),("curved_textile_overlap_lip",lip_mesh),("hex_tread",tread),("hex_side_wrap",sidehex)]:
        rm=mesh.copy(); rm.apply_transform(T); rm.invert()
        rscene.add_geometry(rm,node_name=name,geom_name=name)
    rscene.export(HERE/"v6_sole_right.3mf")
    comp=trimesh.util.concatenate([body_mesh,lip_mesh,tread,sidehex])
    comp.export(HERE/"v6_sole_left_preview_compound.stl")

    # Export a smooth CadQuery reference last for future surface edits.
    print("[V6] upper reference", flush=True)
    reference_last=upper_loft(0.0,0.0,0.0)
    cq.exporters.export(reference_last,str(HERE/"v6_upper_reference_last.step"))

    print("[V6] infill upper", flush=True)
    infill=build_infill_upper_mesh(HERE/"v6_upper_infill_envelope_left.stl")
    mirror_stl(HERE/"v6_upper_infill_envelope_left.stl",HERE/"v6_upper_infill_envelope_right.stl")

    print("[V6] frame", flush=True)
    frame=build_upper_frame_mesh(HERE/"v6_upper_reinforcement_frame_left.stl")
    mirror_stl(HERE/"v6_upper_reinforcement_frame_left.stl",HERE/"v6_upper_reinforcement_frame_right.stl")

    print("[V6] fuzzy shell", flush=True)
    fuzzy=build_fuzzy_shell_mesh(HERE/"v6_upper_fuzzy_shell_left.stl")
    mirror_stl(HERE/"v6_upper_fuzzy_shell_left.stl",HERE/"v6_upper_fuzzy_shell_right.stl")

    # Upper variants remain separate STL parts so slicer-specific settings can be
    # assigned independently without a costly high-poly 3MF repack.

    print("[V6] coupons", flush=True)
    # Test coupons: curved upper-volume swatch + lip/textile retention strip
    swatch=(cq.Workplane("XY").box(45,35,4.5).faces(">Z").workplane().circle(12).cutBlind(-4.5)).val()
    cq.exporters.export(swatch,str(HERE/"testcoupon_infill_only.stl"),tolerance=0.12)
    lip_coupon=(cq.Workplane("XZ").moveTo(0,0).spline([(2,0),(3.3,2.5),(3.0,6),(1.8,8)]).lineTo(-1.2,8).spline([(-1.8,6),(-2.0,3),(-3.8,0)]).close().extrude(55)).val()
    cq.exporters.export(lip_coupon,str(HERE/"testcoupon_lip_textile_overlap.stl"),tolerance=0.12)

    print("[V6] validation", flush=True)
    # Validation report
    sole_m=trimesh.load(HERE/"v6_sole_body_left.stl",force="mesh")
    lip_m=trimesh.load(HERE/"v6_curved_lip_left.stl",force="mesh")
    infill_m=trimesh.load(HERE/"v6_upper_infill_envelope_left.stl",force="mesh")
    frame_m=trimesh.load(HERE/"v6_upper_reinforcement_frame_left.stl",force="mesh")
    report={
        "sole_body_valid_brep": sole_body.isValid(),
        "curved_lip_valid_brep": curved_lip.isValid(),
        "sole_body_mesh_watertight": bool(sole_m.is_watertight),
        "curved_lip_mesh_watertight": bool(lip_m.is_watertight),
        "sole_body_mesh_components": int(len(sole_m.split(only_watertight=False))),
        "curved_lip_mesh_components": int(len(lip_m.split(only_watertight=False))),
        "sole_body_bounds_mm": sole_m.bounds.tolist(),
        "curved_lip_bounds_mm": lip_m.bounds.tolist(),
        "sole_body_faces": int(len(sole_m.faces)),
        "curved_lip_faces": int(len(lip_m.faces)),
        "hex_bottom_cells": int(n_tread),
        "hex_side_cells": int(n_side),
        "stitch_holes": int(len(holes)),
        "stitch_hole_actual_spacing_mm": float(actual),
        "infill_upper_components": int(len(infill_m.split(only_watertight=False))),
        "infill_upper_watertight": bool(infill_m.is_watertight),
        "frame_components": int(len(frame_m.split(only_watertight=False))),
        "frame_watertight": bool(frame_m.is_watertight),
        "fuzzy_shell_watertight": bool(fuzzy.is_watertight),
        "fuzzy_shell_components": int(len(fuzzy.split(only_watertight=False))),
        "cadquery_version": cq.__version__,
    }
    (HERE/"VALIDATION.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__": main()
