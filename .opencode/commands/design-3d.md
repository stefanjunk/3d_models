---
description: Start or revise a gated functional 3D-print design
agent: functional-3d-designer
subtask: false
---

Load the `functional-3d-design` skill with the native skill tool before acting.

Treat the following as the user's design request:

$ARGUMENTS

For a new design or a material revision, create or update `design-spec.yaml`, present the structured requirements review, and stop for explicit approval. Do not create a concept image, CAD, source code, or manufacturing export before that approval. After requirements approval, create the required concept image and stop again for explicit concept approval. Continue into production CAD only after both approvals are valid for the current specification revision.

If no design request was supplied, ask for the intended function, approximate size, printer, and desired deliverables. Preserve the user's language in all responses.
