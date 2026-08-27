import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location('build',ROOT/'cad/build.py'); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
def p(): return json.loads((ROOT/'config/model-parameters.json').read_text())
def test_defaults(): b.validate(p())
def test_envelope(): assert b.dims(p())==(161,107)
def test_reject_bad_count():
 q=p(); q['grid']['diameters']=q['grid']['diameters'][:-1]
 try: b.validate(q)
 except AssertionError: return
 assert False
