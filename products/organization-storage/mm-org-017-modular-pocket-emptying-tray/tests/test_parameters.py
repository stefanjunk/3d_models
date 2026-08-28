import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_017_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_three_distinct_visual_styles_share_one_family():
    styles = PARAMS["styles"]
    assert len(styles) == 3
    assert {item["kind"] for item in styles} == {"rounded", "faceted", "ribbed"}


def test_connected_set_fits_portfolio_envelope():
    module = PARAMS["module"]
    connector = PARAMS["connector"]
    assert 3 * module["base_width_mm"] + connector["tab_depth_mm"] <= 180.0
    assert module["base_depth_mm"] <= 160.0
    assert module["wall_height_mm"] <= 45.0


def test_coin_floor_slopes_to_front_with_bounded_angle():
    module = PARAMS["module"]
    scoop = PARAMS["coin_scoop"]
    run = module["base_depth_mm"] - 2 * (module["bowl_inset_mm"] + module["wall_thickness_mm"])
    angle = math.degrees(math.atan((scoop["rear_floor_z_mm"] - scoop["front_floor_z_mm"]) / run))
    assert scoop["rear_floor_z_mm"] > scoop["front_floor_z_mm"]
    assert scoop["minimum_slope_deg"] <= angle <= scoop["maximum_slope_deg"]


def test_front_lip_is_sweep_over_not_retaining_wall():
    scoop = PARAMS["coin_scoop"]
    assert 0.0 < scoop["front_lip_top_z_mm"] - scoop["front_floor_z_mm"] <= 0.8
    assert scoop["opening_width_mm"] >= 30.0
    assert scoop["opening_corner_radius_mm"] >= 4.0


def test_base_and_walls_meet_reference_process_minima():
    module = PARAMS["module"]
    printer = PARAMS["printer"]
    assert module["base_thickness_mm"] / printer["layer_height_mm"] >= 8
    assert module["wall_thickness_mm"] / printer["line_width_mm"] >= 4


def test_connector_coupon_brackets_default_clearance():
    connector = PARAMS["connector"]
    assert connector["coupon_clearances_mm"] == [0.15, 0.25, 0.35]
    assert connector["default_clearance_mm"] == connector["coupon_clearances_mm"][1]


def test_connector_is_printed_in_base_plane():
    assert PARAMS["connector"]["height_mm"] == PARAMS["module"]["base_thickness_mm"]


def test_complete_build_set_fits_reference_bed():
    module = PARAMS["module"]
    coupon = PARAMS["coupon"]
    bed = PARAMS["printer"]["build_volume_mm"]
    assert 3 * 70.0 + 20.0 <= bed[0]
    assert module["base_depth_mm"] + coupon["gauge_depth_mm"] + 35.0 <= bed[1]


def test_all_parametric_parts_are_valid_single_solids():
    build = load_build()
    for style in PARAMS["styles"]:
        shape, _ = build.make_module(PARAMS, style)
        assert shape.isValid(), style["id"]
        assert len(shape.Solids()) == 1, style["id"]
    for maker in (build.make_gauge, build.make_test_key):
        shape, _ = maker(PARAMS)
        assert shape.isValid()
        assert len(shape.Solids()) == 1


def test_connector_gauge_socket_spacing_does_not_create_edge_islands():
    build = load_build()
    gauge, interface = build.make_gauge(PARAMS)
    assert gauge.isValid()
    assert len(gauge.Solids()) == 1
    assert PARAMS["coupon"]["socket_centers_y_mm"] == [7.0, 21.0, 35.0]
    assert interface["clearances_mm"] == [0.15, 0.25, 0.35]


def test_styles_use_no_external_geometry_assets():
    build = load_build()
    for style in PARAMS["styles"]:
        _, interface = build.make_module(PARAMS, style)
        assert interface["external_assets"] == []
