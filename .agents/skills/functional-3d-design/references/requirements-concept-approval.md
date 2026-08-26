# Requirements, concept, and final release approval gates

Use these gates at the start of a new design and when a revision changes function, geometry, interfaces, risk, manufacturing, or appearance. Treat `design-spec.yaml` as the single source of truth; the chat review is a readable projection of it, not a separate requirements document.

## Gate 0A — structured requirements review

Create or update the specification before proposing geometry. Present the understood design in compact tables covering, as applicable:

| Section | Minimum content |
|---|---|
| Goal and scope | user-visible function, included/excluded features, intended user |
| Geometry | envelope, critical dimensions, coordinate/orientation convention |
| Interfaces | mounting, mating parts, clearances, modular connections, assembly |
| Duty | loads, speed, cycles, service life, maintenance |
| Environment | temperature, moisture, UV, chemicals, indoor/outdoor use |
| Manufacturing | printer/build volume, material, nozzle, supports, fabrication preference |
| Appearance | form language, texture, color, visible hardware, ergonomic constraints |
| Risk and evidence | risk class, hazards, assumptions, tests, measurable acceptance criteria |
| Deliverables | editable source, STEP, 3MF/STL, drawings, renders, reports |

Label every nontrivial item as `user-stated`, `inferred`, `recommended`, or `unresolved`. For each unresolved decision that can materially change the design:

- ask a focused question;
- give a recommended answer and why it fits;
- state the main trade-off and the default that will be written to the specification if accepted.

Ask no more than three questions at once. Resolve high-impact geometry, interface, safety, and printer constraints before low-impact styling choices. End with a direct request to approve the specification revision or provide corrections.

Do not generate images, CAD, code, or exports while `workflow.requirements_approval.status` is not `approved`.

## Gate 0B — concept image review

After explicit requirements approval:

1. Store the approved `project.revision` in `workflow.requirements_approval.spec_revision`.
2. Create one coherent concept sheet from that exact revision. Prefer an image-generation tool for appearance-led products and a quick CAD blockout/render or precise schematic for interface-led parts. The deliverable must still be an image.
3. Include a three-quarter overview plus the additional view, cutaway, or exploded detail needed to judge mounting, modular connections, compartments, mechanisms, or assembly. Use reference images when the user supplied them.
4. Keep exact dimensions, tolerances, and safety claims out of AI-generated labels. State them beside the image from `design-spec.yaml`.
5. Provide a short correspondence list linking each important visible feature to the approved requirement and disclose any visual ambiguity or deliberate simplification.
6. Ask the user to approve the concept or request changes.

A concept image communicates design intent; it is not dimensional evidence, a strength result, or proof of printability. Do not create production CAD, source code, or manufacturing exports while `workflow.concept_approval.status` is not `approved`.

## State transitions

Use these states:

- requirements: `pending` -> `approved` or `changes-requested`;
- concept: `blocked` while requirements are unapproved, then `pending` -> `approved` or `changes-requested`.

When the user changes an approved requirement, increment the specification revision, set requirements to `changes-requested`, set concept to `blocked`, and clear the prior concept asset reference. When only the depiction is wrong and the specification remains valid, keep requirements approved and set only concept to `changes-requested`.

After concept approval, record the approving user, specification revision, concept asset, and timestamp when available. Continue with architecture and production geometry only when both approvals are for the current specification revision.

## Gate 0C — final model and release review

After concept approval and once production geometry is stable:

1. Lock the model candidate and assemble its primary evidence: overall views, key dimensions and interfaces, functional result, validation status, print orientation/profile, known limitations, and candidate deliverables.
2. Read `references/watermark-release-gate.md`, copy the canonical workspace `metrimade-watermark/` package into the project, and generate the exact `MM-WM-001-R1` profile from the immutable `project.id` and `project.revision`. Never redraw the mark or type/edit its domain, product ID, or version independently.
3. Find the largest safe region on the print-bed-facing underside, excluding edges, holes, mating/sliding/sealing faces, flexures, snap roots, high-stress zones, and thin walls.
4. Run `scripts/select_watermark.py` with the generated metadata JSON, safe-region size, host-wall thickness, nozzle, and layer height. Use its fit, rotation, clearance, and depth result. Never scale the generated profile down; if it does not fit, choose another safe region or revise the product geometry.
5. Subtract the cutter into the actual production body as the last planned design-feature/solid-geometry change. A derived final-export tessellation/simplification may follow only under the already validated policy, with the mark and protected geometry locked. Rerun geometry, surface-error, wall, bed-contact, mark-readability, and slicer checks on the resulting export.
6. Present the approval candidate in this order: actual model result and functions; critical geometry/interfaces; validation and print readiness; candidate deliverables; open risks; compact marking evidence. Keep the underside view, dimensioned close-up, section, and relevant slicer layers available, but do not let them replace the overall model presentation.
7. Ask for explicit approval of the complete model release. Do not publish, package, or describe exports as final before approval.

When the watermark passes, summarize it in one compact bullet or at most two short lines in the approval and final reports. Expand its treatment only if it blocks the release or the user specifically requests watermark detail. After approval and packaging, end with the model-centered report in `references/final-model-result-report.md`, not with a standalone watermark status.

Use watermark states `blocked`, `pending`, `approved`, and `changes-requested`. Record the specification revision, immutable production-geometry revision/hash, watermark asset ID, exact product ID/version, generated profile metadata and manifest, placement, preview, digital and physical validation evidence, approving user, and timestamp.

Any later change to geometry, part orientation, nozzle, line width, layer height, watermark transform, or marked-part coverage invalidates this gate. A watermark-only correction repeats Gate 0C. A functional or appearance requirement change also reopens the earlier applicable gates.
