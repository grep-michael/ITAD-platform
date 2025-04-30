
from Generics import ITADView
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot,pyqtSignal,Qt

class NetworkingView(ITADView):

    signal_onshow = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout()
        self.status = QLabel("Networking window")
        self.status.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.status)
        self.generate_controls()
        self.adjustSize()
        self.setLayout(self.vbox)


    @pyqtSlot(str)
    def slot_update_status(self,status):
        self.status.setText(status)

    def showEvent(self, a0):
        self.signal_onshow.emit()
        return super().showEvent(a0)

    def generate_controls(self):
        hbox = QHBoxLayout()
        self.quit_button = QPushButton("Stop and continue")
        hbox.addWidget(self.quit_button)
        self.vbox.addLayout(hbox)
