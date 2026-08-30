# Decomposition approval review — MM-TOY-003 v0.1.0

Candidate: `0.1.0-decomposition.1`

Status: pending explicit approval

## Approval requested

Approve the following as the basis for deterministic proxy and production-CAD
work:

- exactly two independently driven wheels on one axle-centered Y datum;
- a five-part parametric printed chassis set with separate battery cradle,
  control/IMU tray, camera guard and two non-rolling landing parts;
- metal motor brackets, encoder gearmotors, metal hubs, wheels, electronics,
  battery/power hardware, RF parts and fasteners as purchased components;
- purchased parts own their exact interfaces; the concept image owns appearance
  direction only and creates no geometry;
- 15 component groups, 21 owned interfaces and 11 keep-outs from the validated
  hybrid plan;
- cascaded velocity, pitch/rate and yaw control behind a supervisory state
  machine, with no direct RC-to-motor PWM;
- non-rolling landing protection that remains clear through normal motion and
  contacts no earlier than 22 degrees pitch;
- the documented staged test ladder and its fail-closed physical gates.

## Provisional choices carried forward

- Pololu item 4755 100:1 encoder gearmotors and item 1995 metal brackets.
- Teensy 4.1, ICM-42688-P-class SPI IMU carrier and Cytron MDD10A-class motor
  driver.
- RunCam Phoenix 2 SE V2, SpeedyBee TX800 and RadioMaster ER5C-class receiver.

These choices authorize only parameterized planning proxies after decomposition
approval. Exact supplier revision, delivered-part measurements and qualification
still own every production interface.

## Still open after approval

- exact 120 mm wheel and metal 6 mm D-shaft hub system;
- exact IMU carrier and qualified current/fault sensing or a replacement driver;
- battery, BEC, fuse, current sensor, regeneration and disconnect topology;
- measured mass, inertia, center of mass and loaded wheel radius;
- complete Anycubic machine/process/filament profiles and process coupons;
- restrained tuning rig, control tuning, fault injection and all physical tests.

Approval does not authorize a purchase, print start, powered balance test,
safety claim, watermark or release. It permits the next deterministic phase:
parametric proxy/control-model work with the open interfaces remaining blocked.
