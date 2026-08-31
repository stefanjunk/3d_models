# Products

Every directory one level below a family is a complete product boundary:

```text
products/<family>/<product-id-and-slug>/
```

The family directory is an index only. Products may share ideas, but they may
not require source, profiles, assets, or generated files stored at family level
or in a sibling product.

## Families

| Family | Scope |
|---|---|
| `organization-storage` | organizers, bathroom storage, shelves, and wall storage |
| `printer-workshop` | printer accessories, workshop tools, and maker equipment |
| `home-kitchen-garden` | household, kitchen, decorative vessels, and garden products |
| `toys-games` | toys, boats, puzzles, fidgets, and tabletop products |
| `art-decor` | decorative meshes, sculpture, display objects, and art |
| `wearables` | accessories and footwear |
| `furniture-systems` | one self-contained package for each system-furniture SKU |

Directories beginning with `unregistered-` are contained product concepts that
still need a stable portfolio SKU. They are not release claims.

## Product contract

A mature product normally contains the following roles, using only the folders
that apply:

```text
README.md
PURPOSE.md
preflight/preflight-input.yaml
preflight/preflight-result.json
preflight/preflight-report.md
design-spec.yaml
decision-log.md
bom.yaml
validation-project.json
source/
assets/
vendor/
profiles/
docs/
scripts/
exports/
previews/
validation/
tests/
build/
releases/
archive/
```

`PURPOSE.md` is mandatory at the product boundary and states the intended use,
scope limits, assessed revision, and evidence basis explicitly. `archive/`
contains older or explicitly legacy versions; only current work and documented
root-review exceptions remain outside it.

Existing products retain some legacy internal names so that the migration does
not merge or overwrite artifacts. New work should follow the template in
[`../templates/product/`](../templates/product/).

At the next functional design phase, an existing product without
`preflight/preflight-result.json` receives a source-linked retrospective
preflight before geometry or manufacturing artifacts are changed.
