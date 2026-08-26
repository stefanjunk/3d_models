import math

from submarine.config import SubmarineConfig
from submarine.mechanism import solve_rocker, validate_rocker


def test_sweep_in_band():
    sol = solve_rocker(SubmarineConfig())
    assert 15.0 <= sol.sweep_deg <= 70.0


def test_slot_covers_crank():
    cfg = SubmarineConfig()
    sol = solve_rocker(cfg)
    d = cfg.rocker_offset_z
    assert sol.slot_r_start <= d - cfg.crank_r - 1
    assert sol.slot_r_end >= d + cfg.crank_r + 1
    assert sol.slot_r_end < cfg.rocker_arm_tip_r


def test_no_problems():
    assert validate_rocker(SubmarineConfig()) == []
