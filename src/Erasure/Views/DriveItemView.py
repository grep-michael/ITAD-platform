from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject,pyqtSignal,Qt
from Erasure.Controllers.DriveModel import DriveModel

class DriveItemView(QFrame):
    wipeRequested = pyqtSignal(object)
    selectionChanged = pyqtSignal(bool)

    def __init__(self,drive_model:DriveModel):
        super().__init__()
        self.drive_model = drive_model
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
        #self.wipe_button.clicked.connect(self._self_wipe)
        hbox.addWidget(label,alignment=Qt.AlignRight)
        hbox.addWidget(self.wipe_checkbox,alignment=Qt.AlignLeft)
        hbox.addWidget(self.wipe_button)

        return hbox

    def build_info_box(self):
        fields = ["Name","Model","Serial_Number","Size"]        
        vbox = QVBoxLayout()
        for field in fields:
            value = self.drive_model.xml.find(".//{}".format(field)).text
            vbox.addWidget(QLabel(value))
        
        return vbox

    def build_status(self):
        vbox = QVBoxLayout()
        self.status_label = QLabel("Status")
        removed = self.drive_model.is_removed()
        if removed:
            self.status_label.setText("Removed")
            self.status_label.setStyleSheet("color: red;")
        self.status_label.setObjectName("status_box")
        vbox.addWidget(self.status_label)
        return vbox

    def update_status(self,message:str,stylesheet:str,override:bool):
        label:QLabel = self.findChild(QLabel, "status_box")
        if not override:
            stylesheet = self.styleSheet()+stylesheet
        self.setStyleSheet(stylesheet)
        label.setText("{}".format(message))
