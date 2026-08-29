import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software" / "common"))
sys.path.insert(0, str(ROOT / "software" / "rov"))

from tethys_protocol import (  # noqa: E402
    ControlCommand,
    ProtocolError,
    mix_simple_rov3,
    pack_control,
    parse_serial_frame,
    sequence_is_newer,
    serial_frame,
    unpack_control,
)
from rov_agent import ArmGate  # noqa: E402


class ProtocolTests(unittest.TestCase):
    def test_control_roundtrip(self):
        original = ControlCommand(42, 1200, -1200, 123, armed=True)
        decoded = unpack_control(pack_control(original))
        self.assertEqual(decoded, ControlCommand(42, 1000, -1000, 123, armed=True))

    def test_crc_rejects_corruption(self):
        packet = bytearray(pack_control(ControlCommand(1, 100)))
        packet[9] ^= 0x01
        with self.assertRaises(ProtocolError):
            unpack_control(bytes(packet))

    def test_mixer_normalizes(self):
        self.assertEqual(mix_simple_rov3(1000, 1000, 0), (1000, 0, 0))
        self.assertEqual(mix_simple_rov3(500, -500, 200), (0, 1000, 200))

    def test_sequence_wrap(self):
        self.assertTrue(sequence_is_newer(0, 0xFFFFFFFF))
        self.assertFalse(sequence_is_newer(10, 10))

    def test_serial_roundtrip(self):
        self.assertEqual(parse_serial_frame(serial_frame("C,1,0,0,0,0")), "C,1,0,0,0,0")

    def test_arm_gate_needs_neutral_time(self):
        gate = ArmGate(neutral_seconds=1.5)
        command = ControlCommand(1, armed=True)
        self.assertFalse(gate.update(command, 10.0))
        self.assertFalse(gate.update(command, 11.4))
        self.assertTrue(gate.update(command, 11.5))
        self.assertFalse(gate.update(ControlCommand(2, estop=True), 11.6))


if __name__ == "__main__":
    unittest.main()
