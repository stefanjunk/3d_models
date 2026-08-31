# Prospective 3D design preflight — MM-TOY-003 / 0.1.0-bom.2

`TrailCam B2 Balance FPV Rover | C5 (91.75/100) | R2 | K3 | Lane E | NOT_AUTONOMOUSLY_RELEASABLE`

## Entscheidung

**HOLD.** Der Interface-Graph ist jetzt vollständig genug für eine nachvollziehbare COTS-Integrationsrunde. Offizielle Nennmaße heben die kritischen mechanischen Hardpoints von einer allgemeinen E2-Beschreibung auf **E3 / nominal erfasst**. Das Gesamtprojekt bleibt bei **R2**, weil gelieferte Revisionen und Toleranzen unvermessen sind, der dynamische Rad/Boden- und Regelkreis ungetestet ist und der vollständige Anycubic-Maschinen-/Prozess-/Filamentprofilsatz fehlt. G3 ist deshalb `FAIL`; K3 verbietet eine autonome Freigabe.

Die C5-Einstufung ist kein Qualitätsurteil über das CAD, sondern beschreibt die intrinsische Systemaufgabe: ein absichtlich instabiles Fahrzeug koppelt 18 mechanische, elektrische, Daten-, Optik-, Mensch- und Umweltschnittstellen mit Regelung, LiPo-Energie, Verschleiß und gestuften Tests.

## Scorecard

| Dimension | Wert | Begründung |
|---|---:|---|
| REQ | 3 | Viele gekoppelte Geometrie-, Massen-, Regelungs-, Sicherheits- und Serviceanforderungen. |
| CTX | 3 | Montage, Kalibrierung, Fahrt, Tip-over, Service, Verschleiß und wechselnde Boden-/RF-Bedingungen. |
| PAR | 4 | 19 kundenspezifische Druckteile plus sechs Fit-Coupons. |
| INT | 4 | 18 teils dynamische, multidomänige und verdeckte Schnittstellen; Maximum I4. |
| CPL | 4 | Rad, Batterie und IMU propagieren Änderungen bis in COM, Regler, Schutz und Tests. |
| MOT | 4 | Koordinierte, aktiv geregelte Bewegung mit Radschlupf, Spiel und Tip-Zuständen. |
| GEO | 2 | Überwiegend parametrische Prismen/Zylinder, aber mehrere gekoppelte Einbauräume. |
| PHY | 4 | Dynamik, Vibration, Wärme, Stromversorgung, Reifencontact und Stoß sind gekoppelt. |
| MAT | 3 | PETG-Anisotropie, Metalle, Elastomer, Inserts/Fastener und LiPo verlangen Prozesskontrolle. |
| EXT | 4 | Eng integriertes Motor-/Sensor-/Elektronik-/Firmware-System. |
| VER | 4 | Coupons, Messung, Simulation, Fault Injection, Restrained- und Fahrtests. |

## Reifegewinn und Grenze

| Reifeanteil | Vorher | Jetzt | Aussage |
|---|---:|---:|---|
| Scope/Variante | R3 | R3 | Die `bom.2`-Variante ist eindeutig benannt, aber noch nicht geliefert. |
| Anforderungen | R3 | R4 | Quantitative Grenzen und gestufte Akzeptanzkriterien sind vorhanden. |
| Kritische Interfaces | R2 | R3 | Nenngeometrie und Quellen sind pro Kante registriert; unabhängige Messung fehlt. |
| Fertigungsprofil | R2 | R2 | Exaktes Anycubic-Profilset fehlt weiterhin. |
| Verifikation | R3 | R3 | Kriterien und Leiter sind definiert, Ergebnisse fehlen. |
| **Projekt** | **R2** | **R2** | Minimum-Regel: kein Gesamt-Sprung trotz echtem Interface-Reifegewinn. |

## COTS-Entscheidung

Der bisherige `Pololu 2686 + INJORA CRAW18003/CRAW20161023`-Radstapel wird für `bom.2` durch **BaneBots T81H-RM61 + T81P-496BB** ersetzt. Das System liefert eine 6-mm-Wellenaufnahme, eine zusammengehörige Naben-/Radfamilie, Hersteller-Nennmaße und verlinktes Naben-STEP. Nennwerte je Seite: 123.825 mm Rad-OD, 20.32 mm Breite, ungefähr 144.582 g Rad plus 14.175 g Nabe. Die frühere CAD-Masse von 179 g pro Radstapel sinkt rechnerisch um 20.243 g pro Seite.

Nur durch diesen Massentausch, ohne Geometrie- oder Ballaständerung, ergäbe sich eine **nicht validierte** Aktualisierung von 2114.656 g auf ungefähr **2074.17 g** und von z=71.156 mm auf ungefähr **72.55 mm**. Der größere Radius projiziert die alte 249.5-mm-Bauhöhe zugleich auf **251.4125 mm**, also 1.4125 mm über das 250-mm-Ziel. Das ist kein neuer CAD-Pass: Dach-/Achsgeometrie, die um 21.68 mm schmalere Lauffläche, Nabenregistrierung, Clearances und Schwerpunkt müssen in einer frischen `parametric.4`-Revision neu gerechnet werden.

Nicht gewählt: goBILDA 120-mm-Rhino trotz STEP, weil die Produktseite auf Ersatz/Auslauf hinweist; Studica 110-mm-All-Terrain bleibt eine bemaßte Alternative, besitzt in der vorliegenden Evidenz aber keinen gleichwertig registrierten STEP-/Nabenvertrag.

Vollständige Zeilen, Quellen, Verfügbarkeits-Snapshots und Muster-Gates stehen in `architecture/cots-interface-register-v0.1.0-bom.2.csv`. Der alte `parametric.3`-Stand bleibt als bestandene `bom.1`-Evidenz erhalten, ist für `bom.2` aber **STALE**.

## Funktionale FMEA

| Fehler | Endwirkung | Erkennung | Gegenmaßnahme / Nachweis |
|---|---|---|---|
| Nabe rutscht oder wandert | Rad-/Balanceverlust, Sturz | Witness marks, axial measurement, encoder mismatch | Muster vermessen; beide Stellschrauben und Snapring prüfen; restrained peak-torque/cycle test |
| Reifenradius/Grip weicht vom Modell ab | Capture-Verlust, Sturz | Loaded-radius and traction test, pitch log | Nur sauberer fester ebener Boden; Modell mit Messwerten korrelieren |
| Motorpod kriecht/reisst | Achsfehler und asymmetrisches Drehmoment | Sichtprüfung, witness marks, axis measurement | Coupon, Durchgangsschrauben/Unterlegscheiben, restrained cycle test |
| Batterie löst sich/kurzschließt | Brand oder harter Leistungsabfall | Inspektion, continuity/current/temp log | Zwei mechanische Rückhaltepfade, Sicherung nahe Pack, erreichbarer Trennstecker |
| IMU-Datum oder Achsenabbildung falsch | Regler verstärkt den Fall | statische Achsenprüfung, stale-data/fault injection | starres gekeytes Datum, dokumentierte Transformation, arming interlock |
| Driver/BEC brownout oder überhitzt | Torque-Verlust oder Reset | EN/DIAG, current sense, rail/temperature log | restrained reversals, unabhängiger cutoff, Freigabegrenzen |
| RC/FPV fällt aus | Stopbefehl/Ansicht verloren | link-health and video-loss injection | RC failsafe unabhängig vom Video; Sichtkontakt; Trennstecker |
| Landeschutz bricht | Kamera/Elektronik schlagen ein | low-energy controlled tip cycles | Druckorientierung freigeben, wiederholter Tip-Test, reject-on-crack |

## Hard Gates

| Gate | Ergebnis | Begründung |
|---|---|---|
| G0 Scope | PASS | Zweck, Nutzer und ausgeschlossene Anwendungen sind benannt. |
| G1 Entitäten/Interfaces | PASS | 22 Knoten und 18 Kanten sind maschinenlesbar erfasst. |
| G2 Evidenz | WARN | Offizielle Nenngeometrie ist brauchbar; Musterrevision/Toleranzen fehlen. |
| G3 Fertigungsprofil | FAIL | Vollständige exakte Maschine/Prozess/Filament-JSON-Profile fehlen. |
| G4 Verifikation | PASS | Jede Kante besitzt messbare Kriterien und eine Methode. |
| G5 Autonomie | WARN | K3 verlangt Expert-in-the-loop; autonome Freigabe ausgeschlossen. |
| G6 Lebenszyklus | PASS | Montage, Kalibrierung, Nutzung, Service, Demontage und Fehler sind berücksichtigt. |

## Minimaler nächster Nachweis

Zuerst je ein exaktes T81-Rad, T81H-RM61-Nabe, Pololu-4755-Motor und 1995-Bracket beschaffen und als zusammengebauten Antriebsstapel vermessen. Exit: Label/Revision, Masse, Rad-OD/Breite, belasteter Radius, Nabenbohrung, Wellenengriff, Stellschraubenlage, Snapring-Sitz, Axialspiel und Fotos sind mit Messunsicherheit dokumentiert. Erst dann darf `variant_confirmed` für die Antriebskanten auf `true` wechseln und das Druck-CAD an `bom.2` angepasst werden.
