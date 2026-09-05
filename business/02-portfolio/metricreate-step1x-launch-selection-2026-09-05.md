# metriCreate Step1X launch selection — 2026-09-05

## Decision

The first three appearance-led Step1X products for metriCreate are, in this
order:

1. `MM-ORG-041` — Octopus cable wrap organizer (`PORT-110`, research `SKU-331`)
2. `MM-ORG-044` — Tree Frog bookmark reading clip (`PORT-114`, research `SKU-332`)
3. `MM-DEC-004` — Sleepy Cat nursery-pot sleeve (`PORT-115`, research `SKU-327`)

This is a launch queue, not storefront approval. All three remain blocked from
publication until their product-local physical and commercial gates pass.

## Meaning of “Step1X-dependent”

No physical product is mathematically possible with only one modelling tool.
For this selection, Step1X-dependent means that the product's differentiating,
appearance-led organic body is intentionally generated from an own reference
image and is not available as controlled parametric CAD or an imported
third-party model. Deterministic CAD still owns every functional interface:

- Octopus: cable channels and flat desk interface
- Frog: page blade, mating pad and page-contacting edges
- Cat: pot cavity, flat seat and drain/vent path

The selected products therefore exercise the owned geometry-only Step1X route
for a real product advantage while keeping fit, retention and safety-relevant
features measurable and editable.

## Portfolio screen

The research portfolio contains 45 rows whose declared generative route names
Step1X. The shortlist used the portfolio's directional scores, then preferred
K1 products with a useful CAD-owned function, low likeness/trademark exposure,
one-part or simple hybrid construction, and a short path to physical evidence.

| Rank | Candidate | Trend / opportunity | Why selected |
|---:|---|---:|---|
| 1 | Octopus cable wrap organizer | 90 / 77.9 | Highest directional score, existing product identity, distinctive organic body, and a simple measurable channel interface. |
| 2 | Tree Frog bookmark reading clip | 87 / 75.9 | Joint-highest remaining score, compact coupon-led qualification, and a clear split between organic ornament and CAD blade. |
| 3 | Sleepy Cat nursery-pot sleeve | 84 / 74.0 | Adds home-decor category breadth and has a simpler fixed cavity interface than articulated alternatives. Scope was narrowed from direct planter to removable-pot sleeve. |

The `SKU-322` articulated whale-shark key pouch also scores 87 / 75.9, but was
not selected for the first wave: its print-in-place joints, articulation-cycle
test and pouch function make its first-pass qualification materially longer and
less predictable. Similar articulated creatures and character-led figurines
were deferred for the same reason or for greater likeness/IP exposure.

## Licence decision after the owned-fork cleanup

The active product runs record owned-fork commit
`4b6da92a56acb3a135b0493703470995c00c5e91`. The executed geometry decoder was
independently replaced at commit `f00dd46`, and the texture stage was deleted at
commit `2433849`. Consequently, new untextured geometry runs at or after the
decoder cutoff are no longer blocked by the removed Hunyuan-derived geometry
code or texture pipeline.

The gate is `WARN`, not `PASS`. Per-SKU image-generator rights, upstream training
provenance, the undeclared licence of the downloaded CLIP configuration,
customer-facing AI disclosure, outgoing model licence, market review and human
release approval remain open. Pre-cutoff geometry and every textured Step1X
artifact remain blocked and must not be relabelled as cleared.

## Current product evidence and next gate

| Product | Current evidence | Binding next gate |
|---|---|---|
| Octopus | v0.2.0 watertight 100k-face digital candidate; exact Anycubic slice passes at 305 layers and 5 h 54 min 54 s | Measure real cables; print and test retention, jacket cycling, edges and loaded stability |
| Frog | Watertight registered organic draft; 0.8/1.0/1.2 mm CAD blade coupons; 0.8 mm exact-profile slice passes | Human concept approval; print coupon series; paper-marking and 100-cycle tests; then join final blade |
| Cat | Watertight run-004 cavity/drain digital draft; exact Anycubic slice passes at 345 layers and 6 h 30 min 24 s | Human concept approval; measure the exact nursery pot; update cavity; test fit, water path and loaded stability |

Storefront order should remain Octopus → Frog → Cat. A product advances to
metriCreate only when its own gate closes; a delay in one SKU must not be hidden
by treating a digital draft as a released model.
