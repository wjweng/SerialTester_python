# New file: pan_tilt_controller.py
"""High level controller for pan/tilt units."""

from __future__ import annotations

from PyQt5 import QtCore, QtWidgets
from typing import Callable, Optional

from serial_comm import SerialComm
from protocol import ProtocolParser, ParseResult, Command


# --- Command Definitions ----------------------------------------------------
CMD_ABS_STOP = bytes([0x81, 0x01, 0x06, 0x02, 0x00, 0x00, 0xFF])
CMD_ABS_ANGLE_STOP = bytes([0x81, 0x01, 0x06, 0x06, 0x00, 0x00, 0xFF])
CMD_REL_STOP = bytes([0x81, 0x01, 0x06, 0x03, 0x00, 0x00, 0xFF])
CMD_GET_SPEED = bytes([0x81, 0xD9, 0x06, 0x03, 0xFF])
CMD_GET_VERSION = bytes([0x81, 0x09, 0x00, 0x02, 0xFF])
CMD_GET_MCU_TYPE = bytes([0x81, 0x09, 0x00, 0x03, 0xFF])
CMD_GET_PAN_TYPE = bytes([0x81, 0xD9, 0x06, 0x02, 0xFF])
CMD_STOP = bytes([0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x03, 0x03, 0xFF])
CMD_STALL_CALI_ON = bytes([0x81, 0xD1, 0x06, 0x05, 0x02, 0xFF])
CMD_STALL_CALI_OFF = bytes([0x81, 0xD1, 0x06, 0x05, 0x03, 0xFF])
CMD_ZERO_CALI_PLUS = bytes([0x81, 0x01, 0x06, 0x05, 0x01, 0x00, 0xFF])
CMD_ZERO_CALI_MINUS = bytes([0x81, 0x01, 0x06, 0x05, 0x01, 0x02, 0xFF])
CMD_CLEAR_ZERO_CALI = bytes([0x81, 0x01, 0x06, 0x05, 0x00, 0xFF])
CMD_ZERO_CALI_STATUS = bytes([0x81, 0xD9, 0x05, 0x55, 0xFF])
CMD_LOCK_HOME = bytes([0x81, 0x01, 0x06, 0x04, 0x01, 0xFF])
CMD_UNLOCK_HOME = bytes([0x81, 0x01, 0x06, 0x04, 0x00, 0xFF])
CMD_LOCK_STATUS = bytes([0x81, 0xD9, 0x05, 0x56, 0xFF])
CMD_GO_HOME = bytes([0x81, 0x01, 0x06, 0x04, 0xFF])
CMD_GET_SPEED_BY_ZOOM = bytes([0x81, 0x09, 0x06, 0xA2, 0xFF])
CMD_SPEED_BY_ZOOM_OFF = bytes([0x81, 0x01, 0x06, 0xA2, 0x03, 0xFF])
CMD_GET_ACCELERATION = bytes([0x81, 0xD9, 0x06, 0x01, 0xFF])
CMD_GET_ACC_LEVEL = bytes([0x81, 0x09, 0x06, 0x31, 0xFF])
CMD_GET_POSITION = bytes([0x81, 0x09, 0x06, 0x12, 0xFF])
CMD_GET_ANGLE = bytes([0x81, 0xD9, 0x05, 0x51, 0xFF])
CMD_GET_AB_COUNT = bytes([0x81, 0xD9, 0x05, 0x52, 0xFF])
CMD_GET_Z_COUNT = bytes([0x81, 0xD9, 0x05, 0x53, 0xFF])
CMD_MAX_ANGLE_ON = bytes([0x81, 0x01, 0x06, 0x66, 0x02, 0xFF])
CMD_MAX_ANGLE_OFF = bytes([0x81, 0x01, 0x06, 0x66, 0x03, 0xFF])
CMD_MOTOR_TYPE_0P9D = bytes([0x81, 0x01, 0x00, 0x03, 0x00, 0xFF])
CMD_MOTOR_TYPE_1P8D = bytes([0x81, 0x01, 0x00, 0x03, 0x01, 0xFF])


class PanTiltController(QtWidgets.QWidget):
    """Wrap :class:`SerialComm` with higher level command helpers."""
    data_received = QtCore.pyqtSignal(bytes)

    def __init__(self, comm: Optional[SerialComm] = None) -> None:
        super().__init__()
        self.comm: Optional[SerialComm] = comm
        if self.comm is not None:
            # ensure we get callbacks from the SerialComm instance
            self.comm.on_rx_char = self._on_rx
        self.parser = ProtocolParser()
        self.buffer = bytearray()
        self.pending_cmd: Optional[Command] = None
        self.on_result: Callable[[ParseResult], None] = lambda res: None
        
        # callback invoked whenever data is transmitted
        self.on_tx: Callable[[bytes], None] = lambda data: None

    # --- serial management -------------------------------------------------
    def open(self) -> None:
        if self.comm is not None:
            self.comm.open()

    def close(self) -> None:
        if self.comm is not None:
            self.comm.close()

    def set_comm(self, comm: Optional[SerialComm]) -> None:
        """Assign a new :class:`SerialComm` instance."""
        self.comm = comm
        if self.comm is not None:
            self.comm.on_rx_char = self._on_rx

    # --- internal helpers --------------------------------------------------
    def _on_rx(self, data: bytes) -> None:
        """Handle incoming data from :class:`SerialComm`."""
        # forward raw data first
        self.data_received.emit(data)
        self.buffer.extend(data)
        while 0xFF in self.buffer:
            idx = self.buffer.index(0xFF)
            packet = bytes(self.buffer[:idx + 1])
            del self.buffer[:idx + 1]
            result = self.parser.parse(packet, self.pending_cmd)
            if result:
                self.pending_cmd = None
                self.on_result(result)

    def send(self, data: bytes, pending: Optional[Command] = None) -> None:
        self.pending_cmd = pending
        if self.comm is not None:
            self.comm.send(data)
            self.on_tx(data)

    # --- high level commands ----------------------------------------------
    def abs_stop(self) -> None:
        self.send(CMD_ABS_STOP)

    def abs_angle_stop(self) -> None:
        self.send(CMD_ABS_ANGLE_STOP)

    def abs_move(self, type: str, position: int, speed: int) -> None:
        """Move to absolute *position* at *speed*."""
        cmd = bytearray([0x81, 0x01, 0x06, 0x02, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0xFF])
        if type == "Pan":
            cmd[4] = speed
            cmd[6] = (position >> 12) & 0x0F
            cmd[7] = (position >> 8) & 0x0F
            cmd[8] = (position >> 4) & 0x0F
            cmd[9] = position & 0x0F
        elif type == "Tilt":
            cmd[5] = speed
            cmd[10] = (position >> 12) & 0x0F
            cmd[11] = (position >> 8) & 0x0F
            cmd[12] = (position >> 4) & 0x0F
            cmd[13] = position & 0x0F
        self.send(bytes(cmd))

    def abs_angle_move(self, type: str, angle: int, speed: int) -> None:
        """Move to absolute *angle* at *speed*."""
        cmd = bytearray([0x81, 0x01, 0x06, 0x06, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0xFF])
        if type == "Pan":
            cmd[4] = speed
            cmd[6] = (angle >> 12) & 0x0F
            cmd[7] = (angle >> 8) & 0x0F
            cmd[8] = (angle >> 4) & 0x0F
            cmd[9] = angle & 0x0F
        elif type == "Tilt":
            cmd[5] = speed
            cmd[10] = (angle >> 12) & 0x0F
            cmd[11] = (angle >> 8) & 0x0F
            cmd[12] = (angle >> 4) & 0x0F
            cmd[13] = angle & 0x0F
        self.send(bytes(cmd))

    def rel_stop(self) -> None:
        self.send(CMD_REL_STOP)

    def rel_move(self, direction: str, step: int, speed: int) -> None:
        """Move relatively in *direction* by *step*."""
        cmd = bytearray([0x81, 0x01, 0x06, 0x03, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xFF])
        if direction in ("left", "right"):
            cmd[4] = speed
            cmd[6] = 0x00 if direction == "left" else 0x01
            cmd[7] = (step >> 12) & 0x0F
            cmd[8] = (step >> 8) & 0x0F
            cmd[9] = (step >> 4) & 0x0F
            cmd[10] = step & 0x0F
        else:
            cmd[5] = speed
            cmd[11] = 0x00 if direction == "up" else 0x01
            cmd[12] = (step >> 12) & 0x0F
            cmd[13] = (step >> 8) & 0x0F
            cmd[14] = (step >> 4) & 0x0F
            cmd[15] = step & 0x0F
        self.send(bytes(cmd))

    def get_speed(self) -> None:
        self.send(CMD_GET_SPEED, pending=Command.CURRENT_SPEED)

    def get_version(self) -> None:
        """Query firmware version."""
        self.send(CMD_GET_VERSION, pending=Command.VERSION)

    def get_mcu_type(self) -> None:
        self.send(CMD_GET_MCU_TYPE, pending=Command.MCU_TYPE)

    def get_pan_type(self) -> None:
        self.send(CMD_GET_PAN_TYPE, pending=Command.PAN_TYPE)

    def set_pan_method(self, idx: int) -> None:
        cmd = bytes([0x81, 0xD1, 0x06, 0x02, idx & 0x0F, 0xFF])
        self.send(cmd)

    def tilt_up(self, speed: int) -> None:
        cmd = bytearray([0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x03, 0x01, 0xFF])
        cmd[5] = speed
        self.send(bytes(cmd))

    def tilt_down(self, speed: int) -> None:
        cmd = bytearray([0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x03, 0x02, 0xFF])
        cmd[5] = speed
        self.send(bytes(cmd))

    def pan_left(self, speed: int) -> None:
        cmd = bytearray([0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x01, 0x03, 0xFF])
        cmd[4] = speed
        self.send(bytes(cmd))

    def pan_right(self, speed: int) -> None:
        cmd = bytearray([0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x02, 0x03, 0xFF])
        cmd[4] = speed
        self.send(bytes(cmd))

    def stop(self) -> None:
        self.send(CMD_STOP)

    def stop_at(self, position: int) -> None:
        cmd = bytearray([
            0x81, 0x01, 0x06, 0x01, 0x00, 0x00, 0x03, 0x03,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF
        ])
        cmd[8] = (position >> 12) & 0x0F
        cmd[9] = (position >> 8) & 0x0F
        cmd[10] = (position >> 4) & 0x0F
        cmd[11] = position & 0x0F
        self.send(bytes(cmd))

    def stall_cali_on(self) -> None:
        self.send(CMD_STALL_CALI_ON)

    def stall_cali_off(self) -> None:
        self.send(CMD_STALL_CALI_OFF)

    def zero_cali_plus(self) -> None:
        self.send(CMD_ZERO_CALI_PLUS)

    def zero_cali_minus(self) -> None:
        self.send(CMD_ZERO_CALI_MINUS)

    def clear_zero_cali(self) -> None:
        self.send(CMD_CLEAR_ZERO_CALI)

    def zero_cali_status(self) -> None:
        self.send(CMD_ZERO_CALI_STATUS, pending=Command.ZP_STATUS)

    def lock_home(self) -> None:
        self.send(CMD_LOCK_HOME)

    def unlock_home(self) -> None:
        self.send(CMD_UNLOCK_HOME)

    def lock_status(self) -> None:
        self.send(CMD_LOCK_STATUS, pending=Command.LOCK_STATUS)

    def go_home(self) -> None:
        self.send(CMD_GO_HOME)

    def set_speed_level(self, level: int) -> None:
        cmd = bytes([0x81, 0xD9, 0x06, 0x04, level & 0xFF, 0xFF])
        self.send(cmd, pending=Command.SPEED_PPS)

    def get_speed_by_zoom(self) -> None:
        self.send(CMD_GET_SPEED_BY_ZOOM, pending=Command.SPEED_ZOOM)

    def speed_by_zoom_on(self, ratio: int) -> None:
        self.send(bytes([0x81, 0x01, 0x06, 0xA2, 0x02, ratio & 0x0F, 0xFF]))

    def speed_by_zoom_off(self) -> None:
        self.send(CMD_SPEED_BY_ZOOM_OFF)

    def set_target_speed(self, value: int) -> None:
        cmd = bytearray([0x81, 0xD1, 0x06, 0x03, 0, 0, 0, 0, 0xFF])
        cmd[4] = (value >> 12) & 0x0F
        cmd[5] = (value >> 8) & 0x0F
        cmd[6] = (value >> 4) & 0x0F
        cmd[7] = value & 0x0F
        self.send(bytes(cmd))

    def get_acceleration(self) -> None:
        self.send(CMD_GET_ACCELERATION, pending=Command.ACC_VALUE)

    def set_acceleration(self, value: int) -> None:
        cmd = bytearray([0x81, 0xD1, 0x06, 0x01, 0, 0, 0, 0, 0xFF])
        cmd[4] = (value >> 12) & 0x0F
        cmd[5] = (value >> 8) & 0x0F
        cmd[6] = (value >> 4) & 0x0F
        cmd[7] = value & 0x0F
        self.send(bytes(cmd))

    def get_acc_level(self) -> None:
        self.send(CMD_GET_ACC_LEVEL, pending=Command.ACC_LEVEL)

    def set_acc_level(self, idx: int) -> None:
        self.send(bytes([0x81, 0x01, 0x06, 0x31, (idx + 1) & 0x0F, 0xFF]))

    def get_position(self) -> None:
        self.send(CMD_GET_POSITION, pending=Command.POSITION)

    def get_angle(self) -> None:
        self.send(CMD_GET_ANGLE, pending=Command.ANGLE)

    def get_ab_count(self) -> None:
        self.send(CMD_GET_AB_COUNT, pending=Command.AB_COUNT)

    def get_z_count(self) -> None:
        self.send(CMD_GET_Z_COUNT, pending=Command.Z_COUNT)

    def max_angle_on(self) -> None:
        self.send(CMD_MAX_ANGLE_ON)

    def max_angle_off(self) -> None:
        self.send(CMD_MAX_ANGLE_OFF)

    def motor_type_0p9d(self) -> None:
        self.send(CMD_MOTOR_TYPE_0P9D)

    def motor_type_1p8d(self) -> None:
        self.send(CMD_MOTOR_TYPE_1P8D)