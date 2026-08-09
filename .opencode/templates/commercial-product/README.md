# Commercial FDM Product Template

Copy these files into a new model project before detailed CAD. Do not mark the
product release-ready until commercial provenance, engineering, dimensional,
assembly, mesh, FDM, slicer, coupon, and applicable physical gates are
documented in `reports/evidence.json`.

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
