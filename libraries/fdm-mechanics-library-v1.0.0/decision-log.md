# Decision log — 1.1.0-draft.1 extension

## 2026-08-21 — Continue the approved production correction

- Gate evidence: `design-spec.yaml` records both requirements and concept approval for exact revision `1.1.0-draft.1`. The approved concept asset is `concept/families-31-39-r1.1.0-draft.1.png`.
- Scope: continue families 31–39 and samples 121–156 only. Keep the library `experimental-draft`; do not request or claim final release.
- Finding: the semantic source in `tools/library_spec.py` and `library/fdm_mechanisms.scad` had advanced beyond the generated catalog, sample wrappers, metadata, documentation, and packaged meshes. Existing build evidence reused all 36 extension meshes and therefore did not prove a fresh source build.
- API decision: use the approved public parameter `rocker_r` for family 34. `output_r` was a stale internal/public name and is removed from generated extension artifacts.
- Rebuild decision: preserve a prebuild regression report, regenerate derived source/catalog documentation, force-render all 36 extension plates, and independently render them again for exact packaged-mesh equivalence.
- Environment limitation: OpenSCAD PNG output cannot run headlessly because `xvfb-run`/`Xvfb` is unavailable and no usable display is configured. OpenSCAD instead exports the current assembly view to a temporary STL, which is rendered deterministically with the Matplotlib `Agg` fallback and recorded as such.
- Release boundary: digital geometry evidence does not qualify sealing, friction, retention, torque, electrical behavior, temperature, wear, or cycle life. Physical qualification remains open.

## Library, hardware, and provenance review

- Geometry authority: project-local parametric OpenSCAD source, rendered with OpenSCAD 2021.01. Current-STL previews use Matplotlib `Agg`; no external STL, STEP, scan, or supplier geometry is incorporated in families 31–39.
- Internal library: `library/fdm_mechanisms.scad`, source code under MIT; generated geometry under CC0-1.0 as recorded by the package licenses and catalog metadata.
- External library decision: BOSL2, NopSCADlib, `cq_warehouse`, `bd_warehouse`, `cq_gears`, and step.parts were reviewed as applicable categories but are not required by the current CSG implementation. Adding one would introduce dependency/version/license burden without resolving an approved geometry gap.
- Print-vs-buy: sample bodies and low-load gauges remain printed. O-rings, precision shafts, M2 fasteners, cables/elastomer inserts, cells/contacts, magnets, sensors, and compatible grease remain purchased and supplier-defined.
- Supplier evidence: part numbers, drawings, material compatibility, and measured dimensions are unresolved. Nominal placeholder geometry is reference-only and not manufacturing-authoritative for a product integration.
- Local qualification: no printer/material/nozzle/profile-specific test record exists for the extension. Samples remain `experimental`; no promotion to `qualified-local` is permitted.

## Next gate

After deterministic digital validation, print the family-specific coupons and record supplier/process identities plus leakage, force, torque, runout, retention, thermal, wear, and cycle results. Watermark and final release approval remain blocked until the production candidate and physical evidence are ready for the intended release scope.

## 2026-08-21 — Digital DRAFT checkpoint result

- Fresh extension build: 36/36 passed with no warnings or failures; all STL and assembly-preview artifacts were regenerated from the current semantic source.
- Geometry regression: 36/36 second renders matched the packaged DRAFT plates by canonical sorted-triangle SHA-256. Raw STL file hashes remain informational because triangle order can differ without changing geometry.
- Parameter contract: nine approved family APIs passed; 27/27 valid/invalid boundary renders behaved as expected.
- Family 32 correction: terminal hard-stop solids were moved into robust wall/channel overlap. Samples 125–128 now contain the documented two watertight positive-volume components with no degenerate triangles.
- Whole library: 156/156 structural/mesh checks passed, with 384 separated components.
- Mesh simplification gate: `pending` because its mandatory exact-slicer comparison cannot run without a named printer/profile/slicer. Interim DRAFT disposition is to retain the deterministic, low-complexity source STLs without attempting or planning a lossy step; fits, seals, threads, and contact geometry remain protected and resource budgets stay unmeasured/null.
- Preserved gate asset: `concept/families-31-39-r1.1.0-draft.1.png` remains byte-identical at SHA-256 `4827bae0290786e22d9dec3902d1fc50cda7a16aa1a557520d2e96631af3c6bc`.
- Disposition: remain `experimental-draft`. Exact slicer/profile evidence, physical tests, watermark integration, and final release approval are still open.

## 2026-08-21 — Claims-bounded and provenance correction

- Scope: documentation, catalog records, validation, and package provenance only under the already approved `1.1.0-draft.1` requirements and concept. Public mechanism names, parameter APIs, OpenSCAD geometry, packaged STLs, and the approved concept asset were not changed.
- Generator authority: `tools/library_spec.py` now owns local sealing disclaimers and `tools/generate_sources.py` emits `artifact_status`, `qualification_status`, `status_de`, and `claims_de` into generated records, metadata, CSV/JSON catalogs, all extension READMEs, and visible HTML catalog cards.
- Claims decision: samples 121–156 are explicitly `experimental-draft` and `unqualified`. “Abgedichtet”/“dicht” in family 39 denotes only the intended unpenetrated wall barrier; it does not claim a measured leak rate, IP/water seal, pressure release, or service life. Equivalent local boundaries apply to sealing families 31, 32, 35, and 37.
- Validation decision: `tools/validate_extension.py` deterministically checks all 36 extension records across JSON/CSV, metadata, READMEs, HTML cards, and Markdown rows, including 20 sealing records and four family-39 records. This documentation-only pass is stored separately from the preserved 36/36 geometry and 27/27 boundary evidence so no unnecessary geometry rerender is implied.
- Provenance decision: the actual 1.0.0 release remains dated `2026-08-20`; `2026-08-21` is recorded separately as the artifact date of the non-final `1.1.0-draft.1` checkpoint. The manifest no longer exposes an ambiguous top-level release date for the DRAFT package.
- Invariance evidence: the shared SCAD SHA-256 remained `3e700ed8c0c544d9be352ff8f6329e7691c06cd5d2c8b542853ec79b763b5360`, the ordered aggregate of extension print-plate SHA-256 lines remained `66b73b12f66245863120dfda197cb6e543fc68d6df5bb6de76373927780b716b`, and the concept asset remained `4827bae0290786e22d9dec3902d1fc50cda7a16aa1a557520d2e96631af3c6bc`.
- Durability follow-up: `tools/validate_library.py` now invokes the current-input extension contract/claims validator during every full-library validation instead of relying only on stored JSON status. It requires 36 current extension records, 20 sealing records, four family-39 records, no stale generated artifacts, no claim-record errors, and current JSON/CSV/metadata/README/HTML/Markdown agreement; the stored geometry and claims reports remain additional evidence.

## 2026-08-21 — Requirements change requested for 1.1.0-draft.2

- User direction: the mechanisms are samples, so physical qualification is not a prerequisite for internal integration or reuse by other designs. The target is a reusable `experimental-draft` / `unqualified` sample library.
- Gate effect: current requirements are `changes-requested`; concept approval is `blocked` with no current asset, and watermark approval remains blocked. The prior `1.1.0-draft.1` requirements approval, concept asset, approval metadata, and concept SHA-256 are preserved in `workflow.approval_history`.
- Qualification boundary: physical testing becomes optional future evidence for internal sample reuse, but remains mandatory before `qualified-local` promotion or any product-specific sealing, IP, load, electrical-safety, service-life, or suitability claim.
- Integration recommendation: expose the existing package in place through the local skill and shared library root; do not rename or move the large package directory unless a later verified integration constraint requires it. All 156 samples must remain discoverable/queryable, provenance and licenses must remain intact, package version/status must be explicit, dependencies must be declared, and digital validators must pass after integration.
- Stop condition: no concept, integration, geometry, generator, catalog, manufacturing-export, version, package-manifest, checksum, or release work is authorized until the two current-revision gates are approved.
