---
name: review-mesh-edit
description: Review an organic-to-functional mesh edit against its operation plan and evidence without modifying project files. Use for protected-surface, topology, section, fit, printability, and physical-test audits.
---

# Review Mesh Edit

Load `organic-mesh-functionalization`. Review the scope supplied by the user against `operation-plan.yaml`.

Run safe inspection and validation scripts where useful. Report, in order:

1. source interpretation, scale, and alignment blockers;
2. protected-region breaches or missing proof;
3. topology, Boolean, wall, section, and trapped-fragment concerns;
4. functional-part fit and assembly concerns;
5. printability and material/interface concerns;
6. missing physical tests;
7. a pass, conditional, or fail recommendation.

Distinguish automated evidence, visual assumptions, and physical evidence. Do not edit files.
