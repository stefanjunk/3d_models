import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_023_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_three_presets_are_measurement_driven():
    assert [(item["id"], item["opening_major_mm"], item["opening_minor_mm"]) for item in PARAMS["presets"]] == [
        ("small", 20.0, 16.5), ("medium", 23.0, 19.0), ("large", 26.0, 21.5)
    ]


def test_spans_increase_with_opening_size():
    assert [item["span_mm"] for item in PARAMS["presets"]] == [82.0, 92.0, 102.0]


def test_all_holders_are_valid_single_solids():
    build = load_build()
    for preset in PARAMS["presets"]:
        shape, interface = build.make_holder(PARAMS, preset)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert interface["external_assets"] == []


def test_guide_is_one_valid_solid_and_matches_openings():
    build = load_build()
    shape, interface = build.make_sizing_guide(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["openings_obround_mm"] == [[20.0, 16.5], [23.0, 19.0], [26.0, 21.5]]


def test_ring_wall_is_ten_mm_for_every_preset():
    build = load_build()
    for preset in PARAMS["presets"]:
        _, interface = build.make_holder(PARAMS, preset)
        assert interface["minimum_ring_wall_mm"] == 10.0


def test_comfort_edges_are_bounded():
    assert PARAMS["holder"]["body_edge_radius_mm"] == 1.0
    assert PARAMS["gauge"]["comfort_edge_radius_mm"] == 0.8
    assert PARAMS["holder"]["body_edge_radius_mm"] < PARAMS["holder"]["body_thickness_mm"] / 2


def test_page_contact_is_two_local_pads():
    build = load_build()
    for preset in PARAMS["presets"]:
        _, interface = build.make_holder(PARAMS, preset)
        assert interface["page_pads"] == 2
        assert interface["page_pad_mm"] == [24.0, 12.0, 0.8]


def test_layer_and_line_dimensions_are_integral():
    assert PARAMS["holder"]["body_thickness_mm"] / PARAMS["printer"]["layer_height_mm"] == 25
    assert PARAMS["holder"]["page_pad_height_mm"] / PARAMS["printer"]["layer_height_mm"] == 4
    assert PARAMS["holder"]["wing_depth_mm"] / PARAMS["printer"]["line_width_mm"] == 40


def test_all_parts_fit_product_envelope():
    build = load_build()
    for preset in PARAMS["presets"]:
        dims = build.holder_dimensions(PARAMS, preset)
        assert dims[0] <= 120 and dims[1] <= 60 and dims[2] <= 20
    _, guide = build.make_sizing_guide(PARAMS)
    assert guide["outer_dimensions_mm"] == [96.0, 34.0, 3.0]


def test_print_orientation_is_support_free_contract():
    build = load_build()
    for preset in PARAMS["presets"]:
        _, interface = build.make_holder(PARAMS, preset)
        assert interface["print_orientation"] == "broad_face_down_pads_up"


def test_physical_book_and_comfort_gates_are_explicit():
    contract = PARAMS["workflow_contract"]
    assert contract["required_book_classes"] == ["small_paperback", "large_paperback", "hardcover"]
    assert contract["comfort_sample_minutes"] == 10
    assert contract["handling_cycles"] == 100


def test_claim_boundaries_reject_universal_or_medical_scope():
    contract = PARAMS["workflow_contract"]
    assert contract["ergonomic_claim"] == "sizing_aid_only_no_medical_or_universal_fit_claim"
    assert contract["book_claim"] == "page_positioning_aid_no_binding_or_paper_protection_claim"


def test_final_manufacturing_meshes_respect_triangle_budget():
    report = json.loads((ROOT / "validation/mesh-generation-report.json").read_text())
    assert report["status"] == "PASS"
    assert max(item["triangles"] for item in report["metrics"]["meshes"].values()) <= 60000
    assert PARAMS["mesh"]["linear_deflection_mm"] == 0.10
    assert PARAMS["mesh"]["angular_deflection_rad"] == 0.18
