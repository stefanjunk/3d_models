# FDM-Varianten- und Nachweisvertrag

Da es sich um eine Greenfield-Konstruktion handelt, wird die Vorentwurfsbasis
explizit festgehalten. Nicht geslicte Werte bleiben „ausstehend“; es werden keine
scheinpräzisen Zeiten oder Materialeinsparungen erfunden.

## Ziele und geschützte Geometrie

Ziele: Druckzeit und PETG reduzieren, ohne Servicefähigkeit, Rohrklemmung,
Propellerfreiraum, Gitteröffnung, WTE-Auflage oder Tether-Zugentlastung zu
verschlechtern.

Geschützt:

- 68-mm-Nozzle-Bohrung und nominal mindestens 3 mm reale Propellerfreiheit;
- vollständiges Frontgitter, nominale Quadratöffnung höchstens 5,1 mm;
- vier Nozzle-/Guard-M3-Punkte und austauschbarer Motoradapter;
- zwei Kabelbinder je 10-mm-Sattel und mindestens 3 mm Restboden unter der Nut;
- großflächige, gummigepolsterte 75-mm-WTE-Auflage;
- S-förmige Tether-Zugentlastung vor dem Penetrator;
- keine FDM-Druckbarriere für Druck oder Elektrik.

## Kandidatenmatrix

| ID | Geometrie | Prozess | Status | Evidenz |
|---|---|---|---|---|
| B0 Vorentwurf | monolithischer gedruckter Käfig, massive Knoten | 0,4-mm-Düse / 0,20 mm | verworfen | Keine belastbare Slice-Metrik; große Druckplatte, schlechte Reparierbarkeit und unnötig viel Polymer. Dient nur als definierte Greenfield-Basis. |
| P1 Prozess-only | gleiche modulare Geometrie wie C1 | 0,6 / 0,30 mm, 0,68-mm-Linie | nach Slicerprüfung | Pfadplan: 4 Wände ≈2,53 mm, 3-Pfad-Steg ≈1,91 mm, 5 Bodenschichten ≈1,50 mm. Exakte Pfade noch im Ziel-Slicer prüfen. |
| G1 Geometrie-only | CFK/GFK-Rohre + kleine Sättel + lokale Schützer | 0,4 / 0,20 mm | mechanisch bevorzugt | Standardrohr übernimmt lange Lastpfade; defekte Halter einzeln ersetzbar. Noch keine Vergleichs-G-Code-Metrik. |
| C1 kombiniert | G1-Geometrie | P1-Prozess | **ausgeliefert** | 13/13 STL-Dateien: 0 Randkanten, 0 nichtmanifold Kanten. CAD-Vollmaterial 641,503 cm³ bzw. 814,8 g PETG als obere Grenze; kein Slice-Gewicht. |
| A1 aggressiv | zwei Wände, dünnere Guard-Stege, große Fenster | beliebig | vorab verworfen | Verletzt geschützte Gitter-/Klemmquerschnitte; Einsparung rechtfertigt erhöhtes Bruch-/Eingriffsrisiko nicht. |

## Dünnwandentscheidung

`config/fdm_plan.json` zeigt bei einer 4-mm-Platte mit vier Pfaden je Seite
rechnerisch **keinen verlässlichen Infill-Kern**. Deshalb wird nicht versucht,
über „5 % statt 20 % Infill“ eine Einsparung zu behaupten. Für solche Regionen
werden Außenmaß, Wandanzahl oder echte Fenster geändert – und jede Änderung im
Slicer kontrolliert.

## Noch zu erfassende quantitative Daten

Für B0/P1/G1/C1 im gleichen Slicerprofil:

1. G-Code-Druckzeit;
2. Extrusionsmasse inklusive Support/Brim;
3. Anzahl Werkzeugwechsel/Teile und größte Bettbelegung;
4. Sattelkraft nach Nass-/Trockenzyklus;
5. Guard-Impakt-/Fingerzugriffstest;
6. Tank-Strom, Schub und Vibration bei 20/35/50 %.

Erst diese A/B-Daten dürfen als Prozentverbesserung veröffentlicht werden.
