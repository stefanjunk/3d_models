from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
from build import dock_datums, gauge_width, make_dock, make_key_comb, make_slot_gauge  # noqa: E402

P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_project_and_portfolio_envelope():
    assert P["project"]["id"] == "MM-ORG-031"
    dock = P["dock"]
    assert [dock["width_mm"], dock["depth_mm"], dock["height_mm"]] == [176.0, 108.0, 100.0]
    assert dock["width_mm"] <= 180 and dock["depth_mm"] <= 120 and dock["height_mm"] <= 180


def test_five_device_and_three_book_presets_are_retained():
    assert P["fit"]["device_case_thickness_presets_mm"] == [8, 10, 12, 14, 16]
    assert P["fit"]["book_thickness_presets_mm"] == [18, 30, 42]


def test_selected_slots_equal_nominal_plus_two_sided_clearance():
    datum = dock_datums(P)
    clearance = P["fit"]["clearance_per_side_mm"]
    assert math.isclose(datum["device_slot_mm"], P["fit"]["selected_device_case_thickness_mm"] + 2 * clearance)
    assert math.isclose(datum["book_slot_mm"], P["fit"]["selected_book_thickness_mm"] + 2 * clearance)
    assert datum["device_slot_mm"] == 13 and datum["book_slot_mm"] == 31


def test_dock_brep_is_one_valid_solid_and_support_free():
    shape, interface = make_dock(P)
    assert shape.val().isValid() and len(shape.solids().vals()) == 1
    assert interface["print_orientation"] == "base_down"
    assert interface["support_required"] is False


def test_connector_keepout_and_vertical_access_are_protected():
    _, interface = make_dock(P)
    assert interface["connector_keepout_width_mm"] == 40
    assert interface["connector_vertical_clearance_mm"] >= 10


def test_four_rails_overlap_minimum_centered_device():
    _, interface = make_dock(P)
    assert interface["rail_count"] == 4
    assert interface["minimum_device_contact_overlap_mm"] >= 40


def test_device_gauge_and_keys_reproduce_clearance_contract():
    gauge, gi = make_slot_gauge(P, "device")
    keys, ki = make_key_comb(P, "device")
    assert gauge.val().isValid() and keys.val().isValid()
    assert gi["slot_widths_mm"] == [value + 1 for value in ki["tongue_widths_mm"]]
    assert math.isclose(gi["outer_bounds_mm"][0], gauge_width(gi["slot_widths_mm"], P["coupon"]["wall_mm"]))


def test_book_gauge_and_keys_reproduce_clearance_contract():
    gauge, gi = make_slot_gauge(P, "book")
    keys, ki = make_key_comb(P, "book")
    assert gauge.val().isValid() and keys.val().isValid()
    assert gi["slot_widths_mm"] == [value + 1 for value in ki["tongue_widths_mm"]]


def test_selected_structure_and_light_variant_are_distinct():
    _, selected = make_dock(P)
    _, light = make_dock(P, light=True)
    assert selected["base_mm"] == selected["wall_mm"] == 3
    assert selected["rail_thickness_mm"] == 4
    assert light["base_mm"] == light["wall_mm"] == 2.4
    assert light["rail_thickness_mm"] == 3.2 and light["light_variant"]


def test_all_generated_meshes_are_single_watertight_volumes():
    targets = list((ROOT / "exports").glob("manufacturing/*.stl")) + list((ROOT / "exports").glob("coupons/*.stl")) + list((ROOT / "exports").glob("variants/*.stl"))
    assert len(targets) == 6
    for target in targets:
        mesh = trimesh.load_mesh(target, force="mesh", process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
        assert len(mesh.split(only_watertight=False)) == 1


def test_selected_plate_is_collision_free():
    report = json.loads((ROOT / "reports/nesting-layout.json").read_text())
    assert report["status"] == "PASS"
    assert report["metrics"]["plate_count"] == 1 and report["metrics"]["object_count"] == 5


def test_sparse_geometry_and_light_boundary_are_quantified():
    report = json.loads((ROOT / "reports/optimization-geometric.json").read_text())
    assert report["selected"]["reduction_percent"] >= 85
    assert report["light_variant"]["reduction_percent_vs_selected_dock"] >= 10
    assert report["light_variant"]["constraint"].startswith("REJECTED")


def test_claim_boundary_is_explicit():
    contract = P["physical_contract"]
    assert contract["charging"].startswith("no_electronics_or_charging_claim")
    assert contract["physical_validation"] == "DEFERRED"
    text = (ROOT / "requirements-review.md").read_text().lower()
    assert "open-book reading support" in text and "brand-specific" in text
