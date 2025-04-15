from Generics import ITADWidget
from Controllers.BasicNodeController import BasicNodeController
from Views.StorageView import StorageView 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET

class StorageController(BasicNodeController):
    def __init__(self, element:ET.Element):
        super().__init__(element)
    
    def build_view(self):
        self.view = StorageView()
        self.view.build_from_element(self.element)
    
    def connect_view(self):
        super().connect_view()
        self.view.remove_button.pressed.connect(self.toggle_drive_removed)

    def toggle_drive_removed(self):
        removed_element = self.element.find("Removed")
        if removed_element is None:
            self.element.append(ET.Element("Removed"))
            label:QLabel = self.view.vbox.itemAt(0).widget()
            label.setStyleSheet("color: red;")
            label.setText(label.text() + " (removed)") 
        else:
            self.element.remove(removed_element)
            label:QLabel = self.view.vbox.itemAt(0).widget()
            label.setStyleSheet("")
            label.setText(label.text().split(" ")[0]) 
            