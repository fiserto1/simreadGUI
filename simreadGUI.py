#!/usr/bin/env python3
__author__ = "Tomas Fiser"
__license__ = "GNU"
__version__ = "1.0.0"

# from test_pySIMlib import pySIMlib
import sys, time
from PyQt5.QtWidgets import QMainWindow, QFrame, QGridLayout, QVBoxLayout, QDesktopWidget, QApplication, QDialog, QLabel, QWidget, QPushButton, QInputDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import QCoreApplication, Qt, QBasicTimer, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QFont
from SimSerial import SerialSimLink
from commands import SimCardCommands
from utils import swap_nibbles
from SMSMessage import SMSmessage
from traceback import print_exc


class SIMReadGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.SIMReader = pySIMlib(True)
        self.initUI()
        self.sl = None

    def initUI(self):

        layout = QGridLayout()

        self.connect_button = QPushButton()
        self.connect_button.setText("Connect Reader")
        self.connect_button.clicked.connect(self.connect_reader)
        layout.addWidget(self.connect_button)

        # SIM INFO
        self.sim_info_button = QPushButton()
        self.sim_info_button.setText("SIMInfo")
        self.sim_info_button.clicked.connect(self.get_sim_info)
        self.sim_info_button.setEnabled(False)
        layout.addWidget(self.sim_info_button)

        # PIN GROUP
        self.changePinButton = QPushButton()
        self.changePinButton.setText("Change PIN")
        self.changePinButton.clicked.connect(self.change_pin)
        self.changePinButton.setEnabled(False)
        layout.addWidget(self.changePinButton)

        self.enablePinButton = QPushButton()
        self.enablePinButton.setText("Enable PIN")
        self.enablePinButton.clicked.connect(self.enable_pin)
        self.enablePinButton.setEnabled(False)
        layout.addWidget(self.enablePinButton)

        self.disablePinButton = QPushButton()
        self.disablePinButton.setText("Disable PIN")
        self.disablePinButton.clicked.connect(self.disable_pin)
        self.disablePinButton.setEnabled(False)
        layout.addWidget(self.disablePinButton)

        # PHONEBOOK GROUP
        self.contactsButton = QPushButton()
        self.contactsButton.setText("Contacts")
        self.contactsButton.setEnabled(False)
        layout.addWidget(self.contactsButton)

        # SMS GROUP
        self.smsButton = QPushButton()
        self.smsButton.setText("Messages")
        self.smsButton.clicked.connect(self.get_sms)
        self.smsButton.setEnabled(False)
        layout.addWidget(self.smsButton)

        # EXIT GROUP
        self.exitButton = QPushButton()
        self.exitButton.setText("Exit")
        self.exitButton.clicked.connect(self.exit)
        layout.addWidget(self.exitButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.show()

    def send_terminal_profile(self, _tp):
        return _tp.send_apdu_checksw('A010000011FFFF000000000000000000000000000000')

    def get_sim_info(self):
        if not self.sl:
            self.connect_reader()

        sc = SimCardCommands(self.sl)
        try:
            chv_info = sc.get_chv_info()
            sim_info = sc.get_sim_info()
        except Exception as e:
            print_exc()
            self.show_error_dialog(str(e))
            return

        self.show_info(chv_info, sim_info)

    def show_info(self, chv_info, sim_info):
        msg = QMessageBox()
        # msg.setIcon(QMessageBox.Information)

        text = "PIN1: " + str(chv_info[0]) + '\n' + "PIN1 tries left: " + str(chv_info[1]) + '\n' \
               + "PIN2: " + str(chv_info[2]) + '\n' + "PIN2 tries left: " + str(chv_info[3]) + '\n' \
               + "Location: " + str(sim_info[0]) + '\n' \
               + "MSISDN: " + str(sim_info[1]) + '\n' \
               + "IMSI: " + str(sim_info[2]) + '\n' \
               + "ICCID: " + str(sim_info[3]) + '\n' \
               + "Phase: " + str(sim_info[4]) + '\n'
        msg.setText(text)
        msg.setWindowTitle("SIM Info")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        retval = msg.exec_()
        print("value of pressed message box button:", retval)

    def connect_reader(self):

        self.sl = SerialSimLink(debug=True)
        ports = self.sl.scan_serial_ports()
        if not ports:
            raise Exception("No available serial ports.")
        elif len(ports) < 2:
            selected_port = ports[0]
        else:
            selected_port = self.select_port(ports)

        if not selected_port:
            return

        self.sl.connect(selected_port, 9600)

        # ac = AppLoaderCommands(sl)

        self.sl.wait_for_card()
        time.sleep(0.5)
        sc = SimCardCommands(self.sl)
        try:
            chv_info = sc.get_chv_info()
        except Exception as e:
            print_exc()
            self.show_error_dialog(str(e))
            return

        if chv_info[0]:
            pin = self.enter_pin()
            if not pin or not pin.isdigit() or len(pin) < 4 or len(pin) > 8:
                self.show_error_dialog("PIN is not valid.")
                return

            try:
                sc.verify_chv(1, pin)
            except Exception as e:
                print_exc()
                self.show_error_dialog(str(e))
                return

        self.smsButton.setEnabled(True)
        self.changePinButton.setEnabled(True)
        self.disablePinButton.setEnabled(True)
        self.enablePinButton.setEnabled(True)
        self.sim_info_button.setEnabled(True)
        # self.connect_button.setEnabled(False)

    def show_error_dialog(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)

        retval = msg.exec_()
        print("value of pressed message box button:", retval)

    def enter_pin(self):
        text, ok = QInputDialog.getText(self, "Enter pin dialog", "Enter PIN:")
        if ok and text:
            return text
        else:
            return None

    def select_port(self, ports):
        item, ok = QInputDialog.getItem(self, "Select serial port dialog", "Available serial ports:", ports, 0, False)

        if ok and item:
            return item
        else:
            return None

    def change_pin(self):

        curr_pin, new_pin = self.enter_new_pin()

        if not curr_pin or not curr_pin.isdigit() or len(curr_pin) < 4 or len(curr_pin) > 8:
            return

        if not new_pin or not new_pin.isdigit() or len(new_pin) < 4 or len(new_pin) > 8:
            return

        if not self.sl:
            self.connect_reader()

        sc = SimCardCommands(self.sl)

        try:
            data1 = sc.verify_chv(1, curr_pin)
            data2 = sc.change_chv(1, curr_pin, new_pin)
        except Exception as e:
            print_exc()
            self.show_error_dialog(str(e))
            return

        self.disable_buttons()
        print("Changed!:" + str(data1) + str(data2))

    def disable_buttons(self):
        self.sim_info_button.setEnabled(False)
        self.changePinButton.setEnabled(False)
        self.enablePinButton.setEnabled(False)
        self.disablePinButton.setEnabled(False)
        self.contactsButton.setEnabled(False)
        self.smsButton.setEnabled(False)

    def disable_pin(self):
        pin = self.enter_pin()
        if not pin or not pin.isdigit() or len(pin) < 4 or len(pin) > 8:
            return
        if not self.sl:
            self.connect_reader()

        sc = SimCardCommands(self.sl)

        try:
            sc.disable_chv(pin)
        except Exception as e:
            print_exc()
            self.show_error_dialog(str(e))
            return

        self.disable_buttons()

    def enable_pin(self):
        pin = self.enter_pin()
        if not pin or not pin.isdigit() or len(pin) < 4 or len(pin) > 8:
            return
        if not self.sl:
            self.connect_reader()

        sc = SimCardCommands(self.sl)

        try:
            sc.enable_chv(pin)
        except Exception as e:
            print_exc()
            self.show_error_dialog(str(e))
            return

        self.disable_buttons()


    def enter_new_pin(self):
        dialog = InputDialog()
        if dialog.exec():
            return dialog.getInputs()
        return None

    def get_sms(self):
        if not self.sl:
            self.connect_reader()

        sc = SimCardCommands(self.sl)

        try:
            all_sms = sc.get_sms()
        except Exception as e:
            print_exc()
            self.show_error_dialog(str(e))
            return

        lines = ""
        for sms in all_sms:
            s = SMSmessage()
            s.smsFromData(sms)
            if s.message:
                line = "Timestamp: " + s.timestamp + "From: " + s.number + "Status: " + s.status + "Message: " + s.message + "\n"
                lines += line

        msg = QMessageBox()
        # msg.setIcon(QMessageBox.Information)
        if not lines:
            lines = "No message found."
        msg.setText(lines)
        msg.setWindowTitle("SMS List")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        retval = msg.exec_()
        print("value of pressed message box button:", retval)

    def exit(self):
        if self.SIMReader.state:
            self.SIMReader.closeSession()

        QCoreApplication.instance().quit()

class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("Current Pin", self.first)
        layout.addRow("New Pin", self.second)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return (self.first.text(), self.second.text())

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName("SIMReadGUI")
    app.setStyle('Fusion')

    window = SIMReadGUI()
    app.exec_()