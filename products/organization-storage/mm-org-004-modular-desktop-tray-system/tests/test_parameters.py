import importlib.util
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mm_org_004_build", ROOT / "cad" / "build.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_default_parameter_contract():
    params = MODULE.load_params()
    MODULE.validate_parameters(params)


def test_declared_interface_clearance():
    interface = MODULE.load_params()["interface"]
    socket_head = interface["link_head_width"] + 2.0 * interface["clearance_each_side"]
    assert abs((socket_head - interface["link_head_width"]) / 2.0 - 0.30) < 1e-9


def test_boundary_shell_contract():
    params = MODULE.load_params()
    params["shell"]["wall"] = 2.25
    params["shell"]["floor"] = 2.20
    MODULE.validate_parameters(params)
