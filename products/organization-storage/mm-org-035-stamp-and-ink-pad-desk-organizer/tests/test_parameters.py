import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_identity():
    assert P["project"] == {"id": "MM-ORG-035", "revision": "0.1.0-draft.2", "units": "mm"}


def test_two_pilot_envelopes():
    assert P["modules"]["square"]["case_max_mm"] == [78.0, 78.0, 21.0]
    assert P["modules"]["rectangular"]["case_max_mm"] == [100.0, 69.0, 21.0]


def test_clearance_and_pitch():
    s = P["shared"]
    case_h = max(module["case_max_mm"][2] for module in P["modules"].values())
    assert s["side_clearance_each_mm"] >= 1.5
    assert s["lane_pitch_mm"] - s["shelf_thickness_mm"] - case_h >= 3.0


def test_three_line_support_and_sections():
    s = P["shared"]
    assert s["support_beam_width_mm"] >= 6.0
    assert s["shelf_thickness_mm"] >= 2.4
    assert s["side_rail_thickness_mm"] >= 3.0


def test_front_openings_are_useful():
    assert P["modules"]["square"]["center_opening_mm"] >= 42
    assert P["modules"]["rectangular"]["center_opening_mm"] >= 56
    assert 0.8 <= P["shared"]["front_sill_height_mm"] <= 1.2


def test_coupon_is_smaller_than_cases():
    assert P["coupon"]["depth_mm"] < min(module["case_max_mm"][1] for module in P["modules"].values())


def test_side_print_continuity_revision_is_warning_free():
    initial = json.loads((ROOT / "validation/slicer-anycubic-petg-full-run-001.json").read_text())
    revised = json.loads((ROOT / "validation/slicer-anycubic-petg-full-run-002.json").read_text())
    initial_warnings = [plate["warning_message"] for plate in initial["native_result"]["sliced_plates"] if plate["warning_message"]]
    revised_warnings = [plate["warning_message"] for plate in revised["native_result"]["sliced_plates"] if plate["warning_message"]]
    assert any("floating regions" in warning for warning in initial_warnings)
    assert revised_warnings == []
    assert P["shared"]["front_sill_height_mm"] == 1.2
