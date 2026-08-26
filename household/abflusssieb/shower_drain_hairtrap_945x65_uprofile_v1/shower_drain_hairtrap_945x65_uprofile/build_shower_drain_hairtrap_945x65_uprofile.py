from pathlib import Path
import math
import cadquery as cq

OUT = Path(__file__).resolve().parent

# -------------------- TARGET PARAMETERS (mm) --------------------
TOTAL_LENGTH = 945.0
TOTAL_WIDTH = 65.0
TOTAL_HEIGHT = 20.0
SEGMENT_COUNT = 4
SEGMENT_LENGTH = TOTAL_LENGTH / SEGMENT_COUNT  # exact full assembled length

# U-profile / shell
TOP_T = 4.2
SIDE_WALL_T = 3.0
SIDE_WALL_H = TOTAL_HEIGHT - TOP_T
CORNER_R = 1.6

# Drain catcher geometry
CATCHER_D = 44.0
CATCHER_R = CATCHER_D / 2.0
RECESS_DEPTH = 1.1
RECESS_FLOOR_Z = TOTAL_HEIGHT - RECESS_DEPTH
HOLE_D = 3.2
HOLE_PITCH = 4.8
HOLE_FIELD_R = 19.5
CATCHER_XS = [48.0, SEGMENT_LENGTH / 2.0, SEGMENT_LENGTH - 48.0]
CATCHER_YS = [TOTAL_WIDTH / 2.0]

# Swirl hair-guiding ribs
RIB_W = 1.7
RIB_H = 0.8
RIB_COUNT = 5
RIB_INNER_R = 5.5
RIB_OUTER_R = 19.2
RIB_SWEEP = math.radians(108)
RIB_STEPS = 18
CENTER_BOSS_R = 3.5

# Loose joiner keys (keeps exact outside dimensions on all panels)
KEY_SLOT_DEPTH = 13.0
KEY_W = 10.0
KEY_H = 2.8
KEY_CLEARANCE = 0.20
KEY_Z0 = TOTAL_HEIGHT - TOP_T + 0.7  # start inside the top plate
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
    center = []
    for i in range(RIB_STEPS + 1):
        t = i / RIB_STEPS
        a = phase_rad + t * RIB_SWEEP
        r = RIB_INNER_R + t * (RIB_OUTER_R - RIB_INNER_R)
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
    # Top plate
    top = cq.Workplane("XY").box(length, TOTAL_WIDTH, TOP_T, centered=(False, False, False)).translate((0, 0, TOTAL_HEIGHT - TOP_T))
    # Two long side walls, open at the short ends
    left_wall = cq.Workplane("XY").box(length, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False)).translate((0, 0, 0))
    right_wall = cq.Workplane("XY").box(length, SIDE_WALL_T, SIDE_WALL_H, centered=(False, False, False)).translate((0, TOTAL_WIDTH - SIDE_WALL_T, 0))
    body = top.union(left_wall).union(right_wall)
    try:
        body = body.edges("|Z").fillet(CORNER_R)
    except Exception:
        pass
    return body


def cut_key_slots(panel, left=False, right=False):
    # Slots are cut into the solid top plate and open toward the end faces.
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


def make_panel(panel_type: str):
    assert panel_type in ("left", "mid_left", "mid_right", "right")
    panel = make_base_u()

    centers = [(x, y) for x in CATCHER_XS for y in CATCHER_YS]

    # Shallow recessed catcher zones from the top surface.
    recess_tool = (cq.Workplane("XY", origin=(0, 0, RECESS_FLOOR_Z))
                   .pushPoints(centers).circle(CATCHER_R).extrude(RECESS_DEPTH + 0.05))
    panel = panel.cut(recess_tool)

    # Sieve holes through the top plate.
    holes = (cq.Workplane("XY", origin=(0, 0, TOTAL_HEIGHT - TOP_T - 0.05))
             .pushPoints(screen_points()).circle(HOLE_D / 2.0).extrude(TOP_T + 0.10))
    panel = panel.cut(holes)

    # Key slots
    panel = cut_key_slots(panel,
                          left=panel_type in ("mid_left", "mid_right", "right"),
                          right=panel_type in ("left", "mid_left", "mid_right"))

    # Swirl ribs and center boss inside each catcher recess.
    for cx, cy in centers:
        for k in range(RIB_COUNT):
            pts = spiral_band_points(k * 2.0 * math.pi / RIB_COUNT)
            rib = (cq.Workplane("XY", origin=(cx, cy, RECESS_FLOOR_Z))
                   .polyline(pts).close().extrude(RIB_H))
            panel = panel.union(rib, clean=False)
        boss = (cq.Workplane("XY", origin=(cx, cy, RECESS_FLOOR_Z))
                .circle(CENTER_BOSS_R).extrude(RIB_H))
        panel = panel.union(boss, clean=False)

    try:
        panel = panel.clean()
    except Exception:
        pass
    return panel


def make_key():
    return cq.Workplane("XY").box(KEY_L, KEY_W, KEY_H, centered=(False, True, False))


def make_fit_coupon():
    return make_base_u(length=30.0)


def make_function_tile():
    length = 70.0
    tile = make_base_u(length=length)
    cx, cy = length / 2.0, TOTAL_WIDTH / 2.0
    recess_tool = (cq.Workplane("XY", origin=(0, 0, RECESS_FLOOR_Z))
                   .center(cx, cy).circle(CATCHER_R).extrude(RECESS_DEPTH + 0.05))
    tile = tile.cut(recess_tool)
    pts = [(cx + xx, cy + yy) for xx, yy in _single_catcher_points()]
    holes = (cq.Workplane("XY", origin=(0, 0, TOTAL_HEIGHT - TOP_T - 0.05))
             .pushPoints(pts).circle(HOLE_D / 2.0).extrude(TOP_T + 0.10))
    tile = tile.cut(holes)
    for k in range(RIB_COUNT):
        pts2 = spiral_band_points(k * 2.0 * math.pi / RIB_COUNT)
        rib = (cq.Workplane("XY", origin=(cx, cy, RECESS_FLOOR_Z))
               .polyline(pts2).close().extrude(RIB_H))
        tile = tile.union(rib, clean=False)
    boss = (cq.Workplane("XY", origin=(cx, cy, RECESS_FLOOR_Z))
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
    effective_open_area = gross_open_area - total_catchers * RIB_COUNT * (RIB_W * (RIB_OUTER_R - RIB_INNER_R) * 0.72)
    txt = f"""# Shower drain hair trap – exact 945 × 65 × 20 mm, inverted U-profile

Generated parametrically from `build_shower_drain_hairtrap_945x65_uprofile.py`.

## Key geometry
- Exact assembled outer size: {TOTAL_LENGTH:.1f} × {TOTAL_WIDTH:.1f} × {TOTAL_HEIGHT:.1f} mm
- Segments: {SEGMENT_COUNT}
- Segment outer size: {SEGMENT_LENGTH:.3f} × {TOTAL_WIDTH:.1f} × {TOTAL_HEIGHT:.1f} mm
- Cross-section: inverted U-profile (open bottom)
- Top plate thickness: {TOP_T:.1f} mm
- Side wall thickness: {SIDE_WALL_T:.1f} mm
- Side wall height below top plate: {SIDE_WALL_H:.1f} mm

## Drainage concept
- 3 catcher zones per segment, 1 row centered across the width
- Total catcher zones: {total_catchers}
- Catcher diameter: {CATCHER_D:.1f} mm
- Holes per catcher: {holes_per_catcher}
- Total holes: {total_holes}
- Hole diameter: {HOLE_D:.1f} mm
- Gross open hole area: ~{gross_open_area:.0f} mm²
- Estimated effective open area after swirl ribs: ~{effective_open_area:.0f} mm²
- 5 spiral ribs per catcher to guide hair into the local catcher instead of letting a few hairs block the entire cover

## Joining strategy
- Exact outside dimensions are preserved by using loose internal joiner keys instead of protruding tabs.
- Each seam uses 3 keys.
- Included key part: `joiner_key.stl`
- Included 12-key batch: `joiner_keys_12x.stl`

## Files
- `panel_left.stl`, `panel_mid_left.stl`, `panel_mid_right.stl`, `panel_right.stl`
- `joiner_key.stl`, `joiner_keys_12x.stl`
- `fit_coupon.stl` (30 mm cross-section test)
- `functional_test_tile_70mm.stl`
- STEP exports and `assembly_reference.step`

## Printing notes
- Recommended material: PETG
- Suggested starting point: 0.20 mm layer height, 4-5 walls, 6 top/bottom layers, 25-35% infill
- Print the panels with the open side downward / top surface upward
- Print 9-12 keys and dry-fit the assembly before the full install
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
