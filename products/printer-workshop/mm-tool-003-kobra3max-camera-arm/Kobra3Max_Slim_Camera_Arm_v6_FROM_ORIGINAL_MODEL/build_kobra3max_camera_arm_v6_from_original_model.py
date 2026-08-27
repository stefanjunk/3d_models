from pathlib import Path
import math, json, zipfile
import numpy as np
import trimesh
from shapely.geometry import Point, box
from shapely.ops import unary_union, triangulate

OUT = Path('/mnt/data/k3m_camera_arm_v6_from_original_model')
OUT.mkdir(exist_ok=True)

# ============================================================================
# Kobra 3 Max slim articulated camera arm — v6
# Original geometry. Camera housing rebuilt from dimensions measured off the
# original two-part camera housing model (not from a product photo).
# ============================================================================

# --- printer-side functional interface ---
IFACE_BOSS_D = 19.90
IFACE_BOSS_DEPTH = 10.0
IFACE_PIN_LEN = 4.1
IFACE_PIN_Y = -2.52
IFACE_PIN_Z = -4.19
IFACE_PIN_W_Y = 8.25
IFACE_PIN_H_Z = 2.55
IFACE_SCREW_Y = +3.62
IFACE_SCREW_Z = -3.77
IFACE_SCREW_PILOT_D = 1.80

# --- arm / hinge geometry ---
ARM_CC = 150.0
ARM_H = 12.0
ARM_T = 6.0
HINGE_R = 9.0
HINGE_HOLE_D = 4.35
FORK_GAP = 6.65
EAR_T = 2.8
FORK_Y = FORK_GAP/2 + EAR_T/2
BASE_HINGE_X = -27.0
NECK_H = 12.0

# --- ball joint ---
BALL_D = 11.0
BALL_R = BALL_D/2
BALL_STEM_D = 5.0
BALL_STEM_LEN = 6.0
SOCKET_CLEAR = 0.28
SOCKET_INNER_R = BALL_R + SOCKET_CLEAR
SOCKET_OUTER_R = 8.0
SOCKET_THETA_MIN = math.radians(42.0)
SOCKET_THETA_MAX = math.radians(162.0)
SOCKET_GAP = math.radians(62.0)
SOCKET_CENTER_X = -(ARM_CC + 8.0)

# --- camera housing dimensions derived from the original model ---
# Measured from the original front and rear housing meshes:
#   outer housing front part extents: 40.71 x 23.42 x 18.63 mm
#   useful inner PCB cavity:          32.60 x 15.17 mm
#   lens opening:                     ~14.95 mm
#   LED openings:                     ~5.35 mm
#   LED center spacing:               ~5.92 mm (vertical pair)
#   horizontal offset lens->LED axis: ~15.12 mm
# These values are used as functional dimensions only. The new housing shape is
# independently modeled and not a mesh copy of the original.
CAM_FACE_W = 40.71     # horizontal width across the camera front
CAM_FACE_H = 18.63     # vertical height across the camera front
CAM_CAV_W = 32.60
CAM_CAV_H = 15.17
CAM_DEPTH_FRONT = 10.4
CAM_DEPTH_COVER = 2.4
WALL = 2.0
LIP_D = 3.0
LIP_CLEAR = 0.25
LIP_FRAME = 2.0
CORNER_R = 3.2

# optical layout on the front face (profile coordinates map to Y-horizontal, Z-vertical)
LENS_CY = +5.50
LENS_CZ = 0.0
LENS_AP_D = 15.25
LED_AXIS_Y = -9.62
LED_DZ = 2.96
LED_AP_D = 5.65

# cable and venting
CABLE_NOTCH_W = 10.0
CABLE_NOTCH_H = 4.0
VENT_W = 7.5
VENT_H = 1.7

# compression pads in the rear cover
PAD_T = 0.8
PAD_W = 3.8
PAD_H = 3.8

# housing positions relative to ball center
COVER_OUTER_X = -BALL_STEM_LEN
COVER_INNER_X = COVER_OUTER_X - CAM_DEPTH_COVER
SHELL_BACK_X = COVER_INNER_X
SHELL_FRONT_X = SHELL_BACK_X - CAM_DEPTH_FRONT
LIP_FRONT_X = COVER_INNER_X - LIP_D

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def cleanup(mesh):
    mesh = mesh.copy()
    try:
        mesh.merge_vertices()
        mesh.update_faces(mesh.unique_faces())
        mesh.update_faces(mesh.nondegenerate_faces())
    except Exception:
        pass
    mesh.remove_unreferenced_vertices()
    try:
        trimesh.repair.fix_normals(mesh)
    except Exception:
        pass
    return mesh


def rounded_rect(w, h, r):
    r = min(r, w/2 - 0.1, h/2 - 0.1)
    return box(-w/2 + r, -h/2 + r, w/2 - r, h/2 - r).buffer(r, resolution=48)


def extrude_polygon_y(poly, thickness, y_center=0.0):
    y0, y1 = y_center-thickness/2, y_center+thickness/2
    vertices, faces = [], []
    for tri in triangulate(poly):
        if not poly.covers(tri.representative_point()):
            continue
        c = np.asarray(tri.exterior.coords, float)[:3, :2]  # X,Z
        lo = np.column_stack((c[:,0], np.full(3, y0), c[:,1]))
        hi = np.column_stack((c[:,0], np.full(3, y1), c[:,1]))
        b = len(vertices); vertices.extend(lo.tolist()); faces.append([b,b+2,b+1])
        b = len(vertices); vertices.extend(hi.tolist()); faces.append([b,b+1,b+2])
    def side(coords, hole=False):
        c = np.asarray(coords, float)
        if np.allclose(c[0], c[-1]): c = c[:-1]
        for i in range(len(c)):
            a, d = c[i], c[(i+1)%len(c)]
            pts = [[a[0],y0,a[1]],[d[0],y0,d[1]],[d[0],y1,d[1]],[a[0],y1,a[1]]]
            b = len(vertices); vertices.extend(pts)
            faces.extend(([[b,b+1,b+2],[b,b+2,b+3]] if not hole else [[b,b+2,b+1],[b,b+3,b+2]]))
    side(poly.exterior.coords, False)
    for ring in poly.interiors: side(ring.coords, True)
    return cleanup(trimesh.Trimesh(np.asarray(vertices), np.asarray(faces), process=True))


def extrude_polygon_x(poly, thickness, x_center=0.0):
    x0, x1 = x_center-thickness/2, x_center+thickness/2
    vertices, faces = [], []
    for tri in triangulate(poly):
        if not poly.covers(tri.representative_point()):
            continue
        c = np.asarray(tri.exterior.coords, float)[:3, :2]  # Y,Z
        lo = np.column_stack((np.full(3, x0), c[:,0], c[:,1]))
        hi = np.column_stack((np.full(3, x1), c[:,0], c[:,1]))
        b = len(vertices); vertices.extend(lo.tolist()); faces.append([b,b+1,b+2])
        b = len(vertices); vertices.extend(hi.tolist()); faces.append([b,b+2,b+1])
    def side(coords, hole=False):
        c = np.asarray(coords, float)
        if np.allclose(c[0], c[-1]): c = c[:-1]
        for i in range(len(c)):
            a, d = c[i], c[(i+1)%len(c)]
            pts = [[x0,a[0],a[1]],[x1,a[0],a[1]],[x1,d[0],d[1]],[x0,d[0],d[1]]]
            b = len(vertices); vertices.extend(pts)
            faces.extend(([[b,b+1,b+2],[b,b+2,b+3]] if not hole else [[b,b+2,b+1],[b,b+3,b+2]]))
    side(poly.exterior.coords, False)
    for ring in poly.interiors: side(ring.coords, True)
    return cleanup(trimesh.Trimesh(np.asarray(vertices), np.asarray(faces), process=True))


def box_mesh(extents, center):
    m = trimesh.creation.box(extents=extents)
    m.apply_translation(center)
    return cleanup(m)


def arm_profile(start_x, end_x, zc=0.0, include_start_eye=True):
    lo=min(start_x,end_x); hi=max(start_x,end_x)
    p=box(lo, zc-ARM_H/2, hi, zc+ARM_H/2)
    if include_start_eye:
        p=unary_union([p, Point(start_x, zc).buffer(HINGE_R, resolution=64)])
        p=p.difference(Point(start_x, zc).buffer(HINGE_HOLE_D/2, resolution=48))
    return p


def fork_ear_profile(cx, zc, neck_from_x, neck_to_x):
    p=unary_union([
        Point(cx, zc).buffer(HINGE_R, resolution=64),
        box(min(neck_from_x, neck_to_x), zc-ARM_H/2, max(neck_from_x, neck_to_x), zc+ARM_H/2)
    ])
    return p.difference(Point(cx, zc).buffer(HINGE_HOLE_D/2, resolution=48))

# ---------------------------------------------------------------------------
# arm parts
# ---------------------------------------------------------------------------
def make_printer_mount_hinge():
    boss2d=Point(0,0).buffer(IFACE_BOSS_D/2,resolution=96).difference(Point(IFACE_SCREW_Y,IFACE_SCREW_Z).buffer(IFACE_SCREW_PILOT_D/2,resolution=48))
    boss=extrude_polygon_x(boss2d,IFACE_BOSS_DEPTH,x_center=-IFACE_BOSS_DEPTH/2)
    tongue=box_mesh([IFACE_PIN_LEN,IFACE_PIN_W_Y,IFACE_PIN_H_Z],[IFACE_PIN_LEN/2,IFACE_PIN_Y,IFACE_PIN_Z])
    neck_x0=-IFACE_BOSS_DEPTH;neck_x1=BASE_HINGE_X+HINGE_R-1.5
    neck=box_mesh([abs(neck_x1-neck_x0),ARM_T,NECK_H],[(neck_x0+neck_x1)/2,0,0])
    eprof=fork_ear_profile(BASE_HINGE_X,0,neck_x1-2,BASE_HINGE_X)
    ep=extrude_polygon_y(eprof,EAR_T,+FORK_Y); en=extrude_polygon_y(eprof,EAR_T,-FORK_Y)
    bx0=min(neck_x1-5,BASE_HINGE_X+2); bx1=max(neck_x1-5,BASE_HINGE_X+2)
    bw=max(0.8,FORK_Y-ARM_T/2+EAR_T/2)
    bp=box_mesh([bx1-bx0,bw,ARM_H],[(bx0+bx1)/2,(ARM_T/2+FORK_Y)/2,0]); bn=bp.copy(); bn.apply_translation([0,-(ARM_T/2+FORK_Y),0])
    return cleanup(trimesh.util.concatenate([boss,tongue,neck,ep,en,bp,bn]))


def make_arm1():
    end=-ARM_CC; body_end=end+HINGE_R-1.5
    main=extrude_polygon_y(arm_profile(0,body_end,0,True),ARM_T,0)
    fprof=fork_ear_profile(end,0,end+28,end)
    ep=extrude_polygon_y(fprof,EAR_T,+FORK_Y); en=extrude_polygon_y(fprof,EAR_T,-FORK_Y)
    bx0=end+18; bx1=body_end; bw=max(0.8,FORK_Y-ARM_T/2+EAR_T/2)
    bp=box_mesh([abs(bx1-bx0),bw,ARM_H],[(bx0+bx1)/2,(ARM_T/2+FORK_Y)/2,0]); bn=bp.copy(); bn.apply_translation([0,-(ARM_T/2+FORK_Y),0])
    return cleanup(trimesh.util.concatenate([main,ep,en,bp,bn]))


def spherical_c_socket(center=(0,0,0), axis_sign=-1, ri=SOCKET_INNER_R, ro=SOCKET_OUTER_R,
                       th0=SOCKET_THETA_MIN, th1=SOCKET_THETA_MAX, gap=SOCKET_GAP, n_th=30, n_phi=70):
    gc=math.pi/2; phis=np.linspace(gc+gap/2, gc+2*math.pi-gap/2, n_phi); ths=np.linspace(th0, th1, n_th)
    verts=[]
    for r in [ro,ri]:
        for th in ths:
            for ph in phis:
                verts.append([axis_sign*r*math.cos(th)+center[0], r*math.sin(th)*math.cos(ph)+center[1], r*math.sin(th)*math.sin(ph)+center[2]])
    verts=np.asarray(verts,float); faces=[]; layer=n_th*n_phi
    for li in [0,1]:
        off=li*layer
        for i in range(n_th-1):
            for j in range(n_phi-1):
                a=off+i*n_phi+j; b=a+1; c=off+(i+1)*n_phi+j+1; d=off+(i+1)*n_phi+j
                faces.extend([[a,b,c],[a,c,d]] if li==0 else [[a,c,b],[a,d,c]])
    for i in [0,n_th-1]:
        for j in range(n_phi-1):
            ao=i*n_phi+j; bo=ao+1; ai=layer+ao; bi=layer+bo
            faces.extend([[ao,ai,bi],[ao,bi,bo]] if i==0 else [[ao,bo,bi],[ao,bi,ai]])
    for j in [0,n_phi-1]:
        for i in range(n_th-1):
            ao=i*n_phi+j; bo=(i+1)*n_phi+j; ai=layer+ao; bi=layer+bo
            faces.extend([[ao,bo,bi],[ao,bi,ai]] if j==0 else [[ao,ai,bi],[ao,bi,bo]])
    return cleanup(trimesh.Trimesh(verts, np.asarray(faces), process=True))


def make_arm2():
    body_end=-ARM_CC
    main=extrude_polygon_y(arm_profile(0,body_end,0,True),ARM_T,0)
    neck=box_mesh([10,ARM_T,ARM_H],[-ARM_CC-4,0,0])
    sock=spherical_c_socket(center=(SOCKET_CENTER_X,0,0), axis_sign=-1)
    return cleanup(trimesh.util.concatenate([main,neck,sock]))

# ---------------------------------------------------------------------------
# new camera housing from original model dimensions
# ---------------------------------------------------------------------------
def front_profile():
    prof = rounded_rect(CAM_FACE_W, CAM_FACE_H, CORNER_R)
    prof = prof.difference(Point(LENS_CY, LENS_CZ).buffer(LENS_AP_D/2, resolution=64))
    prof = prof.difference(Point(LED_AXIS_Y, +LED_DZ).buffer(LED_AP_D/2, resolution=48))
    prof = prof.difference(Point(LED_AXIS_Y, -LED_DZ).buffer(LED_AP_D/2, resolution=48))
    return prof


def make_camera_front_shell():
    front = extrude_polygon_x(front_profile(), WALL, x_center=SHELL_FRONT_X + WALL/2)
    outer = rounded_rect(CAM_FACE_W, CAM_FACE_H, CORNER_R)
    inner = box(-CAM_CAV_W/2, -CAM_CAV_H/2, CAM_CAV_W/2, CAM_CAV_H/2)
    wall_profile = outer.difference(inner)
    wall_len = CAM_DEPTH_FRONT - WALL
    walls = extrude_polygon_x(wall_profile, wall_len, x_center=SHELL_FRONT_X + WALL + wall_len/2)

    # support ledges and tiny bottom shelf to hold the bare PCB
    ledge_x = SHELL_FRONT_X + WALL + 0.8
    ledge_len = 1.6
    ledge_h = CAM_CAV_H - 2.2
    ledge_y = CAM_CAV_W/2 + 0.55
    ledge1 = box_mesh([ledge_len, 1.1, ledge_h], [ledge_x, -ledge_y, 0])
    ledge2 = ledge1.copy(); ledge2.apply_translation([0, 2*ledge_y, 0])
    shelf = box_mesh([1.6, CAM_CAV_W + 0.8, 1.0], [ledge_x, 0, -CAM_CAV_H/2 - 0.55])
    return cleanup(trimesh.util.concatenate([front, walls, ledge1, ledge2, shelf]))


def make_camera_back_cover_ball():
    outer = rounded_rect(CAM_FACE_W, CAM_FACE_H, CORNER_R)
    cable = box(-CABLE_NOTCH_W/2, -CAM_FACE_H/2 - 0.2, CABLE_NOTCH_W/2, -CAM_FACE_H/2 + CABLE_NOTCH_H)
    vent1 = box(-VENT_W/2, 2.4-VENT_H/2, VENT_W/2, 2.4+VENT_H/2)
    vent2 = box(-VENT_W/2, -2.4-VENT_H/2, VENT_W/2, -2.4+VENT_H/2)
    plate_prof = outer.difference(cable).difference(vent1).difference(vent2)
    plate = extrude_polygon_x(plate_prof, CAM_DEPTH_COVER, x_center=(COVER_OUTER_X + COVER_INNER_X)/2)

    lip_outer_w = CAM_FACE_W - 2*WALL - 2*LIP_CLEAR
    lip_outer_h = CAM_FACE_H - 2*WALL - 2*LIP_CLEAR
    lip_inner_w = lip_outer_w - 2*LIP_FRAME
    lip_inner_h = lip_outer_h - 2*LIP_FRAME
    lip_outer = rounded_rect(lip_outer_w, lip_outer_h, max(0.8, CORNER_R-1.0))
    lip_inner = box(-lip_inner_w/2, -lip_inner_h/2, lip_inner_w/2, lip_inner_h/2)
    lip_profile = lip_outer.difference(lip_inner).difference(box(-CABLE_NOTCH_W/2, -lip_outer_h/2 - 0.2, CABLE_NOTCH_W/2, -lip_outer_h/2 + CABLE_NOTCH_H))
    lip = extrude_polygon_x(lip_profile, LIP_D, x_center=(LIP_FRONT_X + COVER_INNER_X)/2)

    ball = trimesh.creation.icosphere(subdivisions=4, radius=BALL_R)
    stem = trimesh.creation.cylinder(radius=BALL_STEM_D/2, height=BALL_STEM_LEN, sections=64)
    stem.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,1,0]))
    stem.apply_translation([-BALL_STEM_LEN/2,0,0])

    # four gentle pads to press the PCB to the front ledges
    px = LIP_FRONT_X + 0.7 + PAD_T/2
    pad_offsets = [(-CAM_CAV_W/2+2.4, +CAM_CAV_H/2-3.0), (+CAM_CAV_W/2-2.4, +CAM_CAV_H/2-3.0),
                   (-CAM_CAV_W/2+2.4, -CAM_CAV_H/2+3.0), (+CAM_CAV_W/2-2.4, -CAM_CAV_H/2+3.0)]
    pads = [box_mesh([PAD_T, PAD_W, PAD_H], [px, yy, zz]) for yy,zz in pad_offsets]
    return cleanup(trimesh.util.concatenate([plate, lip, ball, stem] + pads))


def make_camera_fit_test():
    test_depth = 3.2
    front = extrude_polygon_x(front_profile(), WALL, x_center=WALL/2)
    outer = rounded_rect(CAM_FACE_W, CAM_FACE_H, CORNER_R)
    inner = box(-CAM_CAV_W/2, -CAM_CAV_H/2, CAM_CAV_W/2, CAM_CAV_H/2)
    walls = extrude_polygon_x(outer.difference(inner), test_depth-WALL, x_center=WALL + (test_depth-WALL)/2)
    return cleanup(trimesh.util.concatenate([front, walls]))


def make_washer():
    ring = Point(0,0).buffer(4.0, resolution=64).difference(Point(0,0).buffer(HINGE_HOLE_D/2, resolution=48))
    return extrude_polygon_y(ring, 0.8, 0)


def make_interface_coupon():
    boss2d=Point(0,0).buffer(IFACE_BOSS_D/2,resolution=96).difference(Point(IFACE_SCREW_Y,IFACE_SCREW_Z).buffer(IFACE_SCREW_PILOT_D/2,resolution=48))
    boss=extrude_polygon_x(boss2d,IFACE_BOSS_DEPTH,x_center=-IFACE_BOSS_DEPTH/2)
    tongue=box_mesh([IFACE_PIN_LEN,IFACE_PIN_W_Y,IFACE_PIN_H_Z],[IFACE_PIN_LEN/2,IFACE_PIN_Y,IFACE_PIN_Z])
    handle=box_mesh([15,8,8],[-IFACE_BOSS_DEPTH-7.5,0,0])
    return cleanup(trimesh.util.concatenate([boss,tongue,handle]))

parts = {
    '01_printer_interface_FIRST_hinge.stl': make_printer_mount_hinge(),
    '02_arm1_150mm_eye_to_SECOND_fork.stl': make_arm1(),
    '03_arm2_150mm_eye_with_ball_socket.stl': make_arm2(),
    '04_anycubic_camera_front_shell_FROM_ORIGINAL_MODEL.stl': make_camera_front_shell(),
    '05_anycubic_camera_back_cover_with_ball_FROM_ORIGINAL_MODEL.stl': make_camera_back_cover_ball(),
    '06_anycubic_camera_fit_test_frame_FROM_ORIGINAL_MODEL.stl': make_camera_fit_test(),
    '07_M4_friction_washer_0p8mm.stl': make_washer(),
    '08_printer_interface_fit_test_coupon.stl': make_interface_coupon(),
}
for name, mesh in parts.items():
    mesh.export(OUT/name)

# print plate arrangement
plate = trimesh.Scene()
placements = {'01':(-125,-100),'02':(35,-92),'03':(35,20),'04':(-105,18),'05':(-105,78),'06':(-65,80),'07':(-25,85),'08':(-85,-30)}
for name, mesh0 in parts.items():
    key = name[:2]
    m = mesh0.copy()
    if key in ['01','02','03','07']:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]))
    else:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,1,0]))
    m.apply_translation([0,0,-m.bounds[0][2]])
    dx,dy = placements.get(key,(0,0)); m.apply_translation([dx,dy,0])
    plate.add_geometry(m, geom_name=name)
plate.export(OUT/'K3M_camera_arm_v6_from_original_model_printplate.3mf')

# housing assembly preview geometry
hous = trimesh.Scene()
hous.add_geometry(parts['04_anycubic_camera_front_shell_FROM_ORIGINAL_MODEL.stl'], geom_name='front_shell')
hous.add_geometry(parts['05_anycubic_camera_back_cover_with_ball_FROM_ORIGINAL_MODEL.stl'], geom_name='back_cover_ball')
hous.export(OUT/'camera_housing_assembly.3mf')

manifest = {
    'design':'Kobra 3 Max slim articulated camera arm v6 - camera housing rebuilt from original model dimensions',
    'geometry_origin':'All printable geometry generated parametrically. No third-party/official camera bracket mesh imported into the new printable parts.',
    'camera_dimension_source':'Functional dimensions measured from the original camera housing model meshes (front shell/back cover views and sections).',
    'measured_reference_mm':{
        'front_shell_outer':[40.71,23.42,18.63],
        'pcb_cavity':[32.60,15.17],
        'lens_opening_d':14.95,
        'led_opening_d_1':5.37,
        'led_opening_d_2':5.35,
        'led_center_spacing':5.92,
        'lens_to_led_axis_offset':15.12,
        'lens_center_face_yz':[LENS_CY,LENS_CZ],
        'led_axis_face_y':LED_AXIS_Y,
        'led_centers_face_z':[-LED_DZ,+LED_DZ]
    },
    'new_housing_outer_mm':[CAM_DEPTH_FRONT + CAM_DEPTH_COVER, CAM_FACE_W, CAM_FACE_H],
    'new_housing_cavity_mm':[CAM_CAV_W, CAM_CAV_H],
    'ball_d_mm':BALL_D,
    'arm_lift_mm':2*ARM_CC
}
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

README = f'''# Kobra 3 Max articulated camera arm — v6 from original camera-model dimensions

This revision rebuilds the camera enclosure using **dimensions measured from the original two-part camera housing model**, instead of estimating the camera from a product photo.

## What changed from v5

The camera housing is now based on these measured functional dimensions from the original model:

- front-shell outer extents: **40.71 × 23.42 × 18.63 mm**
- useful PCB cavity: **32.60 × 15.17 mm**
- lens opening: **≈ Ø 14.95 mm**
- LED openings: **≈ Ø 5.35 mm**
- LED center spacing: **≈ 5.92 mm**
- lens-axis to LED-axis horizontal offset: **≈ 15.12 mm**

The new printable housing is still an **independent reconstruction**, not a mesh copy.

## Files

- `04_anycubic_camera_front_shell_FROM_ORIGINAL_MODEL.stl`
- `05_anycubic_camera_back_cover_with_ball_FROM_ORIGINAL_MODEL.stl`
- `06_anycubic_camera_fit_test_frame_FROM_ORIGINAL_MODEL.stl`

The arm kinematics remain:

`printer mount -> hinge 1 -> 150 mm arm -> hinge 2 -> 150 mm arm -> ball socket -> rear-cover ball -> two-part camera housing`

## Housing concept

- **front shell** with separate lens and LED openings
- **rear cover** with integrated ball on the back side
- friction-fit inner lip
- cable notch at the bottom
- small vent slots
- gentle internal compression pads
- front-shell PCB support ledges

## Recommended test order

1. print `08_printer_interface_fit_test_coupon.stl`
2. print `06_anycubic_camera_fit_test_frame_FROM_ORIGINAL_MODEL.stl`
3. check the camera fit and opening alignment
4. print `04...front_shell...` and `05...back_cover...`
5. then print the arms if the fit is good

## Printing

Recommended material: **black PETG**

- 0.20 mm layers
- 4 walls for housing
- 4–5 walls for arms
- 25–35% infill for arms
- 20–30% infill for housing

## Important note

Although the critical dimensions now come from the original camera model, your specific camera module may still have small PCB or connector tolerances. The fit-test frame is still the fastest way to validate the geometry before printing the full set.
'''
(OUT/'README.md').write_text(README, encoding='utf-8')

zip_path = Path('/mnt/data/Kobra3Max_Slim_Camera_Arm_v6_FROM_ORIGINAL_MODEL.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    z.write(Path(__file__), Path(__file__).name)
    for p in sorted(OUT.iterdir()):
        z.write(p, Path(OUT.name)/p.name)

print('Wrote', zip_path)
for n,m in parts.items():
    print(n, np.round(m.extents,2), 'watertight', m.is_watertight, 'components', len(m.split(only_watertight=False)))
