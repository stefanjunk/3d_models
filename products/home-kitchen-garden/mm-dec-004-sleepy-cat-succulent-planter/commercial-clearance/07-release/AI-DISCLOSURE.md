# AI use and provenance — MM-DEC-004

Status: draft disclosure; not approved for customer use.

Proposed customer wording: “AI-assisted design. An original text prompt was used to create the sleeping-cat reference image, and a locally hosted geometry-only Step1X-3D fork generated the organic cat preform. The nursery-pot cavity, base, drainage path, dimensions, print settings and safety decisions are engineered and verified separately. Listing concept images are synthetic and are not photographs of a manufactured item.”

| Artifact | AI role | Evidence | Human-controlled work still required |
|---|---|---|---|
| `organic/reference/cat-concept-001.png` | Original generic concept image from own text prompt | `evidence/imagegen-record.json` | Image rights review and explicit concept approval |
| `organic/raw/step1x/run-001/geometry.raw.glb` | Single-image organic geometry proposal | `organic/raw/step1x/run-001/step1x-run.json` | Floater decision, hidden geometry and final appearance approval |
| `organic/work/run-004/04-cavity-and-drain-clean.stl` | Hybrid derivative | `organic/work/run-004/functionalization-report.json` | Exact-pot measurement, wet-service and stability qualification |

No statement may imply that the generated mesh is a scan, measured reconstruction, watertight planter or physically tested product. Final listing disclosure, platform AI flagging, real-print photography and legal classification remain human-controlled release gates.
