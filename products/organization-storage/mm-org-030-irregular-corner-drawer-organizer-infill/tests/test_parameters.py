import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PARAMS=json.loads((ROOT/"config/model-parameters.json").read_text())


def load_geometry():
    spec=importlib.util.spec_from_file_location("mm_org_030_geometry",ROOT/"cad/geometry.py"); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def test_three_presets_are_distinct_and_valid():
    geometry=load_geometry(); polygons=[geometry.footprint_polygon(p,1.0) for p in PARAMS["presets"]]
    assert [p["id"] for p in PARAMS["presets"]]==["round-corner","rectangular-notch","skewed-corner"]
    assert all(p.is_valid and p.area>10000 for p in polygons)
    assert len({round(p.area,2) for p in polygons})==3


def test_inner_offsets_retain_minimum_area():
    geometry=load_geometry(); tray=PARAMS["tray"]
    assert all(geometry.inner_polygon(p,1.0,tray["wall_mm"]).area>=tray["minimum_inner_area_mm2"] for p in PARAMS["presets"])


def test_clearance_series_brackets_selected():
    fit=PARAMS["fit"]
    assert fit["candidate_per_side_clearances_mm"]==[0.5,1.0,1.5]
    assert fit["selected_per_side_clearance_mm"]==1.0


def test_coupon_diameters_reproduce_key_plus_two_sided_clearance():
    interfaces=json.loads((ROOT/"validation/interface-report.json").read_text())["metrics"]["interfaces"]
    gauge,key=interfaces["clearance-gauge"],interfaces["reference-key"]
    assert key["diameter_mm"]==20.0
    assert gauge["slot_diameters_mm"]==[21.0,22.0,23.0]


def test_templates_share_clearance_and_exact_hashes():
    report=json.loads((ROOT/"reports/template-generation.json").read_text())
    assert report["status"]=="PASS" and report["metrics"]["clearance_per_side_mm"]==1.0
    for item in report["metrics"]["templates"]:
        target=ROOT/item["path"]
        assert hashlib.sha256(target.read_bytes()).hexdigest()==item["sha256"]


def test_template_calibration_contract_is_explicit():
    assert PARAMS["fit"]["paper_print_scale_tolerance_percent"]==0.5
    assert all("100 mm calibration" in target.read_text() for target in (ROOT/"assets/templates").glob("*.svg"))


def test_selected_shell_and_envelope_are_protected():
    tray=PARAMS["tray"]
    assert tray["wall_mm"]>=3 and tray["base_mm"]>=3
    assert all(p["length_mm"]<=220 and p["width_mm"]<=220 and tray["height_mm"]<=80 for p in PARAMS["presets"])


def test_all_meshes_valid_and_below_budget():
    report=json.loads((ROOT/"reports/mesh-complexity.json").read_text())
    assert report["status"]=="PASS" and len(report["meshes"])==6
    assert all(m["watertight"] and m["winding_consistent"] and m["positive_volume"] and m["components"]==1 for m in report["meshes"].values())


def test_one_plate_nesting_is_collision_free():
    report=json.loads((ROOT/"reports/nesting-layout.json").read_text())
    assert report["status"]=="PASS" and report["metrics"]["plate_count"]==1 and report["metrics"]["object_count"]==5


def test_geometric_reduction_and_light_boundary():
    report=json.loads((ROOT/"reports/optimization-geometric.json").read_text()); manifest=json.loads((ROOT/"reports/build-manifest.json").read_text())
    assert report["selected"]["reduction_percent"]>=80
    assert report["light_variant"]["reduction_percent_vs_selected_round"]>=15
    assert all("light-round" not in item for item in manifest["manufacturing_outputs"])


def test_selected_layer_height_is_declared_and_support_free():
    assert np.isclose(PARAMS["printer"]["selected_layer_height_mm"],0.28)
    assert PARAMS["printer"]["supports"]=="none"


def test_claim_boundary_is_explicit():
    contract=PARAMS["physical_contract"]
    assert contract["contents"]=="dry_indoor_small_items_only"
    assert contract["excluded"]=="load_bearing_food_contact_liquids_hot_items_children_under_three"
