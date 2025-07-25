"""Helpers for parsing responses from the MCU protocol."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any


def _nibble_value(packet: bytes, start: int) -> int:
    """Convert four nibbles starting at *start* into an integer."""
    return ((packet[start] & 0x0F) << 12) | ((packet[start + 1] & 0x0F) << 8) |\
           ((packet[start + 2] & 0x0F) << 4) | (packet[start + 3] & 0x0F)


@dataclass
class ParseResult:
    """Result returned from :func:`ProtocolParser.parse`."""
    type: str
    value: Any


class ProtocolParser:
    """Parse packets returned by the controller.

    This helper isolates the byte level processing so the UI code only deals
    with high level results.
    """

    @staticmethod
    def parse(packet: bytes, pending_cmd: Optional[str]) -> Optional[ParseResult]:
        """Parse *packet* assuming it is a reply for *pending_cmd*.

        Parameters
        ----------
        packet:
            Raw packet ending with ``0xFF``.
        pending_cmd:
            Identifier of the command awaiting a reply.

        Returns
        -------
        ParseResult or ``None``
            ``None`` is returned when the packet does not contain a complete or
            recognised response for ``pending_cmd``.
        """
        if not packet or packet[-1] != 0xFF:
            return None

        if pending_cmd == 'pan_type' and len(packet) >= 3:
            return ParseResult('pan_type', packet[2] & 0x03)
        if pending_cmd == 'version' and len(packet) >= 8:
            p5 = f"0{packet[5]}" if packet[5] < 10 else str(packet[5])
            p6 = f"0{packet[6]}" if packet[6] < 10 else str(packet[6])
            p7 = f"0{packet[7]}" if packet[7] < 10 else str(packet[7])
            ver = f"{2000 + packet[4]}{p5}{p6}-{p7}"
            return ParseResult('version', ver)
        if pending_cmd == 'mcu_type' and len(packet) >= 3:
            return ParseResult('mcu_type', packet[2] & 0x01)
        if pending_cmd == 'speed_pps' and len(packet) >= 6:
            return ParseResult('speed_pps', _nibble_value(packet, 2))
        if pending_cmd == 'current_speed' and len(packet) >= 6:
            return ParseResult('current_speed', _nibble_value(packet, 2))
        if pending_cmd == 'acc_level' and len(packet) >= 3:
            return ParseResult('acc_level', (packet[2] & 0x0F) - 1)
        if pending_cmd == 'speed_zoom' and len(packet) >= 3:
            return ParseResult('speed_zoom', packet[2])
        if pending_cmd == 'acc_value' and len(packet) >= 6:
            return ParseResult('acc_value', _nibble_value(packet, 2))
        if pending_cmd == 'position' and len(packet) >= 6:
            return ParseResult('position', _nibble_value(packet, 2))
        if pending_cmd == 'angle' and len(packet) >= 6:
            return ParseResult('angle', _nibble_value(packet, 2))
        if pending_cmd == 'ab_count' and len(packet) >= 6:
            return ParseResult('ab_count', _nibble_value(packet, 2))
        if pending_cmd == 'z_count' and len(packet) >= 6:
            return ParseResult('z_count', _nibble_value(packet, 2))
        if pending_cmd == 'zp_status' and len(packet) >= 6:
            return ParseResult('zp_status', packet[5] & 0x01)
        if pending_cmd == 'lock_status' and len(packet) >= 6:
            return ParseResult('lock_status', packet[5] & 0x01)
        return None
