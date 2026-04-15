from PyQt5 import QtCore, QtWidgets, QtChart, QtGui
from collections import deque
import sys

from serial_ui import Ui_SerialWidget
from config_dialog import ConfigDialog
from app_controller import AppController

DEFAULT_SPEED_LEVEL = 100


class SerialWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SerialWidget()
        self.ui.setupUi(self)

        # Create the controller that will handle all logic
        self.controller = AppController(self)

        self._setup_speed_chart()
        self._connect_signals_to_controller()
        self._connect_controller_to_slots()

        # Initialize the controller, which will load configs and refresh ports
        self.controller.initialize()

    def _setup_speed_chart(self):
        """Initializes the UI for the speed chart."""
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
        
        self.speed_timer = QtCore.QTimer(self)
        self.speed_timer.setInterval(50)
        self.speed_timer.timeout.connect(self.controller.query_speed)

    def _connect_signals_to_controller(self):
        """Connects UI element signals (e.g., button clicks) to the controller's methods."""
        # Connection and config
        self.ui.btnOnline.clicked.connect(self._handle_toggle_connection)
        self.ui.btnConfigure.clicked.connect(self._handle_open_config)
        self.ui.btnClear.clicked.connect(self._handle_clear_text)

        # Test commands
        self.ui.btnTest1.clicked.connect(self._handle_send_test_command_1)
        self.ui.btnTest2.clicked.connect(self._handle_send_test_command_2)
        self.ui.btnTest3.clicked.connect(self._handle_send_test_command_3)
        self.ui.btnTest4.clicked.connect(self._handle_send_test_command_4)
        self.ui.btnTest5.clicked.connect(self._handle_send_test_command_5)
        self.ui.btnTest6.clicked.connect(self._handle_send_test_command_6)
        self.ui.btnTest7.clicked.connect(self._handle_send_test_command_7)
        self.ui.btnTest8.clicked.connect(self._handle_send_test_command_8)

        # Pan/Tilt continuous movement
        self.ui.btnTiltUp.pressed.connect(self._handle_tilt_up_pressed)
        self.ui.btnTiltUp.released.connect(self._handle_tilt_released)
        self.ui.btnTiltDown.pressed.connect(self._handle_tilt_down_pressed)
        self.ui.btnTiltDown.released.connect(self._handle_tilt_released)
        self.ui.btnPanLeft.pressed.connect(self._handle_pan_left_pressed)
        self.ui.btnPanLeft.released.connect(self._handle_pan_released)
        self.ui.btnPanRight.pressed.connect(self._handle_pan_right_pressed)
        self.ui.btnPanRight.released.connect(self._handle_pan_released)
        self.ui.btnPanStop.clicked.connect(self.controller.stop_movement)
        self.ui.btnStopAt.clicked.connect(self._handle_stop_at)

        # Absolute and Relative movement
        self.ui.btnABS.clicked.connect(self._handle_abs_move)
        self.ui.btnABS2.clicked.connect(self._handle_abs2_move)
        self.ui.btnABSAngle.clicked.connect(self._handle_abs_angle_move)
        self.ui.btnABSAngle2.clicked.connect(self._handle_abs_angle2_move)
        self.ui.btnABSStop.clicked.connect(self.controller.abs_stop)
        self.ui.btnABSAngleStop.clicked.connect(self.controller.abs_angle_stop)
        self.ui.btnRelUp.clicked.connect(self._handle_rel_move_up)
        self.ui.btnRelDown.clicked.connect(self._handle_rel_move_down)
        self.ui.btnRelLeft.clicked.connect(self._handle_rel_move_left)
        self.ui.btnRelRight.clicked.connect(self._handle_rel_move_right)
        self.ui.btnRelStop.clicked.connect(self.controller.rel_stop)

        # Calibration and Homing
        self.ui.btnStallCaliOn.clicked.connect(self.controller.stall_cali_on)
        self.ui.btnStallCaliOff.clicked.connect(self.controller.stall_cali_off)
        self.ui.btnZeroCaliPlus.clicked.connect(self.controller.zero_cali_plus)
        self.ui.btnZeroCaliMinus.clicked.connect(self.controller.zero_cali_minus)
        self.ui.btnZeroHome.clicked.connect(self.controller.go_home)
        self.ui.btnClearZeroCali.clicked.connect(self.controller.clear_zero_cali)
        self.ui.btnZeroCaliStatus.clicked.connect(self.controller.get_zero_cali_status)
        self.ui.btnLockHome.clicked.connect(self.controller.lock_home)
        self.ui.btnUnlockHome.clicked.connect(self.controller.unlock_home)
        self.ui.btnLockStatus.clicked.connect(self.controller.get_lock_status)

        # Speed and Acceleration
        self.ui.editSpeedLevel.textChanged.connect(self._handle_speed_level_changed)
        self.ui.btnGetSpeedByZoomRatio.clicked.connect(self.controller.get_speed_by_zoom)
        self.ui.btnSpeedByZoomOn.clicked.connect(self._handle_speed_by_zoom_on)
        self.ui.btnSpeedByZoomOff.clicked.connect(self.controller.speed_by_zoom_off)
        self.ui.btnGetCurrentSpeed.clicked.connect(self.controller.get_current_speed)
        self.ui.btnSetTargetSpeed.clicked.connect(self._handle_set_target_speed)
        self.ui.btnGetAcceleration.clicked.connect(self.controller.get_acceleration)
        self.ui.btnSetAcceleration.clicked.connect(self._handle_set_acceleration)
        self.ui.btnGetAccLevel.clicked.connect(self.controller.get_acc_level)
        self.ui.comboAccLevel.currentIndexChanged.connect(self.controller.set_acc_level)

        # Position, Angle, and Counts
        self.ui.btnGetPosition.clicked.connect(self.controller.get_position)
        self.ui.btnGetAngle.clicked.connect(self.controller.get_angle)
        self.ui.btnABCount.clicked.connect(self.controller.get_ab_count)
        self.ui.btnZCount.clicked.connect(self.controller.get_z_count)

        # Motor and PT Type
        self.ui.btnPanType.clicked.connect(self.controller.get_pan_type)
        self.ui.comboPanMethod.currentIndexChanged.connect(self.controller.set_pan_method)
        self.ui.btnMaxAngleOn.clicked.connect(self.controller.max_angle_on)
        self.ui.btnMaxAngleOff.clicked.connect(self.controller.max_angle_off)
        self.ui.btnMotorType0p9d.clicked.connect(self.controller.motor_type_0p9d)
        self.ui.btnMotorType1p8d.clicked.connect(self.controller.motor_type_1p8d)
        self.ui.comboPTType.currentIndexChanged.connect(self._update_mcu_type_label)

        # Speed Chart
        self.ui.btnShowSpeed.clicked.connect(self.speed_timer.start)
        self.ui.btnStopSpeed.clicked.connect(self.speed_timer.stop)
        self.ui.btnClearChart.clicked.connect(self._handle_clear_speed_chart)

    def _connect_controller_to_slots(self):
        """Connects the controller's signals to the UI's update methods (slots)."""
        self.controller.connection_status_changed.connect(self.on_connection_status_changed)
        self.controller.ports_refreshed.connect(self.on_ports_refreshed)
        self.controller.rx_data_received.connect(self.ui.textRx.append)
        self.controller.tx_data_sent.connect(self.ui.textTx.append)

        # Connect data update signals to UI widgets
        self.controller.fw_version_updated.connect(self.ui.labelFwValue.setText)
        self.controller.mcu_type_updated.connect(self.on_mcu_type_updated)
        self.controller.pan_type_updated.connect(self.ui.comboPanMethod.setCurrentIndex)
        self.controller.speed_pps_updated.connect(self.ui.editSpeedInPPS.setText)
        self.controller.current_speed_updated.connect(self.ui.editCurrentSpeed.setText)
        self.controller.acc_level_updated.connect(self.ui.comboAccLevel.setCurrentIndex)
        self.controller.speed_by_zoom_ratio_updated.connect(self.ui.editSpeedByZoomRatio.setText)
        self.controller.acceleration_updated.connect(self.ui.editAcceleration.setText)
        self.controller.position_updated.connect(self.ui.editMotorPosition.setText)
        self.controller.angle_updated.connect(self.ui.editMotorAngle.setText)
        self.controller.ab_count_updated.connect(self.ui.editABCount.setText)
        self.controller.z_count_updated.connect(self.ui.editZCount.setText)
        self.controller.zero_cali_status_updated.connect(self.ui.editZeroCali.setText)
        self.controller.lock_status_updated.connect(self.ui.editLockStatus.setText)

        # Speed chart
        self.controller.speed_value_received.connect(self.on_speed_value_received)

    # --- UI Event Handlers (Slots that call the controller) ---

    def _handle_toggle_connection(self):
        port_name = self.ui.comboPort.currentText()
        self.controller.toggle_connection(port_name)

    def _handle_clear_text(self):
        self.ui.textTx.clear()
        self.ui.textRx.clear()

    def _get_speed_level(self) -> int:
        text = self.ui.editSpeedLevel.text()
        if not text:
            level = DEFAULT_SPEED_LEVEL
            self.ui.editSpeedLevel.setText(str(level))
            return level
        level = int(text)
        if level < 1:
            level = 1
            self.ui.editSpeedLevel.setText(str(level))
        return level

    def _handle_send_test_command_1(self):
        self.controller.send_test_command(self.ui.editTest1.text())

    def _handle_send_test_command_2(self):
        self.controller.send_test_command(self.ui.editTest2.text())

    def _handle_send_test_command_3(self):
        self.controller.send_test_command(self.ui.editTest3.text())

    def _handle_send_test_command_4(self):
        self.controller.send_test_command(self.ui.editTest4.text())

    def _handle_send_test_command_5(self):
        self.controller.send_test_command(self.ui.editTest5.text())

    def _handle_send_test_command_6(self):
        self.controller.send_test_command(self.ui.editTest6.text())

    def _handle_send_test_command_7(self):
        self.controller.send_test_command(self.ui.editTest7.text())

    def _handle_send_test_command_8(self):
        self.controller.send_test_command(self.ui.editTest8.text())

    def _handle_tilt_up_pressed(self):
        self.controller.tilt_up(self._get_speed_level())

    def _handle_tilt_down_pressed(self):
        self.controller.tilt_down(self._get_speed_level())

    def _handle_pan_left_pressed(self):
        self.controller.pan_left(self._get_speed_level())

    def _handle_pan_right_pressed(self):
        self.controller.pan_right(self._get_speed_level())

    def _handle_tilt_released(self):
        if self.ui.checkMoveStop.isChecked():
            self.controller.stop_movement()

    def _handle_pan_released(self):
        if self.ui.checkMoveStop.isChecked():
            self.controller.stop_movement()

    def _handle_stop_at(self):
        self.controller.stop_at(int(self.ui.editStopAt.text() or "0"))

    def _handle_abs_move(self):
        self.controller.abs_move(
            self.ui.labelMCUType.text(), int(self.ui.editABSPos.text() or "0"), self._get_speed_level())

    def _handle_abs2_move(self):
        self.controller.abs_move(
            self.ui.labelMCUType.text(), int(self.ui.editABS2Pos.text() or "0"), self._get_speed_level())

    def _handle_abs_angle_move(self):
        self.controller.abs_angle_move(
            self.ui.labelMCUType.text(), int(self.ui.editABSAngle.text() or "0"), self._get_speed_level())

    def _handle_abs_angle2_move(self):
        self.controller.abs_angle_move(
            self.ui.labelMCUType.text(), int(self.ui.editABSAngle2.text() or "0"), self._get_speed_level())

    def _handle_rel_move_up(self):
        self.controller.rel_move('up', int(self.ui.editRelStep.text() or '0'), self._get_speed_level())

    def _handle_rel_move_down(self):
        self.controller.rel_move('down', int(self.ui.editRelStep.text() or '0'), self._get_speed_level())

    def _handle_rel_move_left(self):
        self.controller.rel_move('left', int(self.ui.editRelStep.text() or '0'), self._get_speed_level())

    def _handle_rel_move_right(self):
        self.controller.rel_move('right', int(self.ui.editRelStep.text() or '0'), self._get_speed_level())

    def _handle_speed_level_changed(self, text: str):
        self.controller.set_speed_level(int(text or "1"))

    def _handle_speed_by_zoom_on(self):
        self.controller.speed_by_zoom_on(int(self.ui.editSpeedByZoomRatio.text() or "1"))

    def _handle_set_target_speed(self):
        self.controller.set_target_speed(int(self.ui.editTargetSpeed.text() or "0"))

    def _handle_set_acceleration(self):
        self.controller.set_acceleration(int(self.ui.editAcceleration.text() or "100"))

    def _update_mcu_type_label(self, idx: int):
        self.ui.labelMCUType.setText("Pan" if idx == 0 else "Tilt")

    def _handle_open_config(self):
        # The config dialog can still be managed by the view
        dlg = ConfigDialog(self, self.controller.config_data)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.controller.refresh_ports()

    # --- Controller-driven UI Update Methods (Slots) ---

    def on_connection_status_changed(self, is_connected):
        self.ui.btnOnline.setText("OffLine" if is_connected else "OnLine")

    def on_ports_refreshed(self, ports: list, current_port: str):
        self.ui.comboPort.clear()
        self.ui.comboPort.addItems(ports)
        idx = self.ui.comboPort.findText(current_port)
        if idx >= 0:
            self.ui.comboPort.setCurrentIndex(idx)

    def on_mcu_type_updated(self, index: int):
        if index < self.ui.comboPTType.count():
            self.ui.comboPTType.setCurrentIndex(index)
        self._update_mcu_type_label(index)

    def on_speed_value_received(self, value: int):
        self.speed_values.append(value)
        self.speed_times.append(self.speed_counter * (self.speed_timer.interval() / 1000.0))
        self.speed_counter += 1
        self._update_speed_chart_view()

    def _update_speed_chart_view(self):
        self.speed_series.clear()
        points = [QtCore.QPointF(t, v) for t, v in zip(self.speed_times, self.speed_values)]
        self.speed_series.replace(points)
        
        if self.speed_times:
            self.speed_chart.axisX().setRange(self.speed_times[0], self.speed_times[-1])
        if self.speed_values:
            ymin = min(self.speed_values)
            ymax = max(self.speed_values)
            self.speed_chart.axisY().setRange(ymin, ymax + 1 if ymin == ymax else ymax)

    def _handle_clear_speed_chart(self):
        self.speed_series.clear()
        self.speed_values.clear()
        self.speed_times.clear()
        self.speed_counter = 0
        # Re-create axes and set default ranges to 0-1
        self.speed_chart.createDefaultAxes()
        self.speed_chart.axisX().setRange(0, 1)
        self.speed_chart.axisY().setRange(0, 1)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Ensure the controller is shut down properly when the window closes."""
        self.controller.shutdown()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = SerialWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
