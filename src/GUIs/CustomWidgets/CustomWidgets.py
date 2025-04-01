from GUIs.BaseWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFontMetrics,QPixmap
from PyQt5.QtCore import Qt
from Utilities.InputVerification import Verifier
import xml.etree.ElementTree as ET

"""
Custom widgets that I deemed to small to warrent a seperate file
"""

class WebCam(ElementNode):
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

class ExitWindow(QWidget):
    def __init__(self):
        super().__init__()

class SystemCategory(CustomList):
    
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

class TechIDList(CustomList):
    def __init__(self,element):
        prefix = "IN-"
        tech_id_total = 7
        tech_ids = [prefix+str(i+1) for i in range(tech_id_total)]
        super().__init__(
            element,
            tech_ids,
            "Select Tech ID")

