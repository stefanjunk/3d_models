---
description: Route and validate a parametric freeform surfacing task
---

Load the `parametric-freeform-surfacing` skill and treat `$ARGUMENTS` as the project brief or project path. Preserve exact hardpoints, select the lowest-complexity viable surfacing method, produce editable source and manufacturing exports, then use the sibling `validate-printable-3d-projects` skill with `assets/validation-profile.json`. Report `PASS`, `FAIL`, `NOT_RUN`, and `REVIEW_REQUIRED` without collapsing them.
