# Commercial FDM Product Template

Copy these files into a new model project before detailed CAD. Do not mark the
product release-ready until commercial provenance, engineering, dimensional,
assembly, mesh, FDM, slicer, coupon, and applicable physical gates are
documented in `reports/evidence.json`.

Component decisions embedded in `design-spec.json` are authoritative. `bom.json`
is a derived release artifact and must match those decisions; do not maintain a
second component-decision manifest.

Before geometry work, obtain explicit approval of
`references/requirements-summary.md`, then generate and obtain approval of a
versioned `references/concept-vN.png`. Record both approvals and hashes in
`design-intake.json`; the canonical validator must emit `DESIGN_INTAKE_PASS`.

The product listing must name supported nozzle/material classes and distinguish
recommended, conditional, unsupported, and customer-qualified combinations.
Do not advertise universal printer compatibility.

Keep `ATTRIBUTIONS.md` in the distributed product package whenever a CC-BY
asset is present. When no third-party asset is included, retain the explicit
"No CC-BY assets" statement so the release review remains unambiguous.

Keep `THIRD_PARTY_NOTICES.md` synchronized with distributed permissive
dependencies and assets. A dependency used only by the internal build process
must still remain in `provenance.json`, even if it is not redistributed with
the customer package.
