from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal,pyqtSlot
from Generics import ITADWidget

import xml.etree.ElementTree as ET
from Erasure.Views.ErasureWindowView import ErasureWindowView
from Erasure.Controllers.ErasureController import ErasureController
from Erasure.Controllers.DriveModel import DriveModel


class ErasureApp(ITADWidget):

    def __init__(self, tree:ET.Element,parent:QWidget):
        super().__init__()
        self._parent = parent
        self.main_layout = QVBoxLayout()
        self.create_main_window()

        self.load_drives(tree)
        self.main_layout.addWidget(self.main_window)
        self.setLayout(self.main_layout)
    
    def isMaximized(self):
        """
        The ErasureApp class is bascially a proxy between the ErasureWindow and the actual application
        thus we have to pass some elements of the Main application to this class
        """
        return self._parent.isMaximized()

    @pyqtSlot()
    def slot_adjust_size(self):
        """
        DriveController emits a `adjustSize` signal to its driveView and to the ErasureController
        the ErasureController adjusts the size of its ErasureView and emits another `adjustSize` signal to the app, calling this function
        """
        if not self._parent.isMaximized():
            self.set_geometry()
            self._parent.resize(self.width(),self.height())

    def pre_display_update(self,parent:QMainWindow):
        self.set_geometry()
    
    def set_geometry(self):
        desktop = QDesktopWidget()
        screen_height = desktop.availableGeometry().height() - 100
        screen_width = desktop.availableGeometry().width() - 50
        biggest_widget:QWidget = self.findChild(ErasureWindowView)
        prefered_height = min(biggest_widget.height(),screen_height)
        prefered_width = min(biggest_widget.sizeHint().width(),screen_width)
        self.setMinimumHeight(prefered_height)
        self.setMinimumWidth(prefered_width)
        self.adjustSize()
              
    def create_main_window(self):
        self.main_window = ErasureWindowView(self)
        self.erasure_controller = ErasureController()
        self.erasure_controller.connect_to_view(self.main_window)
        self.erasure_controller.adjustSize.connect(self.slot_adjust_size)
        
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

    def showEvent(self,event):
        self.erasure_controller.wipe_all()
        super().showEvent(event)
        
