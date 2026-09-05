"""MM-ORG-042 optimization variants - lightweighting candidates for the lane block.

The baseline master stays source/divider.py; this module never writes over it.
Each variant is one isolated lever family so a measured improvement stays traceable:

  B1  floor thickness only, silhouette unchanged
  B2  B1 + thinner internal dividers + scooped divider tops (visible change)

Protected geometry (never altered): lane clear length along the A6 105 mm edge,
lane floor datum, divider inner faces, rear wall spine, index tab faces, flat bed
face, outer envelope ceiling. The lane clearance stays UNQUALIFIED_PROVISIONAL and
is carried through unchanged - no variant makes a fit claim.
"""
from __future__ import annotations
import json, sys
from dataclasses import dataclass, replace
from pathlib import Path
import cadquery as cq

HERE = Path(__file__).resolve().parent
PROD = HERE.parent
P = json.loads((PROD / "parameters" / "divider.json").read_text(encoding="utf-8"))

MEDIA_W = P["media"]["width_mm"]
CLR = P["lane_clearance_mm"]["value"]
N = P["lane_count"]
PITCH = P["lane_pitch_mm"]
TAB_H = P["tab_height_mm"]
TAB_W = P["tab_width_mm"]
TAB_T = P["tab_thickness_mm"]
FILLET = P["edge_fillet_mm"]
MIN_WALL = P["minimum_wall_mm"]
ENV = P["envelope_ceiling_mm"]

OUTER_W = N * PITCH + P["wall_mm"]          # frozen from the baseline: 133.6 mm
LANE_LEN = MEDIA_W + CLR                    # 105.6 mm clear along the card edge
OUTER_LEN = LANE_LEN + 2 * P["wall_mm"]     # 108.8 mm


@dataclass(frozen=True)
class Cfg:
    name: str
    floor_mm: float
    wall_out_mm: float
    wall_in_mm: float
    depth_mm: float
    scoop_front_mm: float | None = None   # divider height above the floor at the open side
    scoop_run_mm: float = 0.0             # length over which it ramps back to full depth

    @property
    def lane_w(self) -> float:
        return (OUTER_W - 2 * self.wall_out_mm - (N - 1) * self.wall_in_mm) / N

    @property
    def outer_h(self) -> float:
        return self.floor_mm + self.depth_mm


BASELINE = Cfg("baseline", floor_mm=P["floor_mm"], wall_out_mm=P["wall_mm"],
               wall_in_mm=P["wall_mm"], depth_mm=P["lane_depth_mm"])
B1 = replace(BASELINE, name="b1-floor", floor_mm=1.4)
B2 = replace(B1, name="b2-floor-thin-scoop", wall_in_mm=1.35,
             scoop_front_mm=22.0, scoop_run_mm=75.0)
VARIANTS = {c.name: c for c in (BASELINE, B1, B2)}


def _check(cfg: Cfg) -> None:
    for label, w in (("outer wall", cfg.wall_out_mm), ("inner wall", cfg.wall_in_mm),
                     ("tab", TAB_T)):
        if w < MIN_WALL:
            raise ValueError(f"{cfg.name}: {label} {w} below minimum wall {MIN_WALL}")
    if cfg.lane_w <= 0:
        raise ValueError(f"{cfg.name}: non-positive lane width")
    if cfg.floor_mm < 1.2:
        raise ValueError(f"{cfg.name}: floor {cfg.floor_mm} below the 1.2 mm bottom shell")
    if cfg.scoop_front_mm is not None:
        if not 0 < cfg.scoop_front_mm < cfg.depth_mm:
            raise ValueError(f"{cfg.name}: scoop front height outside (0, depth)")
        if not 0 < cfg.scoop_run_mm < LANE_LEN:
            raise ValueError(f"{cfg.name}: scoop run must stay inside the lane length")


def _lane_centres(cfg: Cfg) -> list[float]:
    x = -OUTER_W / 2 + cfg.wall_out_mm
    out = []
    for _ in range(N):
        out.append(x + cfg.lane_w / 2)
        x += cfg.lane_w + cfg.wall_in_mm
    return out


def build(cfg: Cfg) -> cq.Workplane:
    """Open-top lane block: open top, one open long side, flat underside."""
    _check(cfg)
    body = cq.Workplane("XY").box(OUTER_W, OUTER_LEN, cfg.outer_h,
                                  centered=(True, True, False))
    for x in _lane_centres(cfg):
        body = body.cut(
            cq.Workplane("XY").box(cfg.lane_w, LANE_LEN, cfg.depth_mm,
                                   centered=(True, True, False))
            .translate((x, 0, cfg.floor_mm)))
    # open one long side so the media stays visible and reachable edge-on
    body = body.cut(
        cq.Workplane("XY").box(OUTER_W + 2, cfg.wall_out_mm + 0.2, cfg.depth_mm,
                               centered=(True, True, False))
        .translate((0, -OUTER_LEN / 2 + cfg.wall_out_mm / 2 - 0.1, cfg.floor_mm)))
    for x in _lane_centres(cfg):
        body = body.union(
            cq.Workplane("XY").box(TAB_W, TAB_T, TAB_H, centered=(True, True, False))
            .translate((x, OUTER_LEN / 2 - cfg.wall_out_mm / 2, cfg.outer_h)))
    body = body.edges("|Z").fillet(FILLET)
    if cfg.scoop_front_mm is not None:
        body = body.cut(_scoop(cfg))
    return body


def _scoop(cfg: Cfg) -> cq.Workplane:
    """Wedge removed from every divider top, low at the open side, full depth at the rear."""
    y0 = -OUTER_LEN / 2 - 1.0
    y1 = -OUTER_LEN / 2 + cfg.wall_out_mm + cfg.scoop_run_mm
    z_front = cfg.floor_mm + cfg.scoop_front_mm
    z_full = cfg.outer_h
    z_top = cfg.outer_h + TAB_H + 5.0
    pts = [(y0, z_front), (y1, z_full), (y1, z_top), (y0, z_top)]
    return (cq.Workplane("YZ").polyline(pts).close()
            .extrude(OUTER_W + 4.0).translate((-(OUTER_W + 4.0) / 2, 0, 0)))


def _facts(cfg: Cfg, solid: cq.Workplane) -> dict:
    s = solid.val()
    bb = s.BoundingBox()
    got = [bb.xlen, bb.ylen, bb.zlen]
    if any(g > e + 1e-6 for g, e in zip(got, ENV)):
        raise ValueError(f"{cfg.name}: envelope {got} exceeds ceiling {ENV}")
    return {
        "variant": cfg.name,
        "config": {k: getattr(cfg, k) for k in
                   ("floor_mm", "wall_out_mm", "wall_in_mm", "depth_mm",
                    "scoop_front_mm", "scoop_run_mm")},
        "lane_clear_width_mm": round(cfg.lane_w, 4),
        "lane_clear_length_mm": LANE_LEN,
        "bbox_mm": [round(v, 3) for v in got],
        "volume_mm3": round(s.Volume(), 1),
    }


def main(argv: list[str]) -> int:
    out = PROD / "source" / "generated" / "variants"
    out.mkdir(parents=True, exist_ok=True)
    wanted = argv or list(VARIANTS)
    facts = []
    for name in wanted:
        cfg = VARIANTS[name]
        solid = build(cfg)
        cq.exporters.export(solid, str(out / f"divider-block-{name}.step"))
        cq.exporters.export(solid, str(out / f"divider-block-{name}.stl"),
                            opt={"tolerance": 0.01, "angularTolerance": 0.1})
        f = _facts(cfg, solid)
        facts.append(f)
        print(f"{name}: {f['bbox_mm']} mm, {f['volume_mm3']} mm3, "
              f"lane clear {f['lane_clear_width_mm']} mm")
    (PROD / "optimization" / "variant-geometry.json").write_text(
        json.dumps({"schema_version": "1.0", "product": "MM-ORG-042",
                    "baseline_source": "source/divider.py",
                    "lane_clearance_status": P["lane_clearance_mm"]["status"],
                    "variants": facts}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
