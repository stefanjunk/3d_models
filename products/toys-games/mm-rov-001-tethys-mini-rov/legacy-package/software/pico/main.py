"""MicroPython firmware for Raspberry Pi Pico/Pico 2.

Outputs standard 50 Hz reversible-ESC PWM.  GPIO assignments are deliberately
simple so the controller can be assembled on perfboard.
"""

from machine import ADC, Pin, PWM
import sys
import time
import uselect

PWM_PINS = (2, 3, 4)  # left, right, vertical
LEAK_PIN = 15         # normally high; wet pads/transistor pull low
BATTERY_PIN = 26      # ADC0, through 100k/33k divider
WATCHDOG_MS = 300
ESC_BOOT_NEUTRAL_MS = 2500
TELEMETRY_MS = 200
NEUTRAL_US = 1500
SPAN_US = 500


def crc16_ccitt(data, initial=0xFFFF):
    crc = initial
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def parse_frame(line):
    line = line.strip()
    if not line or b"*" not in line:
        return None
    payload, checksum = line.rsplit(b"*", 1)
    try:
        received = int(checksum, 16)
    except ValueError:
        return None
    if crc16_ccitt(payload) != received:
        return None
    try:
        return payload.decode("ascii").split(",")
    except Exception:
        return None


def emit(payload):
    raw = payload.encode("ascii")
    sys.stdout.write("{}*{:04X}\n".format(payload, crc16_ccitt(raw)))


def pulse_us(pwm, value):
    value = max(1000, min(2000, int(value)))
    pwm.duty_u16(value * 65535 // 20000)


def command_to_us(value):
    value = max(-1000, min(1000, int(value)))
    return NEUTRAL_US + value * SPAN_US // 1000


pwms = [PWM(Pin(pin)) for pin in PWM_PINS]
for pwm in pwms:
    pwm.freq(50)
    pulse_us(pwm, NEUTRAL_US)

leak_input = Pin(LEAK_PIN, Pin.IN, Pin.PULL_UP)
battery_adc = ADC(BATTERY_PIN)
poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)
boot_ms = time.ticks_ms()
last_valid_ms = boot_ms
last_telemetry_ms = boot_ms
last_sequence = 0

while True:
    now = time.ticks_ms()
    leak = leak_input.value() == 0
    stale = time.ticks_diff(now, last_valid_ms) > WATCHDOG_MS

    if poller.poll(0):
        fields = parse_frame(sys.stdin.buffer.readline())
        if fields and len(fields) == 6 and fields[0] == "C":
            try:
                sequence = int(fields[1])
                armed = bool(int(fields[2]))
                values = [int(value) for value in fields[3:6]]
            except ValueError:
                fields = None
            if fields is not None:
                last_valid_ms = now
                last_sequence = sequence
                ready = time.ticks_diff(now, boot_ms) >= ESC_BOOT_NEUTRAL_MS
                if armed and ready and not leak:
                    for pwm, value in zip(pwms, values):
                        pulse_us(pwm, command_to_us(value))
                else:
                    for pwm in pwms:
                        pulse_us(pwm, NEUTRAL_US)

    if stale or leak:
        for pwm in pwms:
            pulse_us(pwm, NEUTRAL_US)

    if time.ticks_diff(now, last_telemetry_ms) >= TELEMETRY_MS:
        last_telemetry_ms = now
        # 3.3 V ADC, 100k/33k divider. Calibrate the multiplier on the finished board.
        battery_mv = battery_adc.read_u16() * 3300 * 133 // (65535 * 33)
        age_ms = max(0, time.ticks_diff(now, last_valid_ms))
        emit("T,{},{},{}".format(age_ms, int(leak), battery_mv))
    time.sleep_ms(5)
