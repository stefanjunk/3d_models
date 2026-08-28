import math

from submarine.surfacing import FishEnvelopeProfile


def test_profile_stays_outside_immutable_core(cfg):
    profile = FishEnvelopeProfile(cfg)
    for region, guide in (
        ("nose", profile.nose),
        ("chain", profile.chain),
        ("capsule", profile.capsule),
    ):
        for i in range(81):
            x = guide.x0 + i * (guide.x1 - guide.x0) / 80.0
            ry, rz = profile.radii(region, x)
            core = profile.core_radius(region, x)
            assert min(ry, rz) >= core
            assert math.isfinite(ry) and math.isfinite(rz)


def test_natural_cubic_guides_are_c2_at_internal_knots(cfg):
    profile = FishEnvelopeProfile(cfg)
    for guide in (profile.nose, profile.chain, profile.capsule):
        for spline in (guide.width, guide.height):
            for x in spline.xs[1:-1]:
                eps = 1e-6 * (guide.x1 - guide.x0)
                assert abs(spline.value(x - eps) - spline.value(x + eps)) < 1e-4
                assert abs(spline.derivative(x - eps) - spline.derivative(x + eps)) < 1e-4
                assert abs(spline.second(x - eps) - spline.second(x + eps)) < 1e-4


def test_neutral_region_boundaries_match(cfg):
    profile = FishEnvelopeProfile(cfg)
    nose_end = profile.radii("nose", cfg.nose_length)
    chain_start = profile.radii("chain", cfg.nose_length)
    assert max(abs(a - b) for a, b in zip(nose_end, chain_start)) <= 1.0
