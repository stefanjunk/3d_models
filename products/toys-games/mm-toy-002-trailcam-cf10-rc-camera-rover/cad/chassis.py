"""MM-TOY-002 TrailCam CF10 — CHASSIS_PRINTED, revision 0.4.0 (v1, draft).

Fully printed ladder-frame chassis: two hollow box rails, three crossmembers,
integrated top-open battery tray with strap slots, full-length skid plate,
front/re bumpers with radiused impact corners, suspension pivot-boss pairs,
shock-tower bosses, geared-motor saddle anchors with cable strain relief,
electronics-bridge mount bosses, and a front-center steering-servo mount.

Coordinate system (parameters.ORIGIN_NOTE): x forward, y left, z up.
z=0 is the lowest frame datum (skid underside == print bed face).
Ground plane z=-40 (GROUND_CLEARANCE_MM); axle planes x=+/-126;
wheel center planes y=+/-82.5; wheel centers at z=+5.

Interface mapping (architecture/hybrid-design-plan-v0.4.0.json):
  IF-CHASSIS-SUSP     -> pivot boss pairs + pin bores (item 6, lower bosses)
  IF-CHASSIS-SHOCKS   -> shock tower bosses, 3.2 mm bore along y at z=45
  IF-CHASSIS-STEERING -> steering kinematics are out of scope for v1 chassis
  IF-CHASSIS-SERVO    -> servo mount platform + side-tab slots (item 7)
  IF-CHASSIS-DRIVE    -> motor saddle bosses + strain-relief bosses (item 8)
  IF-CHASSIS-BRIDGE   -> bridge mount bosses on rail tops (item 9)
  IF-CHASSIS-HARDWARE -> all fastener holes are plain M3 clearance 3.4 mm;
                         no printed threads anywhere (contract rule 10).

Units: millimetres. All dimensions come from parameters.py (single source of
truth, rev 0.4.0); nothing here re-defines a parameters.py value.

Print orientation intent: skid underside (z=0) on the build plate, x forward.
No supports intended. DFM notes for v1 (draft quality):
  DFM-1: all horizontal bores (pivot pins 3.2 mm, shock eye 3.2 mm, saddle
         anchors 3.4 mm along y) are printed as circular holes with axes
         horizontal; acceptable in v1, but teardrop profiles would improve
         dimensional accuracy and are the v2 candidate (contract allows
         teardrop or circular in v1).
  DFM-2: shock-tower gussets slope ~60 deg from horizontal; they bridge
         short spans and should print support-free on a 0.6 mm nozzle, with
         minimal sag risk on the underside.
  DFM-3: "two strap slots" is implemented as two strap positions (x=40 and
         x=110), each cut through BOTH tray side walls (10 mm wide along x,
         z 6..18), giving two full over-battery strap paths.
  DFM-4: servo mount is a SOLID pedestal block rising from the skid (no
         bridging between rails). The two side-tab slots leave >= 3.2 mm of
         material to the block outer edge (>= WALL_MIN_MM). Servo envelope
         fit is PROVISIONAL pending DEC-DRIVE-001 servo freeze; re-check the
         49 mm slot spacing against the real servo gauge before manufacture.
  DFM-5: battery tray interior is nominal +1.0 mm (x) / +0.2 mm (y) over
         the PROVISIONAL BATTERY_ENVELOPE_MM; battery seats directly on the
         skid top face (z=2.4), i.e. as low as the contract allows.
  DFM-6: hollow rail cavities stay ventilated to the outside through the
         strap slots, saddle anchor holes and bridge-boss holes, so no
         enclosed void exists anywhere in the part.
  DFM-7: servo side-tab slots are cut 10 mm deep into the solid block (blind,
         no printed threads per contract rule 10). Intended fastening is M3
         machine screws through the servo ears into heat-set inserts or
         captured nuts seated in these bores; final fastener stack is a
         DEC-DRIVE-001 / IF-CHASSIS-HARDWARE decision. The solid block is a
         deliberate draft choice for robustness; a weight-optimised ribbed
         variant is a later optimize-fdm-design candidate.

Exports (deterministic names, mesh tolerance 0.1 mm):
  exports/DRAFT-chassis-printed.step  (editable B-Rep master)
  exports/DRAFT-chassis-printed.stl   (manufacturing mesh, skid-down)
"""

from __future__ import annotations

import sys
import importlib.metadata
from functools import reduce
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # authoritative contract lives next to this file
import parameters as P

# ---------------------------------------------------------------------------
# Key-datum assertions (contract: wheelbase, tread, width, length)
# ---------------------------------------------------------------------------
assert P.WHEELBASE_MM == 252.0, "CC-02 class wheelbase changed"
assert P.AXLE_X_MM == P.WHEELBASE_MM / 2.0 == 126.0, "axle planes must be +/-126"
assert P.TREAD_MM == 165.0, "class tread changed"
assert P.WHEEL_Y_MM == P.TREAD_MM / 2.0 == 82.5, "wheel planes must be +/-82.5"
assert P.OVERALL_LENGTH_TARGET_MM == 400.0, "overall length target changed"
assert P.OVERALL_WIDTH_MAX_MM == 200.0, "overall width limit changed"
assert P.GROUND_CLEARANCE_MM == 40.0, "ground clearance changed"
assert -P.GROUND_CLEARANCE_MM + P.TIRE_DIAMETER_MM / 2.0 == 5.0, "wheel center z=+5"
assert P.FRAME_LENGTH_MM == 340.0, "ladder frame length changed"
assert P.FRAME_RAIL_Y_MM == 32.0, "rail centerline offset changed"
assert P.RAIL_W_MM == 14.0 and P.RAIL_H_MM == 24.0, "rail section changed"

# ---------------------------------------------------------------------------
# Derived layout values (this component only; nothing duplicates parameters.py)
# ---------------------------------------------------------------------------
RAIL_WALL = 2.4                       # box-rail wall; must honour WALL_MIN_MM
assert RAIL_WALL >= P.WALL_MIN_MM
RAIL_CAVITY_W = P.RAIL_W_MM - 2.0 * RAIL_WALL   # 9.2
RAIL_CAVITY_H = P.RAIL_H_MM - 2.0 * RAIL_WALL   # 19.2

X_FRAME = P.FRAME_LENGTH_MM / 2.0     # +/-170 rail ends
Y_RAIL = P.FRAME_RAIL_Y_MM            # +/-32 rail centerlines
RAIL_IN = Y_RAIL - P.RAIL_W_MM / 2.0  # 25 rail inner faces
RAIL_OUT = Y_RAIL + P.RAIL_W_MM / 2.0 # 39 rail outer faces

SKID_T = 2.4                          # skid plate thickness == tray floor height
assert SKID_T >= P.WALL_MIN_MM
FLOOR_TOP = SKID_T                    # battery floor sits on skid top (z=2.4)

CM_T = 8.0                            # crossmember thickness (height 24 == rail)
CM_X = {"front": 150.0, "center": 0.0, "rear": -150.0}

# Battery tray: interior >= BATTERY_ENVELOPE_MM (140 x 47), battery forward of
# the center crossmember so the crossmember doubles as the tray rear wall.
BAT_L, BAT_W, _BAT_H = P.BATTERY_ENVELOPE_MM
TRAY_GAP = 0.5                        # battery removal clearance at both ends
TRAY_X0 = CM_X["center"] + CM_T / 2.0 + TRAY_GAP  # 4.5 -> interior 141 (>=140)
TRAY_X1 = CM_X["front"] - CM_T / 2.0 - TRAY_GAP   # 145.5
TRAY_Y = BAT_W / 2.0 + 0.1                        # 23.6 -> interior 47.2 (>=47)
assert (TRAY_X1 - TRAY_X0) >= BAT_L and 2.0 * TRAY_Y >= BAT_W

STRAP_X = (40.0, 110.0)               # two strap positions (DFM-3)
STRAP_W = 10.0
STRAP_Z = (6.0, 18.0)

BUMP_XMAX = 198.0                     # overall length 396 <= 400 target
BUMP_W = 120.0                        # bumper plan width
BUMP_L = 30.0
BUMP_R = 14.0                         # radiused impact corners

# Suspension corners (contract item 6)
AX = P.AXLE_X_MM                      # +/-126
SS_X_HALF = 10.0                      # pivot bracket width in x (20 total)
BOSS_T = 8.0                          # boss thickness along bore axis y (>=8)
BOSS_HW = 8.0                         # boss half width in x (16 total)
BOSS_H = 14.0                         # boss height in z
BOSS_CH = 3.0                         # chamfered top corners on bosses
BOSS_IN = (59.0, 67.0)                # inner boss y extent (bore axis y)
BOSS_OUT = (71.0, 79.0)               # outer boss y extent; arm gap y 67..71
PIN_BORE_D = 3.2                      # contract bore for 3.0 mm pivot pin
PIN_Z = 6.0                           # bore height, inside contract z in [0,10]
PLATE_Y_END = 80.0                    # pivot base plate stays inboard of wheels
assert PLATE_Y_END < P.WHEEL_Y_MM

# Shock towers (contract item 6, upper bosses)
TOWER_THK = 8.0
TOWER_Y = (47.0, 55.0)
TOWER_Z_TOP = 52.0
SHOCK_BORE_D = 3.2
SHOCK_BORE_Z = 45.0                   # "z ~ +45"

# Motor saddles (contract item 8): two M3 holes per side at 60 mm spacing
M3 = 3.4
SADDLE_SPAN = 72.0                    # boss length along x
SADDLE_HOLE_DX = 30.0                 # holes at x = axle +/- 30 -> 60 spacing
SADDLE_T = 8.4                        # saddle thickness off the rail face
SADDLE_Z = (2.0, 22.0)

# Cable strain-relief bosses with 6 mm radius channels. Placed well inboard of
# the axle so the boss and its channel cutter never touch the motor saddle
# tangentially (a tangent cutter is what breaks mesh manifoldness).
STRAIN_DX = 50.0
STRAIN_R = 6.0

# Electronics bridge bosses (contract item 9)
BRIDGE_X = 100.0
BRIDGE_T = 6.5                        # boss height above rail top

# Servo mount (contract item 7): front center, servo long axis transverse
# (along y). A SOLID pedestal block rises from the skid so the mount plate is
# fully supported (no bridging); two side-tab slots 4.5 mm wide at 49 mm
# spacing are cut through the plate top. Servo body stands on the plate top.
SERVO_L, SERVO_W, SERVO_H = P.SERVO_ENVELOPE_MM
SERVO_TAB_SPACING = 49.0              # two side-tab slots at 49 mm spacing
SERVO_SLOT_W = 4.5                    # slot width (M3 clearance 3.4 + margin)
SERVO_SLOT_LEN = 8.0                  # slot length along x (fore/aft trim)
SERVO_BLOCK_X = (153.0, 170.5)        # front-center block; interlocks with the
                                      # front crossmember face (x=154) for a
                                      # robust union; ends at the rail end +0.5
SERVO_BLOCK_Y = 30.0                  # half-width; overlaps rail inner edges to fuse
SERVO_BLOCK_Z_TOP = 27.0              # plate top; servo stands here up to ~67

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


def prism_xz(pts, y0: float, y1: float) -> cq.Solid:
    """Extrude an (x, z) outline along y between y0 and y1 (Plane.XZ extrudes
    toward -Y, so the profile plane is placed at max(y) and extruded down)."""
    ya, yb = min(y0, y1), max(y0, y1)
    wp = cq.Workplane("XZ", origin=(0.0, yb, 0.0))
    wp = wp.moveTo(*pts[0])
    for p in pts[1:]:
        wp = wp.lineTo(*p)
    return wp.close().extrude(yb - ya).val()


def prism_yz(pts, x0: float, x1: float) -> cq.Solid:
    """Extrude a (y, z) outline along +x between x0 and x1."""
    xa, xb = min(x0, x1), max(x0, x1)
    wp = cq.Workplane("YZ", origin=(xa, 0.0, 0.0))
    wp = wp.moveTo(*pts[0])
    for p in pts[1:]:
        wp = wp.lineTo(*p)
    return wp.close().extrude(xb - xa).val()


def boss_profile_pts(cx: float, z0: float, z1: float, hw: float, ch: float):
    """Rectangle in the x/z plane with chamfered TOP corners (contract item 6:
    bosses >= 8 thick, chamfered tops)."""
    return [
        (cx - hw, z0), (cx + hw, z0),
        (cx + hw, z1 - ch), (cx + hw - ch, z1),
        (cx - hw + ch, z1), (cx - hw, z1 - ch),
    ]


# ---------------------------------------------------------------------------
# Positive geometry
# ---------------------------------------------------------------------------
positives: list[cq.Solid] = []

# 1) Ladder frame rails: hollow box tubes 14 x 24, wall 2.4, x -170..+170,
#    centered at y=+/-32, z 0..24. Ends stay open (ventilated, DFM-6).
def rail(y_center: float) -> cq.Solid:
    wp = (
        cq.Workplane("YZ", origin=(-X_FRAME, y_center, P.RAIL_H_MM / 2.0))
        .rect(P.RAIL_W_MM, P.RAIL_H_MM)
        .rect(RAIL_CAVITY_W, RAIL_CAVITY_H)
        .extrude(2.0 * X_FRAME)
    )
    return wp.val()

positives.append(rail(+Y_RAIL))
positives.append(rail(-Y_RAIL))

# 2) Three crossmembers, height == rail height (<= rail height), spanning the
#    bay between rails with 0.5 mm overlap into the rail inner walls.
for cx in CM_X.values():
    positives.append(box(cx - CM_T / 2.0, cx + CM_T / 2.0,
                         -(RAIL_IN + 0.5), RAIL_IN + 0.5, 0.0, P.RAIL_H_MM))

# 5) Skid plate: full length between rails, underside FLAT at z=0 (bed face),
#    thickness 2.4; its top face is the battery tray floor (z=2.4).
positives.append(box(-X_FRAME, X_FRAME, -(RAIL_OUT + 0.5), RAIL_OUT + 0.5, 0.0, SKID_T))

# 4) Battery tray side walls (top-open tray): solid blocks fusing the tray
#    interior to the rails; strap slots are cut afterwards.
for s in (+1.0, -1.0):
    positives.append(box(TRAY_X0, TRAY_X1, s * TRAY_Y, s * (RAIL_OUT + 0.5),
                         FLOOR_TOP, P.RAIL_H_MM))

# 3) Front/rear bumpers with radiused impact corners; overall length <= 400.
for s in (+1.0, -1.0):
    bumper = (
        cq.Workplane("XY")
        .center(s * (BUMP_XMAX - BUMP_L / 2.0), 0.0)
        .rect(BUMP_L, BUMP_W)
        .extrude(P.RAIL_H_MM)
        .edges("|Z")
        .fillet(BUMP_R)
    )
    positives.append(bumper.val())

# 6) Suspension corners: base plate + riser + inner/outer chamfered bosses.
for sx in (+AX, -AX):
    for s in (+1.0, -1.0):
        # base plate under both bosses; also carries the outer boss
        positives.append(box(sx - SS_X_HALF, sx + SS_X_HALF,
                             s * (RAIL_OUT - 1.0), s * PLATE_Y_END, 0.0, 4.0))
        # riser from rail outer face to the inner boss
        positives.append(box(sx - SS_X_HALF, sx + SS_X_HALF,
                             s * (RAIL_OUT - 1.0), s * (BOSS_IN[0] + 2.0), 0.0, 12.0))
        # inner + outer pivot bosses with chamfered tops, y-axis 3.2 mm bores
        for y0, y1 in (BOSS_IN, BOSS_OUT):
            pts = boss_profile_pts(sx, 0.0, BOSS_H, BOSS_HW, BOSS_CH)
            positives.append(prism_xz(pts, s * y0, s * y1))

# 6) Shock towers: gusset off the rail top + vertical plate, 3.2 mm bore
#    along y at z=45. Gusset slope ~60 deg prints support-free (DFM-2).
for sx in (+AX, -AX):
    for s in (+1.0, -1.0):
        gusset_pts = [
            (s * (RAIL_OUT - 1.0), P.RAIL_H_MM - 0.5),
            (s * TOWER_Y[1], P.RAIL_H_MM - 0.5),
            (s * TOWER_Y[1], TOWER_Z_TOP),
        ]
        positives.append(prism_yz(gusset_pts, sx - BOSS_HW, sx + BOSS_HW))
        # Tower plate with chamfered top corners (profile in y/z, extruded in x).
        tower_pts = boss_profile_pts(s * (TOWER_Y[0] + TOWER_Y[1]) / 2.0,
                                     P.RAIL_H_MM - 0.5, TOWER_Z_TOP,
                                     (TOWER_Y[1] - TOWER_Y[0]) / 2.0, 2.0)
        positives.append(prism_yz(tower_pts, sx - BOSS_HW, sx + BOSS_HW))

# 8) Motor saddle bosses on the rail outer faces (anchor/strain relief for the
#    geared motor units carried by the axle carriers) + strain-relief bosses.
for ax in (+AX, -AX):
    strain_x = ax - (1.0 if ax > 0 else -1.0) * STRAIN_DX  # inboard of axle
    for s in (+1.0, -1.0):
        # saddle: two M3 holes at x = ax +/- 30 (60 mm spacing), axis along y
        positives.append(box(ax - SADDLE_SPAN / 2.0, ax + SADDLE_SPAN / 2.0,
                             s * (RAIL_OUT - 0.4), s * (RAIL_OUT + SADDLE_T),
                             SADDLE_Z[0], SADDLE_Z[1]))
        # cable strain-relief boss with a 6 mm radius open-top channel; boss
        # base set so the floor under the channel stays >= WALL_MIN_MM thick
        positives.append(box(strain_x - 10.0, strain_x + 10.0,
                             s * (RAIL_OUT - 0.4), s * (RAIL_OUT + SADDLE_T),
                             16.0 - STRAIN_R - P.WALL_MIN_MM, 20.0))

# 9) Electronics-bridge mount bosses on the rail tops (M3 clearance, z-axis).
#    Built standalone so the four vertical edges of each boss can be chamfered
#    with a stable selector before fusing (no brittle edge reselection later).
for bx in (+BRIDGE_X, -BRIDGE_X):
    for by in (+Y_RAIL, -Y_RAIL):
        boss_wp = (
            cq.Workplane("XY")
            .center(bx, by)
            .rect(12.0, 12.0)
            .extrude(BRIDGE_T + 0.5)
            .edges("|Z")
            .chamfer(1.0)
        )
        positives.append(boss_wp.val().translate((0, 0, P.RAIL_H_MM - 0.5)))

# 7) Steering servo mount, front center: SOLID pedestal block rising from the
#    skid (no bridging), servo long axis transverse (along y); two side-tab
#    slots 4.5 mm wide at 49 mm spacing are cut through the block top below.
#    The servo flange seats on the block top (z=27) and the body stands up
#    (envelope top ~67 < 120). Servo fore/aft location centered on x=160.
# The block starts 1 mm ahead of the front-crossmember face so it overlaps
# (fuses) the crossmember; it must still stay in front of the battery bay.
assert SERVO_BLOCK_X[0] >= CM_X["front"] + CM_T / 2.0 - 2.0
assert SERVO_BLOCK_X[0] >= TRAY_X1  # never intrude into the battery bay
positives.append(box(SERVO_BLOCK_X[0], SERVO_BLOCK_X[1],
                     -SERVO_BLOCK_Y, SERVO_BLOCK_Y, 0.0, SERVO_BLOCK_Z_TOP))

# ---------------------------------------------------------------------------
# Cutters (all subtracted from the fused positive solid)
# ---------------------------------------------------------------------------
cutters: list[cq.Solid] = []

# 4) Strap slots: 10 mm wide along x, through both side walls (DFM-3).
for sx_ in STRAP_X:
    cutters.append(box(sx_ - STRAP_W / 2.0, sx_ + STRAP_W / 2.0,
                       -(RAIL_OUT + 4.0), RAIL_OUT + 4.0,
                       STRAP_Z[0], STRAP_Z[1]))

# 6) Pivot-pin bores 3.2 mm along y (blind cap strictly INSIDE the riser,
#    open at the outer boss face; caps must never land exactly on a face).
for sx in (+AX, -AX):
    for s in (+1.0, -1.0):
        cutters.append(cyl((sx, s * (BOSS_IN[0] + 1.5), PIN_Z),
                           (sx, s * (BOSS_OUT[1] + 4.5), PIN_Z),
                           PIN_BORE_D / 2.0))

# 6) Shock-eye bores 3.2 mm along y at z=45 (through both tower faces).
for sx in (+AX, -AX):
    for s in (+1.0, -1.0):
        cutters.append(cyl((sx, s * (TOWER_Y[0] - 4.0), SHOCK_BORE_Z),
                           (sx, s * (TOWER_Y[1] + 4.0), SHOCK_BORE_Z),
                           SHOCK_BORE_D / 2.0))

# 8) Motor saddle anchor holes M3 clearance along y (into the rail cavity,
#    vented; DFM-6) — two per saddle at 60 mm spacing.
for ax in (+AX, -AX):
    strain_x = ax - (1.0 if ax > 0 else -1.0) * STRAIN_DX
    for s in (+1.0, -1.0):
        for dx in (+SADDLE_HOLE_DX, -SADDLE_HOLE_DX):
            # Start strictly INSIDE the rail cavity so the hole vents cleanly
            # (never land the cutter cap exactly on the cavity wall face).
            cutters.append(cyl((ax + dx, s * (RAIL_IN + RAIL_WALL + 2.0), 12.0),
                               (ax + dx, s * (RAIL_OUT + SADDLE_T + 3.0), 12.0),
                               M3 / 2.0))
        # 8) cable channel: radius-6 cylinder along x, opens the boss top.
        # Centered EXACTLY on the strain boss mid-y so the cut leaves no
        # sliver strip at the boss edge (channel y half-reach at the boss top
        # must exceed the boss half-width on BOTH sides).
        boss_y_mid = (RAIL_OUT - 0.4 + RAIL_OUT + SADDLE_T) / 2.0
        cutters.append(cyl((strain_x - 12.0, s * boss_y_mid, 16.0),
                           (strain_x + 12.0, s * boss_y_mid, 16.0),
                           STRAIN_R))

# 9) Bridge-boss holes M3 clearance along z (boss + rail top wall -> cavity).
for bx in (+BRIDGE_X, -BRIDGE_X):
    for by in (+Y_RAIL, -Y_RAIL):
        cutters.append(cyl((bx, by, P.RAIL_H_MM + BRIDGE_T + 1.0),
                           (bx, by, 17.0), M3 / 2.0))

# 7) Servo side-tab slots: two vertical slots 4.5 mm wide (along y) x
#    SERVO_SLOT_LEN (along x), cut DOWN from the block top at 49 mm spacing.
#    Vertical (z) screw axis -> slots are through the mounting surface; they
#    stop 10 mm into the solid block (no printed threads, contract rule 10).
#    Servo long axis along y, centered x=160 (DFM-4, DFM-7).
SERVO_SLOT_CX = 160.0
SERVO_SLOT_ZBOT = SERVO_BLOCK_Z_TOP - 10.0
for s in (+1.0, -1.0):
    cutters.append(box(SERVO_SLOT_CX - SERVO_SLOT_LEN / 2.0,
                       SERVO_SLOT_CX + SERVO_SLOT_LEN / 2.0,
                       s * SERVO_TAB_SPACING / 2.0 - SERVO_SLOT_W / 2.0,
                       s * SERVO_TAB_SPACING / 2.0 + SERVO_SLOT_W / 2.0,
                       SERVO_SLOT_ZBOT, SERVO_BLOCK_Z_TOP + 1.0))

# ---------------------------------------------------------------------------
# Fuse and detail
# ---------------------------------------------------------------------------
part = reduce(lambda a, b: a.fuse(b), positives)
part = part.clean()
for c in cutters:
    part = part.cut(c)
part = part.clean()
# Note: bridge-boss vertical-edge chamfers are applied at boss creation
# (stable selector on a standalone boss); pivot/shock bosses get chamfered
# tops from their extruded profiles. No brittle post-hoc edge reselection.

# ---------------------------------------------------------------------------
# Shape checks (contract acceptance 3) and datum checks
# ---------------------------------------------------------------------------
assert len(part.Solids()) == 1, "must be a single positive solid"
assert part.isValid(), "B-Rep must be valid"

bb = part.BoundingBox()
dims = (bb.xlen, bb.ylen, bb.zlen)
assert dims[0] <= P.OVERALL_LENGTH_TARGET_MM + 1e-6, "overall length exceeded"
assert dims[1] <= P.OVERALL_WIDTH_MAX_MM + 1e-6, "overall width exceeded"
assert bb.zmin >= -1e-6, "nothing may sink below the z=0 bed datum"
assert bb.zmax <= 120.0, "contract z max exceeded"
assert bb.ymax <= P.WHEEL_Y_MM and bb.ymin >= -P.WHEEL_Y_MM, \
    "chassis must stay inboard of the wheel center planes"

# ---------------------------------------------------------------------------
# Deterministic exports
# ---------------------------------------------------------------------------
EXPORT_DIR = HERE / "exports"
EXPORT_DIR.mkdir(exist_ok=True)
STEP_PATH = EXPORT_DIR / "DRAFT-chassis-printed.step"
STL_PATH = EXPORT_DIR / "DRAFT-chassis-printed.stl"
STL_TOL = 0.1  # mm, contract mesh tolerance

cq.exporters.export(part, str(STEP_PATH))
cq.exporters.export(part, str(STL_PATH), tolerance=STL_TOL, angularTolerance=0.1)

# ---------------------------------------------------------------------------
# Compact summary
# ---------------------------------------------------------------------------
vol_cm3 = part.Volume() / 1000.0
try:
    cq_version = importlib.metadata.version("cadquery")
except importlib.metadata.PackageNotFoundError:
    cq_version = getattr(cq, "__version__", "unknown")

print("MM-TOY-002 CHASSIS_PRINTED v0.4.0 v1 (DRAFT)")
print(f"toolchain: python {sys.version.split()[0]}, cadquery {cq_version}")
print(f"bbox min: ({bb.xmin:.3f}, {bb.ymin:.3f}, {bb.zmin:.3f}) mm")
print(f"bbox max: ({bb.xmax:.3f}, {bb.ymax:.3f}, {bb.zmax:.3f}) mm")
print(f"bbox size: {dims[0]:.3f} x {dims[1]:.3f} x {dims[2]:.3f} mm")
print(f"volume: {vol_cm3:.1f} cm3")
print(f"solids: {len(part.Solids())} | isValid: {part.isValid()}")
print(f"exports: {STEP_PATH.name}, {STL_PATH.name} (STL tolerance {STL_TOL} mm)")
