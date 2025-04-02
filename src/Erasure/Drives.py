from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject,pyqtSignal,Qt
import xml.etree.ElementTree as ET



class DriveItemView(QFrame):
    wipeRequested = pyqtSignal(object)
    selectionChanged = pyqtSignal(bool)

    def __init__(self,drive_model:'DriveModel'):
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

class DriveController(QObject):
    statusChanged = pyqtSignal(str, str, bool)
    
    def __init__(self,drive_model):#, wipe_service_factory):
        super().__init__()
        self.drive_model = drive_model
        #self.wipe_service_factory = wipe_service_factory
        self.view = None  # Will be set when connecting to view

    def connect_to_view(self,view:DriveItemView):
        self.view = view
        self.view.wipe_button.pressed.connect(self.wipe)
    
    def wipe(self):
        pass
    
    def select_drive(self,selected:bool):
        self.view.wipe_checkbox.setChecked(selected)
    
    def isSelected(self):
        return self.view.wipe_checkbox.isChecked()

class DriveModel:
    def __init__(self,storage_xml:ET.Element):
        self.xml = storage_xml
        self.name = storage_xml.find(".//Name").text
        self.model = storage_xml.find(".//Model").text
        self.serial = storage_xml.find(".//Serial_Number").text
        self.size = storage_xml.find(".//Size").text
        self.path = "/dev/" + self.name


    def is_removed(self):
        return self.xml.find("Removed") is not None