"""Component-driven contract for MM-TOY-003 candidate 0.1.0-parametric.3.

All dimensions are millimetres.  The origin is the common wheel axis on the
vehicle centre plane: +X forward, +Y left, +Z up.  Values ending in
``_PROVISIONAL`` come from manufacturer drawings or named retailer envelopes,
not from delivered-part inspection.  They remain coupon/measurement gates.
"""

from __future__ import annotations

import math

PROJECT_ID = "MM-TOY-003"
REVISION = "0.1.0"
CANDIDATE = "0.1.0-parametric.3"
BOM_CANDIDATE = "0.1.0-bom.1"

# Approved architecture and envelope.
OVERALL_WIDTH_MAX_MM = 260.0
OVERALL_LENGTH_MAX_MM = 190.0
UPRIGHT_HEIGHT_MAX_MM = 250.0
PRINT_BED_MM = (220.0, 220.0, 250.0)
WHEEL_COUNT = 2
AXLE_COUNT = 1

# INJORA CRAW20161023 tire and CRAW18003 rim stack.  The tire width is the
# conservative rotating envelope; exact bead/hex offsets remain intake-owned.
WHEEL_DIAMETER_MM = 120.0
WHEEL_RADIUS_MM = 60.0
WHEEL_WIDTH_MM = 42.0
WHEEL_TRACK_MM = 216.0
WHEEL_CENTER_Y_MM = WHEEL_TRACK_MM / 2.0
WHEEL_INNER_Y_MM = WHEEL_CENTER_Y_MM - WHEEL_WIDTH_MM / 2.0
GROUND_Z_MM = -WHEEL_RADIUS_MM

# Printed structural frame.
SIDE_FRAME_Y_MM = 70.0
SIDE_FRAME_THICKNESS_MM = 6.0
SIDE_FRAME_OUTER_Y_MM = SIDE_FRAME_Y_MM + SIDE_FRAME_THICKNESS_MM / 2.0
CROSSMEMBER_END_Y_MM = SIDE_FRAME_Y_MM - SIDE_FRAME_THICKNESS_MM / 2.0 - 0.3
MOTOR_POD_OUTER_Y_MM = 81.0
WHEEL_TO_PRINTED_GAP_MM = WHEEL_INNER_Y_MM - MOTOR_POD_OUTER_Y_MM
BAR_MAIN_MM = 10.5
BAR_SECONDARY_MM = 7.5
BAR_BRACE_MM = 6.0
WALL_MIN_MM = 2.4
FEATURE_MIN_MM = 1.6

# Metal fasteners and Pololu 1995 bracket.  The three bracket base holes are
# placed across X at the manufacturer-declared 14.8 mm pitch.  Axial slots in
# the printed pod retain +/-2 mm sample-registration travel.
M3_CLEARANCE_MM = 3.6
M3_SLOT_WIDTH_MM = 4.0
M3_INSERT_PILOT_MM_PROVISIONAL = 4.2
M3_INSERT_DEPTH_MM_PROVISIONAL = 7.0
MOTOR_BRACKET_BASE_PITCH_MM = 14.8
MOTOR_BRACKET_CENTER_Y_MM = 78.0
MOTOR_BRACKET_AXIAL_SLOT_MM = 8.0

# Pololu 4755 and 2686 proxies.  The motor page declares a 37 mm class body,
# 73 mm nominal length and a 16 mm long 6 mm D shaft.  The adapter drawing
# declares 20 mm length.  The remaining wheel-hex axial offset is measurable.
MOTOR_BODY_RADIUS_MM = 18.4
MOTOR_BODY_LENGTH_MM_PROVISIONAL = 73.0
MOTOR_OUTPUT_FACE_Y_MM_PROVISIONAL = 84.5
MOTOR_BODY_INNER_Y_MM_PROVISIONAL = (
    MOTOR_OUTPUT_FACE_Y_MM_PROVISIONAL - MOTOR_BODY_LENGTH_MM_PROVISIONAL
)
MOTOR_SHAFT_LENGTH_MM = 16.0
MOTOR_SHAFT_RADIUS_MM = 3.0
WHEEL_ADAPTER_LENGTH_MM = 20.0
WHEEL_ADAPTER_RADIUS_PROXY_MM = 7.0
WHEEL_HEX_AXIAL_RESIDUAL_MM_PROVISIONAL = (
    WHEEL_CENTER_Y_MM
    - (MOTOR_OUTPUT_FACE_Y_MM_PROVISIONAL + WHEEL_ADAPTER_LENGTH_MM)
)

# Gens ace GEA503S60X6GT retailer envelope and guarded strap cradle.
BATTERY_SIZE_MM_PROVISIONAL = (153.0, 44.0, 25.0)
BATTERY_CLEARANCE_PER_SIDE_MM = 1.0
BATTERY_INNER_MM = tuple(
    value + 2.0 * BATTERY_CLEARANCE_PER_SIDE_MM
    for value in BATTERY_SIZE_MM_PROVISIONAL
)
BATTERY_WALL_MM = 3.0
BATTERY_BASE_Z_MM = 112.0
BATTERY_FLOOR_MM = 4.0
BATTERY_CENTER_Z_MM = (
    BATTERY_BASE_Z_MM
    + BATTERY_FLOOR_MM
    + BATTERY_CLEARANCE_PER_SIDE_MM
    + BATTERY_SIZE_MM_PROVISIONAL[2] / 2.0
)
BATTERY_CRADLE_TOP_Z_MM = 145.0
BATTERY_TRIM_MM = 12.0
BATTERY_MOUNT_SLOT_LENGTH_MM = 28.0
BATTERY_STRAP_SLOT_LENGTH_MM = 22.0
BATTERY_STRAP_SLOT_WIDTH_MM = 4.5
BATTERY_CROSSMEMBER_Z_MM = (104.0, 110.0)

# Electronics levels and manufacturer-declared board envelopes.
ELECTRONICS_CROSSMEMBER_Z_MM = (147.0, 153.0)
ELECTRONICS_DECK_Z_MM = (154.0, 157.0)
UPPER_CROSSMEMBER_Z_MM = (168.0, 174.0)
DRIVER_SIZE_MM = (65.0, 51.3, 11.0)
DRIVER_CENTER_MM = (-30.0, 0.0, 162.5)
DRIVER_HOLE_DELTA_MM = (7.62, 43.18)
TEENSY_SIZE_MM = (61.0, 17.8, 7.0)
TEENSY_CENTER_MM = (40.0, 27.0, 162.5)
IMU_SIZE_MM_PROVISIONAL = (25.5, 17.8, 5.0)
IMU_CENTER_MM = (35.0, -33.0, 164.5)
TX800_SIZE_MM = (28.0, 28.0, 8.0)
TX800_CENTER_MM = (-47.0, 44.0, 162.0)
TX800_HOLE_PITCH_MM = 20.0
RP3_SIZE_MM = (22.0, 13.0, 4.0)
RP3_CENTER_MM = (28.0, 48.0, 160.0)
BEC_SIZE_MM = (20.0, 18.0, 9.0)
BEC_CENTER_MM = (-5.0, 45.0, 162.5)

# Power-service panel.  XT60E-M and fuse-holder openings remain explicit
# sample/coupon dimensions because the purchased variants own final geometry.
POWER_PANEL_Y_MM = -64.0
XT60_PANEL_CUTOUT_MM_PROVISIONAL = (17.0, 9.5)
XT60_MOUNT_PITCH_MM_PROVISIONAL = 24.0
FUSE_HOLDER_ENVELOPE_MM_PROVISIONAL = (55.0, 16.0, 15.0)
FUSE_HOLDER_CENTER_MM = (-42.0, -56.0, 130.0)
XT60_ENVELOPE_MM_PROVISIONAL = (30.0, 19.0, 15.0)
XT60_CENTER_MM = (24.0, -55.0, 130.0)

# RunCam Phoenix 2 SE V2 and guard.  Camera side screw position remains a
# longitudinal slot until the exact delivered housing is measured.
CAMERA_SIZE_MM = (22.0, 19.0, 19.0)  # X/Y/Z orientation from 19 x 19 x 22
CAMERA_CENTER_MM = (76.0, 0.0, 139.0)
CAMERA_LENS_RADIUS_MM_PROVISIONAL = 7.0
CAMERA_LENS_PROTRUSION_MM_PROVISIONAL = 6.0
CAMERA_MOUNT_SLOT_LENGTH_MM = 7.0
CAMERA_MOUNT_HOLE_MM_PROVISIONAL = 2.6

# Mechanically retained steel-segment cassette.  The cavity is sized above
# the theoretical volume of 180 g steel; the component-driven frame raises
# the current calculation point enough that only 120 g is entered in the mass
# ledger.  The installed value remains measurement-owned.  Four M3
# through-bolts provide retention; adhesive is not structural closure.
BALLAST_OUTER_MM = (78.0, 46.0, 12.5)
BALLAST_WALL_MM = 3.0
BALLAST_BODY_Z0_MM = 174.0
BALLAST_BODY_Z1_MM = 186.5
BALLAST_LID_Z1_MM = 189.5
BALLAST_FASTENER_X_MM = 33.0
BALLAST_FASTENER_Y_MM = 17.0
BALLAST_CASSETTE_DESIGN_CAPACITY_G = 180.0
BALLAST_INSTALLED_ESTIMATE_G = 120.0

# Non-rolling landing protection.
LANDING_TIP_X_MM = 88.0
LANDING_BOTTOM_Z_MM = -28.0
LANDING_TOP_Z_MM = -20.0
LANDING_CONTACT_TILT_MIN_DEG = 22.0
NORMAL_PITCH_LIMIT_DEG = 12.0
TIP_DETECTION_DEG = 35.0

# FDM planning contract.  Exact material and Anycubic profile remain open.
MATERIAL = "PETG baseline; exact product and conditioning unresolved"
NOZZLE_MM = 0.6
LINE_WIDTH_MM = 0.66
LAYER_HEIGHT_MM = 0.24
PETG_DENSITY_G_PER_MM3 = 1.27e-3
STL_LINEAR_TOLERANCE_MM = 0.10
STL_ANGULAR_TOLERANCE_RAD = 0.10

# BOM 0.1.0-bom.1 installed mass ledger.  Z/X/Y are CAD registration
# positions for the digital calculation only; delivered masses supersede it.
COTS_MASS_POSITION = {
    "motor_left": (210.0, 0.0, 48.0, 0.0),
    "motor_right": (210.0, 0.0, -48.0, 0.0),
    "bracket_left": (14.0, 0.0, 78.0, -9.0),
    "bracket_right": (14.0, 0.0, -78.0, -9.0),
    "wheel_adapter_left": (7.5, 0.0, WHEEL_CENTER_Y_MM, 0.0),
    "wheel_adapter_right": (7.5, 0.0, -WHEEL_CENTER_Y_MM, 0.0),
    "wheel_rim_tire_left": (171.5, 0.0, WHEEL_CENTER_Y_MM, 0.0),
    "wheel_rim_tire_right": (171.5, 0.0, -WHEEL_CENTER_Y_MM, 0.0),
    "battery": (359.0, 0.0, 0.0, BATTERY_CENTER_Z_MM),
    "motor_driver": (32.0, *DRIVER_CENTER_MM),
    "controller": (10.0, *TEENSY_CENTER_MM),
    "controller_headers": (2.0, *TEENSY_CENTER_MM),
    "imu": (3.0, *IMU_CENTER_MM),
    "logic_bec": (3.0, *BEC_CENTER_MM),
    "rc_receiver": (4.6, *RP3_CENTER_MM),
    "fpv_camera": (8.6, *CAMERA_CENTER_MM),
    "video_transmitter": (10.0, *TX800_CENTER_MM),
    "service_disconnect": (3.0, *XT60_CENTER_MM),
    "fuse_holder": (23.6, *FUSE_HOLDER_CENTER_MM),
    "main_fuse": (2.0, -42.0, -56.0, 130.0),
    "bus_capacitor": (4.0, -12.0, 0.0, 160.0),
    "motor_suppression_caps": (1.0, 0.0, 0.0, 0.0),
    "wire_harness": (45.0, 0.0, 0.0, 90.0),
    "fasteners_and_straps": (80.0, 0.0, 0.0, 75.0),
    "upper_trim_ballast": (BALLAST_INSTALLED_ESTIMATE_G, 0.0, 0.0, 181.0),
}


def landing_contact_angle_deg(x_mm: float, z_mm: float) -> float:
    """First positive pitch angle at which an XZ point reaches the ground."""
    for tenth_deg in range(0, 9001):
        angle = math.radians(tenth_deg / 100.0)
        world_z = z_mm * math.cos(angle) - abs(x_mm) * math.sin(angle)
        if world_z <= GROUND_Z_MM:
            return tenth_deg / 100.0
    raise ValueError("landing point does not reach the ground within 90 degrees")


LANDING_CONTACT_ANGLE_DEG = landing_contact_angle_deg(
    LANDING_TIP_X_MM, LANDING_BOTTOM_Z_MM
)

assert WHEEL_COUNT == 2 and AXLE_COUNT == 1
assert WHEEL_TO_PRINTED_GAP_MM >= 5.0
assert WHEEL_TRACK_MM + WHEEL_WIDTH_MM <= OVERALL_WIDTH_MAX_MM
assert MOTOR_BODY_INNER_Y_MM_PROVISIONAL > 0.0
assert WHEEL_HEX_AXIAL_RESIDUAL_MM_PROVISIONAL >= 0.0
assert BATTERY_INNER_MM[0] + 2.0 * BATTERY_WALL_MM <= OVERALL_LENGTH_MAX_MM
assert (BATTERY_MOUNT_SLOT_LENGTH_MM - M3_CLEARANCE_MM) / 2.0 >= BATTERY_TRIM_MM
assert LANDING_CONTACT_ANGLE_DEG >= LANDING_CONTACT_TILT_MIN_DEG
assert LAYER_HEIGHT_MM <= 0.75 * NOZZLE_MM
