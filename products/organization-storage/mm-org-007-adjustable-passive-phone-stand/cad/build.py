#!/usr/bin/env python3
"""Parametric adjustable phone stand with three detent profiles."""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import cadquery as cq
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1];PARAMS=ROOT/"config/model-parameters.json";MASTER=ROOT/"exports/master";MFG=ROOT/"exports/manufacturing";COUPONS=ROOT/"exports/coupons";THREE=ROOT/"exports/3mf";REPORTS=ROOT/"reports";VALIDATION=ROOT/"validation";PID="MM-ORG-007";REV="0.1.0-draft.1"
def load_params():return json.loads(PARAMS.read_text())
def validate_parameters(p):
 b=p['base'];r=p['backrest'];h=p['hinge'];d=p['detent'];assert p['project']['id']==PID and p['project']['revision']==REV;assert b['width']<=95 and b['depth']<=110 and r['height']+2*r['barrel_radius']<=125;assert math.isclose((h['pin_diameter']+2*h['radial_clearance']-h['pin_diameter'])/2,.25,abs_tol=1e-9);assert math.isclose(b['width']-h['shaft_length']-h['head_length'],h['axial_clearance_total'],abs_tol=1e-9);assert d['view_angles']==[55.0,65.0,75.0];assert list(d['profiles'])==['soft','medium','firm'];assert r['case_capacity']>=14 and r['cable_notch']>=12
def box(x,y,z,sx,sy,sz):return cq.Solid.makeBox(sx,sy,sz,cq.Vector(x,y,z))
def rounded(l,w,h,r):return cq.Workplane('XY').rect(l,w).extrude(h).edges('|Z').fillet(r).val()
def cyl_x(radius,length,x,y,z):return cq.Solid.makeCylinder(radius,length,cq.Vector(x,y,z),cq.Vector(1,0,0))
def make_base(profile,p):
 b=p['base'];h=p['hinge'];d=p['detent'];pr=d['profiles'][profile]
 shape=rounded(b['width'],b['depth'],b['plate'],b['corner_radius']).translate(cq.Vector(0,b['depth']/2,0));shape=shape.fuse(box(-b['width']/2,b['depth']-b['rear_beam_depth'],0,b['width'],b['rear_beam_depth'],b['rear_beam_height']))
 for side in (-1,1):
  x=-b['width']/2 if side<0 else b['width']/2-b['ear_thickness'];ear=box(x,b['hinge_y']-b['ear_depth']/2,b['plate'],b['ear_thickness'],b['ear_depth'],b['ear_height']);shape=shape.fuse(ear)
  hole=cyl_x(h['pin_diameter']/2+h['radial_clearance'],b['ear_thickness']+.2,x-.1,b['hinge_y'],b['hinge_z']);shape=shape.cut(hole)
  inner_x=(-b['width']/2+b['ear_thickness']-pr['socket_depth']) if side<0 else (b['width']/2-b['ear_thickness']-.05)
  for view in d['view_angles']:
   tilt=math.radians(90-view);yy=b['hinge_y']+d['trace_radius']*math.sin(tilt);zz=b['hinge_z']+d['trace_radius']*math.cos(tilt);c=cyl_x(pr['socket_radius'],pr['socket_depth']+.1,inner_x,yy,zz);shape=shape.cut(c)
  gx=x+b['ear_thickness']/2;shape=shape.fuse(box(gx-b['gusset']/2,b['hinge_y']-b['ear_depth']/2-b['gusset'],b['plate'],b['gusset'],b['gusset'],b['ear_height']/2))
 if not shape.isValid() or len(shape.Solids())!=1:raise RuntimeError('invalid base')
 return shape
def make_backrest(p):
 r=p['backrest'];h=p['hinge'];d=p['detent'];w=r['width'];shape=box(-w/2,2,0,w,r['panel'],r['height']);window=box(-w/2+r['frame_side'],1.9,r['window_bottom'],w-2*r['frame_side'],r['panel']+.2,r['height']-r['window_bottom']-r['frame_top']);shape=shape.cut(window)
 barrel=cyl_x(r['barrel_radius'],w,-w/2,0,0);bore=cyl_x(h['pin_diameter']/2+h['radial_clearance'],w+.2,-w/2-.1,0,0);shape=shape.fuse(barrel).cut(bore)
 shelf=box(-w/2,-r['shelf_depth']+2,8,w,r['shelf_depth'],r['shelf']);lip=box(-w/2,-r['shelf_depth']+2,8,w,r['lip_depth'],r['lip_height']);shape=shape.fuse(shelf).fuse(lip);notch=box(-r['cable_notch']/2,-r['shelf_depth']+1.9,7.9,r['cable_notch'],r['shelf_depth']+.2,r['lip_height']+1);shape=shape.cut(notch)
 for side in (-1,1):
  x=-w/2-r['side_disc_thickness'] if side<0 else w/2;disc=cyl_x(r['side_disc_radius'],r['side_disc_thickness'],x,0,0);shape=shape.fuse(disc).cut(cyl_x(h['pin_diameter']/2+h['radial_clearance'],r['side_disc_thickness']+.2,x-.1,0,0));nx=x-d['nub_depth'] if side<0 else x+r['side_disc_thickness'];nub=cyl_x(d['nub_radius'],d['nub_depth'],nx,0,d['trace_radius']);shape=shape.fuse(nub)
 if not shape.isValid() or len(shape.Solids())!=1:raise RuntimeError('invalid backrest')
 return shape
def make_pin(p):
 h=p['hinge'];shaft=cyl_x(h['pin_diameter']/2,h['shaft_length'],-45.5,0,0);head=cyl_x(h['head_diameter']/2,h['head_length'],-47.5,0,0);tip=cq.Solid.makeCone(h['pin_diameter']/2,2.0,h['tip_length'],cq.Vector(46.5,0,0),cq.Vector(1,0,0));return shaft.fuse(head).fuse(tip)
def make_coupon(p):
 d=p['detent'];body=box(-32,-6,0,64,12,8)
 for x,key in zip((-20,0,20),('soft','medium','firm')):pr=d['profiles'][key];body=body.cut(cq.Solid.makeCylinder(pr['socket_radius'],pr['socket_depth']+.1,cq.Vector(x,0,8.05),cq.Vector(0,0,-1)))
 if not body.isValid():raise RuntimeError('invalid coupon')
 return body
def orient_back(shape):
 s=shape.rotate(cq.Vector(),cq.Vector(1,0,0),-90);return origin(s)
def orient_pin(shape):
 s=shape.rotate(cq.Vector(),cq.Vector(0,1,0),-90);return origin(s)
def origin(s):b=s.BoundingBox();return s.translate(cq.Vector(-b.xmin,-b.ymin,-b.zmin))
def sha(path):
 d=hashlib.sha256();f=path.open('rb')
 with f:
  for q in iter(lambda:f.read(1048576),b''):d.update(q)
 return d.hexdigest()
def export(s,path,p):path.parent.mkdir(parents=True,exist_ok=True);cq.exporters.export(s,str(path),exportType='STEP') if path.suffix=='.step' else cq.exporters.export(s,str(path),tolerance=p['export']['chordal_tolerance'],angularTolerance=p['export']['angular_tolerance'])
def metrics(path):m=trimesh.load_mesh(path,force='mesh',process=True);return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),'file_bytes':path.stat().st_size,'triangles':int(len(m.faces)),'vertices':int(len(m.vertices)),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume':bool(m.volume>0),'components':int(len(m.split(only_watertight=False))),'volume_mm3':float(m.volume),'extents_mm':np.round(m.extents,5).tolist()}
def ck(i,p,m,x=None):return {'id':i,'status':'PASS' if p else 'FAIL','required':True,'message':m,'metrics':x or {},'evidence':[]}
def rep(tool,inputs,checks,met,limits):return {'schema_version':'1.0','tool':tool,'tool_version':REV,'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','profile':'draft','inputs':[{'path':str(x.relative_to(ROOT)),'sha256':sha(x),'size_bytes':x.stat().st_size} for x in inputs],'checks':checks,'metrics':met,'limitations':limits,'required_capabilities':[]}
def wj(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def zm(z,n,d):i=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,d)
def m3(s,p):v,f=s.tessellate(p['export']['chordal_tolerance'],p['export']['angular_tolerance']);m=trimesh.Trimesh(np.asarray([[q.x,q.y,q.z] for q in v]),np.asarray(f),process=True,validate=True);m.merge_vertices();m.remove_unreferenced_vertices();assert m.is_watertight and m.volume>0;return m
def write3(path,parts,p):
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',ns);model=ET.Element(f'{{{ns}}}model',{'unit':'millimeter','xml:lang':'en-US'})
 for k,v in (('Title','DRAFT MM-ORG-007 Adjustable Passive Phone Stand'),('Designer','metriMade / autonomous CAD workflow'),('Description','Three alternative bases, one backrest and one pin; inventory strip only.'),('LicenseTerms','DRAFT engineering artifact; not a commercial release')):n=ET.SubElement(model,f'{{{ns}}}metadata',{'name':k});n.text=v
 rs=ET.SubElement(model,f'{{{ns}}}resources');bd=ET.SubElement(model,f'{{{ns}}}build');cursor=0
 for oid,(name,s) in enumerate(parts,1):
  m=m3(s,p);o=ET.SubElement(rs,f'{{{ns}}}object',{'id':str(oid),'type':'model','name':name});mn=ET.SubElement(o,f'{{{ns}}}mesh');vn=ET.SubElement(mn,f'{{{ns}}}vertices')
  for x,y,z in m.vertices:ET.SubElement(vn,f'{{{ns}}}vertex',{'x':f'{x:.6f}','y':f'{y:.6f}','z':f'{z:.6f}'})
  tn=ET.SubElement(mn,f'{{{ns}}}triangles')
  for a,b,c in m.faces:ET.SubElement(tn,f'{{{ns}}}triangle',{'v1':str(int(a)),'v2':str(int(b)),'v3':str(int(c))})
  ET.SubElement(bd,f'{{{ns}}}item',{'objectid':str(oid),'transform':f'1 0 0 0 1 0 0 0 1 {cursor:.3f} 0 0'});cursor+=s.BoundingBox().xlen+8
 types=b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>';rels=b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
 path.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:zm(z,'[Content_Types].xml',types);zm(z,'_rels/.rels',rels);zm(z,'3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True));zm(z,'Metadata/model-parameters.json',PARAMS.read_bytes())
def main():
 p=load_params();validate_parameters(p);src=Path(__file__).resolve();native={f'base_{k}':make_base(k,p) for k in p['detent']['profiles']};native['backrest']=make_backrest(p);native['pin']=make_pin(p);printed={k:(orient_back(v) if k=='backrest' else orient_pin(v) if k=='pin' else origin(v)) for k,v in native.items()};mm={}
 for k,v in native.items():export(v,MASTER/f'DRAFT-{PID}-{k}-{REV}.step',p);path=MFG/f'DRAFT-{PID}-{k}-{REV}.stl';export(printed[k],path,p);mm[k]=metrics(path)
 coupon=make_coupon(p);cp=COUPONS/f'DRAFT-{PID}-detent-coupon-{REV}.stl';export(origin(coupon),cp,p);mm['coupon']=metrics(cp);out=THREE/f'DRAFT-{PID}-adjustable-phone-stand-{REV}.3mf';write3(out,list(printed.items()),p)
 b=p['base'];view=65;tilt=-(90-view);back=native['backrest'].rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),tilt).translate(cq.Vector(0,b['hinge_y'],b['hinge_z']));pin=native['pin'].translate(cq.Vector(0,b['hinge_y'],b['hinge_z']));ass=cq.Compound.makeCompound([native['base_medium'],back,pin]);ap=MASTER/f'DRAFT-{PID}-assembly-65deg-{REV}.stl';export(origin(ass),ap,p);bb=ass.BoundingBox();ae=[bb.xlen,bb.ylen,bb.zlen]
 checks=[]
 for k,m in mm.items():checks += [ck(k+'-watertight',m['watertight'],k+' watertight'),ck(k+'-winding',m['winding_consistent'],k+' winding'),ck(k+'-volume',m['positive_volume'],k+' volume'),ck(k+'-component',m['components']==1,k+' one component')]
 mr=rep(PID+'-mesh-generation',[PARAMS,src],checks,{'meshes':mm},['Topology does not prove hinge force, cycles, pin retention, stability or device contact.']);wj(VALIDATION/'mesh-generation-report.json',mr)
 h=p['hinge'];d=p['detent'];ir=rep(PID+'-interface-validation',[PARAMS,src],[ck('radial-clearance',math.isclose(h['radial_clearance'],.25,abs_tol=1e-9),'Hinge radial clearance is 0.25 mm'),ck('axial-clearance',math.isclose(h['axial_clearance_total'],1,abs_tol=1e-9),'Total axial clearance is 1.0 mm'),ck('three-angles',len(d['view_angles'])==3,'Three viewing angles are explicit'),ck('three-profiles',len(d['profiles'])==3,'Three detent profiles are explicit'),ck('coupon',cp.is_file(),'Detent depth coupon exists')],{'angles_deg':d['view_angles'],'profiles':d['profiles'],'physical_fit':'NOT_RUN'},['Nominal CAD does not establish detent engagement or hinge friction.']);wj(VALIDATION/'interface-report.json',ir)
 sr=rep(PID+'-parametric-source',[PARAMS,src,ROOT/'design-spec.yaml',ROOT/'protected-geometry-map.md'],[ck('params',True,'Default and boundary assertions pass'),ck('parts',len(native)==5,'Three bases, backrest and pin generated'),ck('assembly-envelope',ae[0]<=95 and ae[1]<=110 and ae[2]<=125,'65 degree assembly fits envelope',{'extents_mm':ae}),ck('mesh',mr['status']=='PASS','Mesh stage passes'),ck('interface',ir['status']=='PASS','Interface stage passes'),ck('3mf',out.is_file(),'DRAFT 3MF exists')],{'assembly_65deg_extents_mm':ae,'print_set':str(out.relative_to(ROOT))},['Exact slicer and physical tests are deferred.']);wj(VALIDATION/'parametric-source-report.json',sr)
 pts=[cq.Vector(-47.5,10,5),cq.Vector(-47.5,95,5),cq.Vector(-47.5,95,20),cq.Vector(-47.5,60,118),cq.Vector(-47.5,50,118),cq.Vector(-47.5,20,20),cq.Vector(-47.5,10,5)];wire=cq.Wire.makePolygon(pts);wedge=cq.Solid.extrudeLinear(wire,[],cq.Vector(95,0,0));sel=mm['base_medium']['volume_mm3']+mm['backrest']['volume_mm3']+mm['pin']['volume_mm3'];op=rep(PID+'-optimization-comparison',[PARAMS,src,ROOT/'protected-geometry-map.md'],[ck('protected',True,'Protected map exists'),ck('volume',sel<wedge.Volume(),'Hinged frame volume is below solid wedge baseline'),ck('orientation',True,'Base/backrest/pin have explicit support-conscious orientations')],{'baseline_wedge_cad_volume_mm3':wedge.Volume(),'selected_set_cad_volume_mm3':sel,'cad_volume_reduction_percent':100*(wedge.Volume()-sel)/wedge.Volume(),'selection':'B wide plate plus windowed hinged backrest','exact_slicer_metrics':'NOT_RUN'},['CAD volume is not deposited mass or print time; stability remains physical.']);wj(REPORTS/'optimization-comparison.json',op);wj(REPORTS/'build-manifest.json',{'project_id':PID,'revision':REV,'status':'DRAFT','parts':mm,'assembly_extents_mm':ae,'print_set':str(out.relative_to(ROOT)),'print_set_sha256':sha(out),'physical_validation':'DEFERRED'})
 if any(x['status']!='PASS' for x in (mr,ir,sr,op)):raise RuntimeError('digital check failed')
 print(json.dumps({'status':'PASS','assembly_extents_mm':ae,'print_set':str(out)},indent=2))
if __name__=='__main__':main()
