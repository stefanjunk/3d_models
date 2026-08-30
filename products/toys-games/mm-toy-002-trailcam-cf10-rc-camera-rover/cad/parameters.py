"""MM-TOY-002 TrailCam CF10 FPV Rover — shared parametric contract, revision 0.4.0.

Single source of truth for all component scripts. Values are frozen from
design-spec.yaml geometry.designed_datums (sourced Tamiya CC-02 class product
pages, retrieved 2026-08-30) unless marked PROVISIONAL. Units: millimetres.
Do not edit per-component; change here and regenerate every component.
"""

# --- Frozen vehicle datums (class reference, re-verify before manufacturing) ---
WHEELBASE_MM = 252.0            # CC-02 M-size wheelbase
TREAD_MM = 165.0                # class 160-167
TIRE_DIAMETER_MM = 90.0         # kit-class nominal
TIRE_DIAMETER_MAX_MM = 115.0    # envelope for keep-outs
TIRE_WIDTH_MM = 33.0
OVERALL_WIDTH_MAX_MM = 200.0
OVERALL_LENGTH_TARGET_MM = 400.0
GROUND_CLEARANCE_MM = 40.0

# --- Derived datums ---
AXLE_X_MM = WHEELBASE_MM / 2.0          # +/-126 axle planes
WHEEL_Y_MM = TREAD_MM / 2.0             # +/-82.5 wheel center planes
FRAME_LENGTH_MM = 340.0                 # ladder frame without bumpers
FRAME_RAIL_Y_MM = 32.0                  # rail centerline offset from vehicle center plane
RAIL_W_MM = 14.0
RAIL_H_MM = 24.0

# --- Provisional purchased-part envelopes (flagged; measure before manufacturing) ---
BATTERY_ENVELOPE_MM = (140.0, 47.0, 45.0)     # PROVISIONAL 2S/3S shorty LiPo
MOTOR_ENVELOPE_MM = (36.0, 36.0, 80.0)        # PROVISIONAL 540/550 + planetary gearhead
SERVO_ENVELOPE_MM = (40.5, 20.0, 40.0)        # PROVISIONAL standard 1:10 servo
CAMERA_ENVELOPE_MM = (19.0, 19.0, 22.0)       # RunCam Phoenix 2 SE V2 class
VTX_ENVELOPE_MM = (35.0, 35.0, 28.0)          # SpeedyBee TX800 class
RX_ENVELOPE_MM = (40.0, 33.0, 26.0)           # RadioMaster ER5C class

# --- Printed-structure rules (design-spec 0.4.0) ---
WALL_MIN_MM = 2.4                 # frame/bridge walls
FATIGUE_MIN_MM = 3.0              # suspension arms, steering links
FEATURE_MIN_MM = 1.6
FASTENER_DEFAULT = "M3 metal through-bolt, washer, Nyloc or captured nut"
PIVOT_PIN_MM = 3.0                # metal pin or M3 bolt in printed bosses
CLEARANCE_FASTENER_MM = 0.25      # per side, printed-to-printed fastened parts
CLEARANCE_PURCHASED_MM = 0.4      # per side, printed-to-purchased mates

# --- Process planning values (DEC-PROCESS-001, provisional) ---
NOZZLE_MM = 0.6
LAYER_MM = 0.24
LINE_WIDTH_MM = 0.66
MATERIAL = "PETG baseline; PETG-CF/ASA coupon comparison pending"

ORIGIN_NOTE = ("vehicle longitudinal center plane; z=0 at lowest frame datum; "
               "x forward, y left, z up")
