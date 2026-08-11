# Print, buy, or integrate?

## User preference is a real design parameter

The same product can be optimized for:

- maximum printed integration;
- a balanced hybrid;
- maximum use of standard hardware.

Record the chosen mode before selecting mechanisms.

Run:

```bash
python scripts/print_vs_buy.py --component bearing --mode balanced-hybrid --load medium --precision high
```

## Decision factors

Favor printing when the component benefits from:

- custom geometry or one-off dimensions;
- part consolidation and integrated routing/features;
- low production volume;
- low speed and modest load;
- large geometry relative to nozzle resolution;
- easy replacement and local reprinting;
- material compliance such as TPU grips or custom seals at low pressure.

Favor purchasing when the component depends on:

- tight precision and low runout;
- rolling/sliding fatigue and known wear behavior;
- high speed, stored energy, or repeated cycling;
- certified load, fire, electrical, food, or pressure performance;
- hardened surfaces, spring temper, elastomer formulation, or seal finish;
- commodity economics.

## Typical recommendations

| Component | Default | Printed alternative | Preferred hybrid |
|---|---|---|---|
| housing, bracket, duct, adapter | print | — | inserts/fasteners as needed |
| M3–M8 screw/bolt | buy | large low-load thread/knob | printed captive feature + metal screw |
| repeated internal thread | buy interface | printed coarse thread | heat-set insert or captive nut |
| hinge | hybrid | print-in-place/living hinge | printed leaves + metal pin |
| shaft/pivot pin | buy | large low-load plastic pin | steel pin in printed bosses |
| ball bearing | buy | low-speed bushing | bearing seats in printed body |
| bushing | print or buy | tribological filament | replaceable printed sleeve |
| coil/torsion spring | buy | flexure/compliant mechanism | metal spring in printed guides |
| slow large gear | print | yes | metal shaft/bearings |
| high-speed/small/high-load gear | buy | prototype only | purchased gear in printed housing |
| timing belt/chain | buy | demonstration only | printed pulleys/sprockets where justified |
| O-ring/dynamic seal | buy | custom TPU gasket for low pressure | O-ring groove in printed part |
| wall anchor | buy | do not substitute | printed keyhole/plate + certified anchor |
| magnet/electrical contact | buy | do not print as conductor substitute | captured purchased component |

## Part consolidation checklist

Before merging parts, ask:

- Does consolidation eliminate fasteners or alignment steps?
- Can every surface still print and be inspected?
- Can support be removed?
- Can the product be serviced or recycled?
- Does one local failure now discard a large expensive print?
- Are different materials needed for wear, flexibility, temperature, or grip?
- Does the integrated part force a weaker print orientation?
- Can a captive standard part be inserted without pausing in an unsafe way?

## Replacement patterns enabled by printing

| Traditional assembly | Printable replacement | Use when |
|---|---|---|
| bracket + spacers + cable clips | one integrated frame | geometry is stable and service access remains |
| metal spring + latch | printed compliant latch | low/moderate cycle count with tested strain |
| hinge leaves + pin + screws | integrated knuckles + metal pin | print orientation supports knuckles |
| custom machined manifold | printed internal channels | cleaning, leakage, temperature, and support are addressed |
| multiple shims | parametric spacer stack | dimensions can be measured and revised |
| separate soft foot | multi-material or press-fit TPU pad | bonding and replacement are considered |

## Safety default

For safety-critical load paths, default to purchased, rated hardware and use the print as a housing, guide, spacer, or noncritical interface until a qualified engineering process says otherwise.
