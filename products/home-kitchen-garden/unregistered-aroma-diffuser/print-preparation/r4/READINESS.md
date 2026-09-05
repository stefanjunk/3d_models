# R4 Druckvorbereitung — noch keine 3MF erzeugt

Nutzerauftrag: „erzeuge druck dateien. wir brauche die öffnung für die fiole
und den docht und es soll eine 3mf datei sein“.

R3 bleibt die sichtbare Entwicklungsbasis; bisherige Dateien und Prüfberichte
werden nicht verändert. Vorgesehen sind ein verdeckter Fiole-Zugang von unten,
ein abnehmbarer Fuß und eine getrennte Dochtführung. Das ist ein Vorschlag zur
Architektur, noch keine erzeugte oder auf Passung geprüfte Mechanik.
Referenzteile bleiben Ø50 × H64 mm Fiole und Ø5-mm-Docht.

Der Auftrag wechselt von einer Formstudie zur funktionalen Druckdatei.
Preflight 004 ist aktuell, bleibt aber CONCEPT_ONLY / C3 / R0 / K2 / Lane E.
R3s hashgebundene Berichte sind historische Formstudien, keine aktuelle
Fertigungsfreigabe; exakte Vorgängerartefakte liegen unter
../../preflight/history/preflight-003.json und design-spec-0.2.0.yaml.

## Ausgeführte Abklärung

- Repository sauber vor Beginn und mit origin/main synchronisiert.
- Im Produkt: Anycubic Kobra 3 Max mit 0.4-mm-Düse nur als Kandidat;
  Material, genaues Profil und Passungskorrektur UNKNOWN.
- Lokale Slicer-Referenzprofile sind vorhanden. Ein vorhandenes Profil ist
  weder die Bestätigung des verwendeten Filaments noch eine Kalibrierung.
- Registry-Abfrage mit unbekanntem Material: NO_MATCHING_PROCESS.
- Zusätzliche Abfrage des vorhandenen Referenzprozesses
  Kobra 3 Max / Anycubic PLA / 0.4 / Anycubic Slicer Next workspace reference
  profile: UNQUALIFIED für xy_clearance_sliding und hole_delta_vertical.
  Exaktes Ergebnis in reference-calibration-query.json.
  Anycubic PLA ist dabei nur untersuchter Referenzprozess, keine Materialauswahl.
- Vorhandene R3-Prüfung lässt normale Wandstärke und zertifizierte
  Selbstüberschneidungsprüfung offen; 200-mm-Docht kollidiert, 160-mm-Variante
  hat in nominaler Lage keinen volumetrischen Überlapp.

## Konkretes nächstes Arbeitspaket

Tatsächlichen Drucker, Düse und Filament (Hersteller/Typ) bestätigen.
Dann zunächst die vom funktionalen Design-Skill vorgeschriebenen
fit-coupon-xy-series und hole-gauge-vertical als passend profilierte 3MF
vorbereiten. Der Nutzer druckt und vermisst diese; kein automatischer Druckstart.
Erst mit den Ergebnissen werden Fiole-Aufnahme, Dochtbohrung und Fußpassung
festgelegt. Ein danach erzeugtes komplettes 3MF-Set muss Ausrichtung,
Supportentscheidung, eingebettete exakte Profile sowie Slicer-/Meshprüfungen
erhalten. Duftölbetrieb, Materialverträglichkeit und Standtest bleiben separat.

Keine neue Geometrie, kein geschätztes Passungsmaß, kein Herstellungs-G-Code,
keine 3MF, keine Installation und keine Druckeraktion in dieser Abklärung.
Die Anfrage ist noch nicht erfüllt; dies ist die dokumentierte Unterbrechung
am Kalibrierungs-/Prozess-Gate, kein abgeschlossener Druckdatei-Handoff.
