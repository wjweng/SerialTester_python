from PyQt5 import QtCore, QtWidgets, QtChart, QtGui
from collections import deque
import sys
import serial.tools.list_ports

from serial_config import SerialConfig
from serial_ui import Ui_SerialWidget
from protocol import ParseResult
from typing import Optional
from serial_comm import SerialComm
from pan_tilt_controller import PanTiltController

CONFIG_FILE = "serial_config.json"
DEFAULT_SPEED_LEVEL = 100

def list_serial_ports():
    return [p.device for p in serial.tools.list_ports.comports()]

class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent, config: SerialConfig):
        super().__init__(parent)
        self.setWindowTitle("Configure")
        self.config = config

        layout = QtWidgets.QFormLayout(self)

        self.editBaud = QtWidgets.QLineEdit(str(config.baud_rate))
        layout.addRow("Baud rate:", self.editBaud)

        self.comboParity = QtWidgets.QComboBox()
        self.comboParity.addItems(['N', 'E', 'O', 'M', 'S'])
        self.comboParity.setCurrentText(config.parity)
        layout.addRow("Parity:", self.comboParity)

        self.comboStop = QtWidgets.QComboBox()
        self.comboStop.addItems(['1', '1.5', '2'])
        self.comboStop.setCurrentText(str(config.stop_bits))
        layout.addRow("Stop bits:", self.comboStop)

        self.comboFlow = QtWidgets.QComboBox()
        self.comboFlow.addItems(['none', 'rtscts', 'dsrdtr', 'xonxoff'])
        self.comboFlow.setCurrentText(config.flow_control)
        layout.addRow("Flow control:", self.comboFlow)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        layout.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def accept(self):
        self.config.baud_rate = int(self.editBaud.text())
        self.config.parity = self.comboParity.currentText()
        self.config.stop_bits = float(self.comboStop.currentText())
        self.config.flow_control = self.comboFlow.currentText()
        self.config.save(CONFIG_FILE)
        super().accept()


class SerialWindow(QtWidgets.QWidget):
    result_received = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.ui = Ui_SerialWidget()
        self.ui.setupUi(self)

        self.config_data = SerialConfig()
        self.config_data.load(CONFIG_FILE)

        self.comm: Optional[SerialComm] = None
        self.controller = PanTiltController()
        self.controller.on_result = lambda r: self.result_received.emit(r)
        self.controller.on_tx = lambda d: self.ui.textTx.append(' '.join(f'{b:02X}' for b in d))
        self.connected = False
        self.pending_cmd = None

        self.result_received.connect(self.handle_result)
        self.controller.data_received.connect(self.handle_rx)

        self.refresh_ports()

        self.ui.btnOnline.clicked.connect(self.toggle_connection)
        self.ui.btnConfigure.clicked.connect(self.open_config)
        self.ui.btnClear.clicked.connect(self.clear_text)
        self.ui.btnTest1.clicked.connect(lambda: self.handle_test(1))
        self.ui.btnTest2.clicked.connect(lambda: self.handle_test(2))
        self.ui.btnTest3.clicked.connect(lambda: self.handle_test(3))
        self.ui.btnTest4.clicked.connect(lambda: self.handle_test(4))
        self.ui.btnTest5.clicked.connect(lambda: self.handle_test(5))
        self.ui.btnTest6.clicked.connect(lambda: self.handle_test(6))
        self.ui.btnTest7.clicked.connect(lambda: self.handle_test(7))
        self.ui.btnTest8.clicked.connect(lambda: self.handle_test(8))
        self.ui.btnShowSpeed.clicked.connect(self.start_speed_timer)
        self.ui.btnStopSpeed.clicked.connect(self.stop_speed_timer)
        self.ui.btnClearChart.clicked.connect(self.clear_speed_chart)
        self.ui.btnTiltUp.clicked.connect(self.tilt_up_clicked)
        self.ui.btnTiltUp.pressed.connect(self.tilt_up_pressed)
        self.ui.btnTiltUp.released.connect(self.tilt_released)
        self.ui.btnTiltDown.clicked.connect(self.tilt_down_clicked)
        self.ui.btnTiltDown.pressed.connect(self.tilt_down_pressed)
        self.ui.btnTiltDown.released.connect(self.tilt_released)
        self.ui.btnPanLeft.clicked.connect(self.pan_left_clicked)
        self.ui.btnPanLeft.pressed.connect(self.pan_left_pressed)
        self.ui.btnPanLeft.released.connect(self.pan_released)
        self.ui.btnPanRight.clicked.connect(self.pan_right_clicked)
        self.ui.btnPanRight.pressed.connect(self.pan_right_pressed)
        self.ui.btnPanRight.released.connect(self.pan_released)
        self.ui.btnPanStop.clicked.connect(self.controller.stop)
        self.ui.btnStopAt.clicked.connect(self.stop_at)
        self.ui.btnABS.clicked.connect(lambda: self.controller.abs_move(
            self.ui.labelMCUType.text(), int(self.ui.editABSPos.text() or "0"), self.get_speed_level()))
        self.ui.btnABS2.clicked.connect(lambda: self.controller.abs_move(
            self.ui.labelMCUType.text(), int(self.ui.editABS2Pos.text() or "0"), self.get_speed_level()))
        self.ui.btnABSAngle.clicked.connect(lambda: self.controller.abs_move(
            self.ui.labelMCUType.text(), int(self.ui.editABSAngle.text() or "0"), self.get_speed_level()))
        self.ui.btnABSAngle2.clicked.connect(lambda: self.controller.abs_move(
            self.ui.labelMCUType.text(), int(self.ui.editABSAngle2.text() or "0"), self.get_speed_level()))
        self.ui.btnABSStop.clicked.connect(self.controller.abs_stop)
        self.ui.btnABSAngleStop.clicked.connect(self.controller.abs_angle_stop)
        self.ui.btnPanType.clicked.connect(self.controller.get_pan_type)
        self.ui.comboPanMethod.currentIndexChanged.connect(self.set_pan_method)
        self.ui.btnRelUp.clicked.connect(lambda: self.controller.rel_move(
            'up', int(self.ui.editRelStep.text() or '0'), self.get_speed_level()))
        self.ui.btnRelDown.clicked.connect(lambda: self.controller.rel_move(
            'down', int(self.ui.editRelStep.text() or '0'), self.get_speed_level()))
        self.ui.btnRelLeft.clicked.connect(lambda: self.controller.rel_move(
            'left', int(self.ui.editRelStep.text() or '0'), self.get_speed_level()))
        self.ui.btnRelRight.clicked.connect(lambda: self.controller.rel_move(
            'right', int(self.ui.editRelStep.text() or '0'), self.get_speed_level()))
        self.ui.btnRelStop.clicked.connect(self.controller.stop)
        self.ui.btnStallCaliOn.clicked.connect(self.controller.stall_cali_on)
        self.ui.btnStallCaliOff.clicked.connect(self.controller.stall_cali_off)
        self.ui.btnZeroCaliPlus.clicked.connect(self.controller.zero_cali_plus)
        self.ui.btnZeroCaliMinus.clicked.connect(self.controller.zero_cali_minus)
        self.ui.btnZeroHome.clicked.connect(self.controller.go_home)
        self.ui.btnClearZeroCali.clicked.connect(self.controller.clear_zero_cali)
        self.ui.btnZeroCaliStatus.clicked.connect(self.controller.zero_cali_status)
        self.ui.btnLockHome.clicked.connect(self.controller.lock_home)
        self.ui.btnUnlockHome.clicked.connect(self.controller.unlock_home)
        self.ui.btnLockStatus.clicked.connect(self.controller.lock_status)
        self.ui.editSpeedLevel.textChanged.connect(self.speed_level_changed)
        self.ui.btnGetSpeedByZoomRatio.clicked.connect(self.controller.get_speed_by_zoom)
        self.ui.btnSpeedByZoomOn.clicked.connect(self.speed_by_zoom_on)
        self.ui.btnSpeedByZoomOff.clicked.connect(self.controller.speed_by_zoom_off)
        self.ui.btnGetCurrentSpeed.clicked.connect(self.controller.get_speed)
        self.ui.btnSetTargetSpeed.clicked.connect(self.set_target_speed)
        self.ui.btnGetAcceleration.clicked.connect(self.controller.get_acceleration)
        self.ui.btnSetAcceleration.clicked.connect(self.set_acceleration)
        self.ui.btnGetAccLevel.clicked.connect(self.controller.get_acc_level)
        self.ui.btnSetAccLevel.clicked.connect(self.set_acc_level)
        self.ui.btnGetPosition.clicked.connect(self.controller.get_position)
        self.ui.btnGetAngle.clicked.connect(self.controller.get_angle)
        self.ui.btnABCount.clicked.connect(self.controller.get_ab_count)
        self.ui.btnZCount.clicked.connect(self.controller.get_z_count)
        self.ui.btnMaxAngleOn.clicked.connect(self.controller.max_angle_on)
        self.ui.btnMaxAngleOff.clicked.connect(self.controller.max_angle_off)
        self.ui.btnMotorType0p9d.clicked.connect(self.controller.motor_type_0p9d)
        self.ui.btnMotorType1p8d.clicked.connect(self.controller.motor_type_1p8d)
        self.ui.comboPTType.currentIndexChanged.connect(self.update_mcu_display)
        self.update_mcu_display(self.ui.comboPTType.currentIndex())

        self.speed_timer = QtCore.QTimer(self)
        self.speed_timer.timeout.connect(self.send_speed_query)

        # chart for motor speed
        self.speed_series = QtChart.QLineSeries()
        self.speed_chart = QtChart.QChart()
        self.speed_chart.addSeries(self.speed_series)
        self.speed_chart.createDefaultAxes()
        self.speed_chart.legend().hide()
        self.ui.chartSpeed.setChart(self.speed_chart)
        self.ui.chartSpeed.setRenderHint(QtGui.QPainter.Antialiasing)
        self.ui.chartSpeed.setFixedWidth(640)
        self.ui.chartSpeed.setMinimumHeight(480)

        self.speed_values = deque(maxlen=200)
        self.speed_times = deque(maxlen=200)
        self.speed_counter = 0
        self.await_speed = False


    def refresh_ports(self):
        ports = list_serial_ports()
        self.ui.comboPort.clear()
        self.ui.comboPort.addItems(ports)
        idx = self.ui.comboPort.findText(self.config_data.port_name)
        if idx >= 0:
            self.ui.comboPort.setCurrentIndex(idx)

    def toggle_connection(self):
        if not self.connected:
            self.config_data.port_name = self.ui.comboPort.currentText()
            self.controller.close()
            self.comm = SerialComm(config=self.config_data)
            self.controller.set_comm(self.comm)
            self.controller.open()
            self.pending_cmd = 'version'
            self.controller.get_version()
            self.ui.btnOnline.setText("OffLine")
            self.connected = True
        else:
            self.controller.close()
            self.controller.set_comm(None)
            self.comm = None
            self.ui.btnOnline.setText("OnLine")
            self.connected = False

    def send_command(self, data: bytes):
        self.controller.send(data, self.pending_cmd)
        self.ui.textTx.append(' '.join(f'{b:02X}' for b in data))

    def parse_hex(self, text: str) -> bytes:
        text = text.strip().replace(' ', '')
        if len(text) % 2 != 0:
            text = text[:-1]
        try:
            return bytes.fromhex(text)
        except ValueError:
            return b''

    def handle_test(self, idx: int):
        edit = getattr(self.ui, f'editTest{idx}')
        cmd = self.parse_hex(edit.text())
        if cmd:
            self.send_command(cmd)

    def start_speed_timer(self):
        self.speed_timer.start(50)

    def stop_speed_timer(self):
        self.speed_timer.stop()

    def send_speed_query(self):
        self.await_speed = True
        self.controller.get_speed()

    def update_speed_chart(self):
        self.speed_series.clear()
        for t, v in zip(self.speed_times, self.speed_values):
            self.speed_series.append(t, v)
        if self.speed_times:
            self.speed_chart.axisX().setRange(self.speed_times[0], self.speed_times[-1])
        if self.speed_values:
            ymin = min(self.speed_values)
            ymax = max(self.speed_values)
            if ymin == ymax:
                ymax += 1
            self.speed_chart.axisY().setRange(ymin, ymax)

    def get_speed_level(self) -> int:
        text = self.ui.editSpeedLevel.text()
        if not text:
            level = DEFAULT_SPEED_LEVEL
            self.ui.editSpeedLevel.setText(str(level))
        else:
            level = int(text)
        if level == 0:
            level = 1
            self.ui.editSpeedLevel.setText(str(level))
        return level

    def tilt_up_clicked(self):
        if self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.tilt_up(level)

    def tilt_up_pressed(self):
        if not self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.tilt_up(level)

    def tilt_down_clicked(self):
        if self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.tilt_down(level)

    def tilt_down_pressed(self):
        if not self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.tilt_down(level)

    def tilt_released(self):
        if self.ui.checkMoveStop.isChecked():
            self.controller.stop()

    def pan_left_clicked(self):
        if self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.pan_left(level)

    def pan_left_pressed(self):
        if not self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.pan_left(level)

    def pan_right_clicked(self):
        if self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.pan_right(level)

    def pan_right_pressed(self):
        if not self.ui.checkMoveStop.isChecked():
            return
        level = self.get_speed_level()
        self.controller.pan_right(level)

    def pan_released(self):
        if self.ui.checkMoveStop.isChecked():
            self.controller.stop()

    def stop_at(self):
        text = self.ui.editStopAt.text() or "0"
        pos = int(text)
        self.controller.stop_at(pos)
    def update_mcu_display(self, idx: int):
        if idx == 0:
            self.ui.labelMCUType.setText("Pan")
        else:
            self.ui.labelMCUType.setText("Tilt")

    def set_pan_method(self, idx: int):
        if idx is None:
            idx = self.ui.comboPanMethod.currentIndex()
        if idx < 0:
            idx = 0
            self.ui.comboPanMethod.setCurrentIndex(0)
        self.controller.set_pan_method(idx)

    def speed_level_changed(self):
        text = self.ui.editSpeedLevel.text()
        if not text:
            return
        level = int(text)
        if level < 1:
            level = 1
        self.controller.set_speed_level(level)

    def on_rx(self, data: bytes):
        self.data_received.emit(data)
    def speed_by_zoom_on(self):
        ratio = int(self.ui.editSpeedByZoomRatio.text() or "1")
        self.controller.speed_by_zoom_on(ratio)

    def set_target_speed(self):
        val = int(self.ui.editTargetSpeed.text() or "0")
        self.controller.set_target_speed(val)

    def set_acceleration(self):
        val = int(self.ui.editAcceleration.text() or "100")
        self.controller.set_acceleration(val)

    def set_acc_level(self):
        idx = self.ui.comboAccLevel.currentIndex()
        self.controller.set_acc_level(idx)

    def handle_rx(self, data: bytes):
        # Only display incoming packets here. Parsing is handled by the controller.
        packets = []
        start = 0
        for i, byte in enumerate(data):
            if byte == 0xFF:
                packet = data[start:i + 1]
                packets.append(' '.join(f'{b:02X}' for b in packet))
                start = i + 1

        if start < len(data):
            packets.append(' '.join(f'{b:02X}' for b in data[start:]))

        self.ui.textRx.append('\n'.join(packets))

    def handle_result(self, result: ParseResult) -> None:
        if result.type == 'pan_type':
            value = result.value
            if value < self.ui.comboPanMethod.count():
                self.ui.comboPanMethod.setCurrentIndex(value)
            self.pending_cmd = None
        elif result.type == 'version':
            self.ui.labelFwValue.setText(result.value)
            self.pending_cmd = None
            self.controller.get_mcu_type()
        elif result.type == 'mcu_type':
            idx_val = result.value
            if idx_val < self.ui.comboPTType.count():
                self.ui.comboPTType.setCurrentIndex(idx_val)
            self.update_mcu_display(idx_val)
            self.pending_cmd = None
        elif result.type == 'speed_pps':
            self.ui.editSpeedInPPS.setText(str(result.value))
            self.pending_cmd = None
        elif result.type == 'current_speed':
            value = result.value
            self.ui.editCurrentSpeed.setText(str(value))
            self.pending_cmd = None
            if self.await_speed:
                self.speed_values.append(value)
                self.speed_times.append(self.speed_counter * 0.05)
                self.speed_counter += 1
                self.update_speed_chart()
                self.await_speed = False
        elif result.type == 'acc_level':
            idx_val = result.value
            if 0 <= idx_val < self.ui.comboAccLevel.count():
                self.ui.comboAccLevel.setCurrentIndex(idx_val)
            self.pending_cmd = None
        elif result.type == 'speed_zoom':
            self.ui.editSpeedByZoomRatio.setText(str(result.value))
            self.pending_cmd = None
        elif result.type == 'acc_value':
            self.ui.editAcceleration.setText(str(result.value))
            self.pending_cmd = None
        elif result.type == 'position':
            self.ui.editMotorPosition.setText(str(result.value))
            self.pending_cmd = None
        elif result.type == 'angle':
            self.ui.editMotorAngle.setText(str(result.value))
            self.pending_cmd = None
        elif result.type == 'ab_count':
            self.ui.editABCount.setText(str(result.value))
            self.pending_cmd = None
        elif result.type == 'z_count':
            self.ui.editZCount.setText(str(result.value))
            self.pending_cmd = None
        elif result.type == 'zp_status':
            val = result.value
            self.ui.editZeroCali.setText('Done' if val == 1 else 'Not Done')
            self.pending_cmd = None
        elif result.type == 'lock_status':
            val = result.value
            self.ui.editLockStatus.setText('Locked' if val == 1 else 'Unlocked')
            self.pending_cmd = None

    def clear_text(self):
        self.ui.textTx.clear()
        self.ui.textRx.clear()

    def clear_speed_chart(self):
        self.speed_series.clear()
        self.speed_values.clear()
        self.speed_times.clear()
        self.speed_counter = 0
        self.speed_chart.removeAllSeries()
        self.speed_series = QtChart.QLineSeries()
        self.speed_chart.addSeries(self.speed_series)
        self.speed_chart.createDefaultAxes()
        self.speed_chart.legend().hide()

    def open_config(self):
        dlg = ConfigDialog(self, self.config_data)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.refresh_ports()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = SerialWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
