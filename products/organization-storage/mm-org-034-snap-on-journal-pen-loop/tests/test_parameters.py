import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_identity():
    assert P["project"] == {"id": "MM-ORG-034", "revision": "0.1.0-draft.2", "units": "mm"}


def test_cover_gap_variants_are_ordered_and_bounded():
    gaps = list(P["clip"]["gap_variants_mm"].values())
    assert gaps == sorted(gaps)
    assert gaps[0] >= 1.5 and gaps[-1] <= 3.6


def test_common_rail_has_snap_interference_and_clearance():
    rail = P["rail"]
    assert rail["socket_clearance_mm"] >= 0.3
    assert 0.5 <= rail["snap_interference_mm"] <= 1.2
    assert rail["head_height_mm"] > rail["neck_height_mm"]


def test_pen_range_contains_relaxed_bore():
    loop = P["loop"]
    low, high = loop["intended_pen_range_mm"]
    assert low <= loop["relaxed_inner_diameter_mm"] <= high
    assert loop["radial_wall_mm"] >= 1.8


def test_minimum_structural_sections():
    assert P["clip"]["tongue_thickness_mm"] >= 1.6
    assert P["all_tpu"]["tongue_thickness_mm"] >= 1.6


def test_gauge_brackets_working_range():
    values = P["gauge"]["diameters_mm"]
    assert values[0] == P["loop"]["intended_pen_range_mm"][0]
    assert values[-1] <= P["loop"]["intended_pen_range_mm"][1]
