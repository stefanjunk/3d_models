#!/usr/bin/env python3
"""Minimal gamepad/keyboard pilot client for Tethys Mini."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import socket
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from tethys_protocol import (  # noqa: E402
    CONTROL_PORT,
    TELEMETRY_PORT,
    ControlCommand,
    apply_limit,
    pack_control,
)


def shape_axis(raw: float, deadband: float = 0.10, expo: float = 0.35) -> int:
    if abs(raw) <= deadband:
        return 0
    value = (abs(raw) - deadband) / (1.0 - deadband)
    value = (1.0 - expo) * value + expo * value**3
    return int(round((1 if raw >= 0 else -1) * value * 1000))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rov_ip")
    parser.add_argument("--limit", type=float, default=0.35, help="initial power limit, 0..1")
    args = parser.parse_args()
    if not 0.0 < args.limit <= 1.0:
        parser.error("--limit must be >0 and <=1")

    try:
        import pygame
    except ImportError as exc:
        raise SystemExit("Install pygame: python3 -m pip install pygame") from exc

    pygame.init()
    pygame.joystick.init()
    screen = pygame.display.set_mode((760, 300))
    pygame.display.set_caption("Tethys Mini Pilot")
    font = pygame.font.SysFont("monospace", 20)
    joystick = None
    if pygame.joystick.get_count():
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx.bind(("0.0.0.0", TELEMETRY_PORT))
    rx.setblocking(False)
    target = (args.rov_ip, CONTROL_PORT)
    sequence = 0
    arm_hold_since = None
    arm_requested = False
    estop_pulse = False
    telemetry = {"status": "noch keine Telemetrie"}
    running = True
    clock = pygame.time.Clock()

    while running:
        now = time.monotonic()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                arm_requested = False
                estop_pulse = True

        keys = pygame.key.get_pressed()
        surge_raw = float(keys[pygame.K_w] or keys[pygame.K_UP]) - float(keys[pygame.K_s] or keys[pygame.K_DOWN])
        yaw_raw = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(keys[pygame.K_a] or keys[pygame.K_LEFT])
        heave_raw = float(keys[pygame.K_r]) - float(keys[pygame.K_f])
        arm_combo = bool(keys[pygame.K_LSHIFT] and keys[pygame.K_RETURN])

        if joystick is not None:
            surge_raw += -joystick.get_axis(1)
            yaw_raw += joystick.get_axis(0)
            heave_raw += -joystick.get_axis(3 if joystick.get_numaxes() > 3 else 1)
            arm_combo = arm_combo or (
                joystick.get_numbuttons() > 5 and joystick.get_button(4) and joystick.get_button(5)
            )
            if joystick.get_numbuttons() > 1 and joystick.get_button(1):
                arm_requested = False
                estop_pulse = True

        surge = shape_axis(max(-1.0, min(1.0, surge_raw)))
        yaw = shape_axis(max(-1.0, min(1.0, yaw_raw)))
        heave = shape_axis(max(-1.0, min(1.0, heave_raw)))
        neutral = max(abs(surge), abs(yaw), abs(heave)) < 40

        if arm_combo and neutral and not arm_requested:
            if arm_hold_since is None:
                arm_hold_since = now
            elif now - arm_hold_since >= 2.0:
                arm_requested = True
        else:
            arm_hold_since = None

        sequence = (sequence + 1) & 0xFFFFFFFF
        command = ControlCommand(
            sequence=sequence,
            surge=apply_limit(surge, args.limit),
            yaw=apply_limit(yaw, args.limit),
            heave=apply_limit(heave, args.limit),
            armed=arm_requested,
            estop=estop_pulse,
        )
        tx.sendto(pack_control(command), target)
        estop_pulse = False

        while True:
            try:
                telemetry = json.loads(rx.recv(4096).decode("utf-8"))
            except BlockingIOError:
                break
            except (ValueError, UnicodeDecodeError):
                continue

        screen.fill((8, 20, 28))
        colour = (70, 220, 130) if telemetry.get("armed") else (255, 185, 70)
        lines = [
            f"ROV {args.rov_ip}   Limit {args.limit:.0%}   {'ARMED' if telemetry.get('armed') else 'SAFE'}",
            f"surge {command.surge:+5d}   yaw {command.yaw:+5d}   heave {command.heave:+5d}",
            f"leak={telemetry.get('leak')} stale={telemetry.get('stale')} battery={telemetry.get('battery_mv')} mV",
            "ARM: Shift+Enter 2 s oder LB+RB 2 s | E-STOP: Space/Esc oder B",
            "Tasten: W/S vor/zurueck, A/D drehen, R/F auf/ab",
        ]
        for index, line in enumerate(lines):
            screen.blit(font.render(line, True, colour if index == 0 else (205, 225, 235)), (20, 24 + index * 48))
        pygame.display.flip()
        clock.tick(25)

    for _ in range(5):
        sequence = (sequence + 1) & 0xFFFFFFFF
        tx.sendto(pack_control(ControlCommand(sequence=sequence, estop=True)), target)
        time.sleep(0.02)
    tx.close()
    rx.close()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
