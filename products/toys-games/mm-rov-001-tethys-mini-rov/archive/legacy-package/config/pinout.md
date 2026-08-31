# Pico- und Leistungs-Pinout

| Signal | Pico-Pin | Verbindung |
|---|---:|---|
| PWM links | GPIO2 | ESC links Signal |
| PWM rechts | GPIO3 | ESC rechts Signal |
| PWM vertikal | GPIO4 | ESC vertikal Signal |
| Leck, active-low | GPIO15 | Open-collector/Komparator, interner Pull-up |
| Batteriespannung | GPIO26 / ADC0 | 100 kΩ oben, 33 kΩ unten, 100 nF nach GND |
| USB | Micro-USB | Pi USB-Hub, 115200 Baud |
| Masse | GND | Pico, ESC-Signalmasse, BEC gemeinsam |

Der 100k/33k-Teiler ergibt bei 12,6 V nominal etwa 3,13 V. Widerstandstoleranz
und Pico-ADC müssen gegen ein Multimeter kalibriert werden. Die Hochstrommasse
wird sternförmig am Verteiler geführt; ESC-Motorleitungen nicht parallel zur
Kameraflachbandleitung verlegen.
