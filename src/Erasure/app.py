from PyQt5.QtWidgets import *
from GUIs.CustomWidgets import *
import xml.etree.ElementTree as ET
from Erasure.Views.ErasureWindowView import ErasureWindowView
from Erasure.Controllers.ErasureController import ErasureController
from Erasure.Controllers.DriveModel import DriveModel


class ErasureApp(ITADWidget):

    def __init__(self, tree:ET.Element):
        super().__init__()
        layout = QVBoxLayout()
        window = self.create_main_window()
        layout.addWidget(window)
        self.setLayout(layout)
        self.load_drives(tree)
        
    def create_main_window(self):
        main_window = ErasureWindowView()
        self.erasure_controller = ErasureController()
        self.erasure_controller.connect_to_view(main_window)
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


