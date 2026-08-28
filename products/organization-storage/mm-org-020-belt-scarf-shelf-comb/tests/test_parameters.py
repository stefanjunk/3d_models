import importlib.util
import json
from pathlib import Path
import trimesh


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_020_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_presets_encode_measured_roll_envelopes():
    assert [item["id"] for item in PARAMS["presets"]] == ["belt-four", "scarf-three"]
    assert PARAMS["workflow_contract"]["input_dimensions"] == ["shelf_depth", "maximum_roll_diameter", "item_count", "label_preference"]


def test_clear_width_brackets_intended_roll_diameter():
    for preset in PARAMS["presets"]:
        assert preset["clear_slot_width_mm"] - preset["intended_roll_diameter_max_mm"] >= 2.0


def test_both_combs_are_valid_single_solids():
    build = load_build()
    for preset in PARAMS["presets"]:
        shape, interface = build.make_comb(PARAMS, preset)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert interface["label_fields"] == preset["slot_count"]


def test_textile_facing_radii_are_exact_and_bounded():
    comb = PARAMS["comb"]
    assert comb["leading_edge_radius_mm"] == 1.4
    assert comb["top_edge_radius_mm"] == 1.2
    assert 2.0 * comb["leading_edge_radius_mm"] < comb["divider_thickness_mm"]
    assert 2.0 * comb["top_edge_radius_mm"] < comb["divider_thickness_mm"]


def test_open_floor_is_retained_by_two_low_rails():
    comb = PARAMS["comb"]
    assert comb["front_rail_depth_mm"] < comb["depth_mm"] / 4.0
    assert comb["rear_rail_depth_mm"] < comb["depth_mm"] / 4.0
    assert comb["front_rail_height_mm"] < comb["divider_height_mm"] / 3.0


def test_shared_module_connector_datums_are_absolute():
    assert PARAMS["connector"]["centers_y_mm"] == [28.0, 77.0]
    assert PARAMS["connector"]["default_clearance_mm"] == 0.25
    build = load_build()
    interfaces = [build.make_comb(PARAMS, preset)[1] for preset in PARAMS["presets"]]
    assert interfaces[0]["joint_centers_y_mm"] == interfaces[1]["joint_centers_y_mm"]


def test_fabric_coupon_brackets_production_radius():
    coupon = PARAMS["coupon"]
    assert coupon["leading_radii_mm"] == [0.6, 1.0, 1.4]
    assert coupon["leading_radii_mm"][-1] == PARAMS["comb"]["leading_edge_radius_mm"]
    shape, interface = load_build().make_edge_coupon(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["identity_holes"] == [1, 2, 3]


def test_connector_key_is_a_valid_single_solid():
    shape, interface = load_build().make_connector_key(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["height_mm"] == PARAMS["comb"]["base_thickness_mm"]


def test_every_comb_fits_portfolio_envelope():
    build = load_build()
    for preset in PARAMS["presets"]:
        extent = build.make_comb(PARAMS, preset)[1]["outer_dimensions_mm"]
        assert extent[0] <= 220.0 and extent[1] <= 120.0 and extent[2] <= 100.0


def test_base_and_connector_use_whole_reference_layers():
    layer = PARAMS["printer"]["layer_height_mm"]
    assert PARAMS["comb"]["base_thickness_mm"] / layer == 15
    assert PARAMS["connector"]["height_mm"] / layer == 15


def test_physical_fabric_gate_is_explicitly_deferred():
    contract = PARAMS["workflow_contract"]
    assert contract["required_fabrics"] == ["smooth_woven", "knit", "loosely_woven_or_fringe"]
    assert contract["minimum_items_per_preset"] == 3
    assert contract["retrieval_cycles"] == 100
    assert contract["load_claim"] == "none_dry_soft_goods_only"


def test_no_generated_part_uses_external_assets():
    build = load_build()
    interfaces = [build.make_comb(PARAMS, preset)[1] for preset in PARAMS["presets"]]
    interfaces += [build.make_edge_coupon(PARAMS)[1], build.make_connector_key(PARAMS)[1]]
    assert all(item["external_assets"] == [] for item in interfaces)


def test_exported_textile_coupon_has_no_degenerate_facets_or_fragments():
    path = ROOT / "exports/coupons/DRAFT-MM-ORG-020-edge-radius-coupon-0.1.0-draft.1.stl"
    mesh = trimesh.load_mesh(path, force="mesh", process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert len(mesh.split(only_watertight=False)) == 1
    assert bool(mesh.nondegenerate_faces().all())
    assert bool(mesh.unique_faces().all())
