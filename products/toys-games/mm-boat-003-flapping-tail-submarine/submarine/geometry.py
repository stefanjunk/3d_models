"""Part builders for the flapping-tail submarine.

World frame: +X = aft (nose -> tail), +Z = up, +Y = starboard.
All builder output sits in the world frame; the generator applies a
per-part rotation to bring parts into print orientation on export.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

from .config import SubmarineConfig
from .mechanism import solve_rocker
from .surfacing import FishEnvelopeProfile


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


def _ellipse_loft(stations: list[tuple[float, float, float]]) -> cq.Workplane:
    """Loft seam-aligned ellipse wires normal to the X axis."""
    if len(stations) < 2:
        raise ValueError("an ellipse loft needs at least two stations")
    wires: list[cq.Wire] = []
    last_x = -math.inf
    for x, ry, rz in stations:
        if x <= last_x or min(ry, rz) <= 0:
            raise ValueError("ellipse stations must have increasing X and positive radii")
        wires.append(cq.Workplane("YZ", origin=(x, 0, 0)).ellipse(ry, rz).val())
        last_x = x
    return cq.Workplane("XY").newObject([cq.Solid.makeLoft(wires, ruled=False)])


def _fairing_for_region(
    cfg: SubmarineConfig,
    profile: FishEnvelopeProfile,
    region: str,
    x0: float,
    x1: float,
) -> tuple[cq.Workplane, cq.Workplane]:
    """Return (overlapping additive fairing, closed displacement envelope)."""
    target_stations = profile.sample(region, x0, x1, cfg.fish_registered_sections)
    cutter_stations = [
        (
            x,
            max(profile.core_radius(region, x) - cfg.fish_fairing_overlap, cfg.wall),
            max(profile.core_radius(region, x) - cfg.fish_fairing_overlap, cfg.wall),
        )
        for x, _, _ in target_stations
    ]
    target = _ellipse_loft(target_stations)
    overlap_cutter = _ellipse_loft(cutter_stations)
    return target.cut(overlap_cutter), target


def _ellipse_radial_distance(ry: float, rz: float, theta: float) -> float:
    sy, cz = math.sin(theta), math.cos(theta)
    return 1.0 / math.sqrt((sy / ry) ** 2 + (cz / rz) ** 2)


def _crest_wire(
    x: float,
    ry: float,
    rz: float,
    theta: float,
    visible_height: float,
    half_width: float,
    overlap: float,
) -> cq.Wire:
    """Broad low ellipse with an exact visible height and inward overlap."""
    radial = cq.Vector(0.0, math.sin(theta), math.cos(theta))
    tangent = cq.Vector(0.0, math.cos(theta), -math.sin(theta))
    shell_r = _ellipse_radial_distance(ry, rz, theta)
    radial_half = (visible_height + overlap) / 2.0
    centre_offset = shell_r + (visible_height - overlap) / 2.0
    centre = cq.Vector(x, radial.y * centre_offset, radial.z * centre_offset)
    edge = cq.Edge.makeEllipse(
        half_width,
        radial_half,
        centre,
        cq.Vector(1.0, 0.0, 0.0),
        tangent,
    )
    return cq.Wire.assembleEdges([edge])


def _fish_crests(
    cfg: SubmarineConfig,
    profile: FishEnvelopeProfile,
    region: str,
    x0: float,
    x1: float,
) -> list[cq.Workplane]:
    """Three broad shallow longitudinal crests, never rod-like ribs."""
    if not cfg.fish_fairing_enabled:
        return []
    start = x0 + cfg.fish_crest_end_margin
    end = x1 - cfg.fish_crest_end_margin
    if end <= start:
        raise ValueError("crest end margins consume the available body length")
    count = cfg.fish_registered_sections
    stations = [start + i * (end - start) / (count - 1) for i in range(count)]
    crests: list[cq.Workplane] = []
    for angle_deg in cfg.fish_crest_angles_deg:
        theta = math.radians(angle_deg)
        wires: list[cq.Wire] = []
        for i, x in enumerate(stations):
            blend = math.sin(math.pi * i / (count - 1))
            height = cfg.fish_crest_end_height + blend * (
                cfg.fish_crest_peak_height - cfg.fish_crest_end_height
            )
            half_width = cfg.fish_crest_end_half_width + blend * (
                cfg.fish_crest_half_width - cfg.fish_crest_end_half_width
            )
            ry, rz = profile.radii(region, x)
            wires.append(
                _crest_wire(
                    x,
                    ry,
                    rz,
                    theta,
                    height,
                    half_width,
                    cfg.fish_crest_overlap,
                )
            )
        crests.append(cq.Workplane("XY").newObject([cq.Solid.makeLoft(wires, ruled=False)]))
    return crests


def _add_fish_envelope(
    solid: cq.Workplane,
    envelope: cq.Workplane,
    fairing: cq.Workplane,
    target_envelope: cq.Workplane,
    crests: list[cq.Workplane],
) -> tuple[cq.Workplane, cq.Workplane]:
    solid = solid.union(fairing)
    envelope = envelope.union(target_envelope)
    for crest in crests:
        solid = solid.union(crest)
        envelope = envelope.union(crest)
    return solid, envelope


def _dorsal_fin(cfg: SubmarineConfig, profile: FishEnvelopeProfile) -> cq.Workplane:
    """Support-aware swept dorsal fin, rooted only in the rear capsule."""
    x0 = cfg.capsule_start_x + cfg.lug_len + 28.0
    x1 = x0 + cfg.dorsal_fin_length
    if x1 > cfg.capsule_end_x - 16.0:
        raise ValueError("dorsal fin enters the rear drive keep-out")
    z0 = profile.radii("capsule", x0)[1] - 0.9
    z1 = profile.radii("capsule", x1)[1] - 0.9
    peak_x = x0 + 0.55 * cfg.dorsal_fin_length
    peak_z = profile.radii("capsule", peak_x)[1] + cfg.dorsal_fin_height
    outline = (
        cq.Workplane("XZ")
        .moveTo(x0, z0)
        .spline(
            [
                (x0 + 0.28 * cfg.dorsal_fin_length, z0 + 0.50 * cfg.dorsal_fin_height),
                (peak_x, peak_z),
                (x0 + 0.78 * cfg.dorsal_fin_length, z1 + 0.44 * cfg.dorsal_fin_height),
                (x1, z1),
            ],
            includeCurrent=True,
        )
        .lineTo(x0, z0)
        .close()
    )
    return outline.extrude(cfg.dorsal_fin_t / 2.0, both=True)


def _pectoral_fins(cfg: SubmarineConfig, profile: FishEnvelopeProfile) -> list[cq.Workplane]:
    """One swept bilateral pair, canted down for keel-down FDM orientation."""
    x0 = cfg.capsule_start_x + cfg.lug_len + 18.0
    length = cfg.pectoral_fin_length
    x1 = x0 + length
    root_y = profile.radii("capsule", x0 + 0.45 * length)[0] - 1.2
    root_z = -4.0
    fins: list[cq.Workplane] = []
    for side in (-1.0, 1.0):
        points = [
            (x0, side * root_y),
            (x0 + 0.38 * length, side * (root_y + 0.82 * cfg.pectoral_fin_span)),
            (x0 + 0.62 * length, side * (root_y + cfg.pectoral_fin_span)),
            (x1, side * (root_y + 0.58 * cfg.pectoral_fin_span)),
            (x0 + 0.76 * length, side * root_y),
        ]
        fin = (
            cq.Workplane("XY", origin=(0.0, 0.0, root_z))
            .polyline(points)
            .close()
            .extrude(cfg.pectoral_fin_t / 2.0, both=True)
        )
        fin = fin.rotate(
            (0.0, side * root_y, root_z),
            (1.0, side * root_y, root_z),
            -side * cfg.pectoral_fin_cant_deg,
        )
        fins.append(fin)
    return fins


def _add_capsule_fins(
    solid: cq.Workplane,
    envelope: cq.Workplane,
    cfg: SubmarineConfig,
    profile: FishEnvelopeProfile,
) -> tuple[cq.Workplane, cq.Workplane]:
    for fin in [_dorsal_fin(cfg, profile), *_pectoral_fins(cfg, profile)]:
        solid = solid.union(fin)
        envelope = envelope.union(fin)
    return solid, envelope


def _keel_watermark_cutter(cfg: SubmarineConfig) -> cq.Workplane:
    """Exact unscaled MM-WM-001-R2 Compact cutter, readable from underside."""
    asset_dir = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "metrimade-watermark"
        / "generated"
        / f"{cfg.watermark_product_id}_v{cfg.watermark_version}_compact"
    )
    dxf_path = asset_dir / (
        f"metrimade-watermark-{cfg.watermark_product_id}"
        f"-v{cfg.watermark_version}-compact.dxf"
    )
    if not dxf_path.is_file():
        raise FileNotFoundError(f"canonical watermark DXF is missing: {dxf_path}")

    profile = cq.importers.importDXF(str(dxf_path))
    cutter = profile.toPending().extrude(cfg.watermark_depth + cfg.watermark_overlap)
    bb = cutter.val().BoundingBox()
    if bb.xlen > cfg.watermark_width + 1e-3 or bb.ylen > cfg.watermark_height + 1e-3:
        raise ValueError("generated watermark geometry exceeds its authoritative envelope")

    # Match the generator's underside-readable transform exactly:
    # translate([profile_width, 0]) mirror([1, 0, 0]).
    cutter = (
        cutter
        .translate((-cfg.watermark_width / 2.0, 0.0, 0.0))
        .mirror("YZ")
        .translate((cfg.watermark_width / 2.0, 0.0, 0.0))
    )
    origin_x = cfg.keel_center_x - cfg.watermark_width / 2.0
    origin_y = -cfg.watermark_height / 2.0
    keel_bottom_z = -cfg.capsule_od / 2.0 - cfg.keel_h
    return cutter.translate((
        origin_x,
        origin_y,
        keel_bottom_z - cfg.watermark_overlap,
    ))


# ---------------------------------------------------------------- nose
def build_nose(cfg: SubmarineConfig) -> list[PartSpec]:
    profile = FishEnvelopeProfile(cfg)
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

    if cfg.fish_fairing_enabled:
        fairing, target_envelope = _fairing_for_region(
            cfg,
            profile,
            "nose",
            -cfg.bladder_protrude,
            cfg.nose_length,
        )
        nose, env = _add_fish_envelope(
            nose,
            env,
            fairing,
            target_envelope,
            _fish_crests(cfg, profile, "nose", -cfg.bladder_protrude, cfg.nose_length),
        )

    return [
        PartSpec(
            name="nose_body",
            solid=nose,
            envelope=env,
            watertight=True,
            print_rotation=(0.0, -90.0, 0.0),
            note="freeform fish fairing; print standing on rear face, nose tip up",
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
    profile = FishEnvelopeProfile(cfg)
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
        if cfg.fish_fairing_enabled:
            fairing, target_envelope = _fairing_for_region(
                cfg,
                profile,
                "chain",
                drum_x0,
                drum_x0 + drum_len,
            )
            solid, env = _add_fish_envelope(
                solid,
                env,
                fairing,
                target_envelope,
                _fish_crests(cfg, profile, "chain", drum_x0, drum_x0 + drum_len),
            )
        parts.append(
            PartSpec(
                name=f"segment_{i + 1:02d}",
                solid=solid,
                envelope=env,
                watertight=True,
                note="freeform fish-fairing buoyancy segment, hinge pin vertical",
            )
        )
    return parts


# ------------------------------------------------------------- capsule
def build_capsule(cfg: SubmarineConfig) -> list[PartSpec]:
    profile = FishEnvelopeProfile(cfg)
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

    # The capsule's open service bore prevents a direct radial attachment of
    # its two hinge ears. Connect each ear below the tongue sweep, between the
    # bayonet-lug sectors, and join the web to the outer shell only outside the
    # cap-plug radius. This preserves cap removal and full ±10° tongue motion.
    ear_y = cfg.tongue_t / 2 + cfg.hinge_clearance + cfg.ear_t / 2
    tongue_sweep_keepout_z = -9.0
    shell_attach_z = cfg.capsule_inner_r + 0.2
    for side in (-1.0, 1.0):
        ear_outer_y = ear_y + cfg.ear_t / 2
        y0, y1 = sorted((
            side * (ear_outer_y - 0.55),
            side * (ear_outer_y + 1.45),
        ))
        forward_web = box(
            oc,
            x_cf,
            y0,
            y1,
            -od / 2 - 0.5,
            tongue_sweep_keepout_z,
        )
        outer_tab = box(
            x_cf - 0.5,
            x_cf + 2.0,
            y0,
            y1,
            -od / 2 - 0.5,
            -shell_attach_z,
        )
        shell = shell.union(forward_web).union(outer_tab)
        env = env.union(forward_web).union(outer_tab)

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

    if cfg.fish_fairing_enabled:
        fairing, target_envelope = _fairing_for_region(
            cfg,
            profile,
            "capsule",
            x_cf,
            x_rear,
        )
        shell, env = _add_fish_envelope(
            shell,
            env,
            fairing,
            target_envelope,
            _fish_crests(cfg, profile, "capsule", x_cf + 8.0, x_rear - 3.0),
        )
        shell, env = _add_capsule_fins(shell, env, cfg, profile)

        # Protected interface: the additive fairing may reach below the round
        # pressure core near the keel. Re-cut the unchanged plug bore/thread
        # after every aesthetic union so the v1.0 interface remains exact.
        shell = shell.cut(
            cyl_x(kx + 30, kx + 41, cfg.keel_plug_d / 2, 0, zboss)
        )
        shell = shell.cut(
            cyl_x(kx + 41, kx + 45, 8.2, 0, zboss)
        )
        shell = cut_internal_thread(
            shell,
            cfg.keel_plug_d / 2,
            cfg.keel_plug_pitch,
            1.2,
            6.0,
            axis="X",
            z_offset=kx + 35.0,
            cz=zboss,
        )

    # Last planned solid-geometry change: canonical recessed product identity.
    if cfg.watermark_enabled:
        watermark_cutter = _keel_watermark_cutter(cfg)
        shell = shell.cut(watermark_cutter)
        env = env.cut(watermark_cutter)

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
            note="freeform fish electronics hull; keel down, pectoral fins canted for support reduction",
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
def caudal_outline_points(
    cfg: SubmarineConfig,
    root_x: float,
    rocker_tip_z: float,
) -> list[tuple[float, float]]:
    """Smooth caudal outline with baseline-equivalent projected blade area."""
    centre = cfg.caudal_visual_center_z
    half_span = cfg.caudal_span / 2.0
    return [
        (root_x + 6.0, rocker_tip_z + 5.0),
        (root_x + 23.0, centre - 5.0),
        (root_x + 41.0, centre + 23.0),
        (root_x + 61.0, centre + half_span),
        (root_x + 53.0, centre + 13.0),
        (root_x + 41.0, centre),
        (root_x + 53.0, centre - 13.0),
        (root_x + 61.0, centre - half_span),
        (root_x + 41.0, centre - 24.0),
        (root_x + 23.0, centre - 12.0),
        (root_x + 6.0, rocker_tip_z - 5.0),
    ]


def caudal_projected_area_mm2(cfg: SubmarineConfig) -> float:
    """Exact XZ area of the spline-defined caudal blade, excluding the tang."""
    sol = solve_rocker(cfg)
    root_x = cfg.capsule_end_x + 2.0 + 3.0 + 0.2
    rocker_tip_z = sol.pivot_z - cfg.rocker_arm_tip_r
    points = caudal_outline_points(cfg, root_x, rocker_tip_z)
    wire = (
        cq.Workplane("XZ")
        .moveTo(*points[0])
        .spline(points[1:6], includeCurrent=True)
        .spline(points[6:], includeCurrent=True)
        .lineTo(*points[0])
        .close()
        .val()
    )
    return cq.Face.makeFromWires(wire).Area()


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
    sleeve = sleeve.cut(box(x_rear + 6.0, x_rear + 12.0, -0.4, 0.4, -2.4, 2.4))
    sleeve_note = "one-piece split sleeve; glue onto motor shaft with a drop of CA"

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

    # Tail fin: invariant tang/socket plus a symmetric fish-like caudal blade.
    fx0 = hub_x0
    tang = box(fx0 + 1, fx0 + 11, -cfg.fin_t / 2, cfg.fin_t / 2, tip_z - 7, tip_z + 5)
    tang = tang.cut(cyl_z(tip_z - 8, tip_z + 6, 1.25, fx0 + 6, 0))
    blade_pts = caudal_outline_points(cfg, fx0, tip_z)
    wp = (
        cq.Workplane("XZ")
        .moveTo(*blade_pts[0])
        .spline(blade_pts[1:6], includeCurrent=True)
        .spline(blade_pts[6:], includeCurrent=True)
        .lineTo(*blade_pts[0])
        .close()
    )
    blade = wp.extrude(-cfg.fin_t).translate((0, -cfg.fin_t / 2, 0))
    fin = tang.union(blade)

    return [
        PartSpec("crank_disc", solid=disc, print_rotation=(0.0, 90.0, 0.0),
                 note="clamp onto shaft sleeve with a zip tie through the slit"),
        PartSpec("shaft_sleeve", solid=sleeve, print_rotation=(0.0, -90.0, 0.0),
                 note=sleeve_note),
        PartSpec("tail_rocker", solid=rocker, print_rotation=(0.0, 90.0, 0.0),
                 note="grease the crank pin slot; rides on the pivot pin"),
        PartSpec("tail_fin", solid=fin, print_rotation=(0.0, 90.0, 0.0),
                 note="symmetric caudal fin; unchanged tang/socket, pin through Z"),
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
