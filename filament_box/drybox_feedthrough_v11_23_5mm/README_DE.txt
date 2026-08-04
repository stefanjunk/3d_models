# Zweiteilige Filamentdurchführung für die Drybox

## Enthaltene Varianten

1. **Innenteil mit gerundetem Trichter**  
   Wird von innen durch eine 16-mm-Bohrung gesteckt. Der Einlauf ist groß und weich gerundet, damit das Filament auch schräg von der Rolle in die Durchführung läuft.

2. **Außenteil für 4-mm-PTFE direkt**  
   Der übliche PTFE-Führungsschlauch mit 4 mm Außendurchmesser wird etwa 12–15 mm tief eingedrückt. Die Bohrung ist am Eingang aufgeweitet und innen enger.

3. **Außenteil für PC4-M6 (empfohlen)**  
   Besitzt ein 5-mm-Kernloch. Ein handelsüblicher PC4-M6-Pneumatikanschluss wird vorsichtig direkt in PETG eingeschraubt. Mit etwas PTFE-Gewindedichtband ist diese Variante dichter und der Schlauch lässt sich komfortabel lösen.

4. **Optionale TPU-Dichtung**  
   Zwischen Innenflansch und Boxwand legen. Alternativ einen sehr dünnen Film neutralvernetzendes Silikon verwenden.

## Hauptmaße

- Boxbohrung: Ø16 mm
- Filamentkanal: Ø3,5 mm
- Custom-Druckgewinde: ca. Ø15,3 mm, Steigung 2,5 mm
- geeignete Boxwandstärke: ungefähr 1–5 mm
- direkter PTFE-Schlauch: Ø4 mm außen
- innerer Trichtereinlauf: ungefähr Ø18 mm

## Montage

1. Mit einem Stufenbohrer ein sauberes Ø16-mm-Loch bohren.
2. Bohrung beidseitig vollständig entgraten.
3. Optional TPU-Dichtung auf das Innenteil schieben.
4. Innenteil von innen durch die Boxwand stecken.
5. Außenteil von außen aufschrauben und nur handfest anziehen.
6. PTFE-Schlauch in die direkte Aufnahme drücken oder PC4-M6-Anschluss montieren.
7. Dichtheit mit einem Hygrometer über mehrere Stunden prüfen.

Das gedruckte Gewinde ist kein genormtes M16-Gewinde. Innen- und Außenteil gehören als Paar zusammen.

## Druck

Empfohlen: PETG, 0,4-mm-Düse, 0,18–0,24 mm Schichthöhe, 5 Wände, 40–60 % Infill.

- Innenteil: große Trichteröffnung auf das Druckbett
- Außenteil: PTFE-Stutzen auf das Druckbett, Brim verwenden
- TPU-Dichtung: flach drucken, TPU 95A
- Gewinde vor der Montage reinigen und zunächst außerhalb der Box testen

Bei einer 0,8-mm-Düse sollte das Gewindespiel im SCAD-Skript auf etwa 0,45–0,55 mm erhöht werden.

## Passung der direkten PTFE-Aufnahme

4-mm-PTFE-Schläuche und gedruckte Bohrungen schwanken. Zuerst einen Test drucken. Im SCAD-Skript kann `ptfe_socket_d` angepasst werden:

- Schlauch zu locker: Wert um 0,1 mm verkleinern
- Schlauch lässt sich nicht einsetzen: Wert um 0,1–0,2 mm vergrößern

Für die bestmögliche Luftdichtheit ist die PC4-M6-Version vorzuziehen.
