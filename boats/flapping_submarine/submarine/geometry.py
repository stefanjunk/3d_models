"""Part builders for the flapping-tail submarine.

World frame: +X = aft (nose -> tail), +Z = up, +Y = starboard.
All builder output sits in the world frame; the generator applies a
per-part rotation to bring parts into print orientation on export.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cadquery as cq

from .config import SubmarineConfig
from .mechanism import solve_rocker


@dataclass
class PartSpec:
    name: str
    solid: cq.Workplane
    envelope: cq.Workplane | None = None  # closed outer volume for displacement
    watertight: bool = False
    print_rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    note: str = ""


# ------------------------------------------------------------- primitives
def cyl_x(x0: float, x1: float, r: float, cy: float = 0.0, cz: float = 0.0) -> cq.Workplane:
    return (
        cq.Workplane("YZ", origin=(min(x0, x1), cy, cz))
        .circle(r)
        .extrude(abs(x1 - x0))
    )


def cyl_z(z0: float, z1: float, r: float, cx: float = 0.0, cy: float = 0.0) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(cx, cy, min(z0, z1)))
        .circle(r)
        .extrude(abs(z1 - z0))
    )


def box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=((x0 + x1) / 2, (y0 + y1) / 2, z0))
        .rect(x1 - x0, y1 - y0)
        .extrude(z1 - z0)
    )


def _revolve(points: list[tuple[float, float]], angle: float = 360.0) -> cq.Workplane:
    """Revolve a closed XZ half-profile around the X axis (profile at z >= 0)."""
    wp = cq.Workplane("XZ").moveTo(*points[0])
    for p in points[1:]:
        wp = wp.lineTo(*p)
    return wp.close().revolve(angle, (0, 0, 0), (1, 0, 0))


def torus_x(x0: float, x1: float, r_in: float, r_out: float) -> cq.Workplane:
    """Annular ring around the X axis spanning x0..x1."""
    return _revolve([(x0, r_in), (x0, r_out), (x1, r_out), (x1, r_in)])


def _dome_points(dome: float, r: float, x_off: float = 0.0, n: int = 8) -> list[tuple[float, float]]:
    pts = []
    for i in range(n + 1):
        a = math.pi / 2 * i / n
        pts.append((x_off + dome * math.sin(a), r * (1 - math.cos(a))))
    return pts


def _lug(cfg: SubmarineConfig, x0: float, y_center: float, od: float, is_ear: bool) -> cq.Workplane:
    """Tapered hinge lug (thin in Y), extruded in -Y then centred on y_center."""
    t = cfg.ear_t if is_ear else cfg.tongue_t
    h = 0.52 * od if is_ear else 0.48 * od
    hp = 0.72 * h
    pts = [
        (x0, -h / 2),
        (x0 + cfg.lug_len, -hp / 2),
        (x0 + cfg.lug_len, hp / 2),
        (x0, h / 2),
    ]
    wp = cq.Workplane("XZ").moveTo(*pts[0])
    for p in pts[1:]:
        wp = wp.lineTo(*p)
    lug = wp.close().extrude(-t).translate((0, y_center - t / 2, 0))
    pin_x = x0 + cfg.lug_len / 2
    lug = lug.cut(cyl_z(-h, h, cfg.hinge_bore_d / 2, pin_x, y_center))
    return lug


def _hinge_pair(cfg: SubmarineConfig, x0: float, od: float) -> tuple[cq.Workplane, cq.Workplane]:
    """(tongue ending a part at x0, ear pair starting the next part at x0)."""
    tongue = _lug(cfg, x0, 0.0, od, is_ear=False)
    y = cfg.tongue_t / 2 + cfg.hinge_clearance + cfg.ear_t / 2
    ears = _lug(cfg, x0 - cfg.lug_len + cfg.lug_len, -y, od, is_ear=True).union(
        _lug(cfg, x0, +y, od, is_ear=True)
    )
    return tongue, ears


def _tube(od_a: float, od_b: float, x0: float, length: float, wall: float,
          open_front: bool = False) -> tuple[cq.Workplane, cq.Workplane]:
    """Tapered tube along X from x0; returns (shell, envelope)."""
    outer = (
        cq.Workplane("YZ", origin=(x0, 0, 0))
        .circle(od_a / 2)
        .workplane(offset=length)
        .circle(od_b / 2)
        .loft()
    )
    ra, rb = od_a / 2 - wall, od_b / 2 - wall
    xi = x0 + (0 if open_front else wall)
    li = length - (0 if open_front else wall) - wall
    inner = (
        cq.Workplane("YZ", origin=(xi, 0, 0))
        .circle(ra)
        .workplane(offset=li)
        .circle(rb)
        .loft()
    )
    return outer.cut(inner), outer


def _fish_rib_scale(cfg: SubmarineConfig, angle_deg: float) -> float:
    """Blend rib prominence from dorsal to lateral without touching the belly."""
    t = min(abs(angle_deg) / 90.0, 1.0)
    return cfg.fish_rib_dorsal_scale + t * (
        cfg.fish_rib_lateral_scale - cfg.fish_rib_dorsal_scale
    )


def _fish_ribs(
    cfg: SubmarineConfig,
    stations: list[tuple[float, float, float]],
) -> list[cq.Workplane]:
    """Loft circular rib sections along semantic X stations.

    Each station is (x, authoritative shell radius, unscaled rib radius).
    The loft overlaps the exact shell by fish_rib_overlap and never edits it.
    """
    if not cfg.fish_ribs_enabled:
        return []
    ribs: list[cq.Workplane] = []
    for angle_deg in cfg.fish_rib_angles_deg:
        theta = math.radians(angle_deg)
        scale = _fish_rib_scale(cfg, angle_deg)
        wires: list[cq.Wire] = []
        for x, shell_r, nominal_r in stations:
            rib_r = max(nominal_r * scale, 1.5 * cfg.nozzle)
            overlap = min(cfg.fish_rib_overlap, 0.75 * rib_r)
            centre_r = shell_r + rib_r - overlap
            wires.append(
                cq.Wire.makeCircle(
                    rib_r,
                    cq.Vector(x, math.sin(theta) * centre_r, math.cos(theta) * centre_r),
                    cq.Vector(1, 0, 0),
                )
            )
        rib = cq.Solid.makeLoft(wires, ruled=False)
        ribs.append(cq.Workplane("XY").newObject([rib]))
    return ribs


def _add_fish_ribs(
    solid: cq.Workplane,
    envelope: cq.Workplane,
    ribs: list[cq.Workplane],
) -> tuple[cq.Workplane, cq.Workplane]:
    for rib in ribs:
        solid = solid.union(rib)
        envelope = envelope.union(rib)
    return solid, envelope


# ---------------------------------------------------------------- nose
def build_nose(cfg: SubmarineConfig) -> list[PartSpec]:
    r = cfg.hull_od_front / 2
    outer = _revolve(
        _dome_points(cfg.nose_dome, r)
        + [(cfg.nose_length, r), (cfg.nose_length, 0.0)]
    )
    r2 = r - cfg.wall
    shell = outer.cut(
        _revolve(
            _dome_points(max(cfg.nose_dome - cfg.wall, 6.0), r2, x_off=cfg.wall)
            + [(cfg.nose_length - cfg.wall, r2), (cfg.nose_length - cfg.wall, 0.0)]
        )
    )

    bo = cfg.bladder_tube_od / 2
    tube_x0, tube_x1 = -cfg.bladder_protrude, cfg.bladder_inner_len
    tube = cyl_x(tube_x0, tube_x1, bo)
    bore = cyl_x(tube_x0 - 1, cfg.bladder_inner_len - cfg.wall, cfg.bladder_bore_d / 2)
    nose = shell.union(tube).cut(bore)

    tongue, _ = _hinge_pair(cfg, cfg.nose_length, cfg.hull_od_front)
    nose = nose.union(tongue)
    env = outer.union(cyl_x(tube_x0, tube_x1, bo)).union(tongue)

    rib_x0 = cfg.nose_dome + cfg.fish_rib_end_margin
    rib_x1 = cfg.nose_length - cfg.fish_rib_end_margin
    rib_span = rib_x1 - rib_x0
    nose, env = _add_fish_ribs(
        nose,
        env,
        _fish_ribs(
            cfg,
            [
                (rib_x0, r, cfg.fish_rib_end_radius),
                (rib_x0 + 0.25 * rib_span, r, 0.90 * cfg.fish_rib_peak_radius),
                (rib_x0 + 0.70 * rib_span, r, cfg.fish_rib_peak_radius),
                (rib_x1, r, cfg.fish_rib_end_radius),
            ],
        ),
    )

    return [
        PartSpec(
            name="nose_body",
            solid=nose,
            envelope=env,
            watertight=True,
            print_rotation=(0.0, -90.0, 0.0),
            note="fish-rib fairing; print standing on rear face, nose tip up",
        ),
        build_bladder_piston(cfg),
    ]


def build_bladder_piston(cfg: SubmarineConfig) -> PartSpec:
    rod_r = cfg.bladder_rod_d / 2
    rod_len = cfg.bladder_rod_len
    rod = cyl_x(0, rod_len, rod_r)
    knob = (
        cq.Workplane("YZ", origin=(-cfg.bladder_knob_h, 0, 0))
        .polygon(24, cfg.bladder_knob_d)
        .extrude(cfg.bladder_knob_h)
    )
    solid = rod.union(knob)
    for gx in (rod_len - 6.0, rod_len - 11.0):
        solid = solid.cut(torus_x(gx, gx + 2.2, rod_r - 1.1, rod_r + 0.05))
    # place in assembled position: knob in front of the bladder tube face
    solid = solid.translate((-(cfg.bladder_protrude + cfg.bladder_knob_h), 0, 0))
    return PartSpec(
        name="bladder_piston",
        solid=solid,
        print_rotation=(0.0, -90.0, 0.0),
        note="friction piston: push/pull knob to trim displacement",
    )


# ------------------------------------------------------------- segments
def build_segments(cfg: SubmarineConfig) -> list[PartSpec]:
    parts: list[PartSpec] = []
    n = cfg.n_segments
    for i in range(n):
        o = cfg.nose_length + i * cfg.segment_length
        drum_x0 = o + cfg.lug_len
        drum_len = cfg.segment_length - cfg.lug_len
        od_a = cfg.hull_od(o + cfg.lug_len, cfg.nose_length, cfg.capsule_start_x)
        od_b = cfg.hull_od(o + cfg.segment_length, cfg.nose_length, cfg.capsule_start_x)
        shell, env_tube = _tube(od_a, od_b, drum_x0, drum_len, cfg.wall)
        tongue, _ = _hinge_pair(cfg, o + cfg.segment_length, od_b)
        _, ears = _hinge_pair(cfg, o, od_a)
        solid = shell.union(tongue).union(ears)
        env = env_tube.union(tongue).union(ears)
        rib_x0 = drum_x0 + cfg.fish_rib_end_margin
        rib_x1 = drum_x0 + drum_len - cfg.fish_rib_end_margin
        rib_span = rib_x1 - rib_x0

        def shell_radius(x: float) -> float:
            t = (x - drum_x0) / drum_len
            return (od_a + t * (od_b - od_a)) / 2

        solid, env = _add_fish_ribs(
            solid,
            env,
            _fish_ribs(
                cfg,
                [
                    (rib_x0, shell_radius(rib_x0), cfg.fish_rib_end_radius),
                    (rib_x0 + 0.25 * rib_span, shell_radius(rib_x0 + 0.25 * rib_span), cfg.fish_rib_peak_radius),
                    (rib_x0 + 0.75 * rib_span, shell_radius(rib_x0 + 0.75 * rib_span), 0.95 * cfg.fish_rib_peak_radius),
                    (rib_x1, shell_radius(rib_x1), cfg.fish_rib_end_radius),
                ],
            ),
        )
        parts.append(
            PartSpec(
                name=f"segment_{i + 1:02d}",
                solid=solid,
                envelope=env,
                watertight=True,
                note="fish-rib buoyancy segment, hinge pin vertical",
            )
        )
    return parts


# ------------------------------------------------------------- capsule
def build_capsule(cfg: SubmarineConfig) -> list[PartSpec]:
    oc = cfg.capsule_start_x
    x_cf = oc + cfg.lug_len
    x_rear = x_cf + (cfg.capsule_length - cfg.lug_len)
    x_wall = x_rear - cfg.rear_wall
    ri = cfg.capsule_inner_r
    od = cfg.capsule_od

    shell, env = _tube(od, od, x_cf, cfg.capsule_length - cfg.lug_len, cfg.wall, open_front=True)

    hinge_od = cfg.hull_od(cfg.capsule_start_x, cfg.nose_length, cfg.capsule_start_x)
    _, ears = _hinge_pair(cfg, oc, hinge_od)
    shell = shell.union(ears)
    env = env.union(ears)

    # ---- rear wall + gland boss
    gland_fl = cyl_x(x_rear, x_rear + cfg.gland_flange_t, cfg.gland_boss_d / 2)
    gland_stub = cyl_x(
        x_rear + cfg.gland_flange_t,
        x_rear + cfg.gland_boss_len,
        cfg.gland_boss_d / 2 - 2.0,
    )
    boss = gland_fl.union(gland_stub)
    bore = cyl_x(x_wall, x_rear + cfg.gland_boss_len, cfg.gland_bore_d / 2)
    shell = shell.union(boss).cut(bore)
    # o-ring groove ring inside the boss bore (static seal around rotating shaft)
    groove_x = x_rear + cfg.gland_oring_depth
    shell = shell.cut(
        torus_x(groove_x - 1.1, groove_x + 1.1, 0.2, cfg.gland_bore_d / 2 + 0.9).intersect(
            cyl_x(x_rear, x_rear + cfg.gland_boss_len, cfg.gland_boss_d / 2)
        )
    )
    env = env.union(boss)

    # ---- bayonet grooves for the cap: entry channel + circumferential groove
    channel = _revolve(
        [(x_cf, ri - 0.2), (x_cf, ri + 1.2), (x_cf + 9.0, ri + 1.2), (x_cf + 9.0, ri - 0.2)],
        angle=40.0,
    )
    arc = _revolve(
        [(x_cf + 5.5, ri - 0.2), (x_cf + 5.5, ri + 1.2), (x_cf + 9.0, ri + 1.2), (x_cf + 9.0, ri - 0.2)],
        angle=100.0,
    )
    groove = channel.union(arc)
    for ang in (0.0, 120.0, 240.0):
        shell = shell.cut(groove.rotate((0, 0, 0), (1, 0, 0), ang))

    # ---- reed switch pocket (thin recess in the top wall, near the front)
    shell = shell.cut(box(x_cf + 12, x_cf + 32, -3.5, 3.5, 17.0, 19.0))

    # ---- motor cradle saddle (N20), rear inside
    saddle = box(x_rear - 19, x_rear - 1, -12, 12, -ri - 1.2, 6.5)
    shell = shell.union(saddle).cut(cyl_x(x_rear - 20, x_rear - 3, cfg.motor_d / 2 + 0.2))
    shell = shell.cut(cyl_z(-10, 7, 1.3, x_rear - 16, 8)).cut(
        cyl_z(-10, 7, 1.3, x_rear - 16, -8)
    ).cut(cyl_z(-10, 7, 1.3, x_rear - 4, 8)).cut(cyl_z(-10, 7, 1.3, x_rear - 4, -8))

    # ---- battery saddles (2x AAA) on the floor
    for yc in (-6.2, 6.2):
        block = box(x_cf + 9, x_cf + 55, yc - 6.4, yc + 6.4, -ri - 1.2, -8.0)
        shell = shell.union(block).cut(cyl_x(x_cf + 8, x_cf + 56, 5.6, yc, -12.0))
        shell = shell.cut(cyl_z(-19, -7, 1.3, x_cf + 13, yc)).cut(
            cyl_z(-19, -7, 1.3, x_cf + 51, yc)
        )

    # ---- keel ballast pocket under the hull
    kx = cfg.keel_center_x
    keel = box(kx - 35, kx + 35, -cfg.keel_w / 2, cfg.keel_w / 2, -od / 2 - cfg.keel_h, -od / 2 + 2)
    keel_in = box(
        kx - 33, kx + 33,
        -cfg.keel_w / 2 + cfg.keel_wall, cfg.keel_w / 2 - cfg.keel_wall,
        -od / 2 - cfg.keel_h + cfg.keel_wall, -od / 2 - 1.5,
    )
    shell = shell.union(keel).cut(keel_in)
    env = env.union(keel)
    # fill plug boss on keel rear face (protrudes into the hull wall to fuse)
    zboss = -od / 2 - cfg.keel_h / 2 + 1.0
    boss_k = cyl_x(kx + 35, kx + 41, 9.0, 0, zboss)
    shell = shell.union(boss_k).cut(
        cyl_x(kx + 30, kx + 41, cfg.keel_plug_d / 2, 0, zboss)
    )
    from .threads import cut_internal_thread

    shell = cut_internal_thread(
        shell, cfg.keel_plug_d / 2, cfg.keel_plug_pitch, 1.2, 6.0,
        axis="X", z_offset=kx + 35.0, cz=zboss,
    )
    env = env.union(boss_k)

    # ---- pivot webs + eyes for the tail rocker (behind the rear wall)
    sol = solve_rocker(cfg)
    pz = sol.pivot_z
    web_l = box(x_rear - 2, x_rear + 13, 6.2, 8.7, pz - 8.5, pz + 6)
    web_r = box(x_rear - 2, x_rear + 13, -8.7, -6.2, pz - 8.5, pz + 6)
    eye_t = 3.0
    e1_x0, e2_x0 = x_rear + 2.0, x_rear + 2.0 + eye_t + 0.2 + cfg.rocker_t + 0.2
    eye_h, eye_w = 13.0, 18.0
    eye1 = (
        box(e1_x0, e1_x0 + eye_t, -eye_w / 2, eye_w / 2, pz - eye_h / 2, pz + eye_h / 2)
    )
    eye2 = (
        box(e2_x0, e2_x0 + eye_t, -eye_w / 2, eye_w / 2, pz - eye_h / 2, pz + eye_h / 2)
    )
    eye1 = eye1.cut(cyl_x(e1_x0 - 1, e1_x0 + eye_t + 1, (cfg.pivot_pin_d + 0.4) / 2, 0, pz))
    eye2 = eye2.cut(cyl_x(e2_x0 - 1, e2_x0 + eye_t + 1, (cfg.pivot_pin_d + 0.4) / 2, 0, pz))
    eye2 = eye2.cut(
        box(e2_x0 - 1, e2_x0 + eye_t + 1, -(cfg.pivot_pin_d + 0.4) / 2, (cfg.pivot_pin_d + 0.4) / 2,
            pz, pz + eye_h)
    )
    shell = shell.union(web_l).union(web_r).union(eye1).union(eye2)
    env = env.union(eye1).union(eye2).union(web_l).union(web_r)

    rib_x0 = x_cf + cfg.fish_rib_end_margin
    rib_x1 = x_rear - 3.0
    rib_span = rib_x1 - rib_x0
    shell, env = _add_fish_ribs(
        shell,
        env,
        _fish_ribs(
            cfg,
            [
                (rib_x0, od / 2, cfg.fish_rib_end_radius),
                (rib_x0 + 0.22 * rib_span, od / 2, cfg.fish_rib_peak_radius),
                (rib_x0 + 0.62 * rib_span, od / 2, 1.12 * cfg.fish_rib_peak_radius),
                (rib_x1, od / 2, 0.75 * cfg.fish_rib_end_radius),
            ],
        ),
    )

    cap = build_capsule_cap(cfg, x_cf)
    pivot_pin = PartSpec(
        name="pivot_pin",
        solid=cyl_x(e1_x0, e2_x0 + eye_t, cfg.pivot_pin_d / 2, 0, pz).union(
            cyl_x(e1_x0 - 1.5, e1_x0, (cfg.pivot_pin_d + 2.5) / 2, 0, pz)
        ),
        print_rotation=(0.0, -90.0, 0.0),
        note="tail rocker pivot pin; insert from the front, glue dot optional",
    )
    return [
        PartSpec(
            name="capsule_body",
            solid=shell,
            envelope=env,
            watertight=True,
            note="fish-rib electronics hull; print keel down, supports on gland boss",
        ),
        cap,
        pivot_pin,
    ]


def build_capsule_cap(cfg: SubmarineConfig, x_cf: float) -> PartSpec:
    ri = cfg.capsule_inner_r
    plug_r = ri - cfg.cap_bayonet_clearance
    plug = cyl_x(x_cf + 0.5, x_cf + 8.5, plug_r)
    solid = plug
    # sealing groove on plug OD
    solid = solid.cut(
        torus_x(
            x_cf + 2.5,
            x_cf + 4.7,
            plug_r - cfg.cap_oring_groove_depth,
            plug_r + 0.05,
        )
    )
    # bayonet lugs (enter through the channels, twist ~60-90 deg to lock)
    lug = _revolve(
        [(x_cf + 5.75, plug_r - 1.0), (x_cf + 5.75, plug_r + 1.2),
         (x_cf + 8.75, plug_r + 1.2), (x_cf + 8.75, plug_r - 1.0)],
        angle=30.0,
    )
    for ang in (0.0, 120.0, 240.0):
        solid = solid.union(lug.rotate((0, 0, 0), (1, 0, 0), ang))
    # grip tabs (clear the hinge lugs of the last segment)
    for s in (-1, 1):
        y0, y1 = sorted((s * 4.0, s * 7.0))
        for sz in (-1, 1):
            z0, z1 = sorted((sz * 10.0, sz * 13.0))
            solid = solid.union(box(x_cf - 6.0, x_cf + 0.5, y0, y1, z0, z1))
    # coin slot in the front face
    solid = solid.cut(box(x_cf - 0.7, x_cf + 0.5, -10, 10, -1.6, 1.6))
    return PartSpec(
        name="capsule_cap",
        solid=solid,
        watertight=True,
        print_rotation=(0.0, -90.0, 0.0),
        note="bayonet cap; insert, twist ~60-90 deg, o-ring 36x1.5 on plug",
    )


# ------------------------------------------------------------- tail drive
def build_drive(cfg: SubmarineConfig) -> list[PartSpec]:
    x_rear = cfg.capsule_end_x
    sol = solve_rocker(cfg)
    pz = sol.pivot_z

    # x layout behind the rear wall
    hub_x0 = x_rear + 2.0 + 3.0 + 0.2          # behind eye1 (t=3)
    hub_x1 = hub_x0 + cfg.rocker_t
    disc_x0 = hub_x1 + 0.2 + 3.0 + 1.0 + 2.0   # behind eye2 + pin head room
    disc_x1 = disc_x0 + cfg.crank_disc_t

    # shaft sleeve (extends the motor shaft to the crank disc)
    sleeve = cyl_x(x_rear + 4.5, x_rear + 12.0, 2.25)
    sleeve = sleeve.cut(cyl_x(x_rear + 3.5, x_rear + 13.0, 1.55))
    sleeve = sleeve.cut(box(x_rear + 4.5, x_rear + 12.0, -0.4, 0.4, -2.4, 2.4))
    sleeve_note = "glue onto motor shaft with a drop of CA"

    # crank disc with forward crank pin
    disc = cyl_x(disc_x0, disc_x1, cfg.crank_disc_d / 2)
    disc = disc.cut(cyl_x(disc_x0 - 1, disc_x1 + 1, 2.3))
    disc = disc.cut(box(disc_x0 - 1, disc_x1 + 1, -0.4, 0.4, -cfg.crank_disc_d / 2, cfg.crank_disc_d / 2))
    pin_z = cfg.crank_r
    pin_body = cyl_x(hub_x0, disc_x0, cfg.crank_pin_d / 2, 0, pin_z)
    pin_head = cyl_x(hub_x0 - 1.5, hub_x0, (cfg.crank_pin_d + 2.5) / 2, 0, pin_z)
    boss = cyl_x(disc_x0 - 2.0, disc_x0, 4.5, 0, pin_z)
    disc = disc.union(pin_body).union(pin_head).union(boss)

    # tail rocker: hub + arm + slot + fin socket ears (YZ plate, thickness X)
    rocker_hub = cyl_x(hub_x0, hub_x1, 6.0, 0, pz)
    rocker_hub = rocker_hub.cut(cyl_x(hub_x0 - 1, hub_x1 + 1, (cfg.pivot_pin_d + 0.4) / 2, 0, pz))
    tip_z = pz - cfg.rocker_arm_tip_r
    arm_pts = [
        (-5.5, pz - 2), (-4.5, tip_z + 4), (0, tip_z - 5),
        (4.5, tip_z + 4), (5.5, pz - 2),
    ]
    wp = cq.Workplane("YZ", origin=(0, 0, 0)).moveTo(arm_pts[0][0], arm_pts[0][1])
    for p in arm_pts[1:]:
        wp = wp.lineTo(p[0], p[1])
    arm = wp.close().extrude(cfg.rocker_t).translate((hub_x0, 0, 0))
    rocker = rocker_hub.union(arm)
    # radial slot for the crank pin
    slot_l = sol.slot_r_end - sol.slot_r_start
    slot_cz = pz - (sol.slot_r_start + sol.slot_r_end) / 2
    slot = (
        box(hub_x0 - 1, hub_x1 + 1, -cfg.rocker_slot_w / 2, cfg.rocker_slot_w / 2,
            slot_cz - slot_l / 2, slot_cz + slot_l / 2)
        .union(cyl_x(hub_x0 - 1, hub_x1 + 1, cfg.rocker_slot_w / 2, 0, slot_cz - slot_l / 2))
        .union(cyl_x(hub_x0 - 1, hub_x1 + 1, cfg.rocker_slot_w / 2, 0, slot_cz + slot_l / 2))
    )
    rocker = rocker.cut(slot)
    # fin socket ears at the arm tip, with a tang recess between them
    ear_gap = cfg.fin_t / 2 + 0.2
    for s in (-1, 1):
        y0, y1 = sorted((s * ear_gap, s * (ear_gap + 1.2)))
        ear = box(hub_x0, hub_x0 + 12, y0, y1, tip_z - 6, tip_z + 6)
        rocker = rocker.union(ear)
    rocker = rocker.cut(
        box(hub_x0 - 1, hub_x0 + 12, -ear_gap, ear_gap, tip_z - 8, tip_z + 6)
    )
    rocker = rocker.cut(cyl_z(tip_z - 7, tip_z + 7, 1.25, hub_x0 + 6, 0))

    # tail fin: vertical blade (XZ plane) with root tang between the ears
    fx0 = hub_x0
    tang = box(fx0 + 1, fx0 + 11, -cfg.fin_t / 2, cfg.fin_t / 2, tip_z - 7, tip_z + 5)
    tang = tang.cut(cyl_z(tip_z - 8, tip_z + 6, 1.25, fx0 + 6, 0))
    blade_pts = [
        (fx0 + 6, tip_z + 3), (fx0 + 30, tip_z + 2), (fx0 + 52, tip_z - 6),
        (fx0 + 55, tip_z - 16), (fx0 + 46, tip_z - 26), (fx0 + 24, tip_z - 31),
        (fx0 + 8, tip_z - 22), (fx0 + 4, tip_z - 8),
    ]
    wp = cq.Workplane("XZ").moveTo(*blade_pts[0])
    for p in blade_pts[1:]:
        wp = wp.lineTo(*p)
    blade = wp.close().extrude(-cfg.fin_t).translate((0, -cfg.fin_t / 2, 0))
    fin = tang.union(blade)

    return [
        PartSpec("crank_disc", solid=disc, print_rotation=(0.0, 90.0, 0.0),
                 note="clamp onto shaft sleeve with a zip tie through the slit"),
        PartSpec("shaft_sleeve", solid=sleeve, print_rotation=(0.0, -90.0, 0.0),
                 note=sleeve_note),
        PartSpec("tail_rocker", solid=rocker, print_rotation=(0.0, 90.0, 0.0),
                 note="grease the crank pin slot; rides on the pivot pin"),
        PartSpec("tail_fin", solid=fin, print_rotation=(0.0, 90.0, 0.0),
                 note="drop the tang between the rocker ears, pin through (Z)"),
    ]


# ------------------------------------------------------------- small parts
def build_keel_plug(cfg: SubmarineConfig) -> PartSpec:
    from .threads import cut_external_thread

    od = cfg.capsule_od
    zc = -od / 2 - cfg.keel_h / 2 + 1.0
    x_face = cfg.keel_center_x + 41.0
    head = cyl_x(x_face, x_face + 3, 8.0, 0, zc)
    stub = cyl_x(x_face - 8, x_face, cfg.keel_plug_d / 2, 0, zc)
    solid = head.union(stub)
    solid = cut_external_thread(
        solid, cfg.keel_plug_d / 2 - 0.2, cfg.keel_plug_pitch, 1.0, 8.0,
        axis="X", z_offset=x_face - 7.5, cz=zc,
    )
    solid = solid.cut(torus_x(x_face - 0.4, x_face + 1.6, cfg.keel_plug_d / 2 - 1.3, cfg.keel_plug_d / 2 + 0.05))
    solid = solid.cut(box(x_face, x_face + 0.8, -6, 6, zc - 1.2, zc + 1.2))
    return PartSpec(
        name="keel_plug",
        solid=solid,
        print_rotation=(0.0, -90.0, 0.0),
        note="ballast fill plug; o-ring 9x1.5, thread M12x1.5",
    )


def build_ballast_box(cfg: SubmarineConfig) -> list[PartSpec]:
    x0, x1 = 263.0, 289.0
    hw = cfg.ballast_box_w / 2
    z0, z1 = -cfg.capsule_inner_r, -cfg.capsule_inner_r + cfg.ballast_box_h
    outer = box(x0, x1, -hw, hw, z0, z1)
    outer = outer.intersect(cyl_x(x0 - 1, x1 + 1, cfg.capsule_inner_r))
    inner = box(x0 + 2, x1 - 2, -hw + 2, hw - 2, z0 + 2, z1 + 1)
    bx = outer.cut(inner)
    lid = box(x0 - 0.5, x1 + 0.5, -hw - 0.5, hw + 0.5, z1 + 0.4, z1 + 2.0)
    return [
        PartSpec("ballast_box", solid=bx, note="coins/shot inside the hull, coarse trim"),
        PartSpec("ballast_lid", solid=lid, note="loose lid"),
    ]


def build_hinge_pin(cfg: SubmarineConfig) -> PartSpec:
    h = 0.52 * cfg.hull_od_front / 2 + 0.5  # above the tallest lug face
    pin = cyl_z(-h - 1.0, h, cfg.hinge_pin_d / 2)
    pin = pin.union(cyl_z(h, h + 1.5, (cfg.hinge_pin_d + 2.0) / 2))
    # place at the first hinge (nose/segment_01) for the assembly preview
    pin = pin.translate((cfg.nose_length + cfg.lug_len / 2, 0, 0))
    return PartSpec(
        name="hinge_pin",
        solid=pin,
        note="print x5; insert through each hinge, peen/melt both ends lightly",
    )


# ------------------------------------------------------------- assembly
def build_all(cfg: SubmarineConfig) -> list[PartSpec]:
    parts: list[PartSpec] = []
    parts += build_nose(cfg)
    parts += build_segments(cfg)
    parts += build_capsule(cfg)
    parts += build_drive(cfg)
    parts.append(build_keel_plug(cfg))
    parts += build_ballast_box(cfg)
    parts.append(build_hinge_pin(cfg))
    return parts
