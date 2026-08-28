import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_024_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_three_measured_clip_presets():
    assert [(item["id"], item["gap_mm"]) for item in PARAMS["clip_presets"]] == [
        ("thin", 2.2),
        ("shelffit", 2.9),
        ("thick", 3.6),
    ]


def test_host_clearances_are_bounded():
    gaps = np.array([item["gap_mm"] for item in PARAMS["clip_presets"]])
    hosts = np.array([item["target_host_thickness_mm"] for item in PARAMS["clip_presets"]])
    assert np.allclose(gaps - hosts, [0.28, 0.23, 0.30])


def test_face_is_one_valid_solid():
    build = load_build()
    shape, interface = build.make_face(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["outer_dimensions_mm"] == [120.0, 48.0, 15.0]


def test_all_clips_are_valid_single_solids():
    build = load_build()
    for preset in PARAMS["clip_presets"]:
        shape, interface = build.make_clip(PARAMS, preset)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert interface["gap_mm"] == preset["gap_mm"]
        assert interface["external_assets"] == []


def test_gap_gauge_reproduces_clip_series():
    build = load_build()
    shape, interface = build.make_gap_gauge(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["gaps_mm"] == [2.2, 2.9, 3.6]


def test_key_coupon_matches_face_slot():
    build = load_build()
    _, face = build.make_face(PARAMS)
    shape, coupon = build.make_key_coupon(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert coupon["key_slot_mm"] == face["key_slot_mm"]


def test_label_pocket_has_declared_clearance():
    face = PARAMS["face"]
    assert np.isclose(face["label_pocket_width_mm"] - face["label_insert_width_mm"], 1.2)
    assert np.isclose(face["label_pocket_height_mm"] - face["label_insert_height_mm"], 1.2)


def test_key_interface_clearances_are_explicit():
    face = PARAMS["face"]
    clip = PARAMS["clip"]
    assert np.isclose(face["key_entry_height_mm"] - clip["key_head_height_mm"], 0.4)
    assert np.isclose(face["key_track_height_mm"] - clip["key_neck_height_mm"], 0.4)
    assert np.isclose(face["key_entry_width_mm"] - clip["body_width_mm"], 0.6)
    assert np.isclose(clip["key_stem_length_mm"] - face["plate_thickness_mm"], 0.3)


def test_all_parts_fit_portfolio_envelope():
    build = load_build()
    interfaces = [build.make_face(PARAMS)[1], build.make_gap_gauge(PARAMS)[1], build.make_key_coupon(PARAMS)[1]]
    interfaces.extend(build.make_clip(PARAMS, item)[1] for item in PARAMS["clip_presets"])
    for item in interfaces:
        dims = item["outer_dimensions_mm"]
        assert max(dims) <= 180.0
        assert sorted(dims)[-2] <= 55.0


def test_support_conscious_orientations_are_declared():
    build = load_build()
    interfaces = [build.make_face(PARAMS)[1], build.make_gap_gauge(PARAMS)[1], build.make_key_coupon(PARAMS)[1]]
    interfaces.extend(build.make_clip(PARAMS, item)[1] for item in PARAMS["clip_presets"])
    assert all(item["print_orientation"] in {"broad_back_face_down", "broad_profile_face_down", "broad_face_down"} for item in interfaces)


def test_candidate_volume_reduction_passes():
    result = json.loads((ROOT / "reports/optimization-comparison.json").read_text())
    assert result["status"] == "PASS"
    assert result["volume_reduction_percent"] >= 35.0


def test_layer_relations_are_integral():
    layer = PARAMS["printer"]["layer_height_mm"]
    assert PARAMS["face"]["plate_thickness_mm"] / layer == 15
    assert PARAMS["clip"]["bridge_height_mm"] / layer == 15
    assert PARAMS["coupons"]["gap_gauge_thickness_mm"] / layer == 15


def test_claim_boundaries_and_physical_targets_are_explicit():
    contract = PARAMS["workflow_contract"]
    assert contract["claim"] == "light_horizontal_slide_pull_only_no_lifting_or_load_rating"
    assert contract["contents_mass_test_target_kg"] == 0.75
    assert contract["pull_cycle_target"] == 500
