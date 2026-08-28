import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_identity():
    assert P["project"] == {"id": "MM-ORG-036", "revision": "0.1.0-draft.2", "units": "mm"}


def test_pilot_inside_portfolio_envelope():
    platform = P["platform"]
    assert platform["width_mm"] <= 220
    assert platform["depth_mm"] <= 220
    assert platform["lift_height_mm"] <= 90


def test_protected_sections():
    platform = P["platform"]
    assert platform["deck_thickness_mm"] >= 4.0
    assert platform["perimeter_beam_mm"] >= 10.0
    assert platform["internal_rib_width_mm"] >= 6.0
    assert platform["post_size_mm"] >= 16.0


def test_rib_centers_clear_perimeter():
    platform = P["platform"]
    margin = platform["perimeter_beam_mm"] + platform["internal_rib_width_mm"] / 2
    assert all(margin < x < platform["width_mm"] - margin for x in platform["x_rib_centers_mm"])
    assert all(margin < y < platform["depth_mm"] - margin for y in platform["y_rib_centers_mm"])


def test_load_program_is_bounded():
    load = P["load_program"]
    assert load["distributed_mass_kg"] == 2.0
    assert load["duration_days"] == 30
    assert load["max_drawer_temperature_c"] == 40.0


def test_coupons_share_envelope_and_deck():
    coupon = P["coupons"]
    assert [coupon["width_mm"], coupon["depth_mm"]] == P["platform"]["minimum_tray_footprint_mm"]
    assert coupon["deck_thickness_mm"] == P["platform"]["deck_thickness_mm"]
    assert coupon["deck_perimeter_mm"] >= 8.0
    assert coupon["deck_center_rib_mm"] >= 6.0
    assert coupon["side_rib_count_per_side"] == 3


def test_full_watermark_has_dedicated_safe_land():
    mark = P["watermark"]
    assert mark["asset_revision"] == "MM-WM-001-R2"
    assert mark["selected_tier"] == "full" and mark["layout_priority"] == 1
    assert mark["domain_visible"] is True
    assert mark["uniform_scale"] == 1.0 and mark["rotation_deg"] == 0
    assert mark["land_width_mm"] >= 81.239 + 2 * mark["edge_clearance_mm"]
    assert mark["land_depth_mm"] >= 12.8 + 2 * mark["edge_clearance_mm"]
    assert mark["land_thickness_mm"] - mark["engraving_depth_mm"] >= 0.8
    center_post_y = (P["platform"]["depth_mm"] - P["platform"]["post_size_mm"]) / 2
    assert mark["land_origin_y_mm"] >= center_post_y + P["platform"]["post_size_mm"]
    assert mark["land_origin_y_mm"] + mark["land_depth_mm"] < P["platform"]["depth_mm"] - P["platform"]["post_size_mm"]


def test_recessed_watermark_stays_open_and_one_component():
    mesh_report = json.loads((ROOT / "validation/fdm-mesh-platform.json").read_text())
    mark_report = json.loads((ROOT / "validation/watermark-report.json").read_text())
    iteration = json.loads((ROOT / "validation/watermark-land-iteration.json").read_text())
    exact = mesh_report["metrics"]["exact_coordinate_welded"]
    assert mesh_report["status"] == "PASS"
    assert exact["components"] == 1 and exact["boundary_edges"] == 0
    assert mark_report["status"] == "PASS"
    assert mark_report["metrics"]["selector"]["selection"]["layout_tier"] == "full"
    assert iteration["status"] == "PASS"
    assert iteration["iterations"][-1]["land_origin_y_mm"] == P["watermark"]["land_origin_y_mm"]
    assert iteration["iterations"][-1]["exact_coordinate_components"] == 1


def test_top_face_down_jobs_are_warning_free_and_supportless():
    reports = [
        json.loads((ROOT / "validation/slicer-anycubic-pla-full-run-002.json").read_text()),
        json.loads((ROOT / "validation/slicer-anycubic-pla-coupons-run-002.json").read_text()),
    ]
    for report in reports:
        assert report["status"] == "PASS"
        assert report["metrics"]["gcode_files"] == 1
        assert all(not plate["warning_message"] for plate in report["native_result"]["sliced_plates"])
        assert [row["name"] for row in report["slicer"]["profiles"] if row["type"] == "filament"] == [
            "Anycubic PLA @Anycubic Kobra 3 Max 0.4 nozzle"
        ]
    preflight = json.loads((ROOT / "validation/slicer-preflight-report.json").read_text())
    support_check = next(row for row in preflight["checks"] if row["id"] == "supports-disabled")
    assert support_check["status"] == "PASS"
