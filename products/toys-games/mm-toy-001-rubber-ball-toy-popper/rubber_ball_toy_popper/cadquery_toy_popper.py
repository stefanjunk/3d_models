"""Parametric, low-energy 20 mm rubber-ball toy popper.

The launcher uses a spring-driven air piston, a thumb-operated sear, and a
removable safety block. It is intentionally dimensioned around a weak spring
and a large soft projectile. All dimensions are millimetres.

Run with:
    python3 cadquery_toy_popper.py

CadQuery 2.8 or newer is recommended.
"""

from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq


# ---------------------------------------------------------------------------
# User-adjustable parameters
# ---------------------------------------------------------------------------

BALL_DIAMETER = 20.0
BARREL_CLEARANCE = 1.0
BALL_RETENTION_DIAMETER = 19.6

NOZZLE_DIAMETER = 0.4
FIT_CLEARANCE = 0.40
MIN_WALL = 2.4

CHAMBER_INNER_DIAMETER = 32.4
CHAMBER_WALL = 3.0
CHAMBER_LENGTH = 88.0
BODY_LENGTH = 145.0
BARREL_OUTER_DIAMETER = 29.0
AIR_PORT_DIAMETER = 5.0

PISTON_DIAMETER = 31.6
PISTON_THICKNESS = 10.0
PISTON_ROD_DIAMETER = 10.0
O_RING_ID = 28.0
O_RING_CROSS_SECTION = 2.0

# Use only a spring at or below this rate. The printed catch position limits
# compression to SPRING_TRAVEL even if a longer spring is installed.
SPRING_FREE_LENGTH = 74.0
SPRING_RATE_N_PER_MM = 0.25
SPRING_TRAVEL = 32.0
MAX_STORED_ENERGY_J = 0.15

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


# ---------------------------------------------------------------------------
# Derived dimensions and safety checks
# ---------------------------------------------------------------------------

BARREL_INNER_DIAMETER = BALL_DIAMETER + BARREL_CLEARANCE
CHAMBER_OUTER_DIAMETER = CHAMBER_INNER_DIAMETER + 2.0 * CHAMBER_WALL
PISTON_FRONT_REST = CHAMBER_LENGTH
PISTON_REAR_REST = PISTON_FRONT_REST - PISTON_THICKNESS
PISTON_FRONT_COCKED = PISTON_FRONT_REST - SPRING_TRAVEL
PISTON_REAR_COCKED = PISTON_REAR_REST - SPRING_TRAVEL
SPRING_COMPRESSED_LENGTH = PISTON_REAR_COCKED - 4.0
STORED_ENERGY_J = 0.5 * SPRING_RATE_N_PER_MM * SPRING_TRAVEL**2 / 1000.0
MAX_SPRING_FORCE_N = SPRING_RATE_N_PER_MM * SPRING_TRAVEL

assert MIN_WALL + 1e-9 >= 6.0 * NOZZLE_DIAMETER
assert BARREL_INNER_DIAMETER < 22.0, "Keep the bore specific to 20 mm soft balls."
assert BALL_RETENTION_DIAMETER >= 19.4, "Retention must not over-compress the ball."
assert STORED_ENERGY_J <= MAX_STORED_ENERGY_J, (
    f"Spring stores {STORED_ENERGY_J:.3f} J, above the {MAX_STORED_ENERGY_J:.3f} J cap."
)
assert SPRING_COMPRESSED_LENGTH > 35.0


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def cylinder_x(diameter: float, length: float, x: float = 0.0) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(x, 0.0, 0.0)).circle(diameter / 2.0).extrude(length)


def cylinder_y(
    diameter: float,
    length: float,
    x: float = 0.0,
    z: float = 0.0,
) -> cq.Workplane:
    return (
        cq.Workplane("XZ", origin=(x, 0.0, z))
        .circle(diameter / 2.0)
        .extrude(length / 2.0, both=True)
    )


def cylinder_z(
    diameter: float,
    length: float,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
) -> cq.Workplane:
    return cq.Workplane("XY", origin=(x, y, z)).circle(diameter / 2.0).extrude(length)


def centred_box(
    length: float,
    width: float,
    height: float,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(length, width, height)
        .translate((x, y, z))
    )


def bolt_points(radius: float = 19.0) -> list[tuple[float, float]]:
    return [
        (
            radius * math.cos(math.radians(angle)),
            radius * math.sin(math.radians(angle)),
        )
        for angle in (45.0, 135.0, 225.0, 315.0)
    ]


def orient_axis_x_to_z(part: cq.Workplane) -> cq.Workplane:
    return part.rotate((0, 0, 0), (0, 1, 0), -90)


def place_on_bed(part: cq.Workplane) -> cq.Workplane:
    bounds = part.val().BoundingBox()
    return part.translate((0.0, 0.0, -bounds.zmin))


# ---------------------------------------------------------------------------
# Printable parts
# ---------------------------------------------------------------------------

def make_body() -> cq.Workplane:
    chamber = cylinder_x(CHAMBER_OUTER_DIAMETER, 96.0)
    barrel = cylinder_x(BARREL_OUTER_DIAMETER, BODY_LENGTH - 92.0, 92.0)
    transition = (
        cq.Workplane("YZ", origin=(90.0, 0.0, 0.0))
        .circle(CHAMBER_OUTER_DIAMETER / 2.0)
        .workplane(offset=14.0)
        .circle(BARREL_OUTER_DIAMETER / 2.0)
        .loft(combine=True)
    )
    rear_flange = cylinder_x(46.0, 6.0)

    body = chamber.union(barrel).union(transition).union(rear_flange)

    # Broad toy-like ribs also stiffen the thin cylindrical wall.
    for x in (20.0, 42.0, 64.0):
        body = body.union(cylinder_x(CHAMBER_OUTER_DIAMETER + 2.0, 2.4, x))

    rail_profile = [
        (-6.0, -17.0),
        (-8.0, -24.0),
        (8.0, -24.0),
        (6.0, -17.0),
    ]
    rail = (
        cq.Workplane("YZ", origin=(18.0, 0.0, 0.0))
        .polyline(rail_profile)
        .close()
        .extrude(57.0)
    )
    body = body.union(rail)

    # Air chamber, throttled transfer port, and ball bore.
    body = body.cut(cylinder_x(CHAMBER_INNER_DIAMETER, CHAMBER_LENGTH + 1.0, -1.0))
    body = body.cut(cylinder_x(AIR_PORT_DIAMETER, 14.0, CHAMBER_LENGTH - 0.5))
    body = body.cut(
        cylinder_x(BARREL_INNER_DIAMETER, BODY_LENGTH - 99.0 + 1.0, 99.0)
    )

    # Four axial M3 clearance holes for the captured rear cap.
    for y, z in bolt_points():
        body = body.cut(cylinder_x(3.3, 7.0, -0.5).translate((0.0, y, z)))

    # Printed grip-lock pin.
    body = body.cut(cylinder_y(4.2, 30.0, x=26.0, z=-21.0))
    return body


def make_grip() -> cq.Workplane:
    profile = [
        (14.0, -14.5),
        (80.0, -14.5),
        (77.0, -31.0),
        (68.0, -82.0),
        (58.0, -96.0),
        (43.0, -94.0),
        (31.0, -80.0),
        (22.0, -35.0),
    ]
    grip = cq.Workplane("XZ").polyline(profile).close().extrude(10.0, both=True)

    c = FIT_CLEARANCE
    slot_profile = [
        (-6.0 - c, -16.6),
        (-8.0 - c, -24.0 - c),
        (8.0 + c, -24.0 - c),
        (6.0 + c, -16.6),
    ]
    dovetail_slot = (
        cq.Workplane("YZ", origin=(13.0, 0.0, 0.0))
        .polyline(slot_profile)
        .close()
        .extrude(65.0)
    )
    neck_opening = centred_box(65.0, 12.8, 5.0, x=45.5, z=-14.7)
    grip = grip.cut(dovetail_slot.union(neck_opening))
    grip = grip.cut(cylinder_y(4.2, 30.0, x=26.0, z=-21.0))

    try:
        grip = grip.edges("|Y").fillet(2.0)
    except Exception:
        # The unfilleted solid remains fully printable on older OCCT builds.
        pass
    return grip


def make_rear_cap() -> cq.Workplane:
    cap = cylinder_x(46.0, 8.0, -8.0)
    cap = cap.union(cylinder_x(31.6, 4.0, 0.0))

    # Side ears retain the sear and connect the return-spring shelf.
    cap = cap.union(centred_box(14.0, 4.6, 21.0, x=-7.0, y=-5.7, z=10.5))
    cap = cap.union(centred_box(14.0, 4.6, 21.0, x=-7.0, y=5.7, z=10.5))
    cap = cap.union(centred_box(10.5, 10.0, 3.0, x=-18.75, z=1.5))

    cap = cap.cut(cylinder_x(10.6, 14.0, -9.0))
    centre_slot = centred_box(17.0, 6.8, 21.0, x=-6.5, z=13.5)
    cap = cap.cut(centre_slot)
    cap = cap.cut(cylinder_y(3.3, 30.0, x=-10.0, z=14.0))

    # Pocket for a weak 5 x 10 mm sear-return spring.
    cap = cap.cut(cylinder_z(5.4, 2.2, x=-21.0, z=1.0))

    for y, z in bolt_points():
        cap = cap.cut(cylinder_x(3.3, 15.0, -9.0).translate((0.0, y, z)))
    return cap


def make_plunger() -> cq.Workplane:
    piston = cylinder_x(PISTON_DIAMETER, PISTON_THICKNESS, PISTON_REAR_REST)

    # Groove sized for a 28 x 2 mm O-ring.
    groove_width = 2.4
    groove_x = PISTON_REAR_REST + (PISTON_THICKNESS - groove_width) / 2.0
    groove_outer = cylinder_x(PISTON_DIAMETER + 2.0, groove_width, groove_x)
    groove_core = cylinder_x(28.5, groove_width, groove_x)
    piston = piston.cut(groove_outer.cut(groove_core))

    # Two millimetres of overlap with the pull handle keeps the export a
    # single connected solid instead of two merely coplanar shells.
    rod = cylinder_x(PISTON_ROD_DIAMETER, PISTON_REAR_REST + 52.0, -52.0)
    plunger = piston.union(rod)

    # The collar reaches the rear-cap guide after exactly 32 mm of pull. This
    # is the physical travel limiter; the catch is not used to limit power.
    plunger = plunger.union(cylinder_x(14.0, 4.0, 36.0))

    # Circumferential catch groove. At full pull it aligns with the thumb sear.
    catch_outer = cylinder_x(PISTON_ROD_DIAMETER + 2.0, 5.0, 27.0)
    catch_core = cylinder_x(6.5, 5.0, 27.0)
    plunger = plunger.cut(catch_outer.cut(catch_core))

    handle = cylinder_x(46.0, 10.0, -60.0)
    handle_relief = cylinder_x(30.0, 1.5, -60.1)
    plunger = plunger.union(handle).cut(handle_relief)
    return plunger


def make_sear() -> cq.Workplane:
    lever = centred_box(25.0, 5.6, 6.0, x=-11.5, z=13.0)
    tooth = centred_box(4.0, 5.6, 8.0, x=-2.0, z=7.0)
    gusset = (
        cq.Workplane("XZ")
        .polyline([(-7.0, 10.0), (-2.0, 3.0), (-0.5, 10.0)])
        .close()
        .extrude(2.8, both=True)
    )
    sear = lever.union(tooth).union(gusset)
    sear = sear.cut(cylinder_y(3.3, 20.0, x=-10.0, z=14.0))
    return sear


def make_safety_block() -> cq.Workplane:
    block = centred_box(4.0, 5.2, 6.4, z=3.2)
    pull_tab = centred_box(4.0, 14.0, 2.4, y=8.5, z=3.2)
    knob = centred_box(8.0, 4.0, 6.0, y=16.0, z=3.2)
    return block.union(pull_tab).union(knob)


def make_muzzle_ring() -> cq.Workplane:
    ring = cylinder_x(36.0, 12.0)
    ring = ring.cut(cylinder_x(BARREL_OUTER_DIAMETER + FIT_CLEARANCE, 8.2, -0.1))
    ring = ring.cut(cylinder_x(BALL_RETENTION_DIAMETER, 4.3, 7.8))
    return ring


def make_rail_lock_pin() -> cq.Workplane:
    head = cylinder_z(8.0, 2.4)
    shaft = cylinder_z(4.0, 26.0, z=2.4)
    tip = (
        cq.Workplane("XY", origin=(0.0, 0.0, 28.4))
        .circle(2.0)
        .workplane(offset=2.0)
        .circle(1.2)
        .loft(combine=True)
    )
    return head.union(shaft).union(tip)


def make_ball_fit_gauge() -> cq.Workplane:
    gauge = centred_box(82.0, 30.0, 5.0, z=2.5)
    for x, diameter in zip((-27.0, 0.0, 27.0), (19.6, 20.4, 21.0)):
        gauge = gauge.cut(cylinder_z(diameter, 7.0, x=x, z=-1.0))
    return gauge


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_stl(part: cq.Workplane, filename: str) -> None:
    cq.exporters.export(
        part,
        str(OUTPUT_DIR / filename),
        tolerance=0.08,
        angularTolerance=0.12,
    )


def make_assembly_compound(parts: dict[str, cq.Workplane]) -> cq.Workplane:
    body = parts["body"]
    grip = parts["grip"]
    cap = parts["rear_cap"]
    plunger = parts["plunger"]
    sear = parts["sear"]
    muzzle = parts["muzzle_ring"].translate((137.0, 0.0, 0.0))
    safety = parts["safety_block"].translate((-16.0, 0.0, 3.2))
    pin = (
        parts["rail_lock_pin"]
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((26.0, -15.0, -21.0))
    )
    solids = [body, grip, cap, plunger, sear, muzzle, safety, pin]
    compound = cq.Compound.makeCompound([part.val() for part in solids])
    return cq.Workplane(obj=compound)


def export_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    parts = {
        "body": make_body(),
        "grip": make_grip(),
        "rear_cap": make_rear_cap(),
        "plunger": make_plunger(),
        "sear": make_sear(),
        "safety_block": make_safety_block(),
        "muzzle_ring": make_muzzle_ring(),
        "rail_lock_pin": make_rail_lock_pin(),
        "ball_fit_gauge": make_ball_fit_gauge(),
    }

    print_parts = {
        "toy_popper_body.stl": place_on_bed(orient_axis_x_to_z(parts["body"])),
        "toy_popper_grip.stl": place_on_bed(
            parts["grip"].rotate((0, 0, 0), (1, 0, 0), 90)
        ),
        "toy_popper_rear_cap.stl": place_on_bed(
            orient_axis_x_to_z(parts["rear_cap"])
        ),
        "toy_popper_plunger.stl": place_on_bed(
            orient_axis_x_to_z(parts["plunger"])
        ),
        "toy_popper_sear.stl": place_on_bed(
            parts["sear"].rotate((0, 0, 0), (1, 0, 0), 90)
        ),
        "toy_popper_safety_block.stl": place_on_bed(parts["safety_block"]),
        "toy_popper_muzzle_ring_ORANGE.stl": place_on_bed(
            orient_axis_x_to_z(parts["muzzle_ring"])
        ),
        "toy_popper_rail_lock_pin.stl": place_on_bed(parts["rail_lock_pin"]),
        "toy_popper_ball_fit_gauge.stl": place_on_bed(parts["ball_fit_gauge"]),
    }

    for filename, part in print_parts.items():
        export_stl(part, filename)

    assembly = make_assembly_compound(parts)
    export_stl(assembly, "toy_popper_assembly_preview_NOT_FOR_PRINT.stl")
    cq.exporters.export(assembly, str(OUTPUT_DIR / "toy_popper_assembly.step"))

    print(f"Exported {len(print_parts)} printable STL files to {OUTPUT_DIR}")
    print(f"Stored spring energy: {STORED_ENERGY_J:.3f} J")
    print(f"Maximum spring force: {MAX_SPRING_FORCE_N:.1f} N")
    print(f"Bore / retention diameters: {BARREL_INNER_DIAMETER:.1f} / "
          f"{BALL_RETENTION_DIAMETER:.1f} mm")


if __name__ == "__main__":
    export_all()
