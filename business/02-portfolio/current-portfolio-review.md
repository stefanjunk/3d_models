# Current model and portfolio review

Review date: 2026-08-31. The detailed row-level inventory is in `product-portfolio.xlsx` and its version-control sources; deterministic artifact evidence is in `model-artifact-audit.csv` and `model-artifact-audit.md`.

## 3D-preflight portfolio overlay — 2026-08-31

The generated workbook now presents one filterable `Portfolio` list with all 422 records: 108 current product directories and 314 planned products/research ideas. Every row has one populated, unique `Working_SKU`; the redundant `Record_ID`, `Mapped_Working_SKU`, and duplicate `Product Register` worksheet are omitted. Its leading canonical columns expose status, commercial data, C/R/K, current and target lanes, dimensions, materials, manufacturing estimates, scores and next gates side by side; source-prefixed columns preserve the remaining joined evidence fields for audit. The prior 99-row curated product source remains version-controlled in `product-portfolio.csv`, and all 108 exact path-based product preflights remain in their JSON/PURPOSE sources and joined Portfolio fields. The compact format is `C# · R# · K# · Lane X · CONFIDENCE`; `Target_Lane_After_Evidence` remains a separate planning field and never overrides the current lane or release decision.

The workbook now covers 314 research ideas. The 37 ideas already mapped to a product use its current scorecard; 163 legacy ideas use clearly labeled preliminary bands with `R0–R1` and current `Lane E`. SKU-201–300 add 100 explicit-purpose ideas with directional trend scores of 87–94 and structured `K1 · C1–C2 · R2` concept preflights. They remain `Lane E`, `LOW_UNKNOWN`, and `CONCEPT_ONLY` until exact process and variant evidence close.

SKU-301–314 are separate, named-interface children of retained generic ideas. All 14 have explicit purpose, primary-source nominal interface evidence, a hashed research-only Kobra 3 Max/PETG process baseline, measurable acceptance criteria, and compact `C1–C3 · R3 · K1 · Lane B/C · CONDITIONAL` preflights. Eight are C1, four C2, and two C3. Their generic parents do not inherit R3. R3 here means nominal design inputs are complete enough to start controlled CAD; it does not mean a real device/host has fitted, a coupon has passed, demand is proven, or commercial release is approved.

`readiness-advancement-register.csv` and the workbook tab `R Advancement` assess every one of the 314 ideas and 108 product directories. Each row records purpose, current compact preflight, priority wave, advancement potential, evidence boundary, bottleneck, and exact next evidence. This makes the requested high-trend/low-complexity-first sequence explicit without averaging market potential into C/R/K.

The current product estate still has only one R3 product preflight (`MM-PER-001` NameForm); all other product R increases remain evidence-gated. In particular, the Anycubic Kobra 3 Max purge catcher remains R2: own machine photos and the independently measured 17 mm screw pitch improve the interface evidence, but a complete variant-confirmed clean-room envelope, screw hardware/tolerances, full motion keep-outs, storage-architecture decision, independent coupon, and low/mid/high-Z purge tests remain open. The existing ALEX tray remains R1 until the exact furniture article/revision, real drawer measurements, exact process, and physical 209.3/210.0/210.7 mm gauge result exist.

These assessments support side-by-side market-potential/implementation-complexity analysis only and are not safety qualifications, demand proof, or release approvals. The method and regeneration commands are documented in `implementation-priority-scoring.md`.

## metriMade strategy check

The evidence-backed variant approach fits metriMade when it is used as a tightly curated consumer layer: a benefit-first, named, guided `as-is` product can remove measurement ambiguity and create a premium exact-fit proposition. The best candidates are dry, stationary, low-consequence organization/display products such as named notebook and photo formats, a no-case iPhone stand, an open AirTag tile, or a standardized coin/envelope tray.

It does not justify publishing all 314 ideas or all 14 variants as storefront products. Variant R3 and trend score remain separate from demand, rights, physical qualification, fulfillment, content quality, and release status. Active development must retain the 70% initial low-risk release allocation, and compatibility/trademark wording must name the exact tested revision. The shared product/revision system should model a generic family and its named children without duplicating divergent catalog records; only physically qualified, premium consumer-suitable revisions become metriMade-eligible.

Public staging check on 2026-08-31: `https://metrimade.com` correctly states that product data, prices and legal texts are not released, blocks live orders, and does not expose unfinished products as available. Before public launch, normalize the page/OG title from `MetriMade` to the binding `metriMade` spelling. The current `Studio`, `Download & Print`, dimensions and material journey also blurs the approved brand split: metriMade should lead with curated printed `as-is` products, while advanced configuration and digital model packages hand off to the exact shared SKU/revision in metriCreate. Keep the staging/no-index state until brand clearance and the applicable technical, commercial and fulfillment gates pass.

## Headline

- Commercially existing (`P5+`): **0**.
- Staged (`P6`): **0**.
- Live (`P7`): **0**.
- Local neutral/manufacturing 3D-artifact coverage: **96/98 records**; detected parametric source: **82/98**; at least one 3MF: **64/98**; missing: **2**; portfolio/evidence contradictions: **0**.
- Initial launch set: **3/3 at `P2 Digital candidate`**, with exact slicer and physical qualification still open.
- Best on-strategy existing digital candidate: DrawerFit drawer inlay (`P2`).
- Closest technical pipeline pilot: CyberVault nozzle case (`P2`; inherited physical evidence is not a complete R4 release).
- Model-coverage gaps: `MM-TOY-002` TrailCam CF10 is report-only and its claimed generator/ten STLs are absent; `MM-DRN-001` OpenQuad has controlled OpenSCAD source but no exported neutral/manufacturing mesh. `MM-ROV-001` Tethys supplies 13 reference STLs, although ten require winding/positive-volume review. Other remaining launch gaps are slicer, physical, rights, safety, packaging, economics and signed release evidence.

## Core and adjacent models

| Local family | Finding | Portfolio decision |
|---|---|---|
| Drawer inlay R1.3–R1.6 | segmented system; R1.6 is the source/form reference; its inherited real connector non-fit is not treated as resolved evidence | `MM-ORG-001`, initial portfolio; approved revision 0.1.0/concept v1 now has `0.1.0-draft.1`: nine common-220 modules, comb, 18 bins, twelve regenerated seam-relative connector locations, three clearance coupons and valid ten-object 3MF; 37 digital checks pass while exact slicer and physical gates remain open |
| NameForm Bookends | true left/right parametric pair with automatic/explicit name splitting, text sweep and marked exports | `MM-PER-001`, initial portfolio; `P2` digital candidate with valid DRAFT 3MF and digital checks PASS; exact slicing, watermark coupon, load/slide/cycle and appearance tests remain open |
| ShelfFit Mini Bins | new one-body parametric bin printed twice for a provisional 420 × 210 × 150 mm reference shelf | `MM-ORG-002`, initial portfolio; `P2` digital candidate with marked STEP/STL, valid 3MF, layout/optimization/watermark/interface PASS; exact shelf measurement, slicing and TP-01 through TP-07 remain open |
| Modern Carbon Desk Organizer Compact 2.0.0-draft.1 | new 210 × 190 × 173 mm common-220 derivative; parametric housing, drawer printed twice, removable six-bin sorter, coupons, STEP/STL and valid four-item DRAFT 3MF; mesh/envelope/interface evidence passes | `MM-ORG-003`, `P2` digital candidate; exact slicing, coupon/full print, drawer cycles, loaded anti-tip and appearance evidence remain open |
| Over-toilet shelf | complex 680 × 300 × 1650 mm assembly; digital integration evidence but fastener, site, load/creep, anti-tip, slicer, and physical proof open | hold; structural/physical-fulfillment category |
| Toilet-paper FIFO system | production-design work exists; wall-mount and cycle/fit evidence open | later/hold |
| CyberVault nozzle case | strong digital R4 package and earlier user-reported basic mechanism fit; R4 relief/inversion/cycles and commercial evidence open | release-process pilot; not launch hero |
| System-furniture top 20 | 20 watertight STL/STEP concepts remain provisional/unverified; ALEX and BROR now also have standalone 0.2.0-draft.1 CadQuery/JSON packages, three full-width gauges each and valid four-object 3MF files | both top-ranked entries remain `P2` measurement pilots until exact furniture/tool revisions are measured and gauges/full trays are printed; the remaining concepts stay in the research backlog |
| Honeycomb wall shelf | digital assets and test concepts, but fastener/load/creep evidence absent | hold |
| Parametric labyrinth gift box | 53 automated tests and valid exports; slicer and physical maze fit open | later personalized-gift category |
| Dice tower 0.1.2-g1 | digitally final; actual slicer and dice fall tests open | later hobby category |
| Mystery Puzzle Box | requirements-only folder previously contradicted its `P1 Model present` row; revision 1.2.0 now supplies body, lid, slider and return-leaf CAD, eight-object 3MF, 56 procedural motifs and three-latch interface evidence | `MM-PUZ-002`, later adjacent product; corrected to `P2 Digital candidate`; exact slicing and physical TP-01 through TP-08 remain open |

## Higher-risk and off-strategy work

| Family | Main reason not to launch now |
|---|---|
| Hair clip | body/hair contact, hinge/latch cycles, wear and comfort tests open |
| Barefoot shoe variants | fit, skin contact, abrasion, wet grip, fatigue, and production process unqualified |
| Rubber-ball toy popper | projectile toy; explicitly not certified; commercial toy and misuse burden |
| TrailCam CF10 FPV camera rover | report-only concept; claimed CAD/STLs absent; shared analog-FPV/ELRS requirements are documented but chassis, payload, LiPo, radio/failsafe, VTX thermal and supervised driving evidence remain open |
| OpenQuad CF5 FPV quadcopter | source-only and explicitly not flight-proven; no exported mesh, exact slice, coupon, proof-load, propulsion, radio/video or qualified flight evidence |
| Tethys Mini ROV | 13 watertight single-component reference STLs exist, but ten need winding/positive-volume correction; WTE/penetrator measurement, vacuum/leak, propulsion, tether, failsafe, trim and staged-depth evidence remain open |
| Flapping submarine and other boats | water ingress, batteries/motor, buoyancy, endurance, child/toy context |
| Rainwater filter well | ~10 kg PETG system; leak, flow, overflow, tip and environmental tests open |
| Cup and measuring spoon | food-contact/material/process and measurement-accuracy issues |
| Camera arm from original model | source/provenance block plus printer/camera fit and load/vibration testing |
| Kobra 3 Max enclosure | heat, ventilation, fire/electrical adjacency, large purchased BOM, physical build open |
| Vehicle/figure/animal/raw art meshes | sparse product documentation and uncertain source/reference rights; no product-level evidence |
| Marble tile, pillar, bowl | decorative candidates only; no commercial package or physical evidence |

## Internal assets not products

The JuSt watermark package and the local FDM mechanics library are tools/components, not saleable products. They may support a product only after their own provenance and use scope are recorded in that product's manifest.

## Website demo mismatch

The shop demo names and pictures are not evidence of products. `GridFit`, `Arc Cable Dock`, `Planter`, `Laptop Stand`, `Wall Station`, `Orbit Tray`, `Label Rail`, and `Bench Tray` must remain demo/placeholder data unless an approved local release manifest maps the exact catalog entry to an exact model revision. Claims of 3MF, STL, PDF, price, compatibility, or delivery cannot be copied from demo data into production.

## Review limitation

The 96/98 result is a deterministic path and artifact-existence audit, not proof that every historical triangle is printable, rights-cleared or commercially releasable. TrailCam and OpenQuad are deliberately recorded as missing manufacturing/neutral artifacts. Tethys received independent audit of every imported STL: all 13 are watertight and single-component, while ten still require winding/positive-volume review. ShelfFit, Mystery Puzzle Box and the Modern Carbon Compact derivative retain their prior fail-closed digital project validation; other records retain their recorded evidence level. Unknown provenance still blocks release. External folders remain excluded as model evidence.
