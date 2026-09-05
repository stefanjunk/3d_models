/*
  Commercial 3D provenance mark helper.

  This module creates geometry only. It does not establish ownership,
  compliance, authenticity, or AI disclosure. Use only an owned/authorized
  mark and place it on a verified nonfunctional, low-stress surface.

  Validate dimensions for the exact process. Defaults are starting values
  for many 0.4 mm-nozzle FDM workflows, not universal acceptance criteria.
*/

module provenance_mark(
    mark_text,
    size = 4,
    depth = 0.5,
    font = "Liberation Sans:style=Bold",
    halign = "center",
    valign = "center",
    spacing = 1.05
) {
    assert(len(mark_text) > 0, "mark_text must not be empty");
    assert(size > 0, "size must be positive");
    assert(depth > 0, "depth must be positive");

    linear_extrude(height = depth, convexity = 10)
        text(
            text = mark_text,
            size = size,
            font = font,
            halign = halign,
            valign = valign,
            spacing = spacing
        );
}

// Raised example:
// union() {
//     product_geometry();
//     translate([20, 10, 5])
//         provenance_mark("ACME-26A1");
// }
//
// Engraved example:
// difference() {
//     product_geometry();
//     translate([20, 10, 4.7])
//         provenance_mark("ACME-26A1", depth = 0.6);
// }
