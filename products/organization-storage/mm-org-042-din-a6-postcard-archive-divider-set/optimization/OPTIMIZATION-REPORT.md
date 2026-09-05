# MM-ORG-042 — FDM optimization report

Scope: reduce print time and deposited material on the lane block while every protected
interface dimension stays unchanged. Baseline and all candidates were sliced locally with
the exact pinned machine and filament profiles; nothing was uploaded and no print started.

## 1. Baseline identity

| item | value |
|---|---|
| model | `source/generated/divider-block.stl`, sha256 `e0d437c3…f2e23928`, 7124 triangles |
| source | `source/divider.py` (unchanged master) |
| printer | Anycubic Kobra 3 Max, 0.4 mm hardened steel nozzle |
| process | `0.20mm PETG Tool @AC K3 Max`, sha256 `fbe19c51…423a75e1` |
| filament | SUNLU PETG Black, `filament_max_volumetric_speed` 10 mm³/s |
| slicer | Anycubic Slicer Next 1.3.9.4 |
| orientation | flat underside down, no supports |
| time / material | 22 857 s (6 h 21 min) / 93 284 mm³ ≈ 118.5 g |
| layers / peak flow | 295 / 9.61 mm³/s |
| warnings | none |

## 2. Why the usual first lever does not apply

`sparse_infill_density` is already 5 %, and it moves nothing on this part.
`plan_shell_ribs.py` returns `NO_INFILL_CORE` for the 1.6 mm divider plate — four wall
loops from each side need 3.10 mm of the available 1.6 mm — and the 2.0 mm floor is
thinner than `bottom_shell_thickness` + `top_shell_thickness` (2.4 mm). The G-code
confirms it: extruded volume is 99.3 % of the CAD solid volume. Material can only leave
through geometry or through layer count. Details and the region-by-region volume split
are in `protected-geometry.md`.

## 3. Candidates — one isolated lever family each

| id | lever family | change |
|---|---|---|
| A | process only | 0.20 → 0.28 mm layer, outer wall 50 → 40 mm/s, inner wall 80 → 60, solid infill 65 → 50; CAD unchanged |
| B1 | geometry only | floor 2.0 → 1.4 mm; silhouette unchanged |
| B2 | geometry only | B1 + internal dividers 1.6 → 1.35 mm + scooped divider tops (45 mm at the rear ramping to 22 mm at the open side over 75 mm) |
| C | combined | B2 geometry on the A process |

## 4. Measured results

| candidate | time | Δ time | material | Δ material | layers | peak flow | warnings | supports |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 6 h 21 | — | 118.5 g | — | 295 | 9.61 | 0 | none |
| A process 0.28 | 5 h 25 | −14.6 % | 113.9 g | −3.9 % | 211 | 8.16 | 0 | none |
| B1 floor | 5 h 50 | −8.0 % | 107.9 g | −8.9 % | 292 | 9.61 | 0 | none |
| B2 floor+thin+scoop | 4 h 56 | −22.2 % | 93.9 g | −20.8 % | 292 | 9.32 | 0 | none |
| C combined | 4 h 12 | −33.6 % | 89.5 g | −24.4 % | 209 | 9.62 | 0 | none |

Toolpath inspection, not only the summary: no `Bridge`, `Overhang` or `Support` feature
appears in any candidate — the scoop is a shallow sloped *top* surface (17.5° from
horizontal), never an overhang. Gap-infill occurrences rise from 1 (baseline) to 7 (B1,
B2) and 11 (C) as the 1.35 mm wall and the thinner floor enter arachne's variable-width
range; the effect is already contained in the measured totals. Peak flow stays at or
below the baseline in every candidate and never exceeds the filament's declared
10 mm³/s — the slicer clamps to that limit, so C is flow-equivalent to the already
accepted baseline rather than pushing the material harder.

## 5. Protected geometry — verified, not assumed

Measured by ray probing the meshes at z = 12 mm, independent of the generator:

| property | baseline | B1 | B2 | required |
|---|---|---|---|---|
| lane count | 6 | 6 | 6 | 6 |
| lane clear width | 20.40 mm | 20.40 mm | 20.60–20.65 mm | ≥ 20.40 mm |
| lane clear length | 107.15 mm | 107.15 mm | 107.15 mm | unchanged |
| flat bed face `z_min` | 0.000 | 0.000 | 0.000 | 0.000 |
| XY envelope | 133.6 × 108.8 | identical | identical | ≤ 220 × 180 |
| minimum wall | 1.6 mm | 1.6 mm | 1.35 mm | ≥ 1.35 mm |

`fdm_ci.py audit-mesh --profile release` returns PASS for both variant meshes.
`compare-meshes` against the baseline shows XY extents identical, Z lower by exactly
0.600 mm, candidate→reference maximum 0.80 mm and reference→candidate maximum 21.76 mm —
the scooped material and nothing else.

The lane clearance stays `0.60 mm UNQUALIFIED_PROVISIONAL` in every candidate. No
variant makes or weakens a fit claim, and `fit-coupon-xy-series` is unchanged.

## 6. Selection

Two frontiers, because one candidate depends on an unqualified process:

- **On the qualified 0.20 mm process the Pareto set is `B2` alone** — 4 h 56 and 93.9 g,
  −22.2 % time and −20.8 % material, with no new process risk.
- **Unrestricted, `C` dominates on both objectives** — 4 h 12 and 89.5 g, −33.6 % and
  −24.4 %. It needs `process-0p28-petg-tool-k3max-CANDIDATE.json`, which is **not**
  covered by the calibration baseline `MM-R3-K3MAX-PETG-0P4-0P20-2026-08-31`.

**Recommended: B2 now, C after the human slicer-preflight gate accepts the 0.28 mm
process.** B2 captures two thirds of the available saving without touching the qualified
process; C's extra 44 minutes and 4.4 g are real but rest on a layer height nobody has
printed on this machine yet.

## 7. Open items and residual uncertainty

- The 0.28 mm process is **UNQUALIFIED**. Layer adhesion, top-surface finish and the
  0.5 mm vertical fillet at 0.28 mm are unverified. `slicer-preflight` and every stage
  after it are human gates under `autonomy-policy.json`.
- The scoop is a **visible silhouette change** and needs the concept revision recorded in
  `design-spec.yaml` to stand.
- Card retention at the open side drops from 45 mm to 22 mm. It is the standard
  index-card-file scoop and it serves the allowed "browsing by tilting cards forward"
  degree of freedom, but stack stability with real cards is a physical test
  (`AC-INSERT-001`, `AC-CYCLE-001`), not a slicer result.
- The 17.5° sloped divider tops will show stair-stepping — about 0.63 mm step width at
  0.20 mm layers and 0.89 mm at 0.28 mm. This is an appearance-gate item.
- No strength calculation was needed: nothing here is a load path. The block carries
  paper.

## 8. Artifact hashes

| artifact | sha256 |
|---|---|
| `source/divider_variants.py` | `758a27e45b04d00cbe3b5c9e5feb89e38d1fc7231db479c06c45b20af5e390e1` |
| `source/generated/variants/divider-block-b1-floor.stl` | `e8b02d4d8cea7afa0c636a32ba9321f4f07776bf8d2ff5a22d1202d6fe2586db` |
| `source/generated/variants/divider-block-b2-floor-thin-scoop.stl` | `a20c3e1a1410350103c9a9bb3c2698f67b90e5510fc2a364ae069aec2c46285a` |
| `profiles/anycubic-slicer-next/process-0p28-petg-tool-k3max-CANDIDATE.json` | `3e7cd68375d3f3134f88bd1472dd729b37bb6e7354e1b1fef078b8d2d2022931` |
| `exports/v0.1.0/opt-a-process-0p28/plate_1.gcode` | `f2d84fc4ccf8778ed92825125a017a3a1820388d7306b1643513e0d77442e209` |
| `exports/v0.1.0/opt-b1-floor/plate_1.gcode` | `5d16483b54ee6adec40506d4bbe3aa1dadf7eab7696e162421eb33f4ca1f30f5` |
| `exports/v0.1.0/opt-b2-scoop/plate_1.gcode` | `7b2bb4352fbf49fad1ce1fb0c9a11a721fd89061aa3b2aee19ef7acb496f001e` |
| `exports/v0.1.0/opt-c-combined/plate_1.gcode` | `e068e5e3612da513b04f95cd25db551a370e3385f3ce6893b0d5edfdfac3a622` |

Machine-readable: `variant-geometry.json`, `variant-comparison-input.json`,
`variant-comparison-input-qualified-process.json`, `../reports/optimization/*.json`.
