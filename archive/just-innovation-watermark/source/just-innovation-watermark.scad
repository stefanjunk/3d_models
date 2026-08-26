/*
  JuSt Innovation underside watermark
  Release: JSI-WM-001-R1
  Units: millimetres

  Keep this file in source/ and the supplied DXF profiles in exports/dxf/.
  The outlines are custom geometry and have no runtime font dependency.
*/

function jsi_profile_file(variant) =
    variant == "compact"      ? "../exports/dxf/just-innovation-compact.dxf" :
    variant == "standard"     ? "../exports/dxf/just-innovation-standard.dxf" :
    variant == "trace-suffix" ? "../exports/dxf/just-innovation-trace-suffix.dxf" :
    variant == "trace-full"   ? "../exports/dxf/just-innovation-trace-full.dxf" :
    assert(false, str("Unknown JuSt Innovation profile: ", variant));

module jsi_profile_2d(variant = "standard", mirror_x = false) {
    if (mirror_x)
        mirror([1, 0, 0])
            import(file = jsi_profile_file(variant), layer = "WATERMARK");
    else
        import(file = jsi_profile_file(variant), layer = "WATERMARK");
}

// Positive tool body for a Boolean cut. z_overlap prevents coincident faces.
module jsi_watermark_cutter(
    variant = "standard",
    depth = 0.40,
    z_overlap = 0.01,
    mirror_x = false
) {
    assert(depth >= 0.20, "Use at least one 0.20 mm layer of depth.");
    assert(depth <= 0.80, "Depth above 0.80 mm requires a separate host-wall review.");
    assert(z_overlap > 0, "z_overlap must be positive.");
    translate([0, 0, -z_overlap])
        linear_extrude(height = depth + 2 * z_overlap, convexity = 20)
            jsi_profile_2d(variant, mirror_x);
}

// Place children() with its underside at Z=0 and subtract the mark upward.
module jsi_subtract_watermark(
    variant = "standard",
    depth = 0.40,
    mirror_x = false
) {
    difference() {
        children();
        jsi_watermark_cutter(
            variant = variant,
            depth = depth,
            mirror_x = mirror_x
        );
    }
}

// Preview example (uncomment):
// jsi_watermark_cutter("standard", 0.40);
