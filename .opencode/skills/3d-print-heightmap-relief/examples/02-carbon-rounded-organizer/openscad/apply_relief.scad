// Set paths relative to this .scad file or replace them with absolute paths.
render(convexity=20) difference() {
  import("../build/desk-organizer.stl", convexity=20);
  union() {
    import("../build/carbon-cutter.stl", convexity=20);
  }
}
