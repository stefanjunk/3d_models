# R7 Decision Log – Purge-Catcher-Interface

## 2026-08-29 – Anforderungen 0.7.0-requirements.1

### DEC-R7-001 – R6-Fangkopf bleibt Ausgangsbasis

- Status: empfohlen, Anforderungsfreigabe ausstehend
- Entscheidung: Fangraum, Prallwand, offene Fallstrecke, Waben und metriMade-Gestaltung bleiben geschützt; nur die lokale R6-Aufnahme darf sich ändern.
- Grund: Der Benutzer bewertet den Catcher selbst als gut und beanstandet ausdrücklich Montage, Aufstellung und physisches Interface.

### DEC-R7-002 – R6-Wiper-Schraubadapter verwerfen

- Status: als pauschaler Ausschluss in Anforderungen `.2` verworfen; das ungemessene R6-Interface bleibt verworfen
- Entscheidung: Kein Zubehörgewicht und keine normale Wartung sollen über die beiden Wiper-Schrauben laufen.
- Grund: Lochabstand, Schraubenlänge, Gewindeeingriff, Wiper-Bauteilsteifigkeit und reale Kollisionen sind nicht qualifiziert. Das Lösen des Wipers ist für eine häufig zu wartende Abfalllösung unnötig riskant.
- Korrektur: Die Auswurfquelle bewegt sich mit dem Wiper entlang Z. Eine minimale, einmal montierte und real vermessene Schrauben-Datumplatte ist deshalb wieder zulässig; der wartbare Fangkopf wird von dieser Platte getrennt.

### DEC-R7-003 – Vertikale Schwalbenschwanzführung verwerfen

- Status: empfohlen, Anforderungsfreigabe ausstehend
- Entscheidung: Die R6-Führung mit Montage-/Entnahmerichtung von oben wird nicht fortgeführt.
- Grund: Sie benötigt Freiraum in unmittelbarer Maschinennähe, besitzt nur reibungs-/schwerkraftbasierte Halterung und erzeugt einen zusätzlichen toleranzkritischen Coupon, ohne das lose Behälterproblem zu lösen.

### DEC-R7-004 – Freistehender registrierter Dock-Tower

- Status: durch Benutzerkorrektur in Anforderungen `.2` verworfen
- Entscheidung: Dockbasis, Tragsäule, Fangkopf und entnehmbarer Innenbehälter bilden eine gemeinsame Datumskette. Drei weiche Anschläge registrieren nur an stationären Chassisflächen.
- Grund: Die Maschine trägt keine Zubehörlast; Aufstellung, Fallweg und Behälterlage werden gemeinsam reproduzierbar; das tägliche Entleeren benötigt keine Maschinenhandlung.
- Verwerfungsgrund: Der Purge-Wiper fährt entlang Z nach oben und kann auf höheren Z-Positionen auswerfen. Ein stationärer Fangkopf trifft die bewegte Quelle nicht; ein Tower über den ganzen Z-Weg ist vom Benutzer ausdrücklich unerwünscht.

### DEC-R7-005 – Drittanbieterdateien bleiben Betrachtungsquellen

- Status: fest
- Entscheidung: Keine Fremdgeometrie, Maße, Konturen, Fotos, Profile oder Projektmetadaten werden übernommen oder ausgeliefert.
- Grund: Mehrere Dateien tragen BY-NC, BY-NC-SA, Standard-Digital-File- oder exklusive Plattformlizenzen; andere besitzen gar keine verlässliche Rechteangabe. R7 nutzt nur abstrakte Funktionsprinzipien und eine vollständig neue Datum-/Lastpfadarchitektur.

### DEC-R7-006 – Produktion bleibt durch Freigaben gesperrt

- Status: fest
- Entscheidung: Vor ausdrücklicher Anforderungsfreigabe entsteht kein Konzeptbild; vor Konzeptfreigabe entsteht kein R7-CAD oder Fertigungsexport.
- Grund: Das Interface ändert Funktion, Montage, Bauteilaufteilung und physischen Risikopfad wesentlich.

## 2026-08-29 – Anforderungen 0.7.0-requirements.2

### DEC-R7-007 – Fangkopf folgt der bewegten Purge-Quelle

- Status: bevorzugtes Systemkonzept, Anforderungsfreigabe ausstehend
- Entscheidung: Fangkopf und kurzer Abwärts-Umlenker werden als leichte Baugruppe direkt im bewegten Bezugssystem des Wipers angeordnet.
- Grund: Nur eine mitfahrende lokale Fangzone hält den Abstand zur Auswurfquelle über niedrige, mittlere und hohe Z-Position konstant.

### DEC-R7-008 – Vermessene Zwei-Schrauben-Datumplatte

- Status: empfohlen; 17-mm-Lochabstand gemessen, übrige Schraubendaten und Anforderungsfreigabe ausstehend
- Entscheidung: Eine minimale feste Platte darf das vorhandene vertikale Wiper-Schraubenpaar mit 17 mm Mitte-Mitte-Abstand nutzen. Schraubenkopf, Gewinde, Schraubenlänge, Bauteildicke und Gewindeeingriff werden noch am realen Drucker bestimmt; keine Drittanbietermaße werden vorausgesetzt.
- Grund: Das Schraubenpaar bietet ein eindeutiges, mitbewegtes Datum bei geringster Zusatzgeometrie. Die reale Messung bestätigt den 17-mm-Abstand des bisherigen R6-Parameters unabhängig.

### DEC-R7-009 – Kurzhub-Schnellverschluss statt vertikalem Schwalbenschwanz

- Status: empfohlen, Anforderungsfreigabe ausstehend
- Entscheidung: Die Datumplatte bleibt für normale Wartung montiert; der Fangkopf wird über zwei eigene Führungsdatums und eine positive Rastung mit kurzer seitlicher oder schwenkender Bewegung gelöst.
- Grund: Reinigung soll die Wiper-Schrauben nicht wiederholt lösen und keinen langen freien Montageweg über der Baugruppe benötigen.

### DEC-R7-010 – Speichermasse bleibt stationär

- Status: empfohlen, Anforderungsfreigabe und Flugbahntest ausstehend
- Entscheidung: Nur die lokale Fang-/Umlenkfunktion bewegt sich. Ein großer entnehmbarer Behälter steht stationär darunter; seine Einlaufzone wird anhand von Purge-Tests bei niedriger, mittlerer und hoher Z-Position dimensioniert.
- Grund: So bleiben bewegte Masse und Hebelarm klein, ohne Tower, Schlauch oder mitfahrende Abfalllast.

### DEC-R7-011 – Fotovermessung wird als reales, couponpflichtiges Datum übernommen

- Status: erfasst; Anforderungsfreigabe und Coupon ausstehend
- Entscheidung: `WIPER-PHOTO-MEASUREMENTS-R7.yaml` hält die Benutzermaße 17 mm Schraubenabstand, 10 mm zur Purge-Ablageebene, 37 mm zur horizontalen Purge-Wurfbahn und 40 mm rückwärtige Wiper-Ausdehnung samt sechs gehashten Originalfotos fest.
- Grund: Die Fotos bestätigen Orientierung und Bauraum wesentlich besser als die bisherigen Renderannahmen. Wegen Maßstabperspektive und teilweise verdeckter Enddatums bleiben die Werte bis zum Lochbild-/Abstandscoupon physisch zu bestätigen; besonders die lokale Achszuordnung der 37-mm-Messung wird im Konzept explizit dargestellt.
