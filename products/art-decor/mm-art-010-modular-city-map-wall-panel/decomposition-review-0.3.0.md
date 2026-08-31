# Decomposition review 0.3.0 — MM-ART-010 Berlin

Status: **human decomposition approval requested; CAD and coupon geometry remain blocked**.

Machine-readable authority: `plan/hybrid-design-plan-v0.3.0.json`

Planner evidence: `reports/architecture-v0.3.0.json` and `reports/architecture-v0.3.0.md` — **PASS, 0 errors, 0 warnings**. A planner pass proves internal plan integrity, not physical fit, wall safety or release readiness.

## Proposed printed architecture

| Printed body | Quantity | Responsibility |
|---|---:|---|
| Main half | 2 | 300 × 400 mm substrate, Berlin field, rear datum, center locating lands, connector pockets, local standoff sockets, light apertures and rear lands |
| One-way seam connector | 3 | Concealed permanent retention; owns its derived pocket-clearance body |
| Upper hanger | 2 | Local installed self-weight path to customer-selected wall hardware |
| Lower standoff | 2 | Sets the common 18 mm wall plane without a frame |

There is no rear grid, rear frame, adhesive, magnet, screw connection between print sections or replaceable artwork section. Destructive separation is acceptable and no service cycle is claimed.

## Controlled hybrid authorities

- `MAIN_HALF_SET` owns the exact outer boundary, 3 mm substrate, one X = 300 mm split, locating lands, pockets, snap sockets and functional keep-outs.
- `BERLIN_VECTOR_FIELD` owns one immutable global OpenStreetMap-derived artwork frame and the aligned four-color map relief. It is clipped into halves only after global processing.
- `LIGHT_CUTTER_SET` owns negative geometry for a few true front-through paths but may operate only outside seam, connector, hanger, attribution and future watermark keep-outs.
- `LIGHTING_ENVELOPES` models the optional 12 × 4 mm strip space, at least 6 × 4 mm cable route, diffuser lands and three cable exits. Electrical hardware remains excluded.
- `WALL_HARDWARE_REFERENCE` is an excluded planning envelope. It cannot authorize a fastener size or wall load until the actual substrate is known.

## Coupon before full-size CAD

One off-product support-free coupon will combine:

1. four pocket/locating candidates at 0.15, 0.25, 0.35 and 0.45 mm per side;
2. the calculated one-way connector flexure and a representative two-strip center seam;
3. one representative upper-hanger snap/socket in the production layer direction;
4. labeled surfaces for insertion, whitening/crack, flushness and measured-result records.

Spring length, thickness, root radius, lead-in, allowable strain and structural ligament are deliberately not invented in this phase. They become CAD parameters only after a material-specific calculation; the coupon then selects process compensation. Schema-required numeric zeros carrying `dimensions_status` in the plan mean **UNSELECTED**, never zero-thickness production geometry.

## Approval effect

Approval authorizes the shared interface skeleton, flexure calculation, coupon source/export, Berlin source freeze, proxy assembly and production-model pipeline for revision 0.3.0. It does not approve printing, physical fit, wall anchors, lighting electronics, final appearance, safety, watermark, rights or commercial release.

Please approve this decomposition explicitly or request corrections.
