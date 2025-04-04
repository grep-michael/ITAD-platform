from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal,pyqtSlot
from GUIs.CustomWidgets import *

import xml.etree.ElementTree as ET
from Erasure.Views.ErasureWindowView import ErasureWindowView
from Erasure.Controllers.ErasureController import ErasureController
from Erasure.Controllers.DriveModel import DriveModel


class ErasureApp(ITADWidget):

    def __init__(self, tree:ET.Element,parent:QWidget):
        super().__init__()
        self._parent = parent
        layout = QVBoxLayout()
        window = self.create_main_window()

        self.load_drives(tree)
        layout.addWidget(window)
        self.setLayout(layout)
    
    @pyqtSlot()
    def slot_adjust_size(self):
        """
        DriveController emits a `adjustSize` signal to its driveView and to the ErasureController
        the ErasureController adjusts the size of its ErasureView and emits another `adjustSize` signal to the app, calling this function
        """
        self.set_geometry()
        self._parent.resize(self.width(),self.height())

    def pre_display_update(self,parent:QMainWindow):
        self.set_geometry()
    
    def set_geometry(self):
        desktop = QDesktopWidget()
        screen_height = desktop.availableGeometry().height() - 100
        biggest_widget:QWidget = self.findChild(ErasureWindowView)
        prefered_height = min(biggest_widget.height(),screen_height)
        self.setMinimumHeight(prefered_height)
        self.setMinimumWidth(biggest_widget.sizeHint().width())
        self.adjustSize()
        
    def create_main_window(self):
        main_window = ErasureWindowView(self)
        self.erasure_controller = ErasureController()
        self.erasure_controller.connect_to_view(main_window)
        self.erasure_controller.adjustSize.connect(self.slot_adjust_size)
        return main_window

    def load_drives(self,xml_tree):
        drives = self.create_drive_models(xml_tree)
        self.erasure_controller.load_drive_models(drives)

    def create_drive_models(self, xml_tree:ET.Element):
        drive_models = []
        storage_elements = xml_tree.findall(".//SYSTEM_INVENTORY/Devices/Storage")
        
        for storage_xml in storage_elements:
            drive_model = DriveModel(storage_xml)
            drive_models.append(drive_model)
            
        return drive_models
