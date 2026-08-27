import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_total_positions_is_thirty():
    dock = PARAMS["dock"]
    assert len(dock["lane_centers_x_mm"]) * dock["positions_per_lane"] == 30


def test_footprint_and_height_fit_contract():
    dock = PARAMS["dock"]
    assert dock["width_mm"] <= 220
    assert dock["depth_mm"] <= 110
    assert dock["receiver_bar_height_mm"] <= 12


def test_all_lanes_keep_receiver_end_walls():
    dock = PARAMS["dock"]
    slot = PARAMS["slot"]
    assert dock["receiver_bar_length_mm"] - slot["length_mm"] >= 6.0
    half = dock["receiver_bar_length_mm"] / 2
    for center in dock["lane_centers_x_mm"]:
        assert center - half >= dock["perimeter_width_mm"]
        assert center + half <= dock["width_mm"] - dock["perimeter_width_mm"]


def test_lane_bar_clearance():
    dock = PARAMS["dock"]
    centers = dock["lane_centers_x_mm"]
    gap = min(b - a for a, b in zip(centers, centers[1:])) - dock["receiver_bar_length_mm"]
    assert gap >= 6.0


def test_slot_web_at_mouth():
    dock = PARAMS["dock"]
    slot = PARAMS["slot"]
    assert dock["slot_pitch_mm"] - slot["lip_width_mm"] >= 5.0


def test_slot_profile_is_monotonic_and_open():
    slot = PARAMS["slot"]
    assert 0 < slot["throat_width_mm"] < slot["mid_width_mm"] < slot["lip_width_mm"]
    assert slot["bottom_z_mm"] < slot["shoulder_z_mm"] < slot["chamfer_z_mm"] < slot["top_z_mm"]


def test_three_card_classes_seat_with_positive_engagement():
    slot = PARAMS["slot"]
    top = PARAMS["dock"]["receiver_bar_height_mm"]
    low_w, high_w = slot["throat_width_mm"], slot["mid_width_mm"]
    low_z, high_z = slot["bottom_z_mm"], slot["shoulder_z_mm"]
    for card in PARAMS["card_standards"]:
        effective_width = card["thickness_mm"] + 2 * card["side_clearance_mm"]
        assert effective_width <= high_w
        if effective_width <= low_w:
            seat_z = low_z
        else:
            seat_z = low_z + (effective_width - low_w) * (high_z - low_z) / (high_w - low_w)
        assert top - seat_z >= 4.0


def test_thin_card_throat_clearance():
    slot = PARAMS["slot"]
    thin = PARAMS["card_standards"][0]["thickness_mm"]
    assert (slot["throat_width_mm"] - thin) / 2 >= slot["minimum_side_clearance_mm"] - 1e-9


def test_positions_stay_inside_depth():
    dock = PARAMS["dock"]
    last = dock["first_position_y_mm"] + (dock["positions_per_lane"] - 1) * dock["slot_pitch_mm"]
    half_bar = dock["receiver_bar_depth_mm"] / 2
    assert dock["first_position_y_mm"] - half_bar >= dock["perimeter_width_mm"]
    assert last + half_bar <= dock["depth_mm"] - dock["perimeter_width_mm"]


def test_coupon_reuses_production_pitch_and_envelope():
    dock = PARAMS["dock"]
    coupon = PARAMS["coupon"]
    assert coupon["slot_pitch_mm"] == dock["slot_pitch_mm"]
    assert coupon["positions"] == 3
    last = coupon["first_position_y_mm"] + (coupon["positions"] - 1) * coupon["slot_pitch_mm"]
    assert last + dock["receiver_bar_depth_mm"] / 2 < coupon["depth_mm"]
