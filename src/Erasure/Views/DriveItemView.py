from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject,pyqtSignal,Qt,QSize,pyqtSlot
from datetime import datetime,timedelta
from Erasure.Controllers.DriveModel import DriveModel

from Erasure.Messages import *


class DriveItemView(QFrame):

    def __init__(self,drive_model:DriveModel,parent:QWidget):
        super().__init__()
        self._parent = parent
        self.drive_model = drive_model
        self.setStyleSheet("DriveItemView { border: 2px solid black; } ")
        self.initUI()

    def initUI(self):
        master_layout = QVBoxLayout()
        self.control_panel = self.build_controls()
        self.info_box = self.build_info_box()
        self.status_box = self.build_status()

        master_layout.addLayout(self.control_panel)
        master_layout.addLayout(self.info_box)
        master_layout.addLayout(self.status_box)
        self.setLayout(master_layout)

    def set_checked(self,bool:bool):
        self.wipe_checkbox.setChecked(bool)

    def build_controls(self):
        hbox = QHBoxLayout()
        label = QLabel("Selected:")
        self.wipe_checkbox = QCheckBox()
        self.wipe_checkbox.setObjectName("wipe_check_box")
        self.wipe_button = QPushButton(text="Wipe")
        hbox.addWidget(label,alignment=Qt.AlignRight)
        hbox.addWidget(self.wipe_checkbox,alignment=Qt.AlignLeft)
        hbox.addWidget(self.wipe_button)
        
        return hbox

    def build_info_box(self):
        fields = ["Name","Model","Serial_Number","Size"]        
        vbox = QVBoxLayout()
        for field in fields:
            value = self.drive_model.xml.find(".//{}".format(field)).text
            label = QLabel(value)
            vbox.addWidget(label)
        
        return vbox

    def build_status(self):
        self.status_label = SatusBox(self.drive_model)
        return self.status_label

    def sizeHint(self):
        return super().sizeHint()

class SatusBox(QVBoxLayout):

    def __init__(self,drive_model:DriveModel):
        super().__init__()
        self.drive_model = drive_model
        self.header_text = "{}".format(self.drive_model.path)
        self.initUI()

    def initUI(self):
        self.addLayout(self.build_header())
        self.addWidget(self.build_status())

    def build_header(self):
        
        timebox = QHBoxLayout()
        self.start_time = QLabel("Start Time")
        self.start_time.setAlignment(Qt.AlignLeft)

        self.time_estimate = QLabel("Time Estimate")
        self.time_estimate.setAlignment(Qt.AlignRight)

        self.time_elasped = QLabel("Time Elasped")
        self.time_elasped.setAlignment(Qt.AlignCenter)

        def gen_seperator():
            separator = QFrame()
            separator.setFrameShape(QFrame.VLine)
            separator.setFrameShadow(QFrame.Plain)
            separator.setLineWidth(1)
            return separator

        timebox.addWidget(self.start_time)
        timebox.addWidget(gen_seperator())
        timebox.addWidget(self.time_elasped)
        timebox.addWidget(gen_seperator())
        timebox.addWidget(self.time_estimate)
        
        
        return timebox

    def build_status(self):
        self.status_label = QLabel("Status")
        self.status_label.setObjectName("status_box")
        return self.status_label
    
    def update_status(self,message):
        label:QLabel = self.status_label
        label.setText(message)
        label.adjustSize()