# Decision log

## 2026-09-05 — Product intake

- Registered existing research concept SKU-332 as product `MM-ORG-044` and portfolio record `PORT-114`.
- Selected a hybrid workflow: own text-to-image plate, owned geometry-only Step1X fork for the frog, then deterministic CAD for every book/page interface.
- Rejected the research value of 0.8 mm as a manufacturing requirement. Blade thickness and preload remain unqualified until coupon and cycle evidence exist for the pinned FDM process.
- Limited intended use to an adult, dry-indoor reading accessory. It is not a child toy and carries no archival-paper claim.
- Commercial release remains blocked by image-generator rights review, product-local provenance completion, physical qualification and human release approval.

## 2026-09-05 — Organic draft and blade coupons

- Accepted the own green frog image for organic draft generation only. Both image-generation attempts baked the checkerboard into RGB pixels; Step1X therefore performed its documented local U2Net background removal.
- Generated untextured Step1X run-001 with clean owned-fork commit `4b6da92`; the registered 44.3 mm draft is one watertight component and visually preserves the intended frog and rear interface stock.
- Did not infer approval of the new image. Concept approval remains pending under the manual autonomy ceiling.
- Generated separate 0.8, 1.0 and 1.2 mm CAD blade coupons instead of guessing a final product thickness. Every coupon mesh passes; the 0.8 mm candidate also passes an exact-profile local slice.
- Stopped before the final frog-to-blade join because no coupon has been printed and no paper sample or cycle result exists.

## 2026-09-05 — Mandatory whole-product concept image

- Added `concept/concept-product-v0.1.0-r1.png` as the Gate 0B asset. It shows the selected frog, the provisional CAD-style page blade and its intended placement on an open book.
- Kept the isolated frog image in `organic/reference/` classified only as the Step1X generation plate; it no longer stands in for the complete product concept.
- Recorded the own reference render, exact edit prompt, output hash, explicit upload authority and AI-concept disclosure. Blade thickness, preload, paper compatibility and fatigue remain unqualified.
- Kept concept approval pending because the current autonomy policy assigns that gate to a human and creation of the image is not approval of its depiction.
