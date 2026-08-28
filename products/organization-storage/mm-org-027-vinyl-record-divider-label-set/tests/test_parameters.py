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
    importer = load_module(ROOT / "tools/import_labels.py", "mm_org_027_import")
    rows = importer.parse_rows(ROOT / "config/labels.csv", PARAMS)
    assert [item["normalized_label"] for item in rows] == ["A-E", "F-J", "K-O", "P-T", "U-Z", "JAZZ"]
    assert [item["tab_position"] for item in rows] == ["left", "center", "right", "left", "center", "right"]


def test_csv_import_rejects_duplicate_or_unsupported_rows(tmp_path):
    importer = load_module(ROOT / "tools/import_labels.py", "mm_org_027_import_bad")
    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text("label,tab_position\nJazz,left\nJAZZ,right\n", encoding="utf-8")
    with pytest.raises(ValueError):
        importer.parse_rows(duplicate, PARAMS)
    unsupported = tmp_path / "unsupported.csv"
    unsupported.write_text("label,tab_position\nA/E,center\n", encoding="utf-8")
    with pytest.raises(ValueError):
        importer.parse_rows(unsupported, PARAMS)


def test_maximum_label_keeps_printable_pixels():
    font = load_module(ROOT / "cad/gridfont.py", "mm_org_027_font")
    cap = PARAMS["label_cap"]
    data = font.layout("W" * 10, cap["width_mm"] - 2 * cap["text_margin_x_mm"], cap["text_height_mm"], cap["maximum_pixel_pitch_mm"], cap["minimum_pixel_width_mm"])
    assert data["pixel_width_mm"] >= 0.8


def test_live_batch_proof_is_exact_and_complete():
    proof = json.loads((ROOT / "reports/live-batch-preview.json").read_text())
    assert proof["status"] == "PASS"
    assert all(item["status"] == "PASS" for item in proof["checks"])
    assert proof["metrics"]["labels"] == [item["normalized_label"] for item in BATCH["labels"]]
    assert proof["metrics"]["font_id"] == "MM-GRID-5X7-v1"
    assert proof["metrics"]["svg_sha256"] == hashlib.sha256((ROOT / "renders/MM-ORG-027-live-batch-preview.svg").read_bytes()).hexdigest()


def test_csv_proof_and_cad_share_one_exact_glyph_contract():
    imported = json.loads((ROOT / "reports/csv-import.json").read_text())
    proof = json.loads((ROOT / "reports/live-batch-preview.json").read_text())
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())
    expected = [item["normalized_label"] for item in imported["metrics"]["labels"]]
    actual = [item["normalized_label"] for item in interface["metrics"]["labels"]]
    assert imported["status"] == proof["status"] == interface["status"] == "PASS"
    assert expected == proof["metrics"]["labels"] == actual
    assert imported["metrics"]["font_id"] == proof["metrics"]["font_id"] == interface["metrics"]["font_record"]["font_id"] == "MM-GRID-5X7-v1"
    assert imported["metrics"]["batch_json_sha256"] == hashlib.sha256((ROOT / "config/label-batch.json").read_bytes()).hexdigest()
    assert proof["metrics"]["svg_sha256"] == hashlib.sha256((ROOT / "renders/MM-ORG-027-live-batch-preview.svg").read_bytes()).hexdigest()
    assert proof["metrics"]["minimum_pixel_width_mm"] >= PARAMS["label_cap"]["minimum_pixel_width_mm"]


def test_smooth_and_windowed_carriers_are_valid_single_solids():
    build = load_module(ROOT / "cad/build.py", "mm_org_027_carriers")
    smooth, smooth_i = build.make_carrier(PARAMS)
    windowed, windowed_i = build.make_carrier(PARAMS, windowed=True)
    assert smooth.isValid() and len(smooth.Solids()) == 1
    assert windowed.isValid() and len(windowed.Solids()) == 1
    assert smooth_i["record_contact_surface"] == "continuous"
    assert windowed_i["record_contact_surface"] == "interrupted"
    assert windowed.Volume() < smooth.Volume()


def test_every_label_cap_is_valid_with_protected_text_band():
    build = load_module(ROOT / "cad/build.py", "mm_org_027_caps")
    for item in BATCH["labels"]:
        shape, interface = build.make_label_cap(PARAMS, item)
        assert shape.isValid() and len(shape.Solids()) == 1
        assert interface["text_to_slot_margin_mm"] >= 2.0
        assert interface["minimum_backing_mm"] >= 1.8 or np.isclose(interface["minimum_backing_mm"], 1.8)
        assert interface["layout"]["pixel_width_mm"] >= 0.8


def test_fit_contract_and_coupon_bracket_production():
    build = load_module(ROOT / "cad/build.py", "mm_org_027_fit")
    gauge, gauge_i = build.make_slot_gauge(PARAMS)
    key, key_i = build.make_fit_key(PARAMS)
    assert gauge.isValid() and key.isValid()
    assert gauge_i["candidate_slot_widths_mm"] == [1.8, 1.9, 2.0]
    assert np.isclose(PARAMS["label_cap"]["nominal_slot_width_mm"] - PARAMS["carrier"]["thickness_mm"], 0.3)
    assert key_i["thickness_mm"] == PARAMS["carrier"]["thickness_mm"]


def test_all_selected_parts_respect_portfolio_envelope():
    envelope = PARAMS["workflow_contract"]["single_part_envelope_mm"]
    assert PARAMS["carrier"]["length_mm"] <= envelope[0]
    assert max(PARAMS["carrier"]["height_mm"], PARAMS["label_cap"]["width_mm"], PARAMS["coupon"]["gauge_width_mm"]) <= envelope[1]
    assert max(PARAMS["carrier"]["thickness_mm"], PARAMS["label_cap"]["thickness_mm"], PARAMS["coupon"]["gauge_thickness_mm"]) <= envelope[2]


def test_selected_layer_relations_are_integral():
    layer = PARAMS["printer"]["selected_layer_height_mm"]
    assert np.isclose(PARAMS["carrier"]["thickness_mm"] / layer, 8.0)
    assert np.isclose(PARAMS["label_cap"]["thickness_mm"] / layer, 12.0)
    assert np.isclose(PARAMS["label_cap"]["engraving_depth_mm"] / layer, 3.0)


def test_nesting_has_no_overlap_and_fourteen_objects():
    build = load_module(ROOT / "cad/build.py", "mm_org_027_nesting")
    placements, boxes, collisions = build.nesting(PARAMS, BATCH["labels"])
    assert len(placements) == len(boxes) == 14
    assert collisions == []
    assert max(item["x1"] for item in boxes) <= 420.0
    assert max(item["y1"] for item in boxes) <= 414.0


def test_no_infill_core_and_selected_contact_constraint_are_recorded():
    result = json.loads((ROOT / "reports/optimization-geometric.json").read_text())
    assert result["status"] == "PASS"
    assert result["thin_plate_core"]["status"] == "NO_INFILL_CORE"
    assert result["selected"]["reduction_percent"] >= 40.0
    assert result["windowed"]["constraint"] == "REJECTED_PENDING_PHYSICAL_EDGE_AND_RACKING_EVIDENCE"


def test_claim_and_contact_boundaries_are_explicit():
    contract = PARAMS["workflow_contract"]
    assert contract["claim"] == "dry_indoor_shelf_index_only_not_record_support_or_archival_protection"
    assert contract["contact"] == "use_between_protective_outer_sleeves_not_against_bare_records"
