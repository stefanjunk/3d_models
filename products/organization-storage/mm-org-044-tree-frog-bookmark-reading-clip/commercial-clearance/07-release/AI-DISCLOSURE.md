# AI use and provenance — MM-ORG-044

Status: draft disclosure; not approved for customer use.

Proposed customer wording: “AI-assisted design. An original text prompt was used to create the frog reference image, and a locally hosted geometry-only Step1X-3D fork generated the organic frog preform. The page blade, attachment geometry, dimensions, print settings and safety decisions are engineered and verified separately. Listing concept images are synthetic and are not photographs of a manufactured item.”

| Artifact | AI role | Evidence | Human-controlled work still required |
|---|---|---|---|
| `organic/reference/frog-concept-001-selected.png` | Original generic concept image from own text prompt | `evidence/imagegen-record.json` | Image rights review and explicit concept approval |
| `organic/raw/step1x/run-001/geometry.raw.glb` | Single-image organic geometry proposal | `organic/raw/step1x/run-001/step1x-run.json` | Hidden geometry review, CAD blade/join and final appearance approval |
| Blade coupons | No generative geometry | `coupons/blade-series-001/blade-coupon-series-report.json` | Physical page-marking and 100-cycle qualification |

No statement may imply that the generated mesh is a scan, measured reconstruction or physically tested product. Final listing disclosure, platform AI flagging, real-print photography and legal classification remain human-controlled release gates.
