from PyQt5 import QtCore
from typing import Optional
import serial.tools.list_ports

from serial_config import SerialConfig
from serial_comm import SerialComm
from pan_tilt_controller import PanTiltController
from protocol import ParseResult, Command

CONFIG_FILE = "serial_config.json"
DEFAULT_SPEED_LEVEL = 100

def list_serial_ports():
    return [p.device for p in serial.tools.list_ports.comports()]

class AppController(QtCore.QObject):
    """
    The main controller for the application. It handles the business logic,
    communication with the serial port, and interaction with the data models.
    It communicates with the UI (View) through signals and slots.
    """
    # --- Signals to notify the View of changes ---
    connection_status_changed = QtCore.pyqtSignal(bool)
    ports_refreshed = QtCore.pyqtSignal(list, str)
    rx_data_received = QtCore.pyqtSignal(str)
    tx_data_sent = QtCore.pyqtSignal(str)

    # Signals for updating specific UI fields
    fw_version_updated = QtCore.pyqtSignal(str)
    mcu_type_updated = QtCore.pyqtSignal(int)
    pan_type_updated = QtCore.pyqtSignal(int)
    speed_pps_updated = QtCore.pyqtSignal(str)
    current_speed_updated = QtCore.pyqtSignal(str)
    acc_level_updated = QtCore.pyqtSignal(int)
    speed_by_zoom_ratio_updated = QtCore.pyqtSignal(str)
    acceleration_updated = QtCore.pyqtSignal(str)
    position_updated = QtCore.pyqtSignal(str)
    angle_updated = QtCore.pyqtSignal(str)
    ab_count_updated = QtCore.pyqtSignal(str)
    z_count_updated = QtCore.pyqtSignal(str)
    zero_cali_status_updated = QtCore.pyqtSignal(str)
    lock_status_updated = QtCore.pyqtSignal(str)

    # Signal for the speed chart
    speed_value_received = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_data = SerialConfig()
        self.comm: Optional[SerialComm] = None
        self.pan_tilt_controller = PanTiltController()
        self.connected = False
        self.pending_cmd = None
        self.await_speed = False

        # Connect to the PanTiltController's signals
        self.pan_tilt_controller.on_result = self._handle_result
        self.pan_tilt_controller.on_tx = self._handle_tx
        self.pan_tilt_controller.data_received.connect(self._handle_rx)

    def initialize(self):
        """Load configurations and prepare the controller."""
        self.config_data.load(CONFIG_FILE)
        self.refresh_ports()

    def shutdown(self):
        """Clean up resources, like closing the serial port."""
        if self.connected:
            self.pan_tilt_controller.close()

    def refresh_ports(self):
        """Refreshes the list of available serial ports."""
        ports = list_serial_ports()
        self.ports_refreshed.emit(ports, self.config_data.port_name)

    def _handle_tx(self, data: bytes):
        """Handle outgoing data display."""
        self.tx_data_sent.emit(' '.join(f'{b:02X}' for b in data))

    def _handle_rx(self, data: bytes):
        """Handle incoming raw data display."""
        packets = []
        start = 0
        for i, byte in enumerate(data):
            if byte == 0xFF:
                packet = data[start:i + 1]
                packets.append(' '.join(f'{b:02X}' for b in packet))
                start = i + 1

        if start < len(data):
            packets.append(' '.join(f'{b:02X}' for b in data[start:]))
        
        self.rx_data_received.emit('\n'.join(packets))

    def _handle_result(self, result: ParseResult):
        """
        Parse the result from the protocol and emit signals to update the UI.
        This is the core logic that was previously in SerialWindow._handle_result.
        """
        if result.type == Command.PAN_TYPE:
            self.pan_type_updated.emit(result.value)
        elif result.type == Command.VERSION:
            self.fw_version_updated.emit(result.value)
            self.pan_tilt_controller.get_mcu_type()
        elif result.type == Command.MCU_TYPE:
            self.mcu_type_updated.emit(result.value)
        elif result.type == Command.SPEED_PPS:
            self.speed_pps_updated.emit(str(result.value))
        elif result.type == Command.CURRENT_SPEED:
            value = result.value
            self.current_speed_updated.emit(str(value))
            if self.await_speed:
                self.speed_value_received.emit(value)
                self.await_speed = False
        elif result.type == Command.ACC_LEVEL:
            self.acc_level_updated.emit(result.value)
        elif result.type == Command.SPEED_ZOOM:
            self.speed_by_zoom_ratio_updated.emit(str(result.value))
        elif result.type == Command.ACC_VALUE:
            self.acceleration_updated.emit(str(result.value))
        elif result.type == Command.POSITION:
            self.position_updated.emit(str(result.value))
        elif result.type == Command.ANGLE:
            self.angle_updated.emit(str(result.value))
        elif result.type == Command.AB_COUNT:
            self.ab_count_updated.emit(str(result.value))
        elif result.type == Command.Z_COUNT:
            self.z_count_updated.emit(str(result.value))
        elif result.type == Command.ZP_STATUS:
            self.zero_cali_status_updated.emit('Done' if result.value == 1 else 'Not Done')
        elif result.type == Command.LOCK_STATUS:
            self.lock_status_updated.emit('Locked' if result.value == 1 else 'Unlocked')
        
        self.pending_cmd = None

    def toggle_connection(self, port_name: str):
        """Connect or disconnect the serial port."""
        if not self.connected:
            self.config_data.port_name = port_name
            self.pan_tilt_controller.close()
            self.comm = SerialComm(config=self.config_data)
            self.pan_tilt_controller.set_comm(self.comm)
            self.pan_tilt_controller.open()
            self.pending_cmd = Command.VERSION
            self.pan_tilt_controller.get_version()
            self.connected = True
        else:
            self.pan_tilt_controller.close()
            self.pan_tilt_controller.set_comm(None)
            self.comm = None
            self.connected = False
        self.connection_status_changed.emit(self.connected)

    def send_test_command(self, hex_string: str):
        """Parse and send a raw hex command."""
        text = hex_string.strip().replace(' ', '')
        if len(text) % 2 != 0:
            text = text[:-1]
        try:
            cmd = bytes.fromhex(text)
            if cmd:
                self.pan_tilt_controller.send(cmd, self.pending_cmd)
        except ValueError:
            # Optionally, emit a signal to show an error in the UI
            pass

    def query_speed(self):
        """Request the current speed for the chart."""
        self.await_speed = True
        self.get_current_speed()

    # --- Methods to be called from the View ---
    # These methods act as a facade, forwarding calls to the PanTiltController.
    # This decouples the View from the PanTiltController.

    def get_pan_type(self):
        self.pan_tilt_controller.get_pan_type()

    def set_pan_method(self, index: int):
        self.pan_tilt_controller.set_pan_method(index)

    def stop_at(self, position: int):
        self.pan_tilt_controller.stop_at(position)

    def abs_stop(self):
        self.pan_tilt_controller.abs_stop()

    def abs_angle_stop(self):
        self.pan_tilt_controller.abs_angle_stop()

    def stall_cali_on(self):
        self.pan_tilt_controller.stall_cali_on()

    def stall_cali_off(self):
        self.pan_tilt_controller.stall_cali_off()

    def zero_cali_plus(self):
        self.pan_tilt_controller.zero_cali_plus()

    def zero_cali_minus(self):
        self.pan_tilt_controller.zero_cali_minus()

    def go_home(self):
        self.pan_tilt_controller.go_home()

    def clear_zero_cali(self):
        self.pan_tilt_controller.clear_zero_cali()

    def get_zero_cali_status(self):
        self.pan_tilt_controller.zero_cali_status()

    def lock_home(self):
        self.pan_tilt_controller.lock_home()

    def unlock_home(self):
        self.pan_tilt_controller.unlock_home()

    def get_lock_status(self):
        self.pan_tilt_controller.lock_status()

    def get_speed_by_zoom(self):
        self.pan_tilt_controller.get_speed_by_zoom()

    def speed_by_zoom_on(self, ratio: int):
        self.pan_tilt_controller.speed_by_zoom_on(ratio)

    def speed_by_zoom_off(self):
        self.pan_tilt_controller.speed_by_zoom_off()

    def get_current_speed(self):
        self.pan_tilt_controller.get_speed()

    def get_acceleration(self):
        self.pan_tilt_controller.get_acceleration()

    def get_acc_level(self):
        self.pan_tilt_controller.get_acc_level()

    def get_position(self):
        self.pan_tilt_controller.get_position()

    def get_angle(self):
        self.pan_tilt_controller.get_angle()

    def get_ab_count(self):
        self.pan_tilt_controller.get_ab_count()

    def get_z_count(self):
        self.pan_tilt_controller.get_z_count()

    def max_angle_on(self):
        self.pan_tilt_controller.max_angle_on()

    def max_angle_off(self):
        self.pan_tilt_controller.max_angle_off()

    def motor_type_0p9d(self):
        self.pan_tilt_controller.motor_type_0p9d()

    def motor_type_1p8d(self):
        self.pan_tilt_controller.motor_type_1p8d()

    def set_speed_level(self, level: int):
        self.pan_tilt_controller.set_speed_level(level)

    def tilt_up(self, speed_level: int):
        self.pan_tilt_controller.tilt_up(speed_level)

    def tilt_down(self, speed_level: int):
        self.pan_tilt_controller.tilt_down(speed_level)

    def pan_left(self, speed_level: int):
        self.pan_tilt_controller.pan_left(speed_level)

    def pan_right(self, speed_level: int):
        self.pan_tilt_controller.pan_right(speed_level)

    def stop_movement(self):
        self.pan_tilt_controller.stop()

    def abs_move(self, mcu_type: str, position: int, speed: int):
        self.pan_tilt_controller.abs_move(mcu_type, position, speed)

    def abs_angle_move(self, mcu_type: str, angle: int, speed: int):
        self.pan_tilt_controller.abs_angle_move(mcu_type, angle, speed)

    def rel_stop(self):
        self.pan_tilt_controller.rel_stop()

    def rel_move(self, direction: str, steps: int, speed: int):
        self.pan_tilt_controller.rel_move(direction, steps, speed)

    def set_target_speed(self, speed: int):
        self.pan_tilt_controller.set_target_speed(speed)

    def set_acceleration(self, value: int):
        self.pan_tilt_controller.set_acceleration(value)

    def set_acc_level(self, level: int):
        self.pan_tilt_controller.set_acc_level(level)
