# 3D model workspace

This repository stores each product as one self-contained directory. A product
folder owns its source, inputs, profiles, manufacturing exports, validation
evidence, tests, and retained revision packages. Moving or copying that one
folder must not make the product depend on a sibling product.

## Repository layout

```text
products/       self-contained product folders grouped by family
templates/      starting point for a new product; never a runtime dependency
research/       market research, concepts, and excluded third-party downloads
business/       portfolio, release, commercial, and operating records
libraries/      standalone reference libraries; required subsets are vendored
tools/          repository checks and standalone generators
archive/        legacy suites and local tool state retained during migration
```

The authoritative product paths and lifecycle records are in
[`business/02-portfolio/product-portfolio.csv`](business/02-portfolio/product-portfolio.csv).
Run `python3 tools/validate_product_layout.py` after adding or moving a product.

## Containment rule

- Family directories classify products only. They contain no shared CAD,
  exports, profiles, assets, or build code.
- A dependency needed to rebuild a product is copied under that product's
  `vendor/` or `assets/third-party/` directory with its version and license.
- Product status and revision belong in metadata and artifact names, not in the
  permanent product-directory name.
- Generated dependency directories and caches are ignored. Manufacturing
  artifacts remain tracked when they are deliberate evidence or deliverables.

See [`products/README.md`](products/README.md) for the product contract and
[`templates/product/README.md`](templates/product/README.md) for the template.
