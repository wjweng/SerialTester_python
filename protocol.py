
"""Helpers for parsing responses from the MCU protocol."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, Callable
from enum import Enum, auto


class Command(Enum):
    """Commands that can be sent to the controller."""
    PAN_TYPE = auto()
    VERSION = auto()
    MCU_TYPE = auto()
    SPEED_PPS = auto()
    CURRENT_SPEED = auto()
    ACC_LEVEL = auto()
    SPEED_ZOOM = auto()
    ACC_VALUE = auto()
    POSITION = auto()
    ANGLE = auto()
    AB_COUNT = auto()
    Z_COUNT = auto()
    ZP_STATUS = auto()
    LOCK_STATUS = auto()


def _nibble_value(packet: bytes, start: int) -> int:
    """Convert four nibbles starting at *start* into an integer."""
    return ((packet[start] & 0x0F) << 12) | ((packet[start + 1] & 0x0F) << 8) |\
           ((packet[start + 2] & 0x0F) << 4) | (packet[start + 3] & 0x0F)


@dataclass
class ParseResult:
    """Result returned from :func:`ProtocolParser.parse`."""
    type: Command
    value: Any


class ProtocolParser:
    """Parse packets returned by the controller.

    This helper isolates the byte level processing so the UI code only deals
    with high level results.
    """

    def __init__(self):
        self._parsers: dict[Command, Callable[[bytes], Any]] = {
            Command.PAN_TYPE: self._parse_pan_type,
            Command.VERSION: self._parse_version,
            Command.MCU_TYPE: self._parse_mcu_type,
            Command.SPEED_PPS: self._parse_speed_pps,
            Command.CURRENT_SPEED: self._parse_current_speed,
            Command.ACC_LEVEL: self._parse_acc_level,
            Command.SPEED_ZOOM: self._parse_speed_zoom,
            Command.ACC_VALUE: self._parse_acc_value,
            Command.POSITION: self._parse_position,
            Command.ANGLE: self._parse_angle,
            Command.AB_COUNT: self._parse_ab_count,
            Command.Z_COUNT: self._parse_z_count,
            Command.ZP_STATUS: self._parse_zp_status,
            Command.LOCK_STATUS: self._parse_lock_status,
        }

    def parse(self, packet: bytes, pending_cmd: Optional[Command]) -> Optional[ParseResult]:
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

        if pending_cmd in self._parsers:
            parser = self._parsers[pending_cmd]
            value = parser(packet)
            if value is not None:
                return ParseResult(pending_cmd, value)

        return None

    def _parse_pan_type(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 3:
            return packet[2] & 0x03
        return None

    def _parse_version(self, packet: bytes) -> Optional[str]:
        if len(packet) >= 8:
            p5 = f"0{packet[5]}" if packet[5] < 10 else str(packet[5])
            p6 = f"0{packet[6]}" if packet[6] < 10 else str(packet[6])
            p7 = f"0{packet[7]}" if packet[7] < 10 else str(packet[7])
            return f"{2000 + packet[4]}{p5}{p6}-{p7}"
        return None

    def _parse_mcu_type(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 3:
            return packet[2] & 0x01
        return None

    def _parse_speed_pps(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return _nibble_value(packet, 2)
        return None

    def _parse_current_speed(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return _nibble_value(packet, 2)
        return None

    def _parse_acc_level(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 3:
            return (packet[2] & 0x0F) - 1
        return None

    def _parse_speed_zoom(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 3:
            return packet[2]
        return None

    def _parse_acc_value(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return _nibble_value(packet, 2)
        return None

    def _parse_position(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return _nibble_value(packet, 2)
        return None

    def _parse_angle(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return _nibble_value(packet, 2)
        return None

    def _parse_ab_count(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return _nibble_value(packet, 2)
        return None

    def _parse_z_count(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return _nibble_value(packet, 2)
        return None

    def _parse_zp_status(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return packet[5] & 0x01
        return None

    def _parse_lock_status(self, packet: bytes) -> Optional[int]:
        if len(packet) >= 6:
            return packet[5] & 0x01
        return None

