import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_identity_envelope_and_privacy():
    assert P["project"] == {"id": "MM-ORG-038", "revision": "0.1.0-draft.1", "units": "mm"}
    b = P["base"]
    assert b["width_mm"] <= 160 and b["depth_mm"] <= 90 and b["rear_rail_height_mm"] <= 80
    assert P["personalization"]["front_text"] == "YOUR MOMENT"
    assert "do not retain" in P["personalization"]["privacy_mode"]


def test_shared_tapered_slot_contract():
    s = P["slots"]
    assert s["bottom_gap_mm"] < min(s["intended_card_thickness_mm"])
    assert s["top_gap_mm"] > max(s["intended_card_thickness_mm"])
    assert s["rear"]["depth_mm"] == 10.0 and s["front"]["depth_mm"] == 8.0
    assert 5 <= s["back_tilt_deg"] <= 12


def test_bridge_overlap_and_one_piece_intent():
    b = P["base"]
    assert b["connector_depth_mm"] > b["rear_rail_center_y_mm"] - b["rear_rail_depth_mm"] / 2 - (b["front_rail_center_y_mm"] + b["front_rail_depth_mm"] / 2)
    assert all(abs(x) + b["connector_width_mm"] / 2 <= b["front_rail_width_mm"] / 2 + 0.01 for x in b["connector_centers_x_mm"])


def test_slot_bottoms_clear_watermark_recess():
    b, s, w = P["base"], P["slots"], P["watermark"]
    rear_floor = b["rear_rail_height_mm"] - s["rear"]["depth_mm"]
    assert rear_floor - w["engraving_depth_mm"] >= 0.8
    assert w["surface_width_mm"] >= 80.292 + 2 * w["edge_clearance_mm"]
    assert w["surface_depth_mm"] >= 12.8 + 2 * w["edge_clearance_mm"]


def test_supportless_groove_wall_angle():
    s = P["slots"]
    half_delta = (s["top_gap_mm"] - s["bottom_gap_mm"]) / 2
    wall_from_vertical_deg = math.degrees(math.atan(half_delta / s["front"]["depth_mm"]))
    assert wall_from_vertical_deg < 15
    assert P["printing"]["orientation"] == "base-down" and not P["printing"]["generated_support"]


def test_full_watermark_contract():
    w = P["watermark"]
    assert w["asset_revision"] == "MM-WM-001-R2"
    assert w["selected_tier"] == "full" and w["layout_priority"] == 1
    assert w["domain_visible"] and w["uniform_scale"] == 1.0 and w["rotation_deg"] == 0


def test_all_digital_mesh_and_package_reports_pass():
    names = [
        "fdm-mesh-base.json",
        "fdm-mesh-slot-gauge.json",
        "fdm-mesh-watermark-coupon.json",
        "fdm-3mf-base.json",
        "fdm-3mf-coupons.json",
    ]
    assert all(json.loads((ROOT / "validation" / name).read_text())["status"] == "PASS" for name in names)


def test_exact_slicer_jobs_are_warning_free_and_flow_bounded():
    report = json.loads((ROOT / "validation/slicer-preflight-report.json").read_text())
    assert report["status"] == "PASS"
    assert set(report["metrics"]) == {"fit-and-mark-coupons", "momentpair-base"}
    assert all(row["status"] == "PASS" for row in report["checks"] if row["id"].endswith(("native-warning", "parser-warnings", "declared-flow")))
    assert max(job["peak_flow_mm3_s"] for job in report["metrics"].values()) <= 13.3


def test_print_candidate_and_aggregate_validation_pass():
    candidate = json.loads((ROOT / "validation/print-candidate-report.json").read_text())
    summary = json.loads((ROOT / "validation/validation-summary.json").read_text())
    approvals = json.loads((ROOT / "validation/approvals-through-print-candidate.json").read_text())
    assert candidate["status"] == "PASS" and candidate["metrics"]["digital_print_candidate"]
    assert summary["status"] == "PASS"
    assert approvals["status"] == "PASS"


def test_gauge_and_final_slots_share_depth_and_taper_contract():
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())
    slots = interface["metrics"]["slots"]
    gauge = interface["metrics"]["gauge"]
    assert gauge["slot_depths_mm"] == [slots["rear"]["depth_mm"], slots["front"]["depth_mm"]]
    assert gauge["top_gap_mm"] == slots["top_gap_mm"]
    assert gauge["bottom_gap_mm"] == slots["bottom_gap_mm"]
    assert gauge["back_tilt_deg"] == slots["back_tilt_deg"]
