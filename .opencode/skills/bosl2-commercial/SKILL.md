---
name: bosl2-commercial
description: Use when a commercial OpenSCAD design needs pinned BOSL2 attachments, shapes, fastener geometry, hinges, joiners, gears, or other reusable parametric helpers.
---

# BOSL2 Commercial Integration

Use only the tag/commit pinned in `libraries/third-party-lock.json` and the
ignored `.deps/openscad/BOSL2` checkout. BOSL2 is BSD-2-Clause; record the exact
version and retain the required copyright/license notice when distributing
derived source that includes BOSL2 code.

This checkout may omit the optional `libraries/` infrastructure. If the lock,
bootstrap script, or smoke script is absent, return `BLOCKED` with the missing
path. Do not fetch an unpinned replacement.

## Setup

```bash
python3 libraries/scripts/bootstrap_third_party.py
python3 libraries/scripts/smoke_third_party.py
```

Run OpenSCAD with:

```bash
OPENSCADPATH=.deps/openscad openscad -o exports/model.stl model.scad
```

## Rules

- Prefer attachments and named anchors over duplicated transforms.
- Record BOSL2 version/commit in provenance.
- Do not confuse permissive BOSL2 code licensing with rights to any separately
  imported third-party model.
- Execute the `.scad`, reload the STL, and run normal mesh/FDM gates.
