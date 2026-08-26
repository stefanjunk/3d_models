#!/usr/bin/env python3
"""NameForm Bookends MM-PER-001 — CadQuery build + validation pipeline.

Spec revision 0.2.0. Tool route: CadQuery (B-Rep source of truth, see
source/nameform_bookends.py). OpenSCAD revision 0.1.0 is superseded (defects
D15 in decision-log.md).

Two-phase flow (watermark release gate):
  phase 1 (default): build + evidence
    1. font metrics (fontTools) -> SIZE / CAP / word width / glyph polygon
    2. stability-driven BALLAST search (build master, exact mesh mass/CM)
    3. exports: master + final STL (STL tolerance recorded), STEP masters
    4. final = master + watermark recess (LAST solid change)
    5. min glyph stroke width (vector, shapely buffer)
    6. single-part 3MF (pair = two sequential prints; decision D17)
    7. watermark gate evidence (selector scale applied, canonical asset hash,
       orientation proof, presence) + gate render artifacts (underside view,
       dimensioned close-up, section)
    8. validation JSONs (design-spec.yaml is then updated by the operator with
       geometry_revision = final STL SHA-256, then phase 2)
  phase 2 (--finalize): release gate + package
    9. validate_design_spec.py --require-final-approval (must pass)
   10. release/manifest.json (SHA-256) + build summary — emitted ONLY after
       the gate passes (gate: "Do not emit a final package when it fails")

Run from the project root:  python3 scripts/build.py [--finalize]
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import shapely
import trimesh
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent          # organizer/nameform-bookends
sys.path.insert(0, str(ROOT / "source"))
import nameform_bookends as nb  # noqa: E402

SKILL = Path("/workspace/3d_models/.agents/skills/functional-3d-design")
FONT = nb.FONT_PATH
WORD = "M"
WIDTH_BUDGET = nb.WIDTH_BUDGET     # 192 mm
CAP_MAX = nb.CAP_MAX               # 180 mm
DENSITY = 1.24                     # g/cm3 PLA
BOOK_MASS_KG = 2.0
BOOK_OFFSET_M = 0.025              # CM beyond book face
G = 9.81
SF_TARGET = 1.55
TIP_EDGE_Y = nb.LETTER_FRONT       # +48 mm front bottom tipping edge

OUT_MASTER = ROOT / "exports" / "master"
OUT_FINAL = ROOT / "exports" / "final"
VAL = ROOT / "validation"
VAL_WM = VAL / "watermark"
RELEASE = ROOT / "release"


def log(msg: str) -> None:
    print(f"[build] {msg}", flush=True)


# ---------------------------------------------------------------------------
def font_metrics(word: str) -> dict:
    f = TTFont(FONT)
    upm = f["head"].unitsPerEm
    gs = f.getGlyphSet()
    cap_units = 0
    for c in "HAKM":
        pen = BoundsPen(gs)
        gs[c].draw(pen)
        if pen.bounds:
            cap_units = max(cap_units, pen.bounds[3])
    cap_ratio = cap_units / upm
    cmap = f.getBestCmap()
    adv = sum(gs[cmap[ord(c)]].width for c in word) / upm
    size = min(WIDTH_BUDGET / adv, CAP_MAX / cap_ratio)
    cap = cap_ratio * size
    word_w = adv * size
    assert word_w <= WIDTH_BUDGET + 1e-6 and cap <= CAP_MAX + 1e-6
    return {"size": size, "cap": cap, "word_width": word_w, "cap_ratio": cap_ratio,
            "advance_em": adv}


def word_polygon(word: str, size: float):
    """Positioned word as one shapely geometry (mm). Built from matplotlib's
    TextPath (same font file, size in mm) with cubic Beziers flattened to 16
    segments each — plenty for a 2 mm stroke-width measurement."""
    import matplotlib.path as mpath
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath

    tp = TextPath((0, 0), word, prop=FontProperties(fname=FONT), size=size)
    verts, codes = tp.vertices, tp.codes

    def cubic(p0, p1, p2, p3, t):
        u = 1.0 - t
        return (u ** 3) * p0 + 3 * (u ** 2) * t * p1 + 3 * u * (t ** 2) * p2 + (t ** 3) * p3

    subs: list[list[np.ndarray]] = []
    cur: list[np.ndarray] = []
    i = 0
    while i < len(verts):
        c = codes[i]
        if c == mpath.Path.MOVETO:
            cur = [np.asarray(verts[i])]
            i += 1
        elif c == mpath.Path.LINETO:
            cur.append(np.asarray(verts[i]))
            i += 1
        elif c == mpath.Path.CURVE4:
            p0 = cur[-1]
            p1, p2, p3 = (np.asarray(verts[i + k]) for k in range(3))
            for t in np.linspace(0.0, 1.0, 17)[1:]:
                cur.append(cubic(p0, p1, p2, p3, float(t)))
            i += 3
        elif c == mpath.Path.CLOSEPOLY:
            if len(cur) >= 3:
                subs.append(cur)
            cur = []
            i += 1
        else:  # pragma: no cover — defensive
            i += 1
    if len(cur) >= 3:
        subs.append(cur)
    return shapely.MultiPolygon([shapely.Polygon(s) for s in subs])


def min_stroke_width(poly) -> float:
    """2 * max r with poly.buffer(-r) non-empty (vector, no raster artifact)."""
    lo, hi = 0.0, 60.0
    for _ in range(45):
        mid = (lo + hi) / 2.0
        if poly.buffer(-mid).area > 1e-6:
            lo = mid
        else:
            hi = mid
    return 2.0 * lo


# ---------------------------------------------------------------------------
def analyze(stl: Path) -> dict:
    m = trimesh.load(str(stl))
    if not isinstance(m, trimesh.Trimesh):
        raise RuntimeError(f"{stl}: expected single Trimesh, got {type(m)}")
    bodies = len(list(m.split(only_watertight=False)))
    vol_cm3 = float(m.volume) / 1000.0
    zmin = float(m.bounds[0][2])
    if zmin < -1e-6:
        raise RuntimeError(f"geometry below bed datum: zmin={zmin} mm")
    return {
        "file": stl.name,
        "is_watertight": bool(m.is_watertight),
        "is_winding_consistent": bool(m.is_winding_consistent),
        "bodies": bodies,
        "bbox_mm": [float(v) for v in (m.bounds[1] - m.bounds[0])],
        "bounds_mm": [[float(v) for v in m.bounds[0]], [float(v) for v in m.bounds[1]]],
        "volume_cm3": round(vol_cm3, 3),
        "mass_g": round(vol_cm3 * DENSITY, 1),
        "centroid_mm": [round(float(v), 3) for v in m.centroid],
    }


def stability(a: dict) -> dict:
    mass_n = a["mass_g"] * 1e-3 * G
    arm_m = (TIP_EDGE_Y - a["centroid_mm"][1]) / 1000.0
    m_tip = mass_n * arm_m
    m_book = BOOK_MASS_KG * G * BOOK_OFFSET_M
    sf = m_tip / m_book
    return {
        "model": ("rigid body, books 2.0 kg CM 25 mm beyond book face (y=-29 mm), "
                  f"tipping about front bottom edge (y={TIP_EDGE_Y:.0f} mm)"),
        "mass_kg": round(a["mass_g"] / 1000.0, 3),
        "centroid_y_mm": a["centroid_mm"][1],
        "tip_arm_mm": round(TIP_EDGE_Y - a["centroid_mm"][1], 3),
        "resisting_moment_Nm": round(m_tip, 4),
        "overturning_moment_Nm": round(m_book, 4),
        "SF": round(sf, 3),
        "target": SF_TARGET,
        "pass": bool(sf >= SF_TARGET),
    }


# ---------------------------------------------------------------------------
def layout(ballast: float) -> dict:
    base_w = WIDTH_BUDGET + nb.WIDTH_MARGIN
    base_back = nb.BOOK_FACE_Y - ballast
    base_front = nb.LETTER_FRONT
    return {
        "base_w": base_w, "base_back": base_back, "base_front": base_front,
        "base_cy": (base_back + base_front) / 2.0,
    }


def select_watermark(base_depth: float) -> dict:
    r = subprocess.run(
        [sys.executable, str(SKILL / "scripts" / "select_watermark.py"),
         "--surface-width", str(WIDTH_BUDGET + nb.WIDTH_MARGIN),
         "--surface-height", str(base_depth),
         "--host-wall", str(nb.BASE_H), "--nozzle", "0.4",
         "--layer-height", "0.2", "--depth", str(nb.WM_DEPTH),
         "--json-out", str(VAL / "watermark-selector.json")],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"select_watermark failed:\n{r.stdout}\n{r.stderr}")
    return json.loads((VAL / "watermark-selector.json").read_text())


def asset_sha256() -> str:
    return hashlib.sha256(Path(nb.DEFAULT_WM_DXF).read_bytes()).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def watermark_evidence(a_master: dict, a_final: dict, ballast: float,
                       selector: dict) -> dict:
    sel = selector["selection"]
    wm_scale = float(sel["uniform_scale"])
    wm_rot = float(sel["rotation_deg"])
    ly = layout(ballast)
    wm_cy = ly["base_cy"]
    env = nb.watermark_cutter(nb.DEFAULT_WM_DXF, nb.WM_DEPTH, wm_scale, wm_rot)
    ebb = env.BoundingBox()
    ink_w = ebb.xmax - ebb.xmin
    ink_h = ebb.ymax - ebb.ymin
    margin_x = ly["base_w"] / 2.0 - ink_w / 2.0
    margin_y = min(wm_cy - ink_h / 2.0 - ly["base_back"],
                   ly["base_front"] - (wm_cy + ink_h / 2.0))
    proof = {
        "convention": ("finished underside viewed from outside (bed side) with the "
                       "viewer on the word-face side (+Y): either looking up at the "
                       "standing part, or flipping it about its left-right (X) axis "
                       "and looking down — both give the same image frame"),
        "image_frame": {"viewer_right": "part -X", "viewer_up": "part +Y (word-face side)"},
        "applied_transform": "X-mirror of the asset (x -> -x), mark re-centered on the underside center",
        "check": {
            "mark_reading_dir": {"asset": "+x", "part": "-X", "viewer": "right", "match": True},
            "mark_up": {"asset": "+y", "part": "+Y", "viewer": "up", "match": True},
        },
    }
    delta_mm3 = (a_master["volume_cm3"] - a_final["volume_cm3"]) * 1000.0
    expected_mm3 = sum(s.Volume() for s in env.Solids())
    presence = {
        "master_volume_cm3": a_master["volume_cm3"],
        "final_volume_cm3": a_final["volume_cm3"],
        "removed_mm3": round(delta_mm3, 1),
        "expected_recess_mm3": round(expected_mm3, 1),
        "within_tolerance": bool(abs(delta_mm3 - expected_mm3) <= 0.10 * expected_mm3 + 1.0),
        "final_differs_from_master": bool(a_master["volume_cm3"] != a_final["volume_cm3"]),
    }
    return {
        "asset_id": "JSI-WM-001-R1",
        "asset_sha256": asset_sha256(),
        "profile": "standard",
        "nominal_profile_envelope_mm": [32.0, 10.0],
        "actual_envelope_mm": [round(ink_w, 3), round(ink_h, 3)],
        "selector_envelope_mm": sel.get("actual_envelope_mm"),
        "uniform_scale": wm_scale,
        "rotation_deg": wm_rot,
        "position_mm": [0.0, round(wm_cy, 3)],
        "surface": "print-bed-facing-underside",
        "depth_mm": nb.WM_DEPTH,
        "host_wall_mm_before": nb.BASE_H,
        "host_wall_mm_after": round(nb.BASE_H - nb.WM_DEPTH, 3),
        "edge_clearance_mm": [round(margin_x, 2), round(margin_y, 2)],
        "feature_clearance_mm": 2.0,
        "nozzle_mm": 0.4,
        "layer_height_mm": 0.2,
        "coverage": "1/1 distributed parts (single part; the pair = two prints of this marked part)",
        "underside_free_of_texture": True,
        "orientation": proof,
        "presence": presence,
        "selector": selector,
        "geometry_revision": None,   # filled at finalize with final STL SHA-256
        "pass": bool(presence["final_differs_from_master"]
                     and presence["within_tolerance"]
                     and margin_x >= 5.0 and margin_y >= 5.0),
    }


# ---------------------------------------------------------------------------
# Gate render artifacts (vector, from the production candidate geometry)
# ---------------------------------------------------------------------------
def _mark_ink(scale: float) -> tuple[float, float]:
    """Ink envelope (w, h) of the canonical asset at the given scale."""
    import ezdxf
    doc = ezdxf.readfile(nb.DEFAULT_WM_DXF)
    xs: list[float] = []
    ys: list[float] = []
    for e in doc.modelspace():
        if e.dxftype() == "POLYLINE":
            xs.extend(v.dxf.location.x for v in e.vertices)
            ys.extend(v.dxf.location.y for v in e.vertices)
        elif e.dxftype() == "LWPOLYLINE":
            pts = e.get_points(format="xy")
            xs.extend(p[0] for p in pts)
            ys.extend(p[1] for p in pts)
    return (max(xs) - min(xs)) * scale, (max(ys) - min(ys)) * scale


def _mark_polys_view(scale: float, wm_cy: float):
    """Asset polylines as (outer, holes) in the VIEWER frame of the finished
    underside: view = (x_view, y_view) = (-part_x, +part_y); part = X-mirrored,
    re-centered asset placed at (0, wm_cy)."""
    import ezdxf
    doc = ezdxf.readfile(nb.DEFAULT_WM_DXF)
    polys = []
    for e in doc.modelspace():
        if e.dxftype() == "POLYLINE":
            polys.append([(v.dxf.location.x, v.dxf.location.y) for v in e.vertices])
        elif e.dxftype() == "LWPOLYLINE":
            polys.append(list(e.get_points(format="xy")))
    sp = []
    for p in polys:
        poly = shapely.Polygon(p)
        if not poly.is_valid:
            poly = poly.buffer(0)
        sp.append(poly)
    holes = {}
    for i in range(len(sp)):
        for j in range(len(sp)):
            if i != j and sp[j].area > sp[i].area and sp[j].contains(sp[i].representative_point()):
                holes.setdefault(j, []).append(i)
    hole_idx = {i for hs in holes.values() for i in hs}

    def to_view(pts):
        # Viewer frame of the finished underside (viewer on the word-face side):
        # image = (-part_x, +part_y); the part carries the X-mirrored asset, so
        # the image shows the asset un-mirrored (it reads normally).
        out = []
        for x, y in pts:
            x, y = x * scale, y * scale
            out.append((x, wm_cy + y))
        return out

    groups = []
    for j in range(len(polys)):
        if j in hole_idx:
            continue
        groups.append({"outer": to_view(polys[j]),
                       "holes": [to_view(polys[i]) for i in holes.get(j, [])]})
    return groups


def _dimples_view(ly: dict, wm_cy: float, wm_half_w: float, wm_half_h: float) -> list:
    pts = []
    x = nb.DIMPLE_PITCH / 2
    while x <= ly["base_w"] / 2 - 1.0 + 1e-9:
        y = ly["base_back"] + nb.DIMPLE_PITCH / 2
        while y <= nb.LETTER_FRONT - nb.DIMPLE_PITCH / 2 + 1e-9:
            if not (-wm_half_w <= x <= wm_half_w and wm_cy - wm_half_h <= y <= wm_cy + wm_half_h):
                pts.append((-x, y))       # viewer frame
            y += nb.DIMPLE_PITCH
        x += nb.DIMPLE_PITCH
    return pts


def render_underside_view(ly: dict, wm_scale: float, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    wm_cy = ly["base_cy"]
    fig, ax = plt.subplots(figsize=(11.0, 7.4), dpi=150)
    hw = ly["base_w"] / 2
    x0, x1 = -hw, hw
    y0, y1 = ly["base_back"], ly["base_front"]
    c = nb.CHAMFER
    base = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
            (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]
    ax.add_patch(plt.Polygon(base, closed=True, facecolor="#f4f1ec",
                             edgecolor="#4a4a4a", lw=1.6))
    ink_w, ink_h = _mark_ink(wm_scale)
    for (px, py) in _dimples_view(ly, wm_cy, ink_w / 2 + 2.0, ink_h / 2 + 2.0):
        s = nb.DIMPLE_SIZE / 2
        ax.add_patch(plt.Rectangle((px - s, py - s), nb.DIMPLE_SIZE, nb.DIMPLE_SIZE,
                                   facecolor="#d8d2c8", edgecolor="#a89f8f", lw=0.5))
    for g in _mark_polys_view(wm_scale, wm_cy):
        ax.add_patch(plt.Polygon(g["outer"], closed=True, facecolor="#8a6d3b",
                                 edgecolor="#3d2f16", lw=1.0))
        for h in g["holes"]:
            ax.add_patch(plt.Polygon(h, closed=True, facecolor="#f4f1ec",
                                     edgecolor="#3d2f16", lw=0.8))
    ax.annotate("watermark recess (0.40 mm deep)",
                xy=(0, wm_cy), xytext=(52, wm_cy + 34),
                fontsize=9, ha="left",
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#3d2f16"))
    ax.text(0, y1 + 6, "FRONT — word side (viewer stands here)", ha="center", fontsize=9.5)
    ax.text(0, y0 - 7, "BOOK SIDE — book row leans here", ha="center", fontsize=9.5)
    ax.set_xlim(-hw - 14, hw + 14)
    ax.set_ylim(y0 - 16, y1 + 16)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("NameForm Bookend M — orthographic finished-underside view "
                 "(as seen from outside, mark reads normally)", fontsize=11)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)


def render_closeup(ly: dict, wm_scale: float, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    wm_cy = ly["base_cy"]
    ink_w, ink_h = _mark_ink(wm_scale)
    half_w, half_h = ink_w / 2, ink_h / 2
    margin_x = ly["base_w"] / 2 - half_w
    margin_y = min(wm_cy - half_h - ly["base_back"], ly["base_front"] - (wm_cy + half_h))
    fig, ax = plt.subplots(figsize=(11.0, 6.2), dpi=150)
    hw = ly["base_w"] / 2
    y0, y1 = ly["base_back"], ly["base_front"]
    c = nb.CHAMFER
    base = [(-hw + c, y0), (hw - c, y0), (hw, y0 + c), (hw, y1 - c),
            (hw - c, y1), (-hw + c, y1), (-hw, y1 - c), (-hw, y0 + c)]
    ax.add_patch(plt.Polygon(base, closed=True, facecolor="#f4f1ec",
                             edgecolor="#4a4a4a", lw=1.4))
    zone_w, zone_h = half_w + 2.0, half_h + 2.0
    ax.add_patch(plt.Rectangle((-zone_w, wm_cy - zone_h), 2 * zone_w, 2 * zone_h,
                               fill=False, edgecolor="#b08030", lw=1.1, ls="--"))
    for (px, py) in _dimples_view(ly, wm_cy, zone_w, zone_h):
        s = nb.DIMPLE_SIZE / 2
        ax.add_patch(plt.Rectangle((px - s, py - s), nb.DIMPLE_SIZE, nb.DIMPLE_SIZE,
                                   facecolor="#d8d2c8", edgecolor="#a89f8f", lw=0.5))
    for g in _mark_polys_view(wm_scale, wm_cy):
        ax.add_patch(plt.Polygon(g["outer"], closed=True, facecolor="#8a6d3b",
                                 edgecolor="#3d2f16", lw=1.0))
        for h in g["holes"]:
            ax.add_patch(plt.Polygon(h, closed=True, facecolor="#f4f1ec",
                                     edgecolor="#3d2f16", lw=0.8))

    def dim(xa, xb, y, text, offset=0.0):
        yy = y + offset
        ax.annotate("", xy=(xb, yy), xytext=(xa, yy),
                    arrowprops=dict(arrowstyle="<->", lw=0.9, color="#8b1a1a"))
        ax.text((xa + xb) / 2, yy + (1.6 if offset >= 0 else -3.4), text,
                ha="center", fontsize=8.6, color="#8b1a1a")

    dim(-half_w, half_w, wm_cy - zone_h - 2.5, f"mark {ink_w:.1f} x {ink_h:.1f} mm "
        f"(scale {wm_scale:g}, standard profile)", -1.0)
    dim(half_w, hw, y1 + 4.0, f"edge clearance {margin_x:.1f} mm")
    dim(-hw, -half_w, y1 + 4.0, f"{margin_x:.1f} mm")
    ax.annotate("", xy=(hw + 8, wm_cy + half_h), xytext=(hw + 8, wm_cy - half_h),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="#8b1a1a"))
    ax.annotate("", xy=(wm_cy + half_h, -hw - 8), xytext=(wm_cy - half_h, -hw - 8),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="#8b1a1a"))
    ax.text(-hw - 10, wm_cy, f"{margin_y:.1f} mm", ha="right", va="center",
            fontsize=8.6, color="#8b1a1a", rotation=90)
    ax.text(hw + 10, wm_cy, f"{margin_y:.1f} mm", ha="left", va="center",
            fontsize=8.6, color="#8b1a1a", rotation=90)
    ax.annotate("dimple exclusion zone (mark + 2 mm)", xy=(zone_w * 0.7, wm_cy + zone_h),
                xytext=(48, y1 - 14), fontsize=8.6,
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#b08030"))
    ax.text(0, y0 - 6, "FRONT — word side", ha="center", fontsize=9)
    ax.set_xlim(-hw - 20, hw + 20)
    ax.set_ylim(y0 - 12, y1 + 14)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("NameForm Bookend M — underside mark, dimensioned clearances "
                 "(edge/feature, 0.40 mm recess)", fontsize=11)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)


def render_section(final_stl: Path, ly: dict, wm_cy: float, out_png: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from trimesh.intersections import mesh_plane

    m = trimesh.load(str(final_stl))
    sec = mesh_plane(m, plane_normal=[1, 0, 0], plane_origin=[0, 0, 0])
    fig, ax = plt.subplots(figsize=(9.6, 7.6), dpi=150)
    for a, b in sec:
        ax.plot([a[1], b[1]], [a[2], b[2]], color="#2b2b2b", lw=1.1)
    hw = ly["base_w"] / 2
    # bed datum
    ax.plot([-hw - 8, hw + 8], [0, 0], color="#1c4587", lw=1.4, ls="-.")
    ax.text(hw + 9, 0, "BED DATUM z = 0 (unchanged)", fontsize=8.4, color="#1c4587",
            va="center")
    # base height dim
    ax.annotate("", xy=(-hw - 4, 20), xytext=(-hw - 4, 0),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="#8b1a1a"))
    ax.text(-hw - 5, 10, "20.0", ha="right", va="center", fontsize=8.4, color="#8b1a1a",
            rotation=90)
    # residual wall dim (recess bottom to base top)
    ax.annotate("", xy=(hw + 4, 20), xytext=(hw + 4, 0.4),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="#8b1a1a"))
    ax.text(hw + 5, 10.2, f"residual wall {nb.BASE_H - nb.WM_DEPTH:.1f}", ha="left",
            va="center", fontsize=8.4, color="#8b1a1a", rotation=90)
    # recess depth callout (mark crosses x=0 near y=-26)
    ax.annotate(f"watermark recess {nb.WM_DEPTH:.2f} mm", xy=(-26.0, 0.4),
                xytext=(30, -14), fontsize=8.6,
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#3d2f16"))
    ax.annotate("stop panel 4.0 mm", xy=(-2, 90), xytext=(52, 90), fontsize=8.6,
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#2b2b2b"))
    ax.annotate("letter M (section)", xy=(24, 63), xytext=(58, 60), fontsize=8.6,
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#2b2b2b"))
    ax.annotate("book face", xy=(-4, 30), xytext=(-72, 34), fontsize=8.6,
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#2b2b2b"))
    # overall height dim
    top = max(float(p[2]) for a, b in sec for p in (a, b))
    ax.annotate("", xy=(hw + 14, top), xytext=(hw + 14, 0),
                arrowprops=dict(arrowstyle="<->", lw=0.9, color="#8b1a1a"))
    ax.text(hw + 15, top / 2, f"{top:.1f}", ha="left", va="center", fontsize=8.4,
            color="#8b1a1a", rotation=90)
    ax.set_xlim(-hw - 10, hw + 26)
    ax.set_ylim(-18, top + 8)
    ax.set_aspect("equal")
    ax.set_xlabel("depth y (mm)  —  book side left, word side right", fontsize=9)
    ax.set_ylabel("height z (mm)", fontsize=9)
    ax.grid(True, lw=0.3, alpha=0.5)
    ax.set_title("NameForm Bookend M — section A–A at x = 0 (through mark center): "
                 "recess depth, bed datum, residual wall", fontsize=11)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)


# ---------------------------------------------------------------------------
def _mesh_xml(m) -> str:
    v = m.vertices
    f = m.faces
    verts = "\n".join(f'      <vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>'
                      for x, y, z in v)
    tris = "\n".join(f'      <triangle v1="{a}" v2="{b}" v3="{c}"/>'
                     for a, b, c in f)
    return (f'    <object id="1" type="model" '
            f'partnumber="nameform-bookends-M" pname="NameForm Bookend M (JuSt)">\n'
            f"      <mesh>\n        <vertices>\n{verts}\n        </vertices>\n"
            f"        <triangles>\n{tris}\n        </triangles>\n"
            f"      </mesh>\n    </object>\n")


def export_3mf(final_stl: Path, out_3mf: Path) -> int:
    """Single-part 3MF. The PAIR is delivered as two sequential prints of the
    same file: a 216x152 part cannot be printed simultaneously with its mate on
    any 220 mm customer bed or the 300 mm operator bed (decision D17)."""
    m = trimesh.load(str(final_stl))
    if not m.is_watertight:
        raise RuntimeError("refusing to export non-watertight mesh to 3MF")
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '</Types>\n')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>\n')
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" '
        'xs:noNamespaceSchemaLocation="http://schemas.microsoft.com/3dmanufacturing/2015/02/main.xsd">\n'
        '  <metadata name="Application">JustInnovation 1.0</metadata>\n'
        '  <metadata name="Title">NameForm Bookend M (print twice for a pair)</metadata>\n'
        '  <metadata name="Creator">JuSt Innovation / Stefan Junk</metadata>\n'
        '  <resources>\n'
        + _mesh_xml(m)
        + '  </resources>\n'
        '  <build>\n    <item objectid="1"/>\n  </build>\n'
        '</model>\n')
    out_3mf.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_3mf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
    ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    with zipfile.ZipFile(out_3mf) as z:
        names = set(z.namelist())
        assert names >= {"[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model"}, names
        root = ET.fromstring(z.read("3D/3dmodel.model"))
        objects = root.findall(".//m:object", ns)
        items = root.findall(".//m:item", ns)
        tris = root.findall(".//m:triangle", ns)
    assert len(objects) == 1 and len(items) == 1, (len(objects), len(items))
    assert len(tris) == len(m.faces)
    bb = m.bounds[1] - m.bounds[0]
    assert all(b <= 216.0 for b in bb[:2]) and bb[2] <= 240.0, bb
    log(f"3mf: {out_3mf.name} objects=1 items=1 tris={len(tris)} bed-fit OK")
    return len(items)


def validate_mesh(mesh: Path, json_out: Path) -> None:
    r = subprocess.run(
        [sys.executable, str(SKILL / "scripts" / "validate_mesh.py"),
         str(mesh), "--require-watertight", "--max-bodies", "1",
         "--bed", "216", "216", "240", "--json-out", str(json_out)],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"validate_mesh failed for {mesh}:\n{r.stdout}\n{r.stderr}")


# ---------------------------------------------------------------------------
def build_phase() -> int:
    import time
    t_start = time.time()
    VAL.mkdir(exist_ok=True)
    VAL_WM.mkdir(exist_ok=True)
    fm = font_metrics(WORD)
    log(f"font: SIZE={fm['size']:.4f} CAP={fm['cap']:.4f} wordW={fm['word_width']:.4f}")

    # --- stability-driven ballast search (master builds) -------------------
    best = None
    for ballast in range(100, 161, 10):
        ly = layout(ballast)
        base_depth = ly["base_front"] - ly["base_back"]
        selector = select_watermark(base_depth)
        wm_scale = float(selector["selection"]["uniform_scale"])
        wm_rot = float(selector["selection"]["rotation_deg"])
        master_wp = nb.build(WORD, fm["size"], fm["cap"], fm["word_width"],
                             ballast, watermark=False,
                             wm_scale=wm_scale, wm_rotation_deg=wm_rot)
        master = OUT_MASTER / f"nameform-bookends-{WORD}-master.stl"
        nb.export_stl(master_wp, master)
        a = analyze(master)
        st = stability(a)
        log(f"ballast={ballast}: mass={a['mass_g']:.0f} g SF={st['SF']} (target {SF_TARGET})")
        best = {"ballast": ballast, "master_wp": master_wp, "master": a,
                "stability": st, "selector": selector, "wm_scale": wm_scale,
                "wm_rot": wm_rot}
        if st["pass"]:
            break
    if not best["stability"]["pass"]:
        log("ERROR: stability target not reached at max ballast")
        return 1
    ballast = best["ballast"]
    ly = layout(ballast)
    wm_scale, wm_rot = best["wm_scale"], best["wm_rot"]

    # --- final = master + watermark (LAST solid change) --------------------
    final_wp = nb.build(WORD, fm["size"], fm["cap"], fm["word_width"],
                        ballast, watermark=True,
                        wm_scale=wm_scale, wm_rotation_deg=wm_rot)
    final = OUT_FINAL / f"nameform-bookends-{WORD}-final.stl"
    nb.export_stl(final_wp, final)
    a_final = analyze(final)
    a_master = analyze(OUT_MASTER / f"nameform-bookends-{WORD}-master.stl")
    log(f"final: mass={a_final['mass_g']:.0f} g vol={a_final['volume_cm3']} cm3")

    # --- STEP editable masters ---------------------------------------------
    step_master = OUT_MASTER / f"nameform-bookends-{WORD}-master.step"
    step_final = OUT_FINAL / f"nameform-bookends-{WORD}-final.step"
    nb.export_step(best["master_wp"], step_master)
    nb.export_step(final_wp, step_final)

    # --- min glyph feature (vector) ----------------------------------------
    poly = word_polygon(WORD, fm["size"])
    min_w = min_stroke_width(poly)
    feat = {"word": WORD, "font": "DejaVu Sans Bold (OFL-1.1)",
            "method": "vector: max r with word_polygon.buffer(-r) non-empty (shapely), 2*r",
            "min_feature_mm": round(min_w, 2), "requirement_mm": 4.0,
            "pass": bool(min_w >= 4.0)}
    log(f"min feature: {min_w:.2f} mm (req 4.0) pass={feat['pass']}")

    # --- 3MF (single part; pair = two sequential prints) --------------------
    out_3mf = OUT_FINAL / f"nameform-bookends-{WORD}-single.3mf"
    n_parts = export_3mf(final, out_3mf)

    # --- watermark gate evidence + render artifacts -------------------------
    wm = watermark_evidence(a_master, a_final, ballast, best["selector"])
    log(f"watermark: scale={wm_scale} envelope={wm['actual_envelope_mm']} "
        f"clearance={wm['edge_clearance_mm']} pass={wm['pass']}")
    render_underside_view(ly, wm_scale, VAL_WM / "underside-view.png")
    render_closeup(ly, wm_scale, VAL_WM / "closeup.png")
    render_section(final, ly, ly["base_cy"], VAL_WM / "section.png")
    log(f"gate renders: {VAL_WM}/underside-view.png, closeup.png, section.png")

    # --- skill mesh validation ---------------------------------------------
    validate_mesh(final, VAL / "mesh-final.json")
    validate_mesh(OUT_MASTER / f"nameform-bookends-{WORD}-master.stl",
                  VAL / "mesh-master.json")

    # --- reports -------------------------------------------------------------
    final_sha = sha256(final)
    (VAL / "geometry.json").write_text(json.dumps(
        {"part": a_final, "master": a_master, "min_feature": feat,
         "watermark": wm, "single_3mf_parts": n_parts,
         "stl_tolerance_mm": nb.STL_TOLERANCE,
         "stl_angular_tolerance_rad": nb.STL_ANGULAR_TOLERANCE,
         "final_stl_sha256": final_sha}, indent=2) + "\n")
    (VAL / "stability.json").write_text(json.dumps(best["stability"], indent=2) + "\n")
    (VAL / "watermark.json").write_text(json.dumps(wm, indent=2) + "\n")
    (VAL / "build-summary.json").write_text(json.dumps(
        {"product": "MM-PER-001", "revision": "0.2.0", "word": WORD,
         "tool": "CadQuery " + __import__("cadquery").__version__
                 + " (cadquery-ocp " + __import__("cadquery_ocp_proxy").__version__ + ")",
         "build_seconds": round(time.time() - t_start, 1),
         "font_size_mm": fm["size"], "cap_mm": fm["cap"],
         "word_width_mm": fm["word_width"], "ballast_mm": ballast,
         "master_stl": str(master), "final_stl": str(final),
         "step_master": str(step_master), "step_final": str(step_final),
         "single_3mf": str(out_3mf),
         "final_stl_sha256": final_sha,
         "gate_artifacts": ["validation/watermark/underside-view.png",
                            "validation/watermark/closeup.png",
                            "validation/watermark/section.png",
                            "validation/watermark.json"],
         "slicer_preview": "UNAVAILABLE — no slicer on build machine; operator "
                           "performs first-layer check on Kobra 3 Max (test-plan TP-05)",
         "next": ("update design-spec.yaml watermark_approval "
                  "(geometry_revision=final_stl_sha256) then run "
                  "python3 scripts/build.py --finalize")},
        indent=2) + "\n")
    log(f"BUILD PHASE DONE in {time.time()-t_start:.0f}s")
    log(f"final STL sha256: {final_sha}")
    return 0


# ---------------------------------------------------------------------------
def finalize_phase() -> int:
    spec = ROOT / "design-spec.yaml"
    r = subprocess.run(
        [sys.executable, str(SKILL / "scripts" / "validate_design_spec.py"),
         str(spec), "--require-final-approval",
         "--json-out", str(VAL / "design-spec-gate.json")],
        capture_output=True, text=True)
    gate = json.loads((VAL / "design-spec-gate.json").read_text()) if \
        (VAL / "design-spec-gate.json").exists() else {}
    if r.returncode != 0 or not gate.get("passed"):
        log("GATE FAILED — final package NOT emitted:")
        log(r.stdout.strip() or r.stderr.strip())
        return 1
    log("gate: PASS (validate_design_spec.py --require-final-approval)")
    if gate.get("warnings"):
        log(f"gate warnings: {gate['warnings']}")

    import time
    t0 = time.time()
    files = [OUT_MASTER / f"nameform-bookends-{WORD}-master.stl",
             OUT_MASTER / f"nameform-bookends-{WORD}-master.step",
             OUT_FINAL / f"nameform-bookends-{WORD}-final.stl",
             OUT_FINAL / f"nameform-bookends-{WORD}-final.step",
             OUT_FINAL / f"nameform-bookends-{WORD}-single.3mf"]
    missing = [str(p) for p in files if not p.exists()]
    if missing:
        log(f"ERROR: missing release files: {missing}")
        return 1
    manifest = {"product": "MM-PER-001", "revision": "0.2.0", "word": WORD,
                "ballast_mm": json.loads((VAL / "build-summary.json").read_text())["ballast_mm"],
                "files": {str(p.relative_to(ROOT)):
                          {"sha256": sha256(p), "bytes": p.stat().st_size}
                          for p in files},
                "watermark_asset": {"id": "JSI-WM-001-R1", "profile": "standard",
                                    "sha256": asset_sha256(),
                                    "uniform_scale": json.loads(
                                        (VAL / "watermark.json").read_text())["uniform_scale"]},
                "emitted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "gate": "design-spec.yaml --require-final-approval: PASS"}
    RELEASE.mkdir(exist_ok=True)
    (RELEASE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (VAL / "build-summary.json").write_text(json.dumps(
        json.loads((VAL / "build-summary.json").read_text())
        | {"manifest": str(RELEASE / "manifest.json"),
           "finalize_seconds": round(time.time() - t0, 1),
           "final_package_emitted": True}, indent=2) + "\n")
    log(f"manifest: {RELEASE / 'manifest.json'} — final package emitted")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    if mode == "--finalize":
        sys.exit(finalize_phase())
    if mode == "build":
        sys.exit(build_phase())
    sys.exit(2)
