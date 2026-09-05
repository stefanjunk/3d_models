#!/usr/bin/env python3
"""MM-FUR-001 — Corner cabinet with glass display top.

Single source of truth for the geometry. Reads source/params.yaml and writes
every derived artifact into exports/. Nothing downstream may be hand-edited:
change params.yaml and re-run.

Coordinate system (room frame, millimetres):
    origin  = the inside corner of the niche at floor level
    +X      = along niche wall 1
    +Y      = along niche wall 2
    +Z      = up
Every part of this cabinet is a prism in Z, so each part is defined by a plan
polygon plus a z range. That is what makes the whole thing cuttable from flat
panels.

Run:  python3 source/corner_cabinet.py [--outdir exports]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

import yaml

SQ2 = math.sqrt(2.0)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


# --------------------------------------------------------------------------- #
# data model
# --------------------------------------------------------------------------- #
@dataclass
class Hole:
    face: str            # which face of the part the hole is drilled on
    x: float             # mm from that face's x datum edge
    y: float             # mm from that face's y datum edge
    dia: float
    depth: float | None  # None = through
    kind: str
    note: str = ""


@dataclass
class Part:
    pid: str
    name_de: str
    name_en: str
    count: int
    material: str
    thickness: float
    plan: list                      # plan polygon, room frame
    z0: float
    z1: float
    local: list                     # flat 2D outline, part frame, origin at bbox min
    faces: dict = field(default_factory=dict)   # face name -> datum description
    holes: list = field(default_factory=list)
    cut_note: str = ""
    drill_variants: dict = field(default_factory=dict)  # variant -> [Hole]

    @property
    def blank(self):
        xs = [p[0] for p in self.local]
        ys = [p[1] for p in self.local]
        return round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)

    @property
    def net_area_m2(self):
        return poly_area(self.local) / 1e6

    @property
    def blank_area_m2(self):
        l, w = self.blank
        return l * w / 1e6


def poly_area(poly):
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


def offset_pentagon(x0, y0, x1, y1, k, inset):
    """Inward offset of the footprint pentagon.

    The pentagon is bounded by x=x0, y=y0, x=x1, y=y1 and the 45 deg front
    x+y=k. Offsetting each bounding line inward by `inset` keeps it a pentagon;
    the front line moves by inset*sqrt(2) in (x+y).
    """
    a, b = x0 + inset, y0 + inset
    c, d = x1 - inset, y1 - inset
    kk = k - inset * SQ2
    # vertices: corner, along wall 1, front-right, front-left, along wall 2
    return [(a, b), (c, b), (c, kk - c), (kk - d, d), (a, d)]


def rect_plan(p0, u, length, thickness):
    """Plan polygon of a vertical panel: from p0 along unit vector u for
    `length`, thickness applied along u rotated +90 deg."""
    ux, uy = u
    nx, ny = -uy, ux
    x0, y0 = p0
    return [
        (x0, y0),
        (x0 + ux * length, y0 + uy * length),
        (x0 + ux * length + nx * thickness, y0 + uy * length + ny * thickness),
        (x0 + nx * thickness, y0 + ny * thickness),
    ]


# --------------------------------------------------------------------------- #
# model
# --------------------------------------------------------------------------- #
def build(P):
    n, pn, hh, fp, dr, sh, gl, hw = (
        P["niche"], P["panel"], P["heights"], P["footprint"],
        P["doors"], P["shelf"], P["glass"], P["hardware"],
    )
    T = pn["thickness_mm"]
    G = {}

    # ---- footprint -------------------------------------------------------- #
    G["leg_1"] = leg1 = n["wall_1_mm"] - n["back_gap_mm"] - n["end_gap_mm"]
    G["leg_2"] = leg2 = n["wall_2_mm"] - n["back_gap_mm"] - n["end_gap_mm"]
    if abs(leg1 - leg2) > 1e-9:
        raise SystemExit("This revision assumes both legs equal; asymmetric niche needs a source change.")
    leg = leg1
    x0 = y0 = n["back_gap_mm"]
    x1 = x0 + leg
    y1 = y0 + leg
    s = fp["side_return_mm"]
    K = x1 + y0 + s                                  # front plane: x + y = K
    C = (x1, y0 + s)                                 # front end at wall 1
    D = (x0 + s, y1)                                 # front end at wall 2
    front_len = SQ2 * (x1 - (x0 + s))
    G.update(x0=x0, y0=y0, x1=x1, y1=y1, K=K, C=C, D=D,
             front_len=front_len, side_return=s, leg=leg)
    G["depth_corner_to_front"] = (K - x0 - y0) / SQ2
    G["footprint_outer"] = outer = [(x0, y0), (x1, y0), C, D, (x0, y1)]
    G["footprint_area_m2"] = poly_area(outer) / 1e6

    # ---- heights ---------------------------------------------------------- #
    z_bot_u = hh["foot_mm"]
    z_bot_t = z_bot_u + T
    z_top_u = hh["total_mm"] - T
    z_top_t = hh["total_mm"]
    vert_h = z_top_u - z_bot_t
    comp = (vert_h - T) / 2.0
    z_shelf_b = z_bot_t + comp
    z_shelf_t = z_shelf_b + T
    G.update(z_bot_u=z_bot_u, z_bot_t=z_bot_t, z_top_u=z_top_u, z_top_t=z_top_t,
             vert_h=vert_h, compartment_h=comp,
             z_shelf_b=z_shelf_b, z_shelf_t=z_shelf_t)

    # ---- doors ------------------------------------------------------------ #
    door_zone_b = z_bot_u + dr["bottom_clearance_mm"]
    door_h_exact = (z_top_u - door_zone_b - dr["gap_vertical_mm"]) / 2.0
    door_h = math.floor(door_h_exact)
    door_w = math.floor((front_len - dr["gap_horizontal_mm"]) / 2.0)
    z_low_b = door_zone_b
    z_low_t = z_low_b + door_h
    z_up_b = z_low_t + dr["gap_vertical_mm"]
    z_up_t = z_up_b + door_h
    outer_reveal = (front_len - 2 * door_w - dr["gap_horizontal_mm"]) / 2.0
    G.update(door_w=door_w, door_h=door_h, door_h_exact=round(door_h_exact, 2),
             z_low_b=z_low_b, z_low_t=z_low_t, z_up_b=z_up_b, z_up_t=z_up_t,
             outer_reveal=round(outer_reveal, 2),
             door_overlay_on_partition=round((T - dr["gap_horizontal_mm"]) / 2.0, 2),
             top_edge_visible=round(z_top_t - z_up_t, 1))

    # ---- shelf ------------------------------------------------------------ #
    shelf_poly = offset_pentagon(x0, y0, x1, y1, K, T + sh["clearance_mm"])
    # front edge stays flush with the front plane (doors overlay it)
    cl = T + sh["clearance_mm"]
    shelf_poly = [(x0 + cl, y0 + cl), (x1 - cl, y0 + cl),
                  (x1 - cl, K - (x1 - cl)), (K - (y1 - cl), y1 - cl),
                  (x0 + cl, y1 - cl)]
    G["shelf_poly"] = shelf_poly
    G["shelf_front_len"] = SQ2 * ((x1 - cl) - (K - (y1 - cl)))

    # ---- centre partition ------------------------------------------------- #
    M = (K / 2.0, K / 2.0)                       # front-plane midpoint
    f = (-1 / SQ2, 1 / SQ2)                      # along front, C -> D
    ninw = (-1 / SQ2, -1 / SQ2)                  # front normal, into cabinet
    nout = (1 / SQ2, 1 / SQ2)                    # front normal, into room
    pd = fp["partition_depth_mm"]
    pr = (M[0] - f[0] * T / 2, M[1] - f[1] * T / 2)   # right-face front corner
    part_plan = [pr,
                 (pr[0] + ninw[0] * pd, pr[1] + ninw[1] * pd),
                 (pr[0] + ninw[0] * pd + f[0] * T, pr[1] + ninw[1] * pd + f[1] * T),
                 (pr[0] + f[0] * T, pr[1] + f[1] * T)]
    G.update(M=M, f=f, n_in=ninw, n_out=nout, partition_plan=part_plan,
             partition_right_front=pr, partition_depth=pd)

    # ---- glass ------------------------------------------------------------ #
    glass_poly = offset_pentagon(x0, y0, x1, y1, K, gl["inset_mm"])
    G["glass_poly"] = glass_poly
    G["glass_area_m2"] = poly_area(glass_poly) / 1e6
    G["glass_mass_kg"] = G["glass_area_m2"] * gl["density_kg_per_m2"]
    G["glass_front_len"] = SQ2 * (glass_poly[1][0] - glass_poly[3][0])

    # ---- door swing envelope --------------------------------------------- #
    # conservative pivot: the door's inner vertical edge in the front plane
    piv = (M[0] + f[0] * dr["gap_horizontal_mm"] / 2, M[1] + f[1] * dr["gap_horizontal_mm"] / 2)
    env = {}
    for ang in (85, 90, 95, 100, 110):
        a = math.radians(ang)
        # closed direction is -f (toward C) for the right door; rotate toward nout
        dx = -f[0] * math.cos(a) + nout[0] * math.sin(a)
        dy = -f[1] * math.cos(a) + nout[1] * math.sin(a)
        tip = (piv[0] - f[0]*0 + dx * door_w, piv[1] + dy * door_w)
        env[ang] = (round(tip[0], 1), round(tip[1], 1))
    G["door_pivot"] = (round(piv[0], 1), round(piv[1], 1))
    G["door_tip_envelope"] = env
    G["max_open_angle_inside_niche_deg"] = max(
        (a for a, t in env.items() if t[0] <= n["wall_1_mm"] and t[1] <= n["wall_2_mm"]),
        default=0)
    # outermost point of the closed cabinet including door thickness
    G["closed_max_x"] = round(C[0] + nout[0] * T, 1)
    G["closed_max_y"] = round(D[1] + nout[1] * T, 1)

    return G


# --------------------------------------------------------------------------- #
# parts
# --------------------------------------------------------------------------- #
def make_parts(P, G):
    T = P["panel"]["thickness_mm"]
    dr, hw = P["doors"], P["hardware"]
    mat = P["panel"]["material_primary"]
    x0, y0, x1, y1, K = G["x0"], G["y0"], G["x1"], G["y1"], G["K"]
    s = G["side_return"]
    leg = G["leg"]
    parts = []

    def loc(poly, ox, oy):
        return [(round(px - ox, 2), round(py - oy, 2)) for px, py in poly]

    # ---- P01 bottom panel ------------------------------------------------- #
    bot = Part(
        "P01", "Bodenplatte", "Bottom panel", 1, mat, T,
        G["footprint_outer"], G["z_bot_u"], G["z_bot_t"],
        loc(G["footprint_outer"], x0, y0),
        faces={
            "TOP": "Panel lying with the TOP face up. Origin = the 90 deg corner "
                   "between the two long straight edges (the niche corner). "
                   "x along the wall-1 edge, y along the wall-2 edge. Mark 'OBEN', "
                   "'Wand 1' and 'Wand 2' on this face before drilling.",
        },
        cut_note=f"Square blank {leg:.0f} x {leg:.0f} mm, then exactly ONE straight cut "
                 f"from (x={leg:.0f}, y={s:.0f}) to (x={s:.0f}, y={leg:.0f}). That cut is "
                 f"{G['front_len']:.1f} mm long and runs at 45 deg to both blank edges; it "
                 f"becomes the diagonal front. It removes a right triangle with "
                 f"{leg - s:.0f} mm legs.",
    )
    # screw-through holes into the vertical panel edges (drilled from the top face,
    # countersunk from below)
    feet = foot_positions(G, P)
    G["foot_positions"] = feet
    keepout = P["hardware"]["foot_plate_pattern_mm"] / 2 + 25.0   # plate half + margin

    def line_holes(p_from, p_to, pitch, inset=55.0):
        """Evenly spaced screw positions along a line, shifted clear of every foot
        mounting plate. A foot plate sits on the underside exactly where these
        through-holes are countersunk, so a coincident pair would be undrillable."""
        L = math.dist(p_from, p_to)
        n_h = max(2, int(round((L - 2 * inset) / pitch)) + 1)
        out = []
        for i in range(n_h):
            t = inset + (L - 2 * inset) * i / (n_h - 1)
            for cand in (t, t + 55.0, t - 55.0, t + 90.0, t - 90.0):
                if not (inset - 20 <= cand <= L - inset + 20):
                    continue
                px = p_from[0] + (p_to[0] - p_from[0]) * cand / L
                py = p_from[1] + (p_to[1] - p_from[1]) * cand / L
                if all(math.dist((px, py), fp) > keepout for fp in feet):
                    out.append((round(px, 1), round(py, 1)))
                    break
        return out

    cl = T / 2.0
    screw_lines = {
        "P03 Rueckwand Wand 2": ((x0 + cl, y0 + 0.0), (x0 + cl, y1)),
        "P04 Rueckwand Wand 1": ((x0 + T, y0 + cl), (x1, y0 + cl)),
        "P05 Seitenwange Wand 1": ((x1 - cl, y0 + T), (x1 - cl, y0 + s)),
        "P06 Seitenwange Wand 2": ((x0 + T, y1 - cl), (x0 + s, y1 - cl)),
    }
    for tgt, (a, b) in screw_lines.items():
        for px, py in line_holes(a, b, 120.0):
            bot.holes.append(Hole("TOP", round(px - x0, 1), round(py - y0, 1), 4.5, None,
                                  "screw_through",
                                  f"4.5 mm through + 9 mm countersink from BELOW; "
                                  f"4.5x50 screw into the bottom edge of {tgt}"))
    # partition centre line
    fmid = (K / 2.0, K / 2.0)
    prear = (fmid[0] + G["n_in"][0] * G["partition_depth"], fmid[1] + G["n_in"][1] * G["partition_depth"])
    for px, py in line_holes(fmid, prear, 120.0):
        bot.holes.append(Hole("TOP", round(px - x0, 1), round(py - y0, 1), 4.5, None,
                              "screw_through",
                              "4.5 mm through + 9 mm countersink from BELOW; "
                              "4.5x50 screw into the bottom edge of P07 lower centre partition"))
    # feet
    for i, (px, py) in enumerate(feet, 1):
        bot.holes.append(Hole("TOP", round(px - x0, 1), round(py - y0, 1), 2.0, None,
                              "foot_transfer",
                              f"Foot F{i}: 2 mm through-hole as a transfer mark only. "
                              f"Flip the panel and screw the foot plate centred on it "
                              f"({hw['foot_plate_pattern_mm']:.0f} mm screw square, "
                              f"4 x 4.0 mm pilot x 12 mm deep, from BELOW)."))
    parts.append(bot)

    # ---- P02 top plate ---------------------------------------------------- #
    top = Part(
        "P02", "Deckplatte", "Top display plate", 1, mat, T,
        G["footprint_outer"], G["z_top_u"], G["z_top_t"],
        loc(G["footprint_outer"], x0, y0),
        faces={"TOP": "Show face. NO holes at all - this is the display surface under "
                      "the glass. Choose the flattest, cleanest side of the blank."},
        cut_note=f"Identical blank to P01: {leg:.0f} x {leg:.0f} mm square plus the same "
                 f"45 deg diagonal cut. Cut both from one setup so the outlines match.",
    )
    parts.append(top)

    # ---- P08 mid shelf ---------------------------------------------------- #
    sp = G["shelf_poly"]
    sx = min(p[0] for p in sp); sy = min(p[1] for p in sp)
    shelf = Part(
        "P08", "Mittelboden (Einlegeboden)", "Fixed mid shelf", 1, mat, T,
        sp, G["z_shelf_b"], G["z_shelf_t"], loc(sp, sx, sy),
        faces={"TOP": "Either face. Origin = the 90 deg corner between the two long "
                      "straight edges. No holes; screws come from below through the battens."},
        cut_note="Square blank {0:.0f} x {0:.0f} mm plus one 45 deg diagonal cut, "
                 "length {1:.1f} mm.".format(max(shelf_blank(sp)), G["shelf_front_len"]),
    )
    parts.append(shelf)

    # ---- P03 / P04 back panels -------------------------------------------- #
    p3 = rect_plan((x0 + T, y0), (0, 1), leg, T)           # along wall 2, x0..x0+T
    back2 = Part(
        "P03", "Rueckwand Wandseite 2", "Back panel, wall 2", 1, mat, T,
        p3, G["z_bot_t"], G["z_top_u"],
        [(0, 0), (leg, 0), (leg, G["vert_h"]), (0, G["vert_h"])],
        faces={"REF": "Inner face (towards the cabinet interior). x from the REAR edge "
                      "(the niche-corner end), y from the BOTTOM edge."},
        cut_note="Plain rectangle, all cuts 90 deg.",
    )
    parts.append(back2)

    p4 = rect_plan((x0 + T, y0 + T), (1, 0), leg - T, -T)   # along wall 1
    back1 = Part(
        "P04", "Rueckwand Wandseite 1", "Back panel, wall 1", 1, mat, T,
        p4, G["z_bot_t"], G["z_top_u"],
        [(0, 0), (leg - T, 0), (leg - T, G["vert_h"]), (0, G["vert_h"])],
        faces={"REF": "Inner face. x from the REAR edge (butts against P03), y from the BOTTOM edge."},
        cut_note="Plain rectangle, all cuts 90 deg. 18 mm shorter than P03 because it "
                 "butts against the inner face of P03 at the corner.",
    )
    parts.append(back1)

    # ---- P05 / P06 side returns ------------------------------------------- #
    sr_len = s - T
    p5 = rect_plan((x1 - T, y0 + T), (0, 1), sr_len, -T)
    side1 = Part(
        "P05", "Seitenwange Wandseite 1", "Side return, wall 1 end", 1, mat, T,
        p5, G["z_bot_t"], G["z_top_u"],
        [(0, 0), (sr_len, 0), (sr_len, G["vert_h"]), (0, G["vert_h"])],
        faces={"REF": "Inner face. x from the REAR edge (butts against P04), y from the BOTTOM edge."},
        cut_note="Plain rectangle, all cuts 90 deg.",
    )
    p6 = rect_plan((x0 + T, y1 - T), (1, 0), sr_len, T)
    side2 = Part(
        "P06", "Seitenwange Wandseite 2", "Side return, wall 2 end", 1, mat, T,
        p6, G["z_bot_t"], G["z_top_u"],
        [(0, 0), (sr_len, 0), (sr_len, G["vert_h"]), (0, G["vert_h"])],
        faces={"REF": "Inner face. x from the REAR edge (butts against P03), y from the BOTTOM edge."},
        cut_note="Plain rectangle, all cuts 90 deg. Mirror twin of P05.",
    )
    parts += [side1, side2]

    # ---- P07 / P09 centre partitions -------------------------------------- #
    pd = G["partition_depth"]
    for pid, z0, z1, nm in (("P07", G["z_bot_t"], G["z_shelf_b"], "unten"),
                            ("P09", G["z_shelf_t"], G["z_top_u"], "oben")):
        pl = [tuple(v) for v in G["partition_plan"]]
        prt = Part(
            pid, f"Mittelsteg {nm}", f"Centre partition, {'lower' if nm=='unten' else 'upper'}",
            1, mat, T, pl, z0, z1,
            [(0, 0), (pd, 0), (pd, z1 - z0), (0, z1 - z0)],
            faces={
                "SIDE-1": "Face towards the wall-1 compartment. x from the FRONT edge, "
                          "y from the BOTTOM edge. Mark FRONT and BOTTOM before drilling.",
                "SIDE-2": "Face towards the wall-2 compartment. x from the FRONT edge, "
                          "y from the BOTTOM edge (same datums, read on the other face).",
            },
            cut_note="Plain rectangle, all cuts 90 deg. Both partitions identical.",
        )
        # hinge mounting-plate holes, one pair per hinge, per face
        for face, cup_from_end in (("SIDE-1", dr["cup_from_end_right_mm"]),
                                   ("SIDE-2", dr["cup_from_end_left_mm"])):
            zb = G["z_low_b"] if pid == "P07" else G["z_up_b"]
            for cz in (zb + cup_from_end, zb + G["door_h"] - cup_from_end):
                for off in (-dr["plate_pitch_mm"] / 2, dr["plate_pitch_mm"] / 2):
                    prt.holes.append(Hole(
                        face, dr["plate_from_front_mm"], round(cz + off - z0, 1),
                        dr["plate_hole_dia_mm"], dr["plate_hole_depth_mm"],
                        "hinge_plate",
                        f"System-32 cross mounting plate, hinge centre at y="
                        f"{cz - z0:.1f} mm. Holes on the two faces are staggered by "
                        f"{dr['cup_from_end_right_mm'] - dr['cup_from_end_left_mm']:.0f} mm "
                        f"so no pair is coaxial in the {T:.0f} mm panel."))
        parts.append(prt)

    # ---- P10 doors -------------------------------------------------------- #
    dw, dh = G["door_w"], G["door_h"]
    C, Dp, f, nout = G["C"], G["D"], G["f"], G["n_out"]
    door_defs = []
    s_centre = G["front_len"] / 2.0
    half_gap = dr["gap_horizontal_mm"] / 2.0
    for hand, s_in, s_out in (("wall-1 side (SIDE-1 hinge face)", s_centre - half_gap, s_centre - half_gap - dw),
                              ("wall-2 side (SIDE-2 hinge face)", s_centre + half_gap, s_centre + half_gap + dw)):
        for row, (zb, zt) in (("lower", (G["z_low_b"], G["z_low_t"])),
                              ("upper", (G["z_up_b"], G["z_up_t"]))):
            a = (C[0] + f[0] * min(s_in, s_out), C[1] + f[1] * min(s_in, s_out))
            b = (C[0] + f[0] * max(s_in, s_out), C[1] + f[1] * max(s_in, s_out))
            pl = [a, b,
                  (b[0] + nout[0] * T, b[1] + nout[1] * T),
                  (a[0] + nout[0] * T, a[1] + nout[1] * T)]
            door_defs.append((hand, row, pl, zb, zt))
    G["door_defs"] = door_defs

    door = Part(
        "P10", "Tuer", "Door", 4, mat, T,
        door_defs[0][2], door_defs[0][3], door_defs[0][4],
        [(0, 0), (dw, 0), (dw, dh), (0, dh)],
        faces={"INNER": "Inner face (towards the cabinet). Lay the door INNER FACE UP with "
                        "the HINGE EDGE to the LEFT and the BOTTOM edge DOWN. x from the "
                        "hinge edge, y from the bottom edge. All four blanks are identical; "
                        "only the two cup heights differ between the drill variants."},
        cut_note="Plain rectangle, all cuts 90 deg. Four identical blanks.",
    )
    for variant, cfe in (("A: wall-1 side doors (2x)", dr["cup_from_end_right_mm"]),
                         ("B: wall-2 side doors (2x)", dr["cup_from_end_left_mm"])):
        hl = []
        for cy in (cfe, dh - cfe):
            hl.append(Hole("INNER", dr["hinge_edge_inset_mm"], cy,
                           dr["cup_diameter_mm"], dr["cup_depth_mm"], "hinge_cup",
                           f"35 mm Forstner bit, depth stop {dr['cup_depth_mm']} mm "
                           f"(leaves {T - dr['cup_depth_mm']:.1f} mm). Cup screws: mark "
                           f"through the fitted hinge, then 2.5 mm pilots."))
        hx = dw - dr["handle_from_outer_edge_mm"]
        for off in (-dr["handle_hole_pitch_mm"] / 2, dr["handle_hole_pitch_mm"] / 2):
            hl.append(Hole("INNER", hx, round(dh / 2 + off, 1),
                           dr["handle_hole_dia_mm"], None, "handle",
                           "Through-hole for the bow-handle M4 screw. Drill from the SHOW "
                           "face with a backing board to avoid tear-out."))
        door.drill_variants[variant] = hl
    parts.append(door)

    # ---- P11 glass -------------------------------------------------------- #
    gp = G["glass_poly"]
    gx = min(p[0] for p in gp); gy = min(p[1] for p in gp)
    glass = Part(
        "P11", "Glasplatte", "Glass top plate", 1,
        P["glass"]["type"], P["glass"]["thickness_mm"],
        gp, G["z_top_t"], G["z_top_t"] + P["glass"]["thickness_mm"],
        loc(gp, gx, gy),
        faces={"TOP": "No holes. Supply the glazier with exports/dxf/P11-glass.dxf."},
        cut_note="Made to measure by a glazier. TOUGHENED (ESG) - it cannot be recut, so "
                 "order it only after the built top plate has been measured.",
    )
    parts.append(glass)
    return parts


def shelf_blank(sp):
    xs = [p[0] for p in sp]; ys = [p[1] for p in sp]
    return round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)


def foot_positions(G, P):
    """Six feet, placed under the vertical panels wherever the mounting plate fits
    inside the bottom panel."""
    x0, y0, x1, y1, K = G["x0"], G["y0"], G["x1"], G["y1"], G["K"]
    T = P["panel"]["thickness_mm"]
    m = 35.0                                  # min centre distance to a panel edge
    along = 150.0                             # in from each end of the front
    behind = 70.0                             # behind the front plane
    f, nin = G["f"], G["n_in"]
    C, D = G["C"], G["D"]
    pts = [
        (x0 + m, y0 + m),                                     # niche corner
        (x1 - m, y0 + m),                                     # wall-1 end, rear
        (x0 + m, y1 - m),                                     # wall-2 end, rear
    ]
    # The two front feet are anchored to the FRONT, not to the side return. Tying
    # them to the side return put them 130 mm from the rear feet once the return
    # was shortened to 182 mm, which stopped spreading the load.
    pts.append((C[0] + f[0] * along + nin[0] * behind,
                C[1] + f[1] * along + nin[1] * behind))
    pts.append((D[0] - f[0] * along + nin[0] * behind,
                D[1] - f[1] * along + nin[1] * behind))
    # front centre, under the partition, set back from the front plane
    pts.append((K / 2.0 - behind / SQ2, K / 2.0 - behind / SQ2))
    return [(round(a, 1), round(b, 1)) for a, b in pts]


# --------------------------------------------------------------------------- #
# battens
# --------------------------------------------------------------------------- #
def battens(P, G):
    T = P["panel"]["thickness_mm"]
    B = P["hardware"]["batten_mm"]
    x0, y0, x1, y1 = G["x0"], G["y0"], G["x1"], G["y1"]
    cl = T + P["shelf"]["clearance_mm"]
    rows = []
    # horizontal shelf bearers, top face flush with the shelf underside
    rows.append(("L01", "Traglatte Rueckwand Wand 2", 1,
                 round((y1 - cl) - (y0 + cl + B), 1),
                 "Screwed to the inner face of P03, top edge at z="
                 f"{G['z_shelf_b']:.0f} mm. Carries the mid shelf."))
    rows.append(("L02", "Traglatte Rueckwand Wand 1", 1,
                 round((x1 - cl) - (x0 + cl + B), 1),
                 "Screwed to the inner face of P04, top edge at z="
                 f"{G['z_shelf_b']:.0f} mm."))
    rows.append(("L03", "Traglatte Seitenwange", 2,
                 round(G["side_return"] - T - cl - B, 1),
                 "Screwed to the inner faces of P05 and P06, top edge at z="
                 f"{G['z_shelf_b']:.0f} mm."))
    # vertical corner battens, in two pieces so the shelf passes through
    rows.append(("L04", "Eckleiste unten", 3, round(G["z_shelf_b"] - G["z_bot_t"], 1),
                 "Inside vertical corner batten, lower section, in the three inside "
                 "corners P03/P04, P04/P05 and P03/P06. Its top edge also carries the "
                 "shelf corner, so the shelf needs no notch."))
    rows.append(("L05", "Eckleiste oben", 3, round(G["z_top_u"] - G["z_shelf_t"], 1),
                 "Same three corners, upper section."))
    total = sum(r[2] * r[3] for r in rows)
    return rows, total


# --------------------------------------------------------------------------- #
# nesting (shelf / guillotine, honest and simple)
# --------------------------------------------------------------------------- #
def nest(blanks, sheet_l, sheet_w, kerf):
    items = []
    for pid, name, l, w, count in blanks:
        for i in range(count):
            items.append([pid, name, max(l, w), min(l, w)])
    items.sort(key=lambda it: -it[2])
    sheets = []
    for it in items:
        placed = False
        for sh in sheets:
            for row in sh["rows"]:
                for (a, b) in ((it[2], it[3]), (it[3], it[2])):
                    if b <= row["h"] + 1e-9 and row["used"] + a + kerf <= sheet_l + 1e-9:
                        row["used"] += a + kerf
                        row["items"].append((it[0], it[1], a, b))
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
            used_h = sum(r["h"] + kerf for r in sh["rows"])
            for (a, b) in ((it[2], it[3]), (it[3], it[2])):
                if a <= sheet_l and used_h + b + kerf <= sheet_w + 1e-9:
                    sh["rows"].append({"h": b, "used": a + kerf,
                                       "items": [(it[0], it[1], a, b)]})
                    placed = True
                    break
            if placed:
                break
        if not placed:
            sheets.append({"rows": [{"h": it[3], "used": it[2] + kerf,
                                     "items": [(it[0], it[1], it[2], it[3])]}]})
    return sheets


# --------------------------------------------------------------------------- #
# writers
# --------------------------------------------------------------------------- #
def write_cut_list(path, P, G, parts, batten_rows):
    rows = []
    for p in parts:
        l, w = p.blank
        rows.append({
            "part_id": p.pid, "bezeichnung_de": p.name_de, "part_en": p.name_en,
            "qty": p.count,
            "blank_length_mm": f"{l:.1f}", "blank_width_mm": f"{w:.1f}",
            "thickness_mm": f"{p.thickness:.1f}",
            "material": p.material,
            "shape": "pentagon (square blank + 1 diagonal cut)" if len(p.local) == 5 else "rectangle",
            "net_area_m2_each": f"{p.net_area_m2:.4f}",
            "blank_area_m2_each": f"{p.blank_area_m2:.4f}",
            "cut_notes": p.cut_note,
            "drill_face_datums": " | ".join(f"{k}: {v}" for k, v in p.faces.items()),
        })
    for bid, name, qty, length, note in batten_rows:
        rows.append({
            "part_id": bid, "bezeichnung_de": name, "part_en": name, "qty": qty,
            "blank_length_mm": f"{length:.1f}",
            "blank_width_mm": f"{P['hardware']['batten_mm']:.1f}",
            "thickness_mm": f"{P['hardware']['batten_mm']:.1f}",
            "material": "softwood square batten (Vierkantleiste Kiefer/Fichte)",
            "shape": "square batten", "net_area_m2_each": "", "blank_area_m2_each": "",
            "cut_notes": "Cut on site with a mitre or hand saw; length is not critical to 1 mm.",
            "drill_face_datums": note,
        })
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows


def write_drill_plan(path, P, parts):
    rows = []
    for p in parts:
        groups = [("-", p.holes)] if p.holes else []
        groups += list(p.drill_variants.items())
        for variant, holes in groups:
            for i, h in enumerate(sorted(holes, key=lambda z: (z.face, z.y, z.x)), 1):
                rows.append({
                    "part_id": p.pid, "part_de": p.name_de, "drill_variant": variant,
                    "hole_no": i, "face": h.face,
                    "x_mm": f"{h.x:.1f}", "y_mm": f"{h.y:.1f}",
                    "dia_mm": f"{h.dia:.1f}",
                    "depth_mm": "through" if h.depth is None else f"{h.depth:.1f}",
                    "kind": h.kind, "note": h.note,
                })
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows


def write_layout_lines(path, P, G):
    T = P["panel"]["thickness_mm"]
    x0, y0, x1, y1, K, s = G["x0"], G["y0"], G["x1"], G["y1"], G["K"], G["side_return"]
    L = G["leg"]
    rows = [
        ("P01/P02", "P03 Rueckwand Wand 2, inner face",
         f"line parallel to the wall-2 edge at {T:.0f} mm"),
        ("P01/P02", "P04 Rueckwand Wand 1, inner face",
         f"line parallel to the wall-1 edge at {T:.0f} mm"),
        # P05 stands across the wall-1 end, so its inner face is a line PARALLEL TO
        # THE WALL-2 EDGE, offset x from the corner. Mirrored for P06.
        ("P01/P02", "P05 Seitenwange Wand 1, inner face",
         f"line parallel to the wall-2 edge, at x={L - T:.0f} mm along the wall-1 edge"),
        ("P01/P02", "P06 Seitenwange Wand 2, inner face",
         f"line parallel to the wall-1 edge, at y={L - T:.0f} mm along the wall-2 edge"),
        ("P01/P02", "P07/P09 centre partition",
         f"the bisector of the 90 deg corner (the 45 deg diagonal through the origin); "
         f"partition faces {T/2:.0f} mm either side of it, running "
         f"{G['partition_depth']:.0f} mm back from the front edge"),
        ("P08 mid shelf", "P09 upper centre partition",
         f"bisector of the 90 deg corner; faces {T/2:.0f} mm either side"),
        ("P03", "shelf bearer L01, top edge",
         f"y = {G['z_shelf_b'] - G['z_bot_t']:.0f} mm from the bottom edge"),
        ("P04", "shelf bearer L02, top edge",
         f"y = {G['z_shelf_b'] - G['z_bot_t']:.0f} mm from the bottom edge"),
        ("P05/P06", "shelf bearer L03, top edge",
         f"y = {G['z_shelf_b'] - G['z_bot_t']:.0f} mm from the bottom edge"),
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["on_part", "marks_the_position_of", "layout_line"])
        w.writerows(rows)
    return rows


def write_dxf(outdir, parts, G):
    import ezdxf
    os.makedirs(outdir, exist_ok=True)
    written = []
    for p in parts:
        doc = ezdxf.new("R2010", setup=True)
        doc.header["$INSUNITS"] = 4          # millimetres
        msp = doc.modelspace()
        for lay, col in (("OUTLINE", 7), ("HOLES", 1), ("HOLES_VARIANT_A", 3),
                         ("HOLES_VARIANT_B", 5), ("TEXT", 8)):
            if lay not in doc.layers:
                doc.layers.add(lay, color=col)
        msp.add_lwpolyline(p.local, close=True, dxfattribs={"layer": "OUTLINE"})
        for h in p.holes:
            msp.add_circle((h.x, h.y), h.dia / 2, dxfattribs={"layer": "HOLES"})
        for i, (variant, holes) in enumerate(p.drill_variants.items()):
            lay = "HOLES_VARIANT_A" if i == 0 else "HOLES_VARIANT_B"
            for h in holes:
                msp.add_circle((h.x, h.y), h.dia / 2, dxfattribs={"layer": lay})
        l, w = p.blank
        msp.add_text(f"{p.pid} {p.name_de}  {l:.0f} x {w:.0f} x {p.thickness:.0f} mm  x{p.count}",
                     height=14, dxfattribs={"layer": "TEXT"}).set_placement((0, -30))
        fn = os.path.join(outdir, f"{p.pid}-{p.name_en.lower().replace(' ', '-').replace(',', '')}.dxf")
        doc.saveas(fn)
        written.append(fn)
    return written


def write_step_stl(outdir, P, G, parts):
    try:
        import cadquery as cq
    except Exception as exc:                                   # pragma: no cover
        return {"status": "skipped", "reason": f"cadquery unavailable: {exc}"}
    asm = None
    solids = []

    def prism(poly, z0, z1):
        wp = cq.Workplane("XY").polyline([(x, y) for x, y in poly]).close()
        return wp.extrude(z1 - z0).translate((0, 0, z0))

    for p in parts:
        if p.pid == "P10":
            for hand, row, pl, zb, zt in G["door_defs"]:
                solids.append(prism(pl, zb, zt))
        else:
            solids.append(prism(p.plan, p.z0, p.z1))
    # feet as simple cylinders
    for (fx, fy) in G["foot_positions"]:
        solids.append(cq.Workplane("XY").center(fx, fy).circle(22.0)
                      .extrude(P["heights"]["foot_mm"]))
    comp = solids[0]
    for s in solids[1:]:
        comp = comp.union(s)
    os.makedirs(outdir, exist_ok=True)
    step = os.path.join(outdir, "MM-FUR-001-assembly.step")
    stl = os.path.join(outdir, "MM-FUR-001-assembly.stl")
    cq.exporters.export(comp, step)
    cq.exporters.export(comp, stl, tolerance=0.2, angularTolerance=0.3)
    bb = comp.val().BoundingBox()
    return {"status": "ok", "step": step, "stl": stl,
            "bbox_mm": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
            "bbox_min": [round(bb.xmin, 1), round(bb.ymin, 1), round(bb.zmin, 1)],
            "bbox_max": [round(bb.xmax, 1), round(bb.ymax, 1), round(bb.zmax, 1)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", default=os.path.join(HERE, "params.yaml"))
    ap.add_argument("--outdir", default=os.path.join(ROOT, "exports"))
    ap.add_argument("--no-3d", action="store_true")
    a = ap.parse_args()

    P = yaml.safe_load(open(a.params, encoding="utf-8"))
    G = build(P)
    parts = make_parts(P, G)
    batten_rows, batten_total = battens(P, G)
    os.makedirs(a.outdir, exist_ok=True)

    cut_rows = write_cut_list(os.path.join(a.outdir, "cut-list.csv"), P, G, parts, batten_rows)
    drill_rows = write_drill_plan(os.path.join(a.outdir, "drill-plan.csv"), P, parts)
    write_layout_lines(os.path.join(a.outdir, "layout-lines.csv"), P, G)
    dxf = write_dxf(os.path.join(a.outdir, "dxf"), parts, G)

    panel_parts = [p for p in parts if p.material == P["panel"]["material_primary"]]
    blanks = [(p.pid, p.name_de, *p.blank, p.count) for p in panel_parts]
    sheets = nest(blanks, P["stock"]["sheet_length_mm"], P["stock"]["sheet_width_mm"],
                  P["stock"]["saw_kerf_mm"])
    blank_area = sum(p.blank_area_m2 * p.count for p in panel_parts)
    net_area = sum(p.net_area_m2 * p.count for p in panel_parts)
    sheet_area = P["stock"]["sheet_length_mm"] * P["stock"]["sheet_width_mm"] / 1e6

    G["panel_blank_area_m2"] = round(blank_area, 3)
    G["panel_net_area_m2"] = round(net_area, 3)
    G["sheets_needed"] = len(sheets)
    G["sheet_utilisation_pct"] = round(100 * blank_area / (len(sheets) * sheet_area), 1)
    G["mass_panels_primary_kg"] = round(net_area * P["panel"]["density_primary_kg_per_m2"], 1)
    G["mass_panels_alternative_kg"] = round(net_area * P["panel"]["density_alternative_kg_per_m2"], 1)
    G["mass_total_primary_kg"] = round(G["mass_panels_primary_kg"] + G["glass_mass_kg"] + 3.0, 1)
    G["painted_area_m2"] = round(2 * net_area + 0.35, 2)
    G["batten_total_mm"] = batten_total

    three = {"status": "skipped"} if a.no_3d else write_step_stl(a.outdir, P, G, parts)

    summary = {
        "product": "MM-FUR-001 Corner cabinet with glass display top",
        "revision": "0.1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0)
                        .isoformat().replace("+00:00", "Z"),
        "generator": "source/corner_cabinet.py",
        "params_sha256": hashlib.sha256(open(a.params, "rb").read()).hexdigest(),
        "RELEASE_STATE": "CONCEPT_ONLY — nominal 1000 x 1000 mm niche, UNMEASURED. "
                         "Do not cut panels or order glass from this revision.",
        "geometry": {k: v for k, v in G.items()
                     if k not in ("footprint_outer", "shelf_poly", "glass_poly",
                                  "partition_plan", "door_defs", "f", "n_in", "n_out")},
        "polygons_room_frame": {
            "footprint_outer": [[round(x, 2), round(y, 2)] for x, y in G["footprint_outer"]],
            "mid_shelf": [[round(x, 2), round(y, 2)] for x, y in G["shelf_poly"]],
            "glass": [[round(x, 2), round(y, 2)] for x, y in G["glass_poly"]],
            "centre_partition": [[round(x, 2), round(y, 2)] for x, y in G["partition_plan"]],
        },
        "material": {
            "blank_area_m2": G["panel_blank_area_m2"],
            "net_area_m2": G["panel_net_area_m2"],
            "offcut_from_diagonal_cuts_m2": round(blank_area - net_area, 3),
            "sheets_2500x1250_needed": len(sheets),
            "sheet_utilisation_pct": G["sheet_utilisation_pct"],
            "per_piece_cut_service_area_m2": G["panel_blank_area_m2"],
            "batten_total_mm": batten_total,
            "painted_area_m2": G["painted_area_m2"],
        },
        "mass_kg": {
            "panels_birch_plywood": G["mass_panels_primary_kg"],
            "panels_spruce_glued_panel": G["mass_panels_alternative_kg"],
            "glass": round(G["glass_mass_kg"], 1),
            "assembled_total_birch_plywood": G["mass_total_primary_kg"],
        },
        "counts": {"cut_list_rows": len(cut_rows), "drilled_holes": len(drill_rows),
                   "dxf_files": len(dxf)},
        "three_d": three,
        "nesting": [
            {"sheet": i + 1,
             "rows": [{"row_height_mm": round(r["h"], 1),
                       "length_used_mm": round(r["used"], 1),
                       "parts": [f"{a_}({c:.0f}x{d:.0f})" for a_, b_, c, d in r["items"]]}
                      for r in sh["rows"]]}
            for i, sh in enumerate(sheets)],
    }
    with open(os.path.join(a.outdir, "geometry-summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False); fh.write("\n")

    print(json.dumps({k: summary[k] for k in
                      ("material", "mass_kg", "counts", "three_d")}, indent=2))
    g = summary["geometry"]
    for k in ("leg", "front_len", "door_w", "door_h", "outer_reveal", "compartment_h",
              "depth_corner_to_front", "closed_max_x", "closed_max_y",
              "max_open_angle_inside_niche_deg", "door_overlay_on_partition",
              "top_edge_visible", "shelf_front_len", "glass_front_len"):
        print(f"  {k:38s} {g[k]}")
    print("  door_tip_envelope", g["door_tip_envelope"])


if __name__ == "__main__":
    main()
