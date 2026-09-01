# Mandatory 3D design preflight integration

Use the sibling `3d-design-preflight` skill before every new functional design
and at the start of every later phase that can change the product. The
preflight is an engineering gate, not a confidence decoration.

## New product intake gate

First decide whether the request creates a separately offered, versioned,
supported, and retired product or only a component/variant of an existing SKU.
For a new product, read the sibling preflight skill's
`references/product-intake.md` and complete its identity, folder, portfolio,
and rights intake before any design-generating action. For an existing product,
work inside its folder and reuse its SKU and license chain.

The intake-only creation of a SKU, product folder, portfolio row,
`commercial-clearance/` scaffold, and preflight/design records is permitted
before the preflight. Concept images, image-to-3D jobs, CAD, meshes, GLBs, and
manufacturing exports are not.

## Project artifacts

Keep these paths inside the owning product:

```text
PURPOSE.md
commercial-clearance/
preflight/
  preflight-input.yaml
  preflight-result.json
  preflight-report.md
design-spec.yaml
```

`preflight/preflight-result.json` is the canonical current assessment. It must
validate against the sibling skill's
`schemas/preflight-result.schema.json`. Git history and
`traceability.previous_assessment_id` preserve its earlier revisions. Record
the current pointer and lifecycle state in `workflow.preflight` in
`design-spec.yaml`.

Use these lifecycle states:

- `pending`: no valid completed assessment exists yet;
- `current`: the artifact validates and covers the current recorded scope;
- `stale`: a relevant input changed after the assessment.

`current` says that the assessment is up to date. It does not override its
decision: `HOLD`, `CONCEPT_ONLY`, Lane D/E controls, K3 expert involvement, and
K4 restrictions remain binding.

## New designs

1. If this is a new product, finish the sibling product-intake gate: one unique
   SKU, correct `products/<family>/<sku>-<slug>` folder, one canonical CSV row,
   generated XLSX row, and initialized license chain. Otherwise confirm the
   existing owning SKU.
2. Allocate only the minimum product/revision traceability records and create
   an explicit `PURPOSE.md`.
3. Copy or populate `preflight/preflight-input.yaml` from the sibling skill.
4. Invoke `3d-design-preflight`, preserving every unknown and linking the
   portfolio row plus rights records in `traceability.basis_refs`.
5. Write and validate `preflight/preflight-result.json` with
   `traceability.mode: PROSPECTIVE` and `initial_design` in
   `change_triggers`.
6. Set `workflow.preflight.status: current`, link the assessment identity and
   revision, then run:

   ```bash
   python .agents/skills/functional-3d-design/scripts/validate_design_spec.py \
     path/to/product/design-spec.yaml --require-current-preflight
   ```

7. Follow the selected lane and decision before entering requirements approval,
   concept generation, production CAD, or manufacturing export.

The initial preflight can legitimately end in `HOLD` or `CONCEPT_ONLY` because
important requirements are still unknown. Resolve the minimum next evidence,
update the assessment, and proceed only under the new decision.

## Existing designs without a preflight

Do not pretend that an assessment happened before the existing geometry. Before
the next design-producing action:

1. inventory the current requirements, decision log, CAD/mesh revision,
   measurements, purchased-part data, process profiles, validation reports, and
   physical results;
2. assess only the current evidence and mark unavailable facts `UNKNOWN`;
3. create the canonical result with `traceability.mode: RETROSPECTIVE`,
   `backfill_missing_preflight` in `change_triggers`, and the inventoried files
   in `basis_refs`;
4. link it from `design-spec.yaml`, validate it, and obey any new hold or
   restricted lane before changing the model.

The backfill does not retroactively validate earlier decisions. Record any
conflict between the preflight and the existing model as an open decision or
verification action.

## When to mark the preflight stale

Mark `workflow.preflight.status: stale` as soon as any of these changes could
alter complexity, readiness, criticality, interfaces, hard gates, lane, or
confidence:

- intended use, exclusions, user context, host/product variant, or lifecycle;
- requirements, acceptance criteria, entities, purchased parts, interfaces,
  dimensions, tolerances, keep-outs, assembly, or service access;
- loads, temperatures, media, environment, failure consequences, or risk;
- source evidence, scans, measurements, supplier revisions, coupons,
  prototypes, test results, or verification plans;
- printer, material, nozzle, orientation, process profile, or other
  manufacturing constraints.

Style-only wording or presentation edits that cannot affect those fields do not
make the assessment stale. If uncertain, mark it stale and perform a focused
reassessment.

An update must state its real `change_triggers`, advance the assessment identity
or version, retain `previous_assessment_id`, refresh `basis_refs`, and update the
`workflow.preflight` pointer fields. Re-run the validator before continuing.

## Gate propagation

- A preflight update that changes scope, requirements, interfaces, risk, or
  manufacturing constraints also reopens the corresponding requirements,
  concept, engineering, and release gates.
- A failed hard gate may be resolved by evidence collection or a controlled
  scope change; never by changing a score without new evidence.
- Final release validation requires a current, schema-valid preflight for the
  current project revision in addition to the existing requirements, concept,
  optimization, watermark, and manufacturing gates.
