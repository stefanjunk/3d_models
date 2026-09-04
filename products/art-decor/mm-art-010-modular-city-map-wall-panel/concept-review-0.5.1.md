# Concept review 0.5.1 — enlarged metriMade site marker

Status: **pending explicit human approval**.

Review artifact: `concepts/berlin-site-marker-concept-v06.png`

Evidence report: `concepts/berlin-site-marker-concept-v06.json`

Artifact SHA-256: `10e3bb0f751572fc806a3282bf87f1a4fa5bf2989252fad3fb365e6a429d242c`

## Exact proposed change

- Replace the former compact metriCreate marker with the canonical monochrome
  stacked `metriMade` lockup `MM-BRAND-001-R1`.
- Enlarge the complete logo envelope to 54.0 × 57.18 mm while preserving its
  source aspect ratio and 0° orientation.
- Keep its center at the frozen address point for Sterkrader Straße 24,
  13507 Berlin.
- Keep the relief at 0.60 mm and in existing semantic tool 4; the selected
  Oak/Mint Green/Midnight/Sky Blue palette therefore remains four-color.

The Berlin map, both display modes, relief hierarchy, permanent two-part split,
connectors, mounting and backlight preparation are unchanged. This is an
artwork/size revision of the existing parameterized site marker, not a map
redesign.

## Digital concept checks

| Check | Boundary crop | Context outline | Result |
|---|---:|---:|---|
| Center-seam clearance | 68.94 mm | 50.37 mm | PASS against 50 mm concept target |
| Outer-perimeter clearance | 20.36 mm | 104.06 mm | PASS against 5 mm geometry target |
| Required logo clear space | 13.50 mm | 13.50 mm | fits inside the tighter perimeter clearance |
| Logo envelope | 54.0 × 57.18 mm | 54.0 × 57.18 mm | aspect ratio preserved |
| Smallest source-component bbox dimension | 1.20 mm | 1.20 mm | above 0.90 mm source target |

The render and measurements support the proposed size but cannot prove visual
recognition at a real viewing distance. A process-matched Oak/Sky Blue raised
logo coupon must be viewed on a wall at 2.0 m under ordinary indoor lighting.

## Approval boundary

Approval of concept v06 authorizes generation of a new immutable revision
0.5.1 CAD/mesh/3MF candidate and the physical logo coupon. It does not approve
commercial release, brand clearance, the recessed rear product watermark,
physical visibility, connector fit, purge behavior, lighting or wall mounting.

Requested decision: explicitly approve or reject
`concepts/berlin-site-marker-concept-v06.png`.
