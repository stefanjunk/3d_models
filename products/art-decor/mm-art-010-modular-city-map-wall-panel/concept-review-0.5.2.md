# Concept review 0.5.2 — complete water apertures and S/U transit accent

Status: **human-approved by Stefan on 2026-09-04**

Approval asset: `concepts/berlin-water-transit-concept-v07.png`

The approval was followed by explicit continuation with the targeted structural strategy: full-thickness local topology bridges are allowed only where a water aperture would otherwise create detached printed land. No rear grid or blanket rib network is authorized. Optional local rear reinforcement remains conditional on exact span analysis and separate print-orientation, lighting and physical review.

## Requirement correspondence

| User correction | Concept v07 |
|---|---|
| Tegeler See and every other water remain cut out | Water polygons and river/canal/stream lines are shown as unfilled light-through openings; Tegeler See relation `451908` has a dedicated detail view. |
| Use blue for S-Bahn and U-Bahn instead of motorways | Sky Blue is drawn from S-/U-Bahn route relations. Motorway/trunk is no longer a separate blue layer and remains part of Midnight streets. |
| Retain the existing product | Both approved display modes, 600 × 400 mm envelope, two-part split, Oak/Mint/Midnight/Sky palette, permanent connectors, rear halo preparation and parameterized metriMade site marker remain. |
| Stay within four filaments | The positive geometry remains four semantic bodies. Water is negative geometry and consumes no filament/tool. |

## Data decision

- Water areas: OSM multipolygons with `natural=water`, reservoir/basin land use or `waterway=riverbank`.
- Water lines: `waterway=river|canal|stream`.
- S-Bahn: route relations with `route=light_rail` and `network:metro=s-bahn`.
- U-Bahn: route relations with `route=subway` and `network:metro=u-bahn`.
- Opposite route directions are visually overlaid in the concept and will be dissolved before production buffering.

The frozen local Berlin PBF yields 1,816 water areas, 1,277 water lines, 38 S-Bahn relations and 18 U-Bahn relations. Tegeler See is present as one non-empty polygon with an area of 3,819,800.57 m² in EPSG:25833.

## Manufacturing controls carried forward

- Minimum opening width: 2.0 mm.
- Minimum protected ligament: 5.0 mm.
- Maximum open fraction: 12% per half.
- Center seam and connector/hanger/attribution/site-marker keep-outs remain protected.
- A source water component may be locally bridged only when the build report identifies the component, reason and retained opening. Silent removal is a failure.
- New 3MFs and exact Anycubic slices are mandatory; the rejected 0.5.1 files do not count.

## Deliberate concept limitation

The local Berlin PBF is sufficient to prove the feature classification and the Tegeler See regression, but it does not cover the complete rectangular Umland extent. The Umland panel in v07 is therefore a semantic concept, not source-coverage or manufacturing evidence. After approval, the recorded exact context-complete source must be reacquired and frozen before production extraction.

## Approval effect

Approval authorizes the revision 0.5.3 decomposition, production-source acquisition, digital geometry generation, target-slicer packaging and validation. It does not authorize printing, printer upload, wall installation or commercial release.
