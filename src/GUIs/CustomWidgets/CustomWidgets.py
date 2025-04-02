from GUIs.CustomWidgets.BaseWidgets import BasicNodeWidget,CustomListWidget,ITADWidget
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics,QPixmap
from PyQt5.QtCore import Qt
from Utilities.InputVerification import Verifier
import xml.etree.ElementTree as ET

"""
Custom widgets that I deemed to small to warrent a seperate file
"""

class StorageWidget(BasicNodeWidget):
    def __init__(self, el:ET.Element):
        super().__init__(el)
        self.add_controls()
        self.set_frame() 
        self.update_graphics()

    def add_controls(self):
        self.vbox.insertLayout(1,
                               self.build_controls()
                               )
   
    def set_frame(self):

        self.frame = QFrame()
        self.frame.setLayout(self.vbox)
        self.frame.setObjectName("StorageContainer")

        self.frame_Layout = QVBoxLayout()
        self.frame_Layout.addWidget(self.frame)
        self.setLayout(self.frame_Layout)
        
    def build_controls(self)->QHBoxLayout:
        hbox = QHBoxLayout()
        button = QPushButton(text="Remove Drive")
        button.clicked.connect(self.toggle_drive_state)
        hbox.addWidget(button)
        return hbox
    
    def toggle_drive_state(self):
        removed_element = self.element.find("Removed")
        if removed_element is None:
            self.element.append(ET.Element("Removed"))
        else:
            self.element.remove(removed_element)

        self.update_graphics()

    def update_graphics(self):
        removed_element = self.element.find("Removed")
        if removed_element is None:
            self.add_drive()
        else:
            self.remove_drive()

    def remove_drive(self):
        #self.element.append(ET.Element("Removed"))
        self.frame.setStyleSheet("#StorageContainer { border: 2px solid red; }")
        label:QLabel = self.vbox.itemAt(0).widget()
        label.setText(label.text() + " (removed)") 
    
    def add_drive(self):
        self.frame.setStyleSheet("")
        label:QLabel = self.vbox.itemAt(0).widget()
        label.setText(label.text().split(" ")[0]) 

class WebCam(BasicNodeWidget):
    def __init__(self,el):
        super().__init__(el)
        self.build_png()

    def build_png(self):
        try:
            pixmap = QPixmap("specs/webcam.png")
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            self.vbox.addWidget(image_label)
        except Exception as e:
            #no webcam
            print(e)

class ExitWindow(ITADWidget):
    def __init__(self):
        super().__init__()

class SystemCategory(CustomListWidget):
    
    def __init__(self,element):
        options = [
            "Desktop",
            "Laptop",
            "Server",
            "All-In-One"
        ]
        super().__init__(
            element,
            options,
            f"Select Category",
            )

class TechIDList(CustomListWidget):
    def __init__(self,element):
        prefix = "IN-"
        tech_id_total = 7
        tech_ids = [prefix+str(i+1) for i in range(tech_id_total)]
        super().__init__(
            element,
            tech_ids,
            "Select Tech ID")

