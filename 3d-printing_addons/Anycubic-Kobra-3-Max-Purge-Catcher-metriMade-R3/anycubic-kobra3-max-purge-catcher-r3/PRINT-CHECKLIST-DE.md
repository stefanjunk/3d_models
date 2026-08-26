# Druck- und Einbaucheckliste R3

## 1. Messlehre vor dem Fangkorb

- [ ] `mount-fit-gauge-core.3mf` oder `mount-fit-gauge.stl` flach drucken.
- [ ] Drucker ausschalten und abkühlen lassen.
- [ ] Lehre an den Wischerträger halten; beide vertikal angeordneten Schrauben müssen jeweils innerhalb eines 8 × 4,2 mm Kapselschlitzes liegen.
- [ ] Der tatsächliche Schraubenabstand muss im abgedeckten Bereich 16,2–23,8 mm liegen; andernfalls stoppen und Parameter korrigieren.
- [ ] Lochmitten, Flanschbreite und Abstand zur Auswurfbahn messen.
- [ ] Bewegungsweg von Druckkopf, Wischer, Bett und Kabeln von Hand prüfen.
- [ ] Bei Nichtpassung stoppen und zuerst `params/catcher.json` korrigieren.

## 2. Waben-/Logo-Probe

- [ ] Vorzugsweise einen 30–40 mm breiten Ausschnitt mit Innenhaut, Wabenrippe und Logo drucken.
- [ ] Die 1,0-mm-Innenhaut muss geschlossen und frei von groben Löchern sein.
- [ ] Wabenrippen müssen ohne lose Kanten mit der Haut verbunden sein.
- [ ] Dünne Schriftzüge und die Aqua-Kante dürfen sich nicht ablösen.

## 3. Slicer-Preflight Fangkorb

- [ ] `metriMade-purge-catcher-3sides-5material-core.3mf` öffnen.
- [ ] Falls das scheitert, die fünf ausgerichteten Fangkorb-STLs gemeinsam als Mehrteilobjekt importieren; nicht automatisch verteilen.
- [ ] Genau ein Fangkorb; vollständiges Logo auf Vorder-, linker und rechter Displayseite; kein Logo gespiegelt.
- [ ] Fünf Materialien zuordnen: Weiß/Navy/Teal/Aqua/Sand. Bei nur vier Slots die Farbabweichung bewusst festlegen.
- [ ] Oberer Einlass, unterer Auslass, 1,0-mm-Seitenhaut, massive Prallwand/Fanghaube und beide M3-Schlitze im Layer-Preview prüfen.
- [ ] Support aus; 5-mm-Brim; mindestens vier Wände.
- [ ] Purge-Tower, Farbwechselzahl, Abfallmenge und Druckdauer bewusst freigeben.

## 4. Fangkorb montieren

- [ ] Nur nach bestandener Lehre drucken und montieren.
- [ ] Beide M3-Schrauben vollständig tragen lassen; Köpfe dürfen die Schlitze nicht nur randseitig berühren.
- [ ] Die im Ersatzpaket genannten M3×7 nicht blind mit der 3-mm-Platte wiederverwenden. Eine längere Schraube nur nutzen, wenn Gewindeeingriff ausreicht und nichts auf Block geht.
- [ ] Fangkorb nicht gegen Wischerhebel, Sensor, Kabel oder Druckkopf verspannen.
- [ ] Auswerfpaddel von Hand betätigen: Feder muss frei zurückstellen und darf Fangkorb oder Schraubenplatte nirgends berühren.
- [ ] Rückseite zeigt zur Befestigung; die drei Logos zeigen nach vorne, links und zur rechten Displayseite.

## 5. Unterbehälter

- [ ] `lower-bin-core.3mf` oder `lower-bin.stl` als eigenen Job drucken.
- [ ] Behälter lose unter den Fangkorb stellen; keine Haken oder Schrauben zwischen den Teilen.
- [ ] Öffnung überdeckt den freien 39 × 23 mm Auslass vollständig.
- [ ] 10–40 mm Luftspalt als Startbereich einstellen.
- [ ] Behälter lässt sich entnehmen, ohne Fangkorb oder Drucker zu belasten.

## 6. Funktions- und Sicherheitsfreigabe

- [ ] Einen Purge-Zyklus unter direkter Beobachtung ausführen.
- [ ] Fragment trifft die massive Prallwand oder Fanghaube, wird nach unten gelenkt, bleibt nicht hängen und fällt in den Behälter.
- [ ] Drei überwachte Purge-Zyklen ohne Treffer außerhalb, Rückstau oder lockere Schrauben.
- [ ] Nach Abkühlung Schraubensitz, Wabenrippen und Verformung kontrollieren.
- [ ] Erst danach normaler Betrieb; erste längere Drucke weiterhin beobachten.

Ein nicht bestandener Punkt blockiert die physische Freigabe.
