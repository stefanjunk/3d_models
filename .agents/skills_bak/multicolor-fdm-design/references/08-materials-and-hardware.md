# Materials and hardware

## Same-family default

For single-nozzle multicolor, use filaments from the same polymer family by default. Similar melt temperatures, cooling, shrinkage, and layer adhesion reduce risk. PLA+ variants still need a coupon if their recommended temperatures or flow behavior differ substantially.

Mixing PLA/PETG can be useful as a deliberately non-bonding support-interface strategy on some multi-tool systems, but it is not the default for a permanent single-nozzle multicolor body.

## Temperature compatibility

The final profile must satisfy every loaded filament. Review:

- overlapping nozzle-temperature window;
- bed-temperature compatibility;
- cooling requirements;
- maximum volumetric speed of the slowest filament;
- drying requirements;
- purge needed after a high-temperature or highly pigmented filament.

A single-nozzle job cannot simultaneously use independent nozzle temperatures at the same instant. Frequent large temperature changes add time and can degrade material.

## Opacity and pigment

Color matching depends strongly on opacity and pigment load. Record:

- opaque, translucent, transparent, metallic, silk, matte, filled;
- recommended backing color and minimum shell depth;
- abrasive filler/hardened-nozzle requirement;
- whether purge contamination is visually severe.

## Material changer compatibility

Hardware compatibility is printer- and feeder-specific. Flexible, abrasive, brittle, oversized, cardboard-spool, or unusual-diameter materials may require direct feed or adapters. Keep these constraints in the printer profile, not as universal skill claims. Verify current manufacturer documentation for ACE/AMS/MMU-class hardware before a job.

## Drying

Multicolor jobs can keep four filaments loaded for many hours. Moisture causes oozing, stringing, blobs, and inconsistent purge. Dry hygroscopic materials and store them sealed. A color-change system with active drying helps only within its documented temperature and material limits.

## Calibration hierarchy

For every materially different color/brand:

1. dry the filament;
2. temperature and flow ratio;
3. pressure advance/dynamic flow behavior where applicable;
4. maximum volumetric speed;
5. purge transition coupon;
6. opacity/thickness swatch.

The combined job should use a safe common profile or per-filament settings supported by the destination slicer/printer.
