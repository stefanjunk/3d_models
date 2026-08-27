from submarine.buoyancy import compute_buoyancy
from submarine.preflight import PartCheck, run_preflight


def _volumes(parts):
    env = {n: p.envelope.val().Volume() for n, p in parts.items() if p.envelope}
    mass = {n: p.solid.val().Volume() for n, p in parts.items()}
    return env, mass


def test_buoyancy_feasible(cfg, parts):
    env, mass = _volumes(parts)
    rep = compute_buoyancy(cfg, env, mass)
    assert rep.displacement_ml > 300
    assert rep.required_ballast_g > 0
    assert rep.keel_ballast_g + rep.box_ballast_g >= rep.required_ballast_g - 1e-6
    assert rep.bladder_range_g >= 4.0
    assert rep.dry_mass_g < rep.displacement_mid_bladder_ml


def test_preflight_passes(cfg, parts):
    env, mass = _volumes(parts)
    rep = compute_buoyancy(cfg, env, mass)
    checks = [
        PartCheck(name, (0, 0, 0), watertight_expected=p.watertight, watertight_actual=True)
        for name, p in parts.items()
    ]
    report = run_preflight(cfg, rep, [], checks)
    assert report["pass"]
