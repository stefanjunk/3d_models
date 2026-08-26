# MVP risk register

| Risk | Probability | Impact | Current control | Trigger / owner action |
|---|---|---|---|---|
| No sellable products despite broad model library | High | Critical | three-SKU critical path and P5 definition | product owner reviews weekly; cut scope, never gates |
| Customer measurement error | High | High | fixed sizes first; measurement usability test | revise guide/tolerances after observed errors |
| Unknown source or design rights | High | Critical | external exclusion; per-input register; mark/design review | block revision at G1 |
| Demo catalog creates unsupported promises | High | High | release-manifest-only production catalog | remove/segregate demo data before staging approval |
| One-person workload delays parallel streams | High | High | role ownership and one-SKU beta option | re-plan when two critical tasks lack owners |
| Configuration generates unprintable/unsafe variants | Medium | Critical | configuration disabled; server validation later | do not enable until range/negative tests and immutable review pass |
| Digital product safety/liability misunderstood | Medium | Critical | per-SKU risk/technical package and legal review | recheck national law/insurance before launch and 2026-12-09 |
| Stripe/webhook/entitlement mismatch | Medium | High | idempotency, reconciler and negative E2E | alert and suspend checkout on unreconciled state |
| Download theft/fraud | Medium | Medium | signed URLs, exact entitlements, monitoring/takedown | investigate abnormal download patterns |
| Printed unit economics are negative | High until measured | High | printing disabled; controlled one-SKU pilot | require measured labor/yield/packaging before pricing |
| Product failure or unsafe claim | Medium | Critical | physical evidence, claim mapping, kill switch and incident runbook | stop affected revision and trace orders immediately |
| Legal/operator profile remains unverified or incomplete | Medium | Critical | core identity recorded; verification/contact/responsibility/signature gate remains | keep checkout/legal flag false until `GOV-001` and `LEG-001` pass |
| CI/security regression reaches main | Medium | High | required CI/branch protection and separated environments | block merge/deploy on failed checks |
| Accessibility or legal flow excludes users | Medium | High | critical-flow accessibility and withdrawal testing | block launch until defects close or counsel-approved scope |
| Broad metriCreate vision overwhelms one-person rights/safety/support capacity | High | Critical | no automatic publication; per-category and per-release gates; 70% initial-core capacity rule | limit active categories and block any SKU without an owner/evidence path |
| metriMade loses premium coherence by mirroring the full maker catalog | Medium | High | explicit consumer-eligibility flag, separate content/media criteria and curated subset rule | remove ineligible product from metriMade without deleting the metriCreate release |
| Cross-brand product records or configurations diverge | Medium | High | single product/revision source of truth and preserved handoff context | block publication/checkout when SKU, revision, price or configuration mapping mismatches |

Review P0/P1 risks weekly until launch, after every material incident, and before enabling a new delivery mode or country.
