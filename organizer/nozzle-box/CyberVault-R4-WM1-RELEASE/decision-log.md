# Entscheidungsprotokoll – Cyber-Düsenschatulle

## Revision 1 – erste Anforderungserfassung

- Vier Düsengruppen vorgesehen: `0,4 STAHL`, `0,4 HART`, `0,6`, `0,8`.
- Hybridgestaltung aus parametrischem CAD und flachem Cyber-Höhenrelief empfohlen.
- Düsengeometrie und Ausführung des Verschlusses blieben offen.

## Revision 2 – integrierter Ein-Druck-Entwurf

- Kapazität auf zwölf Düsen erhöht: drei Stück je Düsengruppe (`user-stated`).
- Magnete, Metallstift und alle anderen Zukaufteile ausgeschlossen (`user-stated`).
- Herausnehmbaren Einsatz verworfen; alle zwölf Kavitäten werden fest in den Unterkasten modelliert (`user-stated`).
- Fertigungspräferenz auf `integrated-print` gesetzt (`user-stated`).
- „Alles in einem Stück“ als ein Print-in-place-Druckjob ohne Montage interpretiert: Unterkasten und Deckel müssen für die Scharnierbewegung geometrisch getrennte, aber unverlierbar gekoppelte Körper bleiben (`inferred`).
- Gefangene gedruckte Scharnierachse und integrierter PETG-Rastverschluss mit Kalibriercoupons empfohlen (`recommended`).
- Flaches Öffnen bis 180° empfohlen, um Zugriff und eine supportarme Ein-Druck-Ausrichtung zu unterstützen (`recommended`).
- Form und Maße der realen Düse bleiben der letzte maßbestimmende offene Punkt (`unresolved`).

## Revision 3 – Kobra-3-Max-Quick-Swap-Schnittstelle

- Duesentyp als komplettes Anycubic-Kobra-3-Max-Quick-Swap-Modul bestaetigt; lose Schraubduesen sind ausgeschlossen (`user-stated`).
- Die zwoelf Module werden horizontal in vier beschrifteten Dreiergruppen angeordnet (`recommended`).
- Statt einer eng abgeformten Negativkavitaet wird eine offene Drei-Punkt-Aufnahme mit freiem Duesenspitzenbereich und Fingermulden vorgesehen (`recommended`). Das toleriert kleine Unterschiede zwischen Herstellerrevisionen besser.
- Anycubic weist offiziell auf alte und neue Kobra-3-Max-Duesenversionen hin, nennt jedoch keine belastbaren Bauteilabmessungen. Gesamtlaenge, maximale Breite und maximale Dicke werden deshalb vor Produktions-CAD an den realen Duesen erfasst; bis dahin bleiben sie explizite Parameter (`recommended`).
- Ein Passcoupon prueft Sitz und Entnahme an der realen Duesenform, bevor die vollstaendige Schatulle gedruckt wird (`recommended`).

## Freigabe Revision 3 – 2026-08-11

- Der Benutzer hat die Anforderungen der Revision 3 explizit freigegeben.
- Die Konzeptphase ist damit entsperrt; Produktions-CAD und Fertigungsexporte bleiben bis zur Konzeptfreigabe gesperrt.
- Der noch nicht bemaßte Außenbauraum bleibt bewusst ein abgeleiteter Parameter und wird erst nach der realen Düsenvermessung berechnet.

## Konzept Revision 3 – 2026-08-11

- Das Konzeptblatt zeigt die feste Innenaufteilung als eindeutig prüfbares, leeres 4×3-Raster mit zwölf Aufnahmen.
- Vier seitliche Beschriftungsfelder bleiben auch bei belegten Aufnahmen sichtbar.
- Die Außenhaut folgt der freigegebenen Cyber-Sprache aus Hex-Motiv, breiten Leiterbahnnuten, Mikrohex-Feldern und robusten Rippen.
- Das Konzept zeigt ein Print-in-place-Fassscharnier sowie eine kompakte, achslose PETG-Rastlasche. Exakte Querschnitte, Freigänge und Dehnung werden erst nach Konzeptfreigabe konstruiert und per Coupon geprüft.
- Das Konzeptbild ist keine Maß- oder Funktionsprüfung; die Aufnahmen werden erst nach Vermessung der realen Quick-Swap-Düsen bemaßt.

## Konzeptfreigabe Revision 3 – 2026-08-11

- Der Benutzer hat das Konzept Revision 3 ausdrücklich freigegeben.
- Anforderungen und Konzept beziehen sich auf dieselbe Spezifikationsrevision; Produktions-CAD ist damit grundsätzlich entsperrt.
- Die maßbestimmende Düsenaufnahme bleibt bis zur Erfassung von Gesamtlänge, maximaler Breite und maximaler Dicke der realen Quick-Swap-Module blockiert. Diese Messung setzt keine neue Anforderungsfreigabe voraus, solange sie nur die bereits freigegebenen Parameter konkretisiert.

## Bildreferenz und Passcoupon – 2026-08-11

- Der Benutzer hat eine bemaßte Produktansicht der Kobra-3-Max-Quick-Swap-Düse bereitgestellt (`user-stated`).
- Verbindlich aus den Maßangaben übernommen: 45,0 mm Gesamtlänge und 5,0 mm Durchmesser am oberen zylindrischen Bereich (`measured-from-callout`, hohe Konfidenz).
- Die Beschriftung 0,4 mm bezeichnet die Düsenöffnung der abgebildeten Variante und wird nicht als Außenmaß verwendet.
- Aus dem Breitenverhältnis zur 5-mm-Zone ergeben sich nur orientierende Werte von etwa 5,6 mm für den langen unteren Körper und 9,2 mm für den maximalen Kragen. Wegen Auflösung, Rendering und fehlender zweiter Ansicht werden diese Werte ausschließlich für großzügige Freiräume verwendet.
- Die Aufnahme wird an zwei zylindrischen Zonen abgestützt. Der Düsenkragen erhält mindestens 11 mm freie Breite; eine eng abgeformte Kontur bleibt ausgeschlossen.
- Ein Drei-Varianten-Coupon mit 0,25 / 0,35 / 0,45 mm radialem Spiel pro Seite entscheidet die endgültige Passung. Diese Konkretisierung ändert keine freigegebene Anforderung und öffnet die Requirements- oder Konzeptfreigabe daher nicht erneut.
- Der Coupon `FIT-COUPON-DRAFT-A` wurde als 56 × 44 × 8 mm großer Einzelkörper erzeugt. STL und 3MF enthalten übereinstimmend 159.296 Dreiecke; Kanteninzidenz, Orientierung, Volumen und Dateiintegrität bestehen die digitale Prüfung.
- Die Dateien bleiben bis zum realen PETG-Passversuch ausdrücklich `DRAFT`; das Produktionsmodell wartet auf die Rückmeldung „1 / 2 / 3 Punkte passt am besten“.

## Passungsfreigabe – 2026-08-11

- Der Benutzer hat die mit zwei Punkten markierte Variante als beste Passung ausgewählt (`user-stated`, physischer Coupon).
- Verbindlicher Produktionswert: 0,35 mm Spiel je Seite an beiden Sattelbezügen.
- Diese Auswahl konkretisiert nur den bereits freigegebenen Passungsparameter; Anforderungen und Konzept Revision 3 bleiben freigegeben.
- Das Produktions-CAD ist damit für die vollständige Cyber-Schatulle entsperrt.

## Produktionskandidat CYBERVAULT-R3-CAD-A – 2026-08-11

- Die qualifizierte Aufnahme verwendet verbindlich 0,35 mm Spiel je Seite.
- Das offene Print-in-place-Modell misst rund 73,52 × 382,27 × 14,52 mm und passt auf das Druckbett des Anycubic Kobra 3 Max.
- Unterkasten und Deckel sind jeweils geschlossene, zusammenhängende Meshkörper; die unabhängige Prüfung meldet weder in offener noch in nominell geschlossener Stellung eine Volumenkollision.
- Die Düsensitz-Passung ist physisch bestanden. Scharnier, Rastverschluss und der vollständige Kasten bleiben bis zum PETG-Test `DRAFT`.
- Das JuSt-Innovation-Wasserzeichen wird gemäß Release-Gate erst nach stabiler Mechanikprüfung als letzte Geometrieänderung integriert.

## Kennzeichnungskandidat CYBERVAULT-R3-CAD-B-WM1 – 2026-08-11

- Das Produktions-Wasserzeichen `JSI-WM-001-R1` (Standardprofil) wurde als letzte Geometrieänderung exakt aus dem gebündelten DXF auf der druckbettseitigen Unterseite des Unterkastens integriert.
- Rezesstiefe 0,40 mm; Bett-Datum unverändert bei Z = 0,00 mm; Restboden 2,60 mm. Alle 18 Konturen sind in den drei wasserzeichentragenden 0,16-mm-Schichten vorhanden.
- Die erneute unabhängige Prüfung bestätigt weiterhin je einen geschlossenen Körper für Unterkasten und Deckel, exakt zwei Komponenten und 0 mm³ Überschneidung in offener sowie nominell geschlossener Stellung.
- Der Kandidat bleibt bis zur ausdrücklichen Wasserzeichenfreigabe und der anschließenden finalen Freigabeprüfung als `DRAFT` gekennzeichnet.

## Physische Grundfunktionsprüfung – 2026-08-11

- Der Benutzer bestätigt: „Scharnier passt, Rastverschluss passt.“
- Damit sind Freibewegung des Scharniers sowie Eingriff und Lösung des Rastverschlusses am gedruckten Kandidaten grundsätzlich physisch bestanden.
- Es wurde keine konkrete Zyklenzahl und kein bestückter Umdrehtest berichtet. Die 100-Zyklen-Vorprüfung, das 1000-Zyklen-Ziel, die Gruppenhaltekontrolle und die Lesbarkeitsprüfung bleiben daher dokumentierte Langzeit- beziehungsweise Nutzungsprüfungen und werden nicht stillschweigend als bestanden gewertet.
- Die Geometrie bleibt unverändert; nur der Nachweisstatus wird aktualisiert. Der nächste formale Schritt ist die Freigabe der bereits integrierten Kennzeichnung `JSI-WM-001-R1`.

## Revision 4 – Aussenhaut-Neugestaltung angefordert – 2026-08-11

- Der Benutzer bewertet die Revision-3-Aussenhaut als noch nicht ausreichend cyber-/science-fiction-artig und fordert deutlich mehr Gravuren, Zeichen sowie eine vollflaechige Bildreliefgestaltung auf Deckel und Seiten (`user-stated`).
- Funktion, zwoelf Duesenplaetze, Innenbeschriftung, 0,35-mm-Passung, Print-in-place-Scharnier und Rastverschluss bleiben unveraendert.
- Die bisherige Deckel-Hoehenkarte belegt nur rund 3,94 % der Rasterpixel und erklaert damit die optisch zu geringe Dichte.
- Empfohlen wird eine neu erzeugte monochrome Line-Art-Vorlage mit zentralem Quantenreaktor/Tech-Iris, segmentierten Panzerpaneelen, Datenbahnen, Hex-Gitter, Messskalen und Warnchevrons.
- Exakte Zeichen wie `CYBERVAULT`, `QSW-12`, `NOZZLE ARRAY`, Phi, Delta und Lambda werden parametrisch erzeugt; zufaellige KI-Schrift wird nicht in das Relief uebernommen.
- Die Deckelgravur wird zweistufig mit 0,64 mm Haupt- und 0,32 mm Nebentiefe ausgelegt. Gravurspannen bleiben maximal 1,6 mm breit, damit die druckbettseitigen Vertiefungen in der offenen Print-in-place-Orientierung sicher geschlossen werden koennen.
- Am umlaufenden Seitenband sind maximal 0,48 mm tiefe Gravuren und wenige 0,32 mm hohe Rippen mit druckbarer Anlauframpe vorgesehen. Scharnier, Rastverschluss und Flexurzonen erhalten mindestens 4 mm Reliefabstand.
- Diese Erscheinungs- und Geometrieaenderung eroeffnet Anforderungen und Konzept als Revision 4 erneut und invalidiert den bisherigen Kennzeichnungs-/Release-Gate. Der Grundfunktionsnachweis der unveraenderten Mechanik bleibt als Teilnachweis erhalten.

## Freigabe Anforderungen Revision 4 – 2026-08-11

- Der Benutzer hat die Anforderungen der Revision 4 explizit freigegeben.
- Die neue Cyber-/Science-Fiction-Aussenhaut darf nun als Konzeptblatt visualisiert werden.
- Innenraum, Duesensitze, Scharnier und Rastverschluss bleiben auf dem physisch bestaetigten Revision-3-Stand unveraendert.
- Produktions-CAD, Relief-Booleans und Fertigungsexporte bleiben bis zur ausdruecklichen Konzeptfreigabe Revision 4 gesperrt.

## Konzeptkandidat Revision 4 – 2026-08-11

- Das Konzeptblatt zeigt die unveraenderte schlanke Schatullenform mit einer deutlich dichteren Aussenhaut: zentraler sechseckiger Reaktorkern, verschachtelte Panzerpaneele, asymmetrische Datenbahnen, Mikrohex-Felder, Messstriche und Warnchevrons.
- Hauptgravuren und Sekundaerlinien sind visuell abgestuft; wenige flache Rippen und stehen gelassene Paneelinseln erzeugen zusaetzliche Reliefwirkung.
- Das Seitenband wird als kontinuierliches System aus Leiterbahnen, Hex-Knoten und Chevrons ueber die Rundungen gefuehrt. Funktionszonen an Scharnier und Rastverschluss bleiben frei.
- Das Bild ist eine Erscheinungs- und Bedienungsfreigabe, kein Mass-, Wandstaerken-, Boolean- oder Slicernachweis.
- Die kleine Draufsicht enthaelt trotz gezieltem Korrekturversuch einen KI-bedingten Akzent in `CYBERVAULT`. Dieser Bildtext ist nicht fertigungsautoritativ; die spaetere CAD-Beschriftung wird exakt als `CYBERVAULT`, `QSW-12` und `NOZZLE ARRAY` parametrisch erzeugt.

## Konzeptfreigabe Revision 4 – 2026-08-11

- Der Benutzer hat das Konzept Revision 4 ausdrücklich freigegeben.
- Produktions-CAD und Relief-Booleans sind damit fuer die neue Aussenhaut entsperrt.
- Verbindliche CAD-Merkmale sind der zentrale Reaktorkern, das dichte zweistufige Paneel-/Datenbahnnetz, exakte technische Beschriftungen sowie das kontinuierlich ausgerichtete Seitenband.
- Innenraum, 0,35-mm-Duesensitze, Print-in-place-Scharnier und Rastverschluss bleiben unveraendert auf dem physisch bestaetigten Revision-3-Stand.
- Die Kennzeichnung bleibt bis zum stabilen R4-Kandidaten blockiert und wird anschliessend erneut als letzte Geometrieaenderung integriert.

## Produktionskandidat CYBERVAULT-R4-CAD-A – 2026-08-11

- Die Deckeloberseite nutzt nun eine reproduzierbare zweistufige 16-Bit-Hoehenkarte mit 0,64 mm Haupt- und 0,32 mm Sekundaergravur. Das 5-mm-Dekorationsraster ist zu 85,24 % belegt; exakte Texte und Glyphen lauten `CYBERVAULT`, `NOZZLE ARRAY`, `QSW-12`, `Phi`, `Delta` und `Lambda`.
- Das Seitenmotiv kombiniert bis 0,48 mm tiefe Leiterbahn-/Knotengravuren mit 0,32 mm hohen, abgestuften Rippen. Daraus folgen mindestens 1,92 mm Restseitenwand und 2,36 mm Restdeckelplatte.
- Die dichte Deckelgravur wird als geschlossener Hoehenkarten-Cutter auf das OpenCascade-Ausgangsmesh angewendet. Der STEP-Export bleibt der editierbare Funktionsmaster; die finalen Reliefdetails sind fertigungsautoritativ in 3MF und STL enthalten.
- Nach Topologie-Kanonisierung bestehen Unterkasten und Deckel als je ein geschlossener, orientierter Manifold-Koerper. Das Print-in-place-STL enthaelt exakt zwei Komponenten; offene und nominell geschlossene Stellung weisen 0 mm³ Volumenkollision auf.
- Duesensitze, Scharnier- und Rastparameter sind gegenueber R3 unveraendert. Die physisch bestaetigte Grundfunktion wird deshalb als Schnittstellennachweis uebertragen; Reliefsichtbarkeit, bestueckter Umdrehtest, 40-cm-Lesbarkeit und Langzeitzyklen bleiben am R4-Druckteil offen.

## Kennzeichnungskandidat CYBERVAULT-R4-CAD-A-WM1 – 2026-08-11

- `JSI-WM-001-R1` (Standardprofil) wurde nach Abschluss der R4-Reliefgeometrie erneut als letzte geplante Produktgeometrieaenderung aus dem gebuendelten DXF in die druckbettseitige Unterseite integriert.
- Rezesstiefe 0,40 mm, Restboden 2,60 mm und Bett-Datum Z = 0,00 mm sind bestaetigt. In drei analytisch geprueften wasserzeichentragenden Hoehen liegen jeweils 18 geschlossene Konturen vor.
- Die anschliessende Vollvalidierung bestaetigt weiterhin exakt zwei Manifold-Koerper, Bauraumpassung und 0 mm³ Kollision. Der Kandidat bleibt bis zur ausdruecklichen Kennzeichnungs- und Release-Freigabe `DRAFT`.

## Finaler Release CYBERVAULT-R4-CAD-A-WM1 – 2026-08-11

- Der Benutzer hat Kennzeichnung und finalen Release Revision 4 ausdrücklich für exakt `CYBERVAULT-R4-CAD-A-WM1` freigegeben.
- Seit der bestandenen Kennzeichnungsprüfung wurde keine Produktgeometrie verändert. Finale STL-Dateien behalten denselben Dreiecksinhalt, die 3MF dieselben Mesh-Ressourcen und der STEP dieselben Bytes wie der freigegebene Kandidat; nur Release-Metadaten und Dateinamen werden bereinigt.
- Die finale Freigabe hebt dokumentierte Nachweisgrenzen nicht auf: physischer R4-Reliefdruck, 40-cm-Lesbarkeit, bestückter Umdrehtest sowie Langzeitzyklen bleiben offen.
