# Dimensioned COTS selection — MM-TOY-003 / 0.1.0-bom.2

Checked 2026-08-31. Availability is a volatile snapshot, not a procurement guarantee. Manufacturer pages and manufacturer drawings/CAD are preferred over marketplace listings; delivered samples remain the physical interface authority.

## Selected drive stack

- **Motor:** Pololu 4755, 37D encoder gearmotor, 6 mm D-shaft, official dimension drawing.
- **Bracket:** Pololu 1995 machined 37D bracket, official dimension drawing.
- **Hub:** BaneBots T81H-RM61, 6 mm shaft, two set screws at 90°, 3/4-inch snap-ring retention, linked STEP/3D model.
- **Wheel:** BaneBots T81P-496BB, 4-7/8 inch (123.825 mm) OD, 0.8 inch (20.32 mm) width, 60A, T81 hub mount.

This replaces the `bom.1` INJORA beadlock/hex stack for the next CAD revision. The new family has a direct, coherent wheel-to-hub contract and better dimensional provenance. It also reduces nominal installed wheel/hub mass by about 40.49 g total and nominal overall width at 216 mm wheel-center track from 258 mm to **236.32 mm**. These are arithmetic estimates only.

## Evidence quality

- E3 means official nominal geometry is sufficient to create a controlled CAD candidate.
- `variant_confirmed=false` means no delivered sample, revision or tolerance has been measured.
- The BaneBots hub viewer exposes a source named `T81H-RM61.stp`; the derived maximum envelope is 20.32 mm. Supplier CAD is referenced, not vendored, and does not override sample measurements.
- The Gens ace page lists the dimensional candidate but shows conflicting availability language; verify before ordering or nominate a dimensionally equivalent pack only through a new change review.
- The Adafruit 4502 official EagleCAD/Fab Print gives a 25.4 x 17.78 mm outline with two 2.5 mm holes at 20.32 mm centers. The delivered PCB revision, axis registration and installed connector height still require intake measurement.

## Rejected/alternate wheel candidates

| Candidate | Positive | Reason not selected |
|---|---|---|
| goBILDA Rhino 120 mm | Official STEP and dimensions | Current manufacturer page indicates replacement/roll-away status, weakening repeat procurement. |
| Studica 76250 110 mm all-terrain | Current dimensioned product, direct 6 mm adapter | No equivalent registered STEP/tolerance contract in the captured evidence; retain as alternate. |
| Existing INJORA CRAW18003 + CRAW20161023 | Matches current 120 × 42 CAD envelope | Selected rim variant was out of stock and the cross-brand Pololu hex stack has weaker dimensional authority. |

## Mandatory intake fields

Photograph label/package; record source/date/revision; weigh each item; measure all fit-critical geometry with the instrument and uncertainty noted; retain manufacturer files by URL/hash where licensing permits; then update the graph edge evidence. Do not copy marketplace CAD into the release package without provenance and license review.
