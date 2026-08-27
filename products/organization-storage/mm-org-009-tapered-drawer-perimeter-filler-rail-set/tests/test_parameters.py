import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mm_org_009_build", ROOT / "cad/build.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def parameters():
    return json.loads((ROOT / "config/model-parameters.json").read_text(encoding="utf-8"))


def test_default_contract():
    BUILD.validate_parameters(parameters())


def test_default_effective_widths():
    value = parameters()
    assert BUILD.rail_widths(value, "left") == (9.9, 20.9)
    assert BUILD.rail_widths(value, "right") == (16.9, 7.9)


def test_rib_pitch_is_bounded():
    value = parameters()["rail"]
    positions, pitch = BUILD.rib_layout(value["length"], value["end_wall"], value["max_rib_pitch"])
    assert positions
    assert pitch <= value["max_rib_pitch"]
    assert pitch - value["rib_thickness"] <= 12.0


def test_rejects_gap_that_erases_scallop_wall_reserve():
    value = parameters()
    value["rail"]["right_rear_gap"] = 8.0
    try:
        BUILD.validate_parameters(value)
    except AssertionError:
        return
    raise AssertionError("invalid narrow gap was accepted")


def test_boundary_geometry_is_valid():
    value = parameters()
    value["rail"]["length"] = 80.0
    value["rail"]["scallop_end_offset"] = 20.0
    value["rail"]["left_front_gap"] = 9.0
    value["rail"]["left_rear_gap"] = 45.0
    value["rail"]["right_front_gap"] = 45.0
    value["rail"]["right_rear_gap"] = 9.0
    BUILD.validate_parameters(value)
    for side in ("left", "right"):
        shape = BUILD.make_rail(value, side)
        assert shape.isValid()
        assert len(shape.Solids()) == 1


def test_source_does_not_mutate_input():
    value = parameters()
    original = copy.deepcopy(value)
    BUILD.make_rail(value, "left")
    assert value == original
