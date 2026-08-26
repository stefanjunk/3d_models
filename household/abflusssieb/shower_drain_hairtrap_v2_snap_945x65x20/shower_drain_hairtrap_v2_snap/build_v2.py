from pathlib import Path
import math
import cadquery as cq

OUT = Path(__file__).resolve().parent

# ============================================================
# PARAMETRIC TARGET GEOMETRY (mm)
# ============================================================
TOTAL_LENGTH = 945.0
TOTAL_WIDTH = 65.0
TOTAL_HEIGHT = 20.0
DECK_COUNT = 4
DECK_LENGTH = TOTAL_LENGTH / DECK_COUNT       # 236.25
DECK_T = 5.0
WALL_VISIBLE_H = TOTAL_HEIGHT - DECK_T        # 15.0
WALL_T = 3.0

# Drain / hair catcher: 4 fields per deck = 16 independent fields.
CATCHER_COUNT_PER_DECK = 4
CATCHER_D = 46.0
CATCHER_R = CATCHER_D / 2
CATCHER_EDGE_CENTER = 29.0
CATCHER_SPACING = (DECK_LENGTH - 2*CATCHER_EDGE_CENTER) / (CATCHER_COUNT_PER_DECK - 1)
CATCHER_XS = [CATCHER_EDGE_CENTER + i*CATCHER_SPACING for i in range(CATCHER_COUNT_PER_DECK)]
CATCHER_Y = TOTAL_WIDTH / 2

RECESS_DEPTH = 1.10
RECESS_FLOOR_Z = DECK_T - RECESS_DEPTH
HOLE_D = 3.20
HOLE_PITCH = 4.60
HOLE_FIELD_R = 20.50

RIB_W = 1.40
RIB_H = 0.75
RIB_COUNT = 5
RIB_INNER_R = 5.2
RIB_OUTER_R = 20.2
RIB_SWEEP = math.radians(108)
RIB_STEPS = 18
CENTER_BOSS_R = 3.2

# Longitudinal T slots in underside of deck.
# Female slot is deliberately open to the build plate; its 5.2 mm roof is a short bridge, no support needed.
RAIL_CENTER_FROM_EDGE = 3.60
SLOT_OPEN_W = 2.80
SLOT_OPEN_H = 1.45
SLOT_HEAD_W = 5.20
SLOT_HEAD_Z0 = 1.20
SLOT_HEAD_H = 1.75

# Male T rail pads on wall (clearance to female slot).
RAIL_STEM_W = 2.20
RAIL_STEM_H = 1.38
RAIL_HEAD_W = 4.55
RAIL_HEAD_Z0 = WALL_VISIBLE_H + 1.12
RAIL_HEAD_H = 1.48
RAIL_PAD_L = 32.0
RAIL_END_MARGIN = 12.0

# Deck-to-deck alignment tongues. These prevent longitudinal drift;
# side walls spanning seams carry the bending load.
TAB_L = 5.5
TAB_W = 7.0
TAB_H = 2.35
TAB_CLEAR = 0.28
TAB_YS = [17.0, TOTAL_WIDTH/2, TOTAL_WIDTH-17.0]

# Side wall segmentation: joints are offset half a deck from deck seams.
WALL_HALF_L = DECK_LENGTH/2                 # 118.125
WALL_BRIDGE_L = DECK_LENGTH                 # 236.25


def single_catcher_points():
    pts = []
    rh = HOLE_PITCH * math.sqrt(3) / 2
    for row in range(-12, 13):
        yy = row * rh
        xoff = (abs(row) % 2) * HOLE_PITCH / 2
        for col in range(-12, 13):
            xx = col * HOLE_PITCH + xoff
            if xx*xx + yy*yy <= HOLE_FIELD_R*HOLE_FIELD_R:
                pts.append((xx, yy))
    return pts


def panel_hole_points():
    base = single_catcher_points()
    pts=[]
    for cx in CATCHER_XS:
        for xx,yy in base:
            pts.append((cx+xx, CATCHER_Y+yy))
    return pts


def spiral_band_points(phase_rad):
    center=[]
    for i in range(RIB_STEPS+1):
        t=i/RIB_STEPS
        a=phase_rad + t*RIB_SWEEP
        r=RIB_INNER_R + t*(RIB_OUTER_R-RIB_INNER_R)
        center.append((r*math.cos(a), r*math.sin(a)))
    left=[]; right=[]
    for i,(x,y) in enumerate(center):
        i0=max(i-1,0); i1=min(i+1,RIB_STEPS)
        dx=center[i1][0]-center[i0][0]
        dy=center[i1][1]-center[i0][1]
        L=math.hypot(dx,dy)
        nx,ny=-dy/L,dx/L
        left.append((x+nx*RIB_W/2,y+ny*RIB_W/2))
        right.append((x-nx*RIB_W/2,y-ny*RIB_W/2))
    return left + list(reversed(right))


def female_rail_slot(center_y):
    # underside opening
    opening = (cq.Workplane('XY')
               .box(DECK_LENGTH+0.2, SLOT_OPEN_W, SLOT_OPEN_H+0.05,
                    centered=(False,True,False))
               .translate((-0.1,center_y,-0.05)))
    # wider T cavity above it
    head = (cq.Workplane('XY')
            .box(DECK_LENGTH+0.2, SLOT_HEAD_W, SLOT_HEAD_H,
                 centered=(False,True,False))
            .translate((-0.1,center_y,SLOT_HEAD_Z0)))
    return opening.union(head)


def make_deck_core():
    deck = cq.Workplane('XY').box(DECK_LENGTH, TOTAL_WIDTH, DECK_T, centered=(False,False,False))

    # Two longitudinal underside T-slots for snap/slide walls.
    for cy in (RAIL_CENTER_FROM_EDGE, TOTAL_WIDTH-RAIL_CENTER_FROM_EDGE):
        deck = deck.cut(female_rail_slot(cy))

    # Circular shallow catcher recesses.
    centers=[(x,CATCHER_Y) for x in CATCHER_XS]
    recess=(cq.Workplane('XY', origin=(0,0,RECESS_FLOOR_Z))
            .pushPoints(centers).circle(CATCHER_R).extrude(RECESS_DEPTH+0.05))
    deck=deck.cut(recess)

    # All sieve holes as one compound operation.
    holes=(cq.Workplane('XY', origin=(0,0,-0.05))
           .pushPoints(panel_hole_points()).circle(HOLE_D/2).extrude(DECK_T+0.10))
    deck=deck.cut(holes)

    # Recessed swirl ribs; their tops remain below surrounding deck surface.
    for cx in CATCHER_XS:
        for k in range(RIB_COUNT):
            pts=spiral_band_points(k*2*math.pi/RIB_COUNT)
            rib=(cq.Workplane('XY', origin=(cx,CATCHER_Y,RECESS_FLOOR_Z))
                 .polyline(pts).close().extrude(RIB_H))
            deck=deck.union(rib,clean=False)
        boss=(cq.Workplane('XY', origin=(cx,CATCHER_Y,RECESS_FLOOR_Z))
              .circle(CENTER_BOSS_R).extrude(RIB_H))
        deck=deck.union(boss,clean=False)
    try:
        deck=deck.clean()
    except Exception:
        pass
    return deck


def add_right_tabs(deck):
    for yy in TAB_YS:
        tab=(cq.Workplane('XY')
             .box(TAB_L,TAB_W,TAB_H,centered=(False,True,False))
             .translate((DECK_LENGTH,yy,0)))
        deck=deck.union(tab,clean=False)
    return deck


def cut_left_tab_pockets(deck):
    for yy in TAB_YS:
        pocket=(cq.Workplane('XY')
                .box(TAB_L+TAB_CLEAR,TAB_W+TAB_CLEAR,TAB_H+TAB_CLEAR,
                     centered=(False,True,False))
                .translate((0,yy,-0.05)))
        deck=deck.cut(pocket)
    return deck


def make_deck(kind):
    # left: male on right; middle: female left + male right; right: female left.
    assert kind in ('left','middle','right')
    d=make_deck_core()
    if kind in ('middle','right'):
        d=cut_left_tab_pockets(d)
    if kind in ('left','middle'):
        d=add_right_tabs(d)
    try:
        d=d.clean()
    except Exception:
        pass
    return d


def rail_pad_starts(length):
    # Fewer discontinuous pads -> much less sliding friction than one 236 mm continuous rail.
    count = 2 if length < 150 else 5
    usable = length - 2*RAIL_END_MARGIN - RAIL_PAD_L
    if count == 1:
        return [(length-RAIL_PAD_L)/2]
    step = usable/(count-1)
    return [RAIL_END_MARGIN+i*step for i in range(count)]


def make_wall(length):
    # Generic LEFT-side assembly orientation: outside face at y=0, rail points inward (+Y).
    wall=cq.Workplane('XY').box(length,WALL_T,WALL_VISIBLE_H,centered=(False,False,False))
    center_y=RAIL_CENTER_FROM_EDGE
    for x0 in rail_pad_starts(length):
        stem=(cq.Workplane('XY')
              .box(RAIL_PAD_L,RAIL_STEM_W,RAIL_STEM_H,
                   centered=(False,True,False))
              .translate((x0,center_y,WALL_VISIBLE_H)))
        head=(cq.Workplane('XY')
              .box(RAIL_PAD_L,RAIL_HEAD_W,RAIL_HEAD_H,
                   centered=(False,True,False))
              .translate((x0,center_y,RAIL_HEAD_Z0)))
        wall=wall.union(stem,clean=False).union(head,clean=False)
    try:
        wall=wall.clean()
    except Exception:
        pass
    return wall


def wall_print_orientation(wall):
    # Lay the large outside face on the print bed: support-free and dimensionally stable.
    return wall.rotate((0,0,0),(1,0,0),90)


def make_rail_fit_top():
    L=65.0
    d=cq.Workplane('XY').box(L,TOTAL_WIDTH,DECK_T,centered=(False,False,False))
    for cy in (RAIL_CENTER_FROM_EDGE,TOTAL_WIDTH-RAIL_CENTER_FROM_EDGE):
        opening=(cq.Workplane('XY')
                 .box(L+0.2,SLOT_OPEN_W,SLOT_OPEN_H+0.05,centered=(False,True,False))
                 .translate((-0.1,cy,-0.05)))
        head=(cq.Workplane('XY')
              .box(L+0.2,SLOT_HEAD_W,SLOT_HEAD_H,centered=(False,True,False))
              .translate((-0.1,cy,SLOT_HEAD_Z0)))
        d=d.cut(opening.union(head))
    return d


def make_function_tile():
    L=65.0
    d=cq.Workplane('XY').box(L,TOTAL_WIDTH,DECK_T,centered=(False,False,False))
    cx=L/2; cy=TOTAL_WIDTH/2
    recess=(cq.Workplane('XY',origin=(0,0,RECESS_FLOOR_Z))
            .center(cx,cy).circle(CATCHER_R).extrude(RECESS_DEPTH+0.05))
    d=d.cut(recess)
    pts=[(cx+xx,cy+yy) for xx,yy in single_catcher_points()]
    holes=(cq.Workplane('XY',origin=(0,0,-0.05))
           .pushPoints(pts).circle(HOLE_D/2).extrude(DECK_T+0.1))
    d=d.cut(holes)
    for k in range(RIB_COUNT):
        pts2=spiral_band_points(k*2*math.pi/RIB_COUNT)
        rib=(cq.Workplane('XY',origin=(cx,cy,RECESS_FLOOR_Z))
             .polyline(pts2).close().extrude(RIB_H))
        d=d.union(rib,clean=False)
    d=d.union(cq.Workplane('XY',origin=(cx,cy,RECESS_FLOOR_Z)).circle(CENTER_BOSS_R).extrude(RIB_H),clean=False)
    try: d=d.clean()
    except Exception: pass
    return d


def export(shape,stem,step=True):
    cq.exporters.export(shape,str(OUT/f'{stem}.stl'),tolerance=0.10,angularTolerance=0.20)
    if step:
        cq.exporters.export(shape,str(OUT/f'{stem}.step'))


def write_readme():
    hpc=len(single_catcher_points())
    catchers=CATCHER_COUNT_PER_DECK*DECK_COUNT
    holes=hpc*catchers
    gross=holes*math.pi*(HOLE_D/2)**2
    pct=gross/(TOTAL_LENGTH*TOTAL_WIDTH)*100
    txt=f'''# Shower Drain Hair Trap V2 – printable plug-together version

## Exact installed envelope
- Length: **{TOTAL_LENGTH:.2f} mm**
- Width: **{TOTAL_WIDTH:.2f} mm**
- Height: **{TOTAL_HEIGHT:.2f} mm**

## FDM-oriented decomposition
The inverted U-profile is no longer printed as one difficult piece.

1. **Top/deck plates** print flat, underside on the build plate and visible surface upward.
2. **Side walls** print lying on their large outside face.
3. Side-wall joints are offset by half a deck length, so each 236.25 mm bridge wall spans one deck seam.
4. Small underside deck tabs prevent longitudinal drift while the side walls carry the seam mechanically.

This avoids large support structures, keeps all sieve holes vertical/circular and keeps build-plate texture off the visible top surface.

## Drainage
- Decks: {DECK_COUNT} × {DECK_LENGTH:.3f} mm
- Hair catcher fields: {catchers} total ({CATCHER_COUNT_PER_DECK} per deck)
- Catcher diameter: {CATCHER_D:.1f} mm
- Holes per catcher: {hpc}
- Total sieve holes: {holes}
- Hole diameter: {HOLE_D:.2f} mm
- Gross open hole area: ~{gross:.0f} mm² ({pct:.1f}% of total top footprint)
- 5 recessed swirl ribs per field; rib tops remain below the surrounding walking surface.

## Side wall / rail system
- Visible wall height: {WALL_VISIBLE_H:.1f} mm
- Wall thickness: {WALL_T:.1f} mm
- T-slot is open on the underside of the deck and only requires a ~{SLOT_HEAD_W:.1f} mm bridge when printing.
- Male rails are discontinuous pads to reduce sliding friction and sensitivity to PETG warping.

### Required side-wall quantities
The same wall geometry is used on left and right; rotate it 180° around Z for the opposite side during assembly.
- `wall_half_print.stl`: **4 copies** total
- `wall_bridge_print.stl`: **6 copies** total

Per side the order is:
`118.125 + 236.25 + 236.25 + 236.25 + 118.125 = 945 mm`

Wall joints occur at the middle of deck plates, not at the deck seams.

## Deck quantities
- `deck_left.stl`: 1
- `deck_middle.stl`: 2
- `deck_right.stl`: 1

## Test parts
- `rail_fit_top.stl` + `rail_fit_wall_print.stl`: verify T-rail clearance before the full print.
- `functional_test_tile.stl`: one full 46 mm catcher field for water/hair testing.

## Recommended PETG starting settings
- 0.20 mm layer height
- 4–5 walls
- 5–6 top/bottom layers
- 25–35% infill for deck plates
- no supports intended
- print deck plates exactly as exported
- print wall STLs exactly as exported (`*_print` files already lie on their outer face)

## Parametric source
`build_v2.py` contains all main dimensions, clearances, hole/rib geometry and decomposition parameters at the top of the file.
'''
    (OUT/'README.md').write_text(txt)


def main():
    print('V2 exact envelope',TOTAL_LENGTH,TOTAL_WIDTH,TOTAL_HEIGHT)
    print('Deck length',DECK_LENGTH,'catcher centers',CATCHER_XS)
    print('holes/catcher',len(single_catcher_points()),'total holes',len(single_catcher_points())*16)

    print('Building shared deck core...')
    core=make_deck_core()
    print('Adding seam features...')
    left=add_right_tabs(core)
    mid=add_right_tabs(cut_left_tab_pockets(core))
    right=cut_left_tab_pockets(core)
    try:
        left=left.clean(); mid=mid.clean(); right=right.clean()
    except Exception:
        pass
    export(left,'deck_left')
    export(mid,'deck_middle')
    export(right,'deck_right')

    print('Building walls...')
    half=make_wall(WALL_HALF_L)
    bridge=make_wall(WALL_BRIDGE_L)
    # STEP in assembly orientation, STL in print orientation.
    cq.exporters.export(half,str(OUT/'wall_half.step'))
    cq.exporters.export(bridge,str(OUT/'wall_bridge.step'))
    cq.exporters.export(wall_print_orientation(half),str(OUT/'wall_half_print.stl'),tolerance=0.10,angularTolerance=0.20)
    cq.exporters.export(wall_print_orientation(bridge),str(OUT/'wall_bridge_print.stl'),tolerance=0.10,angularTolerance=0.20)

    print('Building tests...')
    fit_top=make_rail_fit_top(); export(fit_top,'rail_fit_top')
    fit_wall=make_wall(65.0)
    cq.exporters.export(wall_print_orientation(fit_wall),str(OUT/'rail_fit_wall_print.stl'),tolerance=0.10,angularTolerance=0.20)
    func=make_function_tile(); export(func,'functional_test_tile')

    # Assembly reference: 4 decks at z=15; side-wall pieces offset by half a deck.
    asm=cq.Assembly()
    decks=[left,mid,mid,right]
    for i,d in enumerate(decks):
        asm.add(d,name=f'deck_{i+1}',loc=cq.Location(cq.Vector(i*DECK_LENGTH,0,WALL_VISIBLE_H)))

    wall_lengths=[WALL_HALF_L,WALL_BRIDGE_L,WALL_BRIDGE_L,WALL_BRIDGE_L,WALL_HALF_L]
    starts=[0,WALL_HALF_L,WALL_HALF_L+WALL_BRIDGE_L,WALL_HALF_L+2*WALL_BRIDGE_L,WALL_HALF_L+3*WALL_BRIDGE_L]
    for side in ('left','right'):
        for i,(L,x0) in enumerate(zip(wall_lengths,starts)):
            w=make_wall(L)
            if side=='left':
                loc=cq.Location(cq.Vector(x0,0,0))
            else:
                # Rotate generic left wall 180° around Z and translate so outer face becomes y=65.
                loc=cq.Location(cq.Vector(x0+L,TOTAL_WIDTH,0),cq.Vector(0,0,1),180)
            asm.add(w,name=f'{side}_wall_{i+1}',loc=loc)
    asm.save(str(OUT/'assembly_reference.step'))

    write_readme()
    print('Done')

if __name__=='__main__':
    main()
