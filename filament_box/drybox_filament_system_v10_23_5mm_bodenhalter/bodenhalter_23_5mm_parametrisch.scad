// Bodenstehender Rohrhalter fuer eine Filament-Trockenbox
// Rohr-Aussendurchmesser: 23.5 mm
// Tiefster Auflagepunkt des Rohres: 110.0 mm ueber Boxboden
// Zweimal identisch drucken.

$fn = 128;

rohr_d = 23.5;
spiel_d = 1.3;
aufnahme_d = rohr_d + spiel_d;
auflage_hoehe = 110.0;
aufnahme_r = aufnahme_d/2;
achse_z = auflage_hoehe + aufnahme_r;

halter_tiefe = 32.0;
sockel_breite = 76.0;
sockel_dicke = 8.0;
steg_breite = 44.0;
kopf_r = 21.0;

ausschnitt_unten_halb = 13.4;
ausschnitt_oben_halb = 17.0;

module profil_2d() {
    difference() {
        union() {
            translate([-sockel_breite/2,0]) square([sockel_breite,sockel_dicke]);
            translate([-steg_breite/2,sockel_dicke]) square([steg_breite,achse_z+7-sockel_dicke]);
            polygon([[-sockel_breite/2,sockel_dicke],[-steg_breite/2,sockel_dicke],[-steg_breite/2,72.0]]);
            polygon([[steg_breite/2,sockel_dicke],[sockel_breite/2,sockel_dicke],[steg_breite/2,72.0]]);
            translate([0,achse_z]) circle(r=kopf_r);
        }
        translate([0,achse_z]) circle(d=aufnahme_d);
        polygon([
            [-ausschnitt_unten_halb,achse_z-0.8],
            [-ausschnitt_oben_halb,achse_z+kopf_r+2],
            [ ausschnitt_oben_halb,achse_z+kopf_r+2],
            [ ausschnitt_unten_halb,achse_z-0.8]
        ]);
    }
}

// Fuer den Druck liegt die grosse Seitenflaeche auf dem Druckbett.
rotate([90,0,0])
linear_extrude(height=halter_tiefe, center=true)
    profil_2d();
