from submarine.config import SubmarineConfig


def test_wall_thick_enough():
    cfg = SubmarineConfig()
    assert cfg.wall >= 3 * cfg.nozzle


def test_clearances_positive():
    cfg = SubmarineConfig()
    assert cfg.hinge_clearance >= 0.15
    assert cfg.pivot_clearance >= 0.15


def test_mechanical_library_interfaces():
    cfg = SubmarineConfig()
    # Local library samples 002 and 078, standard PETG/0.4 mm variants.
    assert cfg.hinge_pin_d == 4.0
    assert cfg.hinge_clearance == 0.25
    assert cfg.cap_bayonet_clearance == 0.30
    squeeze = (
        cfg.capsule_inner_r
        - cfg.cap_bayonet_clearance
        - cfg.cap_oring_groove_depth
        + cfg.cap_oring_cs
        - cfg.capsule_inner_r
    )
    assert 0.15 <= squeeze <= 0.25


def test_layout_chain():
    cfg = SubmarineConfig()
    assert cfg.capsule_start_x == cfg.nose_length + cfg.n_segments * cfg.segment_length
    assert cfg.capsule_end_x > cfg.capsule_start_x


def test_bore_fits_piston():
    cfg = SubmarineConfig()
    assert cfg.bladder_rod_d < cfg.bladder_bore_d
    # o-ring must protrude beyond the rod to squeeze in the bore
    protrusion = (cfg.bladder_rod_d / 2 - 1.1 + 1.5) - cfg.bladder_bore_d / 2
    assert 0.1 <= protrusion <= 0.6


def test_fish_ribs_are_printable():
    cfg = SubmarineConfig()
    minimum_diameter = 2 * cfg.fish_rib_end_radius * cfg.fish_rib_lateral_scale
    assert minimum_diameter >= 3 * cfg.nozzle
    assert 0 < cfg.fish_rib_overlap < cfg.fish_rib_end_radius * cfg.fish_rib_lateral_scale
    assert all(abs(angle) <= 90 for angle in cfg.fish_rib_angles_deg)
