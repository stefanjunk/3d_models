# Filament selection guidance

Use `data/materials.yaml` as a filterable knowledge base and run:

```bash
python scripts/select_material.py --help
```

## Selection order

1. Environment: temperature, sunlight, moisture, chemicals, flame/smoke requirements.
2. Mechanical behavior: stiffness, impact, fatigue, creep, wear, flexibility.
3. Printer capability: hotend temperature, bed, chamber, nozzle, drying.
4. Geometry/process: bridging, warp, support, dimensional stability, surface finish.
5. Evidence: exact supplier datasheet and tests on the printed orientation/profile.

Do not select by marketing label alone. PLA+, Tough PLA, PC blends, co-polyesters, and fiber-filled families vary substantially by brand.

## Broad material map

| Family | Good at | Main limitations | Typical use |
|---|---|---|---|
| PLA | easiest detail, stiffness, low warp | heat, creep, impact/fatigue | prototypes, organizers, indoor display |
| PLA+/Tough PLA | easier printing with improved toughness in some brands | not standardized; heat still often limited | indoor functional parts after datasheet review |
| PETG/CPE | toughness, layer bonding, wet/chemical exposure | stringing, bridges, creep, surface scuff | housings, brackets, containers, mechanisms |
| PETG-CF/GF | stiffness, surface, dimensional stability | abrasive, reduced ductility, fiber direction | rigid fixtures and housings, not snap arms by default |
| ABS | impact and temperature over PLA | warp, fumes/odor, enclosure | enclosures, automotive-like indoor parts |
| ASA | UV/weather performance | enclosure/warp/ventilation | outdoor housings, mounts, signage |
| HIPS | machinable/light, dissolvable support with compatible system | lower strength, solvent handling | support or lightweight models |
| PA/nylon | toughness, fatigue, wear, heat | very hygroscopic, warp, drying | gears, clips, bushings, durable mechanisms |
| PA-CF/GF | stiffness, stability, heat | abrasive, anisotropic/brittle features, drying | structural fixtures and rigid technical parts |
| PC/PC blend | strength, heat, impact | demanding chamber/adhesion; blends vary | hot/strong housings and fixtures |
| TPU/TPE | flexibility, grip, impact, seals | slow printing, stringing, dimensional compliance | feet, tires, gaskets, wear pads, flexures |
| PP | fatigue/living hinges, chemical resistance, low density | severe bed-adhesion/warp challenges | living hinges, containers, chemical parts |
| PVB | visual finish and solvent smoothing | not a structural default | translucent/display/decorative parts |
| PVA/BVOH | soluble support | moisture sensitive, compatibility/cost | complex support interfaces |
| wood/metal/mineral/glow fills | appearance or special visual effect | abrasion/clogs, weaker or denser parts | decorative surfaces and props |
| PEI/PEEK/PEKK/PPS | high-performance heat/chemical behavior | industrial temperatures/chamber/drying | specialized qualified systems only |

## Material-specific rules

### Rigid fiber-filled filaments

- Use an abrasion-resistant nozzle.
- Prefer 0.6 mm or larger unless the supplier explicitly supports 0.4 mm.
- Do not assume a carbon-filled version is tougher; fibers commonly increase stiffness and dimensional stability while reducing ductility in some loading directions.
- Avoid using short-fiber composites for a highly deflected snap arm without testing.

### Nylon and other hygroscopic filaments

- Dry according to the exact supplier instructions.
- Print from a controlled dry path where practical.
- Record conditioning state with test results; absorbed moisture can change print quality and mechanical behavior.

### ABS/ASA/PC/high-performance polymers

- Use enclosure and ventilation appropriate to the printer/material.
- Avoid drafts and large abrupt cross-sections.
- Consider shrink/warp in fit allowances.
- Do not print beyond the machine's rated hotend, bed, chamber, and electrical capability.

### Flexible filaments

- Short, constrained filament path and low acceleration help.
- Reduce print speed and retraction.
- Use larger radii and avoid thin unsupported compression walls.
- Hardness labels such as Shore 95A do not fully define stiffness of the printed geometry.

### Food, skin, medical, flame, and electrical claims

A base polymer name does not certify a printed object. Pigments, additives, nozzle contamination, layer porosity, cleaning, post-processing, and local regulations matter. Require product-specific documentation and a qualified process.

## Temperature data

The YAML contains broad process ranges only for filtering. The slicer profile and supplier datasheet override them. Never use the upper printing temperature as a service-temperature rating.
