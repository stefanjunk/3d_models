# Anycubic Kobra 3 Max Filament Settings

**Printer:** Stock Anycubic Kobra 3 Max  
**Nozzles:** 0.4 mm brass and optional 0.8 mm brass replacement  
**Build plate:** Stock textured PEI  
**Slicer:** Anycubic Slicer Next, Advanced mode; field names checked against v2.3.0 commit `70931e5`  
**Profile goal:** Fast, reliable printing without sacrificing visible-wall and top-surface quality  
**Research date:** 1 August 2026

All profile tables below are **derived starting recommendations**, not manufacturer presets. Dry the filament and run the calibration sequence before treating any pressure-advance, flow, or maximum-volumetric-speed value as final. The 0.4 mm Kobra 3 Max values were checked against [Anycubic's pinned Max profile commit](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/commit/987a3c2bf9ed13934137326bfd522896c70e5101). The 0.8 mm geometry and fallback deltas were checked against the exact Max machine and process profiles in pinned [OrcaSlicer commit `972dae2`](https://github.com/OrcaSlicer/OrcaSlicer/commit/972dae22afdadc3251d05e10c2d6f00c35e6b83a), because the pinned Anycubic tree contains no Max 0.8 profile. Verify the values in your installed configuration bundle because bundled and cloud profiles can differ.

## Critical Setup

| Item | Configuration |
|---|---|
| Kobra 3 Max motion | Keep the stock machine ceilings. Control real print speed with feature speeds, acceleration, and filament maximum volumetric speed. The advertised 600 mm/s is not a useful universal process speed. |
| 0.8 mm hardware | Anycubic lists the Kobra 3 Max nozzle as expandable from the stock 0.4 mm to 0.6/0.8 mm. Use a Kobra 3 Max-compatible 0.8 mm nozzle or hotend, install it according to Anycubic's service guidance, then verify Z offset and bed leveling before printing. |
| 0.8 mm printer preset | Prefer the native `Anycubic Kobra 3 Max 0.8 nozzle` preset when the installed bundle exposes it. Otherwise follow the complete [0.8 mm manual fallback](#08-mm-manual-fallback); the pinned Orca JSON is a settings reference, not a directly importable Slicer Next 2.3.0 profile. A 0.4 preset with only its nozzle diameter changed is incomplete. Do not substitute the smaller Kobra 3 profile. |
| Nozzle-change calibration | A nozzle change invalidates nozzle-sensitive tuning. For every 0.8 mm material preset, start with PA disabled and the conservative MVS listed below; then calibrate flow ratio, PA, and MVS with the installed 0.8 mm nozzle before raising flow. |
| TPU feed | Do **not** feed TPU through ACE Pro. Use the shortest low-drag external path, ideally a top-mounted spool close to the toolhead. Follow Anycubic's instruction to loosen the extruder idler screw by half a turn before loading TPU. |
| TPU preparation | Purge old PLA/PETG completely. A clean nozzle or dedicated TPU hotend is useful if flexible filament buckles before the nozzle. Print one object at a time and avoid retract-heavy geometry. |
| PETG plate | Wash with dish soap, preheat the large bed for about 10 minutes, and let it cool before removal. Use a thin glue layer as a **release barrier** if PETG bonds too strongly. |
| Pressure advance | Use one PA source only. Enabling PA in a filament preset replaces printer/auto-calibrated PA; commands are not additive and the last emitted command wins. Calibrate after flow ratio. |
| Profile inheritance | Use the exact Kobra 3 Max **printer** preset for the fitted nozzle. Unlisted filament/cooling fields inherit from the exact duplicated filament base in the preset index; unlisted process fields inherit from the exact duplicated process base. Only unchecked Setting Overrides inherit from the printer preset. Review all inherited values when the configuration bundle changes. |
| Setting Overrides | In Filament > Setting Overrides, check the override box for every listed retraction, wipe, and Z-hop value, including explicit `Off` and `0 mm`. An unchecked box inherits the printer value. |
| Configuration target | Slicer Next v2.3.0 field semantics at commit `70931e5321fa66966a5bfb251efca0e82307d427`, with 0.4 mm Kobra 3 Max profiles from Anycubic commit `987a3c2bf9ed13934137326bfd522896c70e5101` and 0.8 mm Max profiles from Orca commit `972dae22afdadc3251d05e10c2d6f00c35e6b83a`. Do not substitute a smaller Kobra 3 machine preset. |

## Where To Enter Values

| Slicer Next area | Values from this document |
|---|---|
| Filament > Filament | Nozzle and bed temperatures, flow ratio, `Enable pressure advance`, PA coefficient, and `Max volumetric speed` |
| Filament > Cooling | Initial no-cooling layers, full-fan layer, minimum/maximum fan with layer-time thresholds, bridge/overhang fan, cooling slowdown, and minimum speed |
| Filament > Setting Overrides | Retraction length/speed, deretraction speed, retract on layer change, wipe, wipe distance, Z-hop height, and Z-hop type; check each override box |
| Process > Quality | Layer height, line widths, `Walls printing order`, `Print infill first`, and seam position |
| Process > Strength | Wall loops, top/bottom shell layers and minimum thickness, sparse infill density, and sparse infill pattern |
| Process > Speed | Initial/feature/travel speeds and feature acceleration |
| Printer > Extruder 1 > Size / Layer height limits | `Nozzle diameter` plus `Min` and `Max` layer height for the custom 0.8 mm printer preset |
| Printer > Motion ability | Leave the installed Kobra 3 Max machine ceilings unchanged |

## Preset Index

| Nozzle | Custom filament preset | Duplicate this exact filament base | Custom process preset | Duplicate this exact process base |
|---:|---|---|---|---|
| 0.4 mm | `GEEETECH TPU 95A - 0.20 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - GEEETECH TPU 95A - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `GEEETECH TPU 95A - 0.12 Detail Experimental` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail Experimental - GEEETECH TPU 95A - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `GEEETECH TPU 95A - 0.24 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - GEEETECH TPU 95A - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU TPU 95A - 0.20 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - SUNLU TPU 95A - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU TPU 95A - 0.12 Detail Experimental` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail Experimental - SUNLU TPU 95A - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU TPU 95A - 0.24 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - SUNLU TPU 95A - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU PETG Black Standard - 0.20 Balanced` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - SUNLU PETG Black Standard - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU PETG Black Standard - 0.12 Detail` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail - SUNLU PETG Black Standard - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU PETG Black Standard - 0.24 Balanced` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - SUNLU PETG Black Standard - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU High Speed PLA+ 2.0 - 0.20 Balanced` | `Anycubic PLA High Speed @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - SUNLU HS PLA+ 2.0 - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU High Speed PLA+ 2.0 - 0.12 Detail` | `Anycubic PLA High Speed @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail - SUNLU HS PLA+ 2.0 - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU High Speed PLA+ 2.0 - 0.24 Balanced` | `Anycubic PLA High Speed @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - SUNLU HS PLA+ 2.0 - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.8 mm | `GEEETECH TPU 95A - N0.8 Safe Start` | `Anycubic TPU @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - GEEETECH TPU 95A - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `GEEETECH TPU 95A - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - GEEETECH TPU 95A - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `SUNLU TPU 95A - N0.8 Safe Start` | `Anycubic TPU @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - SUNLU TPU 95A - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `SUNLU TPU 95A - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - SUNLU TPU 95A - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `SUNLU PETG Black Standard - N0.8 Safe Start` | `Anycubic PETG @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - SUNLU PETG Black - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `SUNLU PETG Black Standard - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - SUNLU PETG Black - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start` | `Anycubic PLA @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - SUNLU HS PLA+ 2.0 - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - SUNLU HS PLA+ 2.0 - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |

If an exact process base is absent from the installed bundle, use these pinned files as settings references rather than importing them or substituting a smaller Kobra 3 preset: [Anycubic 0.12/0.4](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.12mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json), [Anycubic 0.24/0.4](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.24mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json), [Orca 0.20/0.8](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.20mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json), and [Orca 0.40/0.8](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.40mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json). For missing 0.8 bases, follow the manual fallback below.

The 0.8 mm filament-base names come from the pinned Orca Max bundle and may not appear in every Slicer Next installation. With the custom Max 0.8 printer selected, duplicate the visible Anycubic TPU, PETG, or PLA preset for that printer. If none is visible, create a custom copy from the corresponding 0.4 material, enter every filament/cooling/override value below, then set `Filament > Dependencies > Profile dependencies > Compatible printers` to the exact saved 0.8 printer-preset name. Do not leave a 0.4-only compatibility restriction attached.

## 0.8 mm Manual Fallback

Use this only when Slicer Next does not expose a native Max 0.8 preset. Slicer Next may hide process compatibility editing; enable `Show incompatible presets` in the preset selector when the copied process is not visible, and confirm the selected printer still reports a 0.8 mm nozzle before every slice.

### Printer Delta From The Max 0.4 Preset

Duplicate the exact Anycubic `Anycubic Kobra 3 Max 0.4 nozzle` printer preset and save it as `Anycubic Kobra 3 Max 0.8 nozzle`. Retain its 0-426 by 0-420 printable-area polygon, excluded 3 mm side borders that leave the effective X range at 3-423, 501 mm printable height, start/end G-code, acceleration, and jerk values. Change only the following visible fields:

| Slicer Next field | 0.8 mm fallback value |
|---|---:|
| Extruder 1 > Size > Nozzle diameter | 0.8 mm |
| Extruder 1 > Layer height limits > Min | 0.16 mm |
| Extruder 1 > Layer height limits > Max | 0.56 mm |
| Extruder 1 > Z-Hop > Only lift Z above | 0 mm |

The effective machine retraction defaults remain 0.8 mm length, 30 mm/s retract/de-retract, 1 mm travel threshold, layer-change retract on, wipe on at 1 mm, 0.4 mm `Slope` Z-hop, all surfaces, and `Only lift Z below = 499 mm`.

### Process Delta From The Max 0.4 Preset

For **both** manual 0.8 variants, duplicate the exact `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` process. Save one copy as the listed 0.20/N0.8 process and another as the listed 0.40/N0.8 process. After entering every speed, acceleration, quality, and strength value from the main tables, also set these 0.8-specific fields. A native 0.8 process inherits them; a copied 0.4 process does not.

| Slicer Next field | Both 0.8 processes |
|---|---:|
| Quality > Bridge flow ratio | 1.00 |
| Support > Don't support bridges | On |
| Strength > Detect thin wall | On |
| Quality > Elephant foot compensation | 0.10 mm |
| Quality > Extra perimeters on overhangs | On |
| Quality > X-Y hole compensation | 0 mm |
| Quality > Support line width | 0.82 mm |
| Strength > Top/Bottom solid infill/wall overlap | 15% |
| Speed > Gap infill | 50 mm/s |
| Quality > Seam scarf joint | None |
| Quality > Conditional scarf joint / Scarf joint for inner walls | On / On |
| Quality > Scarf length / Scarf start height / Scarf joint speed | 10 mm / 10% / 30 mm/s |

| Slicer Next field | 0.20 mm layer | 0.40 mm layer |
|---|---:|---:|
| Speed > Overhang `(10%, 25%)` | 0 mm/s, use normal wall speed | 50 mm/s |
| Speed > Overhang `[25%, 50%)` | 40 mm/s | 25 mm/s |
| Speed > Overhang `[50%, 75%)` | 15 mm/s | 15 mm/s |
| Speed > Overhang `[75%, 100%)` | 5 mm/s | 10 mm/s |
| Quality > Top surface flow ratio | 1.00 | 0.96 |

When an 0.8 filament preset was copied from a 0.4 base, first clear every retraction Setting Override checkbox. Then check and enter only the values explicitly listed in [Retraction And Lift Overrides](#retraction-and-lift-overrides); this prevents hidden 0.4-only lift limits from carrying over.

## Filament Presets

| Filament preset name | Nozzle | Nozzle temperature: Initial layer / Other layers | Textured PEI Plate: Initial layer / Other layers | Flow ratio | Max volumetric speed | Enable pressure advance / Pressure advance | Drying |
|---|---:|---:|---:|---:|---:|---|---|
| GEEETECH TPU 95A - 0.20 Balanced | 0.4 mm | 225 / 225 deg C | 50 / 45 deg C | 1.00 | 2.3 mm^3/s | Off / 0 s initially | 50-55 deg C, 4-6 h; print from dryer if possible |
| GEEETECH TPU 95A - 0.24 Balanced | 0.4 mm | 225 / 225 deg C | 50 / 45 deg C | 1.00 | 2.3 mm^3/s | Off / 0 s initially | Same |
| GEEETECH TPU 95A - 0.12 Detail Experimental | 0.4 mm | 225 / 225 deg C | 50 / 45 deg C | 1.00 | 1.6 mm^3/s | Off / 0 s initially | Same; prove 0.20 mm reliability first |
| SUNLU TPU 95A - 0.20 Balanced | 0.4 mm | 215 / 210 deg C | 55 / 50 deg C | 0.98 | 3.2 mm^3/s | On / 0.020 s starting value | 55 deg C, 8-12 h; continue from a drybox |
| SUNLU TPU 95A - 0.24 Balanced | 0.4 mm | 215 / 210 deg C | 55 / 50 deg C | 0.98 | 3.2 mm^3/s | On / 0.020 s starting value | Same |
| SUNLU TPU 95A - 0.12 Detail Experimental | 0.4 mm | 215 / 210 deg C | 55 / 50 deg C | 0.98 | 3.2 mm^3/s | On / 0.020 s starting value | Same; prove 0.20 mm reliability first |
| SUNLU PETG Black Standard - 0.20 Balanced | 0.4 mm | 245 / 250 deg C | 75 / 70 deg C | 0.95 | 10 mm^3/s | On / 0.040 s starting value | 60-65 deg C, 6-8 h |
| SUNLU PETG Black Standard - 0.24 Balanced | 0.4 mm | 245 / 250 deg C | 75 / 70 deg C | 0.95 | 10 mm^3/s | On / 0.040 s starting value | Same |
| SUNLU PETG Black Standard - 0.12 Detail | 0.4 mm | 245 / 250 deg C | 75 / 70 deg C | 0.95 | 10 mm^3/s | On / 0.040 s starting value | Same |
| SUNLU High Speed PLA+ 2.0 - 0.20 Balanced | 0.4 mm | 220 / 220 deg C | 60 / 55 deg C | 0.97 | 18 mm^3/s | On / 0.026 s starting value | 50 deg C for at least 4 h if exposed or stringing |
| SUNLU High Speed PLA+ 2.0 - 0.24 Balanced | 0.4 mm | 220 / 220 deg C | 60 / 55 deg C | 0.97 | 18 mm^3/s | On / 0.026 s starting value | Same |
| SUNLU High Speed PLA+ 2.0 - 0.12 Detail | 0.4 mm | 220 / 220 deg C | 60 / 55 deg C | 0.97 | 18 mm^3/s | On / 0.026 s starting value | Same |
| GEEETECH TPU 95A - N0.8 Safe Start | 0.8 mm | 225 / 225 deg C | 50 / 45 deg C | 1.00 starting value | 2.3 mm^3/s temporary cap | Off / 0 s until recalibrated | 50-55 deg C, 4-6 h; print from dryer if possible |
| SUNLU TPU 95A - N0.8 Safe Start | 0.8 mm | 215 / 210 deg C | 55 / 50 deg C | 0.98 starting value | 3.2 mm^3/s temporary cap | Off / 0 s until recalibrated | 55 deg C, 8-12 h; continue from a drybox |
| SUNLU PETG Black Standard - N0.8 Safe Start | 0.8 mm | 245 / 250 deg C | 75 / 70 deg C | 0.95 starting value | 10 mm^3/s temporary cap | Off / 0 s until recalibrated | 60-65 deg C, 6-8 h |
| SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start | 0.8 mm | 220 / 220 deg C | 60 / 55 deg C | 0.97 starting value | 18 mm^3/s temporary cap | Off / 0 s until recalibrated | 50 deg C for at least 4 h if exposed or stringing |

Each 0.24/0.4 process has a separately named filament preset with the same material values as its 0.20 counterpart, avoiding ambiguous `0.20` names in the slicer. Each 0.8 mm filament preset is shared by its 0.20 and 0.40 mm process variants.

`MVS` is maximum volumetric speed. It is the hard sustained-flow cap and matters more than the printer's headline speed. The 0.8 mm values deliberately reuse the proven 0.4 mm caps only for safe first prints; Orca states that MVS changes with nozzle diameter, so recalibrate before increasing them and keep 10-20% below the first failure or quality transition.

The GEEETECH 45 deg C later bed, 25% minimum fan, PETG 75 deg C first-layer bed, and SUNLU TPU 55 deg C/8-12 h drying cycle are derived Kobra/direct-drive starting values outside or between manufacturer bands. They are intentionally labeled recommendations, not manufacturer specifications.

PA sweep ranges are calibration instructions, not preset values: `0.00-0.04 s` for TPU, `0.025-0.060 s` for PETG, and `0.015-0.045 s` for High Speed PLA+ 2.0. If printer auto-calibration is preferred, disable filament PA rather than entering a number.

## Retraction And Lift Overrides

Each material row applies to all listed layer heights and both nozzle sizes. Check every listed override box. These are starting values; retune only after flow and PA are stable with the fitted nozzle.

| Filament | Length | Retraction Speed | De-retraction Speed | Retract when change layer | Wipe while retracting | Wipe Distance | Z-hop height / Z-hop type |
|---|---:|---:|---:|---|---|---:|---|
| GEEETECH TPU 95A | 0.5 mm | 20 mm/s | 20 mm/s | Off | Off | 0 mm | 0 mm / Normal |
| SUNLU TPU 95A | 0.8 mm | 30 mm/s | 25 mm/s | Off | Off | 0 mm | 0 mm / Normal |
| SUNLU PETG Black Standard | 0.8 mm | 30 mm/s | 30 mm/s | On | On | 1 mm | 0.4 mm / Slope |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 35 mm/s | 35 mm/s | On | On | 1 mm | 0.4 mm / Slope |

## Cooling Overrides

| Filament preset | No cooling for the first | Full fan speed at layer | Min fan speed threshold | Max fan speed threshold | Force cooling for overhangs and bridges | Overhangs and external bridges fan speed | Slow printing down for better layer cooling / Min print speed |
|---|---:|---:|---:|---:|---|---:|---|
| GEEETECH TPU 95A - 0.20 Balanced | 2 layers | 4 | 25% at 60 s | 35% at 15 s | On | 50% | On / 10 mm/s |
| GEEETECH TPU 95A - 0.24 Balanced | 2 layers | 4 | 25% at 60 s | 35% at 15 s | On | 50% | On / 10 mm/s |
| GEEETECH TPU 95A - 0.12 Detail Experimental | 2 layers | 4 | 30% at 60 s | 40% at 15 s | On | 50% | On / 8 mm/s |
| SUNLU TPU 95A - 0.20 Balanced | 2 layers | 4 | 30% at 60 s | 50% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU TPU 95A - 0.24 Balanced | 2 layers | 4 | 30% at 60 s | 50% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU TPU 95A - 0.12 Detail Experimental | 2 layers | 4 | 40% at 60 s | 60% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU PETG Black Standard - 0.20 Balanced | 3 layers | 6 | 35% at 60 s | 55% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU PETG Black Standard - 0.24 Balanced | 3 layers | 6 | 35% at 60 s | 55% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU PETG Black Standard - 0.12 Detail | 3 layers | 6 | 40% at 60 s | 65% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - 0.20 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - 0.24 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - 0.12 Detail | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| GEEETECH TPU 95A - N0.8 Safe Start | 2 layers | 4 | 25% at 60 s | 35% at 15 s | On | 50% | On / 7 mm/s |
| SUNLU TPU 95A - N0.8 Safe Start | 2 layers | 4 | 30% at 60 s | 50% at 15 s | On | 100% | On / 9 mm/s |
| SUNLU PETG Black Standard - N0.8 Safe Start | 3 layers | 6 | 35% at 60 s | 55% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |

The 0.24/0.4 cooling values match the corresponding 0.20/0.4 starting values. Each 0.8 cooling row serves both 0.20 and 0.40 mm processes; layer-time slowdown handles most geometry-dependent differences. The thresholds are derived starting values. Unlisted cooling fields inherit from the duplicated filament base in the preset index; inspect the sliced preview for unexpected slowdowns.

Both 0.12 mm TPU profiles are experimental. First complete a representative 0.20 mm print reliably; 0.12 mm greatly increases layer count, print duration, retraction opportunities, and exposure to feed drag. Fall back to 0.16 mm or 0.20 mm if extrusion becomes intermittent.

## Process Speeds

| Filament | Nozzle | Layer | Initial layer | Initial layer infill | Outer wall | Inner wall | Sparse infill | Internal solid infill | Top surface | External bridge | Travel |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 12 mm/s | 15 mm/s | 18 mm/s | 24 mm/s | 25 mm/s | 20 mm/s | 16 mm/s | 12 mm/s | 160 mm/s |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 12 mm/s | 15 mm/s | 20 mm/s | 25 mm/s | 25 mm/s | 22 mm/s | 18 mm/s | 15 mm/s | 180 mm/s |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 12 mm/s | 15 mm/s | 20 mm/s | 21 mm/s | 21 mm/s | 20 mm/s | 18 mm/s | 15 mm/s | 180 mm/s |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 6 mm/s | 7 mm/s | 12 mm/s | 14 mm/s | 14 mm/s | 13 mm/s | 11 mm/s | 10 mm/s | 180 mm/s |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 6 mm/s | 7 mm/s | 6 mm/s | 7 mm/s | 7 mm/s | 6 mm/s | 5 mm/s | 5 mm/s | 160 mm/s |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 20 mm/s | 20 mm/s | 30 mm/s | 45 mm/s | 50 mm/s | 40 mm/s | 30 mm/s | 20 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 20 mm/s | 20 mm/s | 25 mm/s | 35 mm/s | 35 mm/s | 30 mm/s | 25 mm/s | 20 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 20 mm/s | 20 mm/s | 25 mm/s | 29 mm/s | 29 mm/s | 28 mm/s | 25 mm/s | 20 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 8 mm/s | 9 mm/s | 16 mm/s | 19 mm/s | 19 mm/s | 18 mm/s | 16 mm/s | 14 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 8 mm/s | 9 mm/s | 8 mm/s | 9 mm/s | 9 mm/s | 9 mm/s | 7 mm/s | 7 mm/s | 160 mm/s |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 30 mm/s | 35 mm/s | 65 mm/s | 90 mm/s | 100 mm/s | 80 mm/s | 45 mm/s | 22 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 30 mm/s | 35 mm/s | 80 mm/s | 110 mm/s | 110 mm/s | 90 mm/s | 55 mm/s | 25 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 30 mm/s | 35 mm/s | 80 mm/s | 90 mm/s | 90 mm/s | 85 mm/s | 50 mm/s | 25 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 20 mm/s | 25 mm/s | 45 mm/s | 60 mm/s | 60 mm/s | 50 mm/s | 40 mm/s | 25 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 20 mm/s | 25 mm/s | 25 mm/s | 30 mm/s | 30 mm/s | 28 mm/s | 20 mm/s | 18 mm/s | 230 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 35 mm/s | 45 mm/s | 100 mm/s | 180 mm/s | 230 mm/s | 150 mm/s | 80 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 35 mm/s | 45 mm/s | 120 mm/s | 180 mm/s | 200 mm/s | 160 mm/s | 80 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 35 mm/s | 45 mm/s | 110 mm/s | 165 mm/s | 165 mm/s | 145 mm/s | 75 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 25 mm/s | 35 mm/s | 75 mm/s | 105 mm/s | 105 mm/s | 95 mm/s | 60 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 25 mm/s | 35 mm/s | 40 mm/s | 54 mm/s | 54 mm/s | 48 mm/s | 35 mm/s | 25 mm/s | 280 mm/s |

For the 0.8 mm rows, the temporary rectangular flow ceilings at 0.82 mm line width are approximately `14/7 mm/s` for GEEETECH TPU, `20/10 mm/s` for SUNLU TPU, `61/30 mm/s` for PETG, and `110/55 mm/s` for High Speed PLA+ at 0.20/0.40 mm layers. The table stays at or below those caps for extrusion features; travel is not flow-limited. Confirm in Preview using the `Flow` color scheme because the slicer's rounded bead model can differ slightly from the rectangular check.

## Process Acceleration

| Filament | Nozzle | Layer | Normal printing | Initial layer | Outer wall | Inner wall | Sparse infill | Internal solid infill | Top surface | Bridge | Travel |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 1,000 | 400 | 600 | 900 | 1,200 | 700 | 500 | 400 | 2,500 |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 1,500 | 500 | 800 | 1,200 | 1,500 | 1,000 | 700 | 500 | 3,000 |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 1,500 | 500 | 800 | 1,200 | 1,500 | 1,000 | 700 | 500 | 3,000 |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 1,000 | 400 | 600 | 800 | 1,000 | 700 | 500 | 400 | 2,500 |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 700 | 300 | 400 | 600 | 700 | 500 | 350 | 300 | 2,000 |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 1,000 | 500 | 600 | 900 | 1,000 | 800 | 600 | 600 | 3,000 |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 1,000 | 500 | 600 | 1,000 | 1,000 | 800 | 600 | 600 | 3,000 |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 1,000 | 500 | 600 | 1,000 | 1,000 | 800 | 600 | 600 | 3,000 |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 1,000 | 500 | 600 | 900 | 1,000 | 800 | 600 | 500 | 2,500 |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 800 | 400 | 500 | 700 | 800 | 600 | 500 | 400 | 2,200 |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 2,500 | 500 | 900 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 3,000 | 500 | 1,200 | 2,500 | 3,000 | 2,000 | 1,000 | 1,200 | 6,000 |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 2,800 | 500 | 1,100 | 2,300 | 2,800 | 2,000 | 1,000 | 1,200 | 5,500 |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 2,500 | 500 | 900 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 2,000 | 500 | 800 | 1,600 | 2,000 | 1,500 | 700 | 800 | 4,500 |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 4,500 | 500 | 1,500 | 3,500 | 4,500 | 3,000 | 1,000 | 2,000 | 8,000 |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 5,000 | 500 | 2,000 | 4,000 | 5,000 | 3,500 | 1,000 | 2,500 | 8,000 |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 4,500 | 500 | 1,800 | 3,800 | 4,500 | 3,300 | 1,000 | 2,300 | 7,500 |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 4,000 | 500 | 1,500 | 3,200 | 4,000 | 2,800 | 900 | 1,800 | 7,000 |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 3,200 | 500 | 1,200 | 2,600 | 3,200 | 2,300 | 800 | 1,500 | 6,500 |

Acceleration values are in `mm/s^2`. Lower outer/top acceleration is intentional on the Max's large moving bed.

## Quality And Line Width

| Filament | Nozzle | Layer height | Initial layer height | Default line width | Outer wall | Inner wall | Sparse infill | Internal solid infill | Top surface | Initial layer width | Walls printing order | Print infill first | Seam position |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.40 | 0.42 | 0.45 | 0.42 | 0.40 | 0.50 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 0.20 mm | 0.45 | 0.42 | 0.45 | 0.45 | 0.45 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 0.24 mm | 0.45 | 0.42 | 0.45 | 0.45 | 0.45 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |

Line-width values are in `mm`. The 0.8 mm values match the pinned Orca Max 0.8 process geometry. Paint or rotate the aligned seam onto a hidden edge per model; seam painting is not a reusable preset field.

## Strength

For every custom process below, explicitly set `Top shell thickness = 0 mm` and `Bottom shell thickness = 0 mm`. This makes the listed layer counts authoritative; otherwise an inherited 1 mm minimum can turn four 0.24 mm top layers into five.

| Filament | Nozzle | Layer | Wall loops | Top shell layers | Bottom shell layers | Sparse infill density | Sparse infill pattern |
|---|---:|---:|---:|---:|---:|---:|---|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 3 | 8 | 7 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 3 | 8 | 7 | 15% | Gyroid |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 3 | 8 | 7 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 3 | 7 | 7 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |

Use more walls, not just more infill, when strength is the priority. Two 0.82 mm walls are already about 1.64 mm thick; add a third only when the model needs it. Extra walls and infill make TPU parts less flexible. Avoid TPU supports where possible; they are difficult to remove.

## What Owners Reported

| Material | Online experience | How it changed this profile |
|---|---|---|
| GEEETECH TPU 95A | A Kobra 3 owner completed two long prints, then repeatedly had GEEETECH 95A wrap around the extruder rollers. Retract-heavy small geometry was worse; slower speed and slicer changes did not reliably cure it. [Forum thread](https://forum.drucktipps3d.de/forum/thread/39344-kobra-3-tpu-problem-im-extruder/) | Conservative 20-25 mm/s extrusion, short top feed, clean hotend, wipe off, no layer-change retract, and a stop-and-inspect rule for clicking. |
| GEEETECH TPU 95A | A Kobra 3 Max user reported about 25 mm/s as the reliable ceiling and clogging above it; other owners recommended a roughly six-inch top-fed tube. [Reddit](https://old.reddit.com/r/AnycubicOfficial/comments/1k4n3ou/any_tips_on_printing_tpu_on_anycubic_kobra_3_max/) | The Kobra-specific 25 mm/s evidence overrides faster generic reviews. |
| SUNLU TPU 95A | An X1C owner improved stringing with 200 deg C, flow 1.0, 4.5 mm^3/s, 0.8 mm at 25 mm/s retraction, 30-50% fan, and 100% bridge fan. [Bambu forum](https://forum.bambulab.com/t/settings-for-sunlu-tpu/34584) | Supports moderate temperature, short retraction, and localized high bridge cooling. The Max profile remains slower and lower-flow. |
| SUNLU TPU 95A | An A1 owner found 50 deg C for 6 hours insufficient; 65 deg C for 12 hours improved wet-filament symptoms. [Reddit](https://old.reddit.com/r/FixMyPrint/comments/1uw2spm/issues_printing_tpu_honeycomb/) | The recommended 55 deg C for 8-12 hours is a conservative derived compromise; use a calibrated dryer and let the spool cool before feeding. |
| SUNLU TPU 95A | A Qidi owner found reducing MVS only delayed failure; removing the PTFE tube enabled a 13-hour print. [Reddit](https://old.reddit.com/r/QidiTech3D/comments/1jzpg5s/q1_pro_tpu_issue_filament_feeding/) | Feed drag must be fixed before treating the problem as a nozzle or speed issue. |
| SUNLU PETG Black | A direct color-match owner used 250 deg C first layer and 245 deg C later, with fan mostly off except for overhangs. [Bambu forum](https://forum.bambulab.com/t/best-settings-for-sunlu-petg/33776?page=2#post_35) | Supports 245-250 deg C and moderate normal cooling rather than full fan. |
| PETG on Kobra 3 | An owner reported nearly flawless output at 250/100 deg C for two layers, then 240/80 deg C and 80 mm/s; later users reported improvement. [Reddit](https://old.reddit.com/r/anycubic/comments/1exjpt8/petg_on_kobra_3/) | Confirms slower first layers and a warm bed, but 100 deg C is not used as a general default. |
| SUNLU High Speed PLA+ 2.0 | An exact-product owner at 450 mm/s reported slight stringing, visible VFAs, about 5% worse finish, and only about 35% shorter print time. [Reddit](https://www.reddit.com/r/3Dprinting/comments/1m1w03t/favorite_brand_of_filament/n3l70c2/) | Keeps visible walls at 100-120 mm/s; internal features use 180-200 mm/s at 0.20 mm and up to 230 mm/s at 0.12 mm. |

## Calibration Order

| Step | Action | Keep or change the table value when... |
|---:|---|---|
| 0 | After fitting the 0.8 mm nozzle, select the matching printer preset, rerun leveling, and verify Z offset with a first-layer patch. | The slicer still reports a 0.4 mm nozzle or an initial-layer line width other than 0.82 mm: stop and correct the printer/process preset before calibration. |
| 1 | Dry the spool and use the intended feed path. | Popping, bubbles, roughness, or fine stringing remain: dry again before tuning retraction. |
| 2 | Verify the first layer and bed cleanliness. | Large PETG parts lift: preheat longer, use 5-8 mm brim/mouse ears, then raise bed by 5 deg C if needed. |
| 3 | Run a temperature tower at representative speed. | High-flow lines look matte/weak: raise 5 deg C. Excess gloss or ooze: lower 5 deg C. |
| 4 | Calibrate flow ratio separately for each nozzle/material pair. | Change in 0.01 steps. Do not use flow to hide a partial clog or TPU feed drag. |
| 5 | Calibrate PA separately for each nozzle/material pair; only after stable TPU extrusion for TPU. | Corners bulge: PA may be low. Thin corners or gaps after direction changes: PA may be high. |
| 6 | Run maximum volumetric-flow calibration separately for every nozzle/material pair. | Set MVS 10-20% below the first repeatable roughness, gloss transition, under-extrusion, or layer-strength failure; after increasing MVS, revalidate PA at representative flow. |
| 7 | Tune retraction last. | TPU clicking/wrapping: set retraction to 0 before increasing it. Rigid-filament stringing after drying: adjust by 0.1 mm. |
| 8 | Print a dimensional coupon. | Apply XY/hole compensation only from measured error, not another printer's profile. |

## Failure Corrections

| Symptom | First correction |
|---|---|
| TPU wraps around gears or extruder clicks | Stop immediately. Set retraction to 0, keep wipe and z-hop off, shorten the feed path, inspect idler pressure, and purge/clean the nozzle. For GEEETECH, reduce to 20 mm/s and 1.8 mm^3/s MVS. |
| TPU prints air after several hours | Check spool/tube drag and hotend residue. Do not assume a true nozzle clog. Let a warm spool cool before feeding if the drive wheel slips. |
| TPU strings | Dry again, avoid crossing walls, then lower nozzle 5 deg C. Increase retraction only after extrusion is mechanically reliable. |
| PETG strings or blobs | Dry, lower nozzle 5 deg C, verify flow, then test 0.9-1.0 mm retraction. |
| PETG weak or matte at speed | Raise nozzle 5 deg C or reduce MVS from 10 to 8 mm^3/s; reduce normal fan by 10 percentage points. |
| PETG damages or locks to PEI | Lower first-layer nozzle/bed by 5 deg C, add a thin glue release layer, and wait for full cooling. |
| PLA+ rough/matte high-speed infill | Reduce MVS from 18 to 16 mm^3/s before lowering every feature speed. |
| PLA+ ringing or VFAs | Reduce outer wall to 80-100 mm/s and outer acceleration to 1,200-1,500 mm/s^2. |
| Poor top surface | Lower top speed by 15-20 mm/s or add one top layer after flow is calibrated. |
| 0.8 mm profile under-extrudes | Confirm the 0.8 mm printer preset and 0.82 mm line widths, then lower MVS by 15%, inspect the nozzle/hotend, and run a temperature tower. Do not compensate by increasing flow ratio. |
| 0.8 mm first layer is over-squished or detached | Recheck nozzle installation, leveling, and Z offset with the 0.40 mm first-layer height before changing bed temperature or flow. |

## Sources And Limits

### Manufacturer Data

- [Anycubic Kobra 3 Max specifications](https://www.anycubic.com/products/kobra-3-max)
- [Anycubic Kobra 3 Max Combo specifications](https://www.anycubic.com/products/kobra-3-max-combo), including standard 0.4 mm and expandable 0.6/0.8 mm nozzle support
- [Anycubic Kobra 3 Max TPU guide](https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/tpu-printing-guide)
- [SUNLU TPU 95A product data](https://www.sunlu.com/products/tpu-95a-flexible-filament) and [TDS](https://media.sunlu.com/prod/20260330/e8b9c06a-4b93-46cb-9532-d9deb185a7c8.pdf?filename=TDS)
- [SUNLU standard PETG product data](https://www.sunlu.com/products/petg-3d-printing-filament) and [filament/drying guide](https://www.sunlu.com/wiki/filament-usage-guide)
- [SUNLU High Speed PLA+ 2.0 product data](https://store.sunlu.com/products/moq-6kg-high-speed-pla-2-0hspla-plus-2-0-high-speed-3d-printer-filament-1kg) and [TDS](https://media.sunlu.com/prod/20260330/225ab1bc-a40a-435b-8d20-a2745303674b.pdf?filename=TDS)
- [GEEETECH TPU product data](https://www.geeetech.com/products/tpu-3d-printer-filament-1-75mm-1kg-roll), [printing guide](https://blog.geeetech.com/materials/tpu-filament-guide-how-to-print-with-tpu/), and [drying guide](https://blog.geeetech.com/materials/3d-printing-filament/why-tpu-filament-absorbs-moisture-easily-and-how-to-dry-it/)

### Slicer Behavior And Reference Profiles

- [Anycubic Slicer Next parameter guide](https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta(orca-version)/parameter-settings)
- [Anycubic Slicer Next v2.3.0 commit `70931e5`](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/commit/70931e5321fa66966a5bfb251efca0e82307d427), used for field semantics; the repository publishes tags rather than GitHub releases
- [Anycubic Kobra 3 Max 0.4 mm machine profile, pinned commit](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/machine/Anycubic%20Kobra%203%20Max%200.4%20nozzle.json)
- [Anycubic Kobra 3 Max 0.20 mm process profile, pinned commit](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.20mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json)
- [Anycubic Kobra 3 Max 0.24 mm / 0.4 mm process profile, pinned commit](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.24mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json)
- [OrcaSlicer Kobra 3 Max merge commit `972dae2`](https://github.com/OrcaSlicer/OrcaSlicer/commit/972dae22afdadc3251d05e10c2d6f00c35e6b83a), a secondary profile reference
- [Orca Kobra 3 Max 0.8 mm machine profile](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/machine/Anycubic%20Kobra%203%20Max%200.8%20nozzle.json)
- [Orca Kobra 3 Max 0.20 mm / 0.8 mm process](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.20mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json) and [0.40 mm / 0.8 mm process](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.40mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json)
- [Orca maximum volumetric-speed calibration](https://github.com/OrcaSlicer/OrcaSlicer/wiki/volumetric_speed_calib) and [pressure-advance calibration](https://github.com/OrcaSlicer/OrcaSlicer/wiki/pressure_advance_calib)

### Owner Reports

- The directly retrieved owner evidence used to modify these profiles is linked row-by-row in [What Owners Reported](#what-owners-reported).

The strongest online experience evidence is material- and printer-specific for GEEETECH TPU, but exact SUNLU TPU 95A/Kobra 3 Max evidence is scarce. Reports from other modern direct-drive printers are therefore labeled as transferable experience rather than proof. Kobra 3 reports also transfer imperfectly to the Max because the Max has a much larger moving bed and lower quality-oriented process acceleration.
