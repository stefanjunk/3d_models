# Druck- und Einbaucheckliste R5

## 1. Messlehre vor der Fanghaube

- [ ] `mount-fit-gauge-core.3mf` oder `mount-fit-gauge.stl` flach drucken.
- [ ] Drucker ausschalten und vollständig abkühlen lassen.
- [ ] Lehre am Wischerträger anlegen; beide vertikalen Schrauben müssen innerhalb der beiden 8 × 4,2-mm-Schlitze liegen.
- [ ] Tatsächlichen Schraubenabstand messen. Zielbereich der Lehre: 16,2–23,8 mm.
- [ ] Schraubenköpfe, Flanschfläche sowie Abstand zu Paddel, Druckkopf, Bett und Kabeln prüfen.
- [ ] Bei Nichtpassung stoppen und `params/catcher.json` korrigieren.

## 2. Slicer-Preflight

- [ ] `metriMade-purge-catcher-3sides-5material-core.3mf` öffnen.
- [ ] Falls das scheitert, die fünf ausgerichteten Fanghauben-STLs gemeinsam als Mehrteilobjekt importieren; nicht automatisch verteilen.
- [ ] Genau eine Fanghaube und je ein vollständiges, ungespiegeltes Logo auf Vorder-, linker Prall- und rechter Display-/Schraubseite sichtbar.
- [ ] Kein rechteckiger Logo-Hintergrund; nur Waben und je eine schmale körperfarbene Tragstrebe hinter dem i-Punkt.
- [ ] Fünf Materialien Weiß/Navy/Teal/Aqua/Sand zuordnen oder einen bewussten Einfarb-Funktionstest anlegen.
- [ ] Wabenzellen müssen echte Öffnungen sein; kein Slicer darf sie automatisch schließen.
- [ ] Der 57 × 39-mm-Durchfall und der obere Einflug bleiben offen.
- [ ] Massive obere Trefferzone, 8-mm-Überhang und beide M3-Schlitze in der Layer-Vorschau prüfen.
- [ ] Support aus, 5–8-mm-Brim und mindestens vier Wände verwenden.
- [ ] Bei Mehrfarbdruck Farbwechselzahl, Purge-Tower, Abfallmenge und Druckzeit bewusst freigeben.

## 3. Montage

- [ ] Nur nach bestandener Lehre drucken und montieren.
- [ ] Vom Drucker vorne gesehen: Schlitz-Ohr rechts über das vertikale Schraubenpaar legen; hohe Prallwand links gegenüber dem Wischer.
- [ ] Beide Schrauben tragen vollständig. Schraubenköpfe dürfen Schlitze nicht nur am Rand klemmen.
- [ ] Weder M3×7 noch die im Beispiel empfohlenen M3×10 blind übernehmen: Gewindeeingriff und Bottoming für die reale Maschine prüfen.
- [ ] Auswerfpaddel von Hand betätigen. Feder und Paddel müssen frei zurückstellen.
- [ ] Druckkopf, Bett und Kabel im ausgeschalteten Zustand über den vollen relevanten Weg bewegen.

## 4. Behälter darunter

- [ ] Vorhandenen Korb/Behälter oder optional `lower-bin-core.3mf` verwenden.
- [ ] Öffnung muss den gesamten 57 × 39-mm-Fallbereich mit Sicherheitsrand abdecken.
- [ ] Behälter lose mit 10–40 mm Start-Luftspalt aufstellen; keine mechanische Verbindung zur Fanghaube.
- [ ] Behälter muss entnehmbar bleiben, ohne Drucker oder Fanghaube zu belasten.

## 5. Funktionsfreigabe

- [ ] Ersten Purge-Zyklus direkt beobachten.
- [ ] Fragment trifft Prallwand oder Überhang, fällt nach unten und bleibt weder in Waben noch am Logo hängen.
- [ ] Kontrollieren, ob feine Fäden seitlich durch die offenen Waben austreten. Falls ja: Betrieb stoppen und Zellgröße bzw. Innenfanglage anpassen.
- [ ] Drei überwachte Zyklen ohne Außentreffer, Rückstau, Verformung oder lockere Schrauben.
- [ ] Erst danach normale Nutzung; erste längere Drucke weiterhin beobachten.

Ein nicht bestandener Punkt blockiert die physische Freigabe.
