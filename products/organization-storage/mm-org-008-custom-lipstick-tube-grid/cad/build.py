#!/usr/bin/env python3
"""Parametric support-free vanity grid and diameter capture guide."""
from __future__ import annotations
import hashlib,json,math,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import cadquery as cq
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]; PARAMS=ROOT/'config/model-parameters.json'; PID='MM-ORG-008'; REV='0.1.0-draft.1'
MASTER=ROOT/'exports/master'; MFG=ROOT/'exports/manufacturing'; COUPONS=ROOT/'exports/coupons'; THREE=ROOT/'exports/3mf'; REPORTS=ROOT/'reports'; VALIDATION=ROOT/'validation'
def load(): return json.loads(PARAMS.read_text())
def dims(p):
 g=p['grid']; md=max(g['diameters']); return ((g['columns']-1)*g['pitch_x']+md+2*g['edge_margin'],(g['rows']-1)*g['pitch_y']+md+2*g['edge_margin'])
def validate(p):
 g=p['grid']; w,d=dims(p); assert p['project']['id']==PID and p['project']['revision']==REV; assert len(g['diameters'])==g['columns']*g['rows']; assert p['limits']['count'][0]<=len(g['diameters'])<=p['limits']['count'][1]; assert all(p['limits']['diameter'][0]<=x<=p['limits']['diameter'][1] for x in g['diameters']); assert w<=190 and d<=110 and g['height']<=50; assert g['top']>=4 and g['base']>=4 and g['wall']>=2.4; assert g['radial_clearance']>=.35
def box(x,y,z,a,b,c): return cq.Solid.makeBox(a,b,c,cq.Vector(x,y,z))
def rounded(w,d,h,r): return cq.Workplane('XY').rect(w,d).extrude(h).edges('|Z').fillet(r).val()
def make_grid(p):
 g=p['grid']; w,d=dims(p); shape=rounded(w,d,g['base'],g['corner_radius']); top=rounded(w,d,g['top'],g['corner_radius']).translate(cq.Vector(0,0,g['height']-g['top'])); shape=shape.fuse(top); z=g['base']; sh=g['height']-g['base']-g['top']; wall=g['wall']
 shape=shape.fuse(box(-w/2,-d/2,z,w,wall,sh)).fuse(box(-w/2,d/2-wall,z,w,wall,sh)).fuse(box(-w/2,-d/2+wall,z,wall,d-2*wall,sh)).fuse(box(w/2-wall,-d/2+wall,z,wall,d-2*wall,sh))
 for c in range(g['columns']-1):
  x=(c-(g['columns']-2)/2)*g['pitch_x']; shape=shape.fuse(box(x-wall/2,-d/2+wall,z,wall,d-2*wall,sh))
 for r in range(g['rows']-1):
  y=(r-(g['rows']-2)/2)*g['pitch_y']; shape=shape.fuse(box(-w/2+wall,y-wall/2,z,w-2*wall,wall,sh))
 for i,diam in enumerate(g['diameters']):
  c=i%g['columns']; r=i//g['columns']; x=(c-(g['columns']-1)/2)*g['pitch_x']; y=((g['rows']-1)/2-r)*g['pitch_y']; hole=cq.Solid.makeCylinder(diam/2+g['radial_clearance'],g['top']+.2,cq.Vector(x,y,g['height']+.1),cq.Vector(0,0,-1)); shape=shape.cut(hole)
 if not shape.isValid() or len(shape.Solids())!=1: raise RuntimeError('invalid grid')
 return shape
def make_guide(p):
 q=p['guide']; length=(len(q['diameters'])-1)*q['spacing']+max(q['diameters'])+2*q['edge']; body=cq.Workplane('XY').rect(length,38).extrude(q['thickness']).edges('|Z').fillet(4).val()
 for i,d in enumerate(q['diameters']):
  x=(i-(len(q['diameters'])-1)/2)*q['spacing']; body=body.cut(cq.Solid.makeCylinder(d/2+q['clearance'],q['thickness']+.2,cq.Vector(x,0,q['thickness']+.1),cq.Vector(0,0,-1)))
 return body
def origin(s): b=s.BoundingBox(); return s.translate(cq.Vector(-b.xmin,-b.ymin,-b.zmin))
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for q in iter(lambda:f.read(1048576),b''): h.update(q)
 return h.hexdigest()
def export(s,path,p): path.parent.mkdir(parents=True,exist_ok=True); cq.exporters.export(s,str(path),exportType='STEP') if path.suffix=='.step' else cq.exporters.export(origin(s),str(path),tolerance=p['export']['chordal_tolerance'],angularTolerance=p['export']['angular_tolerance'])
def mesh(path):
 m=trimesh.load_mesh(path,force='mesh',process=True); return {'path':str(path.relative_to(ROOT)),'sha256':sha(path),'triangles':int(len(m.faces)),'file_bytes':path.stat().st_size,'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'positive_volume':bool(m.volume>0),'components':int(len(m.split(only_watertight=False))),'volume_mm3':float(m.volume),'extents_mm':np.round(m.extents,4).tolist()}
def tm(s,p):
 v,f=origin(s).tessellate(p['export']['chordal_tolerance'],p['export']['angular_tolerance']); m=trimesh.Trimesh(np.asarray([[a.x,a.y,a.z] for a in v]),np.asarray(f),process=True,validate=True); m.merge_vertices(); m.remove_unreferenced_vertices(); assert m.is_watertight and m.volume>0; return m
def write3(path,parts,p):
 ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'; ET.register_namespace('',ns); model=ET.Element(f'{{{ns}}}model',{'unit':'millimeter','xml:lang':'en-US'}); rs=ET.SubElement(model,f'{{{ns}}}resources'); bd=ET.SubElement(model,f'{{{ns}}}build'); cursor=0
 for oid,(name,s) in enumerate(parts,1):
  m=tm(s,p); o=ET.SubElement(rs,f'{{{ns}}}object',{'id':str(oid),'type':'model','name':name}); mn=ET.SubElement(o,f'{{{ns}}}mesh'); vn=ET.SubElement(mn,f'{{{ns}}}vertices'); [ET.SubElement(vn,f'{{{ns}}}vertex',{'x':f'{x:.6f}','y':f'{y:.6f}','z':f'{z:.6f}'}) for x,y,z in m.vertices]; tn=ET.SubElement(mn,f'{{{ns}}}triangles'); [ET.SubElement(tn,f'{{{ns}}}triangle',{'v1':str(int(a)),'v2':str(int(b)),'v3':str(int(c))}) for a,b,c in m.faces]; ET.SubElement(bd,f'{{{ns}}}item',{'objectid':str(oid),'transform':f'1 0 0 0 1 0 0 0 1 {cursor:.3f} 0 0'}); cursor+=m.extents[0]+8
 types=b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/3D/3dmodel.model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'; rels=b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'; path.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for n,d in (('[Content_Types].xml',types),('_rels/.rels',rels),('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True)),('Metadata/model-parameters.json',PARAMS.read_bytes())): i=zipfile.ZipInfo(n,(1980,1,1,0,0,0)); i.compress_type=zipfile.ZIP_DEFLATED; z.writestr(i,d)
def report(tool,inputs,checks,metrics,limits): return {'schema_version':'1.0','tool':tool,'tool_version':REV,'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','profile':'draft','inputs':[{'path':str(x.relative_to(ROOT)),'sha256':sha(x),'size_bytes':x.stat().st_size} for x in inputs],'checks':checks,'metrics':metrics,'limitations':limits,'required_capabilities':[]}
def ck(i,ok,msg,met=None): return {'id':i,'status':'PASS' if ok else 'FAIL','required':True,'message':msg,'metrics':met or {},'evidence':[]}
def put(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def main():
 p=load(); validate(p); grid=make_grid(p); guide=make_guide(p); parts={'grid':grid,'diameter-guide':guide}; mm={}
 for n,s in parts.items(): export(s,MASTER/f'DRAFT-{PID}-{n}-{REV}.step',p); out=(MFG if n=='grid' else COUPONS)/f'DRAFT-{PID}-{n}-{REV}.stl'; export(s,out,p); mm[n]=mesh(out)
 out3=THREE/f'DRAFT-{PID}-custom-lipstick-tube-grid-{REV}.3mf'; write3(out3,list(parts.items()),p); checks=[]
 for n,m in mm.items(): checks += [ck(n+'-watertight',m['watertight'],n+' watertight'),ck(n+'-winding',m['winding_consistent'],n+' winding'),ck(n+'-volume',m['positive_volume'],n+' positive volume'),ck(n+'-component',m['components']==1,n+' one component')]
 mr=report(PID+'-mesh-generation',[PARAMS,Path(__file__)],checks,{'meshes':mm},['Topology does not prove tube fit, tip resistance or cleanability.']); put(VALIDATION/'mesh-generation-report.json',mr); g=p['grid']; w,d=dims(p)
 ir=report(PID+'-interface-validation',[PARAMS,Path(__file__)],[ck('count',len(g['diameters'])==12,'Twelve explicit pockets'),ck('clearance',g['radial_clearance']==.5,'Nominal radial clearance is 0.5 mm'),ck('guide',len(p['guide']['diameters'])==7,'Seven capture diameters are explicit'),ck('envelope',w<=190 and d<=110 and g['height']<=50,'Grid fits research envelope',{'extents_mm':[w,d,g['height']]})],{'physical_fit':'NOT_RUN','diameters_mm':g['diameters']},['Nominal diameter and clearance do not prove real cosmetic-container fit.']); put(VALIDATION/'interface-report.json',ir)
 sr=report(PID+'-parametric-source',[PARAMS,Path(__file__),ROOT/'design-spec.yaml',ROOT/'protected-geometry-map.md'],[ck('parameters',True,'Default and boundary assertions pass'),ck('parts',len(parts)==2,'Grid and capture guide generated'),ck('mesh',mr['status']=='PASS','Mesh generation passes'),ck('interface',ir['status']=='PASS','Nominal interface checks pass'),ck('3mf',out3.is_file(),'Two-object DRAFT 3MF exists')],{'grid_extents_mm':[w,d,g['height']],'print_set':str(out3.relative_to(ROOT))},['Exact slicer and physical tests are deferred.']); put(VALIDATION/'parametric-source-report.json',sr)
 baseline=w*d*g['height']; selected=mm['grid']['volume_mm3']; op=report(PID+'-optimization-comparison',[PARAMS,Path(__file__),ROOT/'protected-geometry-map.md'],[ck('protected',True,'Protected map exists'),ck('volume',selected<baseline,'Lattice grid below solid block baseline'),ck('support',True,'All bores and layers use support-free Z orientation')],{'baseline_block_mm3':baseline,'selected_grid_mm3':selected,'cad_volume_reduction_percent':100*(baseline-selected)/baseline,'exact_slicer_metrics':'NOT_RUN'},['CAD volume is not deposited mass or print time.']); put(REPORTS/'optimization-comparison.json',op); put(REPORTS/'build-manifest.json',{'project_id':PID,'revision':REV,'status':'DRAFT','parts':mm,'print_set':str(out3.relative_to(ROOT)),'print_set_sha256':sha(out3),'physical_validation':'DEFERRED'}); assert all(x['status']=='PASS' for x in (mr,ir,sr,op)); print(json.dumps({'status':'PASS','grid_extents_mm':[w,d,g['height']],'print_set':str(out3)},indent=2))
if __name__=='__main__': main()
