# Decision log

## 2026-08-28 — select measured-envelope architecture

Current paid and downloadable products validate the storage job but mostly target fixed branded families or one modular ecosystem. Selected a brand-neutral analytic generator with explicit measurement and clearance inputs.

## 2026-08-28 — separate envelope size from tape metadata

The rack is sized by maximum physical depth/thickness/height. Tape width, color and inventory state belong on the front label field and cannot safely drive cavity dimensions.

## 2026-08-28 — correct connector datum coupling

The first digital draft placed connector centers at 28% and 72% of each rack depth. Compact and extended racks therefore produced different Y centers and could not mate. Replaced them with common absolute Y=25/55 mm datums, added a cross-preset regression and regenerated STEP/STL/3MF evidence. See `reports/connector-datum-iteration.json`.

## 2026-08-28 — stop at digital print candidate

Exact-profile slicing is complete. Physical cartridge fit, connector fit, retrieval durability, label adhesion and stability are explicitly deferred by user request. No G-code was retained or sent to a printer.
