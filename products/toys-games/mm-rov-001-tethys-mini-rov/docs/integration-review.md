# Tethys Mini ROV integration review

Date: 2026-08-29

## Evidence result

- The archive and extracted package are file-for-file consistent.
- All nine included unit tests pass: CAD-source checks, mesh-manifest checks and
  control-protocol round trips, CRC rejection, mixing, sequence and arming gates.
- A clean temporary run of `cad/generate_parts.py` reproduced all 13 STL files
  and `mesh_manifest.json` byte-for-byte; the archived import was not rewritten.
- Independent release-profile audits load all 13 STLs successfully. All are
  watertight, single-component meshes with zero boundary/nonmanifold edges.
- Three meshes have consistent winding and positive volume. Ten are watertight
  but require review for inconsistent face winding/positive-volume orientation.
- The 13 STLs total 2,565,896 faces and 128,295,892 bytes. This is much heavier
  than necessary for many functional parts and should be evaluated against exact
  slicer resolution after topology is corrected.
- There is no exact Anycubic slice, purchased-part measurement, vacuum/leak test,
  thrust/current curve, trim record or physical water-trial evidence.

## Improvements captured at requirements level

- Preserve the Ethernet tether as the primary submerged control/video link.
  Put any Wi-Fi/ELRS bridge on an optional buoy above the waterline.
- Correct face orientation in the parametric generator and regenerate all ten
  affected meshes; do not silently repair the archived reference STLs.
- After clean topology, compare a bounded manufacturing-mesh simplification
  against the masters while protecting every WTE, tube, motor, guard, tether and
  fastener interface.
- Measure one thruster, propeller, ESC and cable/penetrator set before buying the
  full system, then update the authoritative component envelopes.
- Keep the purchased 75 mm WTE and cable-matched penetrators. Do not replace the
  pressure boundary or propellers with printed parts.
- Add explicit neutral-on-loss, BEC brownout, tether load, vacuum, leak, thrust,
  passive-righting and staged-depth evidence before water release.

No generator or mesh was changed because the guided workflow still requires
explicit requirements and concept approval.
