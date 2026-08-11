---
description: Independently review a 3D design against its approved specification
agent: 3d-design-reviewer
subtask: true
---

Load the `functional-3d-design` skill with the native skill tool. Review the current project and any extra scope in `$ARGUMENTS` without modifying files.

Use `design-spec.yaml` as the source of truth. Check approval-state consistency, requirement-to-feature traceability, dimensions and interfaces, geometry evidence, printability, material/profile assumptions, risk, acceptance tests, and whether claims exceed the recorded evidence. Run only safe read-oriented checks. Return findings ordered by severity with file references, evidence, and a concrete next action. State explicitly when a check could not be performed.
