import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_021_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_presets_are_measurement_driven_and_brand_neutral():
    assert [item["id"] for item in PARAMS["presets"]] == ["slim-five", "mixed-four"]
    assert PARAMS["workflow_contract"]["input_dimensions"] == ["shelf_depth", "closed_case_length", "closed_case_depth", "closed_case_thickness", "case_count", "label_preference"]
    assert PARAMS["workflow_contract"]["optical_protection_claim"] == "none_storage_corral_only"


def test_each_lane_has_two_mm_example_allowance():
    for preset in PARAMS["presets"]:
        allowances = [clear - case for clear, case in zip(preset["lane_clear_widths_mm"], preset["intended_case_thickness_max_mm"])]
        assert allowances == [2.0] * len(allowances)


def test_both_corrals_are_valid_single_solids():
    build = load_build()
    for preset in PARAMS["presets"]:
        shape, interface = build.make_corral(PARAMS, preset)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert interface["label_fields"] == len(preset["lane_clear_widths_mm"])


def test_floor_rise_matches_three_degree_contract():
    build = load_build()
    expected = math.tan(math.radians(3.0)) * PARAMS["corral"]["base_depth_mm"]
    assert math.isclose(build.floor_rise(PARAMS), expected, rel_tol=0.0, abs_tol=1e-12)
    assert 4.0 < expected < 6.0


def test_retention_geometry_is_bounded():
    corral = PARAMS["corral"]
    assert corral["front_stop_height_above_floor_mm"] < corral["rear_wall_height_mm"] < corral["divider_height_mm"]
    assert corral["front_stop_depth_mm"] < corral["base_depth_mm"] / 4.0
    assert corral["rear_wall_depth_mm"] < corral["base_depth_mm"] / 4.0


def test_case_contact_radii_fit_three_mm_divider():
    corral = PARAMS["corral"]
    assert corral["divider_leading_radius_mm"] == 1.4
    assert corral["divider_top_radius_mm"] == 1.2
    assert 2.0 * corral["divider_leading_radius_mm"] < corral["divider_thickness_mm"]
    assert 2.0 * corral["divider_top_radius_mm"] < corral["divider_thickness_mm"]


def test_width_gauge_reproduces_mixed_lane_series():
    build = load_build()
    shape, interface = build.make_width_gauge(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["notch_widths_mm"] == PARAMS["presets"][1]["lane_clear_widths_mm"]
    assert interface["identity_holes"] == [1, 2, 3, 4]


def test_width_gauge_fits_portfolio_width():
    build = load_build()
    assert build.gauge_width(PARAMS) == 211.0
    assert build.gauge_width(PARAMS) <= 220.0


def test_every_corral_fits_portfolio_envelope():
    build = load_build()
    for preset in PARAMS["presets"]:
        dims = build.corral_dimensions(PARAMS, preset)
        assert dims["width_mm"] <= 220.0 and dims["depth_mm"] <= 160.0 and dims["height_mm"] <= 140.0


def test_base_uses_whole_reference_layers_and_printable_wall_count():
    layer = PARAMS["printer"]["layer_height_mm"]
    assert PARAMS["corral"]["base_rear_thickness_mm"] / layer == 15
    assert PARAMS["corral"]["divider_thickness_mm"] / PARAMS["printer"]["line_width_mm"] >= 6.0


def test_physical_case_gate_is_explicitly_deferred():
    contract = PARAMS["workflow_contract"]
    assert contract["required_case_classes"] == ["rigid_clamshell", "semi_rigid_or_eva", "soft_pouch"]
    assert contract["minimum_cases_per_preset"] == 3
    assert contract["retrieval_cycles"] == 100


def test_no_generated_part_uses_external_assets():
    build = load_build()
    interfaces = [build.make_corral(PARAMS, preset)[1] for preset in PARAMS["presets"]]
    interfaces.append(build.make_width_gauge(PARAMS)[1])
    assert all(item["external_assets"] == [] for item in interfaces)
