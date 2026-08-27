import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_twenty_independent_item_classes_fill_grid():
    cassette = PARAMS["cassette"]
    items = PARAMS["item_classes"]
    assert len(items) == 20
    assert cassette["columns"] * cassette["rows"] == len(items)
    assert len({item["id"] for item in items}) == len(items)


def test_default_envelope_matches_pitch_contract():
    cassette = PARAMS["cassette"]
    assert 2 * cassette["margin_mm"] + cassette["columns"] * cassette["cell_pitch_x_mm"] == cassette["width_mm"]
    assert 2 * cassette["margin_mm"] + cassette["rows"] * cassette["cell_pitch_y_mm"] == cassette["depth_mm"]
    assert cassette["width_mm"] <= 220 and cassette["depth_mm"] <= 160


def test_every_class_owns_clearance_parameters():
    for item in PARAMS["item_classes"]:
        assert item["side_clearance_mm"] > 0
        assert item["end_clearance_mm"] > 0


def test_cradle_widths_fit_their_cells():
    cassette = PARAMS["cassette"]
    for item in PARAMS["item_classes"]:
        outside_width = item["body_width_mm"] + 2 * item["side_clearance_mm"] + 2 * cassette["cradle_wall_mm"]
        assert outside_width <= cassette["cell_pitch_y_mm"] - 2.0


def test_body_and_connector_reach_fit_cell_length():
    cassette = PARAMS["cassette"]
    interface = PARAMS["interfaces"]
    available = cassette["cell_pitch_x_mm"] - cassette["back_inset_mm"] - 2.0
    for item in PARAMS["item_classes"]:
        occupied = item["body_length_mm"] + cassette["rear_body_clearance_mm"] + item["connector_reach_mm"] + interface["connector_relief_extra_length_mm"]
        assert occupied <= available


def test_connector_keepout_is_narrower_than_body_cradle():
    interface = PARAMS["interfaces"]
    for item in PARAMS["item_classes"]:
        keepout_width = item["connector_width_mm"] + 2 * interface["connector_clearance_each_side_mm"]
        cradle_width = item["body_width_mm"] + 2 * item["side_clearance_mm"]
        assert keepout_width <= cradle_width


def test_cradle_heights_keep_items_visible_and_located():
    cassette = PARAMS["cassette"]
    for item in PARAMS["item_classes"]:
        height = min(
            cassette["cradle_height_above_base_mm"],
            max(cassette["cradle_min_height_above_base_mm"], item["body_height_mm"] * cassette["cradle_height_body_fraction"]),
        )
        assert cassette["cradle_min_height_above_base_mm"] <= height <= cassette["cradle_height_above_base_mm"]
        assert height < item["body_height_mm"]


def test_minimum_printable_sections():
    cassette = PARAMS["cassette"]
    assert cassette["base_height_mm"] >= 2.0
    assert cassette["outer_wall_mm"] >= 2.0
    assert cassette["cradle_wall_mm"] >= 1.2
    assert cassette["label_recess_depth_mm"] < cassette["base_height_mm"]


def test_measurement_card_width_notches_fit():
    card = PARAMS["measurement_card"]
    used = sum(card["width_notches_mm"]) + (len(card["width_notches_mm"]) - 1) * card["notch_gap_mm"]
    assert used + 2 * card["edge_margin_mm"] <= card["width_mm"]
    assert card["width_notches_mm"] == sorted(card["width_notches_mm"])


def test_measurement_card_thickness_notches_fit():
    card = PARAMS["measurement_card"]
    used = sum(card["thickness_notches_mm"]) + (len(card["thickness_notches_mm"]) - 1) * card["notch_gap_mm"]
    assert used + 2 * card["edge_margin_mm"] <= card["depth_mm"]
    assert card["thickness_notches_mm"] == sorted(card["thickness_notches_mm"])


def test_measurement_card_and_cassette_fit_printer():
    card = PARAMS["measurement_card"]
    cassette = PARAMS["cassette"]
    bed = PARAMS["printer"]["build_volume_mm"]
    assert cassette["width_mm"] <= bed[0] and cassette["depth_mm"] <= bed[1]
    assert card["width_mm"] <= bed[0] and card["depth_mm"] <= bed[1]
    assert cassette["width_mm"] + card["width_mm"] + 30.0 <= bed[0]


def test_ruler_pitch_is_integral():
    card = PARAMS["measurement_card"]
    assert card["ruler_length_mm"] % card["tick_pitch_mm"] == 0


def test_position_code_boolean_budget():
    """Twenty positions use at most two analytic recesses each, not glyph segments."""
    positions = range(1, len(PARAMS["item_classes"]) + 1)
    nonzero_tens = sum(1 for position in positions if position // 10)
    nonzero_units = sum(1 for position in positions if position % 10)
    assert nonzero_tens + nonzero_units == 29
    assert nonzero_tens + nonzero_units <= 2 * len(PARAMS["item_classes"])
