# Druck- und Montageanleitung — Revision 1.1.2

## Empfohlenes Startprofil: PLA / PLA+

| Einstellung | Startwert |
|---|---:|
| Düse | 0,4 mm |
| Schichthöhe | 0,16–0,20 mm |
| Linienbreite | 0,42–0,46 mm |
| Wände | 3–4 |
| Top-/Bottom-Layer | 5–6 |
| Infill | 12–15 % Gyroid oder Cubic |
| Erste Schicht | 20–30 mm/s |
| Sichtbare Außenwand | 35–55 mm/s |
| Brücke der Sorter-Taschen | 25–35 mm/s |
| Support | aus |
| Naht | bevorzugt nach hinten bzw. in eine glatte Randzone |

Temperatur, Kühlung und maximalen Volumenstrom aus dem konkreten Filamentprofil übernehmen. Für die 0,32-mm-Gravur ist eine ruhige Außenwand wichtiger als maximale Druckgeschwindigkeit.

## Zuerst die Proben

1. `04_fit_coupon_optional.stl` mit dem späteren Schubladenprofil drucken.
2. `05_carbon_texture_coupon_optional.stl` stehend wie exportiert drucken.
3. Im Toolpath prüfen, ob beide Richtungen des 2×2-Twills als echte Konturänderung erscheinen.
4. Erst danach Gehäuse, eine Schublade und Sorter slicen.

Die Passungslehre ordnet 0,30 / 0,45 / 0,60 mm Spiel je Seite von links nach rechts an. Der Standardentwurf verwendet 0,45 mm.

## Gehäuse

- Datei unverändert verwenden; die äußere Rückwand liegt auf dem Druckbett.
- Druckmaß: ca. 320 × 148,8 × 230 mm.
- Support aus; die beiden großen Öffnungen wachsen in dieser Orientierung als senkrechte Konturen.
- 6–8 mm Brim empfohlen.
- Die Rückwand ist graviert. Zwei glatte 3-mm-Randbänder sichern den hauptsächlichen Bettkontakt, trotzdem kann starke First-Layer-Stauchung die rückseitige Textur abschwächen. Z-Offset und erste Schicht vorher kalibrieren und keine überbreite erste Linie verwenden.
- Rückwand, Seiten und Randzonen im Slicer auf fehlende dünne Wände und unerwünschten Gap-Fill prüfen.

## Schublade

- Datei zweimal drucken, Boden auf dem Druckbett.
- Support aus; der offene Griff benötigt keine Dachbrücke.
- Die Front folgt der Gehäusekurve. Das gesamte Modell nicht skalieren, um eine stramme Passung zu lösen; zuerst Elefantenfuß kompensieren und dann das im Coupon gewählte Spiel in `model_parameters.json` übernehmen.
- Die Griffzone bleibt glatt. Prüfen, dass der Slicer keine Texturpfade in die Griffkante legt.

## Top-Sorter

- Boden auf dem Druckbett; Support normalerweise aus.
- Alle vier Außenwände sind texturiert, Fachinnenseiten und Oberrand bleiben glatt.
- Die vier 8,6-mm-Stecktaschen besitzen kurze Brückendächer. Brückenpfade kontrollieren und nur diese Taschen bei Bedarf lokal unterstützen.

## Gefüllte Carbon-Filamente

Bei PLA-CF oder PETG-CF eine verschleißfeste Düse und das exakte Herstellerprofil verwenden. Eine 0,6-mm-Düse ist robust, kann aber feine Höhenkartenanteile stärker glätten. Deshalb mit der gelieferten Probe entscheiden, ob die 0,4-mm-Detailauflösung oder die 0,6-mm-Prozessrobustheit wichtiger ist.

## Montage und Abnahmetest

1. Brim und Elefantenfuß vollständig entfernen.
2. Jede Schublade leer mindestens 20-mal über den ganzen Weg bewegen.
3. Vier Steckzapfen leicht entgraten; Sorter gerade und ohne Gewalt aufsetzen.
4. Optional Filz- oder TPU-Füße ankleben.
5. Mit einer geöffneten, typisch beladenen Schublade einen Anti-Kipp-Test durchführen.
6. Carbonflächen bei Streiflicht prüfen: keine fehlenden Wandpfade, losen Inseln oder sichtbaren Kachelnähte.

Die automatische Prüfung bestätigt Mesh-Topologie, nicht Slicerpfade, Passung oder reale Druckqualität.
