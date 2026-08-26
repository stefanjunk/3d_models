import cadquery as cq
import trimesh

from submarine.config import SubmarineConfig
from submarine.geometry import build_nose


def as_solid(obj) -> cq.Solid:
    sh = obj.val() if hasattr(obj, "val") else obj
    return sh if isinstance(sh, cq.Solid) else sh.Solids()[0]


EXPECTED = {
    "nose_body", "bladder_piston", "segment_01", "segment_02", "segment_03",
    "segment_04", "capsule_body", "capsule_cap", "pivot_pin", "crank_disc",
    "shaft_sleeve", "tail_rocker", "tail_fin", "keel_plug", "ballast_box",
    "ballast_lid", "hinge_pin",
}

NO_CONTACT = [
    ("crank_disc", "capsule_body"),
    ("crank_disc", "tail_rocker"),
    ("tail_rocker", "capsule_body"),
    ("tail_fin", "capsule_body"),
    ("tail_fin", "tail_rocker"),
    ("shaft_sleeve", "capsule_body"),
    ("bladder_piston", "nose_body"),
    ("capsule_cap", "capsule_body"),
    ("ballast_box", "capsule_body"),
    ("pivot_pin", "capsule_body"),
    ("keel_plug", "capsule_body"),
    ("hinge_pin", "nose_body"),
    ("hinge_pin", "segment_01"),
    ("ballast_lid", "capsule_body"),
    ("capsule_cap", "segment_04"),
    ("nose_body", "segment_01"),
    ("segment_01", "segment_02"),
    ("segment_02", "segment_03"),
    ("segment_03", "segment_04"),
    ("segment_04", "capsule_body"),
]


def test_all_parts_present(parts):
    assert set(parts) == EXPECTED


def test_positive_volumes(parts):
    for name, spec in parts.items():
        assert spec.solid.val().Volume() > 1.0, name


def test_hull_parts_watertight(parts):
    for name in ("nose_body", "segment_01", "segment_02", "segment_03",
                 "segment_04", "capsule_body", "capsule_cap"):
        solid = parts[name].solid.val()
        verts, faces = solid.tessellate(0.1)
        m = trimesh.Trimesh([v.toTuple() for v in verts], faces, process=True)
        assert m.is_watertight, name


def test_no_unintended_contact(parts):
    for a, b in NO_CONTACT:
        common = as_solid(parts[a].solid).intersect(as_solid(parts[b].solid))
        assert common.Volume() < 1e-6, f"{a} touches {b}: {common.Volume():.3f} mm^3"


def test_drive_parts_engage(parts):
    """crank pin must actually sit inside the rocker slot at rest."""
    disc = parts["crank_disc"].solid.val()
    rocker = parts["tail_rocker"].solid.val()
    bb_d, bb_r = disc.BoundingBox(), rocker.BoundingBox()
    assert bb_d.xmin < bb_r.xmax and bb_r.xmin < bb_d.xmax


def test_bed_fit(parts, cfg):
    for name, spec in parts.items():
        bb = spec.solid.val().BoundingBox()
        dims = sorted((bb.xlen, bb.ylen, bb.zlen), reverse=True)
        assert dims[0] <= cfg.print_bed[0] and dims[1] <= cfg.print_bed[1], name


def test_fish_ribs_expand_visible_envelope(parts, cfg):
    assert parts["nose_body"].solid.val().BoundingBox().ylen > cfg.hull_od_front + 1.0
    assert parts["segment_01"].solid.val().BoundingBox().ylen > cfg.hull_od_front + 1.0
    assert parts["capsule_body"].solid.val().BoundingBox().ylen > cfg.capsule_od + 2.0


def test_fish_rib_parameter_sweep_valid():
    base = build_nose(SubmarineConfig(fish_ribs_enabled=False))[0].solid.val()
    low = build_nose(
        SubmarineConfig(fish_rib_peak_radius=1.0, fish_rib_end_radius=0.65, fish_rib_overlap=0.4)
    )[0].solid.val()
    high = build_nose(
        SubmarineConfig(fish_rib_peak_radius=2.0, fish_rib_end_radius=1.2, fish_rib_overlap=0.8)
    )[0].solid.val()
    assert base.isValid() and low.isValid() and high.isValid()
    assert base.Volume() < low.Volume() < high.Volume()
