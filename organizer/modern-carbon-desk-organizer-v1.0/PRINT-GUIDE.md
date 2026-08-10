# Druck- und Montageanleitung

## Empfohlenes Standardprofil: PLA / PLA+

| Einstellung | Startwert |
|---|---:|
| Düse | 0,4 mm |
| Schichthöhe | 0,20 mm |
| Linienbreite | 0,42–0,46 mm |
| Wände | 3–4 |
| Top-/Bottom-Layer | 5–6 |
| Infill | 12–15 % Gyroid oder Cubic |
| Erste Schicht | 20–30 mm/s |
| Sichtbare Außenwand | 45–70 mm/s |
| Brücke der Sorter-Taschen | 25–35 mm/s |
| Support | aus |
| Naht | bevorzugt nach hinten |

Nutze Temperatur, Kühlung und maximalen Volumenstrom aus dem konkreten Filamentprofil. Die hohen Geschwindigkeitswerte des Druckers sind für die Carbon-Oberfläche nicht das Ziel; eine ruhige Außenwand erzeugt die bessere Optik.

## Pro Bauteil

### Gehäuse

- Datei unverändert verwenden: Die Rückwand liegt bereits auf dem Druckbett.
- Druckmaß: ca. 320,7 × 148,8 × 230 mm.
- Support aus; die Schubladenöffnungen wachsen in dieser Orientierung ohne große Brücken.
- 6–8 mm Brim empfohlen, besonders bei PETG oder gefülltem Filament.
- Carbon-Seiten im Toolpath stark vergrößern: Beide diagonalen Strangrichtungen müssen echte Außenwandpfade erzeugen.

### Schublade

- Datei zweimal drucken, Boden auf dem Druckbett.
- Support aus; der Griff ist oben offen und braucht keine Dachbrücke.
- Bei zu strammer Passung zuerst Elefantenfuß kompensieren und Außenmaße prüfen, nicht sofort das gesamte Modell skalieren.
- Der Coupon ordnet die drei Passungen von links nach rechts als 0,30 / 0,45 / 0,60 mm Spiel je Seite an.

### Top-Sorter

- Boden auf dem Druckbett; Support normalerweise aus.
- Die vier 8,6-mm-Stecktaschen im Boden besitzen kurze Brückendächer. Brückenpfade im Slicer kontrollieren.
- Bei schlechter Brückenqualität nur diese Taschen lokal unterstützen oder die Brückeneinstellungen verbessern.

### Carbon-Probe

- Die L-förmige Probe steht auf ihrer Basis; die Textur wird senkrecht gedruckt wie am Organizer.
- Keine Fuzzy-Skin-Funktion verwenden: Sie würde das definierte Twill-Muster überdecken.
- Reliefhöhe und Wiederholungsmaß nur nach Sichtprüfung der Probe ändern.

## Gefüllte Carbon-Filamente

Für PLA-CF oder PETG-CF ist eine gehärtete bzw. verschleißfeste 0,6-mm-Düse der robuste Ausgangspunkt. Nutze etwa 0,24–0,28 mm Schichthöhe und das exakte Herstellerprofil. Das feinere 1,10-mm-Strangrelief bleibt damit noch etwa zwei Linien breit. Gefüllte Filamente sind häufig steifer und maßhaltiger, aber nicht automatisch zäher.

## Montage und Funktionstest

1. Brim und Elefantenfuß sauber entfernen.
2. Jede Schublade leer über den ganzen Weg bewegen. Sie muss ohne Verkanten herausnehmbar sein.
3. Vier Steckzapfen leicht entgraten. Sorter gerade aufsetzen und nicht mit Gewalt schräg aufdrücken.
4. Optional vier Filz- oder TPU-Füße anbringen.
5. Schwere Gegenstände in die untere Schublade legen. Nicht beide schwer beladenen Schubladen gleichzeitig vollständig ausziehen.

## Abnahmetest

- Schubladen laufen nach 20 vollständigen Bewegungen ohne Abriebklemmen.
- Sorter sitzt plan und wackelt nicht auf den vier Zapfen.
- Organizer kippt mit typischer Beladung und einer vollständig geöffneten Schublade nicht.
- Carbon-Twill ist bei Streiflicht sichtbar und besitzt keine losen, unterextrudierten Rippen.
- Toolpath-Vorschau enthält keine fehlenden Wände, eingeschlossenen Supports oder unerwarteten Brücken.
