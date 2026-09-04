# Anycubic Kobra 3 Max — wiper mount interface geometry

- **Authority:** user-measured on the physical machine, 2026-08-29.
- **Scope:** one Anycubic Kobra 3 Max unit (`unit_id` not recorded). Host-object
  geometry only. This is *not* process-calibration data; it says nothing about
  clearances, shrinkage, or dimensional compensation.
- **Source trace:**
  `products/printer-workshop/unregistered-kobra3max-purge-catcher/WIPER-PHOTO-MEASUREMENTS-R7.yaml`
  (`ANYCUBIC-K3MAX-PURGE-CATCHER-R7`, requirement revision 0.7.0-requirements.2).
- **Review date:** re-verify before any production CAD release that depends on
  these datums.

## Measured values

| ID | Quantity | Value | From → to |
|---|---|---:|---|
| M-R7-001 | vertical screw centre pitch | 17 mm | lower screw centre → upper screw centre |
| M-R7-002 | lower screw centre → purge deposition plane | 10 mm | `D-WIPER-LOWER-SCREW` → `D-PURGE-DEPOSIT` |
| M-R7-003 | screw datum → horizontal purge throw plane | 37 mm | screw datum → `D-PURGE-THROW` |
| M-R7-004 | screw seating plane → rear wiper extent | 40 mm | `D-WIPER-SCREW-PLANE` → `D-WIPER-REAR` |

## Stated uncertainty — read before use

The instrument was a folding rule with 1 mm graduation, read directly by the
user and supported by six scale-in-frame photographs. **Resolution is 1 mm and
the trace explicitly declines to claim a smaller uncertainty**: there was no
repeated measurement series, no square gauge, and the end datums are not
visible in every photograph.

Every value is recorded in the source trace as usable for *requirements,
concept placement, or concept envelope only*. A printed hole-pattern/datum
coupon is required before production CAD depends on any of them. Do not treat
these numbers as a toleranced interface contract.

## Conflicts

None recorded. No second measurement series exists to compare against, which is
itself the reason the values stay at concept authority.
