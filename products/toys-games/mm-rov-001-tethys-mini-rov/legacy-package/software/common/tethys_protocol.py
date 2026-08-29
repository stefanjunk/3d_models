"""Tethys Mini ROV wire protocol and 3-thruster mixer.

The topside control packet is intentionally fixed-size and stateless.  A stale
packet can never keep a thruster running because both the Linux agent and the
Pico enforce independent watchdogs.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import struct
import zlib

MAGIC = b"THY1"
VERSION = 1
CONTROL_PORT = 5005
TELEMETRY_PORT = 5006
VIDEO_PORT = 8888

FLAG_ARM = 0x01
FLAG_ESTOP = 0x02

_CONTROL_NO_CRC = struct.Struct("!4sBBIhhh")
_CONTROL = struct.Struct("!4sBBIhhhI")


class ProtocolError(ValueError):
    """Raised for malformed, incompatible, or corrupted packets."""


def _axis(value: int | float) -> int:
    return max(-1000, min(1000, int(round(value))))


@dataclass(frozen=True)
class ControlCommand:
    sequence: int
    surge: int = 0
    yaw: int = 0
    heave: int = 0
    armed: bool = False
    estop: bool = False

    def normalized(self) -> "ControlCommand":
        return ControlCommand(
            sequence=self.sequence & 0xFFFFFFFF,
            surge=_axis(self.surge),
            yaw=_axis(self.yaw),
            heave=_axis(self.heave),
            armed=bool(self.armed),
            estop=bool(self.estop),
        )


def pack_control(command: ControlCommand) -> bytes:
    command = command.normalized()
    flags = (FLAG_ARM if command.armed else 0) | (FLAG_ESTOP if command.estop else 0)
    body = _CONTROL_NO_CRC.pack(
        MAGIC,
        VERSION,
        flags,
        command.sequence,
        command.surge,
        command.yaw,
        command.heave,
    )
    return body + struct.pack("!I", zlib.crc32(body) & 0xFFFFFFFF)


def unpack_control(packet: bytes) -> ControlCommand:
    if len(packet) != _CONTROL.size:
        raise ProtocolError(f"expected {_CONTROL.size} bytes, got {len(packet)}")
    magic, version, flags, sequence, surge, yaw, heave, received_crc = _CONTROL.unpack(packet)
    if magic != MAGIC:
        raise ProtocolError("wrong packet magic")
    if version != VERSION:
        raise ProtocolError(f"unsupported protocol version {version}")
    expected_crc = zlib.crc32(packet[:-4]) & 0xFFFFFFFF
    if received_crc != expected_crc:
        raise ProtocolError("CRC mismatch")
    return ControlCommand(
        sequence=sequence,
        surge=surge,
        yaw=yaw,
        heave=heave,
        armed=bool(flags & FLAG_ARM),
        estop=bool(flags & FLAG_ESTOP),
    ).normalized()


def mix_simple_rov3(surge: int | float, yaw: int | float, heave: int | float) -> tuple[int, int, int]:
    """Mix surge/yaw/heave to left, right, and vertical thruster commands.

    All outputs are normalized to [-1000, 1000] while preserving the requested
    left/right ratio.  Swap a motor's two phase wires or invert that output in
    configuration if its physical direction is opposite.
    """
    left = float(surge) + float(yaw)
    right = float(surge) - float(yaw)
    vertical = float(heave)
    scale = max(1.0, abs(left) / 1000.0, abs(right) / 1000.0, abs(vertical) / 1000.0)
    return _axis(left / scale), _axis(right / scale), _axis(vertical / scale)


def apply_limit(value: int | float, limit: float) -> int:
    if not 0.0 <= limit <= 1.0:
        raise ValueError("limit must be between 0 and 1")
    return _axis(float(value) * limit)


def sequence_is_newer(candidate: int, previous: int) -> bool:
    """32-bit wrap-safe monotonic sequence comparison."""
    delta = (candidate - previous) & 0xFFFFFFFF
    return 0 < delta < 0x80000000


def crc16_ccitt(data: bytes, initial: int = 0xFFFF) -> int:
    crc = initial
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def serial_frame(payload: str) -> bytes:
    raw = payload.encode("ascii")
    return raw + f"*{crc16_ccitt(raw):04X}\n".encode("ascii")


def parse_serial_frame(line: bytes | str) -> str:
    if isinstance(line, str):
        line = line.encode("ascii")
    line = line.strip()
    try:
        payload, checksum = line.rsplit(b"*", 1)
        received = int(checksum, 16)
    except (ValueError, TypeError) as exc:
        raise ProtocolError("malformed serial frame") from exc
    if crc16_ccitt(payload) != received:
        raise ProtocolError("serial CRC mismatch")
    return payload.decode("ascii")


def telemetry_json(**fields: object) -> bytes:
    return (json.dumps(fields, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
