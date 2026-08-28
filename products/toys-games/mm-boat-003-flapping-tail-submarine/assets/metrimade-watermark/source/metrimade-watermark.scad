// metriMade product watermark integration helper — MM-WM-001-R2
// Pass the generated product-specific SVG profile from tools/generate_watermark.py.

module metrimade_watermark_profile(
    profile_svg,
    profile_width,
    underside_readable = true
) {
    if (underside_readable)
        translate([profile_width, 0]) mirror([1, 0, 0])
            import(profile_svg, center = false);
    else
        import(profile_svg, center = false);
}

module metrimade_watermark_cutter(
    profile_svg,
    profile_width,
    depth = 0.40,
    underside_readable = true,
    overlap = 0.01
) {
    assert(depth >= 0.40 && depth <= 0.80, "Qualified depth range is 0.40-0.80 mm");
    assert(overlap > 0 && overlap <= 0.05, "Use a small positive Boolean overlap");
    translate([0, 0, -overlap])
        linear_extrude(height = depth + overlap)
            metrimade_watermark_profile(
                profile_svg,
                profile_width,
                underside_readable
            );
}

module metrimade_subtract_watermark(
    profile_svg,
    profile_width,
    depth = 0.40,
    underside_readable = true,
    overlap = 0.01
) {
    difference() {
        children();
        metrimade_watermark_cutter(
            profile_svg,
            profile_width,
            depth,
            underside_readable,
            overlap
        );
    }
}
