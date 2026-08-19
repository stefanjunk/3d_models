from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cq = pytest.importorskip("cadquery")
block = load_module("block_mold", ROOT / "scripts" / "cadquery" / "block_mold.py")
coupon = load_module("detail_coupon", ROOT / "scripts" / "cadquery" / "detail_coupon.py")


def test_demo_block_parts_are_valid() -> None:
    master = block.center_and_scale(block.demo_master("roman-pillar", 40.0), (1.0, 1.0, 1.0))
    outer, dims = block.make_block(master, 8.0, 6.0, 10.0)
    complete = outer.cut(master)
    a, b = block.split_shape(complete, dims, "X")
    a, b, positions = block.add_keys(a, b, master, dims, "X", 8.0, 3.0, 2.0, 0.2)
    assert a.isValid()
    assert b.isValid()
    assert len(positions) == 4
    assert a.Volume() > 0
    assert b.Volume() > 0


def test_detail_coupon_and_negative_are_valid() -> None:
    master, features = coupon.build_coupon(
        80.0, 50.0, 3.0,
        [0.4, 0.8, 1.2],
        [0.2, 0.4, 0.6],
        curved=True,
        sag=5.0,
    )
    tray = coupon.make_negative_tray(master, 5.0, 4.0)
    assert master.isValid()
    assert tray.isValid()
    assert len(features) == 3
    assert tray.Volume() > master.Volume()
