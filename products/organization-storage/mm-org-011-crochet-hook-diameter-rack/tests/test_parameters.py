from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hook_rack_build", ROOT / "cad/build.py")
BUILD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILD)


def parameters() -> dict:
    return json.loads((ROOT / "config/model-parameters.json").read_text(encoding="utf-8"))


def test_default_parameters_pass() -> None:
    BUILD.validate_parameters(parameters())


def test_default_envelope_matches_contract() -> None:
    assert BUILD.rack_dimensions(parameters()) == (204.0, 112.0, 104.0)


def test_fifteen_profiles_map_to_three_by_five() -> None:
    p = parameters()
    assert len(p["hook_profiles"]) == p["rack"]["rows"] * p["rack"]["columns"] == 15


def test_every_slot_has_positive_shaft_clearance() -> None:
    p = parameters()
    assert all(item["shaft_diameter"] + p["rack"]["slot_clearance"] > item["shaft_diameter"] for item in p["hook_profiles"])


def test_every_handle_has_lateral_spacing() -> None:
    p = parameters()
    assert all(p["rack"]["column_pitch"] - item["handle_major"] >= p["rack"]["minimum_handle_spacing"] for item in p["hook_profiles"])


def test_oversized_handle_fails_closed() -> None:
    p = copy.deepcopy(parameters())
    p["hook_profiles"][0]["handle_major"] = 40.0
    with pytest.raises(AssertionError):
        BUILD.validate_parameters(p)


def test_measurement_card_covers_all_default_shafts() -> None:
    p = parameters()
    assert set(p["measurement_card"]["shaft_notches"]) == {item["shaft_diameter"] for item in p["hook_profiles"]}


def test_default_geometry_is_valid_single_solid_per_part() -> None:
    rack, profile_metrics = BUILD.make_rack(parameters())
    card, card_metrics = BUILD.make_measurement_card(parameters())
    assert rack.isValid() and len(rack.Solids()) == 1
    assert card.isValid() and len(card.Solids()) == 1
    assert len(profile_metrics) == 15
    assert len(card_metrics["notches"]) == 24
