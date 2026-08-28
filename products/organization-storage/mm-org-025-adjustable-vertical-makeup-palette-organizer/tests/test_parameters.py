import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_sixteen_position_grid_is_centered_and_exact():
    build = load_module(ROOT / "cad/build.py", "mm_org_025_build")
    positions = build.slot_positions(PARAMS)
    assert len(positions) == 16
    assert np.isclose(positions[0], -positions[-1])
    assert np.allclose(np.diff(positions), [11.5] * 15)


def test_base_is_one_valid_solid():
    build = load_module(ROOT / "cad/build.py", "mm_org_025_base")
    shape, interface = build.make_base(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert np.allclose(interface["outer_dimensions_mm"], [190.0, 106.0, 10.0])


def test_divider_is_one_valid_windowed_solid():
    build = load_module(ROOT / "cad/build.py", "mm_org_025_divider")
    shape, interface = build.make_divider(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["tongue_thickness_mm"] == 2.4
    assert shape.Volume() < np.prod(interface["outer_dimensions_mm"]) * 0.65


def test_coupon_pair_reproduces_protected_tongue():
    build = load_module(ROOT / "cad/build.py", "mm_org_025_coupons")
    gauge_shape, gauge = build.make_slot_gauge(PARAMS)
    key_shape, key = build.make_fit_key(PARAMS)
    _, divider = build.make_divider(PARAMS)
    assert gauge_shape.isValid() and key_shape.isValid()
    assert gauge["candidate_slot_widths_mm"] == [2.7, 2.9, 3.1]
    assert key["tongue_thickness_mm"] == divider["tongue_thickness_mm"]
    assert key["tongue_length_mm"] == divider["tongue_length_mm"]


def test_default_layout_has_seven_dividers_and_six_compartments():
    build = load_module(ROOT / "cad/build.py", "mm_org_025_layout")
    assert PARAMS["divider"]["default_slot_indices"] == [0, 2, 4, 6, 8, 11, 15]
    assert np.allclose(build.compartment_clearances(PARAMS), [20.6, 20.6, 20.6, 20.6, 32.1, 43.6])


def test_supported_thicknesses_keep_one_mm_retrieval_clearance():
    build = load_module(ROOT / "cad/build.py", "mm_org_025_thickness")
    clears = np.array(build.compartment_clearances(PARAMS))
    supported = np.array(PARAMS["workflow_contract"]["default_supported_palette_thicknesses_mm"])
    assert np.allclose(clears - supported, 1.0)


def test_slot_clearances_are_explicit():
    assert np.isclose(PARAMS["base"]["slot_width_mm"] - PARAMS["divider"]["thickness_mm"], 0.5)
    assert np.isclose(PARAMS["base"]["slot_length_mm"] - PARAMS["divider"]["foot_length_mm"], 0.6)


def test_researched_portfolio_envelope_is_respected():
    assert PARAMS["base"]["width_mm"] <= 225.0
    assert PARAMS["base"]["depth_mm"] <= 110.0
    assert PARAMS["base"]["rail_height_mm"] + PARAMS["divider"]["panel_height_mm"] <= 135.0


def test_layer_relations_are_integral():
    layer = PARAMS["printer"]["layer_height_mm"]
    assert np.isclose(PARAMS["base"]["rail_height_mm"] / layer, 50)
    assert np.isclose(PARAMS["divider"]["thickness_mm"] / layer, 12)
    assert np.isclose(PARAMS["coupon"]["gauge_height_mm"] / layer, 50)


def test_photo_capture_happy_path():
    capture = load_module(ROOT / "tools/photo_dimension_capture.py", "mm_org_025_capture")
    data = json.loads((ROOT / "assets/photo-capture-example.json").read_text())
    result = capture.capture_dimensions(data)
    assert result["status"] == "PASS"
    assert result["closed_face_width_mm"] == 130.0
    assert result["closed_face_height_mm"] == 71.0
    assert result["closed_thickness_mm"] == 15.2
    assert result["recommended_minimum_compartment_clear_mm"] == 16.2


def test_photo_capture_fails_closed_on_perspective():
    capture = load_module(ROOT / "tools/photo_dimension_capture.py", "mm_org_025_capture_fail")
    data = json.loads((ROOT / "assets/photo-capture-example.json").read_text())
    data["palette"]["corners_px"][2][0] = 1400.0
    result = capture.capture_dimensions(data)
    assert result["status"] == "FAIL"


def test_photo_capture_rejects_zero_reference():
    capture = load_module(ROOT / "tools/photo_dimension_capture.py", "mm_org_025_capture_zero")
    data = json.loads((ROOT / "assets/photo-capture-example.json").read_text())
    data["reference"]["edge_b_px"] = data["reference"]["edge_a_px"]
    with pytest.raises(ValueError):
        capture.capture_dimensions(data)


def test_dry_storage_claim_boundary_is_explicit():
    assert PARAMS["workflow_contract"]["claim"] == "dry_countertop_storage_only_no_universal_fit_or_hygiene_claim"
    assert PARAMS["workflow_contract"]["thermal_boundary"] == "keep_away_from_high_heat_hair_tools"


def test_all_generated_parts_declare_support_conscious_orientation():
    build = load_module(ROOT / "cad/build.py", "mm_org_025_orientation")
    interfaces = [
        build.make_base(PARAMS)[1],
        build.make_divider(PARAMS)[1],
        build.make_slot_gauge(PARAMS)[1],
        build.make_fit_key(PARAMS)[1],
    ]
    assert all(item["print_orientation"] in {"rails_on_bed", "broad_face_down"} for item in interfaces)


def test_candidate_volume_reduction_passes():
    result = json.loads((ROOT / "reports/optimization-comparison.json").read_text())
    assert result["status"] == "PASS"
    assert result["volume_reduction_percent"] >= 35.0
