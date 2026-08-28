# Decision log – MM-SHO-001 V6.2

## 2026-08-28 – Draft 2 durch Nutzerkorrektur ersetzt

Stefan meldete sichtbare Löcher an Vorder- und Hinterabschluss beider
betrachteter Varianten, eine zu hohe Mittelfußkontur und einen Upper-Scheitel
oberhalb des Kragens. Die digitale Draft-2-Topologie war zwar wasserdicht,
bildete an den Stirnseiten aber eine sichtbare innere Bogenöffnung von etwa
`11,31 × 8,60 mm` hinten und `36,90 × 8,60 mm` vorne. Der vordere
Centerline-Scheitel erreichte `z=59,1341 mm`, also `7,1341 mm` über der
Kragenvorderkante. Revision `6.2.0-draft.3` fordert deshalb geschlossene
Endkappen und eine ab dem Kragen nicht erneut ansteigende Upper-Mittellinie.
Anforderungs- und Konzeptfreigabe wurden entsprechend wieder geöffnet; noch
keine Produktionsgeometrie wurde geändert.

Stefan gab die Draft-3-Anforderungen anschließend mit `freigegeben` frei. Der
Konzept-Gate wurde anschließend mit `freigegebene` bestätigt. Damit sind
Anforderungen und Formrichtung für die Draft-3-Produktionsgeometrie
freigegeben; digitale, Slicer- und physische Gates bleiben davon unberührt.

## 2026-08-28 – Draft-3-Geometrie digital bestanden

Alle drei Upper-Arten erhalten an Ferse und Zehe parametrische massive
8-mm-Abschlüsse mit mindestens `1,4 mm` lokaler Wand. Nach der exakten
Manifold-Union wird die Quelle bei `y=0,05/267,95 mm` eben beschnitten und mit
höchstens `0,05 mm` longitudinaler Verschiebung wieder auf `0/268 mm`
abgebildet. Dieser kleine kontrollierte Schritt beseitigt die beim direkten
Endschnitt entstandenen numerischen Sliver-Dreiecke, ohne den geschützten
V6.1-Anschluss oder die Gesamtlänge zu verändern. Alle sechs Schuh-STLs haben
danach null degenerierte Flächen, null Randkanten und genau eine positive,
wasserdichte Komponente; die gemessene Restöffnung beträgt an beiden Enden
`0,0 mm²`.

Die sichtbare Centerline beginnt an der vorderen Kragenkante bei
`y=95,208 mm, z=52,0 mm` und fällt bis `y=182,24 mm` monoton auf `z=39,45 mm`.
Der frühere 7,1341-mm-Hochpunkt über dem Kragen ist damit entfernt. Im
betroffenen Vorfuß-/Mittelfußbereich sinkt das äußere Hüllvolumen gegenüber
Draft 2 um `21.036,76 mm³` beziehungsweise `9,478 %`. Die vorgeschriebenen
Endkappen erhöhen lokal das eigentliche Materialvolumen; dieser dokumentierte
Trade-off wird akzeptiert, weil geschlossene Enden eine freigegebene
Funktionsanforderung sind.

Die Spezialprüfung besteht `17/17`, alle Mesh-Audits und der hashgebundene
Formreview bestehen. Der Projektstatus bleibt `REVIEW_REQUIRED`, bis exaktes
Anycubic-/TPU-Slicing, Coupon, Materialprüfung und Anprobe vorliegen. Ein
Produkt-Wasserzeichen wird erst nach Stabilisierung der Release-Geometrie als
letzte Geometrieänderung ergänzt.

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
