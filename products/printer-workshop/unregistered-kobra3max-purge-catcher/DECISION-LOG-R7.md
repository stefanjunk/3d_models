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

### DEC-R7-012 – Anforderungen `.2` freigegeben

- Status: vom Benutzer freigegeben
- Entscheidung: Die Requirements-Revision `0.7.0-requirements.2` gilt seit `2026-08-29T12:01:09+02:00` als freigegeben. Die empfohlenen Standardentscheidungen DEC-R7-01 bis DEC-R7-03 und die Interpretation der 37 mm als horizontaler Seitenversatz werden übernommen.
- Evidenz: Benutzerantwort „freigegebene“ unmittelbar auf die ausdrückliche Freigabeaufforderung für Revision `.2`.
- Folge: Konzeptstatus wechselt auf `pending`; ein Konzeptbild darf erzeugt werden. Produktions-CAD und Fertigungsexporte bleiben bis zur separaten Konzeptfreigabe gesperrt.

### DEC-R7-013 – Eigenständiges Z-Rider-Konzeptblatt v1 zur Prüfung ausgegeben

- Status: Konzeptfreigabe ausstehend
- Entscheidung: `concepts/R7-concept-sheet-z-rider-v1.png` visualisiert die freigegebene Architektur als kompakten Fangkopf am mitfahrenden Wiper, dünne Zwei-Schrauben-Datumplatte, kurzen lösbaren Anschluss, offene direkte Abwärtsumlenkung und separaten stationären Unterbehälter.
- Abgrenzung: Das KI-generierte Blatt ist ein nicht maßhaltiges Systemkonzept. Es definiert weder Schraubenkopf, Plattendicke, Rastprofil, Passung, Keep-outs noch Behälterabmessungen. Die 17/10/37/40-mm-Bezüge und alle Prüfkriterien werden ausschließlich aus der Spezifikation und den Realmessungen abgeleitet.
- Rechte: Die Geometrie wurde neu aus Funktionsanforderungen, eigenen R6-Merkmalen und den sechs eigenen Maschinenfotos visualisiert. Kein Drittanbieter-Mesh, -Bild, -Maß oder Befestigungsprofil wurde als Eingabe verwendet oder nachgezeichnet.
- Folge: R7-CAD, Fertigungsexporte und Slicing bleiben bis zur ausdrücklichen Freigabe dieses Konzeptblatts gesperrt.

### DEC-R7-014 – Z-Rider-Konzeptblatt v1 freigegeben

- Status: vom Benutzer freigegeben
- Entscheidung: Die im Konzeptblatt gezeigte Systemarchitektur und Formrichtung gilt seit `2026-08-29T12:17:09+02:00` als freigegeben.
- Evidenz: Benutzerantwort „freigegeben“ auf die ausdrückliche Freigabeaufforderung für `R7 Z-Rider v1`.
- Folge: Parametrische DRAFT-Geometrie und Testcoupons dürfen erzeugt werden. Das Bild bleibt nicht maßhaltig; reale Schraubendaten, Passung, Vollweg, Purge-Flugbahn, Kennzeichnung und finale Freigabe bleiben eigene Gates.

## 2026-08-30 – Benutzerkorrektur und R7-DRAFT-2

### DEC-R7-015 – R7-DRAFT-1 wegen nur deklarierter Maße verwerfen

- Status: verworfen und als negativer Nachweis erhalten
- Benutzerkorrektur: Im vorhandenen Dateibestand war kein Modell erkennbar, das den eingebrachten Maßen entspricht.
- Feststellung: R7-DRAFT-1 lud 17/10/37/40 mm in die Parameterdatei, prüfte geometrisch aber nur den 17-mm-Schraubenabstand. Die übrigen Werte waren nicht an benannte CAD-Flächen, Fangzonen oder Maschinen-Keep-outs gebunden.
- Entscheidung: Ein Zahlenvergleich im Parameterobjekt gilt nicht als Maßnachweis. R7-DRAFT-1 und R2–R6 werden aus dem aktiven Produktbestand entfernt; Rohmessungen und Freigaben bleiben erhalten.

### DEC-R7-016 – Vier Realmaße als explizite CAD-Zwangsbedingungen

- Status: R7-DRAFT-2 digital bestanden, physisch couponpflichtig
- Entscheidung: 17 mm steuern die Lochmittelpunkte, 10 mm legen das Purge-Datum bei `Z=-10` in die geschlossene Fangzone, 37 mm legen die Fangmittelebene bei `X=37` fest und 40 mm definieren den rückwärtigen Wiper-Keep-out bis `Y=-40`; sämtliche neue Fertigungsgeometrie bleibt bei `Y>=0`.
- Ergebnis: Alle vier nominalen Abweichungen sind 0,00 mm. Fangkopf und Datumplatte bilden je einen gültigen Einzelkörper; die bewegte PETG-Masse der ausgewählten Variante beträgt digital rund 24,44 g.
- Grenze: Schraubenidentität, reale Enddatums, Kollisionsfreiheit, Rastzyklen und Purge-Funktion bleiben physisch offen. Der Anycubic-Slicer warnt beim Vollteil und bei der Datumplatte vor Auskragungen; die 17-mm-Messlehre sliced ohne Warnung und bleibt der erste Druckschritt.

### DEC-R7-017 – Balanced auswählen und native Anycubic-3MF getrennt ausweisen

- Status: digital ausgewählt; menschliche Slicer-Vorschau und physische Coupons ausstehend
- Entscheidung: Die balanced-Geometrie mit 1,35-mm-Wabengitter und 1,60-mm-Vollwänden ist die einzige aktive Hauptkörpervariante. Sie bleibt mit 24,44 g unter dem 25-g-Ziel und besitzt mehr Wandreserve als aggressive; conservative überschreitet mit 29,80 g das Massenziel.
- 3MF-Handoff: Minimal-Core-3MFs bleiben als unabhängig validierte Austauschpakete erhalten, werden von Anycubic Slicer Next 1.3.9.4 im Headless-Modus aber nicht als belegte Platte erkannt. Die anwendbaren Dateien werden deshalb zusätzlich nativ mit den vollständigen Kobra-3-Max-/0,20-mm-/PETG-Profilen exportiert und müssen einen erneuten `slice-anycubic-next`-Lauf bestehen.
- Ergebnis: Alle fünf nativen Anycubic-Projekt-3MFs bestehen den Zielslicer-Rücktest. Hauptkörper und Datumplatte behalten die native Warnung vor möglicher Auskragung; daraus folgt ausdrücklich keine automatische Druckfreigabe.

### DEC-R7-018 – Gemeinsame Maßreferenz getrennt von Fertigungsdateien

- Status: digital bestanden; ausschließlich Inspektionsartefakt
- Anlass: In der getrennten Fertigungsübergabe zeigt die Fangkörper-3MF das 17-mm-Lochbild der separaten Datumplatte nicht. Dadurch ist die vollständige Maßbindung beim Öffnen nur einer Bauteildatei nicht unmittelbar sichtbar.
- Entscheidung: Eine zusätzliche 3MF kombiniert Datumplatte und Fangkörper in Einbaukoordinaten mit vier abgesetzten Maßleisten von exakt 17/10/37/40 mm. Die Leisten sind keine Fertigungsgeometrie; Datei und Berichte tragen `REFERENCE_ONLY_DO_NOT_PRINT`.
- Ergebnis: Sechs Komponenten bestehen Mesh- und Core-3MF-Prüfung. Der native Anycubic-Import/Slice besteht mit vollständigem Kobra-3-Max-/0,20-mm-/PETG-Profilsatz und meldet erwartungsgemäß schwebende Bereiche. Die fünf getrennten Druckprojekte bleiben die einzigen Fertigungsdateien.

### DEC-R7-019 – R7-DRAFT-2 wegen fehlendem realem Einbaunachweis verwerfen

- Status: verworfen; keine R7-Datei drucken oder montieren
- Benutzerkorrektur: Die Maßgrafik wirkt plausibel, die Modelle werden jedoch nicht passen.
- Feststellung: Die Digitalprüfung bewies nur interne Beziehungen im erfundenen CAD-Koordinatensystem. Für vorhandene Wiper-Schale, Metallablage, Rollen, Kabel, Bett, reale Schraubenköpfe und den Montageweg existierten weder Maschinensolids noch konservative vollständige Keep-outs.
- Kritische Abstraktionen: 37 mm wurden zur Mitte eines 62-mm-Catchers, 40 mm nur zu einer rückwärtigen Referenzebene und 10 mm zu einer beliebigen Ebene innerhalb der Fangzone. Der Catcher belegt nominal `X=6..68`, `Y=2,4..46,4` und `Z=-36..26` mm, ohne dass dieser freie Raum am Drucker nachgewiesen wurde.
- Entscheidung: Anforderungen wechseln auf `0.7.0-requirements.3 / changes-requested`; Konzept und Produktion sind blockiert. Vor neuer Geometrie müssen konkrete Fehlpassung, Achsrichtung/Endpunkte und zulässige X/Y/Z-Hüllkurve geklärt und mit einer flachen Interface-/Umrisslehre geprüft werden.
