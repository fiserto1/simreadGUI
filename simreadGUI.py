#!/usr/bin/env python3
__author__ = "Tomas Fiser"
__license__ = "GNU"
__version__ = "1.0.0"

from test_pySIMlib import pySIMlib
import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QGridLayout, QVBoxLayout, QDesktopWidget, QApplication, QHBoxLayout, QLabel, QWidget, QPushButton
from PyQt5.QtCore import QCoreApplication, Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont


class SIMReadGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.SIMReader = pySIMlib(True)
        self.initUI()

    def initUI(self):

        layout = QGridLayout()

        self.connectButton = QPushButton()
        self.connectButton.setText("Connect Reader")
        self.connectButton.clicked.connect(self.connectReader)
        layout.addWidget(self.connectButton)

        # SIM INFO
        self.simInfoButton = QPushButton()
        self.simInfoButton.setText("SIMInfo")
        layout.addWidget(self.simInfoButton)

        # PIN GROUP
        self.changePinButton = QPushButton()
        self.changePinButton.setText("Change PIN")
        layout.addWidget(self.changePinButton)
        self.enablePinButton = QPushButton()
        self.enablePinButton.setText("Disable PIN")
        layout.addWidget(self.enablePinButton)
        self.disablePinButton = QPushButton()
        self.disablePinButton.setText("Enable PIN")
        layout.addWidget(self.disablePinButton)

        # PHONEBOOK GROUP
        self.contactsButton = QPushButton()
        self.contactsButton.setText("Contacts")
        layout.addWidget(self.contactsButton)

        # SMS GROUP
        self.smsButton = QPushButton()
        self.smsButton.setText("Messages")
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

    def connectReader(self):

        #selectCOM()
        comport = "COM4"

        if not self.SIMReader.state:
            self.SIMReader.openSession(comport)
        else:
            self.SIMReader.closeSession()

        if self.SIMReader.state:
            self.connectButton.setText("Disconnect Reader")
        else:
            self.connectButton.setText("Connect Reader")

    def exit(self):
        if self.SIMReader.state:
            self.SIMReader.closeSession()

        QCoreApplication.instance().quit()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName("SIMReadGUI")

    window = SIMReadGUI()
    app.exec_()