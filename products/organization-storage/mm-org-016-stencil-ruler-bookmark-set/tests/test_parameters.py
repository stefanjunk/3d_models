import json
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_three_distinct_production_styles():
    styles = PARAMS["styles"]
    assert len(styles) == 3
    assert {style["id"] for style in styles} == {"layout-5mm", "layout-4mm", "signal-12"}


def test_bookmark_envelope_is_a5_a6_portable():
    plate = PARAMS["plate"]
    assert plate["length_mm"] <= 142.0
    assert plate["width_mm"] <= 40.0
    assert plate["height_mm"] == 4 * PARAMS["printer"]["layer_height_mm"]


def test_production_features_meet_minimum_contract():
    plate = PARAMS["plate"]
    minimum = PARAMS["minimum_features"]
    assert plate["registration_hole_diameter_mm"] >= minimum["production_opening_mm"]
    assert plate["rule_slot_width_mm"] >= minimum["production_opening_mm"]
    assert plate["paper_boundary_mm"] >= minimum["paper_edge_boundary_mm"]


def test_registration_holes_retain_edge_boundary():
    plate = PARAMS["plate"]
    radius = plate["registration_hole_diameter_mm"] / 2.0
    assert plate["registration_x_mm"] - radius >= plate["paper_boundary_mm"]


def test_grid_runs_are_integral():
    plate = PARAMS["plate"]
    for style in PARAMS["styles"][:2]:
        assert plate["registration_length_mm"] % style["grid_pitch_mm"] == 0


def test_layout_slots_retain_declared_ligaments():
    width = PARAMS["plate"]["rule_slot_width_mm"]
    minimum = PARAMS["minimum_features"]["production_ligament_mm"]
    for style in PARAMS["styles"][:2]:
        ys = style["horizontal_slot_y_mm"]
        assert min(b - a - width for a, b in zip(ys, ys[1:])) >= minimum


def test_layout_box_series_matches_native_grid():
    for style in PARAMS["styles"][:2]:
        pitch = style["grid_pitch_mm"]
        assert style["box_widths_mm"] == [pitch * value for value in (1, 2, 3, 4)]


def test_signal_set_is_original_project_geometry_only():
    signal = PARAMS["styles"][2]
    assert len(signal["icon_names"]) == 12
    assert len(set(signal["icon_names"])) == 12
    assert all(name.isascii() and name.islower() for name in signal["icon_names"])


def test_identity_codes_are_unique():
    assert [style["identity_holes"] for style in PARAMS["styles"]] == [1, 2, 3]


def test_coupon_sweeps_below_and_above_production_minimum():
    sizes = PARAMS["coupon"]["feature_sizes_mm"]
    minimum = PARAMS["minimum_features"]["production_opening_mm"]
    assert min(sizes) == PARAMS["minimum_features"]["coupon_only_minimum_mm"]
    assert min(sizes) < minimum <= max(sizes)
    assert sizes == sorted(sizes)


def test_all_parts_fit_reference_bed_together():
    plate = PARAMS["plate"]
    coupon = PARAMS["coupon"]
    bed = PARAMS["printer"]["build_volume_mm"]
    assert 3 * plate["width_mm"] + coupon["width_mm"] + 50.0 <= bed[0]
    assert max(plate["length_mm"], coupon["depth_mm"]) + 20.0 <= bed[1]


def test_all_twelve_signal_profiles_are_valid_single_solids():
    spec = importlib.util.spec_from_file_location("mm_org_016_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    height = PARAMS["plate"]["height_mm"]
    for name in PARAMS["styles"][2]["icon_names"]:
        cutter = build.signal_cutter(name, 0.0, 0.0, height)
        assert cutter.isValid(), name
        assert len(cutter.Solids()) == 1, name
