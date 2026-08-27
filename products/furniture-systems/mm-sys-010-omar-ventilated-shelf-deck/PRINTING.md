# Vorläufiges FDM-Druckprofil

Das Profil ist ein Startpunkt für Prototypen, keine Produktionsfreigabe.

| Parameter | Startwert |
|---|---:|
| Düse | 0,6 mm |
| Linienbreite | 0,68 mm |
| Schichthöhe | 0,28 mm |
| Außenwände | 3 |
| Bodenlagen | 4-5 |
| Toplagen | 4-5, soweit vorhanden |
| Infill | 10-15 % Gyroid/Grid nur bei geschlossenen Volumen |
| Supports | zunächst aus; supportfreie Entwurfsabsicht im Slicer prüfen |
| Brim | 5-8 mm bei hohen Teilern und langen Rails |

## Material

- **PETG:** Standard für Clips, Werkstatt, Haushalt und leichte Docking-Funktionen.
- **ASA:** nur für Garage, UV oder erhöhte Temperatur; Schrumpfung neu kalibrieren.
- **PLA Pro:** nur für starre Innenraum-Organizer ohne Clipvorspannung oder Wärmebelastung.
- **TPU:** optionale separate Kontaktpads; nicht Bestandteil der einteiligen STL-Dateien.

## Orientierung

Die STL-Dateien sind bereits mit ihrer vorgesehenen breiten Druckfläche auf Z = 0 exportiert. Nicht automatisch neu orientieren. Hohe Kassetten und Teiler benötigen sauberes Bed-Leveling, gleichmäßige Kühlung und gegebenenfalls Brim.

## Vor Produktionsdruck

1. Modell im tatsächlichen Slicer öffnen und auf dünne Wände, Brücken, Nähte und erste Schicht prüfen.
2. Möbelkontakt oder Clip als Coupon drucken, nicht sofort das ganze Modell.
3. PETG-Fit zuerst mit 0,20/0,35/0,50 mm Spiel pro Seite vergleichen.
4. Clipteile in derselben Orientierung, Materialcharge und Trocknung wie das Endteil prüfen.
5. Erst nach Passung und Lasttest den vollständigen Druck starten.
