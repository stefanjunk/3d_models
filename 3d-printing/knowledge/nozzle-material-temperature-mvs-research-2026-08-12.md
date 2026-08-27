# Nozzle Material, Temperature, And MVS Research

**Printer scope:** Stock Anycubic Kobra 3 Max<br>
**Nozzle scope:** 0.4 and 0.8 mm standard-bore Kobra-compatible nozzles in brass, stainless steel, and conventional hardened steel<br>
**Filament scope:** The seven materials in `anycubic-kobra-3-max-filament-settings.md`<br>
**Research date:** 12 August 2026

## Decision Summary

1. Keep the existing brass temperatures and MVS values as the operational baseline.
2. Start stainless and conventional hardened steel at the same indicated temperature as brass after a 5-minute heat soak.
3. Permit a `+5 C` fallback only when a representative high-flow test repeatedly shows weak, matte, or under-extruded lines and the exact filament range permits it.
4. Enter 80% of brass MVS for the first untested steel print, then replace that value with 80-90% of the installed nozzle/material pair's measured failure transition.
5. Treat the 80% value as an uncalibrated commissioning safety policy, not a measured conductivity penalty. A quality steel nozzle can equal the brass result.
6. Calibrate diameter and material as independent variables. A 0.8 mm outlet lowers path speed at a given MVS and may reduce pressure, but it does not proportionally lengthen the melt zone.

The evidence does not support a universal steel temperature offset or an alloy-derived MVS multiplier. The operational policy is deliberately conservative where direct Kobra evidence is absent.

## Research Questions

- How different are representative brass, stainless, and hardened-steel thermal conductivities?
- Does that difference prove a required change in the printer's indicated nozzle temperature?
- Is there controlled applied evidence comparing brass and steel flow?
- Can one defensible MVS correction be transferred across seven polymers, two diameters, and three nozzle materials?
- Which values can be entered before physical calibration without misrepresenting uncertainty?

## Method

The first research cycle established material-property direction, printer/profile context, vendor guidance, and applied flow evidence. The second cycle searched specifically for counterexamples to an automatic temperature increase, controlled identical-geometry stainless comparisons, Kobra 3 Max steel-nozzle flow data, and reasons not to scale MVS from bulk conductivity. Sources were ranked as follows:

1. Manufacturer alloy datasheets for representative conductivity.
2. Version-pinned slicer profiles for exact field values and machine context.
3. Controlled applied extrusion experiments for flow behavior.
4. Printer/nozzle vendor guidance for troubleshooting practice.
5. Owner reports for failure-mode discovery, never as universal constants.

The comparison excludes CHT or split-bore high-flow designs, longer melt zones, ruby/carbide inserts, proprietary high-conductivity hardened alloys, special coatings that claim brass-like performance, and different hotends. These changes can outweigh bulk nozzle material.

## Evidence Matrix

| Claim | Best evidence | What it establishes | What it does not establish | Confidence |
|---|---|---|---|---|
| Brass conducts heat much better than the two representative steels | Copper Development Association C36000, Alleima 304/3R12, Uddeholm Rigor/A2 | Direction and approximate magnitude of bulk conductivity | Exact alloy in an unverified retail nozzle; required print-temperature offset | High for representative alloys |
| Temperature materially changes achievable flow | CNC Kitchen V6 mass-flow benchmark | In one V6/PLA system, higher temperature reduced slip and raised usable flow | Exact Kobra/PETG/TPU/Silk MVS | Medium-high, system-specific |
| Quality hardened steel may not require more indicated heat | CNC Kitchen brass/hardened-steel comparison | Noticeable difference mainly below about 200 C in the tested V6/PLA setup | Stainless behavior or all steel nozzles | Medium, controlled but narrow |
| Steel may need a small increase when under-extruding | Prusa troubleshooting guidance | A practical conditional correction | A mandatory offset for every print | Medium |
| MVS depends on the complete extrusion system | E3D flow guidance and Orca MVS calibration guidance | Material, temperature, geometry, machine, extruder, and nozzle all matter | A universal steel multiplier | High as process guidance |
| Exact Kobra steel MVS values exist for all requested combinations | No qualifying source found | Research gap | Any numerical material penalty | None |

## Material Properties

Representative values used only to establish direction:

| Representative nozzle alloy | Thermal conductivity | Temperature context | Source |
|---|---:|---:|---|
| C36000 free-cutting brass | About 116 W/(m K) | 20 C | [Copper Development Association](https://alloys.copper.org/alloy/C36000) |
| 304-type stainless / Alleima 3R12 | About 15 W/(m K); about 18 W/(m K) | 20 C; 200 C | [Alleima datasheet](https://www.alleima.com/en/technical-center/material-datasheets/tube-and-pipe-seamless/alleima-3r12/) |
| Hardened A2-type tool steel / Uddeholm Rigor | About 26 W/(m K); about 27 W/(m K) | 20 C; 200 C | [Uddeholm datasheet](https://www.uddeholm.com/en/app/uploads/sites/216/productdb/api/tech_uddeholm-rigor_en.pdf) |

Stainless is therefore less conductive than the representative hardened tool steel, and both are much less conductive than C360 brass. It would still be invalid to divide an MVS or multiply a temperature by those ratios. The printer controls heater-block sensor temperature, not polymer-core temperature at the nozzle exit. Interface contact, sensor placement, heater power, nozzle mass and length, melt-zone geometry, bore finish, plating, polymer viscosity, pigment, and flow all affect the result.

## Applied Flow Evidence And Counterevidence

[CNC Kitchen's flow benchmark](https://www.cnckitchen.com/blog/flow-rate-benchmarking-of-a-hotend) extruded fixed filament lengths and weighed the output. In the tested stock V6/Bondtech/PLA system at 215 C, under-extrusion appeared before audible skipping and the practical limit was around 10-15 mm3/s. Raising temperature materially reduced slip at a fixed 15 mm3/s. This supports testing temperature at representative flow rather than relying only on a slow temperature tower.

The same experiment compared a standard E3D hardened-steel nozzle with brass. A noticeable difference appeared mainly below about 200 C; the author concluded that a quality hardened-steel nozzle need not automatically run hotter. This directly contradicts a universal `+5` or `+10 C` rule, while remaining too narrow to prove identical behavior for stainless, the Kobra hotend, or every polymer.

[Prusa's nozzle guidance](https://help.prusa3d.com/article/e3d-v6-nozzles_920168) and [under-extrusion troubleshooting](https://help.prusa3d.com/article/under-extrusion_2007) support small steel temperature increases as a correction when symptoms justify them. Read together with the controlled counterexample, the defensible policy is conditional testing, not a preset-wide automatic offset.

No qualifying controlled experiment was found that held Kobra geometry, bore, installation, filament, color, drying, temperature, and flow constant while comparing brass, stainless, and hardened steel. Stainless therefore remains a separate commissioning column but not a separately claimed measured penalty.

## Temperature Policy

For every row in the operational table:

- Begin steel at the brass initial/other-layer temperatures.
- Heat-soak at target temperature for 5 minutes.
- Use a representative high-flow test and inspect both surface and layer strength.
- Try `+5 C` only for repeatable weak, matte, or under-extruded lines and only inside the exact filament's documented or defensible range.
- Restore baseline and lower MVS if the increase causes more stringing, ooze, degradation, heat creep, or an unwanted Silk sheen change.
- Do not exceed GRATKIT's documented all-metal-hotend ceiling; its 0.8 mm row therefore has no hotter fallback.

This policy gives stainless and hardened steel the same starting temperature, not because their conductivities are equal, but because no evidence maps either conductivity to a reliable indicated-temperature correction in this hotend.

## MVS Policy

Maximum volumetric speed is a complete-system calibration result. The first steel value is calculated as:

```text
steel commissioning MVS = 0.80 x brass profile MVS
```

Decimal presentation follows useful slicer precision. Examples are 10 to 8 mm3/s, 18 to 14.4 mm3/s, 3.0 to 2.4 mm3/s, and 2.3 to 1.8 mm3/s after rounding. Stainless and hardened steel receive separate saved presets even where the initial number is the same.

The 20% reserve covers unknown installation, bore finish, alloy, and thermal response for a first print. It is not inferred from conductivity and is not retained after calibration. For each diameter/material/filament pair:

1. Dry the filament and stabilize the feed path.
2. Verify installation, PID behavior where applicable, leveling, and Z offset.
3. Calibrate temperature and flow ratio.
4. Run MVS until the first repeatable roughness, gloss transition, under-extrusion, extruder slip/clicking, or layer-strength failure.
5. Retain 80-90% of that transition.
6. Revalidate pressure advance at representative flow.

If calibrated steel reaches brass MVS with equivalent quality and strength, use 100% of brass. If it fails earlier, record the measured result and test conditions instead of preserving the generic 80% value.

## Nozzle Diameter Interaction

Approximate path flow is:

```text
flow (mm3/s) = line width (mm) x layer height (mm) x path speed (mm/s)
```

At 12 mm3/s with the guide's 0.82 mm line width, ELEGOO Rapid PETG reaches approximately 73 mm/s at 0.20 mm layers and 36 mm/s at 0.40 mm layers. A larger nozzle does not turn the printer's advertised 600 mm/s motion speed into an extrusion speed. Slicer Preview remains authoritative because its bead model is more detailed than this rectangular screening calculation.

## ELEGOO Rapid PETG Application

ELEGOO's [product data](https://www.elegoo.com/products/rapid-petg-filament-1-75mm-colored-1kg.js) identifies unfilled Rapid PETG, 1.75 mm, +/-0.02 mm, and a marketing capability up to 600 mm/s. The exact [Anycubic Slicer Next ELEGOO base](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/blob/4f50fdc94ebbc798d57716c031be16f75b70c0a5/resources/profiles/Elegoo/filament/ELEGOO/Elegoo%20RAPID%20PETG%20%40base.json) uses 250 C, 70 C bed, density 1.26, 30-80% normal cooling, 90% overhang cooling, and 18 mm3/s MVS. The exact [Orca system profile](https://github.com/OrcaSlicer/OrcaSlicer/blob/43a83397d4e4e032edf0fca5258ccd0ab886a7d4/resources/profiles/OrcaFilamentLibrary/filament/Elegoo/Elegoo%20Rapid%20PETG%20%40System.json) uses flow 0.99, PA 0.052, and 18 mm3/s.

ELEGOO machine profiles range from 10 to 34 mm3/s, demonstrating that MVS is not a product constant. The exact standard-PETG Kobra references use flow 0.95/MVS 8 at 0.4 and flow 0.97/MVS 12 at 0.8. The Rapid PETG profile retains those Kobra flow-ratio starts and the exact 0.8 MVS, while its 10 mm3/s 0.4 value is a derived conservative step above standard PETG and below ELEGOO's 18 mm3/s system profile. PA starts disabled until nozzle-specific calibration. A later 14 or 16 mm3/s cap requires a measured failure transition of at least about 16.5 or 18.8 mm3/s when retaining 85% margin.

The advertised 600 mm/s would require about 54 mm3/s at 0.45 x 0.20 mm, so it is not used as a Kobra feature speed. Plain Rapid PETG has no abrasive filler claim; this does not apply to PETG-CF, PETG-GF, glow, metal-filled, or other filled variants.

The exact German offer checked on 12 August 2026 was [Alza white, 1 kg, EUR 13.49 including VAT](https://www.alza.de/elegoo-rapid-petg-1-75mm-1kg-cardboard-spool-white-d12389175.htm), shown in stock above 10 units. The retailer listed 240-270 C, 65-75 C bed, and 30-600 mm/s; those fields confirm product identity but do not replace the versioned slicer profiles or Kobra calibration.

## Operational Output

The main guide now provides:

- 7 materials and 35 fixed process combinations.
- 28 logical filament-preset rows: 21 at 0.4 mm and 7 shared 0.8 mm presets.
- Separate brass, stainless, and hardened temperature/MVS columns in every filament row.
- 28 cooling rows, 7 retraction rows, and 35 rows each for speed, acceleration, quality/line width, and strength.
- A calibration sequence that invalidates nozzle-sensitive values after a diameter or material change.

## Limitations

- No physical Kobra 3 Max validation prints were performed in this research pass.
- Retail nozzle alloy, heat treatment, coating, bore quality, and exact geometry may differ from the representative materials.
- The strongest controlled steel comparison covers hardened steel, PLA, and an E3D V6 rather than stainless, the Kobra hotend, and all seven filaments.
- Owner reports are useful for discovering feed, cooling, and surface failures but cannot establish a universal MVS.
- The 80% steel values and ELEGOO 10/12 mm3/s values remain conservative starts until measured on the installed hardware.

## Sources

- [Copper Development Association: C36000](https://alloys.copper.org/alloy/C36000)
- [Alleima 3R12 / 304-type stainless datasheet](https://www.alleima.com/en/technical-center/material-datasheets/tube-and-pipe-seamless/alleima-3r12/)
- [Uddeholm Rigor / A2-type tool-steel datasheet](https://www.uddeholm.com/en/app/uploads/sites/216/productdb/api/tech_uddeholm-rigor_en.pdf)
- [CNC Kitchen: Flow Rate Benchmarking of a Hotend](https://www.cnckitchen.com/blog/flow-rate-benchmarking-of-a-hotend)
- [Prusa: E3D V6 Nozzles](https://help.prusa3d.com/article/e3d-v6-nozzles_920168)
- [Prusa: Under-extrusion](https://help.prusa3d.com/article/under-extrusion_2007)
- [E3D: Volumetric Flow Rate Guidance](https://e3d-online.com/pages/revo-high-flow-volumetric-flow-rate-calculator)
- [OrcaSlicer: Maximum Volumetric Speed Calibration](https://github.com/OrcaSlicer/OrcaSlicer/wiki/volumetric_speed_calib)
- [ELEGOO Rapid PETG Product Data](https://www.elegoo.com/products/rapid-petg-filament-1-75mm-colored-1kg.js)
- [Anycubic Slicer Next: ELEGOO Rapid PETG Base](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/blob/4f50fdc94ebbc798d57716c031be16f75b70c0a5/resources/profiles/Elegoo/filament/ELEGOO/Elegoo%20RAPID%20PETG%20%40base.json)
- [OrcaSlicer: ELEGOO Rapid PETG System Profile](https://github.com/OrcaSlicer/OrcaSlicer/blob/43a83397d4e4e032edf0fca5258ccd0ab886a7d4/resources/profiles/OrcaFilamentLibrary/filament/Elegoo/Elegoo%20Rapid%20PETG%20%40System.json)
- [Alza Germany: ELEGOO Rapid PETG White 1 kg](https://www.alza.de/elegoo-rapid-petg-1-75mm-1kg-cardboard-spool-white-d12389175.htm)
