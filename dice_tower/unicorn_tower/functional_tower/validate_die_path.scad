// Collision check against the actual final STL reloaded from disk.
include <generated_parameters.scad>
$fn = 24;

module die_cube(index) {
    translate(die_path[index])
        rotate([0, 0, die_pose[index][0]])
            rotate([0, die_pose[index][1], 0])
                cube([die_size, die_size, die_size], center = true);
}

module die_sweep_actual() {
    for (i = [0 : len(die_path) - 2])
        hull() {
            die_cube(i);
            die_cube(i + 1);
        }
}

intersection() {
    import(final_mesh_path, convexity = 24);
    die_sweep_actual();
}
