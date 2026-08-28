import importlib.util
import hashlib
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


def test_normalization_transliterates_german_characters():
    font = load_module(ROOT / "cad/gridfont.py", "mm_org_026_font")
    allowed = PARAMS["personalization"]["allowed_characters"]
    assert font.normalize_text("Jörg Weiß", allowed, 18) == "JOERG WEISS"


def test_normalization_rejects_unsupported_characters():
    font = load_module(ROOT / "cad/gridfont.py", "mm_org_026_font_bad")
    with pytest.raises(ValueError):
        font.normalize_text("ALEX / MORGAN", PARAMS["personalization"]["allowed_characters"], 18)


def test_maximum_lengths_keep_printable_pixels():
    font = load_module(ROOT / "cad/gridfont.py", "mm_org_026_font_limits")
    plate = PARAMS["plate"]
    available = plate["width_mm"] - 2 * plate["text_margin_x_mm"]
    name = font.layout("W" * 18, available, plate["name_height_mm"], plate["maximum_pixel_pitch_mm"], plate["minimum_pixel_width_mm"])
    title = font.layout("W" * 26, available, plate["title_height_mm"], plate["maximum_pixel_pitch_mm"], plate["minimum_pixel_width_mm"])
    assert name["pixel_width_mm"] >= 0.8
    assert title["pixel_width_mm"] >= 0.8


def test_live_preview_matches_default_text_and_font():
    preview = json.loads((ROOT / "reports/live-text-preview.json").read_text())
    assert preview["status"] == "PASS"
    assert preview["normalized_name"] == "ALEX MORGAN"
    assert preview["normalized_title"] == "DESIGN STUDIO"
    assert preview["font_id"] == "MM-GRID-5X7-v1"


def test_live_preview_and_cad_interface_share_one_exact_glyph_contract():
    preview = json.loads((ROOT / "reports/live-text-preview.json").read_text())
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())
    insert = interface["metrics"]["interfaces"]["personalized-insert"]
    svg_hash = hashlib.sha256((ROOT / "renders/MM-ORG-026-live-text-preview.svg").read_bytes()).hexdigest()
    input_hashes = {item["path"]: item["sha256"] for item in preview["inputs"]}
    assert preview["status"] == "PASS"
    assert all(item["status"] == "PASS" for item in preview["checks"])
    assert preview["svg_sha256"] == svg_hash
    assert preview["font_id"] == insert["font_id"]
    assert preview["normalized_name"] == insert["normalized_name"]
    assert preview["normalized_title"] == insert["normalized_title"]
    assert input_hashes["cad/gridfont.py"] == hashlib.sha256((ROOT / "cad/gridfont.py").read_bytes()).hexdigest()
    assert input_hashes["config/model-parameters.json"] == hashlib.sha256((ROOT / "config/model-parameters.json").read_bytes()).hexdigest()


def test_font_is_allowlisted_without_external_binary():
    allowlist = json.loads((ROOT / "assets/font-allowlist.json").read_text())
    record = allowlist["fonts"][0]
    assert record["font_id"] == "MM-GRID-5X7-v1"
    assert record["external_font_file"] is False
    assert record["design_use_status"] == "APPROVED_INTERNAL_DIGITAL_CANDIDATE"
    assert record["commercial_release_status"] == "REVIEW_REQUIRED"


def test_personalized_insert_is_one_valid_solid():
    build = load_module(ROOT / "cad/build.py", "mm_org_026_plate")
    shape, interface = build.make_plate(PARAMS)
    assert shape.isValid() and len(shape.Solids()) == 1
    assert np.allclose(interface["outer_dimensions_mm"], [200.0, 50.0, 3.0])
    assert interface["minimum_backing_mm"] == 2.4


def test_stand_is_one_valid_solid_with_open_slot():
    build = load_module(ROOT / "cad/build.py", "mm_org_026_stand")
    shape, interface = build.make_stand(PARAMS)
    assert shape.isValid() and len(shape.Solids()) == 1
    assert np.allclose(interface["outer_dimensions_mm"], [26.0, 62.0, 20.0])
    assert interface["minimum_open_insertion_depth_mm"] > 16.0


def test_coupon_brackets_production_and_key_matches_insert():
    build = load_module(ROOT / "cad/build.py", "mm_org_026_coupon")
    gauge_shape, gauge = build.make_slot_gauge(PARAMS)
    key_shape, key = build.make_fit_key(PARAMS)
    assert gauge_shape.isValid() and key_shape.isValid()
    assert gauge["candidate_slot_widths_mm"] == [3.2, 3.4, 3.6]
    assert key["thickness_mm"] == PARAMS["plate"]["thickness_mm"]


def test_nominal_slot_has_point_four_total_clearance():
    assert np.isclose(PARAMS["stand"]["slot_width_mm"] - PARAMS["plate"]["thickness_mm"], 0.4)


def test_installed_assembly_respects_portfolio_envelope():
    build = load_module(ROOT / "cad/build.py", "mm_org_026_envelope")
    envelope = PARAMS["workflow_contract"]["assembly_envelope_mm"]
    assert PARAMS["plate"]["width_mm"] <= envelope[0]
    assert PARAMS["stand"]["depth_mm"] <= envelope[1]
    assert build.installed_height(PARAMS) <= envelope[2]


def test_default_stands_are_symmetric():
    assert PARAMS["stand"]["default_center_offsets_x_mm"] == [-78.0, 78.0]


def test_layer_relations_are_integral():
    layer = PARAMS["printer"]["layer_height_mm"]
    assert np.isclose(PARAMS["plate"]["thickness_mm"] / layer, 15)
    assert np.isclose(PARAMS["stand"]["height_mm"] / layer, 100)
    assert np.isclose(PARAMS["plate"]["engraving_depth_mm"] / layer, 3)


def test_support_conscious_orientations_are_declared():
    build = load_module(ROOT / "cad/build.py", "mm_org_026_orientation")
    interfaces = [build.make_plate(PARAMS)[1], build.make_stand(PARAMS)[1], build.make_slot_gauge(PARAMS)[1], build.make_fit_key(PARAMS)[1]]
    assert all(item["print_orientation"] in {"base_down", "back_face_down"} for item in interfaces)


def test_claim_and_privacy_boundaries_are_explicit():
    contract = PARAMS["workflow_contract"]
    assert contract["claim"] == "indoor_decorative_identification_only_no_affiliation_or_accessibility_claim"
    assert contract["privacy"] == "do_not_retain_customer_names_outside_order_and_proof_records"


def test_candidate_volume_reduction_passes():
    result = json.loads((ROOT / "reports/optimization-comparison.json").read_text())
    assert result["status"] == "PASS"
    assert result["volume_reduction_percent"] >= 35.0
