"""MM-TOY-002 TrailCam CF10 — SUSPENSION_ARMS + AXLE_CARRIERS, rev 0.4.0 (v1, draft).

Architecture (lead decision 2026-08-30, decision-log.md): printed lower wishbone
arm + upper coil-over shock acting as the upper link. NO printed upper arm.

Component families built here (one script, all deterministic):
  SUSPENSION_ARM  lower wishbone, left/right via `side` parameter; front and rear
                  use the SAME physical part (shape is x-symmetric about the axle
                  plane), built on the +x axle plane (x=+AXLE_X_MM).
  AXLE_CARRIER    upright, left/right via `side`; front carriers add a steering
                  arm boss (front=True) -> geometry differs -> separate
                  deterministic front/rear exports.

Coordinate system (parameters.ORIGIN_NOTE): x forward, y left, z up. Parts are
built in as-used vehicle coordinates and exported in that orientation (no hidden
transforms, CAD coding standard).

Interface constants QUOTED from chassis.py v1 (frozen; chassis.py is NOT modified
and NOT imported — importing it would rebuild/re-export the chassis):
  BOSS_IN = (59.0, 67.0)        inner clevis boss y extent (bore axis along y)
  BOSS_OUT = (71.0, 79.0)       outer clevis boss y extent; arm tang gap y 67..71
  PIN_BORE_D = 3.2, PIN_Z = 6.0 pivot bore 3.2 mm along y at (x=+/-126, z=6)
  BOSS_H = 14.0                 bosses span z 0..14
  BOSS_HW = 8.0                 boss half width in x (bosses x 118..134)
  SS_X_HALF = 10.0              corner base plate x half (x 116..136)
  base plate                    y 38..80, z 0..4 under both bosses
  TOWER_Y = (47.0, 55.0)        shock tower plate y extent (tower faces)
  SHOCK_BORE_D = 3.2, SHOCK_BORE_Z = 45.0  tower bore along y at (x=+/-126, z=45)
  M3 = 3.4                      all fastener holes are plain M3 clearance
  SADDLE_HOLE_DX = 30.0         saddle anchor holes along y at (x=+/-126+/-30, z=12)
  saddle body                   y 38.6..47.4 off the rail outer face, z 2..22
  wheel centers                 (x=+/-126, y=+/-82.5, z=+5); tire dia 90 (env 115)

Purchased-part PROXIES (comment-only; never modeled): 540/550 planetary geared
motor (parameters.MOTOR_ENVELOPE_MM = (36, 36, 80)), 5 mm wheel shaft/bearing,
coil-over shock, steering link, all M3 fasteners. NO printed threads anywhere
(chassis.py contract rule 10; parameters.FASTENER_DEFAULT = M3 through-bolt).

KNOWN DRAFT CONFLICTS with frozen chassis v1 corner geometry (chassis.py must not
change here; flagged for a chassis v2 reconciliation):
  K-1 chassis OUTER clevis boss (y 71..79, z 0..14, x 118..134) + base plate
      (y 38..80, z 0..4, x 116..136) occupy the same space as the arm outer end
      and the carrier upright/slots required by this task's interface contract.
  K-2 motor clamp bore (dia 36.4, y 58..72 at z=5) intersects the chassis inner
      clevis boss, riser and base plate volumes.
  K-3 pivot bore z=6 sits only 0.4 mm above the base plate top (z=4): the arm
      tang can only keep a 0.4 mm lip below the 3.2 bore (ASSUME-2).
  K-4 the shock tower plate itself fills y 47..55, so the 8 mm carrier shock eye
      cannot sit INSIDE y 47..55 (ASSUME-1).
  K-5 nominal tire inner face (tire y 66..99) overlaps the chassis corner region;
      inherited packaging question, out of scope for this task.

ASSUMPTIONS (draft, all reviewable before manufacturing):
  ASSUME-1 carrier shock eye at y 55.25..63.25, i.e. 8 mm thick with 0.25 mm
           clearance OUTBOARD of the tower outboard face; eye bore is coaxial
           with the tower bore (asserted). "Reaches y 47..55" is read as
           "reaches the tower interface band"; an eye inside y 47..55 would
           intersect the frozen tower plate (K-4).
  ASSUME-2 arm plate z 4.0..11.0: it rests on the chassis base plate top (z=4)
           (K-3); 0.4 mm lip below the tang bore; suspension travel is limited
           by tang/base-plate contact and needs a motion sweep later.
  ASSUME-3 motor bore 36.4 mm = 0.2 mm/side over a 36 mm can. Note:
           parameters.CLEARANCE_PURCHASED_MM = 0.4/side would give 36.8; contract
           fixes 36.4 — measure the real motor before manufacturing.
  ASSUME-4 gearhead face seats on the carrier upright face y=+/-72; motor body is
           inserted inboard; wheel shaft bore 5.0 is PROVISIONAL for a purchased
           metal shaft/bearing.
  ASSUME-5 coil-over axis is along y between the tower bore (y 47..55) and the
           carrier eye bore (y 55.25..63.25): short eye-to-eye spacing, so
           suspension stroke is geometry-limited; kinematics review pending.
  ASSUME-6 front and rear suspension arms are the same part; front/rear carriers
           differ (steering boss) -> 8 deterministic carrier exports.

Exports (deterministic names, STL tolerance 0.1 mm, as-used orientation):
  exports/DRAFT-suspension-arm-left.step/.stl
  exports/DRAFT-suspension-arm-right.step/.stl
  exports/DRAFT-axle-carrier-left-front.step/.stl
  exports/DRAFT-axle-carrier-right-front.step/.stl
  exports/DRAFT-axle-carrier-left-rear.step/.stl
  exports/DRAFT-axle-carrier-right-rear.step/.stl

Units: millimetres. All vehicle datums come from parameters.py (single source of
truth, rev 0.4.0); chassis interface values are quoted above as comments.
"""

from __future__ import annotations

import importlib.metadata
import math
import sys
from functools import reduce
from pathlib import Path

import cadquery as cq
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # authoritative contract lives next to this file
import parameters as P

# ---------------------------------------------------------------------------
# Frozen-datum assertions (values this component relies on)
# ---------------------------------------------------------------------------
assert P.AXLE_X_MM == 126.0, "axle planes must be +/-126"
assert P.WHEEL_Y_MM == 82.5, "wheel planes must be +/-82.5"
assert P.WALL_MIN_MM == 2.4, "printed wall minimum changed"
assert P.FATIGUE_MIN_MM == 3.0, "fatigue section minimum changed"
assert P.CLEARANCE_FASTENER_MM == 0.25, "printed-to-printed clearance changed"
assert P.CLEARANCE_PURCHASED_MM == 0.4, "printed-to-purchased clearance changed"
assert P.MOTOR_ENVELOPE_MM[0] == 36.0, "motor can diameter changed"

# ---------------------------------------------------------------------------
# Interface constants quoted from chassis.py v1 (see module docstring)
# ---------------------------------------------------------------------------
CH_BOSS_IN_Y = (59.0, 67.0)
CH_BOSS_OUT_Y = (71.0, 79.0)
CH_PIVOT_BORE_D = 3.2
CH_PIVOT_Z = 6.0
CH_BOSS_HW = 8.0
CH_BASE_PLATE_TOP_Z = 4.0          # base plate z 0..4 under the corner
CH_TOWER_Y = (47.0, 55.0)
CH_SHOCK_BORE_D = 3.2
CH_SHOCK_BORE_Z = 45.0
CH_M3 = 3.4
CH_SADDLE_HOLE_DX = 30.0
CH_SADDLE_HOLE_Z = 12.0
CH_SADDLE_OUT_Y = P.FRAME_RAIL_Y_MM + P.RAIL_W_MM / 2.0 + 8.4  # 47.4 quoted

# ---------------------------------------------------------------------------
# SUSPENSION_ARM design constants (front/rear identical; side via `side`)
# ---------------------------------------------------------------------------
AX = P.AXLE_X_MM                   # build on the +x axle plane; mirror by side
ARM_GAP_Y = (CH_BOSS_IN_Y[1], CH_BOSS_OUT_Y[0])     # (67, 71) -> 4.0 gap
ARM_TANG_CLEAR = 0.2               # per side, task contract (0.2 clearance/side)
ARM_TANG_T = (ARM_GAP_Y[1] - ARM_GAP_Y[0]) - 2.0 * ARM_TANG_CLEAR  # 3.6
ARM_TANG_X_HALF = CH_BOSS_HW       # tang width matches boss width (16)
ARM_PLATE_Z = (4.0, 11.0)          # flat plate resting on base plate top (K-3)
ARM_PIVOT = (AX, CH_PIVOT_Z)       # tang bore center (x, z), axis along y
ARM_HOLE_Y = 74.0                  # outer hole line "y ~ 74"
ARM_HOLE_DX = 10.0                 # holes at x = 126 +/- 10 -> 20 spacing
ARM_HOLE_D = CH_M3                 # M3 clearance, vertical axis
ARM_HOLE_BOSS_R = 4.7              # hole r 1.7 + 3.0 fatigue wall
ARM_FILLET = 2.0                   # root fillets at tang and hole ends
ARM_FLARE_PTS = [(118.0, 70.6), (134.0, 70.6),         # wishbone flare: full
                 (140.7, ARM_HOLE_Y), (111.3, ARM_HOLE_Y)]  # width at the holes
ARM_NOTCH_TRI = [(120.7, ARM_HOLE_Y), (131.3, ARM_HOLE_Y),  # keyhole notch apex
                 (AX, 73.0)]                                # at the cap center
ARM_NOTCH_CAP_C = (AX, 73.0)       # V-root cap arc center (smooth root, r>=2.0)
ARM_NOTCH_CAP_R = 2.0              # cap arc radius IS the V root fillet

# IF-* arm assertions, before expensive geometry (CAD coding standard)
assert 3.4 <= ARM_TANG_T <= 3.8, "tang thickness contract: 3.6 (3.4..3.8)"
assert abs(ARM_TANG_T - 3.6) < 1e-9
assert abs((ARM_GAP_Y[1] - ARM_GAP_Y[0]) - 4.0) < 1e-9, "clevis gap must be 4.0"
assert ARM_PIVOT == (126.0, 6.0), "pivot bore at (x=126, z=6), axis along y"
assert CH_PIVOT_BORE_D == 3.2, "IF-CHASSIS-SUSP pivot bore 3.2 (coaxial contract)"
assert abs(2.0 * ARM_HOLE_DX - 20.0) < 1e-9, "outer holes 20 mm spacing in x"
assert ARM_HOLE_D == CH_M3 == 3.4, "outer holes M3 clearance 3.4"
ARM_T = ARM_PLATE_Z[1] - ARM_PLATE_Z[0]
assert ARM_T >= P.FATIGUE_MIN_MM, "legs >= FATIGUE_MIN_MM thick"
assert ARM_FILLET >= 2.0, "root fillets >= 2.0"
assert abs(ARM_PLATE_Z[0] - CH_BASE_PLATE_TOP_Z) < 1e-9, "arm rests on base plate"


def _notch_tangent_point():
    """Tangent point of the notch edge (corner -> cap circle), exact 2D math."""
    px, py = AX - ARM_HOLE_DX + ARM_HOLE_BOSS_R, ARM_HOLE_Y   # (120.7, 74)
    cx, cy = ARM_NOTCH_CAP_C
    r = ARM_NOTCH_CAP_R
    vx, vy = cx - px, cy - py
    d = math.hypot(vx, vy)
    vx, vy = vx / d, vy / d
    s_, c_ = r / d, math.sqrt(d * d - r * r) / d
    # rotate unit vector toward the circle side that lies BELOW the hole line
    ux, uy = vx * c_ + vy * s_, vy * c_ - vx * s_
    tx, ty = px + math.sqrt(d * d - r * r) * ux, py + math.sqrt(d * d - r * r) * uy
    return tx, ty


def _arm_leg_width(y: float) -> float:
    """Left wishbone leg width (flare edge -> notch boundary) at height y."""
    x_flare = 118.0 - (y - 70.6) * (118.0 - 111.3) / (ARM_HOLE_Y - 70.6)
    cx, cy = ARM_NOTCH_CAP_C
    r = ARM_NOTCH_CAP_R
    if y <= cy - r:                       # above the cap: legs are merged
        return 2.0 * (cx - x_flare) - 2.0 * r  # both legs + cap, conservative
    tx, ty = _notch_tangent_point()
    if y <= ty:                           # cap arc
        x_notch = cx - math.sqrt(r * r - (y - cy) ** 2)
    else:                                 # straight notch edge
        x_notch = (AX - ARM_HOLE_DX + ARM_HOLE_BOSS_R) + (y - ARM_HOLE_Y) * (
            tx - (AX - ARM_HOLE_DX + ARM_HOLE_BOSS_R)) / (ty - ARM_HOLE_Y)
    return x_notch - x_flare


for _y in (71.0, 71.5, 72.0, 72.5, 73.0, 73.5, 73.9):
    assert _arm_leg_width(_y) >= 8.0 - 1e-6, f"leg width < 8 at y={_y}"

# ---------------------------------------------------------------------------
# AXLE_CARRIER design constants
# ---------------------------------------------------------------------------
C_UPRIGHT_X = (110.0, 142.0)       # centered on the axle plane x=126
C_UPRIGHT_Y = (72.0, 80.0)         # "spanning y 72..80"
C_UPRIGHT_Z = (0.0, 30.0)          # "in z 0..30 region"
C_FLANGE_Z0 = 11.25                # flange deck over the arm prongs
C_SLOT_GAP = P.CLEARANCE_FASTENER_MM  # 0.25 printed-to-printed clearance
# prong slots receive the arm outer prongs (arm prong x extents below)
C_PRONG_X = (AX - ARM_HOLE_DX - ARM_HOLE_BOSS_R, AX - ARM_HOLE_DX + ARM_HOLE_BOSS_R)  # L 111.3..120.7
C_PRONG_X_R = (AX + ARM_HOLE_DX - ARM_HOLE_BOSS_R, AX + ARM_HOLE_DX + ARM_HOLE_BOSS_R)  # R 131.3..140.7
C_SLOT_L_X = (C_PRONG_X[0] - C_SLOT_GAP - 1.05, C_PRONG_X[1] + C_SLOT_GAP)  # opens at block edge
C_SLOT_R_X = (C_PRONG_X_R[0] - C_SLOT_GAP, C_PRONG_X_R[1] + C_SLOT_GAP + 1.05)
C_SLOT_Y = (71.9, 80.1)            # open inboard and outboard (cutter overshoot)
C_SLOT_Z = (-0.1, C_FLANGE_Z0)     # open below; flange deck above
C_MOUTH_Y1 = 74.05                 # central mouth between prongs (shaft mouth)
C_PRONG_Y_MAX = ARM_HOLE_Y + ARM_HOLE_BOSS_R  # 78.7 arm prong reach
# shock arm + eye (ASSUME-1)
C_EYE_D = 13.0
C_EYE_T = 8.0                      # "8 mm thick eye"
C_EYE_Y0 = CH_TOWER_Y[1] + P.CLEARANCE_FASTENER_MM  # 55.25 outboard of tower
C_EYE_BORE_D = CH_SHOCK_BORE_D     # 3.2, coaxial with the tower bore
# motor clamp + tabs
C_MOTOR_BORE_D = 36.4              # task contract (ASSUME-3)
C_MOTOR_AXIS = (AX, 5.0)           # (x, z), axis along y == wheel axis
C_MOTOR_Y = (58.0, 72.6)           # clamp band; 0.6 overlap into the upright
C_CLAMP_OD = C_MOTOR_BORE_D + 7.0  # 43.4 -> 3.5 ring wall >= FATIGUE_MIN_MM
C_SLIT_W = 2.0                     # split slot width in z, radial in +x
C_SLIT_Z = (C_MOTOR_AXIS[1] - C_SLIT_W / 2.0, C_MOTOR_AXIS[1] + C_SLIT_W / 2.0)
C_EAR_X = (143.5, 154.5)           # clamp bolt ears at the +x OD
C_EAR_Z_UP = (6.2, 16.2)
C_EAR_Z_LO = (-6.2, 3.8)
C_CLAMP_BOLT = (149.0, 65.0)       # vertical M3.4 clamp bolt (x, y)
C_SHAFT_BORE_D = 5.0               # PROVISIONAL purchased shaft/bearing (ASSUME-4)
C_HUB_D = 14.0
C_HUB_Y = (79.9, P.WHEEL_Y_MM)     # bearing seat up to the wheel center plane
C_TAB_GAP = P.CLEARANCE_FASTENER_MM  # tab face vs saddle outboard face
C_TAB_Y = (CH_SADDLE_OUT_Y + C_TAB_GAP, 59.5)      # 47.65..59.5
C_TAB_Z = (4.5, 17.5)              # around the z=12 saddle hole line
C_TAB_L_X = (91.3, 107.5)          # around saddle hole x=96, clear of motor OD
C_TAB_R_X = (151.3, 160.7)         # around saddle hole x=156
# steering arm boss (front only), extends rearward (-x at the front corner)
C_STEER_X = (AX - 28.0 - 7.0, 111.0)   # hole at x=98, boss to x=111
C_STEER_Y = (71.0, 80.7)
C_STEER_Z = (20.0, 30.0)
C_STEER_HOLE = (AX - 28.0, 76.0)   # task contract (x=98, y=76), vertical

# IF-* carrier assertions, before expensive geometry
assert C_UPRIGHT_Y == (72.0, 80.0) and C_UPRIGHT_Z == (0.0, 30.0)
assert C_EYE_T == 8.0, "shock eye 8 mm thick"
assert C_EYE_BORE_D == CH_SHOCK_BORE_D == 3.2, "eye bore == tower bore dia"
assert C_EYE_Y0 - CH_TOWER_Y[1] >= P.CLEARANCE_FASTENER_MM - 1e-9, \
    "eye clears the frozen tower outboard face (ASSUME-1)"
assert C_MOTOR_AXIS == (AX, 5.0) == (AX, C_MOTOR_AXIS[1]), "motor axis at (126, z=5)"
assert C_MOTOR_AXIS == (126.0, 5.0), "motor bore coaxial with wheel shaft bore"
assert abs(C_MOTOR_BORE_D - (P.MOTOR_ENVELOPE_MM[0] + 0.4)) < 1e-9, \
    "36.4 = 36 mm can + 0.2/side (ASSUME-3)"
assert abs(C_MOTOR_Y[0] - 58.0) < 1e-9 and C_MOTOR_Y[1] >= 72.0, "clamp y 58..72"
assert (C_CLAMP_OD - C_MOTOR_BORE_D) / 2.0 >= P.FATIGUE_MIN_MM, "clamp ring wall"
assert C_SHAFT_BORE_D == 5.0, "wheel shaft bore 5.0 (PROVISIONAL)"
assert abs((AX + CH_SADDLE_HOLE_DX) - (AX - CH_SADDLE_HOLE_DX) - 60.0) < 1e-9, \
    "tab holes 60 mm spacing in x"
assert CH_SADDLE_HOLE_Z == 12.0 and CH_SADDLE_HOLE_DX == 30.0, \
    "tab holes coaxial with chassis saddle holes (x=126+/-30, z=12)"
assert abs(C_TAB_Y[0] - CH_SADDLE_OUT_Y - 0.25) < 1e-9, "tab clears saddle face"
assert C_STEER_HOLE == (98.0, 76.0), "steering hole at (126-28, y=76)"
assert C_HUB_Y[1] <= P.WHEEL_Y_MM, "carrier body inboard of the wheel plane"
# min-wall / fatigue-section checks (requirement 7), derived from the constants
assert (AX - C_SHAFT_BORE_D / 2.0) - (C_PRONG_X[1] + C_SLOT_GAP) >= P.WALL_MIN_MM, \
    "shaft-bore web x-wall >= WALL_MIN_MM"            # 123.5 - 120.95 = 2.55
assert (C_PRONG_X_R[0] - C_SLOT_GAP) - (AX + C_SHAFT_BORE_D / 2.0) >= P.WALL_MIN_MM
assert (AX - C_SHAFT_BORE_D / 2.0) >= P.WALL_MIN_MM, "web floor under shaft bore"
assert (C_HUB_D - C_SHAFT_BORE_D) / 2.0 >= P.FATIGUE_MIN_MM, "hub boss wall"
assert (C_EYE_D - C_EYE_BORE_D) / 2.0 >= P.FATIGUE_MIN_MM, "shock eye wall"
assert min(C_CLAMP_BOLT[0] - CH_M3 / 2.0 - C_EAR_X[0],
           C_EAR_X[1] - (C_CLAMP_BOLT[0] + CH_M3 / 2.0)) >= P.FATIGUE_MIN_MM, \
    "clamp ear walls around the clamp bolt"
assert min(AX - CH_SADDLE_HOLE_DX - CH_M3 / 2.0 - C_TAB_L_X[0],
           C_TAB_L_X[1] - (AX - CH_SADDLE_HOLE_DX + CH_M3 / 2.0)) >= P.FATIGUE_MIN_MM, \
    "tab x-walls around the saddle hole"
assert min(CH_SADDLE_HOLE_Z - CH_M3 / 2.0 - C_TAB_Z[0],
           C_TAB_Z[1] - (CH_SADDLE_HOLE_Z + CH_M3 / 2.0)) >= P.FATIGUE_MIN_MM, \
    "tab z-walls around the saddle hole"
assert min(C_STEER_HOLE[0] - CH_M3 / 2.0 - C_STEER_X[0],
           C_STEER_X[1] - (C_STEER_HOLE[0] + CH_M3 / 2.0)) >= P.FATIGUE_MIN_MM, \
    "steering boss x-walls"
assert min(C_STEER_HOLE[1] - CH_M3 / 2.0 - C_STEER_Y[0],
           C_STEER_Y[1] - (C_STEER_HOLE[1] + CH_M3 / 2.0)) >= P.FATIGUE_MIN_MM, \
    "steering boss y-walls"
# prong/slot mating geometry (arm <-> carrier interface)
assert C_SLOT_L_X[1] - C_PRONG_X[1] >= C_SLOT_GAP - 1e-9
assert C_PRONG_X[0] - C_SLOT_L_X[0] >= C_SLOT_GAP - 1e-9
assert C_PRONG_X_R[0] - C_SLOT_R_X[0] >= C_SLOT_GAP - 1e-9
assert C_SLOT_R_X[1] - C_PRONG_X_R[1] >= C_SLOT_GAP - 1e-9


# ---------------------------------------------------------------------------
# Small solid/cutter helpers (absolute vehicle coordinates, mm)
# ---------------------------------------------------------------------------
def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Solid:
    xa, xb = min(x0, x1), max(x0, x1)
    ya, yb = min(y0, y1), max(y0, y1)
    za, zb = min(z0, z1), max(z0, z1)
    return cq.Solid.makeBox(xb - xa, yb - ya, zb - za, pnt=(xa, ya, za))


def cyl(p0, p1, r: float) -> cq.Solid:
    import cadquery as _cq
    d = _cq.Vector(p1) - _cq.Vector(p0)
    return cq.Solid.makeCylinder(r, d.Length, pnt=p0, dir=d.normalized())


def prism_xy(pts, z0: float, z1: float) -> cq.Solid:
    """Extrude an (x, y) outline along z between z0 and z1."""
    za, zb = min(z0, z1), max(z0, z1)
    wp = cq.Workplane("XY", origin=(0.0, 0.0, za))
    wp = wp.moveTo(*pts[0])
    for p in pts[1:]:
        wp = wp.lineTo(*p)
    return wp.close().extrude(zb - za).val()


def prism_yz(pts, x0: float, x1: float) -> cq.Solid:
    """Extrude a (y, z) outline along +x between x0 and x1 (chassis.py pattern)."""
    xa, xb = min(x0, x1), max(x0, x1)
    wp = cq.Workplane("YZ", origin=(xa, 0.0, 0.0))
    wp = wp.moveTo(*pts[0])
    for p in pts[1:]:
        wp = wp.lineTo(*p)
    return wp.close().extrude(xb - xa).val()


def _outline_walk(wire: cq.Wire):
    """Ordered outer-wire walk -> list of (edge, traversed_forward)."""
    def key(p):
        return (round(p.x, 6), round(p.y, 6), round(p.z, 6))
    edges = list(wire.Edges())
    order = [(edges.pop(0), True)]
    while edges:
        e_last, f_last = order[-1]
        cur_end = e_last.endPoint() if f_last else e_last.startPoint()
        for i, e in enumerate(edges):
            if key(e.startPoint()) == key(cur_end):
                order.append((edges.pop(i), True))
                break
            if key(e.endPoint()) == key(cur_end):
                order.append((edges.pop(i), False))
                break
        else:
            raise RuntimeError("outer wire walk failed")
    return order


def concave_corner_vertices(solid: cq.Solid, wire: cq.Wire, z_probe: float):
    """Concave (root) corners of a planar outline wire. Parametrization-free:
    for every corner, sample one point on each adjacent edge close to the
    corner; if the midpoint of those two points is outside the solid, the
    corner is reentrant (a root). Returns cq.Vertex objects (usable by
    Wire.fillet2D)."""
    order = _outline_walk(wire)
    n = len(order)
    eps = 0.015  # normalized edge parameter close to the corner vertex

    def near_v(e, v):
        if abs(e.startPoint().x - v.x) < 1e-6 and abs(e.startPoint().y - v.y) < 1e-6:
            return e.positionAt(eps)
        return e.positionAt(1.0 - eps)

    out = []
    for i in range(n):
        e_b, f_b = order[i]
        v = e_b.startPoint() if f_b else e_b.endPoint()
        p_in = near_v(order[i - 1][0], v)
        p_out = near_v(e_b, v)
        mid = cq.Vector((p_in.x + p_out.x) / 2.0, (p_in.y + p_out.y) / 2.0, z_probe)
        if solid.isInside(mid, 1e-6):
            continue  # convex corner (midpoint inside) — not a root
        cand = [x for x in e_b.Vertices()
                if abs(x.Center().x - v.x) < 1e-6 and abs(x.Center().y - v.y) < 1e-6]
        assert len(cand) == 1, "corner vertex lookup failed"
        out.append(cand[0])
    return out


def fillet_face_2d(face: cq.Face, targets, r: float) -> cq.Face:
    """Sequential 2D fillets at the target corner coordinates (robust)."""
    out = face
    for (tx, ty) in targets:
        cand = [v for v in out.Vertices()
                if abs(v.Center().x - tx) < 1e-3 and abs(v.Center().y - ty) < 1e-3]
        assert len(cand) == 1, f"fillet target ({tx:.2f}, {ty:.2f}) not found"
        mf = BRepFilletAPI_MakeFillet2d(out.wrapped)
        mf.AddFillet(cand[0].wrapped, r)
        mf.Build()
        assert mf.IsDone(), f"2D fillet failed at ({tx:.2f}, {ty:.2f})"
        out = cq.Face(mf.Shape())
        assert out.isValid(), "filleted face became invalid"
    return out


# ---------------------------------------------------------------------------
# SUSPENSION_ARM builder (built at x=+126; side=+1 left, side=-1 right)
# ---------------------------------------------------------------------------
ARM_OUTER_HOLES_LOCAL = (  # (x, y) vertical holes; exported for cross-asserts
    (AX - ARM_HOLE_DX, ARM_HOLE_Y),
    (AX + ARM_HOLE_DX, ARM_HOLE_Y),
)


def build_arm(side: int) -> cq.Solid:
    """Lower wishbone arm built at x=+126; side=+1 left, side=-1 right.

    Plan shape (flat plate, z thickness vertical, printed flat as used):
      tang rect + wishbone flare trapezoid + two hole-boss discs, with a
      keyhole notch between the legs whose cap arc (r=2.0) IS the V-root.
    Root fillets >= 2.0 are applied as 2D fillets on the fused outline before
    extrusion (concave corners: tang-end roots + hole-end roots); the cap arc
    and the boss-disc arcs are smooth fatigue-friendly roots by construction.
    """
    s = float(side)
    z0, z1 = ARM_PLATE_Z
    sy = lambda pts: [(x, s * y) for (x, y) in pts]

    positives: list[cq.Solid] = []
    # inner clevis tang (3.6 thick in y, inside the 4.0 chassis clevis gap)
    positives.append(prism_xy(sy([(AX - ARM_TANG_X_HALF, ARM_GAP_Y[0] + ARM_TANG_CLEAR),
                                  (AX + ARM_TANG_X_HALF, ARM_GAP_Y[0] + ARM_TANG_CLEAR),
                                  (AX + ARM_TANG_X_HALF, ARM_GAP_Y[1] - ARM_TANG_CLEAR),
                                  (AX - ARM_TANG_X_HALF, ARM_GAP_Y[1] - ARM_TANG_CLEAR)]),
                              0.0, 1.0))
    # wishbone flare from the tang to the full width at the hole line
    positives.append(prism_xy(sy(ARM_FLARE_PTS), 0.0, 1.0))
    # hole bosses (fatigue wall >= 3.0 around each outer M3 hole)
    for (hx, hy) in ARM_OUTER_HOLES_LOCAL:
        positives.append(cyl((hx, s * hy, 0.0), (hx, s * hy, 1.0), ARM_HOLE_BOSS_R))
    plan = reduce(lambda a, b: a.fuse(b), positives).clean()

    # keyhole notch between the legs (open at the outboard/hole end), cut
    # BEFORE filleting so its corners are part of the outline to be filleted
    sk_n = cq.Sketch().polygon(sy(ARM_NOTCH_TRI)).push(
        [(ARM_NOTCH_CAP_C[0], s * ARM_NOTCH_CAP_C[1])]).circle(ARM_NOTCH_CAP_R)
    notch = (cq.Workplane("XY", origin=(0.0, 0.0, z0 - 0.5))
             .placeSketch(sk_n).extrude(ARM_T + 1.0).val())
    plan = plan.cut(notch).clean()
    assert len(plan.Solids()) == 1 and plan.isValid()

    # root fillets >= 2.0: every concave corner of the fused outline (2 roots
    # where the legs meet the tang, 2 roots at the hole-end notch corners; the
    # V-root cap arc is already the smooth fillet). 2D fillet on the outline
    # wire before extrusion — stable, no brittle post-fuse edge reselection.
    top = [f for f in plan.Faces() if abs(f.Center().z - 1.0) < 1e-6][0]
    wire = top.outerWire()
    roots = concave_corner_vertices(plan, wire, z_probe=0.5)
    assert len(roots) == 4, f"expected 4 root corners, got {len(roots)}"
    try:
        top = cq.Face.makeFromWires(wire.fillet2D(ARM_FILLET, roots))
        assert top.isValid(), "filleted outline face invalid"
    except Exception:
        top = fillet_face_2d(top, [(v.Center().x, v.Center().y) for v in roots],
                             ARM_FILLET)

    # extrude the filleted plan face from z1 downward to z0 (as-used plate)
    top = top.translate((0.0, 0.0, z1 - 1.0))
    prism = BRepPrimAPI_MakePrism(top.wrapped, gp_Vec(0.0, 0.0, -ARM_T))
    part = cq.Solid(prism.Shape()).clean()
    assert len(part.Solids()) == 1 and part.isValid()

    cutters: list[cq.Solid] = []
    # pivot bore 3.2 along y at (126, z=6) — coaxial with the chassis pivot bore
    cutters.append(cyl((ARM_PIVOT[0], s * (ARM_GAP_Y[0] - 0.7), ARM_PIVOT[1]),
                       (ARM_PIVOT[0], s * (ARM_GAP_Y[1] + 0.7), ARM_PIVOT[1]),
                       CH_PIVOT_BORE_D / 2.0))
    # two outer M3 holes, vertical axis, 20 mm spacing in x (mate with carrier)
    for (hx, hy) in ARM_OUTER_HOLES_LOCAL:
        cutters.append(cyl((hx, s * hy, z0 - 0.5), (hx, s * hy, z1 + 0.5),
                           ARM_HOLE_D / 2.0))
    for c in cutters:
        part = part.cut(c).clean()
    return part


# ---------------------------------------------------------------------------
# AXLE_CARRIER builder (built at x=+126; side=+1 left, side=-1 right;
# front=True adds the steering arm boss)
# ---------------------------------------------------------------------------
C_FLANGE_HOLES_LOCAL = ARM_OUTER_HOLES_LOCAL     # coaxial with arm outer holes
C_TAB_HOLES_LOCAL = (                            # coaxial with chassis saddle holes
    (AX - CH_SADDLE_HOLE_DX, CH_SADDLE_HOLE_Z),
    (AX + CH_SADDLE_HOLE_DX, CH_SADDLE_HOLE_Z),
)


def build_carrier(side: int, front: bool) -> cq.Solid:
    s = float(side)

    positives: list[cq.Solid] = []
    # 1) upright block spanning y 72..80 at x=126 in the z 0..30 region
    positives.append(box(C_UPRIGHT_X[0], C_UPRIGHT_X[1],
                         s * C_UPRIGHT_Y[0], s * C_UPRIGHT_Y[1],
                         C_UPRIGHT_Z[0], C_UPRIGHT_Z[1]))
    # wheel-side hub boss up to the wheel center plane (PROVISIONAL bearing seat)
    positives.append(cyl((AX, s * C_HUB_Y[0], C_MOTOR_AXIS[1]),
                         (AX, s * C_HUB_Y[1], C_MOTOR_AXIS[1]), C_HUB_D / 2.0))
    # 3) motor clamp band (motor proxy: 540/550 planetary can, dia 36, not modeled).
    #    Band overlaps the upright by 0.6 for a robust fuse; gearhead face seats
    #    on the upright face y=+/-72 (ASSUME-4).
    positives.append(cyl((AX, s * C_MOTOR_Y[0], C_MOTOR_AXIS[1]),
                         (AX, s * C_MOTOR_Y[1], C_MOTOR_AXIS[1]), C_CLAMP_OD / 2.0))
    # clamp ears flanking the +x radial split slot; vertical clamp bolt pulls them
    positives.append(box(C_EAR_X[0], C_EAR_X[1], s * C_MOTOR_Y[0], s * C_MOTOR_Y[1],
                         *C_EAR_Z_UP))
    positives.append(box(C_EAR_X[0], C_EAR_X[1], s * C_MOTOR_Y[0], s * C_MOTOR_Y[1],
                         *C_EAR_Z_LO))
    # 6) anti-rotation tabs on the inboard face, bolting to the chassis saddle
    #    holes (coaxial, axis along y, at x=126+/-30, z=12)
    for (tx0, tx1) in (C_TAB_L_X, C_TAB_R_X):
        positives.append(box(tx0, tx1, s * C_TAB_Y[0], s * C_TAB_Y[1], *C_TAB_Z))
    # 2) upper inward shock arm: root block on the flange deck + ramp + eye
    positives.append(box(122.0, 130.0, s * 71.5, s * 79.5, 16.5, 30.5))
    positives.append(prism_yz([(s * 79.5, 16.5), (s * 79.5, 30.5),
                               (s * 57.0, 50.5), (s * 57.0, 39.5)], 122.0, 130.0))
    positives.append(cyl((AX, s * C_EYE_Y0, CH_SHOCK_BORE_Z),
                         (AX, s * (C_EYE_Y0 + C_EYE_T), CH_SHOCK_BORE_Z),
                         C_EYE_D / 2.0))
    # 5) steering arm boss (FRONT only): rearward toward the vehicle center
    if front:
        positives.append(box(C_STEER_X[0], C_STEER_X[1],
                             s * C_STEER_Y[0], s * C_STEER_Y[1], *C_STEER_Z))

    part = reduce(lambda a, b: a.fuse(b), positives).clean()

    cutters: list[cq.Solid] = []
    # 1) prong slots + central mouth: receive the arm outer prongs with 0.25
    #    printed-to-printed clearance; flange deck stays above at z=11.25
    cutters.append(box(C_SLOT_L_X[0], C_SLOT_L_X[1], s * C_SLOT_Y[0],
                       s * C_SLOT_Y[1], *C_SLOT_Z))
    cutters.append(box(C_SLOT_R_X[0], C_SLOT_R_X[1], s * C_SLOT_Y[0],
                       s * C_SLOT_Y[1], *C_SLOT_Z))
    cutters.append(box(120.8, 131.2, s * 71.9, s * C_MOUTH_Y1, *C_SLOT_Z))
    # 4) wheel shaft bore 5.0 through along y (PROVISIONAL purchased shaft)
    cutters.append(cyl((AX, s * 71.5, C_MOTOR_AXIS[1]),
                       (AX, s * 82.8, C_MOTOR_AXIS[1]), C_SHAFT_BORE_D / 2.0))
    # 3) motor clamp bore + split slot + vertical clamp bolt hole
    cutters.append(cyl((AX, s * 57.5, C_MOTOR_AXIS[1]),
                       (AX, s * 72.9, C_MOTOR_AXIS[1]), C_MOTOR_BORE_D / 2.0))
    cutters.append(box(AX, C_EAR_X[1] - 6.0 + 0.5, s * 57.5, s * 72.9, *C_SLIT_Z))
    cutters.append(cyl((C_CLAMP_BOLT[0], s * C_CLAMP_BOLT[1], -7.0),
                       (C_CLAMP_BOLT[0], s * C_CLAMP_BOLT[1], 17.5), CH_M3 / 2.0))
    # 6) tab holes, axis along y, coaxial with the chassis saddle anchor holes
    for (tx, tz) in C_TAB_HOLES_LOCAL:
        cutters.append(cyl((tx, s * 47.0, tz), (tx, s * 60.0, tz), CH_M3 / 2.0))
    # 1) flange holes: coaxial with the arm outer holes, through the flange deck
    for (hx, hy) in C_FLANGE_HOLES_LOCAL:
        cutters.append(cyl((hx, s * hy, C_FLANGE_Z0 - 0.25), (hx, s * hy, 30.5),
                           CH_M3 / 2.0))
    # 2) shock eye bore 3.2 along y at (126, z=45) — coaxial with the tower bore;
    #    the coil-over shock itself is a purchased proxy (never modeled)
    cutters.append(cyl((AX, s * (C_EYE_Y0 - 0.75), CH_SHOCK_BORE_Z),
                       (AX, s * (C_EYE_Y0 + C_EYE_T + 0.75), CH_SHOCK_BORE_Z),
                       C_EYE_BORE_D / 2.0))
    # 5) steering link hole (FRONT only): M3.4 vertical at (126-28, y=76)
    if front:
        cutters.append(cyl((C_STEER_HOLE[0], s * C_STEER_HOLE[1], 19.5),
                           (C_STEER_HOLE[0], s * C_STEER_HOLE[1], 30.5), CH_M3 / 2.0))

    for c in cutters:
        part = part.cut(c).clean()
    return part


# ---------------------------------------------------------------------------
# Build, verify, export
# ---------------------------------------------------------------------------
parts = [
    ("DRAFT-suspension-arm-left", build_arm(+1), "arm"),
    ("DRAFT-suspension-arm-right", build_arm(-1), "arm"),
    ("DRAFT-axle-carrier-left-front", build_carrier(+1, front=True), "carrier"),
    ("DRAFT-axle-carrier-right-front", build_carrier(-1, front=True), "carrier"),
    ("DRAFT-axle-carrier-left-rear", build_carrier(+1, front=False), "carrier"),
    ("DRAFT-axle-carrier-right-rear", build_carrier(-1, front=False), "carrier"),
]

# in-script CadQuery checks (contract acceptance 3): single valid solid per part
for name, part, kind in parts:
    assert len(part.Solids()) == 1, f"{name}: must be a single solid"
    assert part.isValid(), f"{name}: B-Rep must be valid"

# arm <-> carrier coaxial interface: flange holes == arm outer holes (same axis)
assert C_FLANGE_HOLES_LOCAL == ARM_OUTER_HOLES_LOCAL
# carrier shock eye bore coaxial with the chassis shock tower bore (IF-CHASSIS-SHOCKS)
assert C_EYE_BORE_D == CH_SHOCK_BORE_D and C_MOTOR_AXIS[0] == AX
# carrier tab holes coaxial with the chassis saddle holes (IF-CHASSIS-DRIVE)
assert C_TAB_HOLES_LOCAL[0][0] == AX - CH_SADDLE_HOLE_DX
assert C_TAB_HOLES_LOCAL[1][0] == AX + CH_SADDLE_HOLE_DX
assert C_TAB_HOLES_LOCAL[0][1] == CH_SADDLE_HOLE_Z == 12.0
# motor clamp bore coaxial with the wheel shaft bore (both along y at (126, z=5))
assert C_MOTOR_AXIS == (AX, 5.0)

EXPORT_DIR = HERE / "exports"
EXPORT_DIR.mkdir(exist_ok=True)
STL_TOL = 0.1  # mm, contract mesh tolerance (same as chassis.py)

summary = []
for name, part, kind in parts:
    # measure BEFORE exporting: cq.exporters mutates the shape's cached data
    bb = part.BoundingBox()
    vol_mm3 = part.Volume()
    n_solids = len(part.Solids())
    valid = part.isValid()

    step_path = EXPORT_DIR / f"{name}.step"
    stl_path = EXPORT_DIR / f"{name}.stl"
    cq.exporters.export(part, str(step_path))
    cq.exporters.export(part, str(stl_path), tolerance=STL_TOL, angularTolerance=0.1)

    # geometric interface guards
    if kind == "carrier":
        assert max(bb.ymax, -bb.ymin) <= P.WHEEL_Y_MM + 1e-4, \
            f"{name}: carrier body must stay inboard of the wheel center plane " \
            f"(ymax {bb.ymax:.4f})"
    else:
        assert bb.zmin >= CH_BASE_PLATE_TOP_Z - 1e-4, \
            f"{name}: arm must not sink below the chassis base plate top " \
            f"(zmin {bb.zmin:.6f})"
        assert max(bb.ymax, -bb.ymin) <= C_PRONG_Y_MAX + 1e-4, "arm reach y ~78.7"
    summary.append((name, bb, vol_mm3, n_solids, valid, stl_path))

# independent trimesh verification of every exported STL (acceptance 2)
import trimesh  # noqa: E402

mesh_summary = []
for name, bb, vol_mm3, n_solids, valid, stl_path in summary:
    m = trimesh.load(str(stl_path))
    assert m.is_watertight, f"{name}: STL not watertight"
    assert m.is_winding_consistent, f"{name}: STL winding inconsistent"
    assert m.body_count == 1, f"{name}: STL must be a single body"
    assert m.volume > 0.0, f"{name}: STL volume must be > 0"
    mesh_summary.append((name, m))

# ---------------------------------------------------------------------------
# Compact summary
# ---------------------------------------------------------------------------
try:
    cq_version = importlib.metadata.version("cadquery")
except importlib.metadata.PackageNotFoundError:
    cq_version = getattr(cq, "__version__", "unknown")

print("MM-TOY-002 SUSPENSION_ARMS + AXLE_CARRIERS v0.4.0 v1 (DRAFT)")
print(f"toolchain: python {sys.version.split()[0]}, cadquery {cq_version}, "
      f"trimesh {trimesh.__version__} | STL tolerance {STL_TOL} mm")
print("interfaces: IF-CHASSIS-SUSP (pivot clevis), IF-CHASSIS-SHOCKS (tower bore),")
print("            IF-CHASSIS-DRIVE (saddle holes), IF-SUSP-CARRIERS (flange holes)")
for (name, bb, vol_mm3, n_solids, valid, stl_path), (_, m) in zip(summary, mesh_summary):
    print(f"{name}")
    print(f"  bbox min ({bb.xmin:.2f}, {bb.ymin:.2f}, {bb.zmin:.2f}) "
          f"max ({bb.xmax:.2f}, {bb.ymax:.2f}, {bb.zmax:.2f}) mm")
    print(f"  bbox size {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm | "
          f"volume {vol_mm3 / 1000.0:.1f} cm3 (mesh {m.volume / 1000.0:.1f})")
    print(f"  solids {n_solids} | isValid {valid} | "
          f"tris {len(m.faces)} | watertight {m.is_watertight} | "
          f"winding {m.is_winding_consistent} | bodies {m.body_count}")
print("exports:", ", ".join(s[0] + ".step/.stl" for s in summary))
print("OK")
