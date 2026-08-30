"""MM-TOY-002 TrailCam CF10 FPV Rover — shared parametric contract, revision 0.4.0.

Single source of truth for all component scripts. Values are frozen from
design-spec.yaml geometry.designed_datums (sourced Tamiya CC-02 class product
pages, retrieved 2026-08-30) unless marked PROVISIONAL. Units: millimetres.
Do not edit per-component; change here and regenerate every component.
"""

# --- Frozen vehicle datums (class reference, re-verify before manufacturing) ---
WHEELBASE_MM = 252.0  # CC-02 M-size wheelbase
TREAD_MM = 165.0  # class 160-167
TIRE_DIAMETER_MM = 90.0  # kit-class nominal
TIRE_DIAMETER_MAX_MM = 115.0  # envelope for keep-outs
TIRE_WIDTH_MM = 33.0
OVERALL_WIDTH_MAX_MM = 200.0
OVERALL_LENGTH_TARGET_MM = 400.0
GROUND_CLEARANCE_MM = 40.0

# --- Derived datums ---
AXLE_X_MM = WHEELBASE_MM / 2.0  # +/-126 axle planes
WHEEL_Y_MM = TREAD_MM / 2.0  # +/-82.5 wheel center planes
# Rejected experiment-only datums retained to reproduce the blocked corner-stack
# trace. New geometry must not consume these values; see the phase-2 review.
PIVOT_X_MM = 86.0  # REJECTED corner-stack-v2 proposal
PIVOT_Z_MM = 8.0  # REJECTED corner-stack-v2 proposal
FRAME_LENGTH_MM = 340.0  # ladder frame without bumpers
FRAME_RAIL_Y_MM = 32.0  # rail centerline offset from vehicle center plane
RAIL_W_MM = 14.0
RAIL_H_MM = 24.0

# --- Provisional purchased-part envelopes (flagged; measure before manufacturing) ---
BATTERY_ENVELOPE_MM = (140.0, 47.0, 45.0)  # PROVISIONAL 2S/3S shorty LiPo
MOTOR_ENVELOPE_MM = (36.0, 36.0, 80.0)  # PROVISIONAL 540/550 + planetary gearhead
SERVO_ENVELOPE_MM = (40.5, 20.0, 40.0)  # PROVISIONAL standard 1:10 servo
CAMERA_ENVELOPE_MM = (19.0, 19.0, 22.0)  # RunCam Phoenix 2 SE V2 class
VTX_ENVELOPE_MM = (35.0, 35.0, 28.0)  # SpeedyBee TX800 class
RX_ENVELOPE_MM = (40.0, 33.0, 26.0)  # RadioMaster ER5C class

# --- Printed-structure rules (design-spec 0.4.0) ---
WALL_MIN_MM = 2.4  # frame/bridge walls
FATIGUE_MIN_MM = 3.0  # suspension arms, steering links
FEATURE_MIN_MM = 1.6
FASTENER_DEFAULT = "M3 metal through-bolt, washer, Nyloc or captured nut"
PIVOT_PIN_MM = 3.0  # metal pin or M3 bolt in printed bosses
CLEARANCE_FASTENER_MM = 0.25  # per side, printed-to-printed fastened parts
CLEARANCE_PURCHASED_MM = 0.4  # per side, printed-to-purchased mates

# --- Double-wishbone v2 kinematic contract (0.4.0-draft.2) ---
# These are digital point/axis datums, not manufacturing interfaces.  The
# current chassis v1 does not provide the required longitudinal (x-axis)
# wishbone pivots.  Exact ball joints, shocks, CVDs, hubs and wheels remain a
# purchased-sample gate; see reports/cots-drivetrain-study-v0.4.0.md.
DWV2_LOWER_INBOARD_Y_MM = 42.0
DWV2_LOWER_INBOARD_Z_MM = 10.0
DWV2_LOWER_INBOARD_HALF_SPAN_X_MM = 16.0
DWV2_UPPER_INBOARD_Y_MM = 41.0
DWV2_UPPER_INBOARD_Z_MM = 35.0
DWV2_UPPER_INBOARD_HALF_SPAN_X_MM = 14.0
DWV2_LOWER_OUTER_Y_MM = 70.0
DWV2_LOWER_OUTER_Z_MM = 7.0
DWV2_UPPER_OUTER_Y_MM = 68.0
DWV2_UPPER_OUTER_Z_MM = 31.0
DWV2_FRONT_UPPER_OUTER_X_MM = 123.0
DWV2_REAR_UPPER_OUTER_X_MM = -126.0
DWV2_WHEEL_CENTER_Z_MM = 5.0
DWV2_LOWER_SHOCK_Y_MM = 56.0
DWV2_LOWER_SHOCK_Z_MM = 8.5
DWV2_UPPER_SHOCK_Y_MM = 49.0
DWV2_UPPER_SHOCK_Z_MM = 48.0
DWV2_FRONT_TIE_OUTER_MM = (114.0, 67.0, 22.0)
DWV2_FRONT_TIE_INNER_MM = (114.0, 34.0, 28.0)
DWV2_REAR_TOE_OUTER_MM = (-138.0, 67.0, 18.0)
DWV2_REAR_TOE_INNER_MM = (-138.0, 40.0, 21.0)
DWV2_INNER_HALFSHAFT_Y_MM = 18.0
DWV2_INNER_HALFSHAFT_Z_MM = 15.0
DWV2_OUTER_HALFSHAFT_Y_MM = 72.0
DWV2_OUTER_HALFSHAFT_Z_MM = 5.0
DWV2_TRAVEL_MIN_MM = -10.0
DWV2_TRAVEL_MAX_MM = 10.0
DWV2_TRAVEL_STEP_MM = 1.0
DWV2_STEER_MIN_DEG = -20.0
DWV2_STEER_MAX_DEG = 20.0
DWV2_STEER_STEP_DEG = 2.0

# Provisional official COTS-envelope baseline only.  It is not an interface
# freeze and it carries no torque, life or compatibility claim.
POLOLU_4743_BODY_DIAMETER_MM = 34.8
POLOLU_4743_FLANGE_DIAMETER_MM = 36.8
POLOLU_4743_BODY_LENGTH_MM = 54.7
POLOLU_4743_AXIAL_ENVELOPE_WITH_SHAFT_MM = 76.7
POLOLU_4743_OUTPUT_SHAFT_DIAMETER_MM = 6.0
POLOLU_4743_OUTPUT_SHAFT_LENGTH_MM = 16.0
RC4WD_VVV_S0183_LENGTH_RANGE_MM = (55.0, 70.0)
RC4WD_VVV_S0183_BODY_DIAMETER_MM = 10.0
RC4WD_VVV_S0183_END_BORE_MM = 5.0

# --- V2 chassis pivot-host coupon (0.4.0-draft.3) ---
# Local coupon frame: x longitudinal, y outward from a frame-rail centerline,
# z up from the rail bottom.  These dimensions qualify the chassis-side
# longitudinal pivot topology only; they do not freeze arm or COTS geometry.
DWV2_HOST_RAIL_LENGTH_MM = 80.0
DWV2_HOST_RAIL_WALL_MM = 2.4
DWV2_HOST_ARM_EYE_WIDTH_MM = 6.0
DWV2_HOST_ARM_EYE_DIAMETER_MM = 12.8
DWV2_HOST_CLEVIS_GAP_MM = 6.6
DWV2_HOST_EYE_POCKET_DIAMETER_MM = 13.4
DWV2_HOST_LUG_THICKNESS_MM = 4.0
DWV2_HOST_PIVOT_BORE_MM = 3.5
DWV2_HOST_PIVOT_BOSS_DIAMETER_MM = 13.6
DWV2_HOST_ARM_BEAM_PROXY_RADIUS_MM = 3.0

# --- Process planning values (DEC-PROCESS-001, provisional) ---
NOZZLE_MM = 0.6
LAYER_MM = 0.24
LINE_WIDTH_MM = 0.66
MATERIAL = "PETG baseline; PETG-CF/ASA coupon comparison pending"

ORIGIN_NOTE = (
    "vehicle longitudinal center plane; z=0 at lowest frame datum; "
    "x forward, y left, z up"
)
