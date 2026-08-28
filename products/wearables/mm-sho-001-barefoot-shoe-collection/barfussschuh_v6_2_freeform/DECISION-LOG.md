# Decision log – MM-SHO-001 V6.2

## 2026-08-28 – Konzept 6.2.0-draft.2 freigegeben

Stefan bestätigte `yes, approved`. Die genehmigte Richtung erhält die
V6.1-Sohlengeometrie und ersetzt nur das Upper durch eine direkte
Freeform-Fläche mit weichem, geschlossenem Komfortkragen.

## 2026-08-28 – Geschützte Sohlenschnittstelle auf PCHIP gebunden

Eine natürliche kubische Interpolation der V6.1-Sohlenstationen driftete
zwischen den Stationen bis ungefähr 1,45 mm. Die unabhängige V6.1-Referenz und
V6.2 verwenden deshalb für die geschützte Schnittstelle PCHIP. Der dichte
1001-Punkt-Vergleich misst im akzeptierten Kandidaten maximal
`1.7053025658242404e-13 mm` Drift.

## 2026-08-28 – Draft-2 Attempt 1 visuell verworfen

Obwohl die Topologie bestanden hatte, zeigte die erste Draft-2-Produktion eine
isolierte vordere Kragenspitze bei `z=61.9479 mm` und zu ausgeprägte hintere
Schultern. Render und Bericht bleiben unter
`previews/rejected-v6.2.0-draft.2-attempt.1/` und
`validation/visual-review-draft2-attempt1.json` erhalten.

## 2026-08-28 – Kragenprofil und lokale Fairing-Zone akzeptiert

Der akzeptierte Rand folgt einem niedriggradigen periodischen Höhenprofil mit
Front/Seite/Heck `52.0/44.3/49.0 mm`. Eine 18-mm-Smootherstep-Zone verteilt die
Korrektur lokal, ohne die Öffnungsplanform oder den Sohlenanschluss zu
verschieben. Die Fairnessprüfung bewertet nur sichtbare Kurvensegmente und
misst nicht durch die ausgesparte Öffnung.

## 2026-08-28 – Dickes Infill-Envelope am Kragen lokal begrenzt

Der nominelle 4,5-mm-Innenoffset kollidierte in der engeren hinteren
Fairing-Zone. Nur diese optionale dicke Variante tapert dort auf 2,6 mm; die
breite Fläche bleibt bei 4,5 mm. Danach meldet PyMeshLab für alle acht Exporte
null selbstschneidende Flächen.

## 2026-08-28 – Keine Mesh-Decimation ohne Slicer-Baseline

Mit 419.352 Dreiecken und 19,996 MiB liegt das Voll-Upper unter den erklärten
Budgets. Ohne exaktes Maschinen-/Prozess-/TPU-Profil ist kein belastbarer
Zeit- oder Materialgewinn messbar. Der High-Fidelity-Master bleibt daher
unverändert; Optimierung wird erst mit einem reproduzierbaren Slicer-A/B-Test
wieder geöffnet.
