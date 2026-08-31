#!/usr/bin/env python3
"""Build the dimensioned-COTS preflight and interface graph for MM-TOY-003."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-31"
STAMP = "2026-08-31T18:20:00+02:00"
ASSESSMENT = "PREFLIGHT-MM-TOY-003-002"
REVISION = "0.1.0-bom.2"

URL = {
    "motor": "https://www.pololu.com/product/4755",
    "motor_drawing": "https://www.pololu.com/file/0J1735/37d-metal-gearmotors-dimension-diagram.pdf",
    "bracket": "https://www.pololu.com/product/1995",
    "bracket_drawing": "https://www.pololu.com/file/0J653/1995-37D-machined-bracket.pdf",
    "hub": "https://banebots.com/t81-hub-6mm-shaft/",
    "hub_cad": "https://www.3dvieweronline.com/members/Id544d8a7bb8401b0c7450ed9d6950a1fc/fN6usS0aaWQQ7m5",
    "wheel": "https://banebots.com/banebots-wheel-4-7-8-x-0-8-hub-mount-60a-black/",
    "battery": "https://gensace.de/products/gens-ace-g-tech-5000mah-11-1v-60c-3s1p-lipo-with-xt60-plug",
    "driver": "https://www.pololu.com/product/2507",
    "driver_drawing": "https://www.pololu.com/file/0J1403/pololu-dual-vnh5019-motor-driver-shield-dimensions.pdf",
    "bec": "https://www.pololu.com/product/2851",
    "bec_drawing": "https://www.pololu.com/file/0J1436/d24v50f5-step-down-voltage-regulator-dimensions.pdf",
    "controller": "https://www.pjrc.com/store/teensy41.html",
    "controller_drawing": "https://www.pjrc.com/teensy/dimensions.html",
    "imu": "https://www.adafruit.com/product/4502",
    "imu_drawing": "https://github.com/adafruit/Adafruit-LSM6DSOX-PCB/blob/master/Adafruit_LSM6DSOX.brd",
    "imu_guide": "https://learn.adafruit.com/lsm6dsox-and-ism330dhc-6-dof-imu/downloads",
    "receiver": "https://radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver",
    "camera": "https://shop.runcam.com/runcam-phoenix-2-special-edition/",
    "vtx": "https://www.speedybee.com/speedybee-tx800/",
    "fuse": "https://www.littelfuse.com/assetdocs/1786152?assetguid=77ab3607-41f8-4bbc-987e-e8022a7a6f03",
}


ENTITIES = [
    ("E-PRINT-FRM", "PRINTED_PART", "printed structural frame and motor pods"),
    ("E-PRINT-BAT", "PRINTED_PART", "printed battery cradle"),
    ("E-PRINT-IMU", "PRINTED_PART", "printed IMU datum"),
    ("E-PRINT-CAM", "PRINTED_PART", "printed camera guard"),
    ("E-PRINT-LND", "PRINTED_PART", "printed landing protection"),
    ("E-COTS-MOT", "PURCHASED_PART", "Pololu 4755 37D encoder gearmotors"),
    ("E-COTS-BRK", "PURCHASED_PART", "Pololu 1995 motor brackets"),
    ("E-COTS-HUB", "PURCHASED_PART", "BaneBots T81H-RM61 6 mm hubs"),
    ("E-COTS-WHL", "PURCHASED_PART", "BaneBots T81P-496BB wheels"),
    ("E-COTS-BAT", "PURCHASED_PART", "Gens ace GEA503S60X6GT battery"),
    ("E-COTS-FUS", "PURCHASED_PART", "Littelfuse 178.6152.0001 fuse holder"),
    ("E-COTS-DRV", "PURCHASED_PART", "Pololu 2507 dual VNH5019 driver"),
    ("E-COTS-BEC", "PURCHASED_PART", "Pololu 2851 D24V50F5 regulator"),
    ("E-COTS-CTL", "PURCHASED_PART", "PJRC Teensy 4.1 controller"),
    ("E-COTS-IMU", "PURCHASED_PART", "Adafruit 4502 ISM330DHCX breakout"),
    ("E-COTS-RX", "PURCHASED_PART", "RadioMaster RP3 V2 EU-LBT receiver"),
    ("E-COTS-CAM", "PURCHASED_PART", "RunCam Phoenix 2 SE V2 camera"),
    ("E-COTS-VTX", "PURCHASED_PART", "SpeedyBee TX800 video transmitter"),
    ("E-SW-BAL", "SOFTWARE", "balance controller and safety supervisor"),
    ("E-ENG-BUS", "ENERGY", "protected 3S battery and logic power buses"),
    ("E-HUM-OPR", "HUMAN", "supervising operator"),
    ("E-ENV-GND", "ENVIRONMENT", "firm level test surface and RF environment"),
]


def dim(identifier, feature, nominal, source, criticality="FIT_CRITICAL", status="OFFICIAL_NOMINAL"):
    return {
        "id": identifier,
        "feature": feature,
        "nominal_mm": nominal,
        "lower_mm": None,
        "upper_mm": None,
        "clearance_mm": None,
        "uncertainty_mm": None,
        "status": status,
        "source_ref": source,
        "criticality": criticality,
    }


def iface(
    identifier,
    name,
    a,
    b,
    boundary,
    domains,
    function,
    geometry,
    dimensions,
    sources,
    scores,
    criticality,
    mode,
    effect,
    mitigation,
    method,
    criteria,
    coverage=75,
    note="Official nominal geometry is available; delivered revision, tolerance and measurement uncertainty are not yet confirmed.",
):
    total = sum(scores)
    tier = "I0" if total <= 3 else "I1" if total <= 7 else "I2" if total <= 11 else "I3" if total <= 15 else "I4" if total <= 19 else "I5"
    return {
        "id": identifier,
        "name": name,
        "endpoint_a": a,
        "endpoint_b": b,
        "boundary": boundary,
        "domains": domains,
        "function": function,
        "geometry": geometry,
        "lifecycle_states": ["assembly", "calibration", "use", "service", "disassembly", "failure"],
        "coordinate_frame": {
            "origin": "common wheel-axis and vehicle center-plane intersection unless the interface dimension states a local datum",
            "x_positive": "vehicle forward",
            "y_positive": "vehicle left along the wheel axis",
            "z_positive": "up in the nominal balanced pose",
            "unit": "mm",
        },
        "dimensions": dimensions,
        "keepouts_and_access": ["Preserve tool access, cable bend radius, and the declared moving or thermal envelope."],
        "evidence": {
            "level": "E3",
            "sources": sources,
            "variant_confirmed": False,
            "coverage_percent": coverage,
            "uncertainty_note": note,
            "observability": "PARTLY_OBSERVED",
        },
        "interface_complexity": dict(zip(("GEO", "KIN", "TOL", "PHY", "VAR", "LIF"), scores)) | {"total": total, "tier": tier},
        "criticality": criticality,
        "failure_modes": [{"mode": mode, "effect": effect, "mitigation": mitigation}],
        "verification": {"method": method, "acceptance_criteria": criteria, "status": "PLANNED", "result_refs": []},
        "owner": "MM-TOY-003 integration",
        "version": "0.2",
    }


INTERFACES = [
    iface(
        "IF-INT-MEC-FST-MOTBRKT-001", "37D motor to metal bracket", "E-COTS-MOT", "E-COTS-BRK", "INT", ["GEO", "MEC"], "FST", "MIXED",
        [dim("DIM-MOT-DIA-001", "motor body diameter", 36.8, URL["motor_drawing"]), dim("DIM-MOT-BOSS-002", "output boss diameter", 12.0, URL["motor_drawing"])],
        [URL["motor"], URL["motor_drawing"], URL["bracket"], URL["bracket_drawing"]], [2, 2, 2, 3, 1, 3], "K3",
        "Bracket seating or fastener loosening permits motor motion", "Encoder frame shifts and balance torque becomes unpredictable", "Register the exact motor/bracket drawings, use locking fasteners, inspect and witness-mark.", "measurement",
        ["Both delivered motors seat without bracket distortion; fasteners reach specified engagement; no perceptible motion after a restrained torque test."], 88),
    iface(
        "IF-INT-MEC-FST-BRKFRM-001", "metal bracket to printed motor pod", "E-COTS-BRK", "E-PRINT-FRM", "INT", ["GEO", "MEC"], "FST", "PLN",
        [dim("DIM-BRK-WID-001", "bracket outside width and height", 36.8, URL["bracket_drawing"]), dim("DIM-BRK-THK-002", "bracket axial thickness", 6.5, URL["bracket_drawing"]), dim("DIM-BRK-PAT-003", "spacing of three chassis M3 holes", 14.8, URL["bracket_drawing"])],
        [URL["bracket_drawing"], "cad/component_parameters.py"], [2, 1, 3, 3, 2, 4], "K3",
        "Printed slot creeps, cracks or loses bracket clamp", "Motor axis departs from the common axle datum", "Use a process-matched coupon, through-fasteners and load-spreading washers; reject cracked or loose pods.", "test_coupon",
        ["Both delivered brackets pass the selected coupon with documented clearance; assembled pod survives the restrained torque and cycle test without slip or crack."], 76),
    iface(
        "IF-INT-MEC-ROT-HUBSHFT-001", "6 mm D-shaft to T81 hub", "E-COTS-MOT", "E-COTS-HUB", "INT", ["GEO", "MEC", "KIN"], "ROT", "CYL",
        [dim("DIM-SHAFT-DIA-001", "motor output shaft nominal diameter", 6.0, URL["motor_drawing"], "SAFETY_CRITICAL"), dim("DIM-SHAFT-LEN-002", "available output shaft length", 16.0, URL["motor_drawing"], "FUNCTION_CRITICAL"), dim("DIM-HUB-ENV-003", "T81 hub maximum envelope from linked STEP", 20.32, URL["hub_cad"], "FUNCTION_CRITICAL", "REFERENCE_MODEL_VALIDATED")],
        [URL["motor_drawing"], URL["hub"], URL["hub_cad"]], [2, 3, 3, 4, 2, 4], "K3",
        "Hub slips, walks axially or set screw damages the shaft", "Wheel torque or retention is lost and the rover falls", "Confirm shaft engagement and both 90-degree set-screw locations on samples; use the hub retention specified by the manufacturer.", "prototype_test",
        ["Measured hub bore accepts the delivered 6 mm D-shaft; both set screws fully engage; axial clearance is positive; no slip occurs in the restrained peak-torque test."], 82),
    iface(
        "IF-INT-MEC-RET-WHLHUB-001", "T81 hub to T81 wheel", "E-COTS-HUB", "E-COTS-WHL", "INT", ["GEO", "MEC", "KIN"], "RET", "SNAP",
        [dim("DIM-WHL-OD-001", "wheel outside diameter", 123.825, URL["wheel"], "FUNCTION_CRITICAL"), dim("DIM-WHL-WID-002", "wheel width", 20.32, URL["wheel"], "FUNCTION_CRITICAL"), dim("DIM-SNAP-DIA-003", "hub snap-ring nominal size", 19.05, URL["hub"], "SAFETY_CRITICAL")],
        [URL["hub"], URL["hub_cad"], URL["wheel"]], [2, 2, 3, 3, 2, 4], "K3",
        "Wheel disengages from hub or deforms under side load", "Drive and balance support are lost", "Use the matched T81 family and specified 3/4-inch snap ring; inspect retention before each powered test.", "prototype_test",
        ["Matched T81 wheel seats fully, snap ring is positively retained, and neither wheel moves axially beyond the approved measured limit after the cycle test."], 86),
    iface(
        "IF-ENV-MEC-LOD-WHLGRND-001", "wheel tread to test surface", "E-COTS-WHL", "E-ENV-GND", "ENV", ["MEC", "KIN", "ENV"], "LOD", "FREEFORM",
        [dim("DIM-WHL-OD-004", "loaded-wheel design diameter reference", 123.825, URL["wheel"], "FUNCTION_CRITICAL")],
        [URL["wheel"], "design-spec.yaml"], [2, 3, 3, 4, 3, 4], "K3",
        "Insufficient traction, tire compression or wear exceeds the controller model", "The capture envelope is exceeded and the rover tips", "Limit first tests to clean firm level ground; identify load radius and friction experimentally before free balancing.", "prototype_test",
        ["Measured loaded radius is recorded; restrained traction and capture tests pass on the named surface before any free-balance test."], 68,
        "Nominal size and 60 Shore A compound are manufacturer-declared; loaded radius, friction, wear and batch variation require physical evidence."),
    iface(
        "IF-INT-MEC-RET-BATCRDL-001", "3S battery to printed cradle", "E-COTS-BAT", "E-PRINT-BAT", "INT", ["GEO", "MEC", "ELE"], "RET", "VOLUME",
        [dim("DIM-BAT-LEN-001", "battery length", 154.0, URL["battery"], "SAFETY_CRITICAL"), dim("DIM-BAT-WID-002", "battery width", 43.0, URL["battery"], "SAFETY_CRITICAL"), dim("DIM-BAT-HGT-003", "battery height", 25.0, URL["battery"], "SAFETY_CRITICAL")],
        [URL["battery"], "cad/component_parameters.py"], [2, 1, 3, 4, 3, 4], "K3",
        "Pack is crushed, ejected, chafed or cannot be disconnected", "Fire risk or sudden loss of balance power", "Measure the delivered pack at rest and after cycles; use a guarded strap path without cell compression and retain disconnect access.", "test_coupon",
        ["Delivered pack fits with recorded clearance and no cell compression; two independent restraints hold it through the tip and vibration test; connector remains reachable."], 74),
    iface(
        "IF-INT-ELE-PWR-BATBUS-001", "battery through fuse to protected bus", "E-COTS-BAT", "E-ENG-BUS", "INT", ["ELE", "THM", "MEC"], "PWR", "MIXED",
        [dim("DIM-FUS-LEN-001", "fuse-holder body length", 23.2, URL["fuse"], "FUNCTION_CRITICAL"), dim("DIM-FUS-WID-002", "fuse-holder body width", 20.2, URL["fuse"], "FUNCTION_CRITICAL")],
        [URL["battery"], URL["fuse"], "architecture/control-architecture-v0.1.0.md"], [2, 1, 3, 4, 3, 4], "K3",
        "Short circuit, connector heating or ineffective disconnect", "Battery damage, fire or uncontrolled power loss", "Fuse close to the pack, strain-relieved harness, reachable disconnect and current/temperature-limited restrained tests.", "prototype_test",
        ["Polarity and continuity inspection pass; fuse rating is approved from measured current; voltage drop and temperatures stay inside component limits during restrained tests."], 72),
    iface(
        "IF-INT-ELE-PWR-BUSDRV-001", "protected 3S bus to dual motor driver", "E-ENG-BUS", "E-COTS-DRV", "INT", ["ELE", "THM"], "PWR", "PLN",
        [dim("DIM-DRV-LEN-001", "driver PCB length", 65.0, URL["driver_drawing"], "FIT_CRITICAL"), dim("DIM-DRV-WID-002", "driver PCB width", 51.0, URL["driver_drawing"], "FIT_CRITICAL")],
        [URL["driver"], URL["driver_drawing"]], [2, 1, 2, 4, 2, 4], "K3",
        "Driver overheats, browns out or fails short", "Balance torque is asymmetric, lost or uncontrolled", "Validate cooling, current sense, EN/DIAG and regeneration on a restrained bench with independent cutoff.", "prototype_test",
        ["Both channels meet commanded direction/current; EN/DIAG and current sense detect injected faults; temperatures remain within the approved test limit."], 84),
    iface(
        "IF-INT-ELE-PWR-BUSBEC-001", "protected bus to 5 V logic rail", "E-ENG-BUS", "E-COTS-BEC", "INT", ["ELE", "THM"], "PWR", "PLN",
        [dim("DIM-BEC-LEN-001", "regulator length", 20.3, URL["bec_drawing"]), dim("DIM-BEC-WID-002", "regulator width", 17.8, URL["bec_drawing"]), dim("DIM-BEC-HGT-003", "regulator maximum height", 8.8, URL["bec_drawing"])],
        [URL["bec"], URL["bec_drawing"]], [1, 1, 2, 3, 2, 3], "K3",
        "Logic rail dips or becomes noisy during motor transients", "Controller resets and balance torque is lost", "Separate power routing, local capacitance and logged brownout/transient tests under restrained motor load.", "prototype_test",
        ["The 5 V rail remains within controller limits during worst-case restrained direction reversals and no controller reset occurs."], 88),
    iface(
        "IF-INT-ELE-PWR-DRVMOTOR-001", "dual driver outputs to left and right motors", "E-COTS-DRV", "E-COTS-MOT", "INT", ["ELE", "MEC", "THM"], "PWR", "MIXED",
        [dim("DIM-MOT-LEN-003", "motor body and gearbox nominal length", 73.0, URL["motor_drawing"], "FIT_CRITICAL")],
        [URL["driver"], URL["motor"], URL["motor_drawing"]], [2, 2, 2, 4, 2, 4], "K3",
        "Channels are swapped, reversed or current-limited inconsistently", "The controller reinforces a fall instead of correcting it", "Key harnesses, verify polarity channel-by-channel and require a wheel-off-ground direction test before arming.", "prototype_test",
        ["Positive command produces the documented wheel direction on both channels; current sense is calibrated and injected disconnect/short diagnostics cause disarm."], 80),
    iface(
        "IF-INT-MEC-LOC-IMUDATM-001", "IMU board to printed inertial datum", "E-COTS-IMU", "E-PRINT-IMU", "INT", ["GEO", "MEC", "KIN"], "LOC", "PLN",
        [dim("DIM-IMU-LEN-001", "PCB length from official Eagle Dimension layer", 25.4, URL["imu_drawing"], "FUNCTION_CRITICAL"), dim("DIM-IMU-WID-002", "PCB width from official Eagle Dimension layer", 17.78, URL["imu_drawing"], "FUNCTION_CRITICAL"), dim("DIM-IMU-PAT-003", "center distance of two 2.5 mm mounting holes", 20.32, URL["imu_drawing"], "FUNCTION_CRITICAL")],
        [URL["imu"], URL["imu_guide"], URL["imu_drawing"], "cad/component_parameters.py"], [2, 2, 3, 4, 2, 4], "K3",
        "IMU axis registration moves or vibrates relative to the frame", "Pitch estimate is biased or delayed and balance becomes unstable", "Export the exact official PCB revision/fab geometry or measure the sample; use a rigid keyed datum and document axis transform.", "measurement",
        ["Delivered PCB outline and two 2.5 mm holes match the registered 25.4 x 17.78 mm / 20.32 mm pattern; sensor axes are registered; repeat mounting changes static angle by no more than the approved calibration limit."], 82,
        "The official EagleCAD/Fab Print captures the nominal board and hole geometry; the delivered January-2024-or-later PCB revision and installed connector height remain unconfirmed."),
    iface(
        "IF-INT-DAT-DAT-IMUCTRL-001", "IMU SPI data to controller", "E-COTS-IMU", "E-COTS-CTL", "INT", ["DAT", "ELE"], "DAT", "MIXED",
        [dim("DIM-CTL-LEN-001", "Teensy 4.1 PCB length", 60.96, URL["controller_drawing"], "FIT_CRITICAL"), dim("DIM-CTL-WID-002", "Teensy 4.1 PCB width", 17.78, URL["controller_drawing"], "FIT_CRITICAL")],
        [URL["imu"], URL["controller"], URL["controller_drawing"]], [1, 1, 2, 4, 2, 4], "K3",
        "Stale, aliased or incorrectly mapped IMU data reaches the controller", "The state estimate drives incorrect motor torque", "Rigid SPI wiring, timestamp/health checks, axis calibration and fault injection before balance arming.", "prototype_test",
        ["Sample rate and latency meet the control budget; stale-data injection causes disarm; all six axis signs match the documented frame."], 78),
    iface(
        "IF-INT-DAT-DAT-CTRLDRV-001", "balance controller commands to motor driver", "E-SW-BAL", "E-COTS-DRV", "INT", ["DAT", "ELE"], "DAT", "MIXED",
        [dim("DIM-DRV-PAT-003", "driver mounting/layout authority", None, URL["driver_drawing"], "FIT_CRITICAL", "OFFICIAL_NOMINAL")],
        [URL["driver"], URL["driver_drawing"], "architecture/control-architecture-v0.1.0.md"], [1, 2, 2, 4, 2, 4], "K3",
        "PWM/enable logic or fault handling is wrong", "Motors receive unintended or no corrective torque", "Hardware default-off enable, bounded commands, watchdog and injected EN/DIAG fault tests.", "simulation",
        ["Power-up is torque-off; watchdog, over-tilt and injected driver fault enter the documented disarmed state within the approved deadline."], 82),
    iface(
        "IF-HUM-DAT-USR-OPRRX-001", "operator command link to receiver", "E-HUM-OPR", "E-COTS-RX", "HUM", ["HUM", "DAT", "ENV"], "USR", "FREEFORM",
        [dim("DIM-RX-LEN-001", "receiver length", 22.0, URL["receiver"], "FIT_CRITICAL"), dim("DIM-RX-WID-002", "receiver width", 13.0, URL["receiver"], "FIT_CRITICAL"), dim("DIM-RX-HGT-003", "receiver height", 4.0, URL["receiver"], "FIT_CRITICAL")],
        [URL["receiver"], "architecture/control-architecture-v0.1.0.md"], [2, 1, 2, 4, 3, 4], "K3",
        "Link loss, stale commands or incorrect failsafe state", "The operator cannot request a controlled stop", "Use EU-LBT exact variant, CRSF link-health supervision, command timeout and line-of-sight stop/disconnect access.", "prototype_test",
        ["Loss and stale-frame injection command zero velocity/yaw and then the documented safe state; range is not claimed before a supervised site test."], 76),
    iface(
        "IF-INT-OPT-VIS-CAMGARD-001", "camera to printed guard and view corridor", "E-COTS-CAM", "E-PRINT-CAM", "INT", ["OPT", "GEO", "MEC"], "VIS", "VOLUME",
        [dim("DIM-CAM-WID-001", "camera body width", 19.0, URL["camera"], "FIT_CRITICAL"), dim("DIM-CAM-HGT-002", "camera body height", 19.0, URL["camera"], "FIT_CRITICAL"), dim("DIM-CAM-DEP-003", "camera body depth", 22.0, URL["camera"], "FIT_CRITICAL")],
        [URL["camera"], "cad/component_parameters.py"], [2, 1, 2, 2, 2, 3], "K2",
        "Guard blocks the lens, touches the PCB or transfers impact", "Video is obscured or the camera is damaged", "Measure the lens barrel and screw pattern; run a camera-width coupon and inspect the full intended field of view.", "test_coupon",
        ["Delivered camera fits without board contact and the guard does not vignette the approved field of view through the intended pitch range."], 78),
    iface(
        "IF-INT-DAT-DAT-CAMVTX-001", "analog camera output to video transmitter", "E-COTS-CAM", "E-COTS-VTX", "INT", ["DAT", "ELE", "THM"], "DAT", "MIXED",
        [dim("DIM-VTX-LEN-001", "VTX PCB length", 28.0, URL["vtx"], "FIT_CRITICAL"), dim("DIM-VTX-WID-002", "VTX PCB width", 28.0, URL["vtx"], "FIT_CRITICAL"), dim("DIM-VTX-PAT-003", "VTX mounting-hole pitch", 20.0, URL["vtx"], "FIT_CRITICAL")],
        [URL["camera"], URL["vtx"]], [2, 1, 2, 3, 2, 4], "K2",
        "Video wiring or VTX cooling fails", "FPV image is lost while motion control may remain active", "Keep video independent from balance, strain-relieve antenna, validate supply and cooling at the lawful selected output.", "prototype_test",
        ["Video remains usable through the restrained operating test and VTX temperature stays below the approved component limit; video loss does not block stop/failsafe."], 76),
    iface(
        "IF-ENV-DAT-DAT-VTXRF-001", "video transmitter RF path to supervised environment", "E-COTS-VTX", "E-ENV-GND", "ENV", ["DAT", "ENV", "THM"], "DAT", "FREEFORM",
        [dim("DIM-VTX-PAT-004", "antenna and 20 mm mount reference", 20.0, URL["vtx"], "FUNCTION_CRITICAL")],
        [URL["vtx"], "design-spec.yaml"], [2, 1, 2, 3, 3, 4], "K2",
        "Antenna is blocked, detached or configured unlawfully", "Video is lost, RF hardware is damaged or operation violates local constraints", "Maintain antenna keep-out/strain relief and approve regional settings before any RF test.", "expert_review",
        ["Antenna keep-out is visually clear through all service states and the responsible operator approves the regional channel/power configuration."], 66),
    iface(
        "IF-ENV-MEC-LOD-LNDGRND-001", "landing protection to ground after tip", "E-PRINT-LND", "E-ENV-GND", "ENV", ["MEC", "KIN", "ENV"], "LOD", "FREEFORM",
        [dim("DIM-LND-ANG-001", "minimum planned first-contact tilt angle in degrees represented numerically", 22.0, "design-spec.yaml", "SAFETY_CRITICAL", "DERIVED")],
        ["design-spec.yaml", "validation/v0.1.0-parametric.3/geometry-validation.json"], [2, 3, 3, 4, 3, 4], "K3",
        "Landing part breaks, rolls or contacts too early", "Camera/electronics strike the ground or balance authority is clipped", "Validate printed orientation and impact cycles; keep the skids non-rolling and clear during the approved balance envelope.", "prototype_test",
        ["At nominal assembly the first landing contact is at or beyond 22 degrees; repeated controlled tip tests show no crack and protect camera, battery and electronics."], 70),
]


COTS = [
    ["drive", "MOT-001", "Pololu", "4755", "RETAIN", 2, URL["motor"], URL["motor_drawing"], "36.8 mm body; 73 mm nominal product length; 6 mm D-shaft x 16 mm", 210.0, "ACTIVE_PREFERRED_ON_MANUFACTURER_PAGE", "E3", "not physically confirmed", "IF-INT-MEC-FST-MOTBRKT-001;IF-INT-MEC-ROT-HUBSHFT-001;IF-INT-ELE-PWR-DRVMOTOR-001", "Register official drawing; preserve sample gate", "Measure shaft D/length, boss and bracket seating"],
    ["drive", "BRK-001", "Pololu", "1995", "RETAIN", 2, URL["bracket"], URL["bracket_drawing"], "36.8 x 36.8 x 6.5 mm; three M3 chassis holes at 14.8 mm centers", 14.0, "ACTIVE_ON_MANUFACTURER_PAGE", "E3", "not physically confirmed", "IF-INT-MEC-FST-MOTBRKT-001;IF-INT-MEC-FST-BRKFRM-001", "Use drawing as nominal pod interface", "Measure delivered outline/thickness and run pod coupon"],
    ["drive", "HUB-002", "BaneBots", "T81H-RM61", "SELECT", 2, URL["hub"], URL["hub_cad"], "6 mm shaft; 20.32 mm maximum STEP envelope; two set screws at 90 deg; 3/4 in snap ring", 14.175, "MANUFACTURER_USUALLY_SHIPS_1_TO_3_DAYS", "E3", "not physically confirmed", "IF-INT-MEC-ROT-HUBSHFT-001;IF-INT-MEC-RET-WHLHUB-001", "Replace Pololu 2686/12 mm hex adapter geometry", "Measure bore, engagement and set-screw locations"],
    ["drive", "WHL-002", "BaneBots", "T81P-496BB", "SELECT", 2, URL["wheel"], URL["wheel"], "123.825 mm OD x 20.32 mm width; 60 Shore A; T81 hub mount", 144.582, "MANUFACTURER_USUALLY_SHIPS_1_TO_3_DAYS", "E3", "not physically confirmed", "IF-INT-MEC-RET-WHLHUB-001;IF-ENV-MEC-LOD-WHLGRND-001", "Replace INJORA rim/tire geometry; update wheel proxy and track clearance", "Measure free/loaded diameter, width, mass and retention"],
    ["power", "BAT-001", "Gens ace", "GEA503S60X6GT", "RETAIN_WITH_SOURCE_RISK", 1, URL["battery"], URL["battery"], "154 x 43 x 25 mm", 359.0, "MANUFACTURER_PAGE_AVAILABILITY_CONTRADICTORY", "E3", "not physically confirmed", "IF-INT-MEC-RET-BATCRDL-001;IF-INT-ELE-PWR-BATBUS-001", "Update cradle nominal from retailer envelope to manufacturer envelope", "Confirm order source; measure pack and leads; fit coupon"],
    ["power", "FUS-001", "Littelfuse", "178.6152.0001", "RETAIN", 1, URL["fuse"], URL["fuse"], "official 2D drawing; approximately 23.2 x 20.2 mm body", 23.6, "DRAWING_CURRENT_AVAILABILITY_NOT_ASSERTED", "E3", "not physically confirmed", "IF-INT-ELE-PWR-BATBUS-001", "Register drawing and cable/cover keep-outs", "Measure body, terminals and cover/service access"],
    ["control", "DRV-001", "Pololu", "2507", "RETAIN", 1, URL["driver"], URL["driver_drawing"], "65 x 51 mm PCB nominal drawing", 32.0, "ACTIVE_ON_MANUFACTURER_PAGE", "E3", "not physically confirmed", "IF-INT-ELE-PWR-BUSDRV-001;IF-INT-ELE-PWR-DRVMOTOR-001;IF-INT-DAT-DAT-CTRLDRV-001", "Register official board drawing", "Measure revision, headers and heat-sink envelope; fit coupon"],
    ["power", "BEC-001", "Pololu", "2851", "RETAIN", 1, URL["bec"], URL["bec_drawing"], "20.3 x 17.8 x 8.8 mm", 3.0, "ACTIVE_ON_MANUFACTURER_PAGE", "E3", "not physically confirmed", "IF-INT-ELE-PWR-BUSBEC-001", "Register official board drawing and mounting holes", "Measure headers and installed wire envelope"],
    ["control", "CTL-001", "PJRC", "Teensy 4.1 without headers", "RETAIN", 1, URL["controller"], URL["controller_drawing"], "60.96 x 17.78 mm PCB nominal", 10.0, "MANUFACTURER_PRODUCT_PAGE_ACTIVE", "E3", "not physically confirmed", "IF-INT-DAT-DAT-IMUCTRL-001", "Register official pin/board drawing", "Confirm exact header option and installed height"],
    ["control", "IMU-001", "Adafruit", "4502", "RETAIN", 1, URL["imu"], URL["imu_drawing"], "25.4 x 17.78 mm PCB; two 2.5 mm holes at 20.32 mm centers from official EagleCAD", 3.0, "MANUFACTURER_PAGE_IN_STOCK_AT_CHECK", "E3", "not physically confirmed", "IF-INT-MEC-LOC-IMUDATM-001;IF-INT-DAT-DAT-IMUCTRL-001", "Register official Eagle outline/hole pattern and sensor axes", "Measure delivered revision, PCB, holes, axes and installed connector height"],
    ["radio", "RX-001", "RadioMaster", "RP3 V2 EU-LBT", "RETAIN", 1, URL["receiver"], URL["receiver"], "22 x 13 x 4 mm", 4.6, "EU_LBT_VARIANT_LISTED_AVAILABLE_AT_CHECK", "E3", "not physically confirmed", "IF-HUM-DAT-USR-OPRRX-001", "Register envelope and antenna keep-outs", "Confirm EU-LBT label/revision and antenna lead geometry"],
    ["fpv", "CAM-001", "RunCam", "Phoenix 2 SE V2", "RETAIN", 1, URL["camera"], URL["camera"], "19 x 19 x 22 mm", 8.6, "MANUFACTURER_PRODUCT_PAGE_ACTIVE", "E3", "not physically confirmed", "IF-INT-OPT-VIS-CAMGARD-001;IF-INT-DAT-DAT-CAMVTX-001", "Use manufacturer envelope; keep lens/screw details provisional", "Measure body, lens barrel and screw geometry; fit coupon"],
    ["fpv", "VTX-001", "SpeedyBee", "TX800", "RETAIN", 1, URL["vtx"], URL["vtx"], "28 x 28 mm PCB; 20 x 20 mm M3 mounting pattern", 5.6, "MANUFACTURER_PRODUCT_PAGE_ACTIVE", "E3", "not physically confirmed", "IF-INT-DAT-DAT-CAMVTX-001;IF-ENV-DAT-DAT-VTXRF-001", "Register board/pattern and antenna/cooling keep-outs", "Measure revision, connector height and antenna routing; fit coupon"],
]


def write_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_result():
    scores = {"REQ": 3, "CTX": 3, "PAR": 4, "INT": 4, "CPL": 4, "MOT": 4, "GEO": 2, "PHY": 4, "MAT": 3, "EXT": 4, "VER": 4}
    return {
        "assessment_id": ASSESSMENT,
        "assessment_version": "0.2.0",
        "assessment_date": DATE,
        "product": "TrailCam B2 Balance FPV Rover",
        "scope": {
            "intended_use": "A supervised, low-speed, two-wheel single-axis FPV rover that actively balances as an inverted pendulum on firm level test surfaces.",
            "user_context": "Adult hobby builder and supervised test operator; no autonomous, public-road, stair, human-carrying or unsupervised use.",
            "variants": [REVISION, "Pololu 4755 drive with BaneBots T81H-RM61 hubs and T81P-496BB wheels"],
            "out_of_scope": ["Production or print release", "Powered free-balancing before restrained tests", "Safety, range, runtime or terrain claims", "Printer upload or print start"],
        },
        "entities": [{"id": i, "kind": k, "name": n} for i, k, n in ENTITIES],
        "interfaces": INTERFACES,
        "complexity": {
            "dimension_scores": scores,
            "score_0_100": 91.75,
            "class": "C5",
            "drivers": [
                "INT=4: 18 mechanical, electrical, data, optical, human and environmental interfaces include dynamic and safety-relevant boundaries.",
                "CPL=4: wheel geometry, mass properties, controller model, power integrity and landing envelope propagate changes across the system.",
                "MOT/PHY/EXT/VER=4: active balance couples repeated motion, tire contact, electronics, firmware and a staged verification ladder.",
            ],
        },
        "readiness": {
            "level": "R2",
            "component_levels": {"scope_variant": "R3", "requirements": "R4", "critical_interfaces": "R3", "manufacturing_profile": "R2", "verification": "R3"},
            "blocking_unknowns": [
                "Delivered COTS revisions, tolerances and measured installed envelopes are not confirmed.",
                "BaneBots hub engagement, set-screw registration and snap-ring retention on the Pololu shaft are not physically verified.",
                "With the old axle-relative body unchanged, the 123.825 mm wheel projects an upright height of 251.4125 mm and therefore needs a bom.2 envelope correction to return below 250 mm.",
                "Loaded tire radius, traction, wear and dynamic controller correlation are untested.",
                "Exact Anycubic printer, process and filament JSON profiles are absent.",
                "No restrained electrical, fault-injection, tip, cycle or supervised balance evidence exists.",
            ],
            "completeness_percent": 68.0,
        },
        "criticality": {
            "level": "K3",
            "rationale": "A powered dynamically unstable rover with a LiPo battery can fall, shed a wheel, overheat or move unexpectedly; expert-in-the-loop staged tests and independent cutoff remain mandatory.",
            "credible_failure_effects": ["unexpected motion or impact injury", "LiPo or wiring fire", "wheel or structural separation", "loss of balance and damage to camera/electronics"],
        },
        "gates": {"G0": "PASS", "G1": "PASS", "G2": "WARN", "G3": "FAIL", "G4": "PASS", "G5": "WARN", "G6": "PASS"},
        "decision": {
            "lane": "E",
            "confidence": "NOT_AUTONOMOUSLY_RELEASABLE",
            "design_release": "HOLD",
            "rationale": "Dimensioned official COTS evidence raises the critical hardpoint interfaces to nominal R3, but the project remains R2 because the exact manufacturing profile and physical/dynamic verification are absent; G3 fails and K3 prohibits autonomous release.",
        },
        "warnings": [
            {"code": "PURCHASED_PART_REVISION_UNKNOWN", "severity": "BLOCKER", "message": "Exact delivered variants and tolerances are not sample-confirmed; nominal manufacturer geometry is not a fit release."},
            {"code": "DYNAMIC_OR_FATIGUE_LOAD", "severity": "BLOCKER", "message": "Wheel retention, tire contact, printed pod creep, tip impacts and balance dynamics require staged physical tests."},
            {"code": "MANUFACTURING_PROFILE_INCOMPLETE", "severity": "BLOCKER", "message": "The complete exact Anycubic machine/process/filament profile set is unavailable, so G3 fails and no 3MF/G-code is authorized."},
            {"code": "AUTONOMOUS_RELEASE_PROHIBITED", "severity": "BLOCKER", "message": "K3 powered-vehicle scope requires expert review, controlled prototypes and a human-owned release decision."},
            {"code": "SUPPLY_STATUS_RECHECK", "severity": "WARN", "message": "Availability snapshots are volatile; the Gens ace manufacturer page is internally inconsistent and must be checked before ordering."},
            {"code": "COTS_ENVELOPE_REDESIGN_REQUIRED", "severity": "BLOCKER", "message": "The selected wheel is 3.825 mm larger in diameter and 21.68 mm narrower than the bom.1 proxy; an unchanged body would project to 251.4125 mm upright height, above the 250 mm requirement."},
        ],
        "next_actions": [
            {"priority": 1, "action": "Procure and intake-measure one exact sample of every geometry-owning COTS item, beginning with the T81 wheel/hub and Pololu motor/bracket stack.", "exit_criterion": "Part labels, revisions, mass, critical dimensions, tolerance/uncertainty and photos are recorded; all variant_confirmed fields for the selected drive stack can become true."},
            {"priority": 2, "action": "Update the parametric wheel/hub proxies and printed motor-pod/clearance/roof geometry to bom.2, then rebuild the whole-system mass/COM and control model.", "exit_criterion": "A fresh candidate is at most 250 mm tall and passes the interface graph, envelope, clearance, mass/COM, parameter-sweep and idealized-control checks against measured bom.2 inputs."},
            {"priority": 3, "action": "Print only process-matched interface coupons after supplying a complete Anycubic profile set.", "exit_criterion": "Motor bracket, battery, IMU, driver, camera, VTX and service-panel coupons pass documented fit criteria."},
            {"priority": 4, "action": "Run expert-reviewed wheel-off-ground, restrained power, fault-injection, low-energy tip/cycle and finally supervised free-balance tests.", "exit_criterion": "All interface acceptance criteria pass with logs and independent cutoff available; no release claim is made before human review."},
        ],
        "traceability": {
            "mode": "PROSPECTIVE",
            "project_id": "MM-TOY-003",
            "project_revision": "0.1.0",
            "basis_refs": ["design-spec.yaml", "architecture/bom-procurement-v0.1.0-bom.1.csv", "architecture/cots-interface-register-v0.1.0-bom.2.csv", "architecture/interface-graph-v0.1.0-bom.2.json", "validation/v0.1.0-parametric.3/geometry-validation.json", *sorted(set(URL.values()))],
            "change_triggers": ["dimensioned_cots_interface_review", "wheel_stack_supply_change", "interface_graph_backfill"],
            "previous_assessment_id": "PREFLIGHT-MM-TOY-003-001",
            "created_at": "2026-08-31T12:29:39+02:00",
            "updated_at": STAMP,
        },
    }


def build_graph(result):
    return {
        "schema_version": "1.0",
        "project_id": "MM-TOY-003",
        "revision": REVISION,
        "basis_preflight": ASSESSMENT,
        "status": "CANDIDATE_UNMEASURED",
        "nodes": [{"id": i, "kind": k, "name": n} for i, k, n in ENTITIES],
        "edges": [{"id": x["id"], "source": x["endpoint_a"], "target": x["endpoint_b"], "boundary": x["boundary"], "domains": x["domains"], "function": x["function"], "criticality": x["criticality"], "interface_tier": x["interface_complexity"]["tier"], "evidence_level": x["evidence"]["level"], "variant_confirmed": x["evidence"]["variant_confirmed"], "verification_status": x["verification"]["status"]} for x in result["interfaces"]],
        "graph_metrics": {
            "node_count": len(ENTITIES),
            "edge_count": len(INTERFACES),
            "critical_edge_count": sum(1 for x in INTERFACES if x["criticality"] == "K3"),
            "unconfirmed_variant_edge_count": sum(1 for x in INTERFACES if not x["evidence"]["variant_confirmed"]),
            "max_interface_tier": "I4",
        },
        "change_propagation": [
            {"source_change": "T81 wheel diameter, width, mass or loaded radius", "affected": ["hub retention", "wheel/ground model", "track and pod clearance", "overall width", "upright height", "mass/COM", "controller model", "landing geometry"]},
            {"source_change": "battery size, mass or connector exit", "affected": ["cradle fit", "retention", "disconnect corridor", "mass/COM", "balance gains", "tip behavior"]},
            {"source_change": "IMU PCB revision or axis registration", "affected": ["printed datum", "axis transform", "state estimator", "fault thresholds", "balance verification"]},
            {"source_change": "Anycubic process/material profile", "affected": ["coupon clearance", "pod creep/strength", "landing impact", "all printable fit interfaces"]},
        ],
    }


def build_input():
    return """product: TrailCam B2 Balance FPV Rover
intended_use: >-
  Supervised low-speed two-wheel single-axis FPV rover with active inverted-pendulum balance on firm level test surfaces.
user_context: Adult hobby builder and supervised operator; no autonomous, public-road, stair, human-carrying or unsupervised use.
host_variant:
  manufacturer: Mixed COTS stack
  model: Pololu 4755 / BaneBots T81H-RM61 / T81P-496BB
  revision: 0.1.0-bom.2 candidate
  variant_confirmed: false
lifecycle_states: [transport, assembly, calibration, use, service, disassembly, storage, failure]
requirements:
  - Exactly two independently driven wheels on one geometric axle.
  - IMU-based active upright stabilization with supervised fail-closed testing.
  - Maximum complete design mass 2200 g and COM 70 to 110 mm above axle.
  - Dimension-owning COTS interfaces shall use official drawings/CAD where available.
known_components:
  - Pololu 4755 motor and 1995 bracket
  - BaneBots T81H-RM61 hub and T81P-496BB wheel
  - Gens ace GEA503S60X6GT 3S battery
  - Pololu 2507 motor driver and 2851 regulator
  - Teensy 4.1, Adafruit 4502, RadioMaster RP3 V2, RunCam Phoenix 2 SE V2, SpeedyBee TX800
available_evidence:
  - design-spec.yaml
  - architecture/bom-procurement-v0.1.0-bom.1.csv
  - architecture/cots-interface-register-v0.1.0-bom.2.csv
  - architecture/interface-graph-v0.1.0-bom.2.json
  - validation/v0.1.0-parametric.3/geometry-validation.json
manufacturing_profile:
  printer: unknown exact Anycubic variant/profile
  process: FDM/FFF
  nozzle_mm: 0.6
  material: PETG product not frozen
  orientation_known: true
known_loads_environment:
  loads: [dynamic wheel torque, tire contact, motor vibration, tip impact, battery retention]
  temperature_c: null
  media: [indoor air, clean firm level ground]
  duration: staged prototype only
safety_notes:
  - K3 powered dynamically unstable rover with LiPo energy storage.
  - Human-controlled disconnect and expert-reviewed staged testing are mandatory.
interfaces:
""" + "".join(f"  - {x['id']}\n" for x in INTERFACES)


def build_report(result):
    return f"""# Prospective 3D design preflight — MM-TOY-003 / {REVISION}

`TrailCam B2 Balance FPV Rover | C5 (91.75/100) | R2 | K3 | Lane E | NOT_AUTONOMOUSLY_RELEASABLE`

## Entscheidung

**HOLD.** Der Interface-Graph ist jetzt vollständig genug für eine nachvollziehbare COTS-Integrationsrunde. Offizielle Nennmaße heben die kritischen mechanischen Hardpoints von einer allgemeinen E2-Beschreibung auf **E3 / nominal erfasst**. Das Gesamtprojekt bleibt bei **R2**, weil gelieferte Revisionen und Toleranzen unvermessen sind, der dynamische Rad/Boden- und Regelkreis ungetestet ist und der vollständige Anycubic-Maschinen-/Prozess-/Filamentprofilsatz fehlt. G3 ist deshalb `FAIL`; K3 verbietet eine autonome Freigabe.

Die C5-Einstufung ist kein Qualitätsurteil über das CAD, sondern beschreibt die intrinsische Systemaufgabe: ein absichtlich instabiles Fahrzeug koppelt 18 mechanische, elektrische, Daten-, Optik-, Mensch- und Umweltschnittstellen mit Regelung, LiPo-Energie, Verschleiß und gestuften Tests.

## Scorecard

| Dimension | Wert | Begründung |
|---|---:|---|
| REQ | 3 | Viele gekoppelte Geometrie-, Massen-, Regelungs-, Sicherheits- und Serviceanforderungen. |
| CTX | 3 | Montage, Kalibrierung, Fahrt, Tip-over, Service, Verschleiß und wechselnde Boden-/RF-Bedingungen. |
| PAR | 4 | 19 kundenspezifische Druckteile plus sechs Fit-Coupons. |
| INT | 4 | 18 teils dynamische, multidomänige und verdeckte Schnittstellen; Maximum I4. |
| CPL | 4 | Rad, Batterie und IMU propagieren Änderungen bis in COM, Regler, Schutz und Tests. |
| MOT | 4 | Koordinierte, aktiv geregelte Bewegung mit Radschlupf, Spiel und Tip-Zuständen. |
| GEO | 2 | Überwiegend parametrische Prismen/Zylinder, aber mehrere gekoppelte Einbauräume. |
| PHY | 4 | Dynamik, Vibration, Wärme, Stromversorgung, Reifencontact und Stoß sind gekoppelt. |
| MAT | 3 | PETG-Anisotropie, Metalle, Elastomer, Inserts/Fastener und LiPo verlangen Prozesskontrolle. |
| EXT | 4 | Eng integriertes Motor-/Sensor-/Elektronik-/Firmware-System. |
| VER | 4 | Coupons, Messung, Simulation, Fault Injection, Restrained- und Fahrtests. |

## Reifegewinn und Grenze

| Reifeanteil | Vorher | Jetzt | Aussage |
|---|---:|---:|---|
| Scope/Variante | R3 | R3 | Die `bom.2`-Variante ist eindeutig benannt, aber noch nicht geliefert. |
| Anforderungen | R3 | R4 | Quantitative Grenzen und gestufte Akzeptanzkriterien sind vorhanden. |
| Kritische Interfaces | R2 | R3 | Nenngeometrie und Quellen sind pro Kante registriert; unabhängige Messung fehlt. |
| Fertigungsprofil | R2 | R2 | Exaktes Anycubic-Profilset fehlt weiterhin. |
| Verifikation | R3 | R3 | Kriterien und Leiter sind definiert, Ergebnisse fehlen. |
| **Projekt** | **R2** | **R2** | Minimum-Regel: kein Gesamt-Sprung trotz echtem Interface-Reifegewinn. |

## COTS-Entscheidung

Der bisherige `Pololu 2686 + INJORA CRAW18003/CRAW20161023`-Radstapel wird für `bom.2` durch **BaneBots T81H-RM61 + T81P-496BB** ersetzt. Das System liefert eine 6-mm-Wellenaufnahme, eine zusammengehörige Naben-/Radfamilie, Hersteller-Nennmaße und verlinktes Naben-STEP. Nennwerte je Seite: 123.825 mm Rad-OD, 20.32 mm Breite, ungefähr 144.582 g Rad plus 14.175 g Nabe. Die frühere CAD-Masse von 179 g pro Radstapel sinkt rechnerisch um 20.243 g pro Seite.

Nur durch diesen Massentausch, ohne Geometrie- oder Ballaständerung, ergäbe sich eine **nicht validierte** Aktualisierung von 2114.656 g auf ungefähr **2074.17 g** und von z=71.156 mm auf ungefähr **72.55 mm**. Der größere Radius projiziert die alte 249.5-mm-Bauhöhe zugleich auf **251.4125 mm**, also 1.4125 mm über das 250-mm-Ziel. Das ist kein neuer CAD-Pass: Dach-/Achsgeometrie, die um 21.68 mm schmalere Lauffläche, Nabenregistrierung, Clearances und Schwerpunkt müssen in einer frischen `parametric.4`-Revision neu gerechnet werden.

Nicht gewählt: goBILDA 120-mm-Rhino trotz STEP, weil die Produktseite auf Ersatz/Auslauf hinweist; Studica 110-mm-All-Terrain bleibt eine bemaßte Alternative, besitzt in der vorliegenden Evidenz aber keinen gleichwertig registrierten STEP-/Nabenvertrag.

Vollständige Zeilen, Quellen, Verfügbarkeits-Snapshots und Muster-Gates stehen in `architecture/cots-interface-register-v0.1.0-bom.2.csv`. Der alte `parametric.3`-Stand bleibt als bestandene `bom.1`-Evidenz erhalten, ist für `bom.2` aber **STALE**.

## Funktionale FMEA

| Fehler | Endwirkung | Erkennung | Gegenmaßnahme / Nachweis |
|---|---|---|---|
| Nabe rutscht oder wandert | Rad-/Balanceverlust, Sturz | Witness marks, axial measurement, encoder mismatch | Muster vermessen; beide Stellschrauben und Snapring prüfen; restrained peak-torque/cycle test |
| Reifenradius/Grip weicht vom Modell ab | Capture-Verlust, Sturz | Loaded-radius and traction test, pitch log | Nur sauberer fester ebener Boden; Modell mit Messwerten korrelieren |
| Motorpod kriecht/reisst | Achsfehler und asymmetrisches Drehmoment | Sichtprüfung, witness marks, axis measurement | Coupon, Durchgangsschrauben/Unterlegscheiben, restrained cycle test |
| Batterie löst sich/kurzschließt | Brand oder harter Leistungsabfall | Inspektion, continuity/current/temp log | Zwei mechanische Rückhaltepfade, Sicherung nahe Pack, erreichbarer Trennstecker |
| IMU-Datum oder Achsenabbildung falsch | Regler verstärkt den Fall | statische Achsenprüfung, stale-data/fault injection | starres gekeytes Datum, dokumentierte Transformation, arming interlock |
| Driver/BEC brownout oder überhitzt | Torque-Verlust oder Reset | EN/DIAG, current sense, rail/temperature log | restrained reversals, unabhängiger cutoff, Freigabegrenzen |
| RC/FPV fällt aus | Stopbefehl/Ansicht verloren | link-health and video-loss injection | RC failsafe unabhängig vom Video; Sichtkontakt; Trennstecker |
| Landeschutz bricht | Kamera/Elektronik schlagen ein | low-energy controlled tip cycles | Druckorientierung freigeben, wiederholter Tip-Test, reject-on-crack |

## Hard Gates

| Gate | Ergebnis | Begründung |
|---|---|---|
| G0 Scope | PASS | Zweck, Nutzer und ausgeschlossene Anwendungen sind benannt. |
| G1 Entitäten/Interfaces | PASS | 22 Knoten und 18 Kanten sind maschinenlesbar erfasst. |
| G2 Evidenz | WARN | Offizielle Nenngeometrie ist brauchbar; Musterrevision/Toleranzen fehlen. |
| G3 Fertigungsprofil | FAIL | Vollständige exakte Maschine/Prozess/Filament-JSON-Profile fehlen. |
| G4 Verifikation | PASS | Jede Kante besitzt messbare Kriterien und eine Methode. |
| G5 Autonomie | WARN | K3 verlangt Expert-in-the-loop; autonome Freigabe ausgeschlossen. |
| G6 Lebenszyklus | PASS | Montage, Kalibrierung, Nutzung, Service, Demontage und Fehler sind berücksichtigt. |

## Minimaler nächster Nachweis

Zuerst je ein exaktes T81-Rad, T81H-RM61-Nabe, Pololu-4755-Motor und 1995-Bracket beschaffen und als zusammengebauten Antriebsstapel vermessen. Exit: Label/Revision, Masse, Rad-OD/Breite, belasteter Radius, Nabenbohrung, Wellenengriff, Stellschraubenlage, Snapring-Sitz, Axialspiel und Fotos sind mit Messunsicherheit dokumentiert. Erst dann darf `variant_confirmed` für die Antriebskanten auf `true` wechseln und das Druck-CAD an `bom.2` angepasst werden.
"""


def build_graph_md(graph):
    node_index = {node["id"]: f"N{i:02d}" for i, node in enumerate(graph["nodes"], 1)}
    lines = [
        f"# Interface graph — MM-TOY-003 / {REVISION}", "", "Status: `CANDIDATE_UNMEASURED`; authority: `preflight/preflight-result.json`.", "", "```mermaid", "flowchart LR"
    ]
    for node in graph["nodes"]:
        lines.append(f'  {node_index[node["id"]]}["{node["name"]}"]')
    for edge in graph["edges"]:
        label = f'{edge["id"]}<br/>{edge["criticality"]}/{edge["interface_tier"]}/{edge["evidence_level"]}'
        lines.append(f'  {node_index[edge["source"]]} -->|"{label}"| {node_index[edge["target"]]}')
    lines += ["```", "", "## Interface register", "", "| ID | A → B | Domains | K/IC/E | Verification |", "|---|---|---|---|---|"]
    names = {node["id"]: node["name"] for node in graph["nodes"]}
    for edge in graph["edges"]:
        lines.append(f'| `{edge["id"]}` | {names[edge["source"]]} → {names[edge["target"]]} | {", ".join(edge["domains"])} | {edge["criticality"]}/{edge["interface_tier"]}/{edge["evidence_level"]} | {edge["verification_status"]} |')
    lines += ["", "## Change propagation", ""]
    for row in graph["change_propagation"]:
        lines.append(f'- **{row["source_change"]}:** {" → ".join(row["affected"])}')
    lines += ["", "All 18 interface variants are intentionally unconfirmed. The graph may drive CAD decomposition and intake planning, but it is not a release graph until delivered-part measurements and the planned verification results are linked.", ""]
    return "\n".join(lines)


def build_cots_report():
    return f"""# Dimensioned COTS selection — MM-TOY-003 / {REVISION}

Checked {DATE}. Availability is a volatile snapshot, not a procurement guarantee. Manufacturer pages and manufacturer drawings/CAD are preferred over marketplace listings; delivered samples remain the physical interface authority.

## Selected drive stack

- **Motor:** Pololu 4755, 37D encoder gearmotor, 6 mm D-shaft, official dimension drawing.
- **Bracket:** Pololu 1995 machined 37D bracket, official dimension drawing.
- **Hub:** BaneBots T81H-RM61, 6 mm shaft, two set screws at 90°, 3/4-inch snap-ring retention, linked STEP/3D model.
- **Wheel:** BaneBots T81P-496BB, 4-7/8 inch (123.825 mm) OD, 0.8 inch (20.32 mm) width, 60A, T81 hub mount.

This replaces the `bom.1` INJORA beadlock/hex stack for the next CAD revision. The new family has a direct, coherent wheel-to-hub contract and better dimensional provenance. It also reduces nominal installed wheel/hub mass by about 40.49 g total and nominal overall width at 216 mm wheel-center track from 258 mm to **236.32 mm**. These are arithmetic estimates only.

## Evidence quality

- E3 means official nominal geometry is sufficient to create a controlled CAD candidate.
- `variant_confirmed=false` means no delivered sample, revision or tolerance has been measured.
- The BaneBots hub viewer exposes a source named `T81H-RM61.stp`; the derived maximum envelope is 20.32 mm. Supplier CAD is referenced, not vendored, and does not override sample measurements.
- The Gens ace page lists the dimensional candidate but shows conflicting availability language; verify before ordering or nominate a dimensionally equivalent pack only through a new change review.
- The Adafruit 4502 official EagleCAD/Fab Print gives a 25.4 x 17.78 mm outline with two 2.5 mm holes at 20.32 mm centers. The delivered PCB revision, axis registration and installed connector height still require intake measurement.

## Rejected/alternate wheel candidates

| Candidate | Positive | Reason not selected |
|---|---|---|
| goBILDA Rhino 120 mm | Official STEP and dimensions | Current manufacturer page indicates replacement/roll-away status, weakening repeat procurement. |
| Studica 76250 110 mm all-terrain | Current dimensioned product, direct 6 mm adapter | No equivalent registered STEP/tolerance contract in the captured evidence; retain as alternate. |
| Existing INJORA CRAW18003 + CRAW20161023 | Matches current 120 × 42 CAD envelope | Selected rim variant was out of stock and the cross-brand Pololu hex stack has weaker dimensional authority. |

## Mandatory intake fields

Photograph label/package; record source/date/revision; weigh each item; measure all fit-critical geometry with the instrument and uncertainty noted; retain manufacturer files by URL/hash where licensing permits; then update the graph edge evidence. Do not copy marketplace CAD into the release package without provenance and license review.
"""


def main():
    result = build_result()
    graph = build_graph(result)
    write_json(ROOT / "preflight/preflight-result.json", result)
    (ROOT / "preflight/preflight-input.yaml").write_text(build_input(), encoding="utf-8")
    (ROOT / "preflight/preflight-report.md").write_text(build_report(result), encoding="utf-8")
    write_json(ROOT / "architecture/interface-graph-v0.1.0-bom.2.json", graph)
    (ROOT / "architecture/interface-graph-v0.1.0-bom.2.md").write_text(build_graph_md(graph), encoding="utf-8")
    (ROOT / "reports/dimensioned-cots-selection-v0.1.0-bom.2.md").write_text(build_cots_report(), encoding="utf-8")
    columns = ["subsystem", "item_id", "manufacturer", "mpn", "selection", "quantity", "official_product_url", "official_drawing_or_cad_url", "declared_geometry_mm", "installed_mass_g_each", "availability_snapshot", "evidence_level", "variant_status", "interface_ids", "cad_action", "physical_gate", "checked_date"]
    with (ROOT / "architecture/cots-interface-register-v0.1.0-bom.2.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(columns)
        for row in COTS:
            writer.writerow([*row, DATE])


if __name__ == "__main__":
    main()
