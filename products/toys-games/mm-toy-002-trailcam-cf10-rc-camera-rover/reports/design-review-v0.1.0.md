# TrailCam CF10 v0.1.0 design review

Review date: 2026-08-29

Reviewed evidence: legacy PDF SHA-256 `21224fbd4c396d79fae382f0cd77d4781f239ec4e05c511b2a5549d49f31c4b5`

## Outcome

The system architecture is directionally sound: purchased crawler drivetrain,
printed interface nodes, purchased rails, independent RC/video paths, fit
coupons and staged testing are appropriate. The repository package is not a
reproducible design, however. Only the report is present, so none of its ten STL
or generator claims can be independently rerun or accepted.

## Findings

| Priority | Finding | Design impact | Revision 0.3.0 response |
|---|---|---|---|
| Blocker | Claimed generator, JSON parameters, ten STL files, validation reports, product BOM and license are absent | No editable source, no artifact hash chain and no reproducible digital candidate | Rebuild from an approved measured contract; retain the PDF as legacy evidence only |
| High | The report places a 2S pack on the upper payload rails | Raises the center of gravity and rollover energy | Keep the traction battery at the lowest approved COTS chassis position |
| High | A 1 kg deck test is named, but no nominal payload, dynamic load case or reliable chassis load path is defined | A passing deck alone would not show that bodyposts, clamps or the chassis interface are safe | Define 500 g recommended service payload, 1 kg proof load and a measured frame/hardpoint adapter, subject to approval |
| High | Bodyposts appear to carry the payload frame | Bodyposts are not accepted as structural crash/load anchors without exact evidence | Use them only as locators unless a dedicated measured/load-tested light-payload variant passes |
| Medium | Camera is exposed at the front and cable/impact paths are not shown | Lens damage, cable snagging and detached fragments are foreseeable | Add a replaceable radiused guard, strain relief and optical-field keep-out |
| Medium | The rail clamp result is shown but its split, fastener bearing, nut capture, torque and layer orientation are not evidenced | Clamp cracking, creep or slip can release the payload | Use M3 metal through-fasteners, continuous clamp load paths, local pads/gussets and a 50 N slip coupon |
| Medium | The reported 42.2% saving is CAD volume only | It does not establish print-time, deposited mass, support burden or retained stiffness | Recreate a baseline and compare process-only, geometry-only and combined candidates with exact slicer profiles |
| Medium | VTX cooling, antenna keep-out and cable motion clearances are prose-only | Video loss, heat failure or mechanical interference may occur | Convert them to explicit envelopes and thermal/range/motion acceptance checks |
| High | FPV was not a core requirement and no exact radio/video family was selected | Mounts, cooling, power and failure behavior could be designed around incompatible placeholders | Use the OpenQuad RunCam Phoenix 2 SE V2/TX800 analog-FPV reference and the EdgeTX/ELRS family, subject to exact measurement and legal/electrical verification |
| High | “Similar drone components” did not distinguish exact reuse from platform-specific interfaces | A serial aircraft receiver or twin-stick control layout could be incorrectly treated as a surface-vehicle drop-in | Share the ELRS ecosystem, camera, VTX and goggles; use a surface PWM receiver and surface controls for TrailCam; keep propulsion/video independent |
| Medium | Several COTS, price, firmware and legal statements are dated 2026-08-13 | Procurement and operating assumptions can become stale | Re-verify primary manufacturer/regulatory sources before BOM freeze; no purchase recommendation is approved here |

## Protected geometry for the redesign

- Chassis mounting datums and every steering/suspension/wheel/driveshaft envelope.
- Battery position, access and visible emergency disconnect.
- Rail alignment, clamp bores, split planes, fastener seats and tool access.
- Camera optical field, antenna active-element keep-out and cable bend radii.
- Continuous deck edge beams, load-oriented ribs and local interface pads.
- Bed faces and the future product-marking safe region.

## Planned comparison

The legacy geometry cannot be an exact baseline because it is missing. After
requirements and concept approval, revision 0.3.0 will establish a reproducible
reconstructed baseline and compare:

1. process-only 0.4/0.6 mm nozzle candidates;
2. geometry-only edge-beam/rib/window/load-pad candidate;
3. combined candidate; and
4. conservative frame-adapter and camera-guard candidate for physical proof.

No candidate will be called improved merely because it is lighter. Interface,
motion, stiffness, slip, impact, slicer and physical constraints must pass.
