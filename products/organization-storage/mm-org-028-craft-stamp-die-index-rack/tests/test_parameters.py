import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())
BATCH = json.loads((ROOT / "config/label-batch.json").read_text())


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_csv_import_matches_default_batch():
    importer = load_module(ROOT / "tools/import_labels.py", "mm_org_028_import")
    rows = importer.parse_rows(ROOT / "config/labels.csv", PARAMS)
    assert [item["normalized_label"] for item in rows] == ["STAMPS", "DIES", "ALPHA", "FLORAL"]
    assert [item["tab_position"] for item in rows] == ["left", "center", "right", "left"]


def test_csv_import_rejects_duplicate_or_unsupported_rows(tmp_path):
    importer = load_module(ROOT / "tools/import_labels.py", "mm_org_028_import_bad")
    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text("label,tab_position\nDies,left\nDIES,right\n", encoding="utf-8")
    with pytest.raises(ValueError):
        importer.parse_rows(duplicate, PARAMS)
    unsupported = tmp_path / "unsupported.csv"
    unsupported.write_text("label,tab_position\nA/B,center\n", encoding="utf-8")
    with pytest.raises(ValueError):
        importer.parse_rows(unsupported, PARAMS)


def test_maximum_label_keeps_printable_pixels():
    font = load_module(ROOT / "cad/gridfont.py", "mm_org_028_font")
    divider = PARAMS["divider"]
    data = font.layout("W" * 10, divider["tab_width_mm"] - 2 * divider["text_margin_x_mm"], divider["text_height_mm"], divider["maximum_pixel_pitch_mm"], divider["minimum_pixel_width_mm"])
    assert data["pixel_width_mm"] >= 0.8


def test_live_batch_proof_is_exact_and_complete():
    proof = json.loads((ROOT / "reports/live-batch-preview.json").read_text())
    assert proof["status"] == "PASS"
    assert all(item["status"] == "PASS" for item in proof["checks"])
    assert proof["metrics"]["labels"] == [item["normalized_label"] for item in BATCH["labels"]]
    assert proof["metrics"]["font_id"] == "MM-GRID-5X7-v1"
    assert proof["metrics"]["svg_sha256"] == hashlib.sha256((ROOT / "renders/MM-ORG-028-live-batch-preview.svg").read_bytes()).hexdigest()


def test_csv_proof_and_cad_share_one_exact_glyph_contract():
    imported = json.loads((ROOT / "reports/csv-import.json").read_text())
    proof = json.loads((ROOT / "reports/live-batch-preview.json").read_text())
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())
    expected = [item["normalized_label"] for item in imported["metrics"]["labels"]]
    cad = [item["normalized_label"] for item in interface["metrics"]["labels"]]
    assert expected == proof["metrics"]["labels"] == cad
    assert imported["metrics"]["font_id"] == proof["metrics"]["font_id"] == interface["metrics"]["font_record"]["font_id"] == "MM-GRID-5X7-v1"
    assert imported["metrics"]["batch_json_sha256"] == hashlib.sha256((ROOT / "config/label-batch.json").read_bytes()).hexdigest()


def test_lane_stack_and_capacity_are_explicit():
    rack = PARAMS["rack"]
    stack = (rack["lane_count"] + 1) * rack["fin_thickness_mm"] + rack["lane_count"] * rack["lane_gap_mm"]
    assert rack["lane_count"] == 15
    assert (rack["length_mm"] - stack) / 2 >= 3.0
    assert PARAMS["workflow_contract"]["capacity"] == "fifteen_lanes_not_fifteen_guaranteed_loaded_envelopes"


def test_default_envelope_contract_fits_and_excludes_loose_dies():
    envelope = PARAMS["envelope_contract"]
    assert envelope["maximum_width_mm"] <= PARAMS["rack"]["depth_mm"]
    assert envelope["maximum_loaded_thickness_mm"] < PARAMS["rack"]["lane_gap_mm"]
    assert envelope["contents"].startswith("filled protective")
    assert envelope["excluded"].startswith("loose_exposed")


def test_fit_contract_and_coupon_bracket_production():
    rack = PARAMS["rack"]
    divider = PARAMS["divider"]
    coupon = PARAMS["coupon"]
    assert np.isclose(rack["lane_gap_mm"] - divider["pad_installed_thickness_mm"], 0.4)
    assert coupon["candidate_slot_widths_mm"] == [10.9, 11.2, 11.5]
    assert coupon["key_width_mm"] == divider["pad_installed_thickness_mm"]


def test_selected_dividers_retain_protected_frames_and_three_pads():
    interfaces = json.loads((ROOT / "validation/interface-report.json").read_text())["metrics"]["interfaces"]
    selected = [value for name, value in interfaces.items() if name.startswith("index-divider-")]
    assert len(selected) == 4
    assert all(item["frame_width_mm"] >= 8 and item["center_rib_width_mm"] >= 12 for item in selected)
    assert all(item["pad_count"] == 3 and item["pad_installed_thickness_mm"] == 10.8 for item in selected)


def test_all_unique_meshes_are_valid_and_below_budget():
    report = json.loads((ROOT / "reports/mesh-complexity.json").read_text())
    assert report["status"] == "PASS"
    assert len(report["meshes"]) == 8
    assert all(item["watertight"] and item["winding_consistent"] and item["positive_volume"] and item["components"] == 1 for item in report["meshes"].values())
    assert all(item["triangles"] <= PARAMS["mesh"]["triangle_stop"] and item["file_mib"] <= PARAMS["mesh"]["max_mesh_mib"] for item in report["meshes"].values())


def test_two_plate_nesting_has_no_overlap_and_seven_objects():
    report = json.loads((ROOT / "reports/nesting-layout.json").read_text())
    assert report["status"] == "PASS"
    assert report["metrics"]["plate_count"] == 2
    assert report["metrics"]["object_count"] == 7
    assert all(item["status"] == "PASS" for item in report["checks"])


def test_selected_layer_relations_are_integral():
    layer = PARAMS["printer"]["selected_layer_height_mm"]
    assert np.isclose(PARAMS["rack"]["base_thickness_mm"] / layer, 15.0)
    assert np.isclose(PARAMS["divider"]["thickness_mm"] / layer, 12.0)
    assert np.isclose(PARAMS["divider"]["engraving_depth_mm"] / layer, 3.0)


def test_geometric_optimization_keeps_light_variant_out_of_manufacturing():
    result = json.loads((ROOT / "reports/optimization-geometric.json").read_text())
    manifest = json.loads((ROOT / "reports/build-manifest.json").read_text())
    assert result["status"] == "PASS"
    assert result["selected"]["reduction_percent"] >= 50.0
    assert result["light_variant"]["constraint"] == "REJECTED_PENDING_LOADED_RACKING_AND_ENVELOPE_SNAG_EVIDENCE"
    assert all("light-index-divider" not in item for item in manifest["manufacturing_outputs"])


def test_claim_and_single_part_boundaries_are_explicit():
    envelope = PARAMS["workflow_contract"]["single_part_envelope_mm"]
    assert envelope == [220.0, 180.0, 200.0]
    assert PARAMS["workflow_contract"]["claim"] == "dry_indoor_index_rack_for_filled_protective_envelopes_only"
    assert PARAMS["divider"]["body_height_mm"] + PARAMS["divider"]["tab_height_mm"] <= envelope[2]
