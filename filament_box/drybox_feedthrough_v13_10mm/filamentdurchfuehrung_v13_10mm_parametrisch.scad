/*
  Drybox-Filamentdurchführung V13 – für eine Ø10,0-mm-Bohrung
  part = "layout", "inner", "outer_direct", "outer_pc4", "gasket", "m6_test"

  HINWEIS:
  "10 mm" bezeichnet die Bohrung in der Box, nicht ein M10-Gewinde.
  Das Befestigungsgewinde ist ein druckoptimiertes Sondergewinde (ca. Ø9,35 mm,
  Steigung 1,5 mm), damit es durch die 10-mm-Bohrung passt.
*/
part = "layout";
$fn = 160;

filament_bore_d = 3.4;
hole_d = 10.0;

bulk_pitch = 1.5;
bulk_root_d = 7.65;
bulk_major_d = 9.35;
bulk_clearance = 0.28;
bulk_length = 16.0;

ptfe_entry_d = 4.50;
ptfe_socket_d = 4.08;

module helical_external_thread(root_d, major_d, pitch, length, crest=0.30) {
    depth=(major_d-root_d)/2;
    union() {
        cylinder(d=root_d,h=length);
        linear_extrude(height=length,twist=-360*length/pitch,
                       slices=ceil(length/pitch*90),convexity=40)
            translate([root_d/2,0])
                polygon([[0,-pitch*crest],[depth,0],[0,pitch*crest]]);
    }
}

module bulk_female_thread_cutter(length=15.8) {
    helical_external_thread(
        bulk_root_d+2*bulk_clearance,
        bulk_major_d+2*bulk_clearance,
        bulk_pitch,length,0.30);
}

module m6_female_thread_cutter(length=9.2) {
    // Druckoptimiertes M6x1-Innengewinde für PC4-M6.
    helical_external_thread(4.92,6.24,1.0,length,0.30);
}

module inner_part() {
    difference() {
        union() {
            // trichterförmiger Körper, große Stirnseite zeigt ins Boxinnere
            hull() {
                cylinder(d=24.0,h=0.8);
                translate([0,0,7.2]) cylinder(d=25.0,h=0.8);
            }
            // flache Dicht-/Klemmfläche an der Boxwand
            translate([0,0,7.2]) cylinder(d=25.0,h=0.8);
            // Gewindezapfen passt durch Ø10-mm-Bohrung
            translate([0,0,8.0])
                helical_external_thread(bulk_root_d,bulk_major_d,
                                        bulk_pitch,bulk_length,0.30);
        }
        // großzügiger, abgerundeter Einlauftrichter
        hull() {
            translate([0,0,-0.1]) cylinder(d=19.0,h=0.3);
            translate([0,0,2.5]) cylinder(d=15.0,h=0.3);
        }
        hull() {
            translate([0,0,2.5]) cylinder(d=15.0,h=0.3);
            translate([0,0,5.3]) cylinder(d=9.0,h=0.3);
        }
        hull() {
            translate([0,0,5.3]) cylinder(d=9.0,h=0.3);
            translate([0,0,8.1]) cylinder(d=filament_bore_d,h=0.3);
        }
        translate([0,0,7.8]) cylinder(d=filament_bore_d,h=16.5);
    }
}

module outer_body() {
    union() {
        // großer Griff-/Klemmflansch an der Boxwand
        cylinder(d=27.0,h=4.0,$fn=12);
        translate([0,0,4.0]) cylinder(d1=27.0,d2=16.0,h=0.8);
        translate([0,0,4.8]) cylinder(d=16.0,h=23.2);
    }
}

module bulk_thread_and_channel_cut() {
    translate([0,0,-0.15]) bulk_female_thread_cutter(15.9);
    translate([0,0,15.1]) cylinder(d1=9.8,d2=6.4,h=1.3);
    translate([0,0,16.3]) cylinder(d1=6.4,d2=filament_bore_d,h=1.8);
}

module outer_direct() {
    difference() {
        outer_body();
        bulk_thread_and_channel_cut();
        translate([0,0,17.8]) cylinder(d=filament_bore_d,h=1.2);
        // leicht konische Direktaufnahme für 4-mm-PTFE
        translate([0,0,18.8]) cylinder(d1=3.84,d2=ptfe_socket_d,h=7.7);
        translate([0,0,26.4]) cylinder(d1=ptfe_socket_d,d2=ptfe_entry_d,h=1.8);
    }
}

module outer_pc4() {
    difference() {
        outer_body();
        bulk_thread_and_channel_cut();
        translate([0,0,17.4]) cylinder(d1=filament_bore_d,d2=4.92,h=1.2);
        translate([0,0,18.3]) m6_female_thread_cutter(9.2);
        translate([0,0,27.2]) cylinder(d1=6.24,d2=6.9,h=1.0);
    }
}

module gasket() {
    difference() {
        cylinder(d=23.0,h=1.4);
        translate([0,0,-0.1]) cylinder(d=9.4,h=1.6);
    }
}

module m6_test() {
    difference() {
        cylinder(d=14.0,h=8.5);
        translate([0,0,-0.1]) m6_female_thread_cutter(8.7);
    }
}

if(part=="inner") inner_part();
else if(part=="outer_direct") outer_direct();
else if(part=="outer_pc4") outer_pc4();
else if(part=="gasket") gasket();
else if(part=="m6_test") m6_test();
else {
    translate([-34,0,0]) inner_part();
    outer_direct();
    translate([34,0,0]) outer_pc4();
    translate([0,36,0]) gasket();
    translate([34,36,0]) m6_test();
}
