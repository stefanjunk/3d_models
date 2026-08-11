# Self-learning and extension workflow

## Goal

Convert repeated local measurements into versioned, reviewable knowledge without pretending that one successful print is universal truth.

## What to record

For every meaningful test:

- project and part revision;
- printer, firmware, slicer, profile hash;
- nozzle diameter/material and wear state;
- filament manufacturer, product, color/batch if known, drying/conditioning;
- orientation, layer height, line width, walls, infill, cooling, speed/volumetric cap;
- measured dimensions and test method;
- load, cycles, temperature, humidity/UV/chemical exposure;
- pass/fail and failure mode;
- photos, raw data, or report path.

## Status model

- `concept`: source or idea only.
- `experimental`: generated/printed with incomplete evidence.
- `qualified-local`: passed a named acceptance plan on a recorded local process.
- `deprecated`: failed, unsafe, or superseded.

`qualified-local` is intentionally narrower than "validated" or "certified".

## Workflow

1. Initialize/search the library:

```bash
python scripts/parts_library.py init
python scripts/parts_library.py search drawer
```

2. Add a new part entry from a JSON file:

```bash
python scripts/parts_library.py add --entry templates/part-entry.json
```

3. Record a test:

```bash
python scripts/record_test_result.py --part-id my-part --result tests/result.json
```

4. Promote only after linked evidence:

```bash
python scripts/parts_library.py promote --part-id my-part --status qualified-local
```

The promotion command refuses qualification without validation and test evidence.

## Learning rules

- Store observations separately from universal rules.
- Add confidence and sample count.
- Preserve failures; they prevent repetition.
- Prefer measured correction by printer/material/nozzle profile over a global magic tolerance.
- Review and merge duplicated parts by interface compatibility, not name similarity.
- Keep source provenance and license for external geometry.
- Version parameter schemas; a breaking interface change requires a new major revision.

## Extending the skill

When a repeated failure or decision appears:

1. add a test case reproducing it;
2. add or update a rule in `data/`;
3. update the matching reference;
4. run the package tests and example builds;
5. add a changelog entry;
6. keep the rule scoped to evidence.

This follows a guideline → principle → executable rule pattern: narrative knowledge is distilled into a rule, then checked by scripts/tests.
