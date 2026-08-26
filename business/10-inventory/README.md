# Produktionsinventar

Letzte Aktualisierung: 2026-08-26  
Datenstatus: **Erstinventur offen**

Diese Datei ist die einzige Inventarquelle für Menschen und Agenten. Es gibt bewusst keine zweite JSON-, CSV- oder generierte Ansicht.

## Leseregeln

- Jeder physische Gegenstand oder zusammengefasste Bestand erhält eine dauerhafte ID.
- Unbekannte Angaben werden mit `unbekannt` bezeichnet und nicht geschätzt.
- Eine leere Kategorie bedeutet „noch nichts erfasst“, nicht „nachweislich nichts vorhanden“.
- Datumsangaben verwenden `YYYY-MM-DD`, Massen Gramm, Abmessungen Millimeter und Geldbeträge EUR.
- Supportfilament wird ausschließlich unter **Filamente** mit der Rolle `Support` oder `Support-Interface` geführt.
- Montierte Düsen müssen beim Drucker und im Düsendatensatz wechselseitig über ihre IDs verknüpft sein.
- Agenten dürfen Einträge ergänzen oder ändern, müssen dabei aber die vorhandenen Überschriften und Feldnamen beibehalten.

## ID-Bereiche

- `LOC-0001` ff. — Lagerorte
- `PRN-0001` ff. — Drucker
- `NZL-0001` ff. — Düsen
- `FIL-0001` ff. — Filamentspulen oder Gebinde
- `TOL-0001` ff. — Werkzeuge und Zusatzgeräte
- `CON-0001` ff. — Hilfs- und Verbrauchsmaterial

## Lagerorte

Noch keine Einträge.

## Drucker

Noch keine Einträge.

## Düsen

Noch keine Einträge.

## Filamente einschließlich Supportmaterial

Noch keine Einträge.

## Werkzeuge und Zusatzgeräte

Noch keine Einträge.

## Hilfs- und Verbrauchsmaterial

Noch keine Einträge.

Hierzu gehören beispielsweise Haftmittel, Trockenmittel, Reinigungsmittel, Schmierstoffe, Verpackung und Schutzausrüstung. Filament und Düsen werden nicht in diesem Abschnitt erfasst.

## Änderungsprotokoll

- 2026-08-26 — Inventarstruktur angelegt; Erstinventur noch offen.

## Datensatzvorlagen

Die folgenden Vorlagen erklären das einheitliche Format. Sie sind **keine Inventareinträge**. Beim Erfassen wird die passende Vorlage in den zugehörigen Abschnitt kopiert, ausgefüllt und dort „Noch keine Einträge“ entfernt.

### Vorlage Lagerort

```markdown
### LOC-0001 — Bezeichnung

- Typ: Werkstatt | Raum | Schrank | Regal | Box | Maschinenplatz | Sonstiges
- Übergeordneter Ort: ID oder keiner
- Status: Aktiv | Inaktiv
- Notizen: —
```

### Vorlage Drucker

```markdown
### PRN-0001 — Hersteller und Modell

- Status: Verfügbar | Druckt | Wartung | Außer Betrieb | Ausgemustert
- Standort: LOC-ID oder unbekannt
- Seriennummer / Asset-Tag: unbekannt
- Technologie: FDM/FFF
- Bauraum: X × Y × Z mm oder unbekannt
- Filamentdurchmesser: mm oder unbekannt
- Montierte Düse: NZL-ID oder keine
- Eigenschaften: Heizbett, Gehäuse, Multimaterial, Auto-Leveling, gehärteter Filamentpfad, Netzwerk oder unbekannt
- Freigegebene Materialien: Liste oder unbekannt
- Druckprofile: Pfade oder Namen oder unbekannt
- Firmware: unbekannt
- Gekauft am: unbekannt
- Letzte Wartung: unbekannt
- Nächste Wartung: unbekannt
- Notizen: —
```

### Vorlage Düse

```markdown
### NZL-0001 — Hersteller, Produkt und Durchmesser

- Status: Montiert | Auf Lager | Prüfen | Verschlissen | Entsorgt
- Anzahl: 1
- Standort: LOC-ID oder unbekannt
- Montiert in: PRN-ID oder keine
- Hersteller / Artikelnummer: unbekannt
- Durchmesser: mm oder unbekannt
- Werkstoff: Messing | Beschichtetes Messing | Gehärteter Stahl | Edelstahl | Rubin | Wolframcarbid | Sonstiges | Unbekannt
- Für abrasive Filamente geeignet: Ja | Nein | Unbekannt
- High-Flow: Ja | Nein | Unbekannt
- Kompatible Drucker: PRN-IDs oder unbekannt
- Einsatzstunden: unbekannt
- Gekauft am / Preis: unbekannt
- Produktseite / Datenblatt: unbekannt
- Notizen: —
```

### Vorlage Filament

```markdown
### FIL-0001 — Hersteller, Produkt und Farbe

- Status: Versiegelt | Offen | In Benutzung | Niedrig | Quarantäne | Leer | Entsorgt
- Rolle: Modell | Support | Support-Interface | Purge | Prototyp
- Standort: LOC-ID oder unbekannt
- Hersteller / Produkt / Artikelnummer: unbekannt
- Materialfamilie / Variante: zum Beispiel PLA / PLA+
- Farbe / Farbcode: unbekannt
- Durchmesser: mm oder unbekannt
- Abrasiv: Ja | Nein | Unbekannt
- Kompatible Drucker: PRN-IDs oder unbekannt
- Geeignete Modellmaterialien bei Supportrolle: Liste oder nicht zutreffend
- Trennverfahren bei Supportrolle: Breakaway | Wasserlöslich | Sonstiges | Nicht zutreffend | Unbekannt
- Anfangsmasse netto: g oder unbekannt
- Restmasse netto: g oder unbekannt
- Ermittlung der Restmasse: Waage | Druckerverbrauch | Sichtprüfung | Herstellerangabe | Unbekannt
- Chargennummer: unbekannt
- Gekauft / geöffnet / haltbar bis: unbekannt
- Hersteller-Trocknung: Temperatur °C und Dauer h oder unbekannt
- Zuletzt getrocknet: unbekannt
- Produktseite / Datenblatt: unbekannt
- Notizen: —
```

### Vorlage Werkzeug oder Zusatzgerät

```markdown
### TOL-0001 — Bezeichnung

- Kategorie: Messmittel | Wartung | Nachbearbeitung | Trocknung/Lagerung | Sicherheit | Elektronik | Handwerkzeug | Vorrichtung | Sonstiges
- Status: Verfügbar | In Benutzung | Service | Kalibrierung fällig | Ausgemustert | Verloren
- Anzahl: 1
- Standort: LOC-ID oder unbekannt
- Hersteller / Modell / Seriennummer: unbekannt
- Messbereich / Genauigkeit: unbekannt oder nicht zutreffend
- Letzte Kalibrierung / nächste Fälligkeit: unbekannt oder nicht zutreffend
- Gekauft am / Preis: unbekannt
- Produktseite / Datenblatt: unbekannt
- Notizen: —
```

### Vorlage Hilfs- oder Verbrauchsmaterial

```markdown
### CON-0001 — Bezeichnung

- Kategorie: Haftmittel | Reinigung | Trockenmittel | Schmierstoff | Nachbearbeitung | Verpackung | Sicherheit | Ersatzteil | Befestigung | Elektrik | Sonstiges
- Status: Auf Lager | Niedrig | Nicht vorrätig | Quarantäne | Abgelaufen | Entsorgt
- Bestand / Einheit: unbekannt
- Mindestbestand / Einheit: unbekannt
- Standort: LOC-ID oder unbekannt
- Hersteller / Produkt / Artikelnummer: unbekannt
- Charge: unbekannt
- Gekauft / geöffnet / haltbar bis: unbekannt
- Geeignete Materialien oder Geräte: unbekannt
- Produktseite / Datenblatt: unbekannt
- Notizen: —
```
