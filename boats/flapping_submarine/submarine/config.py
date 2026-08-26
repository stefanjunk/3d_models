"""Parametric toy submarine with flapping tail.

Frame convention (world): +X points from the nose toward the tail (aft),
+Z is up, +Y to starboard. Units: millimetres unless noted.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class SubmarineConfig:
    """Single source of truth for all dimensions and allowances."""

    # hull chain (nose -> segments -> capsule)
    n_segments: int = 4
    segment_length: float = 36.0
    hull_od_front: float = 42.0
    hull_od_rear: float = 36.0
    nose_length: float = 50.0
    nose_dome: float = 18.0
    capsule_od: float = 44.0
    capsule_length: float = 115.0
    wall: float = 2.4
    rear_wall: float = 3.0

    # library reference 078: standard PETG bayonet running clearance
    cap_bayonet_clearance: float = 0.30
    cap_oring_cs: float = 1.50
    cap_oring_groove_depth: float = 1.00

    # aesthetic envelope: fair longitudinal ribs, 0 deg = dorsal (+Z)
    fish_ribs_enabled: bool = True
    fish_rib_angles_deg: tuple[float, ...] = (0.0, 45.0, -45.0, 90.0, -90.0)
    fish_rib_peak_radius: float = 1.40
    fish_rib_end_radius: float = 0.80
    fish_rib_overlap: float = 0.65
    fish_rib_end_margin: float = 1.50
    fish_rib_dorsal_scale: float = 1.15
    fish_rib_lateral_scale: float = 0.90

    # displacement bladder (friction piston, adjustable displacement)
    bladder_tube_od: float = 25.0
    bladder_bore_d: float = 21.2
    bladder_protrude: float = 26.0
    bladder_inner_len: float = 45.0  # bore tube length inside the nose, from tip
    bladder_rod_d: float = 20.6
    bladder_rod_len: float = 63.0
    bladder_travel: float = 20.0
    bladder_knob_d: float = 30.0
    bladder_knob_h: float = 9.0
    bladder_oring_cs: float = 1.5

    # hinge (axis vertical Z, side-by-side ears, inserted pin)
    hinge_pin_d: float = 4.0
    hinge_bore_d: float = 4.5
    hinge_clearance: float = 0.25  # library reference 002: standard PETG variant
    ear_t: float = 5.0
    tongue_t: float = 5.0
    lug_len: float = 13.0
    hinge_flex_deg: float = 10.0

    # motor (N20 gearmotor ~3 V)
    motor_d: float = 12.0
    motor_len: float = 15.0
    motor_shaft_d: float = 3.0

    # crank / slotted rocker mechanism
    crank_r: float = 6.0
    crank_disc_d: float = 22.0
    crank_disc_t: float = 5.0
    crank_pin_d: float = 4.0
    rocker_offset_z: float = 16.0  # pivot height above shaft axis
    rocker_t: float = 4.0
    rocker_slot_w: float = 6.0
    rocker_arm_tip_r: float = 46.0
    pivot_pin_d: float = 4.0
    pivot_clearance: float = 0.25

    # tail fin
    fin_length: float = 55.0
    fin_depth: float = 30.0
    fin_t: float = 2.8

    # gland (motor shaft seal: o-ring seated in the boss bore)
    gland_boss_d: float = 13.0
    gland_flange_t: float = 2.0
    gland_boss_len: float = 3.5
    gland_bore_d: float = 3.4
    gland_oring_cs: float = 1.5
    gland_oring_depth: float = 2.0  # o-ring ring centre behind boss face

    # keel ballast pocket under capsule
    keel_l: float = 70.0
    keel_w: float = 22.0
    keel_h: float = 18.0
    keel_wall: float = 2.0
    keel_plug_d: float = 12.0
    keel_plug_pitch: float = 1.5

    # internal ballast box (coins)
    ballast_box_l: float = 26.0
    ballast_box_w: float = 22.0
    ballast_box_h: float = 24.0

    # print + physics
    nozzle: float = 0.4
    print_bed: tuple[float, float, float] = (220.0, 220.0, 250.0)
    rho_print: float = 1.27  # PETG g/cm^3
    rho_water: float = 1.00
    rho_shot_fill: float = 4.4  # steel shot + epoxy mix, g/cm^3
    rho_coin_fill: float = 3.9  # loose coins, g/cm^3
    motor_mass_g: float = 12.0
    battery_mass_g: float = 23.0  # 2x AAA
    misc_mass_g: float = 7.0  # reed switch, wires, o-rings, grease, zip ties
    target_submergence: float = 0.98

    def to_dict(self) -> dict:
        d = asdict(self)
        d["print_bed"] = list(self.print_bed)
        return d

    # derived -----------------------------------------------------
    @property
    def capsule_inner_r(self) -> float:
        return self.capsule_od / 2 - self.wall

    def hull_od(self, x: float, x0: float, x1: float) -> float:
        """Linear hull OD between hinge rows x0..x1."""
        t = (x - x0) / (x1 - x0)
        return self.hull_od_front + (self.hull_od_rear - self.hull_od_front) * t

    @property
    def segment_start_x(self) -> float:
        return self.nose_length

    @property
    def capsule_start_x(self) -> float:
        return self.nose_length + self.n_segments * self.segment_length

    @property
    def capsule_end_x(self) -> float:
        return self.capsule_start_x + self.capsule_length

    @property
    def keel_center_x(self) -> float:
        return self.capsule_start_x + 52.0

    def segment_bounds(self, i: int) -> tuple[float, float]:
        x0 = self.nose_length + i * self.segment_length
        return x0, x0 + self.segment_length
