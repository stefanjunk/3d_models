# Beschaffungs- und Variantenliste

Preis- und Verfügbarkeits-Snapshot: **13. August 2026**. Preise schwanken, teils
USD ohne Versand, Einfuhr und Steuer. Vor Bestellung immer Maße, Lieferstatus,
Kabeldurchmesser und Steckervarianten prüfen.

## Empfohlene v0.1

| Baugruppe | Menge | Richtpreis | Auswahl / Begründung |
|---|---:|---:|---|
| 2828-Unterwasser-Outrunner, 500 KV, 3–4S | 3 | 3 × US$29,10 | [APISQUEEN 2828](https://www.underwaterthruster.com/products/apisqueen-brushless-waterproof-motor-2828-12v-16v-500kv-for-underwater-thruster-boat-rov); gefluteter Motor statt Wellendichtung. 100-m-Angabe ist unbestätigte Herstellerangabe. |
| 45-A-Bidirektional-ESC, 1–2-ms-PWM | 3 | 3 × US$17,64 | [APISQUEEN ESC](https://www.underwaterthruster.com/products/apisqueen-12-24v-3-6s-lipo-45a-bi-directional-esc-to-control-brushless-motors-propellers-in-forward-or-reverse-rotation); Neutral 1,5 ms. Nur IPX6, daher **im trockenen WTE**. |
| 60-mm-Unterwasserpropeller, CW/CCW | 4 | 4 × US$3 | [U2-Propeller](https://www.underwaterthruster.com/products/60mm-diameter-three-blade-plastic-propeller-for-u2-underwater-propeller); je zwei Drehrichtungen, einer als Ersatz. Keine gedruckten Propeller. |
| 75-mm/3″ Locking-WTE, ca. 220 mm nutzbar | 1 | US$160–240 | [Blue Robotics WTE-Konfigurator](https://bluerobotics.com/store/watertight-enclosures/wte-vp/); Acrylrohr, transparente Front, rückseitige Kappe mit mindestens 6× M10, PRV/Vent. Endgültigen Preis konfigurieren. |
| WetLink-Penetrator, kabelgenau gewählt | 4 | US$52–68 | 3× normaler [WetLink](https://bluerobotics.com/store/cables-connectors/penetrators/wlp-vp/) für Motorkabel + 1× [JPT](https://bluerobotics.com/store/cables-connectors/penetrators/wetlink-penetrator-jpt/) für den durchgehenden Tethermantel. Spezifikation gilt nur mit geprüftem Kabel; Durchmesser vor Kauf messen. |
| Druckentlastungsventil/Vent + Blindstopfen | 1 Satz | US$15–30 | Für sicheres Öffnen, Vakuumtest und unbenutzte M10-Bohrungen; laut [WTE-Handbuch](https://bluerobotics.com/learn/watertight-enclosure-wte-assembly-new/) erforderlich/empfohlen. |
| Raspberry Pi Zero 2 W | 1 | €19–25 | [Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/): 65×30 mm, CSI, H.264 1080p30, offizieller Listenpreis US$15. |
| Camera Module 3 Wide | 1 | €35–45 | [Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/); Autofokus und Weitwinkel, hinter planer Acrylfront. Unter Wasser wird der Bildwinkel kleiner. |
| Ethernet/USB-HAT für Pi Zero | 1 | ca. US$12 | [Waveshare ETH/USB HUB HAT B](https://www.waveshare.com/eth-usb-hub-hat-b.htm); 100BASE-TX reicht für Video und Steuerung. |
| Raspberry Pi Pico 2 | 1 | €5–8 | [Pico 2](https://www.raspberrypi.com/products/raspberry-pi-pico-2/); Hardware-PWM, unabhängiger 300-ms-Watchdog. |
| Geregelter 5-V/5-A-BEC | 1 | €15–30 | Z. B. [Matek BEC12S-PRO](https://www.mateksys.com/?portfolio=bec12s-pro) oder [Pololu 5 V/5 A](https://www.pololu.com/product/2851). Kein No-Name-Regler ohne Brownout-Test. |
| 3S-LiPo 2200 mAh, ≥30C, XT60 | 1 | €20–30 | Gängige RC-Auto/Fluggröße; etwa 100×34×28 mm. Z. B. [Gens Ace 3S](https://gensace.de/collections/3s-lipo-battery). Maße vor Kauf prüfen. |
| Sicherungen, XT60, Verteiler, 12/18-AWG-Kabel | 1 Satz | €20–35 | 30-A-Hauptsicherung nahe Akku, je 10 A pro Motorzweig als Startwert; nach Strommessung festlegen. Elektronikzweig separat absichern. |
| Lecksensorpads + Transistor/Komparator | 1 | €3–8 | Zwei Pads an der tiefsten Gehäusestelle, normally-safe Eingang zum Pico. Vor jedem Tauchgang mit feuchtem Tuch testen. |
| Cat5e-Patch-/Installationskabel, 5–10 m | 1 | €10–20 | Nur Pool-Prototyp: Oberflächenende trocken halten, eigene Zugentlastung. Für Feldbetrieb PUR-/wasserblockiertes [Subsea-Kabel](https://bluerobotics.com/store/cables-connectors/pur-subsea-cable/) verwenden. |
| CFK-Rohr 10×8×1000 mm | 1 | €14,80 | [AHLtec](https://www.ahltec.de/shop/de/Carbon-Rohr-10-mm-x-8-mm-x-1000-mm.html), aktuell sofort lieferbar; Zuschnitt 2×300 + 2×190 mm. Schnittenden mit Epoxid versiegeln. Für Salzwasser GFK bevorzugen. |
| PETG/ASA, 1-kg-Spule | 1 | €20–30 | PETG als Einstieg; ASA bei beherrschtem Warping. Kein PLA für dauerhaft nasse/warme Funktionsteile. |
| Geschlossenzelliger PE/EVA-Schaum | ca. 1 l Rohvolumen | €8–15 | [PE/EVA-Platten](https://www.modulor.de/platten/schaumstoff/pe-eva-weichschaumstoff/); schrittweise zuschneiden, nicht mit offenporigem Schaum starten. |
| 316/A4-M3/M4, Nyloc, Unterlegscheiben, Kabelbinder, TPU-Pads | 1 Satz | €25–40 | Standardhardware, elektrisch von CFK isolieren. Kabelbinder 4,8 mm; zwei pro Sattel. |
| Breite Actioncam-Tauchleuchte | 1 | €25–50 | Separat einschalten, dadurch keine weitere Durchführung. Beispiel: [Decathlon 1000 lm](https://www.decathlon.de/p/tauchlampe-1-000-lm-schwarz/336076/m8669338). Eine enge Spotlampe erzeugt Rückstreuung. |

### Realistische Kostenspanne

- **Empfohlene COTS-WTE-Version:** ungefähr **€620–820 geliefert**, ohne Laptop,
  Gamepad, LiPo-Lader und Vakuumpumpe.
- Größte Unsicherheit: konfigurierte WTE-Enden, Einfuhr/Versand, echte
  Kabeldurchführungen und lokaler Komponentenbestand.
- Ein geeigneter Balancer-Lader (€30–60) und Vakuumtestwerkzeug (€30–100) gehören
  in die Werkstattkosten, falls noch nicht vorhanden.

Das ist teurer als ein typisches RC-Auto, aber die vermeintlich billigen
Abkürzungen liegen ausgerechnet an Druckgrenze, Durchführung und reversibler
Unterwasserpropulsion. Dort wird nicht gespart.

## Thruster-/Steuerungsvarianten

| Variante | Mehr-/Minderkosten | Vorteil | Nachteil / Entscheidung |
|---|---:|---|---|
| Separate 2828 + Prop + gedruckter Schutz + PWM-ESC | Basis | Günstig, austauschbar, Standard-PWM | Motor-/Propellergeometrie und Strom/Schub müssen im Tank vermessen werden. **Gewählt.** |
| Komplettes [APISQUEEN U01-Set](https://www.underwaterthruster.com/products/apisqueen-12v-16v-2kg-thrust-u01-tow-set-brushless-underwater-thruster-propeller-with-bi-directional-control-esc-for-rov-boat) | etwa +US$160 gesamt | Weniger mechanische Integration | Rund US$105 je Set, Herstellerdaten bleiben zu validieren. Gute „weniger Basteln“-Option. |
| 3× [Blue Robotics T200](https://bluerobotics.com/store/thrusters/t100-t200-thrusters/t200-thruster-r2-rp/) + Basic ESC | etwa +US$650 | Reife Dokumentation, Ersatzteile, bekannte Kennfelder | Für 32-cm-ROV überdimensioniert und budgetwidrig. Premium-Option. |
| 4-in-1-Drohnen-ESC mit AM32/3D | potenziell −€20–40 | Sehr kompakt, ein Board | DShot/FC-Konfiguration, Kühlung und Rückwärtsbetrieb komplexer; nicht v0.1. |
| RC-Car-ESC mit Reverse | ähnlich/teurer | Leicht im RC-Handel erhältlich | Brems-/Rückwärtslogik und Neutralverzögerung sind für ROV-Mischer lästig; drei Einzelgeräte nötig. Nicht gewählt. |
| Pi/Pico-Stack | Basis | Klein, vollständig offen, zwei Watchdogs | Zunächst kein Heading-/Depth-Hold. **Gewählt.** |
| [ArduSub](https://ardupilot.org/sub/) + offiziell unterstützter Controller + BlueOS/Cockpit | +€230–400 | Reife Bedienung, Logs, Sensor-/Autopilotpfad | Höherer Preis und Bauraum; Upgrade nach mechanischer Validierung. |

## Optionale Oberflächenboje

Direktes WLAN/ELRS sitzt **oberhalb** der Wasserlinie. Eine kleine Boje enthält
einen [GL.iNet Opal](https://www.gl-inet.com/en-us/products/gl-sft1200/) (US$39,99)
und optional einen ELRS-Empfänger; nur ein 3–5-m-Tether geht zum ROV. Als Sender
eignet sich etwa der [RadioMaster Pocket ELRS](https://radiomasterrc.com/products/pocket-radio-controller-m2).
Diese Variante trennt den Piloten mechanisch vom Kabel, erhöht aber Teilezahl,
Fehlerstellen und Oberflächenwindangriff. Erst nach der direkten Tether-Version.
