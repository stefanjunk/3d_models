# Validierungsbericht – Monolithische geometrische Haarspange R2

Datum: 2026-08-10  
Status: **digital bestanden / physisch noch nicht qualifiziert**

## Rekonstruktionsumfang

Die Vorlage ist ein einzelnes perspektivisches Konzeptbild. Maßstab, Kamera, Rückseite, Wandstärken und exakter Mechanismus sind daraus nicht messbar. Deshalb wurden die vom Nutzer vorgegebenen Abmessungen als Autorität verwendet und die verdeckte Mechanik als funktionaler Neuentwurf ausgeführt.

| Merkmal | Einstufung | Umsetzung |
|---|---|---|
| Segmentierte Armor-Schale | beobachtet, hohe Sicherheit | durchgehender Federbogen mit versetzten, erhabenen Paneelen |
| Einteilig, kein Metall | angefordert, hohe Sicherheit | ein zusammenhängender Meshkörper |
| Innere Zähne | beobachtet/inferiert, mittlere Sicherheit | 7 untere und 6 versetzte obere Kammzähne |
| Scharnierdetails | verborgen, hohe Unsicherheit | lange C-Flexur mit 1,6 mm Querschnitt und Hartanschlag |
| Klickverschluss | angefordert, hohe Sicherheit; Geometrie inferiert | 1,6-mm-Rastzunge mit Fanghaken |

## Digitale Geometrieprüfung

| Prüfung | Ergebnis | Status |
|---|---:|---|
| Außenmaß | 60,60 × 24,09 × 22,00 mm | bestanden |
| Manifold-Kernelstatus | `NoError` | bestanden |
| zusammenhängende Körper | 1 | bestanden |
| STL-Dreiecke | 1.580 | bestanden |
| offene / nicht-manifold Kanten | 0 / 0 | bestanden |
| degenerierte / doppelte Dreiecke | 0 / 0 | bestanden |
| Volumen | ca. 9.372 mm³ | bestanden |
| PETG-Massenschätzung bei 1,27 g/cm³ | ca. 11,90 g | bestanden, Ziel <20 g |
| 3MF-Einheit | Millimeter | bestanden |
| 3MF-Archiv- und XML-Struktur | lesbar | bestanden |

Die unabhängigen Detailwerte stehen in `mesh-audit-clip.json`, `mesh-audit-coupon.json` und `generation-metrics.json`.

## Vorläufige Flexur- und Rastungsrechnung

Die Berechnung nutzt nur einen kleinen, geraden Rechteck-Kragarm als konservativen Screening-Vergleich. Die echte C-Flexur ist gekrümmt und verformt sich geometrisch nichtlinear.

| Element | L × B × D | angenommene Auslenkung | Screening-Kraft | Wurzeldehnung | Ergebnis |
|---|---|---:|---:|---:|---|
| C-Flexur, als gerader Balken angenähert | 21,2 × 8,0 × 1,6 mm | 3,5 mm | 3,61 N | 1,87 % | knapp unter 2-%-Screeninggrenze |
| Rastzunge | 14,8 × 8,0 × 1,6 mm | 1,0 mm | 3,03 N | 1,10 % | Screening bestanden |

Verwendeter angenommener effektiver Druckmodul: 1.200 MPa. Dieser Wert ist kein Materialnachweis. Die geringe rechnerische Reserve der Hauptflexur ist der Grund für den verpflichtenden Coupon- und Zyklentest.

## Fertigungsprüfung

- Druckorientierung: große Seite auf dem Bett, `Zmin = 0`.
- Alle großen Funktionsbereiche beginnen auf der Bettseite; keine schwebende zweite Flexur oder mittig aufgehängte Kammschiene.
- Sichtbare Reliefüberstände der Paneele: maximal ca. 0,9 mm.
- Vorgesehene Mindeststärken: Schale 2,4 mm, Flexur und Rastzunge 1,6 mm.
- Support wird konstruktiv nicht erwartet, muss aber im realen Slicerprofil bestätigt werden.

Nicht durchgeführt: exakter Kobra-3-Max-Slicer-Dry-Run, G-Code-Prüfung, reale Brücken-/Nahtkontrolle und Druckzeit-/Materialschätzung des Slicers.

## Noch erforderliche physische Akzeptanz

1. Rastcoupon 50 Zyklen ohne Weißbruch, Riss oder bleibende Setzung.
2. Vollclip öffnet und schließt, ohne den Hartanschlag zu überfahren.
3. Alle Kontaktkanten sind nach dem Entgraten haut- und haarfreundlich.
4. 30 Minuten Halt am vorgesehenen Pferdeschwanz ohne schmerzhaftes Ziehen.
5. Nach 24 Stunden geschlossenem Zustand keine unzulässige PETG-Kriechverformung.

Bis diese Punkte bestanden und dokumentiert sind, bleibt das Modell `experimental` und nicht `qualified-local`.
