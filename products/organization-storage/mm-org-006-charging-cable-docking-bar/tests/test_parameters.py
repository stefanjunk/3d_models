import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; S=importlib.util.spec_from_file_location("mm_org_006",ROOT/"cad/build.py"); M=importlib.util.module_from_spec(S); assert S.loader; S.loader.exec_module(M)
def test_default_contract(): p=M.load_params(); M.validate_parameters(p)
def test_interface_math():
    p=M.load_params(); s=p["socket"]; assert abs((s["insert_length"]+2*s["clearance_each"]-s["insert_length"])/2-.25)<1e-9
def test_default_geometry_envelope():
    p=M.load_params(); b=p["bar"]; bar=M.make_bar(b["length"],b["socket_count"],p); bb=bar.BoundingBox(); assert bb.xlen<=180 and bb.ylen<=45 and bb.zlen<=25
    for d in p["insert"]["cable_diameters"]: assert len(M.make_insert(d,p).Solids())==1
def test_boundary_custom():
    p=M.load_params(); M.validate_custom(p,180,5,[9,9,9,9,9]); assert M.make_bar(180,5,p).BoundingBox().xlen<=180
