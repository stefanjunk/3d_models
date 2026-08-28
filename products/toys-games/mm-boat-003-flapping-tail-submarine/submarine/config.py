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

    # aesthetic envelope: additive fairing around the immutable pressure core.
    # Profile rows are (normalized longitudinal station, half-width Y,
    # half-height Z). 0 deg crest angle = dorsal (+Z).
    fish_fairing_enabled: bool = True
    fish_registered_sections: int = 5
    fish_fairing_overlap: float = 0.35
    fish_nose_profile: tuple[tuple[float, float, float], ...] = (
        (0.00, 12.50, 12.50),
        (0.16, 14.50, 14.80),
        (0.34, 17.00, 17.50),
        (0.58, 21.50, 22.50),
        (0.80, 22.00, 23.00),
        (1.00, 22.00, 22.80),
    )
    fish_chain_profile: tuple[tuple[float, float, float], ...] = (
        (0.00, 22.00, 22.80),
        (0.25, 22.40, 23.40),
        (0.50, 22.80, 24.00),
        (0.75, 23.10, 24.40),
        (1.00, 22.50, 22.80),
    )
    fish_capsule_profile: tuple[tuple[float, float, float], ...] = (
        (0.00, 22.00, 22.00),
        (0.12, 22.30, 22.80),
        (0.35, 23.50, 24.80),
        (0.55, 24.00, 25.30),
        (0.75, 23.70, 24.70),
        (0.90, 22.80, 23.00),
        (1.00, 22.00, 22.00),
    )
    fish_crest_angles_deg: tuple[float, ...] = (0.0, 62.0, -62.0)
    fish_crest_peak_height: float = 1.00
    fish_crest_end_height: float = 0.55
    fish_crest_half_width: float = 4.20
    fish_crest_end_half_width: float = 2.60
    fish_crest_overlap: float = 0.45
    fish_crest_end_margin: float = 1.50

    # capsule-mounted stabilizing/visual fins
    dorsal_fin_length: float = 52.0
    dorsal_fin_height: float = 14.0
    dorsal_fin_t: float = 3.2
    pectoral_fin_length: float = 38.0
    pectoral_fin_span: float = 16.0
    pectoral_fin_t: float = 3.2
    pectoral_fin_cant_deg: float = 45.0

    # canonical metriMade R2 identity, selected for the flat keel underside
    watermark_enabled: bool = True
    watermark_asset_revision: str = "MM-WM-001-R2"
    watermark_product_id: str = "MM-BOAT-003"
    watermark_version: str = "1.1.0-draft.1"
    watermark_layout_tier: str = "compact"
    watermark_width: float = 40.179
    watermark_height: float = 11.200
    watermark_depth: float = 0.400
    watermark_overlap: float = 0.010

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
    caudal_visual_center_z: float = -10.0
    caudal_span: float = 70.0

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

    def __post_init__(self) -> None:
        if self.fish_registered_sections < 4:
            raise ValueError("fish_registered_sections must be at least 4")
        if len(self.fish_crest_angles_deg) != 3:
            raise ValueError("the approved silhouette requires exactly three crests")
        if self.fish_fairing_overlap <= 0 or self.fish_fairing_overlap >= self.wall:
            raise ValueError("fish_fairing_overlap must stay inside the pressure-core wall")
        if self.fish_crest_end_height < 0.55:
            raise ValueError("crest end height must remain printable with a 0.4 mm nozzle")
        if self.fish_crest_peak_height < self.fish_crest_end_height:
            raise ValueError("crest peak height must not be below the end height")
        for name, value in (
            ("dorsal_fin_t", self.dorsal_fin_t),
            ("pectoral_fin_t", self.pectoral_fin_t),
            ("fin_t", self.fin_t),
        ):
            if value < 2.4:
                raise ValueError(f"{name} must be at least 2.4 mm")
        if self.watermark_layout_tier != "compact":
            raise ValueError("the qualified keel region selects the compact watermark tier")
        if self.watermark_depth < 0.4 or self.watermark_depth > 0.8:
            raise ValueError("watermark depth must remain inside the qualified 0.4-0.8 mm range")
        if self.keel_wall - self.watermark_depth < 0.8:
            raise ValueError("watermark must leave at least 0.8 mm of keel wall")
        for name, profile in (
            ("fish_nose_profile", self.fish_nose_profile),
            ("fish_chain_profile", self.fish_chain_profile),
            ("fish_capsule_profile", self.fish_capsule_profile),
        ):
            if profile[0][0] != 0.0 or profile[-1][0] != 1.0:
                raise ValueError(f"{name} must start at 0 and end at 1")
            if any(b[0] <= a[0] for a, b in zip(profile, profile[1:])):
                raise ValueError(f"{name} stations must be strictly increasing")
            if any(row[1] <= self.wall or row[2] <= self.wall for row in profile):
                raise ValueError(f"{name} radii must exceed the wall thickness")

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
