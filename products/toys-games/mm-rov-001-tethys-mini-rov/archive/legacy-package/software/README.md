# Software-Setup

## Netzwerk

- Topside-Laptop: `192.168.2.1/24`
- ROV/Pi-Ethernet: `192.168.2.2/24`
- Steuerung: UDP 5005, Telemetrie: UDP 5006, Video: TCP 8888
- WLAN des Pi im Einsatz deaktivieren oder nur für Werkbank-SSH verwenden; es
  ist unter Wasser kein Steuerlink.

Die Datei `systemd/10-tethys.network` ist ein Beispiel für systemd-networkd.
Bei Raspberry Pi OS NetworkManager stattdessen eine statische Kabelverbindung
mit gleicher Adresse anlegen.

## Pi installieren

```bash
sudo useradd --system --create-home --groups dialout,video rov
sudo mkdir -p /opt/tethys-mini
sudo cp -r software /opt/tethys-mini/
sudo chown -R rov:rov /opt/tethys-mini
sudo -u rov python3 -m venv /opt/tethys-mini/.venv
sudo -u rov /opt/tethys-mini/.venv/bin/pip install -r /opt/tethys-mini/software/requirements-rov.txt
sudo cp software/systemd/tethys-agent.service /etc/systemd/system/
sudo cp software/systemd/tethys-video.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tethys-agent tethys-video
```

Vorher `rov_agent.py --dry-run` ausführen. Den echten Dienst erst propellerlos
aktivieren und den Pico-Gerätenamen (`/dev/ttyACM0`) kontrollieren. Falls bereits
ein normaler Pi-Benutzer verwendet wird, die `User=`-/`Group=`-Zeilen der Units
entsprechend anpassen, statt einen zweiten Benutzer anzulegen.

## Pico flashen

1. Aktuelles MicroPython für Pico/Pico 2 aufspielen.
2. `pico/main.py` als `main.py` auf das Board kopieren.
3. PWM-Pins 2/3/4 und Leck-Pin 15 ohne ESCs elektrisch prüfen.
4. Danach ESC-Signalleitungen mit gemeinsamer Signalmasse anschließen.

## Topside

```bash
python3 -m venv .venv
.venv/bin/pip install -r software/requirements-topside.txt
.venv/bin/python software/topside/pilot.py 192.168.2.2 --limit 0.35
```

Video:

```bash
ffplay tcp://192.168.2.2:8888 -fflags nobuffer -flags low_delay -framedrop
```

Die Video-Service-Datei nutzt MPEG-TS, weil aktuelle VLC-Versionen damit
zuverlässiger umgehen als mit nacktem H.264. Alternativ:

```bash
vlc tcp://192.168.2.2:8888
```

## Bedienung

| Funktion | Tastatur | typischer Xbox-Controller |
|---|---|---|
| Vor/Zurück | W/S oder Pfeil hoch/runter | linker Stick Y |
| Gieren | A/D oder Pfeil links/rechts | linker Stick X |
| Auf/Ab | R/F | rechter Stick Y |
| Armen | Shift+Enter 2 s, Sticks neutral | LB+RB 2 s, Sticks neutral |
| Disarm/E-Stop | Leertaste/Escape | B |

Das Armen wird danach vom Pi noch einmal für 1,5 s neutral bestätigt. Der
Standardleistungsfaktor ist 35 %.

## Tests

```bash
python3 -m unittest discover -s tests -v
python3 software/rov/rov_agent.py --dry-run
```

Die Unit-Tests prüfen Paket-CRC, Sequenz-Wrap, Mischer, Serial-CRC und Arm-Gate.
Hardware-Watchdogs und PWM müssen zusätzlich real gemessen werden.
