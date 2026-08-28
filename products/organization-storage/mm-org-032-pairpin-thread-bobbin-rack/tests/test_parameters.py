from __future__ import annotations

import json
from pathlib import Path
import sys

import trimesh

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cad"))
from build import make_pin_gauge, make_rack  # noqa: E402

P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_project_and_portfolio_envelope():
    shape, interface = make_rack(P)
    assert P["project"]["id"] == "MM-ORG-032"
    assert interface["outer_bounds_mm"] == [208.0, 151.0, 65.0]
    assert shape.val().isValid() and len(shape.solids().vals()) == 1


def test_eight_pairs_share_four_column_centerlines():
    _, interface = make_rack(P)
    assert interface["pair_count"] == 8
    assert sorted({station["x_mm"] for station in interface["stations"]}) == [26, 78, 130, 182]
    assert all(sum(station["column"] == column for station in interface["stations"]) == 2 for column in range(1, 5))


def test_stored_envelopes_retain_minimum_gap():
    _, interface = make_rack(P)
    assert min(interface["stored_envelope_gaps_mm"].values()) >= P["fit"]["minimum_neighbor_gap_mm"]
    assert interface["stored_envelope_gaps_mm"]["spool_to_bobbin_same_pair_mm"] == 1.5


def test_selected_pin_diameters_share_fit_source():
    _, interface = make_rack(P)
    assert interface["spool_post_diameter_mm"] == P["fit"]["selected_spool_post_diameter_mm"] == 5
    assert interface["bobbin_post_diameter_mm"] == P["fit"]["selected_bobbin_post_diameter_mm"] == 4.5


def test_spool_gauge_brackets_selected_pin():
    shape, interface = make_pin_gauge(P, "spool")
    assert shape.val().isValid() and len(shape.solids().vals()) == 1
    assert interface["candidate_diameters_mm"] == [4, 4.5, 5, 5.5]
    assert interface["selected_diameter_mm"] == 5


def test_bobbin_gauge_brackets_selected_pin():
    shape, interface = make_pin_gauge(P, "bobbin")
    assert shape.val().isValid() and len(shape.solids().vals()) == 1
    assert interface["candidate_diameters_mm"] == [3.5, 4, 4.5, 5]
    assert interface["selected_diameter_mm"] == 4.5


def test_thread_contact_fillets_are_explicit():
    _, interface = make_rack(P)
    assert interface["spool_tip_fillet_mm"] == 1.6
    assert interface["bobbin_tip_fillet_mm"] == 1.4
    assert interface["collar_top_fillet_mm"] == 0.8


def test_light_variant_changes_only_declared_base_section():
    _, selected = make_rack(P)
    _, light = make_rack(P, light=True)
    assert selected["base_mm"] == 3 and light["base_mm"] == 2.4
    for key in ["spool_post_diameter_mm", "bobbin_post_diameter_mm", "spool_tip_fillet_mm", "bobbin_tip_fillet_mm"]:
        assert selected[key] == light[key]


def test_label_datums_are_nonembossed_and_column_counted():
    _, interface = make_rack(P)
    assert len(interface["label_datums"]) == 4
    assert all(item["width_mm"] == 42 and item["height_mm"] == 10 for item in interface["label_datums"])


def test_all_generated_meshes_are_single_watertight_volumes():
    targets = list((ROOT / "exports").glob("manufacturing/*.stl")) + list((ROOT / "exports").glob("coupons/*.stl")) + list((ROOT / "exports").glob("variants/*.stl"))
    assert len(targets) == 4
    for target in targets:
        mesh = trimesh.load_mesh(target, force="mesh", process=True)
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
        assert len(mesh.split(only_watertight=False)) == 1


def test_selected_plate_is_collision_free():
    report = json.loads((ROOT / "reports/nesting-layout.json").read_text())
    assert report["status"] == "PASS"
    assert report["metrics"]["plate_count"] == 1 and report["metrics"]["object_count"] == 3


def test_geometric_reduction_and_light_boundary_are_quantified():
    report = json.loads((ROOT / "reports/optimization-geometric.json").read_text())
    assert report["selected"]["reduction_percent"] >= 90
    assert report["light_variant"]["reduction_percent_vs_selected_rack"] >= 10
    assert report["light_variant"]["constraint"].startswith("REJECTED")


def test_claim_boundary_is_explicit():
    contract = P["physical_contract"]
    assert contract["physical_validation"] == "DEFERRED"
    assert "no_tension_or_feed_claim" in contract["thread_contact"]
    text = (ROOT / "requirements-review.md").read_text().lower()
    assert "machine feeding/tension" in text and "universal fit" in text
