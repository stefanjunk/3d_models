# Decomposition review 0.3.0 — MM-ART-011 Harz and Rheinisches Revier

Status: **human decomposition approval requested; terrain acquisition, CAD and coupon geometry remain blocked**.

Machine-readable authority: `plan/hybrid-design-plan-v0.3.0.json`

Planner evidence: `reports/architecture-v0.3.0.json` and `reports/architecture-v0.3.0.md` — **PASS, 0 errors, 0 warnings**. A planner pass proves internal plan integrity, not physical fit, wall safety, data fidelity or release readiness.

## Proposed printed architecture per pilot

| Printed body | Quantity | Responsibility |
|---|---:|---|
| Main relief half | 2 | 300 × 400 mm substrate, continuous terrain, rear datum, center locating lands, connector pockets, local standoff sockets, light apertures and rear lands |
| One-way seam connector | 3 | Concealed permanent retention; owns its derived pocket-clearance body |
| Upper hanger | 2 | Local installed self-weight path to customer-selected wall hardware |
| Lower standoff | 2 | Sets the common 18 mm wall plane without a frame |

Across Harz and Rheinisches Revier this yields four main halves, six connectors and eight hanger/standoff parts. There is no rear grid, rear frame, adhesive, magnet, screw connection between print sections or replaceable artwork section.

## Controlled hybrid authorities

- `MAIN_HALF_SET` owns the shared exact outer boundary, 3 mm substrate, X = 300 mm split, locating lands, pockets, snap sockets and all functional keep-outs.
- `HARZ_HEIGHTFIELD` owns one immutable 16-bit Copernicus GLO-30-derived master, one physical aspect and one elevation-to-model-Z transform.
- `RHENISH_HEIGHTFIELD` owns one immutable current GeoBasis NRW DGM1-derived 16-bit master, acquisition state, physical aspect and elevation-to-model-Z transform.
- Each heightfield remains continuous-tone geometry. Three global model-Z changes create four abstract colors; color never posterizes or replaces the 16-bit master.
- Pilot-specific negative light cutters may create a few true front-through valley, contour, mine-bench or infrastructure paths only outside functional/data/watermark keep-outs.
- Optional customer lighting remains an excluded 12 × 4 mm strip and at least 6 × 4 mm cable envelope within an 18 mm open cavity.

## Shared coupon before full-size CAD

One off-product coupon may qualify both pilots only when connector/standoff material, nozzle, orientation and process profile are identical. It combines:

1. four pocket/locating candidates at 0.15, 0.25, 0.35 and 0.45 mm per side;
2. the calculated one-way connector flexure and a representative two-strip center seam;
3. one representative upper-hanger snap/socket in the production layer direction;
4. labeled surfaces for insertion, whitening/crack, flushness and measured-result records.

Any material or profile change forces a fresh coupon. Spring length, thickness, root radius, lead-in, allowable strain and structural ligament are not guessed in this phase. Schema-required numeric zeros carrying `dimensions_status` mean **UNSELECTED**, never zero-thickness production geometry.

## Approval effect

Approval authorizes the shared interface skeleton, flexure calculation, shared coupon source/export, frozen terrain acquisition, 16-bit processing, proxy assemblies and both production-model pipelines for revision 0.3.0. It does not approve printing, physical fit, wall anchors, lighting electronics, terrain appearance, safety, watermark, data rights or commercial release.

Please approve this decomposition explicitly or request corrections.
