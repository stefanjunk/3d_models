#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import distance_transform_edt
from skimage import measure

HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/'v6_config.json').read_text())
L=float(CFG['foot_length']+CFG['toe_clearance'])
SOLE_TABLE=np.array([
    [0.00, 0.33*CFG['heel_width'], 0.0, 2.00, 6.90, 0.80, 0.08],
    [0.05, 0.88*CFG['heel_width'], 0.0, 0.80, 5.70, 0.70, 0.10],
    [0.12, 1.07*CFG['heel_width'], -1.0, 0.10, 5.00, 0.58, 0.13],
    [0.22, 1.10*CFG['heel_width'], -2.0, 0.00, 4.90, 0.52, 0.15],
    [0.35, 0.99*CFG['waist_width'], -4.0, 0.00, 4.90, 0.46, 0.20],
    [0.48, 1.04*CFG['waist_width'], -4.0, 0.00, 4.90, 0.46, 0.22],
    [0.62, 0.92*CFG['ball_width'], -2.0, 0.00, 4.90, 0.50, 0.18],
    [0.72, 1.05*CFG['ball_width'], 0.0, 0.00, 4.90, 0.56, 0.15],
    [0.82, 1.05*CFG['toe_box_width'], 2.0, 0.30, 5.20, 0.68, 0.12],
    [0.90, 1.03*CFG['toe_box_width'], 4.0, 1.20, 6.10, 0.78, 0.10],
    [0.96, 0.87*CFG['toe_box_width'], CFG['medial_toe_shift'], 3.00, 7.90, 0.88, 0.08],
    [1.00, 0.45*CFG['toe_box_width'], CFG['medial_toe_shift'], 5.00, 9.90, 0.95, 0.05],
],dtype=float)
UPPER_TABLE=np.array([
    [0.00, 20.0,  0.0, 10.0],
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
    [0.995,34.0,  5.0, 11.0],
    [1.00, 6.0,  5.0, 10.0],
],dtype=float)
sf=SOLE_TABLE[:,0]; uf=UPPER_TABLE[:,0]
sole_interp={name:PchipInterpolator(sf,SOLE_TABLE[:,i]) for i,name in enumerate(['s','width','shift','bottom','top','edge_rise','top_crown']) if i>0}
upper_interp={name:PchipInterpolator(uf,UPPER_TABLE[:,i]) for i,name in enumerate(['s','width','shift','height']) if i>0}

def clamp(v,lo=0.0,hi=1.0): return max(lo,min(hi,v))
def smooth(t): t=clamp(t); return t*t*(3-2*t)
def sole_vals(s): s=clamp(s); return {k:float(f(s)) for k,f in sole_interp.items()}
def upper_vals(s): s=clamp(s); return {k:float(f(s)) for k,f in upper_interp.items()}
def taper_height(s,nominal):
    skirt=float(CFG['upper_skirt_height'])
    hf=smooth(s/max(1e-6,float(CFG['upper_heel_taper_ratio'])))
    tf=smooth((1-s)/max(1e-6,float(CFG['upper_toe_taper_ratio'])))
    return skirt+max(0.0,nominal-skirt)*min(hf,tf)

def make_core(pitch, wall):
    # padded grid so marching cubes always gets closed surfaces
    xmin,xmax=-70,74; ymin,ymax=-8.0,L+8.0; zmin,zmax=0.0,80.0
    xs=np.arange(xmin,xmax+pitch,pitch,dtype=np.float32)
    ys=np.arange(ymin,ymax+pitch,pitch,dtype=np.float32)
    zs=np.arange(zmin,zmax+pitch,pitch,dtype=np.float32)
    core=np.zeros((len(zs),len(ys),len(xs)),dtype=np.bool_)
    meta=[]; xx=xs[None,:]
    inset=float(CFG['upper_lower_interface_inset']); skirt=float(CFG['upper_skirt_height'])
    for j,y in enumerate(ys):
        end_margin=max(0.5, wall-0.7)
        if y<end_margin or y>L-end_margin:
            meta.append(None); continue
        s=clamp(float(y/L)); sv=sole_vals(s); uv=upper_vals(s)
        # Core is the inner void. Euclidean offset by `wall` produces the
        # outer shoe surface. Therefore subtract wall here so the OUTER lower
        # edge, not the inner void, matches the sole/lip interface.
        outer_base=sv['top']+0.55
        base=outer_base + wall - 0.7
        outer_h=max(skirt+0.5,taper_height(s,uv['height']))
        h=max(skirt+0.5, outer_h-wall)
        lower_hw=max(1.2,sv['width']/2-inset-wall); lower_shift=sv['shift']
        crown_hw=max(1.2,uv['width']/2-wall); crown_shift=uv['shift']
        dz=zs[:,None]-base; valid=(dz>=0)&(dz<=h)
        u=np.clip((dz-skirt)/max(0.5,h-skirt),0.0,1.0)
        sm=u*u*(3-2*u)
        center=lower_shift*(1-sm)+crown_shift*sm
        maxhw=lower_hw*(1-sm)+crown_hw*sm
        dome=np.cos(0.5*np.pi*np.power(u,0.92))
        hw=np.maximum(0.30,maxhw*dome)
        core[:,j,:]=valid&(np.abs(xx-center)<=hw)
        meta.append((base,lower_hw,lower_shift))
    return xs,ys,zs,core,meta

def make_upper(out_path,wall,frame_only,pitch):
    xs,ys,zs,core,meta=make_core(pitch,wall)
    # Euclidean offset of the anatomical last: robust, continuous outer band.
    dist=distance_transform_edt(~core,sampling=(pitch,pitch,pitch))
    outer=core | (dist<=wall)
    shell=outer & (~core)
    xx=xs[None,:]
    # Remove the broad bottom floor; retain only a strong perimeter attachment ring.
    attachment_radial=5.0
    for j,m in enumerate(meta):
        if m is None: continue
        base,hw,shift=m
        low=(zs[:,None] <= base+2.2)
        interior=np.abs(xx-shift) < max(0.0,hw-attachment_radial)
        shell[:,j,:] &= ~(low & interior)
    # Open ankle/collar.
    cY=float(CFG['collar_center_y_ratio'])*L; crx=float(CFG['collar_radius_x']); cry=float(CFG['collar_radius_y']); collar_z=float(CFG['collar_cut_z'])
    for j,y in enumerate(ys):
        collar_xy=((xx/crx)**2+((y-cY)/cry)**2)<=1
        shell[:,j,:] &= ~((zs[:,None]>=collar_z)&collar_xy)
        if frame_only and meta[j] is not None:
            base,_,_=meta[j]
            lower=zs[:,None] <= base+float(CFG['upper_lower_band_height'])
            heel=(y<=float(CFG['upper_heel_counter_length_ratio'])*L)&(zs[:,None]<=base+float(CFG['upper_heel_counter_height']))
            collar_r=np.sqrt((xx/crx)**2+((y-cY)/cry)**2)
            cuff=(np.abs(collar_r-1.0)<0.14)&(zs[:,None]>=collar_z-4)&(zs[:,None]<=collar_z+5)
            shell[:,j,:] &= (lower|heel|cuff)
    verts,faces,_,_=measure.marching_cubes(shell.astype(np.float32),level=0.5,spacing=(pitch,pitch,pitch))
    xyz=np.column_stack((verts[:,2]+xs[0],verts[:,1]+ys[0],verts[:,0]+zs[0]))
    mesh=trimesh.Trimesh(vertices=xyz,faces=faces,process=True)
    mesh.remove_unreferenced_vertices(); mesh.fix_normals(); mesh.export(out_path)
    return mesh

def mirror(src,dst):
    m=trimesh.load(src,force='mesh'); T=np.eye(4); T[0,0]=-1; m.apply_transform(T); m.invert(); m.export(dst)

if __name__=='__main__':
    items=[
      ('v6_1_upper_infill_envelope_left.stl',float(CFG['upper_infill_envelope_thickness']),False,float(CFG['upper_envelope_voxel'])),
      ('v6_1_upper_reinforcement_frame_left.stl',float(CFG['upper_frame_thickness']),True,float(CFG['upper_frame_voxel'])),
      ('v6_1_upper_fuzzy_shell_left.stl',float(CFG['upper_fuzzy_wall_thickness']),False,float(CFG['fuzzy_shell_voxel'])),
    ]
    report={}
    for name,wall,frame,pitch in items:
        print('building',name,flush=True)
        m=make_upper(HERE/name,wall,frame,pitch); mirror(HERE/name,HERE/name.replace('_left','_right'))
        report[name]={'bounds':m.bounds.tolist(),'watertight':bool(m.is_watertight),'components':len(m.split(only_watertight=False)),'faces':len(m.faces)}
    stations=[]
    for s in [0.06,0.12,0.22,0.48,0.62,0.72,0.82,0.90,0.96]:
        sv=sole_vals(s); uv=upper_vals(s); target=sv['width']-2*float(CFG['upper_lower_interface_inset'])
        stations.append({'s':s,'y_mm':s*L,'sole_width_mm':sv['width'],'upper_lower_interface_width_mm':target,'upper_dome_reference_width_mm':uv['width']})
    report['interface_stations']=stations
    env=report[items[0][0]]
    report['rules']={'upper_reaches_heel':env['bounds'][0][1]<=0.5,'upper_reaches_toe':env['bounds'][1][1]>=L-1.0,'lower_interface_derived_from_sole':True,'lower_interface_inset_each_side_mm':float(CFG['upper_lower_interface_inset'])}
    (HERE/'VALIDATION_V6_1_UPPER.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
