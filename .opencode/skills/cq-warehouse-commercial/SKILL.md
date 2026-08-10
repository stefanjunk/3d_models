---
name: cq-warehouse-commercial
description: Use when a commercial CadQuery assembly needs ISO fasteners, nuts, washers, bearings, inserts, clearance holes, tapped holes, press fits, or a pinned cq_warehouse dependency.
---

# cq_warehouse Commercial Integration

Use only the commit pinned in `libraries/third-party-lock.json` and the ignored
`.deps/python` cache. Load `commercial-cad-provenance` before adding the library
to a commercial project manifest.

This checkout may omit the optional `libraries/` infrastructure. If the lock,
bootstrap script, or smoke script is absent, return `BLOCKED` with the missing
path. Do not install an unpinned package or borrow another checkout.

## Setup

```bash
python3 libraries/scripts/bootstrap_third_party.py
python3 libraries/scripts/smoke_third_party.py
```

Run model scripts with:

```bash
PYTHONPATH=.deps/python python3 model.py
```

## Rules

- Select a real purchased fastener/bearing/insert and record its standard or
  manufacturer source.
- Use simplified thread representation for routine assembly unless actual
  printed/thread geometry is a requirement.
- Generate matching holes from the selected component; do not independently
  type nominal diameters in multiple files.
- Record library version/commit and Apache-2.0 notice in provenance.
- Validate fit, tool access, assembly order, and actual purchased hardware.

The passing compatibility smoke proves only that the pinned library generates a
valid sample solid under the current Python/CadQuery environment.
