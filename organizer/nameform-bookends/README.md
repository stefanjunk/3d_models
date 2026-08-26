# NameForm Bookends v0.3.0

Status: digitally validated DRAFT candidate. The geometry, marked STEP/STL/3MF
pair, text sweep, and validation evidence exist. Exact slicer review, watermark
coupon, complete-pair tests, and final release approval remain open.

The design is a true left/right pair. Each foot points inward under the books;
each decorative wing points outward. Text is never mirrored, and the fixed
160 mm book stop does not shrink when a longer name is used.

## Personalization modes

Preview the automatic width-balanced split without building CAD:

```bash
python3 organizer/nameform-bookends/scripts/customize_v030.py \
  --name STEFAN --plan-only
```

This produces `STE | FAN`. A longer name is split at the character boundary
that minimizes the wider rendered half; both halves then share one font size
and baseline.

Build a marked DRAFT pair with STEP, STL, separate left/right 3MFs, an assembly
STEP, and a hash report:

```bash
python3 organizer/nameform-bookends/scripts/customize_v030.py \
  --name ALEXANDER \
  --out-dir organizer/nameform-bookends/exports/v0.3.0/custom/alexander
```

Choose the two sides explicitly for initials, words, or a manual split:

```bash
python3 organizer/nameform-bookends/scripts/customize_v030.py \
  --left-text BÜ --right-text Qß \
  --out-dir organizer/nameform-bookends/exports/v0.3.0/custom/bue-qss
```

Put the whole name on both sides:

```bash
python3 organizer/nameform-bookends/scripts/customize_v030.py \
  --name STEFAN --same-on-both \
  --out-dir organizer/nameform-bookends/exports/v0.3.0/custom/stefan-both
```

Supported input is NFC-normalized `A-Z`, `a-z`, digits, spaces, hyphen,
apostrophe, and German `ÄÖÜäöüẞß`. Missing or unsupported glyphs fail closed.
A one-character name is repeated on both sides. Text that would fall below the
18 mm outline-height guard is rejected.

## Manufacturing boundary

The generated 3MFs are standards-valid geometry packages, not slicer-native
production jobs. Print left and right separately on their designed `z=0`
datum. Before use or release, complete the exact-slicer preflight in
`print-profile-v0.3.0.json` and all tests in `test-plan.yaml`. No script in this
project uploads to or starts a printer.
