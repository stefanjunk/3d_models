# Druck- und Freigabecheckliste — R7-DRAFT-2

Der Hauptkörper ist noch **kein physisch freigegebenes Serienteil**. Die
Reihenfolge ist absichtlich fail-closed.

Die Datei `ANYCUBIC-R7-INSPECTION-measured-assembly-reference.3mf` ist nur zum
gemeinsamen Ansehen und Nachmessen der 17/10/37/40-mm-Bezüge bestimmt. Sie
enthält zusätzliche Maßleisten und eine montierte Darstellung: **nicht
drucken** und nicht als Fertigungsplatte verwenden.

## 1. Maschine und Schrauben dokumentieren

- [ ] Drucker stromlos schalten.
- [ ] Gewindegröße, Schraubenkopf-Durchmesser und -Höhe messen.
- [ ] vorhandene Schraubenlänge und Bauteildicke dokumentieren.
- [ ] verbleibenden Gewindeeingriff mit geplanter 2,4-mm-Datumplatte nachweisen.
- [ ] Wiper-Lage vor dem Lösen markieren; nach Montage darf sie sich nicht ändern.

## 2. Lochbildlehre

- [ ] `ANYCUBIC-R7-mount-pattern-gauge.3mf` in Anycubic Slicer Next öffnen.
- [ ] Maßstab 100 % und 17,0 mm Mitte-Mitte in der Slicer-Messung bestätigen.
- [ ] Lehre drucken; der geprüfte Headless-Lauf benötigt etwa 94 Sekunden.
- [ ] Beide Schrauben müssen ohne Verspannen durchgehen; Wiper-Datum bleibt unverändert.
- [ ] Ergebnis und Messmethode dokumentieren.

## 3. Führung und Rastung

- [ ] `ANYCUBIC-R7-slide-clearance-coupon.3mf` drucken.
- [ ] 0,20/0,30/0,40 mm vergleichen; kleinste frei montierbare, spielfreie Variante wählen.
- [ ] `ANYCUBIC-R7-latch-cycle-coupon.3mf` drucken.
- [ ] eindeutiges vollständiges Einrasten und sicheren Hartanschlag prüfen.
- [ ] 100 Ein-/Ausbauzyklen ohne Riss, bleibende Verformung oder unbeabsichtigtes Lösen bestehen.

## 4. Datumplatte und Hauptkörper

- [ ] Datumplatten-3MF im Slicer manuell auf Überhänge, Supports und Schichten prüfen.
- [ ] Datumplatte erst nach bestandenem Lochbild- und Schraubennachweis drucken.
- [ ] Hauptkörper-3MF manuell prüfen; der native Slicer meldet einen möglichen frei schwebenden Überhang.
- [ ] Supports dürfen keine Schraubenauflage, Führung, Rastung oder Purge-Fläche beschädigen.
- [ ] gedruckte bewegte Gesamtmasse einschließlich Datumplatte wiegen; Ziel ≤ 25 g.

## 5. Montage- und Funktionsgates

- [ ] Baugruppe stromlos montieren; keine erzwungene Passung oder halbe Raststellung zulassen.
- [ ] X/Y/Z vollständig von Hand verfahren; Bett, Kopf, Kabel und Wiper mit Zielreserve ≥ 5 mm prüfen.
- [ ] Rastung darf sich bei Bewegung, leichtem Zug und Vibration nicht lösen.
- [ ] je drei beaufsichtigte Purge-Zyklen bei niedriger, mittlerer und hoher Z-Position durchführen.
- [ ] Alle neun Auswürfe müssen gefangen werden und ohne Rückstau nach unten fallen.
- [ ] Erst danach Hauptteil, Kennzeichnung und finale Freigabe bewerten.

Kein Arbeitsschritt dieser Checkliste umfasst Upload oder Druckstart durch die
Automatisierung; diese Aktionen bleiben ausdrücklich beim Menschen.
