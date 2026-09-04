#!/usr/bin/env python3
"""MM-FUR-001 — technical drawings, generated from source/params.yaml.

Produces exports/drawings/*.svg and *.png:
    01-grundriss      plan view with panel footprints, feet and door swing
    02-frontansicht   true-size elevation of the 45 deg diagonal front
    03-schnitt        vertical section on the corner bisector
    04-plattenplan    every blank to scale with its drilled holes
    05-bohrbilder     enlarged drill patterns for the doors and partitions

Nothing here is authoritative: exports/cut-list.csv and exports/drill-plan.csv are.
"""
from __future__ import annotations

import csv
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Circle, Rectangle, Wedge
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from corner_cabinet import build, make_parts, battens          # noqa: E402

SQ2 = math.sqrt(2.0)
OUT = os.path.join(ROOT, "exports", "drawings")
INK = "#1b1b1b"
DIM = "#b3261e"
AUX = "#8a8a8a"
FILL = "#f2f2ef"


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight",
                    dpi=200, facecolor="white")
    plt.close(fig)
    return name


def dim(ax, p0, p1, text, off=0.0, side=1, fs=7.5, color=DIM):
    """Simple linear dimension with arrows."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L * off * side, dx / L * off * side
    ax.annotate("", xy=(x1 + nx, y1 + ny), xytext=(x0 + nx, y0 + ny),
                arrowprops=dict(arrowstyle="<|-|>", color=color, lw=0.7,
                                shrinkA=0, shrinkB=0, mutation_scale=7))
    ax.plot([x0, x0 + nx], [y0, y0 + ny], color=color, lw=0.4)
    ax.plot([x1, x1 + nx], [y1, y1 + ny], color=color, lw=0.4)
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90:
        ang += 180
    ax.text((x0 + x1) / 2 + nx, (y0 + y1) / 2 + ny, text, ha="center", va="bottom",
            fontsize=fs, color=color, rotation=ang, rotation_mode="anchor")


def title(ax, main, sub):
    ax.set_title(f"{main}\n{sub}", fontsize=10, loc="left", color=INK, pad=12)


# --------------------------------------------------------------------------- #
def plan(P, G, parts):
    T = P["panel"]["thickness_mm"]
    fig, ax = plt.subplots(figsize=(9.2, 9.2))
    x0, y0, x1, y1, K = G["x0"], G["y0"], G["x1"], G["y1"], G["K"]
    n1, n2 = P["niche"]["wall_1_mm"], P["niche"]["wall_2_mm"]

    # niche walls
    ax.add_patch(Rectangle((-90, -90), n1 + 90, 90, fc="#dcdcd6", ec=AUX, lw=0.6))
    ax.add_patch(Rectangle((-90, 0), 90, n2, fc="#dcdcd6", ec=AUX, lw=0.6))
    ax.plot([n1, n1], [-90, 60], color=AUX, lw=0.8, ls=(0, (5, 3)))
    ax.plot([-90, 60], [n2, n2], color=AUX, lw=0.8, ls=(0, (5, 3)))
    ax.text(n1, -60, f"  1 m mark, wall 1\n  ({n1:.0f} mm) MEASURE", fontsize=7, color=AUX)
    ax.text(-85, n2 + 14, f"1 m mark, wall 2 ({n2:.0f} mm) MEASURE", fontsize=7, color=AUX)

    # carcass outline
    ax.add_patch(MplPoly(G["footprint_outer"], closed=True, fc=FILL, ec=INK, lw=1.4, zorder=2))
    # vertical panels
    for p in parts:
        if p.pid in ("P03", "P04", "P05", "P06", "P07"):
            ax.add_patch(MplPoly(p.plan, closed=True, fc="#c9c9c2", ec=INK, lw=0.8, zorder=3))
    # mid shelf and glass
    ax.add_patch(MplPoly(G["shelf_poly"], closed=True, fc="none", ec="#2f6fb0",
                         lw=0.9, ls=(0, (6, 3)), zorder=4))
    ax.add_patch(MplPoly(G["glass_poly"], closed=True, fc="none", ec="#1f8a70",
                         lw=0.9, ls=(0, (2, 2)), zorder=4))
    # doors (closed) and swing
    piv_r = None
    for hand, row, pl, zb, zt in G["door_defs"]:
        if row != "lower":
            continue
        ax.add_patch(MplPoly(pl, closed=True, fc="#ffffff", ec=INK, lw=1.0, zorder=5))
    piv = G["door_pivot"]
    # Both doors hinge on the centre partition. The wall-1 door sweeps -45..+45 deg,
    # the wall-2 door +45..+135 deg. Their union is the semicircle drawn here.
    ax.add_patch(Wedge(piv, G["door_w"], -45, 135, width=0.8, fc="none", ec=DIM,
                       lw=0.7, ls=(0, (4, 3)), zorder=1))
    tip90 = G["door_tip_envelope"][90]
    # one door drawn fully open at 90 deg (the wall-2 door), as a solid leaf
    T2 = P["panel"]["thickness_mm"]
    nx, ny = G["n_out"]
    px, py = piv
    ax.add_patch(MplPoly([(px, py), (tip90[0], tip90[1]),
                          (tip90[0] - ny * T2, tip90[1] + nx * T2),
                          (px - ny * T2, py + nx * T2)],
                         closed=True, fc="#ffffff", ec=DIM, lw=1.1, zorder=6))
    ax.text(tip90[0] + 10, tip90[1] + 14,
            f"one door drawn open 90 deg\ntip ({tip90[0]:.0f}, {tip90[1]:.0f}) - inside the "
            f"{P['niche']['wall_1_mm']:.0f} mm niche\ndashed arc = swing envelope of both doors",
            fontsize=7, color=DIM)

    # feet
    for i, (fx, fy) in enumerate(G["foot_positions"], 1):
        ax.add_patch(Circle((fx, fy), 22, fc="#3a3a3a", ec="none", zorder=7))
        ax.text(fx + 28, fy - 6, f"F{i}", fontsize=7, color=INK, zorder=7)

    # dimensions
    dim(ax, (x0, y0), (x1, y0), f"{G['leg']:.0f}", off=-150, fs=8)
    dim(ax, (x0, y0), (x0, y1), f"{G['leg']:.0f}", off=150, fs=8)
    dim(ax, G["C"], G["D"], f"front {G['front_len']:.1f}", off=-128, fs=8)
    dim(ax, (x1, y0), G["C"], f"{G['side_return']:.0f}", off=-60, side=-1, fs=7.5)
    ax.annotate(f"back gap {P['niche']['back_gap_mm']:.0f} mm per wall\n"
                f"(set to skirting thickness + 3 mm)",
                xy=(x0, y1 * 0.72), xytext=(-360, y1 * 0.80), fontsize=7, color=DIM,
                arrowprops=dict(arrowstyle="->", color=DIM, lw=0.6))
    ax.annotate(f"depth corner to front {G['depth_corner_to_front']:.0f} mm",
                xy=((x0 + K / 2) / 2, (y0 + K / 2) / 2), xytext=(120, 320),
                fontsize=7.5, color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.6))
    ax.plot([x0, K / 2], [y0, K / 2], color=AUX, lw=0.6, ls=(0, (1, 3)))

    handles = [
        ("carcass 18 mm panels", INK), ("mid shelf P08 (dashed blue)", "#2f6fb0"),
        ("glass P11 (dotted green)", "#1f8a70"), ("door swing / dimensions", DIM),
    ]
    for i, (lab, c) in enumerate(handles):
        ax.text(-360, -60 - i * 46, lab, fontsize=7.5, color=c)

    title(ax, "MM-FUR-001  01 Grundriss / plan view   1:10 nominal",
          f"Room frame: origin = niche corner, +X = wall 1, +Y = wall 2. "
          f"All values mm. Carcass legs {G['leg']:.0f} mm, front {G['front_len']:.1f} mm. "
          f"CONCEPT_ONLY - niche UNMEASURED.")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-380, n1 + 140); ax.set_ylim(-260, n2 + 150)
    return save(fig, "01-grundriss")


# --------------------------------------------------------------------------- #
def front(P, G):
    T = P["panel"]["thickness_mm"]
    dr = P["doors"]
    fl = G["front_len"]
    fig, ax = plt.subplots(figsize=(10.4, 7.2))

    def band(u0, u1, z0, z1, **kw):
        ax.add_patch(Rectangle((u0, z0), u1 - u0, z1 - z0, **kw))

    # carcass front edges behind the doors
    band(0, fl, G["z_bot_u"], G["z_top_t"], fc="#e6e6e1", ec=AUX, lw=0.6)
    # top plate rim + glass
    band(0, fl, G["z_top_u"], G["z_top_t"], fc=FILL, ec=INK, lw=1.2)
    band((fl - G["glass_front_len"]) / 2, (fl + G["glass_front_len"]) / 2,
         G["z_top_t"], G["z_top_t"] + P["glass"]["thickness_mm"],
         fc="#dff1ec", ec="#1f8a70", lw=1.1)
    ax.text(fl / 2, G["z_top_t"] + 26,
            f"P11 glass {P['glass']['thickness_mm']:.0f} mm ESG, "
            f"{G['glass_area_m2']:.3f} m2, {G['glass_mass_kg']:.1f} kg",
            ha="center", fontsize=7.5, color="#1f8a70")

    # doors
    ors = G["outer_reveal"]
    dw, dh = G["door_w"], G["door_h"]
    cols = [(ors, ors + dw, "wall-2 side\nvariant B"),
            (ors + dw + dr["gap_horizontal_mm"], ors + 2 * dw + dr["gap_horizontal_mm"],
             "wall-1 side\nvariant A")]
    rows = [(G["z_low_b"], G["z_low_t"], "unten"), (G["z_up_b"], G["z_up_t"], "oben")]
    for ci, (u0, u1, cl) in enumerate(cols):
        for ri, (z0, z1, rl) in enumerate(rows):
            band(u0, u1, z0, z1, fc="#ffffff", ec=INK, lw=1.1, zorder=3)
            ax.text((u0 + u1) / 2, (z0 + z1) / 2 + 66,
                    f"P10 {'links' if ci == 0 else 'rechts'} {rl}",
                    ha="center", fontsize=8.5, color=INK, zorder=4)
            ax.text((u0 + u1) / 2, (z0 + z1) / 2 + 22, f"{dw:.0f} x {dh:.0f} x {T:.0f}",
                    ha="center", fontsize=8, color=INK, zorder=4)
            ax.text((u0 + u1) / 2, (z0 + z1) / 2 - 30, cl, ha="center", fontsize=7,
                    color=AUX, zorder=4)
            # handle
            hu = u1 - dr["handle_from_outer_edge_mm"] if ci == 1 else u0 + dr["handle_from_outer_edge_mm"]
            zc = (z0 + z1) / 2
            ax.plot([hu, hu], [zc - dr["handle_hole_pitch_mm"] / 2, zc + dr["handle_hole_pitch_mm"] / 2],
                    color="#6b6b6b", lw=3.4, solid_capstyle="round", zorder=5)
            for off in (-dr["handle_hole_pitch_mm"] / 2, dr["handle_hole_pitch_mm"] / 2):
                ax.add_patch(Circle((hu, zc + off), 5, fc="#3a3a3a", ec="none", zorder=6))
            # hinge cups (hidden, on the centre side)
            cfe = dr["cup_from_end_right_mm"] if ci == 1 else dr["cup_from_end_left_mm"]
            cu = u0 + dr["hinge_edge_inset_mm"] if ci == 1 else u1 - dr["hinge_edge_inset_mm"]
            for cz in (z0 + cfe, z1 - cfe):
                ax.add_patch(Circle((cu, cz), dr["cup_diameter_mm"] / 2, fc="none",
                                    ec=DIM, lw=0.7, ls=(0, (2, 2)), zorder=6))

    # feet, projected
    Dp, K = G["D"], G["K"]
    for i, (fx, fy) in enumerate(G["foot_positions"], 1):
        u = ((fx - Dp[0]) - (fy - Dp[1])) / SQ2
        if -20 <= u <= fl + 20:
            ax.add_patch(Rectangle((u - 22, 0), 44, G["z_bot_u"], fc="none", ec="#3a3a3a",
                                   lw=0.8, ls=(0, (3, 2))))
            ax.text(u, -34 - 26 * (i % 2), f"F{i}", ha="center", fontsize=6.5,
                    color="#3a3a3a")
    ax.plot([-40, fl + 40], [0, 0], color=INK, lw=1.6)

    # dimensions
    dim(ax, (0, G["z_top_t"]), (fl, G["z_top_t"]), f"{fl:.1f}  (Front / diagonal front)",
        off=118, fs=8)
    dim(ax, (ors, G["z_low_b"]), (ors + dw, G["z_low_b"]), f"{dw:.0f}", off=-70, fs=8)
    dim(ax, (ors + dw + dr["gap_horizontal_mm"], G["z_low_b"]),
        (ors + 2 * dw + dr["gap_horizontal_mm"], G["z_low_b"]), f"{dw:.0f}", off=-70, fs=8)
    for z0, z1, lab in ((0, G["z_bot_u"], f"{G['z_bot_u']:.0f} Fuesse"),
                        (G["z_low_b"], G["z_low_t"], f"{dh:.0f} door"),
                        (G["z_up_b"], G["z_up_t"], f"{dh:.0f} door"),
                        (0, G["z_top_t"], f"{G['z_top_t']:.0f} total to top of wood")):
        off = -70 if lab.endswith("wood") else 60
        dim(ax, (fl, z0), (fl, z1), lab, off=off, fs=7.5)
    ax.annotate(f"horizontal joint, gap {dr['gap_vertical_mm']:.0f} mm",
                xy=(fl * 0.18, G["z_low_t"] + dr["gap_vertical_mm"] / 2),
                xytext=(-140, G["z_low_t"] - 40), fontsize=7, color=DIM,
                arrowprops=dict(arrowstyle="->", color=DIM, lw=0.6))
    ax.annotate(f"vertical joint over the centre partition,\n"
                f"gap {dr['gap_horizontal_mm']:.0f} mm, "
                f"{G['door_overlay_on_partition']:.1f} mm overlay per door",
                xy=(fl / 2, G["z_up_t"] * 0.86),
                xytext=(fl + 60, G["z_top_t"] + 120), fontsize=7, color=DIM,
                arrowprops=dict(arrowstyle="->", color=DIM, lw=0.6))

    title(ax, "MM-FUR-001  02 Frontansicht / true-size elevation of the diagonal front",
          f"Four identical {dw:.0f} x {dh:.0f} x {T:.0f} mm doors, half-overlay hinges on the "
          f"centre partition (dashed cups). Top plate edge stands {G['top_edge_visible']:.0f} mm "
          f"proud above the doors. All values mm.")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-150, fl + 190); ax.set_ylim(-125, G["z_top_t"] + 210)
    return save(fig, "02-frontansicht")


# --------------------------------------------------------------------------- #
def section(P, G):
    T = P["panel"]["thickness_mm"]
    depth = G["depth_corner_to_front"]
    fig, ax = plt.subplots(figsize=(9.6, 6.4))

    def band(v0, v1, z0, z1, lab=None, outside=False, **kw):
        ax.add_patch(Rectangle((v0, z0), v1 - v0, z1 - z0, **kw))
        if not lab:
            return
        if outside:                      # thin bands: label clear of the geometry
            ax.annotate(lab, xy=(v0 + (v1 - v0) * 0.3, (z0 + z1) / 2),
                        xytext=(-330, (z0 + z1) / 2), fontsize=7.5, color=INK,
                        va="center", arrowprops=dict(arrowstyle="->", color=AUX, lw=0.5))
        else:
            ax.text((v0 + v1) / 2, (z0 + z1) / 2, lab, ha="center", va="center",
                    fontsize=7.5, color=INK)

    v_back = 0.0                    # at the rear (corner) end
    v_front = depth                 # at the front plane
    v_in = T * SQ2                  # inner face of the two back panels, on the bisector

    ax.add_patch(Rectangle((-70, 0), 70, 1120, fc="#dcdcd6", ec=AUX, lw=0.6))
    ax.text(-66, 1150, "wall corner", fontsize=7, color=AUX)

    band(v_back, v_front, G["z_bot_u"], G["z_bot_t"], "P01 Bodenplatte 18", outside=True, fc=FILL, ec=INK, lw=1.1)
    band(v_back, v_front, G["z_top_u"], G["z_top_t"], "P02 Deckplatte 18", outside=True, fc=FILL, ec=INK, lw=1.1)
    band(v_back, v_front - 0.5, G["z_top_t"], G["z_top_t"] + P["glass"]["thickness_mm"],
         None, fc="#dff1ec", ec="#1f8a70", lw=1.1)
    ax.text(v_front * 0.5, G["z_top_t"] + 30, "P11 Glas 6 mm ESG + Ansichtskarten darunter",
            ha="center", fontsize=7.5, color="#1f8a70")
    band(v_in, v_front, G["z_shelf_b"], G["z_shelf_t"], "P08 Mittelboden 18",
         outside=True, fc=FILL, ec="#2f6fb0", lw=1.1)
    band(v_back, v_in, G["z_bot_t"], G["z_top_u"], None, fc="#c9c9c2", ec=INK, lw=0.8)
    ax.annotate("P03/P04 Rueckwaende 18",
                xy=(v_in / 2, G["z_bot_t"] + 300),
                xytext=(-330, G["z_bot_t"] + 300), fontsize=7.5, color=INK, va="center",
                arrowprops=dict(arrowstyle="->", color=AUX, lw=0.5))
    pd = G["partition_depth"]
    band(v_front - pd, v_front, G["z_bot_t"], G["z_shelf_b"],
         "P07 Mittelsteg\n(laengs geschnitten)", fc="#e8e8e0", ec=INK, lw=0.7, hatch="////")
    band(v_front - pd, v_front, G["z_shelf_t"], G["z_top_u"],
         "P09 Mittelsteg\n(laengs geschnitten)", fc="#e8e8e0", ec=INK, lw=0.7, hatch="////")
    # doors
    for z0, z1 in ((G["z_low_b"], G["z_low_t"]), (G["z_up_b"], G["z_up_t"])):
        band(v_front, v_front + T, z0, z1, None, fc="#ffffff", ec=INK, lw=1.1)
    ax.annotate("P10 Tuer 18 (liegt vor der Front)",
                xy=(v_front + T / 2, G["z_up_b"] + 120),
                xytext=(v_front - 300, G["z_top_t"] + 90), fontsize=7.5, color=INK,
                arrowprops=dict(arrowstyle="->", color=AUX, lw=0.5))
    # feet
    fm = G["foot_positions"][-1]
    ax.add_patch(Rectangle((v_front - 55 - 22, 0), 44, G["z_bot_u"], fc="#3a3a3a", ec="none"))
    ax.add_patch(Rectangle((30, 0), 44, G["z_bot_u"], fc="#3a3a3a", ec="none"))
    ax.plot([-70, v_front + 120], [0, 0], color=INK, lw=1.6)

    xs = v_front + 130
    for z0, z1, lab in ((0, G["z_bot_u"], f"{G['z_bot_u']:.0f} Fuesse"),
                        (G["z_bot_t"], G["z_shelf_b"], f"{G['compartment_h']:.0f} clear"),
                        (G["z_shelf_t"], G["z_top_u"], f"{G['compartment_h']:.0f} clear"),
                        (0, G["z_top_t"], f"{G['z_top_t']:.0f}")):
        dim(ax, (xs, z0), (xs, z1), lab, off=(60 if lab.endswith("clear") else -60), fs=7.5)
    dim(ax, (v_back, -70), (v_front, -70), f"{depth:.0f} depth on the corner bisector",
        off=0, fs=8)
    dim(ax, (v_front - pd, G["z_shelf_t"] + 60), (v_front, G["z_shelf_t"] + 60),
        f"partition depth {pd:.0f}", off=0, fs=7)

    title(ax, "MM-FUR-001  03 Schnitt / vertical section on the corner bisector",
          f"Compartments {G['compartment_h']:.0f} mm clear each. Top face of the timber plate "
          f"at exactly {G['z_top_t']:.0f} mm; the glass adds "
          f"{P['glass']['thickness_mm']:.0f} mm on top. All values mm.")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-420, v_front + 260); ax.set_ylim(-160, G["z_top_t"] + 150)
    return save(fig, "03-schnitt")


# --------------------------------------------------------------------------- #
def panel_sheet(P, G, parts, batten_rows):
    fig, ax = plt.subplots(figsize=(11.6, 8.4))
    cur_x, cur_y, row_h, gap = 0.0, 0.0, 0.0, 90.0
    maxw = 2300.0
    for p in parts:
        l, w = p.blank
        if cur_x + l > maxw:
            cur_x, cur_y = 0.0, cur_y - row_h - gap - 60
            row_h = 0.0
        pts = [(x + cur_x, y + cur_y) for x, y in p.local]
        ax.add_patch(MplPoly(pts, closed=True, fc=FILL if p.pid != "P11" else "#dff1ec",
                             ec=INK if p.pid != "P11" else "#1f8a70", lw=1.0))
        allh = list(p.holes) + [h for hs in p.drill_variants.values() for h in hs]
        for h in allh:
            c = {"hinge_cup": DIM, "hinge_plate": "#2f6fb0", "handle": "#7a3fa0",
                 "screw_through": "#4a4a4a", "foot_transfer": "#1f8a70"}.get(h.kind, INK)
            ax.add_patch(Circle((cur_x + h.x, cur_y + h.y), max(h.dia / 2, 3.2),
                                fc="none", ec=c, lw=0.7))
        ax.text(cur_x + 6, cur_y + w + 22,
                f"{p.pid}  {p.name_de}  x{p.count}", fontsize=8, color=INK)
        ax.text(cur_x + 6, cur_y - 30,
                f"{l:.0f} x {w:.0f} x {p.thickness:.0f} mm", fontsize=7.5, color=DIM)
        cur_x += l + gap
        row_h = max(row_h, w)
    leg = [("hinge cup 35 mm", DIM), ("hinge mounting plate 5 mm", "#2f6fb0"),
           ("handle 5 mm through", "#7a3fa0"), ("carcass screw 4.5 mm through", "#4a4a4a"),
           ("foot transfer mark 2 mm", "#1f8a70")]
    for i, (lab, c) in enumerate(leg):
        ax.text(0, cur_y - 190 - i * 62, "o  " + lab, fontsize=8, color=c)
    title(ax, "MM-FUR-001  04 Plattenplan / all blanks to scale with drilled holes",
          "Both drill variants A and B are overlaid on the single door blank P10; "
          "use exports/drill-plan.csv for the numbers. Hole symbols are enlarged for "
          "legibility. All values mm.")
    ax.set_aspect("equal"); ax.axis("off"); ax.autoscale_view()
    ax.relim(); ax.autoscale()
    return save(fig, "04-plattenplan")


# --------------------------------------------------------------------------- #
def drill_details(P, G, parts):
    dr = P["doors"]
    door = next(p for p in parts if p.pid == "P10")
    part7 = next(p for p in parts if p.pid == "P07")
    fig, axs = plt.subplots(1, 3, figsize=(14.6, 5.8))

    for ax, (variant, holes) in zip(axs[:2], door.drill_variants.items()):
        l, w = door.blank
        ax.add_patch(Rectangle((0, 0), l, w, fc=FILL, ec=INK, lw=1.2))
        ax.plot([0, 0], [0, w], color=DIM, lw=2.6)
        ax.text(-14, w / 2, "HINGE EDGE", rotation=90, va="center", ha="right",
                fontsize=8, color=DIM)
        for h in holes:
            c = DIM if h.kind == "hinge_cup" else "#7a3fa0"
            ax.add_patch(Circle((h.x, h.y), h.dia / 2, fc="none", ec=c, lw=1.1))
            ax.plot([h.x], [h.y], marker="+", color=c, ms=6, mew=0.8)
            ax.text(h.x + h.dia / 2 + 8, h.y,
                    f"{h.x:.1f} / {h.y:.1f}   d{h.dia:.0f}"
                    + (f" x {h.depth:.1f}" if h.depth else " through"),
                    fontsize=7, color=c, va="center")
        dim(ax, (0, 0), (l, 0), f"{l:.0f}", off=-46, fs=8)
        dim(ax, (0, 0), (0, w), f"{w:.0f}", off=42, fs=8)
        ax.set_title(f"P10 door, drill variant {variant}\nINNER FACE UP, hinge edge LEFT, "
                     f"bottom edge DOWN", fontsize=8, color=INK, pad=14)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_xlim(-90, l + 210); ax.set_ylim(-80, w + 60)

    ax = axs[2]
    l, w = part7.blank
    ax.add_patch(Rectangle((0, 0), l, w, fc=FILL, ec=INK, lw=1.2))
    ax.plot([0, 0], [0, w], color=DIM, lw=2.6)
    ax.text(-14, w / 2, "FRONT EDGE", rotation=90, va="center", ha="right",
            fontsize=8, color=DIM)
    for i, h in enumerate(sorted(part7.holes, key=lambda z: z.y)):
        c = "#2f6fb0" if h.face == "SIDE-1" else "#1f8a70"
        ax.add_patch(Circle((h.x, h.y), 4.5, fc="none", ec=c, lw=1.0))
        lx = h.x + 30 + 118 * (i % 2)
        ax.plot([h.x + 6, lx - 4], [h.y, h.y], color=c, lw=0.4)
        ax.text(lx, h.y, f"{h.face} y={h.y:.0f}", fontsize=6.6, color=c, va="center")
    dim(ax, (0, 0), (l, 0), f"{l:.0f}", off=-46, fs=8)
    dim(ax, (0, 0), (0, w), f"{w:.0f}", off=42, fs=8)
    ax.set_title("P07 / P09 centre partition, both faces\n"
                 f"plate row {dr['plate_from_front_mm']:.0f} mm from front edge, "
                 f"pitch {dr['plate_pitch_mm']:.0f} mm, d5 x 10 deep\n"
                 "SIDE-1 / SIDE-2 staggered 16 mm: no pair coaxial",
                 fontsize=8, color=INK, pad=14)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-90, l + 330); ax.set_ylim(-80, w + 60)

    fig.suptitle("MM-FUR-001  05 Bohrbilder / enlarged drill patterns for the precision holes",
                 fontsize=10, x=0.02, ha="left")
    return save(fig, "05-bohrbilder")


def main():
    P = yaml.safe_load(open(os.path.join(HERE, "params.yaml"), encoding="utf-8"))
    G = build(P)
    parts = make_parts(P, G)
    batten_rows, _ = battens(P, G)
    made = [plan(P, G, parts), front(P, G), section(P, G),
            panel_sheet(P, G, parts, batten_rows), drill_details(P, G, parts)]
    print("drawings written to exports/drawings:")
    for m in made:
        print("  ", m + ".svg", "+", m + ".png")


if __name__ == "__main__":
    main()
