"""MM-TOY-003 TrailCam B2 — parametric contract, revision 0.1.0-parametric.1.

Millimetres are used throughout.  The origin is the intersection of the common
wheel axis and the vehicle longitudinal centre plane: +X forward, +Y left,
+Z up.  Values marked PROVISIONAL describe planning proxies and must not be
used as manufacturing authority until the delivered parts are measured.
"""

from __future__ import annotations

import math

PROJECT_ID = "MM-TOY-003"
REVISION = "0.1.0"
CANDIDATE = "0.1.0-parametric.1"

# Approved vehicle envelope and wheel architecture.
OVERALL_WIDTH_MAX_MM = 260.0
OVERALL_LENGTH_MAX_MM = 190.0
UPRIGHT_HEIGHT_MAX_MM = 250.0
WHEEL_COUNT = 2
AXLE_COUNT = 1
WHEEL_DIAMETER_MM = 120.0  # PROVISIONAL exact wheel unresolved
WHEEL_RADIUS_MM = WHEEL_DIAMETER_MM / 2.0
WHEEL_WIDTH_MM = 40.0
WHEEL_TRACK_MM = 205.0
WHEEL_CENTER_Y_MM = WHEEL_TRACK_MM / 2.0
GROUND_Z_MM = -WHEEL_RADIUS_MM

# Printed structure.
SIDE_FRAME_Y_MM = 72.0
SIDE_FRAME_THICKNESS_MM = 6.0
SIDE_FRAME_OUTER_Y_MM = SIDE_FRAME_Y_MM + SIDE_FRAME_THICKNESS_MM / 2.0
WHEEL_INNER_Y_MM = WHEEL_CENTER_Y_MM - WHEEL_WIDTH_MM / 2.0
WHEEL_BODY_GAP_MM = WHEEL_INNER_Y_MM - SIDE_FRAME_OUTER_Y_MM
CROSSMEMBER_END_Y_MM = SIDE_FRAME_Y_MM - SIDE_FRAME_THICKNESS_MM / 2.0 - 0.3
BAR_MAIN_MM = 14.0
BAR_SECONDARY_MM = 10.0
BAR_BRACE_MM = 8.0
WALL_MIN_MM = 2.4
FEATURE_MIN_MM = 1.6

# Fasteners are metal. Printed interfaces use clearance/insert proxies only.
M3_CLEARANCE_MM = 3.6
M3_INSERT_PILOT_MM = 4.2  # PROVISIONAL; freeze from exact insert + coupon
M3_INSERT_DEPTH_MM = 7.0
MOTOR_BRACKET_BOTTOM_PITCH_MM = 14.8  # Pololu item 1995 supplier value
MOTOR_BRACKET_CENTER_Y_MM = 52.0  # PROVISIONAL placement

# Module locations and COTS planning envelopes.
BATTERY_ENVELOPE_MM = (90.0, 50.0, 38.0)  # PROVISIONAL 3S LiPo class
BATTERY_CENTER_MM = (0.0, 0.0, 94.0)
BATTERY_TRIM_MM = 12.0
CONTROL_TRAY_Z_MM = 122.0
CAMERA_ENVELOPE_MM = (22.0, 19.0, 19.0)  # X/Y/Z, RunCam class proxy
CAMERA_CENTER_MM = (73.0, 0.0, 139.5)
MOTOR_BODY_RADIUS_MM = 17.4  # PROVISIONAL official 37D family body radius
MOTOR_BODY_INNER_Y_MM = 10.0
MOTOR_BODY_OUTER_Y_MM = 68.5
MOTOR_SHAFT_OUTER_Y_MM = 96.0
MOTOR_SHAFT_FRAME_CLEARANCE_MM = 8.0  # PROVISIONAL; exact hub/shaft sweep owns final value

# Non-rolling landing protection. The contact-controlling corner is the outer
# lower corner of the front/rear crossbar at (+/-88, -28) in the XZ plane.
LANDING_TIP_X_MM = 88.0
LANDING_BOTTOM_Z_MM = -28.0
LANDING_TOP_Z_MM = -20.0
LANDING_CONTACT_TILT_MIN_DEG = 22.0
NORMAL_PITCH_LIMIT_DEG = 12.0
TIP_DETECTION_DEG = 35.0

# Process planning values only; exact Anycubic JSON profiles remain open.
MATERIAL = "PETG baseline; exact product and conditioning unresolved"
NOZZLE_MM = 0.6
LINE_WIDTH_MM = 0.66
LAYER_HEIGHT_MM = 0.24
STL_LINEAR_TOLERANCE_MM = 0.10
STL_ANGULAR_TOLERANCE_RAD = 0.10

# Preliminary mass ledger for the digital proxy. Purchased values are not
# qualification evidence; the report must preserve this limitation.
PETG_DENSITY_G_PER_MM3 = 1.27e-3
COTS_MASS_G = {
    "motor_left": 210.0,
    "motor_right": 210.0,
    "brackets_pair": 35.0,
    "wheel_hub_left": 105.0,
    "wheel_hub_right": 105.0,
    "battery_power_set": 390.0,
    "control_stack": 150.0,
    "camera_vtx_rx": 25.0,
    "antennas": 18.0,
    "hardware": 80.0,
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
assert WHEEL_BODY_GAP_MM >= 5.0
assert 110.0 <= WHEEL_DIAMETER_MM <= 130.0
assert LANDING_CONTACT_ANGLE_DEG >= LANDING_CONTACT_TILT_MIN_DEG
assert LAYER_HEIGHT_MM <= 0.75 * NOZZLE_MM
