# Tethys Mini ROV v0.1

Ein kleiner, modularer 3-Thruster-ROV für beaufsichtigte Maker- und Pooltests. Das
Konzept kombiniert einen geprüften 75-mm-COTS-Druckkörper, 10×8-mm-CFK/GFK-Rohre,
druckbare PETG-Halter und Propellerschützer sowie eine offene Pi/Pico-Steuerung.

![Layout](assets/tethys_mini_layout.png)

## Was enthalten ist

- `docs/RESEARCH_AND_DESIGN.md` – Recherche, Architektur, Entscheidungen und Quellen
- `docs/BOM.md` – beschaffbare Budgetkomponenten und Alternativen
- `docs/BUILD_AND_TEST.md` – Bau-, Dichtigkeits-, Trim- und Inbetriebnahmeplan
- `docs/FDM_VARIANTS.md` – Baseline/Kandidaten und noch offene A/B-Nachweise
- `cad/generate_parts.py` – parametrischer STL-Generator ohne CAD-Lizenzkosten
- `cad/stl/` – geprüfte, druckfertige Referenz-STLs plus Mesh-Manifest
- `software/` – Topside-Pilot, Pi-Agent, Pico-Firmware, Video- und Service-Dateien
- `config/fdm_plan.json` – nominale FDM-Pfadplanung für 0,6-mm-Düse

## Zielkonfiguration

| Merkmal | v0.1 |
|---|---|
| Abmessungen | ca. 320 × 240 × 180 mm |
| Freiheitsgrade | Vor/zurück, Gieren, Auf/Ab |
| Thruster | 2 horizontal + 1 vertikal |
| Kommunikation | 5–10 m Ethernet-Daten-Tether; optional WLAN-Boje |
| Energie | 3S-LiPo 2200 mAh an Bord |
| Elektronik | Raspberry Pi Zero 2 W + Pico 2 |
| Zielumgebung | zunächst klares, ruhiges Süßwasser; 0,5–1 m Testtiefe |
| Ausbauziel | nach bestandenen Tests höchstens 3 m; keine CAD-Druckfreigabe |

## Sofortstart am Schreibtisch

```bash
python3 -m unittest discover -s tests -v
python3 cad/generate_parts.py
python3 software/rov/rov_agent.py --dry-run
```

Die Hardware wird erst nach den in `docs/BUILD_AND_TEST.md` definierten Gates mit
montierten Propellern und im Wasser betrieben.

## Wichtiger Status

Dies ist ein validierbarer Engineering-Entwurf, aber **kein zertifiziertes
Spielzeug, kein Personentransportmittel und keine druckgeprüfte Baugruppe**. Die
WTE-, Motor-, Propeller- und Kabelrevisionen müssen vor Fertigung nachgemessen
werden. LiPo, Propeller und Wasser erfordern erwachsene Aufsicht.
