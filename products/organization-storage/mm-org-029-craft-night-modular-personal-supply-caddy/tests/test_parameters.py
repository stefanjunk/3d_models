import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())
BATCH = json.loads((ROOT / "config/name-batch.json").read_text())


def load_module(target: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, target)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_batch_normalization_and_identity():
    assert [item["normalized_name"] for item in BATCH["names"]] == ["ALEX", "BLAIR", "CASEY", "DEVIN"]
    assert BATCH["font_id"] == "MM-GRID-5X7-v1"


def test_name_normalizer_rejects_bad_or_long_input():
    font = load_module(ROOT / "cad/gridfont.py", "mm_org_029_font_bad")
    with pytest.raises(ValueError):
        font.normalize_text("A/B", PARAMS["batch"]["allowed_characters"], 8)
    with pytest.raises(ValueError):
        font.normalize_text("ABCDEFGHI", PARAMS["batch"]["allowed_characters"], 8)


def test_maximum_name_keeps_printable_pixels():
    font = load_module(ROOT / "cad/gridfont.py", "mm_org_029_font")
    p = PARAMS["nameplate"]
    data = font.layout("W" * 8, p["text_available_width_mm"], p["text_height_mm"], p["maximum_pixel_pitch_mm"], p["minimum_pixel_width_mm"])
    assert data["pixel_width_mm"] >= 0.8


def test_live_batch_proof_is_exact_and_complete():
    proof = json.loads((ROOT / "reports/live-batch-preview.json").read_text())
    assert proof["status"] == "PASS"
    assert proof["metrics"]["names"] == [item["normalized_name"] for item in BATCH["names"]]
    assert proof["metrics"]["svg_sha256"] == hashlib.sha256((ROOT / "renders/MM-ORG-029-live-batch-preview.svg").read_bytes()).hexdigest()


def test_csv_proof_and_cad_share_exact_glyph_contract():
    imported = json.loads((ROOT / "reports/csv-import.json").read_text())
    proof = json.loads((ROOT / "reports/live-batch-preview.json").read_text())
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())
    expected = [item["normalized_name"] for item in imported["metrics"]["names"]]
    cad = [item["normalized_name"] for item in interface["metrics"]["names"]]
    assert expected == proof["metrics"]["names"] == cad
    assert imported["metrics"]["font_id"] == proof["metrics"]["font_id"] == interface["metrics"]["font_record"]["font_id"]


def test_dock_and_nameplate_clearances_are_explicit():
    dock, plate = PARAMS["dock"], PARAMS["nameplate"]
    assert dock["candidate_total_clearances_mm"] == [0.2, 0.4, 0.6]
    assert np.isclose(dock["selected_total_clearance_mm"], 0.4)
    assert np.isclose(plate["slot_width_mm"] - plate["thickness_mm"], 0.4)
    assert np.isclose(plate["slot_length_mm"] - plate["width_mm"], 0.4)


def test_vertical_dovetail_is_captive_and_support_free():
    dock, caddy = PARAMS["dock"], PARAMS["caddy"]
    assert dock["key_head_width_mm"] > dock["key_base_width_mm"]
    assert dock["key_height_mm"] < caddy["dock_boss_height_mm"]
    assert dock["key_origin_z_mm"] == 0
    assert PARAMS["printer"]["supports"] == "none"


def test_bed_built_dock_revision_is_warning_free():
    assert PARAMS["dock"]["key_origin_z_mm"] == 0
    for report_name in ("slicer-system-020.json", "slicer-system-028.json"):
        report = json.loads((ROOT / "validation" / report_name).read_text())
        assert report["status"] == "PASS"
        assert all(not item.get("warning_message", "").strip() for item in report["native_result"]["sliced_plates"])
        assert all(not value["metrics"]["warnings"] for value in report["gcode_reports"].values())


def test_selected_shell_and_envelopes_are_protected():
    caddy = PARAMS["caddy"]
    assert caddy["wall_mm"] >= 3 and caddy["base_mm"] >= 3
    assert [caddy["length_mm"], caddy["width_mm"], caddy["height_mm"]] == [145.0, 95.0, 65.0]
    assert caddy["length_mm"] + PARAMS["nameplate"]["boss_depth_mm"] - caddy["wall_mm"] <= 180


def test_all_unique_meshes_are_valid_and_below_budget():
    report = json.loads((ROOT / "reports/mesh-complexity.json").read_text())
    assert report["status"] == "PASS" and len(report["meshes"]) == 9
    assert all(item["watertight"] and item["winding_consistent"] and item["positive_volume"] and item["components"] == 1 for item in report["meshes"].values())
    assert all(item["triangles"] <= PARAMS["mesh"]["triangle_stop"] and item["file_mib"] <= PARAMS["mesh"]["max_mesh_mib"] for item in report["meshes"].values())


def test_one_plate_nesting_has_no_overlap_and_eleven_objects():
    report = json.loads((ROOT / "reports/nesting-layout.json").read_text())
    assert report["status"] == "PASS"
    assert report["metrics"]["plate_count"] == 1 and report["metrics"]["object_count"] == 11
    assert all(item["status"] == "PASS" for item in report["checks"])


def test_selected_layer_relations_are_integral():
    layer = PARAMS["printer"]["selected_layer_height_mm"]
    assert np.isclose(PARAMS["caddy"]["wall_mm"] / layer, 15.0)
    assert np.isclose(PARAMS["caddy"]["base_mm"] / layer, 15.0)
    assert np.isclose(PARAMS["nameplate"]["engraving_depth_mm"] / layer, 3.0)


def test_geometric_optimization_keeps_light_variant_out_of_manufacturing():
    result = json.loads((ROOT / "reports/optimization-geometric.json").read_text())
    manifest = json.loads((ROOT / "reports/build-manifest.json").read_text())
    assert result["selected"]["reduction_percent"] >= 70.0
    assert result["light_variant"]["constraint"] == "REJECTED_PENDING_LOADED_FLEX_DROP_AND_DOCKING_EVIDENCE"
    assert all("light-personal-caddy" not in item for item in manifest["manufacturing_outputs"])


def test_claim_boundary_excludes_hot_tools_solvents_and_food():
    contract = PARAMS["physical_contract"]
    assert contract["contents"] == "dry_indoor_adult_craft_supplies_only"
    assert contract["excluded"] == "hot_tools_solvents_liquids_food_contact_children_unsupervised"
