from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("caddy_build", ROOT / "cad/build.py")
BUILD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILD)


def parameters() -> dict:
    return json.loads((ROOT / "config/model-parameters.json").read_text(encoding="utf-8"))


def test_default_parameters_pass() -> None:
    BUILD.validate_parameters(parameters())


def test_german_name_is_deterministically_transliterated() -> None:
    assert BUILD.sanitize_name("Jörg Weiß", parameters()) == "JOERG WEISS"


def test_unsupported_character_fails_closed() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        BUILD.sanitize_name("MIA!", parameters())


def test_overlength_name_fails_closed() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        BUILD.sanitize_name("ABCDEFGHIJKLMNOPQ", parameters())


def test_sixteen_character_name_keeps_printable_pixels() -> None:
    p = parameters()
    layout = BUILD.text_layout("ABCDEFGHIJKLMNOP", p["nameplate"])
    assert layout["pixel_width"] >= p["nameplate"]["minimum_pixel_width"]


def test_nominal_phone_slot_has_declared_clearance() -> None:
    caddy = parameters()["caddy"]
    gap = caddy["phone_backrest_y"] - (caddy["phone_front_lip_y"] + caddy["wall_thickness"])
    assert gap >= caddy["maximum_phone_case_thickness"] + 0.5


def test_default_geometry_is_valid_and_single_solid() -> None:
    p = parameters()
    body = BUILD.make_caddy(p)
    plate, _ = BUILD.make_text_plate(p, p["personalization"]["name"])
    assert body.isValid() and len(body.Solids()) == 1
    assert plate.isValid() and len(plate.Solids()) == 1


def test_coupon_uses_production_channel_parameters() -> None:
    p = parameters()
    holder, plate, layout = BUILD.make_fit_coupon(p)
    assert holder.isValid() and len(holder.Solids()) == 1
    assert plate.isValid() and len(plate.Solids()) == 1
    assert layout["nominal_front_clearance_mm"] == p["nameplate"]["channel_clearance"]
