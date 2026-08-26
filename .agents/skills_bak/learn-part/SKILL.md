---
name: learn-part
description: Record validated component or physical-test evidence for later local reuse in functional 3D designs. Use when adding or updating parts-library records, qualification evidence, provenance, licensing, or printer-specific test results.
---

# Learn Part

Load `functional-3d-design` and evaluate the component or test evidence in the user's request.

Use the skill's parts-library and test-record scripts and schemas. Record source, version, license or supplier identifier, printer/material/nozzle/profile identity, validation evidence, limitations, and status.

Never promote a component to `qualified-local` unless the required geometry checks and linked physical-test evidence exist. Return the record changed, status decision, supporting evidence, and unresolved limitations.
