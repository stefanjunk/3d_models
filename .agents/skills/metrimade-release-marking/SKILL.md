---
name: metrimade-release-marking
description: Generate, place, validate, and approve the owned metriMade.com product mark on printable products before commercial release. Use when a printable product or SKU reaches its release gate, when choosing a mark tier or safe surface region, when a mark must be re-approved after a geometry or version change, or when auditing marking coverage across a multipart assembly. Do not use it to design product geometry or to decide function.
license: MIT
metadata:
  version: "1.0.0"
  domain: "release marking and product identity"
  asset: "MM-WM-001-R2"
---

# metriMade release marking

Own the product mark as a release gate, not as a design goal. Geometry,
function, and manufacturing readiness are decided by `functional-3d-design`;
this skill decides only whether the release carries a correct, readable,
physically qualified mark.

Resolve every bundled path relative to this `SKILL.md`.

## Read only what the task needs

- Generating tiers, selecting a placement, integrating the cutter, or recording
  approval evidence: `references/watermark-release-gate.md`
- Nothing else in this skill needs a reference read.

## Where the mark comes from

The canonical generator is the versioned `MM-WM-001-R2` package. In this
workspace its source is the repository-level `tools/metrimade-watermark/`
directory; a packaged distribution carries the same pinned core inside the
package under a `metrimade-watermark` asset directory created at packaging
time. Use exactly one source and verify its revision. This skill deliberately
bundles no copy of the mark, so the identity has a single owner.

Generate every tier from the immutable release identity — `project.id` and
`project.revision`. Never redraw a mark, substitute live text, edit identity
text independently, or obtain a smaller tier by scaling a larger one.

## Non-negotiable rules

1. Selection order is Full, then Compact, then Micro, at 0° or 90° and scale
   1.0 only. Full and Compact retain the visible `metriMade.com` domain.
2. Micro may omit the visible domain only after the selector proves that
   neither larger tier fits the measured safe region. Retain the controlled
   domain in 3MF metadata or the provenance sidecar.
3. Mark every independently distributed product or SKU on at least one durable
   primary body. A release must never contain no mark.
4. Keep the mark out of holes, rails, seals, mating planes, threads,
   snap/flexure roots, high-stress zones, deliberate textures, and required
   bed-contact lands.
5. Insert the mark as the **last planned design-feature/solid-geometry change**.
   A prevalidated tessellation/simplification policy may run afterward only with
   the mark and protected geometry locked and all affected checks repeated.
6. A digital mark is not a qualified mark. A passed coupon for the selected tier
   on the intended production process is mandatory before release approval.
7. Do not overwrite or silently rebuild historical releases carrying a
   JuSt Innovation or `MM-WM-001-R1` mark. Introduce `MM-WM-001-R2` only
   through a new product revision.

## Gate procedure

1. **Confirm the model is release-ready.** The production geometry must be
   stable and verified first. Marking an unverified model wastes the coupon.
2. **Generate all tiers** from the exact product ID and version.
3. **Measure the safe region** in CAD and run the selector:

   ```bash
   python scripts/select_watermark.py \
     --metadata <generated-tier-dir-or-metadata-json> \
     --surface-width 80 --surface-height 45 \
     --host-wall 2.0 --nozzle 0.4 --layer-height 0.2
   ```

   `--metadata` accepts one metadata JSON, repeated arguments, or the directory
   the generator wrote its tiers into.

   Default edge clearance is the larger of 2.0 mm or two nozzle diameters.
   Require a host wall of at least 1.20 mm and a remaining wall of at least
   0.80 mm after engraving. Qualified depth is 0.40–0.80 mm; the generated
   default is 0.40 mm. Treat `BLOCK` as final for that candidate region.
4. **Integrate the generated geometry** by the route for the owning tool, then
   verify the actual exported underside directly. The STL cutter is mirrored in
   X so the finished underside reads normally; a top-view CAD screenshot is not
   evidence.
5. **Record the evidence** listed in the reference: asset revision, selected
   tier and priority, domain visibility, exact product ID/version, metadata and
   manifest hashes, envelope, rotation, position, surface, depth, clearances,
   local wall before/after, marked-part coverage, process identity, and
   production-geometry revision/hash.
6. **Request approval.** This gate is human-controlled. Never record
   `HUMAN_APPROVED` from an agent.

## Reporting rule

Report the mark as a compact secondary release note — one bullet, or at most
two short lines, under a **Kennzeichnung** heading — after the model result,
function, validation, and deliverables. Expand it only when it blocks release
or the user asks. Never make marking status the headline, opening result, or
dominant conclusion of a successful design handoff.

## Release blockers

A missing, unreadable, mirrored, protruding, structurally unsafe,
identity-mismatched, physically unqualified, or unapproved mark blocks release.
Never omit the owned logo, product ID, or version, and never scale a generated
tier or retype identity text.

## Companion routing

- `functional-3d-design` owns geometry, requirements, validation, and the
  `design-spec.yaml` workflow record, including the release-approval gate state.
- `commercialize-3d-models` owns AI-provenance disclosure and the commercial
  release decision, which is separate from this geometric mark.
- `validate-printable-3d-projects` executes the deterministic checks and holds
  `watermark-approval` as a declared manual gate.
