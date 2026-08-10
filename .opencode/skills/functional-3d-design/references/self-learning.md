# Evidence-backed local parts library

Store observations as versioned local evidence, never as universal FDM rules.

For each meaningful test record the part revision, printer, firmware, slicer,
profile hash, nozzle, exact material and batch where known, conditioning,
orientation, layer settings, loads, cycles, environment, measurements, result,
failure mode, and evidence paths.

Statuses are:

- `concept`: source or idea only;
- `experimental`: generated or printed with incomplete evidence;
- `qualified-local`: passed a named acceptance plan on a recorded local process;
- `deprecated`: failed, unsafe, superseded, or no longer supported.

Use:

```bash
python3 scripts/parts_library.py init
python3 scripts/parts_library.py add --entry templates/part-entry.json
python3 scripts/record_test_result.py --part-id my-part --result templates/test-result.json
python3 scripts/parts_library.py promote --part-id my-part --status qualified-local
```

Qualification requires linked geometry validation, physical test evidence, and
printer/material/nozzle/profile identity. Each qualifying record must reference
an existing project-contained report, include its SHA-256, match the part
revision and process identity, and use `evidence_type: geometry-validation` or
`evidence_type: physical-test`. Physical evidence also requires nonempty
measurements. Pass the project root with `--evidence-root`. Preserve failed
tests. Scope every correction to its measured process instead of creating a
global tolerance.
