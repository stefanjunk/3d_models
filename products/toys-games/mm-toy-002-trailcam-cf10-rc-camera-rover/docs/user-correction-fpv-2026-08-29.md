# User correction trace — FPV and shared vehicle components

Date: 2026-08-29

## Earlier system proposal

TrailCam revision 0.2.0 treated the product as an RC camera-rover payload with a
provisional generic 19 mm camera, independent RC/video links and an unresolved
camera/VTX/receiver stack. The loose OpenQuad BOM was correctly identified as
not belonging to TrailCam, but no cross-product component-family contract was
created. OpenQuad and the separate Tethys submarine were still loose packages.

## User correction

- TrailCam shall be specifically designed for FPV with a camera.
- It should ideally use components similar to the flight drones, particularly
  the control-radio module and camera transmission.
- Integrate the flight drone and the other remote-controlled submarine; the
  flapping-tail submarine is already integrated and is not the requested one.

## Normalized response in revision 0.3.0

- OpenQuad is integrated as `MM-DRN-001`; its later FPV BOM supplies the
  provisional air/ground reference stack.
- Tethys is integrated as `MM-ROV-001` and identified as the separate submarine.
- TrailCam explicitly uses FPV as a core function and provisionally shares the
  RunCam Phoenix 2 SE V2, SpeedyBee TX800, analog goggles/display and the
  EdgeTX/ExpressLRS 2.4 GHz LBT ecosystem with OpenQuad.
- Receivers and controller ergonomics remain platform-specific: serial CRSF and
  twin-stick for air; PWM and surface controls for ground.
- Tethys remains Ethernet-tethered under water. RF reuse is limited to an
  optional surface buoy because 2.4/5.8 GHz is not a viable submerged primary
  control/video architecture.

Status: normalized requirements draft, pending explicit user approval. No new
production CAD or imported safety-critical geometry was changed.
