import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / "config/model-parameters.json").read_text())


def test_identity_and_envelope():
    assert P["project"] == {"id": "MM-ORG-037", "revision": "0.1.0-draft.1", "units": "mm"}
    c = P["cassette"]
    assert c["width_mm"] <= 220 and c["depth_mm"] <= 220 and c["height_mm"] <= 45


def test_protected_thicknesses():
    c = P["cassette"]
    assert c["base_thickness_mm"] >= 2.4
    assert c["wall_thickness_mm"] >= 2.4
    assert c["foot_divider_thickness_mm"] >= 2.0


def test_declared_capacity_and_generic_cells():
    c = P["cassette"]
    assert c["foot_columns"] * c["foot_rows"] == 10
    assert P["bobbin_inserts"]["pocket_count"] == 7
    assert P["gauges"]["foot_cell"]["cell_widths_mm"] == [30.0, 35.0, 40.0]


def test_two_bobbin_standards_are_distinct_and_bounded():
    standards = P["bobbin_inserts"]["standards"]
    assert standards["cb_20p5"]["nominal_diameter_mm"] == 20.5
    assert standards["horizontal_21p6"]["nominal_diameter_mm"] == 21.6
    assert standards["cb_20p5"]["index_bars"] == 1
    assert standards["horizontal_21p6"]["index_bars"] == 2
    assert P["bobbin_inserts"]["diametral_clearance_mm"] == 0.8


def test_insert_clearance_is_explicit():
    c = P["cassette"]
    i = P["bobbin_inserts"]
    inner_width = c["width_mm"] - 2 * c["wall_thickness_mm"]
    assert round((inner_width - i["width_mm"]) / 2, 3) == 0.4
    assert round((c["rear_bobbin_bay_depth_mm"] - i["depth_mm"]) / 2, 3) == 0.4


def test_full_watermark_contract():
    mark = P["watermark"]
    assert mark["asset_revision"] == "MM-WM-001-R2"
    assert mark["selected_tier"] == "full" and mark["layout_priority"] == 1
    assert mark["domain_visible"] and mark["uniform_scale"] == 1.0
    assert mark["land_width_mm"] >= 79.936 + 2 * mark["edge_clearance_mm"]
    assert mark["land_depth_mm"] >= 12.8 + 2 * mark["edge_clearance_mm"]
    assert P["cassette"]["base_thickness_mm"] - mark["engraving_depth_mm"] >= 0.8


def test_all_digital_mesh_and_package_reports_pass():
    names = [
        "fdm-mesh-cassette.json",
        "fdm-mesh-cb-insert.json",
        "fdm-mesh-horizontal-insert.json",
        "fdm-mesh-bobbin-gauge.json",
        "fdm-mesh-foot-gauge.json",
        "fdm-mesh-watermark-coupon.json",
        "fdm-3mf-cb-kit.json",
        "fdm-3mf-horizontal-kit.json",
        "fdm-3mf-gauges.json",
    ]
    assert all(json.loads((ROOT / "validation" / name).read_text())["status"] == "PASS" for name in names)


def test_exact_slicer_jobs_and_independent_flow_scope_pass():
    report = json.loads((ROOT / "validation/slicer-preflight-report.json").read_text())
    assert report["status"] == "PASS"
    assert set(report["metrics"]) == {"fit-gauges", "cb-kit", "horizontal-kit"}
    assert all(row["status"] == "PASS" for row in report["checks"] if row["id"].endswith(("macro-flow", "rounded-coordinate-flow-scope")))
    assert max(job["independent_macro_peak"]["flow_mm3_s"] for job in report["metrics"].values()) <= 13.3


def test_print_candidate_and_aggregate_validation_pass():
    candidate = json.loads((ROOT / "validation/print-candidate-report.json").read_text())
    summary = json.loads((ROOT / "validation/validation-summary.json").read_text())
    approvals = json.loads((ROOT / "validation/approvals-through-print-candidate.json").read_text())
    assert candidate["status"] == "PASS" and candidate["metrics"]["digital_print_candidate"]
    assert summary["status"] == "PASS"
    assert approvals["status"] == "PASS"


def test_bobbin_gauge_and_final_insert_targets_share_one_contract():
    interface = json.loads((ROOT / "validation/interface-report.json").read_text())
    clearance = P["bobbin_inserts"]["diametral_clearance_mm"]
    for standard_id, metric_id in (("cb_20p5", "cb_insert"), ("horizontal_21p6", "horizontal_insert")):
        nominal = P["bobbin_inserts"]["standards"][standard_id]["nominal_diameter_mm"]
        assert round(interface["metrics"][metric_id]["pocket_diameter_mm"], 6) == round(nominal + clearance, 6)
    assert next(row for row in interface["checks"] if row["id"] == "physical-gauges")["status"] == "PASS"
