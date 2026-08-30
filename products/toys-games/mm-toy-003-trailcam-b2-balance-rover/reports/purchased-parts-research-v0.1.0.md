# Purchased-parts research — MM-TOY-003 v0.1.0

Date checked: 2026-08-30

Status: decomposition research; candidates are not qualified inventory records

Only manufacturer sources are used below. A supplier page or STEP file is not a
substitute for measuring the delivered part, recording its revision and testing
its relevant electrical/mechanical behavior.

## Candidate findings

| Function | Candidate and official evidence | Useful evidence | Decision |
|---|---|---|---|
| Encoder gearmotor, two required | [Pololu 100:1 37D 12 V encoder gearmotor, item 4755](https://www.pololu.com/product/4755/resources) | 102.08:1 ratio, 100 rpm no-load at 12 V, 5.5 A extrapolated stall current, 34 kg·cm extrapolated stall torque, 64 CPR motor-shaft encoder and about 6533 CPR at the output; 6 mm D-shaft | Provisional best-fit speed-class candidate. Purchase two and characterize torque/current/temperature; stall values are not continuous ratings. |
| Motor envelope | [Pololu 37D dimension drawing and datasheet](https://www.pololu.com/file/0J1736/pololu-37d-metal-gearmotors-rev-1-2.pdf) and [official family datasheet](https://www.pololu.com/file/0J1706/pololu-37d-metal-gearmotors.pdf) | Supplier-controlled flange, body, shaft and encoder-envelope data are available; encoder versions are roughly 200–210 g depending on version | Import supplier STEP only as a purchased-part reference and confirm critical dimensions on both samples. |
| Metal motor bracket, two required | [Pololu machined aluminium bracket, item 1995](https://www.pololu.com/product/1995/1461) | Six motor holes and three tapped M3 chassis holes; supplier states 14.8 mm bottom-hole spacing and includes motor screws | Provisional. The metal bracket owns its mating pattern; printed chassis uses measured clearance holes and load-spreading seats. |
| Main controller | [PJRC Teensy 4.1](https://www.pjrc.com/store/teensy41.html) and [PJRC board dimensions](https://www.pjrc.com/teensy/dimensions.html) | 600 MHz Cortex-M7 class controller and official board dimensions | Provisional. Deterministic timer, encoder, SPI, watchdog and logging implementation still needs a firmware proof. |
| IMU sensor | [TDK InvenSense ICM-42688-P](https://www.invensense.tdk.com/en-us/products/consumer/icm-42688-p/) | Production six-axis device; manufacturer lists low gyro/accelerometer noise and SPI up to 24 MHz | Sensor family candidate only. No exact small carrier board is frozen; carrier mounting, regulator, level shifting, axes and actual noise must be qualified. |
| Dual motor driver | [Cytron MDD10A](https://my.cytron.io/p-10amp-5v-30v-dc-motor-driver-2-channels) | Two brushed DC channels, 5–30 V for current revision, 10 A continuous and 30 A peak per channel, 3.3/5 V logic, regenerative braking and PWM to 20 kHz; the supplier warns that reverse-polarity protection is absent | Provisional electrical-current-class candidate only. It does not satisfy current telemetry/fault reporting by itself; add qualified sensing and a motor-enable safety path or replace it. Regeneration and disconnect behavior remain open. |
| FPV camera | [RunCam Phoenix 2 Special Edition](https://shop.runcam.com/runcam-phoenix-2-special-edition/) | Manufacturer lists 19 × 19 × 22 mm, 8.6 g and 5–36 V input | Provisional. Measure exact V2 unit, lens protrusion, screw axes, connector and field of view. |
| Video transmitter | [SpeedyBee TX800](https://www.speedybee.com/speedybee-tx800/) | Manufacturer lists a 28 × 28 mm PCB, 20 × 20 mm mounting, 5 V supply, 5.6 g and 48 channels | Provisional. Qualify exact revision, cooling, antenna connector, local legal configuration and interaction with control electronics. |
| RC receiver | [RadioMaster ER5C](https://www.radiomasterrc.com/products/er5c-elrs-pwm-receiver) | Manufacturer lists 37 × 19 × 13 mm, 6.6 g, 4.5–8.4 V and 2.4 GHz ELRS PWM operation | Provisional. Freeze protocol/channel mapping and prove explicit link-health and failsafe behavior; a serial receiver may be preferable after timing review. |
| Wheels and hubs | No exact manufacturer-backed candidate frozen | Required planning envelope is 120 × 40 mm per wheel with 205 mm center track. The motor has a 6 mm D-shaft; a metal hub is mandatory. | Open and CAD-blocking. Obtain supplier drawings and two samples; measure runout, mass, inertia, tire stiffness/grip and axial retention. |
| Battery and power protection | No exact manufacturer-backed pack, BEC, fuse, current sensor or disconnect frozen | Packaging assumes a centered 3S-LiPo-class module with ±12 mm longitudinal trim. | Open and powered-test-blocking. Close the complete power budget, regeneration transient, fuse/disconnect topology, current sensing and undervoltage behavior first. |

## Selection implications

At 100 rpm a 120 mm wheel has an ideal no-load ground speed of approximately
2.26 km/h, close to the 2.5 km/h product limit. The 100:1 Pololu candidate is
therefore better aligned with the target than a substantially faster gearbox,
but no-load speed is not a loaded vehicle-speed guarantee.

Two motor stall currents would total approximately 11 A if both channels reached
the supplier's extrapolated point. The MDD10A current class is not, by itself,
evidence for safe operation: wiring, connectors, pack, fuse, sensors, firmware
limits, cooling and regenerative transients all share the current path.

The controller and IMU choices are deliberately separable. The exact IMU
carrier is an interface owner because its mounting holes, axis marks, regulator,
logic levels and mechanical noise path affect both CAD and control performance.

## Intake evidence required before exact CAD

- Part identity, supplier/manufacturer, order link, revision and received date.
- Photographs, mass and caliper measurements of every interface-owning sample.
- Supplier drawing/STEP hash and any discrepancy from the physical sample.
- Motor/encoder polarity, counts, runout and restrained electrical/thermal logs.
- Wheel/hub retention, runout, tire diameter under load, mass and inertia estimate.
- PCB mounting patterns, connector envelopes, cable bend radii and cooling zones.
- Battery, BEC, fuse, current-sensor and disconnect schematic with regeneration review.

Until those records exist, candidate geometry remains a proxy and the component,
integration, physical and release gates remain blocked.
