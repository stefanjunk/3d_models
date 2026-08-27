from pathlib import Path
import math
import cadquery as cq

OUT = Path(__file__).resolve().parent

# -------------------- TARGET PARAMETERS (mm) --------------------
TOTAL_LENGTH = 945.0
TOTAL_WIDTH = 65.0
TOTAL_HEIGHT = 20.0
SEGMENT_COUNT = 4
SEGMENT_LENGTH = TOTAL_LENGTH / SEGMENT_COUNT

# Inverted U-profile shell
TOP_T = 4.2
SIDE_WALL_T = 3.0
SIDE_WALL_H = TOTAL_HEIGHT - TOP_T
CORNER_R = 1.6

# Drain funnel / catcher geometry
CATCHER_D = 42.0
CATCHER_R = CATCHER_D / 2.0
FUNNEL_DEPTH = 2.2
FUNNEL_ENTRY_R = 21.0      # visible upper funnel radius
FUNNEL_FLOOR_R = 17.5      # lower flat capture area radius; outer ring stays hole-free
FUNNEL_FLOOR_Z = TOTAL_HEIGHT - FUNNEL_DEPTH
HOLE_D = 2.6               # reduced to better retain hair
HOLE_PITCH = 4.0
HOLE_FIELD_R = 14.0        # keeps a solid rim between sieve and funnel wall
CATCHER_XS = [29.5, 88.75, 147.5, 206.75]  # four per segment
CATCHER_YS = [TOTAL_WIDTH / 2.0]

# Swirl hair-guiding ribs — start farther out, curl inward
RIB_W = 1.8
RIB_H = 0.95
RIB_COUNT = 5
RIB_START_R = 16.6
RIB_END_R = 7.4
RIB_SWEEP = math.radians(132)
RIB_STEPS = 24
CENTER_BOSS_R = 3.8

# Loose internal seam keys keep exact outside dimensions
KEY_SLOT_DEPTH = 13.0
KEY_W = 10.0
KEY_H = 2.8
KEY_CLEARANCE = 0.20
KEY_Z0 = TOTAL_HEIGHT - TOP_T + 0.7
KEY_YS = [14.0, TOTAL_WIDTH / 2.0, TOTAL_WIDTH - 14.0]
KEY_L = (2 * KEY_SLOT_DEPTH) - 0.35


def _single_catcher_points():
    pts = []
    row_h = HOLE_PITCH * math.sqrt(3) / 2.0
    for row in range(-10, 11):
        yy = row * row_h
        xoff = (abs(row) % 2) * HOLE_PITCH / 2.0
        for col in range(-10, 11):
            xx = col * HOLE_PITCH + xoff
            if xx * xx + yy * yy <= HOLE_FIELD_R * HOLE_FIELD_R:
                pts.append((xx, yy))
    return pts


def screen_points():
    base = _single_catcher_points()
    pts = []
    for cx in CATCHER_XS:
        for cy in CATCHER_YS:
            for xx, yy in base:
                pts.append((cx + xx, cy + yy))
    return pts


def spiral_band_points(phase_rad):
    # Start farther outward and curl inward.
    center = []
    for i in range(RIB_STEPS + 1):
        t = i / RIB_STEPS
        a = phase_rad + t * RIB_SWEEP
        r = RIB_START_R + t * (RIB_END_R - RIB_START_R)
        center.append((r * math.cos(a), r * math.sin(a)))

    left, right = [], []
    for i, (x, y) in enumerate(center):
        i0 = max(i - 1, 0)
        i1 = min(i + 1, RIB_STEPS)
        dx = center[i1][0] - center[i0][0]
        dy = center[i1][1] - center[i0][1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        left.append((x + nx * RIB_W / 2.0, y + ny * RIB_W / 2.0))
        right.append((x - nx * RIB_W / 2.0, y - ny * RIB_W / 2.0))
    return left + list(reversed(right))


def make_base_u(length=SEGMENT_LENGTH):
    top = (cq.Workplane("XY")
           .box(length, TOTAL_WIDTH, TOP_T, centered=(False, False, False))
           .translate((0, 0, TOTAL_HEIGHT - TOP_T)))
    left_wall = (cq.Workplane("XY")
                 .box(length, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False)))
    right_wall = (cq.Workplane("XY")
                  .box(length, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False))
                  .translate((0, TOTAL_WIDTH - SIDE_WALL_T, 0)))
    body = top.union(left_wall).union(right_wall)
    try:
        body = body.edges("|Z").fillet(CORNER_R)
    except Exception:
        pass
    return body


def make_funnel_tool(cx, cy):
    # Shallow funnel: wider at the top, narrower at the lower capture floor.
    wp = cq.Workplane("XY", origin=(cx, cy, TOTAL_HEIGHT))
    funnel = (wp.circle(FUNNEL_ENTRY_R)
              .workplane(offset=-FUNNEL_DEPTH)
              .circle(FUNNEL_FLOOR_R)
              .loft(combine=True, ruled=False))
    return funnel


def cut_key_slots(panel, left=False, right=False):
    for yy in KEY_YS:
        if left:
            slot = (cq.Workplane("XY")
                    .box(KEY_SLOT_DEPTH + KEY_CLEARANCE, KEY_W + KEY_CLEARANCE, KEY_H + KEY_CLEARANCE,
                         centered=(False, True, False))
                    .translate((0, yy, KEY_Z0)))
            panel = panel.cut(slot)
        if right:
            slot = (cq.Workplane("XY")
                    .box(KEY_SLOT_DEPTH + KEY_CLEARANCE, KEY_W + KEY_CLEARANCE, KEY_H + KEY_CLEARANCE,
                         centered=(False, True, False))
                    .translate((SEGMENT_LENGTH - KEY_SLOT_DEPTH - KEY_CLEARANCE, yy, KEY_Z0)))
            panel = panel.cut(slot)
    return panel


def add_catchers(panel, centers):
    # One funnel cut per catcher. Looping is okay at this count and keeps lofts stable.
    for cx, cy in centers:
        panel = panel.cut(make_funnel_tool(cx, cy))

    holes = (cq.Workplane("XY", origin=(0, 0, TOTAL_HEIGHT - TOP_T - 0.05))
             .pushPoints(screen_points()).circle(HOLE_D / 2.0).extrude(TOP_T + 0.10))
    panel = panel.cut(holes)

    for cx, cy in centers:
        for k in range(RIB_COUNT):
            pts = spiral_band_points(k * 2.0 * math.pi / RIB_COUNT)
            rib = (cq.Workplane("XY", origin=(cx, cy, FUNNEL_FLOOR_Z))
                   .polyline(pts).close().extrude(RIB_H))
            panel = panel.union(rib, clean=False)
        boss = (cq.Workplane("XY", origin=(cx, cy, FUNNEL_FLOOR_Z))
                .circle(CENTER_BOSS_R).extrude(RIB_H))
        panel = panel.union(boss, clean=False)

    try:
        panel = panel.clean()
    except Exception:
        pass
    return panel


def make_panel(panel_type: str):
    assert panel_type in ("left", "mid_left", "mid_right", "right")
    panel = make_base_u()
    centers = [(x, y) for x in CATCHER_XS for y in CATCHER_YS]
    panel = add_catchers(panel, centers)
    panel = cut_key_slots(panel,
                          left=panel_type in ("mid_left", "mid_right", "right"),
                          right=panel_type in ("left", "mid_left", "mid_right"))
    return panel


def make_key():
    return cq.Workplane("XY").box(KEY_L, KEY_W, KEY_H, centered=(False, True, False))


def make_fit_coupon():
    return make_base_u(length=30.0)


def make_function_tile():
    length = 70.0
    tile = make_base_u(length=length)
    cx, cy = length / 2.0, TOTAL_WIDTH / 2.0
    tile = tile.cut(make_funnel_tool(cx, cy))
    pts = [(cx + xx, cy + yy) for xx, yy in _single_catcher_points()]
    holes = (cq.Workplane("XY", origin=(0, 0, TOTAL_HEIGHT - TOP_T - 0.05))
             .pushPoints(pts).circle(HOLE_D / 2.0).extrude(TOP_T + 0.10))
    tile = tile.cut(holes)
    for k in range(RIB_COUNT):
        pts2 = spiral_band_points(k * 2.0 * math.pi / RIB_COUNT)
        rib = (cq.Workplane("XY", origin=(cx, cy, FUNNEL_FLOOR_Z))
               .polyline(pts2).close().extrude(RIB_H))
        tile = tile.union(rib, clean=False)
    boss = (cq.Workplane("XY", origin=(cx, cy, FUNNEL_FLOOR_Z))
            .circle(CENTER_BOSS_R).extrude(RIB_H))
    tile = tile.union(boss, clean=False)
    try:
        tile = tile.clean()
    except Exception:
        pass
    return tile


def export_shape(shape, stem):
    cq.exporters.export(shape, str(OUT / f"{stem}.stl"), tolerance=0.10, angularTolerance=0.20)
    cq.exporters.export(shape, str(OUT / f"{stem}.step"))


def write_readme():
    holes_per_catcher = len(_single_catcher_points())
    total_catchers = len(CATCHER_XS) * len(CATCHER_YS) * SEGMENT_COUNT
    total_holes = holes_per_catcher * total_catchers
    gross_open_area = total_holes * math.pi * (HOLE_D / 2.0) ** 2
    effective_open_area = gross_open_area - total_catchers * RIB_COUNT * (RIB_W * (RIB_START_R - RIB_END_R) * 0.75)
    txt = f"""# Shower drain hair trap – exact 945 × 65 × 20 mm, inverted U-profile, funnel catcher variant

Generated parametrically from `build_shower_drain_hairtrap_945x65_funnel.py`.

## Key geometry
- Exact assembled outer size: {TOTAL_LENGTH:.1f} × {TOTAL_WIDTH:.1f} × {TOTAL_HEIGHT:.1f} mm
- Segments: {SEGMENT_COUNT}
- Segment outer size: {SEGMENT_LENGTH:.3f} × {TOTAL_WIDTH:.1f} × {TOTAL_HEIGHT:.1f} mm
- Cross-section: inverted U-profile (open bottom)
- Top plate thickness: {TOP_T:.1f} mm
- Side wall thickness: {SIDE_WALL_T:.1f} mm
- Side wall height below top plate: {SIDE_WALL_H:.1f} mm

## Drainage / hair-catch concept
- 4 funnel catchers per segment, 1 row centered across the width
- Total funnel catchers: {total_catchers}
- Funnel entry diameter: {2*FUNNEL_ENTRY_R:.1f} mm
- Funnel floor diameter: {2*FUNNEL_FLOOR_R:.1f} mm
- Funnel depth: {FUNNEL_DEPTH:.1f} mm
- Hole-free outer rim inside each funnel: {FUNNEL_FLOOR_R - HOLE_FIELD_R:.1f} mm radial margin before the sieve starts
- Holes per catcher: {holes_per_catcher}
- Total holes: {total_holes}
- Hole diameter: {HOLE_D:.1f} mm
- Gross open hole area: ~{gross_open_area:.0f} mm²
- Estimated effective open area after swirl ribs: ~{effective_open_area:.0f} mm²
- 5 swirl ribs per catcher, beginning farther outward and curling inward for stronger hair guidance

## Joining strategy
- Exact outside dimensions are preserved by using loose internal joiner keys instead of protruding tabs.
- Each seam uses 3 keys.
- Included key part: `joiner_key.stl`
- Included 12-key batch: `joiner_keys_12x.stl`

## Files
- `panel_left.stl`, `panel_mid_left.stl`, `panel_mid_right.stl`, `panel_right.stl`
- `joiner_key.stl`, `joiner_keys_12x.stl`
- `fit_coupon.stl`
- `functional_test_tile_70mm.stl`
- STEP exports and `assembly_reference.step`

## Printing notes
- Recommended material: PETG
- User-requested print strategy: upside down with support
- Start with the `functional_test_tile_70mm.stl` to validate support scarring, funnel cleanup, and hair retention before printing all 4 segments
"""
    (OUT / "README.md").write_text(txt)


def main():
    print(f"Segment size: {SEGMENT_LENGTH:.3f} x {TOTAL_WIDTH:.3f} x {TOTAL_HEIGHT:.3f} mm")
    print(f"Holes per catcher: {len(_single_catcher_points())}; total catchers: {len(CATCHER_XS)*len(CATCHER_YS)*SEGMENT_COUNT}")

    panel_names = ("left", "mid_left", "mid_right", "right")
    panels = {}
    for name in panel_names:
        print("Building", name)
        p = make_panel(name)
        panels[name] = p
        export_shape(p, f"panel_{name}")

    key = make_key()
    export_shape(key, "joiner_key")

    key_batch = None
    for row in range(3):
        for col in range(4):
            k = make_key().translate((col * (KEY_L + 4.0), row * 16.0, 0))
            key_batch = k if key_batch is None else key_batch.union(k, clean=False)
    cq.exporters.export(key_batch, str(OUT / "joiner_keys_12x.stl"), tolerance=0.10, angularTolerance=0.20)

    coupon = make_fit_coupon()
    export_shape(coupon, "fit_coupon")

    tile = make_function_tile()
    export_shape(tile, "functional_test_tile_70mm")

    assembly = cq.Assembly()
    for i, name in enumerate(panel_names):
        assembly.add(panels[name], name=name, loc=cq.Location(cq.Vector(i * SEGMENT_LENGTH, 0, 0)))
    assembly.save(str(OUT / "assembly_reference.step"))

    write_readme()
    print("Done")


if __name__ == "__main__":
    main()
