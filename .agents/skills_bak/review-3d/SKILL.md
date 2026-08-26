---
name: review-3d
description: Independently review a functional 3D design against its approved specification without modifying project files. Use for design audits, readiness reviews, evidence checks, risk assessment, and requirement traceability.
---

# Review 3D

Load `functional-3d-design`. Review the current project and any extra scope in the user's request without modifying files.

Use `design-spec.yaml` as the source of truth. Check approval-state consistency, requirement-to-feature traceability, dimensions and interfaces, geometry evidence, printability, material and profile assumptions, risk, acceptance tests, and whether claims exceed recorded evidence.

Run only safe read-oriented checks. Return findings ordered by severity with file references, evidence, impact, and a concrete next action. State explicitly when a check could not be performed.
