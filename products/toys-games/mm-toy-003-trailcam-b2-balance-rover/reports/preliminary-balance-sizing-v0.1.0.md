# Preliminary balance sizing — MM-TOY-003 v0.1.0

Status: order-of-magnitude architecture check only

## Wheel speed

For wheel diameter `d = 0.120 m` and output speed `n = 100 rpm`:

`v = π d n / 60 = 0.628 m/s = 2.262 km/h`

The requested 2.5 km/h limit corresponds to approximately 110.5 rpm at the same
diameter. The provisional 100:1 motor candidate therefore occupies the intended
low-speed region without treating no-load speed as a guaranteed loaded result.

## Static pitch-disturbance torque

The gravitational pitch torque of a body of mass `m` with center of mass `h`
above the axle at lean angle `θ` is:

`τ_total = m g h sin(θ)`

Assuming equal left/right sharing, each motor supplies half:

| Case | Inputs | Total static torque | Per wheel |
|---|---|---:|---:|
| Target | 1.8 kg, 90 mm, 12° | 0.330 Nm | 0.165 Nm |
| Conservative envelope | 2.2 kg, 110 mm, 12° | 0.494 Nm | 0.247 Nm |

Against the 0.35 Nm continuous design target, these simplified static margins
are approximately 2.12× and 1.42× respectively. They do not include commanded
acceleration, wheel/tire inertia, gearbox loss, terrain disturbance, motor
heating, battery sag, saturation or control delay, so they cannot qualify a
motor or prove balance stability.

## Consequences for the next phase

- Keep the center of mass within the 70–110 mm vertical band and close the mass
  ledger before committing the upper-frame shape.
- Preserve ±12 mm battery trim and a lateral offset measurement method.
- Model real motor electrical dynamics, driver limits, delay and output
  saturation before tuning the inner loop.
- Use purchased-sample dynamometer and thermal evidence instead of extrapolated
  stall torque as the continuous operating point.
- Update these calculations from measured wheel radius under load and measured
  total/body mass before the integration gate.
