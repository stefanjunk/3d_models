// Reproducible presentation-only assembly view. Manufacturing geometry remains in the R2 STL/3MF exports.
$fn = 36;

wood = [0.56, 0.34, 0.17, 1.0];
wood_alt = [0.64, 0.40, 0.20, 1.0];

color(wood)
  import("../output/DRAFT/DRAFT-R2-driver-front-procedural-wood-unmarked.stl", convexity=10);
color(wood_alt)
  translate([0, 178.5, 0])
    import("../output/DRAFT/DRAFT-R2-driver-back-procedural-wood-unmarked.stl", convexity=10);
color(wood_alt)
  translate([92, 0, 0])
    import("../output/DRAFT/DRAFT-R2-hardware-front-procedural-wood-unmarked.stl", convexity=10);
color(wood)
  translate([92, 178.5, 0])
    import("../output/DRAFT/DRAFT-R2-hardware-back-procedural-wood-unmarked.stl", convexity=10);
color([0.70, 0.46, 0.24, 1.0])
  translate([4, 173.5, 2.6])
    import("../output/DRAFT/DRAFT-R2-screwdriver-comb-procedural-wood-unmarked.stl", convexity=10);
