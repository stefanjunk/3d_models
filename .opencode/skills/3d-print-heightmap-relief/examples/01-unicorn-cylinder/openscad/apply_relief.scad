// Set paths relative to this .scad file or replace them with absolute paths.
render(convexity=20) difference() {
  import("../build/gift-box-body.stl", convexity=20);
  union() {
    import("../build/unicorn-cutter.stl", convexity=20);
  }
}
