# 3D-design preflight 0.5.3 — MM-ART-010 water/transit and topology-bridge correction

`MM-ART-010 | C3 (65.0/100) | R2 | K2 | Lane C | LOW_UNKNOWN`

## Decision

- Design release: `GO_WITH_CONTROLS`
- Requirements: approved from the user's explicit 2026-09-04 correction
- Concept gate: approved for `concepts/berlin-water-transit-concept-v07.png`
- Decomposition gate: approved for `plan/hybrid-design-plan-v0.5.3.json`
- Manufacturing geometry: authorized under source, topology, mesh and target-slicer controls
- Previous candidate: revision 0.5.1 `digital-candidate-r4` is rejected for production

Revision 0.5.1 is mesh-readable, but it is not a correct Berlin map: the extractor processed river/canal lines but no OSM water-area multipolygons, so Tegeler See relation `451908` and other lakes could not reach the aperture mask. Tool 4 also received motorway/trunk accent geometry instead of S-Bahn/U-Bahn routes.

The corrected revision 0.5.3 contract is:

| Output | Semantic owner |
|---|---|
| Tool 1 / Oak | Land base |
| Tool 2 / Mint Green | Middle relief and area level |
| Tool 3 / Midnight | Street network including motorway/trunk |
| Tool 4 / Sky Blue | S-Bahn and U-Bahn route relations, plus the existing context boundary and site marker |
| Negative geometry | Every retained mapped water area and river/canal/stream |

All-water openings are compared in three structural candidates. The selected default is the least-material candidate that leaves one connected printable body per half: openings only where possible, plus 2.0 mm full-thickness topology bridges only where land would otherwise detach. No rear grid or blanket rib network is allowed. Local rear ribs remain conditional because they conflict with rear-datum-down printing and halo lands.

## Source evidence and limitation

The frozen local Berlin PBF contains 1,816 selected water-area features, 1,277 river/canal/stream lines, 38 direction-specific S-Bahn route relations and 18 U-Bahn route relations. Tegeler See is present as a non-empty 3,819,800.57 m² polygon. This proves the classification and the named regression fixture.

The local PBF does not cover the complete 12-percent `context_outline` margin. Official same-date Berlin and Brandenburg extracts have now been reacquired. Their bounded derivatives, hashes and complete context coverage must pass before production geometry.

## Verification contract

- Every water source component must be retained, intentionally bridged for a documented keep-out/ligament reason, or explicitly reported as removed.
- Tegeler See relation `451908` must create nonzero through-part geometry in both display modes.
- Tool 4 must contain S-/U-Bahn route relations and no independent motorway accent layer.
- Motorway/trunk must remain in tool 3.
- Both halves must remain connected, keep at least 5 mm protected ligament and stay below the 12-percent open-area cap.
- Every inserted topology bridge must report half, coordinates, width, reason and restored area.
- Each half remains independently hung; the center seam is not the primary gravity load path.
- New 3MFs require four-body geometry validation and fresh `slice-anycubic-next` evidence; historical 0.5.1 slices do not count.

## Hard gates

| Gate | Status |
|---|---|
| G0 scope/variant | PASS |
| G1 entities/interfaces | PASS |
| G2 critical evidence | WARN |
| G3 manufacturing profile | WARN |
| G4 verification definition | PASS |
| G5 autonomy/criticality | PASS |
| G6 lifecycle | PASS |

## Next evidence

1. Freeze bounded Berlin/Brandenburg semantic derivatives and prove complete context coverage.
2. Generate and compare the aperture reinforcement candidates, then emit the bridge manifest.
3. Build and validate new CAD/mesh/3MF artifacts and exact Anycubic slices.
4. Continue the physical connector, opacity/light, handling/proof-load, 2 m logo, wall, watermark and release gates.

Canonical machine-readable result: `preflight/preflight-result.json` (`PREFLIGHT-MM-ART-010-016`).
