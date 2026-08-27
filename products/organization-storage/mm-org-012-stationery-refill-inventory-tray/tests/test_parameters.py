from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("refill_tray_build", ROOT / "cad/build.py")
BUILD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILD)


def parameters() -> dict:
    return json.loads((ROOT / "config/model-parameters.json").read_text(encoding="utf-8"))


def test_default_parameters_pass() -> None:
    BUILD.validate_parameters(parameters())


def test_lane_and_pocket_widths_close_exactly() -> None:
    p = parameters(); wall = p["tray"]["wall_thickness"]
    rear = sum(item["clear_width"] for item in p["rear_packet_lanes"]) + (len(p["rear_packet_lanes"]) + 1) * wall
    front = sum(item["clear_width"] for item in p["front_pockets"]) + (len(p["front_pockets"]) + 1) * wall
    assert rear == front == p["tray"]["width"]


def test_all_package_envelopes_have_declared_clearance() -> None:
    p = parameters(); tray = p["tray"]; clearance = tray["package_clearance"]
    rear_depth = tray["depth"] - tray["front_region_depth"] - 2 * tray["wall_thickness"]
    assert all(item["clear_width"] - item["package_width"] >= clearance and rear_depth - item["package_length"] >= clearance for item in p["rear_packet_lanes"])
    front_depth = tray["front_region_depth"] - 2 * tray["wall_thickness"]
    assert all(item["clear_width"] - item["package_width"] >= clearance and front_depth - item["package_depth"] >= clearance for item in p["front_pockets"])


def test_oversized_package_fails_closed() -> None:
    p = copy.deepcopy(parameters()); p["rear_packet_lanes"][0]["package_width"] = 25.0
    with pytest.raises(AssertionError): BUILD.validate_parameters(p)


def test_labels_use_embedded_glyphs() -> None:
    p = parameters()
    assert all(set(item["label"]).issubset(BUILD.GLYPHS) for item in p["rear_packet_lanes"] + p["front_pockets"])


def test_label_pixels_meet_minimum() -> None:
    p = parameters(); tray = p["tray"]
    assert tray["label_pixel_pitch"] * tray["label_pixel_fill"] >= p["limits"]["minimum_label_pixel"]


def test_coupon_reuses_production_wall() -> None:
    p = parameters(); coupon, metrics = BUILD.make_retrieval_coupon(p)
    assert coupon.isValid() and len(coupon.Solids()) == 1
    assert metrics["production_wall_mm"] == p["tray"]["wall_thickness"]


def test_default_tray_is_valid_single_solid() -> None:
    tray, metrics = BUILD.make_tray(parameters())
    assert tray.isValid() and len(tray.Solids()) == 1
    assert len(metrics["rear_lanes"]) == 5
    assert len(metrics["front_pockets"]) == 3
