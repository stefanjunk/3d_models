import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_018_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_radius_series_and_identity_are_monotonic():
    tile = PARAMS["radius_tiles"]
    assert tile["radii_mm"] == [2.0, 4.0, 6.0, 8.0, 10.0, 12.0]
    assert all(b > a for a, b in zip(tile["radii_mm"], tile["radii_mm"][1:]))


def test_radius_tiles_generate_valid_single_solids_with_exact_arc_endpoints():
    build = load_build()
    for count, radius in enumerate(PARAMS["radius_tiles"]["radii_mm"], 1):
        shape, interface = build.make_radius_tile(PARAMS, radius, count)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert interface["radius_mm"] == radius
        assert interface["analytic_arc_start_mm"] == [0.0, radius]
        assert interface["analytic_arc_end_mm"] == [radius, 0.0]
        assert interface["identity_holes"] == count


def test_larger_radius_tiles_remove_more_corner_material_and_selection_uses_smallest_fit():
    build = load_build()
    volumes = [build.make_radius_tile(PARAMS, radius, count)[0].Volume() for count, radius in enumerate(PARAMS["radius_tiles"]["radii_mm"], 1)]
    assert all(b < a for a, b in zip(volumes, volumes[1:]))
    assert PARAMS["measurement_contract"]["radius_selection_rule"] == "smallest_no_force_seating_tile"


def test_height_cards_have_three_exact_ledge_levels_and_two_instances():
    card = PARAMS["height_cards"]
    assert card["reference_heights_mm"] == [15.0, 35.0, 55.0]
    assert card["quantity"] == 2
    assert all(b - a == 20.0 for a, b in zip(card["reference_heights_mm"], card["reference_heights_mm"][1:]))


def test_height_card_is_one_valid_solid():
    shape, interface = load_build().make_height_card(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["floor_datum_y_mm"] == 0.0


def test_clearance_comb_is_monotonic_and_not_sub_two_nozzle_widths():
    widths = PARAMS["clearance_comb"]["finger_widths_mm"]
    nozzle = PARAMS["printer"]["nozzle_diameter_mm"]
    assert widths == [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    assert min(widths) >= 2 * nozzle
    assert all(abs((b - a) - 0.2) < 1e-9 for a, b in zip(widths, widths[1:]))


def test_clearance_comb_is_one_valid_solid():
    shape, _ = load_build().make_clearance_comb(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1


def test_calibration_frame_exposes_external_and_internal_references():
    shape, interface = load_build().make_calibration_frame(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["external_references_mm"] == [130.0, 32.0, 3.0]
    assert interface["internal_window_mm"] == [80.0, 12.0]
    assert interface["round_reference_diameter_mm"] == 10.0
    assert interface["square_reference_mm"] == 10.0


def test_all_parts_share_fifteen_layer_thickness():
    values = [PARAMS["radius_tiles"]["thickness_mm"], PARAMS["height_cards"]["thickness_mm"], PARAMS["clearance_comb"]["thickness_mm"], PARAMS["calibration_frame"]["thickness_mm"]]
    assert values == [3.0, 3.0, 3.0, 3.0]
    assert values[0] / PARAMS["printer"]["layer_height_mm"] == 15


def test_every_single_part_fits_portfolio_envelope():
    assert PARAMS["calibration_frame"]["width_mm"] <= 180.0
    assert PARAMS["height_cards"]["height_mm"] <= 90.0
    assert PARAMS["calibration_frame"]["thickness_mm"] <= 12.0


def test_physical_accuracy_gate_requires_ten_drawers_and_calipers():
    contract = PARAMS["measurement_contract"]
    assert contract["minimum_real_drawers_for_validation"] == 10
    assert contract["maximum_allowed_mean_user_error_mm"] == 1.0
    assert contract["required_drawer_positions"] == ["front", "middle", "rear"]
    assert contract["radius_selection_rule"] == "smallest_no_force_seating_tile"


def test_no_generated_part_uses_external_assets():
    build = load_build()
    interfaces = []
    for count, radius in enumerate(PARAMS["radius_tiles"]["radii_mm"], 1):
        interfaces.append(build.make_radius_tile(PARAMS, radius, count)[1])
    interfaces.extend([build.make_height_card(PARAMS)[1], build.make_clearance_comb(PARAMS)[1], build.make_calibration_frame(PARAMS)[1]])
    assert all(item["external_assets"] == [] for item in interfaces)
