#!/usr/bin/env python3
"""MM-FUR-001 — deterministic geometry checks. Fail-closed.

These are GEOMETRY checks on the generated model. They prove internal
consistency and buildability of the drawing set. They prove NOTHING about the
real niche, the real floor, timber flatness or strength: those are the physical
acceptance criteria A-01..A-10 in design-spec.yaml, all NOT_RUN.

Run: python3 source/checks.py   -> exports/geometry-checks.json, exit 1 on FAIL
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime, timezone

import yaml
from shapely.geometry import Polygon
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from corner_cabinet import build, make_parts, battens   # noqa: E402

SQ2 = math.sqrt(2.0)
R = []


def check(cid, name, ok, detail):
    R.append({"id": cid, "check": name, "result": "PASS" if ok else "FAIL",
              "detail": detail})


def main():
    P = yaml.safe_load(open(os.path.join(HERE, "params.yaml"), encoding="utf-8"))
    G = build(P)
    parts = make_parts(P, G)
    T = P["panel"]["thickness_mm"]
    niche = (P["niche"]["wall_1_mm"], P["niche"]["wall_2_mm"])
    foot = Polygon(G["footprint_outer"])

    # C-01 closed envelope, including door thickness, inside the niche
    mx = max(x for p in parts if p.pid != "P11" for x, y in p.plan)
    my = max(y for p in parts if p.pid != "P11" for x, y in p.plan)
    for hand, row, pl, zb, zt in G["door_defs"]:
        mx = max(mx, max(x for x, y in pl)); my = max(my, max(y for x, y in pl))
    check("C-01", "closed cabinet incl. door thickness stays inside the niche",
          mx <= niche[0] and my <= niche[1],
          f"max x {mx:.1f} <= {niche[0]:.0f}, max y {my:.1f} <= {niche[1]:.0f}; "
          f"spare {niche[0]-mx:.1f} / {niche[1]-my:.1f} mm")

    # C-02 door tip at the 90 deg PARKED position is inside the niche
    t90 = G["door_tip_envelope"][90]
    check("C-02", "door tip at the 90 deg parked position stays inside the niche",
          t90[0] <= niche[0] and t90[1] <= niche[1],
          f"tip {t90}; max usable opening angle {G['max_open_angle_inside_niche_deg']} deg. "
          f"This is the END position only - see C-18 for the swept path, which does "
          f"leave the niche.")

    # C-18 swept path: the door must never strike either wall, and the room-side
    # clear space it demands must be stated. C-02 alone was incomplete: it tested
    # the end position and said nothing about the arc travelled to get there.
    piv = G["door_pivot"]
    dw = G["door_w"]
    f, nout = G["f"], G["n_out"]
    hit_wall, max_x, max_y, max_r = False, 0.0, 0.0, 0.0
    for i in range(0, 361):
        a = math.radians(i * 90.0 / 360.0)                 # 0..90 deg of opening
        for sgn in (+1, -1):                               # both doors of a row
            dx = -sgn * f[0] * math.cos(a) + nout[0] * math.sin(a)
            dy = -sgn * f[1] * math.cos(a) + nout[1] * math.sin(a)
            for frac in (0.25, 0.5, 0.75, 1.0):            # sample along the leaf
                px, py = piv[0] + dx * dw * frac, piv[1] + dy * dw * frac
                if px < 0.0 or py < 0.0:
                    hit_wall = True
                max_x, max_y = max(max_x, px), max(max_y, py)
                max_r = max(max_r, math.hypot(px, py))
    check("C-18", "door leaf never strikes either niche wall while swinging",
          not hit_wall,
          f"swept quarter circle of radius {dw:.0f} mm about the front midpoint "
          f"{piv}. REQUIRED CLEAR SPACE, room side: the leaf reaches x={max_x:.0f} mm "
          f"and y={max_y:.0f} mm from the corner, i.e. up to {max_x-niche[0]:.0f} mm "
          f"BEYOND the 1 m end of each wall, at {max_r:.0f} mm from the corner at its "
          f"furthest. Nothing may stand in that quarter circle. The surroundings beyond "
          f"the niche mouth are UNMEASURED - preflight IF-EXT-KIN-KOT-VOLUME-004, E1.")

    # C-19 feet are spread and sit clear of the panel edges
    p01f = [p for p in parts if p.pid == "P01"][0]
    fs = [(h.x, h.y) for h in p01f.holes if h.kind == "foot_transfer"]
    poly01 = Polygon(p01f.local)
    from shapely.geometry import Point
    half = P["hardware"]["foot_plate_pattern_mm"] / 2 + 6.0
    inside = all(poly01.contains(Point(a, b).buffer(half)) for a, b in fs)
    pair = min(math.dist(a, b) for i, a in enumerate(fs) for b in fs[i + 1:])
    check("C-19", "feet are inside the bottom panel and adequately spread",
          inside and pair >= 200.0,
          f"{len(fs)} feet; closest pair {pair:.0f} mm apart (>= 200 required); every "
          f"mounting plate fully inside the panel with a {half-20:.0f} mm margin")

    # C-03 every carcass part inside the footprint
    bad = []
    for p in parts:
        if p.pid in ("P10", "P11"):
            continue
        if not foot.buffer(0.05).contains(Polygon(p.plan)):
            bad.append(p.pid)
    check("C-03", "every carcass part lies inside the footprint pentagon",
          not bad, f"outside: {bad}" if bad else "P01-P09 all inside")

    # C-04 no solid overlap between distinct vertical parts
    verts = [p for p in parts if p.pid in ("P03", "P04", "P05", "P06", "P07", "P09")]
    ov = []
    for i, a in enumerate(verts):
        for b in verts[i + 1:]:
            if not (a.z1 <= b.z0 + 1e-6 or b.z1 <= a.z0 + 1e-6):
                inter = Polygon(a.plan).intersection(Polygon(b.plan)).area
                if inter > 1.0:
                    ov.append(f"{a.pid}/{b.pid} {inter:.1f} mm2")
    check("C-04", "vertical panels do not interpenetrate", not ov,
          f"overlaps: {ov}" if ov else "no plan overlap between co-height verticals")

    # C-05 horizontal parts do not interpenetrate
    hz = [p for p in parts if p.pid in ("P01", "P02", "P08", "P11")]
    zov = [f"{a.pid}/{b.pid}" for i, a in enumerate(hz) for b in hz[i + 1:]
           if not (a.z1 <= b.z0 + 1e-6 or b.z1 <= a.z0 + 1e-6)]
    check("C-05", "horizontal plates are stacked without z overlap", not zov,
          f"overlap: {zov}" if zov else
          f"bottom {G['z_bot_u']:.0f}-{G['z_bot_t']:.0f}, shelf {G['z_shelf_b']:.0f}-"
          f"{G['z_shelf_t']:.0f}, top {G['z_top_u']:.0f}-{G['z_top_t']:.0f}, "
          f"glass {G['z_top_t']:.0f}-{G['z_top_t']+P['glass']['thickness_mm']:.0f}")

    # C-06 mid shelf clears the surrounding vertical panels
    shelf = Polygon(G["shelf_poly"])
    surrounding = [q for q in parts if q.pid in ("P03", "P04", "P05", "P06")]
    clash = [q.pid for q in surrounding
             if Polygon(q.plan).intersection(shelf).area > 1.0]
    check("C-06", "mid shelf clears the four surrounding vertical panels",
          not clash, f"clash: {clash}" if clash else
          f"clearance {P['shelf']['clearance_mm']:.0f} mm to each inner face")

    # C-07 glass inside the top plate outline
    top = Polygon([p for p in parts if p.pid == "P02"][0].plan)
    glass = Polygon(G["glass_poly"])
    check("C-07", "glass outline lies inside the top-plate outline",
          top.contains(glass),
          f"inset {P['glass']['inset_mm']:.0f} mm; glass {glass.area/1e6:.3f} m2 in "
          f"top {top.area/1e6:.3f} m2")

    # C-08 every hole inside its panel with an edge margin
    viol = []
    for p in parts:
        poly = Polygon(p.local)
        allh = list(p.holes) + [h for hs in p.drill_variants.values() for h in hs]
        for h in allh:
            from shapely.geometry import Point
            if not poly.contains(Point(h.x, h.y).buffer(h.dia / 2 + 3.0)):
                viol.append(f"{p.pid} {h.kind} ({h.x},{h.y}) d{h.dia}")
    check("C-08", "every hole sits inside its panel with a 3 mm edge margin",
          not viol, f"violations: {viol}" if viol else
          f"{sum(len(p.holes)+sum(len(v) for v in p.drill_variants.values()) for p in parts)} holes checked")

    # C-09 cup depth leaves material
    cd = P["doors"]["cup_depth_mm"]
    check("C-09", "hinge cup does not break through the door",
          cd < T - 3.0, f"cup {cd} mm in {T:.0f} mm door leaves {T-cd:.1f} mm")

    # C-10 no coaxial mounting-plate holes on the two partition faces
    worst = []
    for p in parts:
        if p.pid not in ("P07", "P09"):
            continue
        a = [h for h in p.holes if h.face == "SIDE-1"]
        b = [h for h in p.holes if h.face == "SIDE-2"]
        d = min(abs(x.y - y.y) for x in a for y in b if abs(x.x - y.x) < 0.01)
        worst.append((p.pid, d))
    ok = all(d >= 8.0 for _, d in worst)
    check("C-10", "no mounting-plate hole pair is coaxial through the partition",
          ok, f"closest opposite-face vertical separation per part: "
              f"{[(a, f'{b:.0f} mm') for a, b in worst]}; "
              f"two {P['doors']['plate_hole_depth_mm']:.0f} mm holes would need "
              f"{2*P['doors']['plate_hole_depth_mm']:.0f} mm in a {T:.0f} mm panel")

    # C-11 carcass screws clear of the foot mounting plates
    p01 = [p for p in parts if p.pid == "P01"][0]
    feet = [(h.x, h.y) for h in p01.holes if h.kind == "foot_transfer"]
    scr = [(h.x, h.y) for h in p01.holes if h.kind == "screw_through"]
    dmin = min(math.dist(s, f) for s in scr for f in feet)
    need = P["hardware"]["foot_plate_pattern_mm"] / 2 + 15.0
    check("C-11", "every carcass screw clears every foot mounting plate",
          dmin >= need,
          f"closest screw-to-foot {dmin:.1f} mm, required >= {need:.0f} mm "
          f"({len(scr)} screws x {len(feet)} feet)")

    # C-12 door widths add up to the front
    dr = P["doors"]
    total = 2 * G["door_w"] + dr["gap_horizontal_mm"]
    check("C-12", "two door widths plus the centre gap fit the diagonal front",
          0 <= G["front_len"] - total < 2.0,
          f"2 x {G['door_w']:.0f} + {dr['gap_horizontal_mm']:.0f} = {total:.0f} mm on a "
          f"{G['front_len']:.1f} mm front; residual reveal {G['outer_reveal']:.2f} mm per end")

    # C-13 door heights add up between the feet and the top plate
    dh_total = 2 * G["door_h"] + dr["gap_vertical_mm"] + dr["bottom_clearance_mm"]
    span = G["z_top_u"] - G["z_bot_u"]
    check("C-13", "two door heights plus gaps fit under the top plate",
          0 <= span - dh_total < 2.0,
          f"{dr['bottom_clearance_mm']:.0f} + {G['door_h']:.0f} + "
          f"{dr['gap_vertical_mm']:.0f} + {G['door_h']:.0f} = {dh_total:.0f} mm in a "
          f"{span:.0f} mm opening; top-plate edge stays {G['top_edge_visible']:.0f} mm proud")

    # C-14 half-overlay value is in the range real Mittelanschlag hinges cover
    ov_mm = G["door_overlay_on_partition"]
    check("C-14", "door overlay on the partition is within half-overlay hinge range",
          6.0 <= ov_mm <= 10.0,
          f"overlay {ov_mm} mm per door on a {T:.0f} mm partition. STILL AN OPEN ITEM: "
          f"the concrete hinge article's adjustment range is unverified")

    # C-15 top plate exactly at the required height
    check("C-15", "top face of the timber plate is at the required height",
          abs(G["z_top_t"] - P["heights"]["total_mm"]) < 1e-6,
          f"{G['z_top_t']:.0f} mm (owner requirement {P['heights']['total_mm']:.0f} mm); "
          f"glass brings the object to {G['z_top_t']+P['glass']['thickness_mm']:.0f} mm")

    # C-16 both compartments equal and usable
    check("C-16", "both compartments have equal clear height",
          G["compartment_h"] > 380,
          f"2 x {G['compartment_h']:.0f} mm clear")

    # C-17 pentagon panels need exactly one non-90-degree cut each
    pent = [p for p in parts if len(p.local) == 5]
    check("C-17", "each pentagon panel is one square blank plus one straight cut",
          len(pent) == 4,
          f"{[p.pid for p in pent]} - P01/P02/P08 timber plus P11 glass; every other "
          f"part is a plain rectangle")

    fails = [r for r in R if r["result"] == "FAIL"]
    out = {
        "product": "MM-FUR-001", "revision": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0)
                        .isoformat().replace("+00:00", "Z"),
        "scope": "GEOMETRY ONLY. Internal consistency and buildability of the generated "
                 "drawing set. Says nothing about the real niche, floor, timber flatness "
                 "or strength - those are acceptance criteria A-01..A-10, all NOT_RUN.",
        "checks_run": len(R), "failed": len(fails),
        "verdict": "PASS" if not fails else "FAIL",
        "checks": R,
    }
    path = os.path.join(ROOT, "exports", "geometry-checks.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for r in R:
        print(f"  {r['result']:4s} {r['id']}  {r['check']}")
        print(f"          {r['detail']}")
    print(f"\n{out['verdict']}: {len(R)-len(fails)}/{len(R)} geometry checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
