// Set paths relative to this .scad file or replace them with absolute paths.
render(convexity=20) difference() {
  import("../build/honeycomb-shelf.stl", convexity=20);
  union() {
    import("../build/outer-wall-cutter.stl", convexity=20);
    import("../build/inner-wall-cutter.stl", convexity=20);
    import("../build/front-face-cutter.stl", convexity=20);
    import("../build/back-face-cutter.stl", convexity=20);
  }
}
