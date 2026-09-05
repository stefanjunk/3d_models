# Decision log — MM-ART-012

## 2026-09-05 — product intake

- Accepted the existing main-only reservation `PORT-116 / MM-ART-012` as the
  product identity; no portfolio file was edited from the product branch.
- Distinguished this product from `MM-ORG-041`: MM-ART-012 is a purely
  decorative comic figurine and has no cable-retention function.
- Recorded the owner-required order: requirements -> concept image -> explicit
  human concept review -> Step1X-3D.
- Proposed a one-piece, eight-tentacle, stable desk character and a pinned
  Anycubic Kobra 3 Max / SUNLU PETG Black baseline solely as reviewable defaults.
- Kept seller identity, markets, outgoing licence and commercial approval
  explicitly `UNKNOWN/BLOCK`.

## 2026-09-05 — requirements revision 0.1.0 approved

- The project owner responded `freigegeben` to the structured requirements review.
- Gate 0A now permits creation of the mandatory whole-product concept image.
- The approval does not authorize Step1X-3D; Gate 0B remains pending human review.

## 2026-09-05 — concept generation blocked by shared intake audit

- `PORT-116` exists in both the canonical CSV and generated XLSX on `origin/main`.
- The product preflight and linked design specification validate.
- The mandatory global backfill dry-run proposes 183 changes across unrelated
  product paths, and the aggregate portfolio validator is not idempotent.
- Product-intake rules therefore require a fail-closed stop. No imagegen or
  Step1X call was made.
