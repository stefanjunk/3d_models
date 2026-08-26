---
name: design-3d
description: Start or materially revise a gated functional FDM/FFF design. Use for user requests that require structured requirements, concept approval, production CAD, and validated manufacturing outputs.
---

# Design 3D

Load `functional-3d-design` before acting and treat the user's invocation context as the design request.

For a new design or material revision:

1. Create or update `design-spec.yaml`.
2. Present the structured requirements review and stop for explicit approval.
3. After approval, create the required concept image and stop for explicit concept approval.
4. Create production CAD only after both approvals are valid for the current specification revision.

Do not create a concept image, CAD, source code, or manufacturing export before requirements approval. Invalidate concept approval when approved requirements change. Preserve the user's language.

If no actionable design request was supplied, ask for the intended function, approximate size, printer, and desired deliverables.
