import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_019_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_presets_are_unbranded_and_measurement_driven():
    assert [item["id"] for item in PARAMS["presets"]] == ["compact-six", "extended-five"]
    assert PARAMS["workflow_contract"]["compatibility_claim"] == "none_until_physical_fit_test"
    assert PARAMS["workflow_contract"]["input_dimensions"] == ["envelope_depth", "envelope_thickness", "envelope_height", "slot_count", "slot_clearance"]


def test_slot_width_is_measured_thickness_plus_two_sided_clearance():
    build = load_build()
    for preset in PARAMS["presets"]:
        dims = build.rack_dimensions(PARAMS, preset)
        expected = preset["measured_envelope_thickness_mm"] + 2.0 * preset["slot_clearance_mm"]
        assert dims["clear_width_mm"] == expected


def test_slot_depth_is_measured_depth_plus_one_rear_clearance():
    build = load_build()
    for preset in PARAMS["presets"]:
        dims = build.rack_dimensions(PARAMS, preset)
        assert dims["clear_depth_mm"] == preset["measured_envelope_depth_mm"] + PARAMS["rack"]["depth_clearance_mm"]


def test_both_racks_are_valid_single_solids():
    build = load_build()
    for preset in PARAMS["presets"]:
        shape, interface = build.make_rack(PARAMS, preset)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert interface["slot_count"] == preset["slot_count"]
        assert interface["label_fields"] == preset["slot_count"]
        assert interface["status_dot_pairs"] == preset["slot_count"]


def test_rear_rest_angle_is_bounded_and_exact():
    angle = PARAMS["rack"]["lean_angle_deg"]
    assert 5.0 <= angle <= 12.0
    shift = math.tan(math.radians(angle)) * PARAMS["rack"]["retaining_height_mm"]
    assert math.isclose(shift, 4.4973067104765265, rel_tol=0.0, abs_tol=1e-9)


def test_wall_and_recess_skin_are_printable():
    rack = PARAMS["rack"]
    assert rack["divider_thickness_mm"] / PARAMS["printer"]["line_width_mm"] >= 4.0
    remaining = rack["front_wall_thickness_mm"] - rack["label_recess_depth_mm"] - rack["status_dot_depth_mm"]
    assert remaining >= 1.0


def test_clearance_coupon_brackets_default_fit():
    coupon = PARAMS["coupon"]
    assert coupon["clearances_mm"] == [0.3, 0.5, 0.7]
    assert coupon["clearances_mm"][1] == PARAMS["presets"][0]["slot_clearance_mm"]
    shape, interface = load_build().make_clearance_coupon(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["bay_clear_widths_mm"] == [18.6, 19.0, 19.4]


def test_planar_joint_shares_base_height_and_two_centers():
    assert PARAMS["connector"]["height_mm"] == PARAMS["rack"]["base_thickness_mm"]
    assert PARAMS["connector"]["default_clearance_mm"] == 0.25
    assert PARAMS["connector"]["centers_y_mm"] == [25.0, 55.0]
    build = load_build()
    interfaces = [build.make_rack(PARAMS, preset)[1] for preset in PARAMS["presets"]]
    assert interfaces[0]["joint_centers_y_mm"] == interfaces[1]["joint_centers_y_mm"]


def test_every_rack_fits_portfolio_envelope():
    build = load_build()
    for preset in PARAMS["presets"]:
        dims = build.rack_dimensions(PARAMS, preset)
        assert dims["width_mm"] + PARAMS["connector"]["tab_depth_mm"] <= 220.0
        assert dims["depth_mm"] <= 140.0
        assert PARAMS["rack"]["retaining_height_mm"] <= 120.0


def test_base_and_connector_use_whole_reference_layers():
    layer = PARAMS["printer"]["layer_height_mm"]
    assert PARAMS["rack"]["base_thickness_mm"] / layer == 15
    assert PARAMS["connector"]["height_mm"] / layer == 15


def test_physical_retrieval_gate_is_explicitly_deferred():
    contract = PARAMS["workflow_contract"]
    assert contract["physical_retrieval_cycles"] == 100
    assert contract["minimum_empty_cartridges_per_preset"] == 3
    assert contract["supported_use_modes"] == ["desk", "drawer", "shelf"]


def test_no_generated_part_uses_external_assets():
    build = load_build()
    interfaces = [build.make_rack(PARAMS, preset)[1] for preset in PARAMS["presets"]]
    interfaces.append(build.make_clearance_coupon(PARAMS)[1])
    assert all(item["external_assets"] == [] for item in interfaces)
