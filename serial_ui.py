from PyQt5 import QtCore, QtWidgets, QtChart
from tab_main_ui import Ui_MainTab

class Ui_SerialWidget(object):
    def setupUi(self, SerialWidget):
        SerialWidget.setObjectName("SerialWidget")
        SerialWidget.resize(600, 400)

        self.verticalLayout = QtWidgets.QVBoxLayout(SerialWidget)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)

        self.topLayout = QtWidgets.QHBoxLayout()

        self.btnOnline = QtWidgets.QPushButton(SerialWidget)
        self.btnOnline.setObjectName("btnOnline")
        self.btnOnline.setFixedHeight(self.btnOnline.height() * 2)
        self.topLayout.addWidget(self.btnOnline)

        self.groupComPort = QtWidgets.QGroupBox(SerialWidget)
        self.groupComPort.setObjectName("groupComPort")
        self.layoutComPort = QtWidgets.QHBoxLayout(self.groupComPort)
        self.layoutComPort.setObjectName("layoutComPort")
        self.labelComPort = QtWidgets.QLabel(self.groupComPort)
        self.labelComPort.setObjectName("labelComPort")
        self.labelComPort.setAlignment(QtCore.Qt.AlignCenter)
        self.layoutComPort.addWidget(self.labelComPort)
        self.comboPort = QtWidgets.QComboBox(self.groupComPort)
        self.comboPort.setObjectName("comboPort")
        self.layoutComPort.addWidget(self.comboPort)
        self.btnConfigure = QtWidgets.QPushButton(self.groupComPort)
        self.btnConfigure.setObjectName("btnConfigure")
        self.layoutComPort.addWidget(self.btnConfigure)
        self.topLayout.addWidget(self.groupComPort)

        self.groupMCU = QtWidgets.QGroupBox(SerialWidget)
        self.groupMCU.setObjectName("groupMCU")
        self.layoutMCU = QtWidgets.QHBoxLayout(self.groupMCU)
        self.layoutMCU.setObjectName("layoutMCU")
        self.comboPTType = QtWidgets.QComboBox(self.groupMCU)
        self.comboPTType.setObjectName("comboPTType")
        self.comboPTType.addItems(["Pan", "Tilt"])
        self.layoutMCU.addWidget(self.comboPTType)
        self.labelMCUType = QtWidgets.QLabel(self.groupMCU)
        self.labelMCUType.setObjectName("labelMCUType")
        self.labelMCUType.setMinimumWidth(60)
        self.labelMCUType.setFrameShape(QtWidgets.QFrame.Panel)
        self.labelMCUType.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.labelMCUType.setAlignment(QtCore.Qt.AlignCenter)
        self.layoutMCU.addWidget(self.labelMCUType)
        self.topLayout.addWidget(self.groupMCU)

        self.groupFW = QtWidgets.QGroupBox(SerialWidget)
        self.groupFW.setObjectName("groupFW")
        self.layoutFW = QtWidgets.QHBoxLayout(self.groupFW)
        self.layoutFW.setObjectName("layoutFW")

        self.labelFw = QtWidgets.QLabel(self.groupFW)
        self.labelFw.setObjectName("labelFw")
        self.labelFw.setAlignment(QtCore.Qt.AlignCenter)
        self.layoutFW.addWidget(self.labelFw)

        self.labelFwValue = QtWidgets.QLabel(self.groupFW)
        self.labelFwValue.setObjectName("labelFwValue")
        self.labelFwValue.setMinimumWidth(100)
        self.labelFwValue.setFrameShape(QtWidgets.QFrame.Panel)
        self.labelFwValue.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.labelFwValue.setAlignment(QtCore.Qt.AlignCenter)
        self.layoutFW.addWidget(self.labelFwValue)

        self.topLayout.addWidget(self.groupFW)

        self.verticalLayout.addLayout(self.topLayout)

        self.tabWidget = QtWidgets.QTabWidget(SerialWidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tabMain = QtWidgets.QWidget()
        self.tabMain.setObjectName("tabMain")
        self.tabMainUi = Ui_MainTab()
        self.tabMainUi.setupUi(self.tabMain)
        # expose widgets from main tab for external access
        for name in [
            'btnTiltUp', 'btnTiltDown', 'btnPanLeft', 'btnPanRight',
            'btnPanStop', 'btnStopAt', 'checkMoveStop', 'editStopAt',
            'btnABS', 'btnABS2', 'btnABSAngle', 'btnABSAngle2',
            'btnABSStop', 'btnPanType', 'comboPanMethod', 'btnABSAngleStop',
            'editABSPos', 'editABS2Pos', 'editABSAngle', 'editABSAngle2',
            'btnRelUp', 'btnRelDown', 'btnRelLeft', 'btnRelRight', 'btnRelStop',
            'editRelStep', 'btnStallCaliOn', 'btnStallCaliOff',
            'groupZeroCali', 'btnZeroCaliPlus', 'btnZeroCaliMinus',
            'btnZeroHome', 'btnClearZeroCali', 'btnZeroCaliStatus',
            'btnLockHome', 'btnUnlockHome', 'btnLockStatus',
            'editZeroCali', 'editLockStatus',
            'groupSpeedControl', 'editSpeedLevel', 'editSpeedInPPS',
            'btnGetSpeedByZoomRatio', 'btnSpeedByZoomOn', 'btnSpeedByZoomOff',
            'editSpeedByZoomRatio', 'btnGetCurrentSpeed', 'editCurrentSpeed',
            'btnSetTargetSpeed', 'editTargetSpeed', 'groupAcceleration',
            'btnGetAcceleration', 'btnSetAcceleration', 'editAcceleration',
            'btnGetAccLevel', 'btnSetAccLevel', 'comboAccLevel',
            'groupPosition', 'btnGetPosition', 'editMotorPosition', 'btnABCount',
            'editABCount', 'btnGetAngle', 'editMotorAngle', 'btnZCount',
            'editZCount', 'groupMaxAngle', 'btnMaxAngleOn', 'btnMaxAngleOff',
            'groupMotorType', 'btnMotorType0p9d', 'btnMotorType1p8d',
            'groupSpeedChart', 'chartSpeed', 'btnShowSpeed', 'btnStopSpeed', 'btnClearChart']:
            setattr(self, name, getattr(self.tabMainUi, name))
        self.tabWidget.addTab(self.tabMain, "")

        self.tabTest = QtWidgets.QWidget()
        self.tabTest.setObjectName("tabTest")
        self.verticalLayoutTest = QtWidgets.QVBoxLayout(self.tabTest)
        self.verticalLayoutTest.setObjectName("verticalLayoutTest")
        self.groupVisca = QtWidgets.QGroupBox(self.tabTest)
        self.groupVisca.setObjectName("groupVisca")
        self.gridVisca = QtWidgets.QGridLayout(self.groupVisca)
        self.gridVisca.setObjectName("gridVisca")

        self.btnTest1 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest1.setObjectName("btnTest1")
        self.gridVisca.addWidget(self.btnTest1, 0, 0, 1, 1)
        self.editTest1 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest1.setObjectName("editTest1")
        self.gridVisca.addWidget(self.editTest1, 0, 1, 1, 1)

        self.btnTest2 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest2.setObjectName("btnTest2")
        self.gridVisca.addWidget(self.btnTest2, 1, 0, 1, 1)
        self.editTest2 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest2.setObjectName("editTest2")
        self.gridVisca.addWidget(self.editTest2, 1, 1, 1, 1)

        self.btnTest3 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest3.setObjectName("btnTest3")
        self.gridVisca.addWidget(self.btnTest3, 2, 0, 1, 1)
        self.editTest3 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest3.setObjectName("editTest3")
        self.gridVisca.addWidget(self.editTest3, 2, 1, 1, 1)

        self.btnTest4 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest4.setObjectName("btnTest4")
        self.gridVisca.addWidget(self.btnTest4, 3, 0, 1, 1)
        self.editTest4 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest4.setObjectName("editTest4")
        self.gridVisca.addWidget(self.editTest4, 3, 1, 1, 1)

        self.btnTest5 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest5.setObjectName("btnTest5")
        self.gridVisca.addWidget(self.btnTest5, 4, 0, 1, 1)
        self.editTest5 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest5.setObjectName("editTest5")
        self.gridVisca.addWidget(self.editTest5, 4, 1, 1, 1)

        self.btnTest6 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest6.setObjectName("btnTest6")
        self.gridVisca.addWidget(self.btnTest6, 5, 0, 1, 1)
        self.editTest6 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest6.setObjectName("editTest6")
        self.gridVisca.addWidget(self.editTest6, 5, 1, 1, 1)

        self.btnTest7 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest7.setObjectName("btnTest7")
        self.gridVisca.addWidget(self.btnTest7, 6, 0, 1, 1)
        self.editTest7 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest7.setObjectName("editTest7")
        self.gridVisca.addWidget(self.editTest7, 6, 1, 1, 1)

        self.btnTest8 = QtWidgets.QPushButton(self.groupVisca)
        self.btnTest8.setObjectName("btnTest8")
        self.gridVisca.addWidget(self.btnTest8, 7, 0, 1, 1)
        self.editTest8 = QtWidgets.QLineEdit(self.groupVisca)
        self.editTest8.setObjectName("editTest8")
        self.gridVisca.addWidget(self.editTest8, 7, 1, 1, 1)

        self.verticalLayoutTest.addWidget(self.groupVisca)
        self.tabTest.setLayout(self.verticalLayoutTest)
        self.tabWidget.addTab(self.tabTest, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.layoutTxRx = QtWidgets.QHBoxLayout()
        self.layoutTxRx.setObjectName("layoutTxRx")

        self.layoutTx = QtWidgets.QVBoxLayout()
        self.layoutTx.setObjectName("layoutTx")
        self.labelTx = QtWidgets.QLabel(SerialWidget)
        self.labelTx.setObjectName("labelTx")
        self.layoutTx.addWidget(self.labelTx)
        self.textTx = QtWidgets.QTextEdit(SerialWidget)
        self.textTx.setObjectName("textTx")
        self.textTx.setMinimumHeight(200)
        self.layoutTx.addWidget(self.textTx)
        self.layoutTxRx.addLayout(self.layoutTx)

        self.layoutRx = QtWidgets.QVBoxLayout()
        self.layoutRx.setObjectName("layoutRx")
        self.labelRx = QtWidgets.QLabel(SerialWidget)
        self.labelRx.setObjectName("labelRx")
        self.layoutRx.addWidget(self.labelRx)
        self.textRx = QtWidgets.QTextEdit(SerialWidget)
        self.textRx.setObjectName("textRx")
        self.textRx.setMinimumHeight(200)
        self.layoutRx.addWidget(self.textRx)
        self.layoutTxRx.addLayout(self.layoutRx)
        self.layoutTxRx.setStretch(0, 1)
        self.layoutTxRx.setStretch(1, 1)

        self.verticalLayout.addLayout(self.layoutTxRx)

        self.btnClear = QtWidgets.QPushButton(SerialWidget)
        self.btnClear.setObjectName("btnClear")
        self.verticalLayout.addWidget(self.btnClear)

        self.retranslateUi(SerialWidget)
        QtCore.QMetaObject.connectSlotsByName(SerialWidget)

    def retranslateUi(self, SerialWidget):
        _translate = QtCore.QCoreApplication.translate
        SerialWidget.setWindowTitle(_translate("SerialWidget", "Serial Tester"))
        self.btnOnline.setText(_translate("SerialWidget", "OnLine"))
        self.groupComPort.setTitle(_translate("SerialWidget", "ComPort"))
        self.labelComPort.setText(_translate("SerialWidget", "Port:"))
        self.btnConfigure.setText(_translate("SerialWidget", "Configure"))
        self.groupMCU.setTitle(_translate("SerialWidget", "MCU"))
        self.comboPTType.setItemText(0, _translate("SerialWidget", "Pan"))
        self.comboPTType.setItemText(1, _translate("SerialWidget", "Tilt"))
        self.groupFW.setTitle(_translate("SerialWidget", "FW"))
        self.labelFw.setText(_translate("SerialWidget", "FW Version:"))
        self.labelFwValue.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMain), _translate("SerialWidget", "Main"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTest), _translate("SerialWidget", "Test"))
        self.groupSpeedChart.setTitle(_translate("SerialWidget", "Speed Chart"))
        self.btnShowSpeed.setText(_translate("SerialWidget", "Start"))
        self.btnStopSpeed.setText(_translate("SerialWidget", "Stop"))
        self.groupVisca.setTitle(_translate("SerialWidget", "Test Visca Commands"))
        self.btnTest1.setText(_translate("SerialWidget", "Test 1"))
        self.btnTest2.setText(_translate("SerialWidget", "Test 2"))
        self.btnTest3.setText(_translate("SerialWidget", "Test 3"))
        self.btnTest4.setText(_translate("SerialWidget", "Test 4"))
        self.btnTest5.setText(_translate("SerialWidget", "Test 5"))
        self.btnTest6.setText(_translate("SerialWidget", "Test 6"))
        self.btnTest7.setText(_translate("SerialWidget", "Test 7"))
        self.btnTest8.setText(_translate("SerialWidget", "Test 8"))
        self.labelTx.setText(_translate("SerialWidget", "Tx:"))
        self.labelRx.setText(_translate("SerialWidget", "Rx:"))
        self.btnClear.setText(_translate("SerialWidget", "Clear"))
