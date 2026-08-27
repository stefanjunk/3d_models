import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "config/model-parameters.json"
SPEC = importlib.util.spec_from_file_location("mm_org_013_build", ROOT / "cad/build.py")
BUILD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILD)


def parameters() -> dict:
    return json.loads(PARAMETERS.read_text(encoding="utf-8"))


def test_default_parameter_contract() -> None:
    BUILD.validate_parameters(parameters())


def test_three_required_media_formats() -> None:
    data = parameters()
    values = {item["id"]: (item["long_edge"], item["short_edge"]) for item in data["media_formats"]}
    assert values == {"photo-10x15": (150.0, 100.0), "postcard-a6": (148.0, 105.0), "photo-13x18": (180.0, 130.0)}


def test_active_media_has_two_millimetres_total_long_edge_allowance() -> None:
    data = parameters()
    frame_shape, metrics = BUILD.make_frame(data)
    assert frame_shape.isValid()
    assert metrics["active_media_total_clearance_mm"] == 2.0
    assert metrics["active_media_clear_width_mm"] == metrics["active_media_long_edge_mm"] + 2.0


def test_slot_web_and_fit_contract() -> None:
    data = parameters()
    dims = BUILD.derived(data)
    assert dims["slot_width"] == 2.6
    assert min(data["frame"]["slot_positions"][i + 1] - data["frame"]["slot_positions"][i] for i in range(9)) - dims["slot_width"] >= data["limits"]["minimum_slot_web"]


def test_every_default_divider_is_valid_and_legible() -> None:
    data = parameters()
    for label in data["divider"]["labels"]:
        shape, metrics = BUILD.make_divider(data, label)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert metrics["tab_width_mm"] >= metrics["label_width_mm"] + 1.0
        assert metrics["label_pixel_mm"] >= data["limits"]["minimum_label_pixel"]


def test_every_format_gauge_matches_declared_allowance() -> None:
    data = parameters()
    for media in data["media_formats"]:
        shape, metrics = BUILD.make_format_gauge(data, media)
        assert shape.isValid()
        assert len(shape.Solids()) == 1
        assert metrics["gauge_clear_mm"] == [media["long_edge"] + 2.0, media["short_edge"] + 2.0]


def test_installed_geometry_respects_part_height_limit() -> None:
    data = parameters()
    dims = BUILD.derived(data)
    assert dims["installed_bottom_z"] + data["divider"]["tab_height"] <= data["limits"]["maximum_part_envelope"][2]


def test_boundary_rejects_unreadable_label_pixels() -> None:
    data = parameters()
    data["divider"]["label_pixel_fill"] = 0.5
    try:
        BUILD.validate_parameters(data)
    except AssertionError:
        return
    raise AssertionError("undersized label pixels must fail closed")
