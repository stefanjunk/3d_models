import os, math, json
import numpy as np
import trimesh
from shapely.geometry import Polygon

OUT = os.path.dirname(__file__)
SEG = 10  # per rounded corner


def ensure_ccw(p):
    p=np.asarray(p,float)
    area=0.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
    return p if area>0 else p[::-1]


def rounded_rect_points(w,d,r,segments=SEG,x0=0.0,y0=0.0):
    r=max(0.01,min(r,w/2-0.01,d/2-0.01))
    centers=[(x0+w-r,y0+r),(x0+w-r,y0+d-r),(x0+r,y0+d-r),(x0+r,y0+r)]
    ranges=[(-90,0),(0,90),(90,180),(180,270)]
    pts=[]
    for (cx,cy),(a0,a1) in zip(centers,ranges):
        aa=np.linspace(math.radians(a0),math.radians(a1),segments,endpoint=False)
        for a in aa:
            pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return ensure_ccw(pts)

def arc_points(cx,cy,r,a0,a1,segments=SEG,endpoint=False):
    aa=np.linspace(math.radians(a0), math.radians(a1), segments, endpoint=endpoint)
    return [(cx + r*math.cos(a), cy + r*math.sin(a)) for a in aa]


def u_shell_plan_points(w,d,r,wall,back,segments=SEG):
    """Rounded outer footprint with a clean rectangular front opening.
    This matches the OpenSCAD housing geometry and keeps the drawer path free
    of extra internal corner features."""
    outer = Polygon(rounded_rect_points(w,d,r,segments=segments))
    notch = Polygon([
        (wall, 0.0),
        (w-wall, 0.0),
        (w-wall, d-back+0.2),
        (wall, d-back+0.2),
    ])
    u = outer.difference(notch).buffer(0)
    if u.geom_type != 'Polygon':
        u = max(list(u.geoms), key=lambda g: g.area)
    coords = [(float(x), float(y)) for x, y in list(u.exterior.coords)[:-1]]
    return ensure_ccw(coords)


def prism_from_polygon(poly,z0,z1):
    poly=ensure_ccw(poly)
    n=len(poly)
    verts=np.vstack([np.c_[poly,np.full(n,z0)],np.c_[poly,np.full(n,z1)]])
    faces=[]
    for i in range(1,n-1):
        faces.append([0,i+1,i]) # bottom -z
        faces.append([n,n+i,n+i+1]) # top +z
    for i in range(n):
        j=(i+1)%n
        faces += [[i,j,n+j],[i,n+j,n+i]]
    return trimesh.Trimesh(vertices=verts,faces=np.asarray(faces),process=True)


def rounded_solid(w,d,h,r,z0=0.0,x0=0.0,y0=0.0):
    return prism_from_polygon(rounded_rect_points(w,d,r,x0=x0,y0=y0),z0,z0+h)


def rounded_cup(w,d,h,wall=3.0,bottom=3.0,r=12.0,x0=0.0,y0=0.0,z0=0.0):
    outer=rounded_rect_points(w,d,r,x0=x0,y0=y0)
    iw,idd=w-2*wall,d-2*wall
    ir=max(1.0,r-wall)
    inner=rounded_rect_points(iw,idd,ir,x0=x0+wall,y0=y0+wall)
    n=len(outer)
    assert len(inner)==n
    # loops: outer bottom/top, inner bottom/top
    ob=np.c_[outer,np.full(n,z0)]
    ot=np.c_[outer,np.full(n,z0+h)]
    ib=np.c_[inner,np.full(n,z0+bottom)]
    it=np.c_[inner,np.full(n,z0+h)]
    verts=np.vstack([ob,ot,ib,it])
    O0,O1,I0,I1=0,n,2*n,3*n
    faces=[]
    # bottom exterior
    for i in range(1,n-1): faces.append([O0,O0+i+1,O0+i])
    # cavity floor
    for i in range(1,n-1): faces.append([I0,I0+i,I0+i+1])
    # outer walls
    for i in range(n):
        j=(i+1)%n
        faces += [[O0+i,O0+j,O1+j],[O0+i,O1+j,O1+i]]
    # inner walls, reverse winding
    for i in range(n):
        j=(i+1)%n
        faces += [[I0+i,I1+i,I1+j],[I0+i,I1+j,I0+j]]
    # top annulus
    for i in range(n):
        j=(i+1)%n
        faces += [[O1+i,O1+j,I1+j],[O1+i,I1+j,I1+i]]
    return trimesh.Trimesh(vertices=verts,faces=np.asarray(faces),process=True)


def rounded_annulus(w,d,h,r,thickness=0.45,expand=0.45,z0=0.0):
    # external decorative rib around an existing rounded body 0..w,0..d
    outer=rounded_rect_points(w+2*expand,d+2*expand,r+expand,x0=-expand,y0=-expand)
    inner=rounded_rect_points(w,d,r,x0=0,y0=0)
    n=len(outer)
    ob=np.c_[outer,np.full(n,z0)]; ot=np.c_[outer,np.full(n,z0+h)]
    ib=np.c_[inner,np.full(n,z0)]; it=np.c_[inner,np.full(n,z0+h)]
    verts=np.vstack([ob,ot,ib,it]); O0,O1,I0,I1=0,n,2*n,3*n
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces += [[O0+i,O0+j,O1+j],[O0+i,O1+j,O1+i]]
        faces += [[I0+i,I1+i,I1+j],[I0+i,I1+j,I0+j]]
        faces += [[O1+i,O1+j,I1+j],[O1+i,I1+j,I1+i]]
        faces += [[O0+i,I0+j,O0+j],[O0+i,I0+i,I0+j]]
    return trimesh.Trimesh(vertices=verts,faces=np.asarray(faces),process=True)


def box(x0,y0,z0,sx,sy,sz):
    m=trimesh.creation.box(extents=[sx,sy,sz])
    m.apply_translation([x0+sx/2,y0+sy/2,z0+sz/2])
    return m


def front_open_cup(w,d,h,wall=3.2,back=3.2,r=12.0):
    # local cup dims are x=width, y=height, z=depth; opening maps to world front y=0
    m=rounded_cup(w,h,d,wall=wall,bottom=back,r=r)
    v=m.vertices.copy()
    x=v[:,0].copy(); ly=v[:,1].copy(); lz=v[:,2].copy()
    v[:,0]=x
    v[:,1]=d-lz
    v[:,2]=ly
    m.vertices=v
    m.process(validate=True)
    return m


def connector_meshes(w,d,h,fit=0.35,rail_h=56.0,rail_z=12.0,p=4.0,base=8.0,head=12.0,rail_t=2.2):
    y0=d/2
    z1=min(rail_z+rail_h,h-5)
    # male dovetail on right; narrow at body, wide at outer head
    male_poly=[(w,y0-base/2),(w+p,y0-head/2),(w+p,y0+head/2),(w,y0+base/2)]
    male=prism_from_polygon(male_poly,rail_z,z1)
    # female external channel on left: empty tapered channel between two positive rails
    mouth=base+2*fit
    inner=head+2*fit
    top_poly=[(-p-0.15,y0+mouth/2),(0,y0+inner/2),(0,y0+inner/2+rail_t),(-p-0.15,y0+mouth/2+rail_t)]
    bot_poly=[(-p-0.15,y0-mouth/2-rail_t),(0,y0-inner/2-rail_t),(0,y0-inner/2),(-p-0.15,y0-mouth/2)]
    top=prism_from_polygon(top_poly,rail_z,z1)
    bot=prism_from_polygon(bot_poly,rail_z,z1)
    return [male,top,bot]


def add_connectors(meshes,w,d,h,fit=0.35,rail_h=56,rail_z=12):
    meshes.extend(connector_meshes(w,d,h,fit=fit,rail_h=rail_h,rail_z=rail_z))


def drawer_housing():
    # Built in z-layers, matching the OpenSCAD source.
    # The front remains clean: no ribs in the drawer face area.
    w=d=96.0; h=80.0; wall=3.2; back=3.2; r=15.0
    open_h=34.8; lower_z=4.2; shelf_t=3.2
    upper_z=lower_z + open_h + shelf_t
    meshes=[]

    full_plan = rounded_rect_points(w,d,r)
    open_plan = u_shell_plan_points(w,d,r,wall,back)

    meshes.append(prism_from_polygon(full_plan, 0.0, lower_z))
    meshes.append(prism_from_polygon(open_plan, lower_z, lower_z + open_h))
    meshes.append(prism_from_polygon(full_plan, lower_z + open_h, upper_z))
    meshes.append(prism_from_polygon(open_plan, upper_z, upper_z + open_h))
    meshes.append(prism_from_polygon(full_plan, upper_z + open_h, h))

    for z in (lower_z+1.2, upper_z+1.2):
        meshes.append(box(wall-0.3,7,z,1.4,d-back-10,1.5))
        meshes.append(box(w-wall-1.1,7,z,1.4,d-back-10,1.5))

    add_connectors(meshes,w,d,h)
    return trimesh.util.concatenate(meshes)


def drawer():
    # Updated together with the housing: larger visible front radii while the
    # functional body remains small enough for smooth sliding.
    body_w=88.6; body_d=91.0; body_h=32.2; body_r=10.0
    face_w=89.1; face_h=34.6; face_t=2.4; face_r=11.2
    meshes=[rounded_cup(body_w,body_d,body_h,wall=2.4,bottom=2.4,r=body_r)]
    bezel=rounded_solid(face_w,face_t,face_h,face_r,
                        x0=-(face_w-body_w)/2,y0=-face_t,z0=0.0)
    meshes.append(bezel)
    # low-profile rounded pull centered on the bezel
    handle=rounded_solid(30,5.5,6.2,2.4,x0=(body_w-30)/2,y0=-4.2,z0=9.7)
    meshes.append(handle)
    return trimesh.util.concatenate(meshes)


def cubby():
    w=d=96.0; h=80.0
    meshes=[front_open_cup(w,d,h,wall=3.2,back=3.2,r=13.0)]
    add_connectors(meshes,w,d,h)
    return trimesh.util.concatenate(meshes)


def shallow_tray():
    w=d=96.0; h=26.0; r=14.0
    meshes=[rounded_cup(w,d,h,wall=3.0,bottom=3.0,r=r)]
    add_connectors(meshes,w,d,h,rail_h=14,rail_z=6)
    # a single removable-look divider lip
    meshes.append(box(46.5,3.2,3.0,2.4,d-6.4,15.5))
    return trimesh.util.concatenate(meshes)


def divided_bin():
    w=d=96.0; h=78.0; r=15.0
    meshes=[rounded_cup(w,d,h,wall=3.0,bottom=3.0,r=r)]
    # dividers: larger rear compartment + smaller front cells
    meshes.append(box(46.7,3.0,3.0,2.6,d-6.0,57.0))
    meshes.append(box(3.0,47.0,3.0,43.7,2.6,57.0))
    meshes.append(box(49.3,58.0,3.0,43.7,2.6,57.0))
    add_connectors(meshes,w,d,h)
    # gentle horizontal rib texture
    for z in np.arange(10,61,5.5):
        meshes.append(rounded_annulus(w,d,0.75,r,expand=0.38,z0=float(z)))
    return trimesh.util.concatenate(meshes)


def pen_cup():
    w=64.0; d=96.0; h=110.0; r=17.0
    meshes=[rounded_cup(w,d,h,wall=3.0,bottom=3.0,r=r)]
    meshes.append(box(3.0,50.0,3.0,w-6.0,2.6,87.0))
    add_connectors(meshes,w,d,h,rail_h=56,rail_z=12)
    for z in np.arange(10,79,5.5):
        meshes.append(rounded_annulus(w,d,0.75,r,expand=0.38,z0=float(z)))
    return trimesh.util.concatenate(meshes)


def connector_test():
    # compact fit test: left block has male, right block has receiver
    meshes=[]
    w=24; d=34; h=30
    meshes.append(box(0,0,0,w,d,h))
    meshes += connector_meshes(w,d,h,rail_h=20,rail_z=5)
    m=trimesh.util.concatenate(meshes)
    return m

parts={
    'drawer_housing.stl': drawer_housing(),
    'drawer.stl': drawer(),
    'cubby_module.stl': cubby(),
    'shallow_tray_module.stl': shallow_tray(),
    'divided_bin_module.stl': divided_bin(),
    'pen_cup_module.stl': pen_cup(),
    'connector_fit_test.stl': connector_test(),
}

report={}
for name,m in parts.items():
    path=os.path.join(OUT,name)
    m.export(path)
    loaded=trimesh.load(path,force='mesh')
    report[name]={
        'extents_mm':[round(float(x),2) for x in loaded.extents],
        'watertight':bool(loaded.is_watertight),
        'components':len(loaded.split(only_watertight=False)),
        'faces':int(len(loaded.faces)),
        'volume_mm3':round(float(abs(loaded.volume)),1),
    }
with open(os.path.join(OUT,'validation.json'),'w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
