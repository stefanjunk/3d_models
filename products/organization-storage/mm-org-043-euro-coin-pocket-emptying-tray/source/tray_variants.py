"""MM-ORG-043 optimization variants - lightweighting candidates for the coin tray.

The baseline master stays source/tray.py; this module never writes over it. Each
variant isolates one lever family:

  B1  cell pitch tightened to the minimum-wall limit; footprint shrinks, no coin fit changes
  B2  B1 + every recess cut to the deepest recess depth, so the eight staggered solid
      floor stacks collapse into one plane

Protected: coin recess diameters (EU nominals + the named clearance), the named clearance
itself, the 2.0 mm under-floor, the finger notches, the rim, the flat underside, the
support-free entry ramp and the outer envelope ceiling.
"""
from __future__ import annotations
import json, sys
from dataclasses import dataclass
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
P = json.loads((PROD / "parameters" / "tray.json").read_text(encoding="utf-8"))

COINS = P["coins"]
CLR = P["recess_clearance_mm"]["value"]
BOUND = P["recess_clearance_mm"]["upper_bound_mm"]
NPR = P["coins_per_recess"]
EXTRA = P["recess_extra_depth_mm"]
NW, ND = P["notch_width_mm"], P["notch_depth_mm"]
COLS, ROWS = P["cols"], P["rows"]
WALL = P["wall_mm"]
RIM = P["rim_mm"]
UNDER = P["under_floor_mm"]
RIM_ABOVE = P["rim_above_field_mm"]
SD, SR = P["slope_depth_mm"], P["slope_rise_mm"]
FIL, MINW = P["edge_fillet_mm"], P["minimum_wall_mm"]
ENV = P["envelope_ceiling_mm"]

DEPTHS = {c["id"]: c["edge_mm"] * NPR + EXTRA for c in COINS}
MAX_DEPTH = max(DEPTHS.values())
SLAB_Z = MAX_DEPTH + UNDER


@dataclass(frozen=True)
class Cfg:
    name: str
    pitch_x_mm: float
    pitch_y_mm: float
    uniform_depth: bool = False


BASELINE = Cfg("baseline", P["cell_pitch_x_mm"], P["cell_pitch_y_mm"])
B1 = Cfg("b1-pitch", 28.0, 28.0)
B2 = Cfg("b2-pitch-uniform-depth", 28.0, 28.0, uniform_depth=True)
VARIANTS = {c.name: c for c in (BASELINE, B1, B2)}


def _check(cfg: Cfg) -> None:
    if CLR > BOUND:
        raise ValueError(f"recess clearance {CLR} exceeds the separation bound {BOUND}")
    ds = sorted(c["diameter_mm"] for c in COINS)
    step = min(b - a for a, b in zip(ds, ds[1:]))
    if CLR >= step / 2:
        raise ValueError(f"clearance {CLR} >= half the smallest diameter step {step}")
    biggest = max(c["diameter_mm"] for c in COINS) + CLR
    for axis, pitch in (("x", cfg.pitch_x_mm), ("y", cfg.pitch_y_mm)):
        if pitch - biggest < MINW:
            raise ValueError(
                f"{cfg.name}: cell pitch {axis}={pitch} leaves "
                f"{pitch - biggest:.2f} mm between recesses, below {MINW}")
    if RIM < MINW or UNDER < MINW:
        raise ValueError("rim or under-floor below the minimum wall")


def _assert_envelope(solid, name: str) -> None:
    bb = solid.val().BoundingBox()
    got = [bb.xlen, bb.ylen, bb.zlen]
    if any(g > e + 1e-6 for g, e in zip(got, ENV)):
        raise ValueError(f"{name} actual bounding box {[round(g,2) for g in got]} "
                         f"exceeds ceiling {ENV}")


def build(cfg: Cfg) -> cq.Workplane:
    _check(cfg)
    field_x = COLS * cfg.pitch_x_mm
    field_y = ROWS * cfg.pitch_y_mm
    outer_x = field_x + 2 * RIM
    outer_y = field_y + SD + 2 * RIM
    body = cq.Workplane("XY").box(outer_x, outer_y, SLAB_Z, centered=(True, True, False))
    body = body.union(
        cq.Workplane("XY").box(outer_x, outer_y, RIM_ABOVE, centered=(True, True, False))
        .translate((0, 0, SLAB_Z))
        .cut(cq.Workplane("XY").box(outer_x - 2 * RIM, outer_y - 2 * RIM, RIM_ABOVE,
                                    centered=(True, True, False)).translate((0, 0, SLAB_Z))))
    y0 = -outer_y / 2 + RIM + field_y
    ramp = (cq.Workplane("YZ")
            .polyline([(y0, SLAB_Z), (y0 + SD, SLAB_Z), (y0 + SD, SLAB_Z + SR)]).close()
            .extrude(outer_x - 2 * RIM)
            .translate((-(outer_x - 2 * RIM) / 2, 0, 0)))
    body = body.union(ramp)
    for i, coin in enumerate(sorted(COINS, key=lambda c: c["diameter_mm"])):
        col, row = i % COLS, i // COLS
        x = -field_x / 2 + cfg.pitch_x_mm / 2 + col * cfg.pitch_x_mm
        y = -outer_y / 2 + RIM + cfg.pitch_y_mm / 2 + row * cfg.pitch_y_mm
        d = coin["diameter_mm"] + CLR
        depth = MAX_DEPTH if cfg.uniform_depth else DEPTHS[coin["id"]]
        body = body.cut(cq.Workplane("XY").circle(d / 2).extrude(depth)
                        .translate((x, y, SLAB_Z - depth)))
        body = body.cut(cq.Workplane("XY").box(NW, ND * 2, depth, centered=(True, True, False))
                        .translate((x, y - d / 2, SLAB_Z - depth)))
    body = body.edges("|Z").fillet(FIL)
    _assert_envelope(body, cfg.name)
    return body


def main(argv: list[str]) -> int:
    out = PROD / "source" / "generated" / "variants"
    out.mkdir(parents=True, exist_ok=True)
    facts = []
    for name in (argv or list(VARIANTS)):
        cfg = VARIANTS[name]
        solid = build(cfg)
        cq.exporters.export(solid, str(out / f"coin-tray-{name}.step"))
        cq.exporters.export(solid, str(out / f"coin-tray-{name}.stl"),
                            opt={"tolerance": 0.01, "angularTolerance": 0.1})
        bb = solid.val().BoundingBox()
        biggest = max(c["diameter_mm"] for c in COINS) + CLR
        f = {"variant": name,
             "config": {"pitch_x_mm": cfg.pitch_x_mm, "pitch_y_mm": cfg.pitch_y_mm,
                        "uniform_depth": cfg.uniform_depth},
             "bbox_mm": [round(v, 3) for v in (bb.xlen, bb.ylen, bb.zlen)],
             "volume_mm3": round(solid.val().Volume(), 1),
             "inter_recess_wall_mm": round(min(cfg.pitch_x_mm, cfg.pitch_y_mm) - biggest, 3),
             "recess_depths_mm": ({c["id"]: MAX_DEPTH for c in COINS} if cfg.uniform_depth
                                  else {k: round(v, 3) for k, v in DEPTHS.items()})}
        facts.append(f)
        print(f"{name}: {f['bbox_mm']} mm, {f['volume_mm3']} mm3, "
              f"inter-recess wall {f['inter_recess_wall_mm']} mm")
    (PROD / "optimization" / "variant-geometry.json").write_text(
        json.dumps({"schema_version": "1.0", "product": "MM-ORG-043",
                    "baseline_source": "source/tray.py",
                    "recess_clearance_status": P["recess_clearance_mm"]["status"],
                    "variants": facts}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
