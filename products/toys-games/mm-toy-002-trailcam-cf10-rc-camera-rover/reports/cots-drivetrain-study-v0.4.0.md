# MM-TOY-002 COTS drivetrain study — revision 0.4.0

Date: 2026-08-30

Scope: official-source research for the confirmed double-wishbone route

Decision class: digital envelopes only; no purchase, fit, load or manufacturing approval

## Selected envelope architecture A

Use one chassis-fixed geared motor per axle, a purchased 1:1 metal right-angle
gear pair, a supported metal cross-shaft acting as a locked spool, and two
purchased articulated halfshafts.  This retains the approved two-motor/no-diff
architecture while allowing both wheels on an axle to move independently.

| Function | Official candidate and documented facts | Gate |
|---|---|---|
| Geared motor | [Pololu #4743](https://www.pololu.com/product/4743), 12 V, 50:1, 200 rpm no-load, 6 x 16 mm D-shaft, six M3 face holes with 15.5 mm adjacent spacing and 3 mm maximum screw penetration. The [official 37D drawing](https://www.pololu.com/file/0J1735/37d-metal-gearmotors-dimension-diagram.pdf) gives 34.8 mm body diameter, 36.8 mm flange, 24.0 mm gearbox length for 50:1, 30.7 mm motor length and a 22 mm front-output envelope. | `GO-D` conservative CAD envelope only. Continuous load, thermal behavior, torque margin and mounting access are not validated. |
| Right-angle gears | [ServoCity 6 mm-bore 2317-0006-0024](https://www.servocity.com/2317-series-mod-0-8-steel-miter-gear-set-screw-6mm-round-bore-24-tooth/) plus [5 mm-bore 2317-0005-0024](https://www.servocity.com/2317-series-mod-0-8-steel-miter-gear-set-screw-5mm-round-bore-24-tooth/): steel, MOD 0.8, 24 teeth, nominal 1:1/90 degrees, 20 mm back-face-to-mating-axis datum. | `GO-D` envelope only. Thrust reaction, set-screw flats, runout, guarding and retention need a physical bench fixture. |
| Locked spool stock | [ServoCity 2100-0005-0050](https://www.servocity.com/5mm-shaft-stainless-steel-50mm-length/), 5 x 50 mm stainless shaft, supported by [5 x 10 x 4 mm bearings 1600-0410-0005](https://www.servocity.com/5mm-id-x-10mm-od-non-flanged-ball-bearing-2-pack/). | Shaft-end geometry, axial retention and cup adapters are unresolved. Any cutting/flat machining must be documented as a separate fabrication step. |
| Halfshafts | Two [RC4WD VVV-S0183](https://store.rc4wd.com/Mega-Truck-Universal-Shaft-Ver-2-55mm--70mm-217--276-5mm_p_5419.html), officially listed as 55–70 mm long, 10 mm body diameter, 5 mm end bores, 27 g and retained with M3 x 3 set screws. | `REVIEW_REQUIRED`. The supplier does not publish a STEP model, usable joint angle, torque rating, minimum spline engagement, running clearance or plunge limit under articulation. |

At the documented 200 rpm with a 1:1 final transfer, the ideal no-load speeds
are 3.39 km/h for a 90 mm tire and 4.34 km/h for a 115 mm tire.  These are
kinematic calculations, not a formal 5 km/h compliance claim: motor tolerance,
battery voltage, tire growth, load and controller behavior are not included.

The v2 skeleton currently reports its own inner-to-outer halfshaft proxy rather
than claiming the RC4WD part fits.  The published 55–70 mm range is useful only
for selecting the next physical sample.  Exact spool-end, cup, outer-joint,
stub-axle and wheel-backspacing locations must be measured together before the
interface is frozen.

## Rejected or secondary candidates

- The goBILDA 5203 Yellow Jacket 26.9:1 motor is a useful benchmark but its
  official envelope and 437 g mass are substantially larger than the Pololu
  candidate.  It is not the current packaging baseline.
- A Traxxas 1/16 drivetrain family offers a locker, ring/pinion, halfshafts,
  stub axles, 12 mm hexes and bearings, but no official dimensioned motor-to-
  pinion or housing interface was found.  It is `FAIL-D` until a sample is
  measured.
- A Kyosho FZ02 corner family documents an approximately matching 164 mm track,
  while FZ02L-BT wheels reach the requested 105–110 mm diameter only at much
  wider 235–250 mm tracks.  Kyosho does not document the mixed combination or
  the required upright/CVD dimensions; it is not an interface authority.
- Tamiya TT-02 direct coupling item 22047 is a coherent locked-spool family,
  but the motor-to-pinion adapter and installed cup/shaft dimensions remain
  undocumented for this rover.  It remains a sourcing reference, not the v2
  baseline.

## Required sample measurements before part CAD

1. RC4WD shaft minimum and maximum running length at 0, 10, 20 and 25 degrees;
   spline engagement, play, OD sweep and set-screw/flat geometry.
2. Complete cross-shaft stack: bearing shoulders, gear location, axial clips,
   adapter cups and thrust path under forward/reverse load.
3. Wheel/hub stack: bearing IDs/ODs/widths, axle length, 12 mm hex or alternate
   drive, rim cavity, backspacing and tire deflection envelope.
4. Upper/lower spherical-joint centers, angular travel, retention and printed
   seat coupon results.
5. Shock compressed/extended eye-to-eye length, body/spring OD and end-joint
   angular range.

No supplier CAD is copied into the repository.  The project exports contain
only analytic, conservatively labelled proxy geometry.
