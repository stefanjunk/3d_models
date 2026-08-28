import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMS = json.loads((ROOT / "config/model-parameters.json").read_text())


def load_build():
    spec = importlib.util.spec_from_file_location("mm_org_022_build", ROOT / "cad/build.py")
    build = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(build)
    return build


def test_bin_presets_are_original_measurement_driven_widths():
    assert [(item["id"], item["outer_width_mm"]) for item in PARAMS["bins"]] == [("narrow", 45.0), ("medium", 67.5), ("wide", 90.0)]
    assert "gridfinity" not in json.dumps(PARAMS).lower()


def test_electronics_rows_tile_exactly():
    widths = {item["id"]: item["outer_width_mm"] for item in PARAMS["bins"]}
    row = PARAMS["carrier"]["packing_width_mm"]
    assert 4 * widths["narrow"] == row
    assert widths["wide"] + 2 * widths["narrow"] == row


def test_sewing_row_tiles_exactly():
    widths = {item["id"]: item["outer_width_mm"] for item in PARAMS["bins"]}
    assert 2 * widths["medium"] + widths["narrow"] == PARAMS["carrier"]["packing_width_mm"]


def test_all_bins_are_valid_single_solids():
    build = load_build()
    for preset in PARAMS["bins"]:
        shape, interface = build.make_bin(PARAMS, preset)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert interface["external_assets"] == []


def test_open_carrier_is_valid_and_exact():
    build = load_build()
    shape, interface = build.make_carrier(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["open_floor"] is True
    assert interface["outer_dimensions_mm"] == [186.0, 156.0, 4.0]


def test_label_slot_gauge_brackets_target():
    build = load_build()
    shape, interface = build.make_label_slot_gauge(PARAMS)
    assert shape.isValid()
    assert len(shape.Solids()) == 1
    assert interface["slot_gaps_mm"] == [0.5, 0.7, 0.9]
    assert interface["identity_holes"] == [1, 2, 3]


def test_label_card_is_thinner_than_target_slot():
    bin_p = PARAMS["bin"]
    assert bin_p["paper_card_thickness_max_mm"] == 0.4
    assert bin_p["paper_card_thickness_max_mm"] < bin_p["label_slot_gap_mm"]


def test_pickup_geometry_is_local_and_bounded():
    bin_p = PARAMS["bin"]
    assert [bin_p["scoop_depth_mm"], bin_p["scoop_rise_mm"]] == [13.0, 7.0]
    assert bin_p["scoop_depth_mm"] < bin_p["outer_depth_mm"] / 4
    assert bin_p["scoop_rise_mm"] < bin_p["outer_height_mm"] / 3


def test_shell_uses_four_lines_and_nine_layers():
    assert PARAMS["bin"]["wall_mm"] / PARAMS["printer"]["line_width_mm"] == 4
    assert PARAMS["bin"]["floor_mm"] / PARAMS["printer"]["layer_height_mm"] == 9


def test_every_part_fits_portfolio_envelope():
    build = load_build()
    interfaces = [build.make_bin(PARAMS, preset)[1] for preset in PARAMS["bins"]]
    interfaces += [build.make_carrier(PARAMS)[1], build.make_label_slot_gauge(PARAMS)[1]]
    assert all(item["outer_dimensions_mm"][0] <= 220 and item["outer_dimensions_mm"][1] <= 160 and item["outer_dimensions_mm"][2] <= 140 for item in interfaces)


def test_pilot_quantities_fill_declared_rows():
    bins = {item["id"]: item for item in PARAMS["bins"]}
    assert (bins["narrow"]["quantity_electronics"], bins["wide"]["quantity_electronics"]) == (6, 1)
    assert (bins["narrow"]["quantity_sewing"], bins["medium"]["quantity_sewing"]) == (2, 4)


def test_small_parts_and_electrical_boundaries_are_explicit():
    contract = PARAMS["workflow_contract"]
    assert contract["pilot_use_cases"] == ["unpowered_electronic_components", "adult_sewing_notions"]
    assert contract["small_parts_warning"] == "adult_storage_only_not_child_directed"
    assert contract["electrical_claim"] == "passive_storage_only_no_batteries_or_energized_parts"
