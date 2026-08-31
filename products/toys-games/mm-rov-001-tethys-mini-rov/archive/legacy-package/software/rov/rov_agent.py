#!/usr/bin/env python3
"""Onboard UDP-to-Pico bridge with independent arming and stale-command failsafe."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import select
import socket
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from tethys_protocol import (  # noqa: E402
    CONTROL_PORT,
    TELEMETRY_PORT,
    ControlCommand,
    ProtocolError,
    mix_simple_rov3,
    parse_serial_frame,
    sequence_is_newer,
    serial_frame,
    telemetry_json,
    unpack_control,
)


class ArmGate:
    """Require a continuous neutral command before accepting an arm request."""

    def __init__(self, neutral_seconds: float = 1.5, neutral_band: int = 40):
        self.neutral_seconds = neutral_seconds
        self.neutral_band = neutral_band
        self._neutral_since: float | None = None
        self.armed = False

    def update(self, command: ControlCommand, now: float) -> bool:
        neutral = max(abs(command.surge), abs(command.yaw), abs(command.heave)) <= self.neutral_band
        if command.estop or not command.armed:
            self.disarm()
            return False
        if self.armed:
            return True
        if not neutral:
            self._neutral_since = None
            return False
        if self._neutral_since is None:
            self._neutral_since = now
        if now - self._neutral_since >= self.neutral_seconds:
            self.armed = True
        return self.armed

    def disarm(self) -> None:
        self.armed = False
        self._neutral_since = None


class PicoLink:
    def __init__(self, device: str, baud: int, dry_run: bool = False):
        self.dry_run = dry_run
        self.serial = None
        self.last_status = {"leak": False, "battery_mv": None, "pico_age_ms": None}
        if not dry_run:
            try:
                import serial  # type: ignore
            except ImportError as exc:
                raise SystemExit("pyserial is required unless --dry-run is used") from exc
            self.serial = serial.Serial(device, baudrate=baud, timeout=0, write_timeout=0.1)

    def send(self, sequence: int, armed: bool, outputs: tuple[int, int, int]) -> None:
        left, right, vertical = outputs if armed else (0, 0, 0)
        frame = serial_frame(f"C,{sequence & 0xFFFFFFFF},{int(armed)},{left},{right},{vertical}")
        if self.serial is not None:
            self.serial.write(frame)

    def poll(self) -> dict[str, object]:
        if self.serial is None:
            return self.last_status
        while self.serial.in_waiting:
            line = self.serial.readline()
            try:
                fields = parse_serial_frame(line).split(",")
                if len(fields) == 4 and fields[0] == "T":
                    self.last_status = {
                        "pico_age_ms": int(fields[1]),
                        "leak": bool(int(fields[2])),
                        "battery_mv": int(fields[3]),
                    }
            except (ProtocolError, ValueError):
                continue
        return self.last_status

    def close(self) -> None:
        try:
            self.send(0, False, (0, 0, 0))
        finally:
            if self.serial is not None:
                self.serial.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--controller-ip", default=None)
    parser.add_argument("--serial", default="/dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--watchdog-ms", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    watchdog_s = args.watchdog_ms / 1000.0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.bind, CONTROL_PORT))
    sock.setblocking(False)
    pico = PicoLink(args.serial, args.baud, args.dry_run)
    gate = ArmGate()
    last_rx = 0.0
    last_seq: int | None = None
    controller: tuple[str, int] | None = None
    last_telemetry = 0.0
    command = ControlCommand(sequence=0)

    try:
        while True:
            now = time.monotonic()
            readable, _, _ = select.select([sock], [], [], 0.02)
            if readable:
                packet, source = sock.recvfrom(256)
                if args.controller_ip and source[0] != args.controller_ip:
                    continue
                try:
                    candidate = unpack_control(packet)
                except ProtocolError:
                    continue
                if last_seq is not None and not sequence_is_newer(candidate.sequence, last_seq):
                    continue
                command, last_seq, last_rx, controller = candidate, candidate.sequence, now, source

            status = pico.poll()
            stale = now - last_rx > watchdog_s
            leak = bool(status.get("leak", False))
            if stale or leak:
                gate.disarm()
            armed = False if stale or leak else gate.update(command, now)
            outputs = mix_simple_rov3(command.surge, command.yaw, command.heave) if armed else (0, 0, 0)
            pico.send(command.sequence, armed, outputs)

            if controller and now - last_telemetry >= 0.2:
                last_telemetry = now
                data = telemetry_json(
                    version=1,
                    armed=armed,
                    stale=stale,
                    leak=leak,
                    battery_mv=status.get("battery_mv"),
                    outputs=outputs,
                    sequence=last_seq,
                )
                sock.sendto(data, (controller[0], TELEMETRY_PORT))
    except KeyboardInterrupt:
        return 0
    finally:
        pico.close()
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
