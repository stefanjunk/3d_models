import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mm_org_005", ROOT / "cad" / "build.py")
MODULE = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(MODULE)

def test_default_contract():
    p = MODULE.load_params(); MODULE.validate_parameters(p)

def test_input_limits():
    p = MODULE.load_params(); lo=p["input_limits"]
    assert MODULE.custom_variant(p,lo["desk_min"],lo["cable_min"])["jaw_gap"] == 8.0
    assert MODULE.custom_variant(p,lo["desk_max"],lo["cable_max"])["jaw_gap"] == 15.6

def test_default_envelopes():
    p=MODULE.load_params(); limit=p["manufacturing_envelope"]
    for variant in p["variants"].values():
        shape=MODULE.print_orientation(MODULE.make_clip(variant,p)); b=shape.BoundingBox()
        assert all(a <= z + 0.05 for a,z in zip((b.xlen,b.ylen,b.zlen),limit))
