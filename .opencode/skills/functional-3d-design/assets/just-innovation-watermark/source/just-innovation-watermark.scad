/* JuSt Innovation underside watermark — JSI-WM-001-R1; units: millimetres. */

function jsi_profile_file(variant) =
    variant == "compact"  ? "../exports/dxf/just-innovation-compact.dxf" :
    variant == "standard" ? "../exports/dxf/just-innovation-standard.dxf" :
    assert(false, str("Unknown JuSt Innovation profile: ", variant));

module jsi_profile_2d(variant = "standard", mirror_x = false) {
    if (mirror_x)
        mirror([1, 0, 0])
            import(file = jsi_profile_file(variant), layer = "WATERMARK");
    else
        import(file = jsi_profile_file(variant), layer = "WATERMARK");
}

module jsi_watermark_cutter(
    variant = "standard",
    depth = 0.40,
    uniform_scale = 1.0,
    z_overlap = 0.01,
    mirror_x = false
) {
    assert(depth >= 0.20 && depth <= 0.80, "Depth must be 0.20–0.80 mm.");
    assert(uniform_scale >= 1.0, "Do not shrink below the approved production profile.");
    assert(z_overlap > 0, "z_overlap must be positive.");
    translate([0, 0, -z_overlap])
        linear_extrude(height = depth + 2 * z_overlap, convexity = 20)
            scale([uniform_scale, uniform_scale])
                jsi_profile_2d(variant, mirror_x);
}

// Place children() with the intended bed-facing underside at Z=0.
module jsi_subtract_watermark(
    variant = "standard",
    depth = 0.40,
    uniform_scale = 1.0,
    mirror_x = false
) {
    difference() {
        children();
        jsi_watermark_cutter(
            variant = variant,
            depth = depth,
            uniform_scale = uniform_scale,
            mirror_x = mirror_x
        );
    }
}
