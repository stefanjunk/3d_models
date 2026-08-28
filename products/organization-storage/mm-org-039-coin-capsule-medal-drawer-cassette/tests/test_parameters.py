import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_identity_envelope_and_capacity():
    assert P["project"] == {"id": "MM-ORG-039", "revision": "0.1.0-draft.1", "units": "mm"}
    h = P["host"]
    assert h["width_mm"] <= 220 and h["depth_mm"] <= 150 and h["height_mm"] <= 20
    assert h["columns"] * h["rows"] == 6


def test_cell_dimensions_are_derived_from_host():
    h = P["host"]
    inner_w = h["width_mm"] - 2 * h["wall_thickness_mm"]
    inner_d = h["depth_mm"] - 2 * h["wall_thickness_mm"]
    expected_w = (inner_w - (h["columns"] - 1) * h["wall_thickness_mm"]) / h["columns"]
    expected_d = (inner_d - (h["rows"] - 1) * h["wall_thickness_mm"]) / h["rows"]
    assert abs(h["cell_width_mm"] - expected_w) < 1e-6
    assert abs(h["cell_depth_mm"] - expected_d) < 1e-6


def test_large_capsule_and_adapter_clearances_are_loose():
    h, i = P["host"], P["interfaces"]
    assert (h["cell_width_mm"] - i["direct_large_square_target_mm"][0]) / 2 >= 0.4
    assert (h["cell_depth_mm"] - i["direct_large_square_target_mm"][1]) / 2 >= 0.4
    adapter_w = h["cell_width_mm"] - 2 * i["adapter_clearance_per_side_mm"]
    adapter_d = h["cell_depth_mm"] - 2 * i["adapter_clearance_per_side_mm"]
    assert adapter_w > i["square_capsule_target_mm"][0] + 2 * i["capsule_clearance_per_side_mm"]
    assert adapter_d > i["square_capsule_target_mm"][1] + 2 * i["capsule_clearance_per_side_mm"]


def test_protected_thicknesses_and_support_height():
    h, i = P["host"], P["interfaces"]
    assert h["wall_thickness_mm"] >= 2.4 and h["floor_thickness_mm"] >= 2.4
    assert i["adapter_thickness_mm"] >= 2.4
    assert h["support_top_z_mm"] + i["square_capsule_target_mm"][2] <= h["height_mm"] + 0.5


def test_access_notch_and_label_bay_are_explicit():
    h, i = P["host"], P["interfaces"]
    assert h["front_access_notch_width_mm"] >= 40
    assert h["front_access_notch_floor_z_mm"] < h["support_top_z_mm"] + i["square_capsule_target_mm"][2]
    assert i["label_bay_recess_mm"] <= 0.6
    assert i["adapter_thickness_mm"] - i["label_bay_recess_mm"] - P["watermark"]["engraving_depth_mm"] >= 0.8


def test_contact_and_claim_boundaries():
    s = P["safety"]
    assert s["encapsulated_items_only"] and s["not_archival_or_tarnish_protection"]
    assert s["no_bare_coin_or_medal_contact_claim"] and s["exclude_child_use"]


def test_watermark_tier_contract():
    w = P["watermark"]
    assert w["asset_revision"] == "MM-WM-001-R2"
    assert w["host_tier"] == "full" and w["host_layout_priority"] == 1 and w["host_domain_visible"]
    assert w["adapter_tier"] == "micro" and w["adapter_layout_priority"] == 3 and not w["adapter_domain_visible"]
    assert w["uniform_scale"] == 1.0 and w["rotation_deg"] == 0


def test_supportless_print_contract():
    assert P["printing"]["orientation"] == "base-down"
    assert not P["printing"]["generated_support"]


def test_generated_mesh_and_package_audits_pass():
    reports = [
        "fdm-mesh-host.json",
        "fdm-mesh-square-adapter.json",
        "fdm-mesh-round-adapter.json",
        "fdm-mesh-interface-gauge.json",
        "fdm-mesh-full-watermark-coupon.json",
        "fdm-mesh-micro-watermark-coupon.json",
        "fdm-3mf-square-kit.json",
        "fdm-3mf-round-kit.json",
        "fdm-3mf-gauges.json",
    ]
    assert all(json.loads((ROOT / "validation" / name).read_text())["status"] == "PASS" for name in reports)


def test_exact_slicer_preflight_passes_for_gauge_and_both_kits():
    report = json.loads((ROOT / "validation/slicer-preflight-report.json").read_text())
    assert report["status"] == "PASS"
    assert set(report["metrics"]) == {"fit-label-and-mark-gauges", "square-50-kit", "round-46-kit"}
    assert all(job["peak_flow_mm3_s"] <= 13.3 for job in report["metrics"].values())
    assert all(job["profile_max_volumetric_speed_mm3_s"] == 12.8 for job in report["metrics"].values())


def test_candidate_and_autonomous_approval_chain_pass():
    candidate = json.loads((ROOT / "validation/print-candidate-report.json").read_text())
    approvals = json.loads((ROOT / "validation/approvals-through-print-candidate.json").read_text())
    assert candidate["status"] == "PASS" and candidate["metrics"]["digital_print_candidate"]
    assert approvals["status"] == "PASS"
    assert approvals["metrics"]["stage_state"]["print-candidate"] == "AUTO_APPROVED"


def test_aggregate_draft_validation_passes_with_only_human_gates_deferred():
    aggregate = json.loads((ROOT / "validation/validation-summary.json").read_text())
    assert aggregate["status"] == "PASS" and aggregate["profile"] == "draft"
    reviews = [row for row in aggregate["checks"] if row["status"] == "REVIEW_REQUIRED"]
    assert len(reviews) == 2 and all(not row["required"] for row in reviews)


def test_stock_flow_failure_is_preserved_and_conservative_reslice_passes():
    stock = json.loads((ROOT / "validation/gcode-pla-gauges-run-001.json").read_text())
    conservative = json.loads((ROOT / "validation/gcode-pla-gauges-run-002.json").read_text())
    assert stock["status"] == "FAIL" and stock["metrics"]["peak_flow_mm3_s"] > 13.3
    assert conservative["status"] == "PASS" and conservative["metrics"]["peak_flow_mm3_s"] <= 13.3
    assert conservative["metrics"]["peak_flow_mm3_s"] < stock["metrics"]["peak_flow_mm3_s"]
