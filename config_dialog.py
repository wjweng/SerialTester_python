from PyQt5 import QtWidgets

from serial_config import SerialConfig

CONFIG_FILE = "serial_config.json"

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