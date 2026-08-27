import importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('m',R/'cad/build.py');M=importlib.util.module_from_spec(S);assert S.loader;S.loader.exec_module(M)
def test_contract():p=M.load_params();M.validate_parameters(p)
def test_parts():
 p=M.load_params();assert all(len(M.make_base(k,p).Solids())==1 for k in p['detent']['profiles']);assert len(M.make_backrest(p).Solids())==1;assert len(M.make_pin(p).Solids())==1
def test_hinge_clearance():p=M.load_params();h=p['hinge'];assert abs((h['pin_diameter']+2*h['radial_clearance']-h['pin_diameter'])/2-.25)<1e-9
