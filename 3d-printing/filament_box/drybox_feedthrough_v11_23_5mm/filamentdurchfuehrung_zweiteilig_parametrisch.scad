/*
  Zweiteilige, möglichst luftdichte Filamentdurchführung für Drybox
  - 16-mm-Bohrung in der Box
  - Innenteil mit großem, gerundetem Einlauftrichter
  - Außenteil wahlweise mit direkter Aufnahme für 4-mm-PTFE
    oder 5-mm-Kernloch für einen PC4-M6-Pneumatikanschluss
  - optionaler TPU-Dichtring

  part = "layout", "inner", "outer_direct", "outer_pc4", "gasket"
*/
part = "layout";
$fn = 128;

box_hole_d       = 16.0;
filament_bore_d  = 3.5;
thread_pitch     = 2.5;
thread_root_d    = 13.2;
thread_major_d   = 15.3;
thread_length    = 13.0;
thread_clearance = 0.35;
ptfe_od          = 4.0;
ptfe_socket_d    = 4.2;   // ggf. nach Testdruck anpassen

module external_thread(root_d=13.2, major_d=15.3, pitch=2.5, length=13) {
    depth=(major_d-root_d)/2;
    union() {
        cylinder(d=root_d,h=length);
        linear_extrude(height=length,twist=-360*length/pitch,
                       slices=ceil(length/pitch*64),convexity=20)
            translate([root_d/2,-pitch*0.30])
                polygon([[0,0],[depth,pitch*0.30],[0,pitch*0.60]]);
    }
}

module smooth_funnel_cutter() {
    // Mehrere überlappende Kegel erzeugen einen sanften Einlauf.
    hull() {
        translate([0,0,-0.1]) cylinder(d=18.0,h=0.3);
        translate([0,0,3.0]) cylinder(d=15.5,h=0.3);
    }
    hull() {
        translate([0,0,3.0]) cylinder(d=15.5,h=0.3);
        translate([0,0,8.0]) cylinder(d=8.0,h=0.3);
    }
    hull() {
        translate([0,0,8.0]) cylinder(d=8.0,h=0.3);
        translate([0,0,11.5]) cylinder(d=filament_bore_d,h=0.3);
    }
}

module inner_funnel() {
    difference() {
        union() {
            // abgerundeter/trichterförmiger Innenkörper
            hull() {
                cylinder(d=23.0,h=0.4);
                translate([0,0,10]) cylinder(d=26.0,h=0.4);
            }
            translate([0,0,10]) cylinder(d=28.0,h=4.0);
            translate([0,0,14])
                external_thread(thread_root_d,thread_major_d,thread_pitch,thread_length);
        }
        smooth_funnel_cutter();
        translate([0,0,11.3]) cylinder(d=filament_bore_d,h=16.0);
    }
}

module female_thread_cutter(length=10.5) {
    external_thread(
        root_d=thread_root_d+2*thread_clearance,
        major_d=thread_major_d+2*thread_clearance+0.30,
        pitch=thread_pitch,
        length=length+0.5
    );
}

module lobed_nut_body() {
    // 12-eckig, gut mit der Hand greifbar
    cylinder(d=31.5,h=10,$fn=12);
}

module outer_adapter(mode="direct") {
    difference() {
        union() {
            cylinder(d=11.0,h=18.0);
            translate([0,0,18]) cylinder(d1=11.0,d2=30.0,h=10.0);
            translate([0,0,28]) lobed_nut_body();
        }
        if (mode=="direct") {
            translate([0,0,-0.1]) cylinder(d1=4.5,d2=ptfe_socket_d,h=2.1);
            translate([0,0,2.0]) cylinder(d=ptfe_socket_d,h=13.2);
            translate([0,0,15.0]) cylinder(d1=ptfe_socket_d,d2=filament_bore_d,h=5.2);
        } else {
            // PC4-M6 wird in dieses 5-mm-Kernloch eingeschraubt.
            translate([0,0,-0.1]) cylinder(d=5.0,h=11.2);
            translate([0,0,11.0]) cylinder(d1=5.0,d2=filament_bore_d,h=6.2);
        }
        translate([0,0,17.0]) cylinder(d=filament_bore_d,h=11.2);
        translate([0,0,27.5]) female_thread_cutter(10.5);
        translate([0,0,36.6]) cylinder(d1=16.4,d2=17.8,h=1.6);
    }
}

module gasket() {
    difference() {
        cylinder(d=27.2,h=1.6);
        translate([0,0,-0.1]) cylinder(d=16.1,h=1.8);
    }
}

if (part=="inner") inner_funnel();
else if (part=="outer_direct") outer_adapter("direct");
else if (part=="outer_pc4") outer_adapter("pc4");
else if (part=="gasket") gasket();
else {
    translate([-24,0,0]) inner_funnel();
    translate([22,0,0]) outer_adapter("direct");
    translate([58,0,0]) outer_adapter("pc4");
    translate([0,30,0]) gasket();
}
