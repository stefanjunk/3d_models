# New product identity, portfolio, and rights intake

Use this gate only when the work creates a new product identity. A component,
variant, colorway, generated preform, or replacement part remains under the
owning SKU when it is versioned, released, supported, and retired with that
product. Allocate another SKU only when the item will be managed or offered as
an independent product. Resolve a materially ambiguous boundary with the
product owner before creating parallel records.

## Identity invariant

Use one stable SKU everywhere:

- `business/02-portfolio/product-portfolio.csv` → `Working_SKU`;
- `products/<family>/<lowercase-sku>-<slug>` → folder prefix;
- `design-spec.yaml` → `project.id` and `project.sku`;
- `preflight/preflight-result.json` → `traceability.project_id`;
- rights, generated-asset, release, catalog, order, support, and retirement
  records together with the applicable revision.

Use the established `MM-<category>-<number>` family. Inspect both the
portfolio source and live product folders before reserving the next unused
value; never infer uniqueness from one file alone. Do not use `SKU-###`
research IDs as commercial product SKUs. Do not create a new
`unregistered-*` folder.

Choose the existing `products/<family>/` directory that matches the product's
commercial purpose. Create a new family only when no current family is
truthful. The product directory must be exactly one level below that family;
do not place it in `research/`, `external/`, `archive/`, a shared `exports/`
directory, or another product's root.

## Canonical portfolio record

`business/02-portfolio/product-portfolio.csv` is the version-controlled source;
`business/02-portfolio/product-portfolio.xlsx` is generated. Never edit the
XLSX by hand.

Before producing a concept image, CAD, mesh, GLB, or manufacturing export:

1. reserve one unique `Record_ID` and `Working_SKU`;
2. create `products/<family>/<lowercase-sku>-<slug>`;
3. add exactly one CSV row whose `Source_Path` is that repo-relative folder;
4. populate every field from evidence, using explicit `UNKNOWN`, `No`, `Hold`,
   or an open gate instead of optimistic claims;
5. set `Rights_Provenance` to a concise, truthful summary and link the detailed
   product-local rights workspace in the design/preflight records.

The same SKU or source path appearing twice is a hard stop. A non-empty
`Rights_Provenance` cell records status; it does not prove clearance.

## Initialize the license chain

Load `commercialize-3d-models` and create its evidence workspace at
`<product>/commercial-clearance/`. Use the seller, markets, and digital,
physical, or combined release scope actually authorized for this product:

```bash
python .agents/skills/commercialize-3d-models/scripts/new_commercial_3d_project.py \
  --name "Product name" \
  --seller-country "DE" \
  --markets "DE" \
  --release-type digital \
  --release-id "MM-CAT-001-0.1.0" \
  --output products/<family>/<sku-slug>/commercial-clearance
```

The values above illustrate shape only; do not copy markets or release type
without scope evidence. Replace the initializer's `REPLACE` example rows.
Record each real source, tool/service/model, component, contributor, and
transformation as it enters the chain, with source/terms evidence, effective
version or revision, SHA-256 where a file exists, and separate permissions for
commercial use, modification, AI input, digital redistribution, and physical
sale. A category with no component yet may remain header-only; never retain a
fake component row.

For image-to-3D, the minimum chain is:

```text
brief/reference rights -> imagegen prompt + generated image -> preprocessing
-> Step1X code/weights/runtime + run record -> raw GLBs -> edited CAD/mesh
-> STL/3MF/STEP -> slicer/print or digital release
```

Preserve the exact imagegen and Step1X records required by their skills. Record
`UNKNOWN` or `BLOCK` when evidence is absent; never manufacture a license
conclusion. An open rights item may leave engineering preflight usable, but it
blocks the affected commercial gate and must appear in `Rights_Provenance`,
the rights workspace, and the preflight blocking evidence or next actions.

## Execute and link the preflight

Create these product-local records before design generation:

```text
PURPOSE.md
design-spec.yaml
preflight/preflight-input.yaml
preflight/preflight-result.json
preflight/preflight-report.md
commercial-clearance/
```

Use `PROSPECTIVE` mode and include `initial_design`,
`portfolio_registration`, and `license_chain_initialization` in the initial
change triggers. `traceability.basis_refs` must include the exact portfolio row
pointer and the applicable rights registers/evidence. Keep the SKU, revision,
portfolio pointer, source path, and rights-workspace pointer in
`design-spec.yaml`.

Validate the result and its design-spec link:

```bash
python .agents/skills/3d-design-preflight/scripts/validate_preflight.py \
  products/<family>/<sku-slug>/preflight/preflight-result.json \
  --project-id MM-CAT-001 --project-revision 0.1.0

python .agents/skills/functional-3d-design/scripts/validate_design_spec.py \
  products/<family>/<sku-slug>/design-spec.yaml --require-current-preflight
```

## Refresh the portfolio workbook

After the product-local records and CSV row are valid, refresh the aggregate
product audit, readiness source, and generated workbook in this order:

```bash
python tools/backfill_product_preflights.py
python tools/backfill_product_preflights.py --write
python business/tools/build_readiness_advancement_register.py
python business/tools/build_product_workbook.py
python tools/validate_product_preflight_portfolio.py
python business/tools/validate_portfolio_preflight_overlay.py
```

Inspect the dry-run `changed_paths` before using `--write`. Continue only when
it proposes the aggregate audit and the new product's intended intake files;
if it proposes another product's files, stop and preserve that concurrent or
incomplete work. Review the final diff because the aggregate commands cover
the entire portfolio.

The intake gate passes only when the XLSX contains one row with the exact SKU
and `Product_Path`, the current preflight validates, and the rights chain is
initialized without placeholder claims. Passing this gate is permission to
follow the preflight decision; it is not requirements, concept, engineering,
rights, safety, or commercial release approval.
