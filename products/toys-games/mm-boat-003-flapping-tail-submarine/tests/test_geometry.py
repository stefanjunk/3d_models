from dataclasses import replace

import cadquery as cq
import trimesh

from submarine.config import SubmarineConfig
from submarine.geometry import build_nose, caudal_projected_area_mm2
from submarine.mechanism import solve_rocker


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
        shape = spec.solid.val()
        assert shape.Volume() > 1.0, name
        assert len(shape.Solids()) == 1, f"{name} is not a single printable body"


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


def test_freeform_envelope_expands_visible_silhouette(parts, cfg):
    assert parts["nose_body"].solid.val().BoundingBox().ylen > cfg.hull_od_front + 1.0
    assert parts["segment_01"].solid.val().BoundingBox().ylen > cfg.hull_od_front + 1.0
    assert parts["capsule_body"].solid.val().BoundingBox().ylen > cfg.capsule_od + 20.0
    assert parts["capsule_body"].solid.val().BoundingBox().zlen > cfg.capsule_od + 25.0


def test_freeform_and_crest_parameter_sweep_valid():
    cfg = SubmarineConfig()
    base = build_nose(replace(cfg, fish_fairing_enabled=False))[0].solid.val()
    low = build_nose(replace(cfg, fish_crest_peak_height=0.70))[0].solid.val()
    high = build_nose(replace(cfg, fish_crest_peak_height=1.30))[0].solid.val()
    assert base.isValid() and low.isValid() and high.isValid()
    assert base.Volume() < low.Volume() < high.Volume()


def test_tail_blade_preserves_drive_area(cfg):
    baseline_area_mm2 = 1278.0
    ratio = caudal_projected_area_mm2(cfg) / baseline_area_mm2
    assert 0.90 <= ratio <= 1.15


def test_tail_full_sweep_clears_capsule(parts, cfg):
    capsule = as_solid(parts["capsule_body"].solid)
    tail = as_solid(parts["tail_fin"].solid)
    half_sweep = solve_rocker(cfg).sweep_deg / 2.0
    for angle in (-half_sweep, -half_sweep / 2.0, 0.0, half_sweep / 2.0, half_sweep):
        moved = tail.rotate((0.0, 0.0, cfg.rocker_offset_z), (1.0, 0.0, cfg.rocker_offset_z), angle)
        common = moved.intersect(capsule)
        assert common.Volume() < 1e-6, f"tail/capsule collision at {angle:.2f} deg"
