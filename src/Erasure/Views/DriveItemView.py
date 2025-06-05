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

    #@pyqtSlot(Message)
    #def slot_status_update(self,message:ErasureStatusUpdateMessage):
    #    acceptable_messages = [ErasureTimeUpdateMessage,
    #                           ErasureStatusUpdateMessage,StartErasureMessage,ErasureErrorMessage,ErasureSuccessMessage
    #                           ]
    #    if message.__class__ not in acceptable_messages:
    #        print("Illegal message passed to DriveItemView: {}".format(message))
    #        return
    #    if isinstance(message,StartErasureMessage):
    #        self.status_label.update_status("Erasure Started",message.stylesheet,message.override)
    #        self.status_label.start_timer()
    #    if isinstance(message,ErasureStatusUpdateMessage):
    #        self.status_label.update_status(message.message,message.stylesheet,message.override)
    #    
    #    self.status_label.update_timer()

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
        self.time_elasped = QLabel("Time Elasped")
        self.time_elasped.setAlignment(Qt.AlignRight)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setLineWidth(1)
        timebox.addWidget(self.start_time)
        timebox.addWidget(separator)
        timebox.addWidget(self.time_elasped)
        
        
        return timebox

    def build_status(self):
        self.status_label = QLabel("Status")
        self.status_label.setObjectName("status_box")
        return self.status_label
    
    def start_timer(self):
        self.start_time.setText(datetime.now().strftime("%H:%M:%S"))
        self.start_time.raw_time = datetime.now()
        
    def update_timer(self):
        if not hasattr(self.start_time,"raw_time"):
            return
        seconds_passed = (datetime.now() - self.start_time.raw_time).total_seconds()
        hours, remainder = divmod(seconds_passed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_elasped.setText('{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds)))

    def update_status(self,message:str,stylesheet:str,override:bool):
        label:QLabel = self.status_label
        #if not override:
        #    stylesheet = label.styleSheet()+stylesheet
        #label.setStyleSheet(stylesheet)
        label.setText(message)
        label.adjustSize()