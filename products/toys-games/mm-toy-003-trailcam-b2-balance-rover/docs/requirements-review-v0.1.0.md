# Anforderungsprüfung — MM-TOY-003 v0.1.0

## Ziel und Abgrenzung

| Punkt | Einstufung | Kandidat v0.1.0 |
|---|---|---|
| Neues Produkt | user-stated | Eigener Ordner und eigene Kennung `MM-TOY-003`; `MM-TOY-002` bleibt unverändert |
| Fahrprinzip | user-stated | Eine geometrische Achse, genau zwei Räder, aktive Aufrechtregelung |
| Lenkung | recommended | Zwei unabhängige Motor-/Encoderkanäle; Differenzmoment statt mechanischer Lenkung |
| Kamera | inferred | Geschützte FPV-Kamera und servicefreundliche TrailCam-Architektur bleiben erhalten |
| Nicht enthalten | recommended | Keine zweite Achse, kein Casterrad, keine Federung, keine autonome Fahrt |

## Geometrie und Aufbau

| Punkt | Einstufung | Kandidat v0.1.0 |
|---|---|---|
| Räder | recommended | 120 mm Ziel, 110–130 mm zulässig, ungefähr 205 mm Spurweite |
| Hülle | recommended | Maximal 260 mm breit, 190 mm lang und 250 mm hoch |
| Masse | recommended | Ziel 1,8 kg, maximal 2,2 kg; Schwerpunkt 70–110 mm oberhalb der Radachse |
| Stil | inferred | Offener anthrazitfarbener Rippenrahmen, orange austauschbare Kamera-/Landeschutzelemente, sichtbare Serviceverschraubung |
| Ruhestellung | recommended | Nicht rollende Front-/Heckbügel oder Kufen berühren erst jenseits von 22° Neigung |

## Regelung und Elektronik

| Punkt | Einstufung | Kandidat v0.1.0 |
|---|---|---|
| Sensorik | recommended | Starre 6-Achs-IMU plus Quadraturencoder an beiden Rädern |
| Regelung | recommended | Kaskade aus Neigungs-/Drehratenregelung, Geschwindigkeitsregelung und differentieller Gierregelung |
| Taktraten | recommended | IMU mindestens 500 Hz, Neigungsregelung 250 Hz, Encoder 100 Hz, Befehle/Failsafe 50 Hz |
| Funk/Video | inferred | ELRS-Steuerung und analoges 5,8-GHz-FPV bleiben voneinander unabhängig |
| Schutz | recommended | Bewusstes Scharf-/Unscharfschalten, Watchdog, Stromlimit, Unterspannung, Kippabschaltung und erreichbarer Akkutrenner |

## Nutzung, Herstellung und Nachweis

| Punkt | Einstufung | Kandidat v0.1.0 |
|---|---|---|
| Einsatz | recommended | Beaufsichtigt, privat, zunächst fester ebener Boden; maximal 2,5 km/h |
| Konstruktion | inferred | `balanced-hybrid`: gedruckter Rahmen/Schutz/Träger, gekaufte Motoren, Encoder, Metallnaben, Räder, Elektronik und Schrauben |
| Druck | recommended | PETG, 0,6-mm-Düse, 0,24-mm-Schicht; jedes Teil passt zusätzlich auf 220 x 220 x 250 mm |
| Risiko | recommended | `normal-functional`, aber aktive Fahrzeugregelung bleibt bis zu angeleiteten physischen Tests nicht betriebsfreigegeben |
| Lieferumfang | user-stated + recommended | Konzept, Zerlegung, Regelungsplan, parametrisches CAD, DRAFT STEP/STL/3MF, Prüfberichte und physischer Testplan |

## Drei freizugebende Entscheidungen

1. **Untergrund:** Soll der erste Prototyp wie empfohlen nur auf glattem Innenboden und trockenem, festem Außenboden fahren? Raues Gelände würde größere Räder, mehr Drehmoment, stärkere Landeschutzelemente und deutlich schwierigere Regelung verlangen.
2. **FPV-Plattform:** Soll die Ähnlichkeit zum TrailCam wie empfohlen die geschützte analoge FPV-Kamera sowie unabhängige ELRS-/5,8-GHz-Verbindungen einschließen? Ohne FPV könnte der Aufbau leichter und niedriger werden.
3. **Abstellen/Umfallen:** Sind zwei nicht rollende Schutzbügel oder Kufen zulässig? Empfohlen ist ja: Der Rover hat weiterhin exakt zwei Räder, kann ausgeschaltet aber Kamera, Akku und Elektronik geschützt ablegen.

Wenn die empfohlenen Antworten passen, genügt **„Anforderungen freigegeben“**.
Korrekturen können stattdessen direkt zu den drei Punkten oder zu einem anderen
Eintrag genannt werden. Vor der Freigabe entstehen weder Konzeptgrafik noch CAD.
